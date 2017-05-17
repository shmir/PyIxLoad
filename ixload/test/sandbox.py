
# GET http://localhost:9001/api/v0/sessions
# DELETE http://localhost:9001/api/v0/sessions
################################################################################
# $Version 1.00$ $Revision: 1 $
# $Date: 07/31/13  $
#
# $Workfile: IxLoad.py $
#
# Copyright 1997 - 2013 by IXIA.
# All Rights Reserved.
#
# 
# Description: IxLoad Python automation proxies
#              It converts python script to TCL command and then excute it
#
#
################################################################################

import Tkinter, sys, os, re


try:
    # create a TCL interpreter instance (Python 2.5+)
    _tcl_ = Tkinter.Tcl()
    _tclCallback_ = _tcl_
except:
    # create a TCL interpreter instance (Python 2.4-)
    _tk_ = Tkinter.Tk()
    _tcl_ = _tk_.tk
    _tclCallback_ = _tk_


sys.path.append('C:/Program Files (x86)/Ixia/IxLoad/8.01-GA/Client/Lib/Common')

def _TclEval(tclStatement):
    # wrapper function for debugging, etc.
    return _tcl_.eval(tclStatement)

def _GetReturnValuePythonFormat(attrValue, tclCmd):
    # help function to convert tcl return value to python format
    if attrValue.startswith("::tp::"):
        return IxLoadObjectProxy(attrValue, tclCmd)
    else:
        # Later need teepee to return type of attr for return correct type of attrValue
        return attrValue

def _GetArgsTclFormat(args, kwargs, tclCmd, prefix = ""):
    # help function for formatting args and kwargs to tcl format
    for value in args:
        tclCmd += _python2Tcl(value, prefix)
    for (key, value) in kwargs.items():
        tclCmd += " -%s%s" % (key, _python2Tcl(value))
    return tclCmd

def _getStatArgs(**kwargs):
    tclCmd = ""
    for (key, value) in kwargs.items():
        if key == "filterList":
            if type(value) != dict:
                raise "Invalid value type for %s which needs to be dictionary" % key
            tclCmd += ' -%s {' % key
            for (filterName, filters) in value.items():
                tclCmd += '"%s" {' % filterName
                for filter in filters:
                    tclCmd += '"%s" ' % filter
                tclCmd += "} "
            tclCmd += "} "
        else:
            tclCmd += " -%s %s" % (key, _python2Tcl(value))
    return tclCmd

_braceSubPattern = re.compile(r"([^\\])([\[\]])")
_escapeCharsPattern = re.compile(r"([\"])")
kQuoteChr = "\""

def _python2Tcl(value, prefix = ""):
    result = None
    if isinstance(value, IxLoadObjectProxy):
        result = " %s%s" % (prefix, value._tclObj_)
    elif isinstance(value, basestring):
        # scriptgen sometimes generates python with escaped brackets [] which
        # isn't necessary for python, so here we need to escape them only if not already escaped
        # Avoid having a path formatted like this: ""[path]""
        formatString = ' "%s%s"'
        if value.startswith(kQuoteChr) and value.endswith(kQuoteChr):
            formatString = ' %s%s'
        value = _escapeCharsPattern.sub(r'\\\1', value)
        result = formatString % (prefix, _braceSubPattern.sub(r"\1\\\2", value))

    elif isinstance(value, list):
        result = _getList(value)
    elif value is None:
        result = prefix
    else:
        try:
            tempValue = float(value)
            
            if tempValue % 1 == 0:#integer
                tempValue = int(value)
            result = " %s%s" % (prefix, tempValue)
        except:
            result = None
    if result is None:
        raise Exception("Unknown object type encountered: %s", value)
    return result

def _getList(aList):
    return " {%s}" % " ".join([_python2Tcl(element) for element in aList])

def _IsWindows():
    return sys.platform[0:3]=="win"


class IxLoadMethodProxy(object):
    def __init__(self, tclObj, cmd):
        self._tclCmd_ = "%s %s" % (tclObj, cmd)
    
    def __call__(self, *args, **kwargs):        
        tclCmd = self._tclCmd_
        prefix = ""
        # Special handle for cget due to its tcl signature <k>
        if tclCmd.split(" ")[-1] == "cget":
            prefix = "-"
        tclCmd = _GetArgsTclFormat(args, kwargs, tclCmd, prefix)
        return _GetReturnValuePythonFormat(_TclEval(tclCmd), tclCmd) 
        

class IxLoadEnumProxy(object):
    def __init__(self, objClass):
        self._objClass_ = objClass

    def __getattr__(self, attr):
        tclCmd = "$::%s(%s)" % (self._objClass_, attr)       
        return tclCmd

class IxLoadObjectProxy(object):
    def __init__(self, tclObj, tclCmd):
        self._tclObj_ = tclObj
        self._tclCmd_ = tclCmd
        self._options_ = None

    def __getattr__(self, attr):
        if self._options_ is None:
            try:
                self._options_ = _TclEval(self._tclObj_ + " getOptions").split(" ")
            except:
                self._options_ = []
        
        if "-%s" % attr in self._options_:
            tclCmd = "%s %s" % (self._tclObj_, attr)
            return _GetReturnValuePythonFormat(_TclEval(tclCmd), tclCmd)
        else:
            return IxLoadMethodProxy(self._tclObj_, attr)
    
    def __getitem__(self, index):
        tclCmd = "%s(%s)" % (self._tclCmd_, index)
        return _GetReturnValuePythonFormat(_TclEval(tclCmd), tclCmd)
    
        
class IxLoad(object):
    # Main entry point for python automation 
    
    def __init__(self):    
        #
        # setup path and load IxLoad package
        #
        if _IsWindows():
            curDir = os.path.normpath(os.path.dirname(sys.modules[self.__module__].__file__))
            self.pipe = None
            wishPath = "C:/Program Files (x86)/Ixia/IxLoad/8.01-GA/TclScripts/bin/IxiaWish.tcl"
            _TclEval('source "%s"' % wishPath)
            self.initializePipe(curDir)
        _TclEval("package require IxLoadCsv")        
        _TclEval("global ixAppPluginManager")         
         
    def __getattr__(self, attr):
        return IxLoadEnumProxy(attr)

    def initializePipe(self, curDir):
        #this should be called only from windows
        sys.path.append(os.path.join(curDir, "../../Client/Lib/Common"))
        import ixPiper
        pid = str(os.getpid())
        self.pipe = ixPiper.getThreadedPipe(pid, self.readCallback_pipe)

    def readCallback_pipe(self, message):
        if message == "exit":
            os.kill(os.getpid(),2)
        else:
            print(message)

    def loadAppPlugin(self, type):
        # API to load a protocol plugin
        _TclEval('$ixAppPluginManager load "%s"'%type)
                        
    def new(self, *args, **kwargs):
        # API to create IxLoadObjectProxy
        cmd = "::IxLoad new"
        cmd = _GetArgsTclFormat(args, kwargs, cmd)            
        return IxLoadObjectProxy(_TclEval(cmd), cmd)
    
    def connect(self, ipAddr):
        # API to connect to remote server
        _TclEval("::IxLoad connect %s" % ipAddr)
            
    def disconnect(self):
        # API to disconnect to remote server
        _TclEval("::IxLoad disconnect")
        
    def waitForTestFinish(self):
        # API to wait test to finish
        _TclEval("vwait ::ixTestControllerMonitor")
        _TclEval("puts $::ixTestControllerMonitor")

    def delete(self, objProxy):
        # API to delete  IxLoadObjectProxy that created by new()
        if objProxy and isinstance(objProxy, IxLoadObjectProxy) and objProxy._tclObj_:
            try:
                _TclEval("::IxLoad delete %s"%objProxy._tclObj_)
            finally:
                del objProxy
        else:
            raise "Failed to delete %s - Invalid value or type passed in delete()" % objProxy

    def retrieveFileCopy(self, inputFile, outputFile):
        inputFile  = inputFile.replace("\\","/")
        outputFile = outputFile.replace("\\","/")
        tclCommand= '::IxLoad retrieveFileCopy "%s" "%s" ' % (inputFile,outputFile)
        _TclEval(tclCommand)

    def waitForCaptureDataReceived(self):
        # API to wait for receiving the rest of the capture data
        _TclEval("""\
        if {$::ixCaptureMonitor == ""} {
            puts "Waiting for last capture data to arrive."
            vwait ::ixCaptureMonitor
            puts "Capture data received."
        }
        """)
   
class StatCollectorUtils(object): 
    # Stat collector utils for python automation
    
    def __init__(self):    
        #
        # setup path and load statCollectorUtils package
        #
        _TclEval("package require statCollectorUtils")

    def Initialize(self, handle):
        # API to initialize StatCollectorUtils
        _TclEval("statCollectorUtils::Initialize -testServerHandle %s" % handle)

    def ClearStats(self):
        # API to clear stats before running the test
        _TclEval("statCollectorUtils::ClearStats")

    def StartCollector(self, pythonCmd):
        # API to start collecting stats for the test
        tcl_callback = _tclCallback_.register(pythonCmd)
        _TclEval("statCollectorUtils::StartCollector -command %s" % tcl_callback)
     
    def StopCollector(self):
        # API to stop collecting stats for the test
        _TclEval("statCollectorUtils::StopCollector")
        
    def AddStat(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddStat"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)
        
    def AddNetworkStat(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddNetworkStat"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddL2L3Stat(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddL2L3Stat"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddPerInterfaceStats(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddPerInterfaceStats"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddPerUrlPerIpStats(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddPerUrlPerIpStats"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddSIPPerStreamStats(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddSIPPerStreamStats"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddMGCPPerStreamStats(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddMGCPPerStreamStats"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddVideoPerStreamStats(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddVideoPerStreamStats"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddVoIPPerChannelStats(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddVoIPPerChannelStats"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddVoIPSipPerChannelStats(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddVoIPSipPerChannelStats"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddVoIPSkinnyPerChannelStats(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddVoIPSkinnyPerChannelStats"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddH248TermGroupPerChannelStats(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddH248TermGroupPerChannelStats"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddVoIPH323PerChannelStats(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddVoIPH323PerChannelStats"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddSIPPerVideoCallStats(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddSIPPerVideoCallStats"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddVideoIPTVPerStreamStats(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddVideoIPTVPerStreamStats"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def AddPerStreamStats(self, **kwargs):
        # API to add stats for watching
        tclCmd = "statCollectorUtils::AddPerStreamStats"
        tclCmd += _getStatArgs(**kwargs)
        _TclEval(tclCmd)

    def GetRegisterStatsCommandXml(self):
        # API to get register stats command xml for the test
        _TclEval("statCollectorUtils::GetRegisterStatsCommandXml")

    def SetCsvVersion(self):
        # API to set csv version for the test
        _TclEval("statCollectorUtils::SetCsvVersion")

    def SetCsvThroughputUnits(self):
        # API to set csvThroughputUnits for the test
        _TclEval("statCollectorUtils::SetCsvThroughputUnits")
        
IxLoad = IxLoad()
IxLoad.connect('localhost')