
import time
import re
import requests

from trafficgenerator.tgn_utils import TgnError
from IxRestUtils import formatDictToJSONPayload


kActionStateFinished = 'finished'
kActionStatusSuccessful = 'Successful'
kActionStatusError = 'Error'
kTestStateUnconfigured = 'Unconfigured'

logger = None


def waitForActionToFinish(connection, replyObj, action_url):
    '''
        This method waits for an action to finish executing. after a POST request is sent in order to start an action,
        The HTTP reply will contain, in the header, a 'location' field, that contains an URL.
        The action URL contains the status of the action. we perform a GET on that URL every 1 second until the action
        finishes with a success.
        If the action fails, we will throw an error and print the action's error message.

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - replyObj the reply object holding the location
        - action_url - URL of the original POST action
    '''

    action_result_url = replyObj.headers.get('location')
    if action_result_url:
        actionResultURL = '/'.join(action_result_url[1:].split('/')[2:])
        finished = False

        while not finished:
            time.sleep(1)
            action_status = connection.httpGet(actionResultURL)
            if connection.api_version == 'v1':
                finished = (action_status.progress == 100)
                success = action_status.state.lower() == 'success'
            else:
                finished = (action_status.state.lower() == 'finished')
                success = (action_status.status.lower() == 'successful')

        if not success:
            error_msg = 'Error while executing {}. '.format(action_url)
            if hasattr(action_status, 'errorMessage'):
                error_msg += action_status.errorMessage
            elif hasattr(action_status, 'error'):
                error_msg += action_status.error
            elif hasattr(action_status, 'warning'):
                error_msg += action_status.warning
            elif hasattr(action_status, 'message'):
                error_msg += action_status.message
            raise TgnError(error_msg)


def performGenericOperation(connection, url, payloadDict):
    '''
        This will perform a generic operation on the given url, it will wait for it to finish.

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - url is the address of where the operation will be performed
        - payloadDict is the python dict with the parameters for the operation
        Returns:
        - reply of the operation POST command
    '''
    data = formatDictToJSONPayload(payloadDict)
    reply = connection.httpPost(url=url, data=data)
    waitForActionToFinish(connection, reply, url)
    return reply


def performGenericPost(connection, listUrl, payloadDict):
    '''
        This will perform a generic POST method on a given url

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - url is the address of where the operation will be performed
        - payloadDict is the python dict with the parameters for the operation
    '''
    data = formatDictToJSONPayload(payloadDict)

    reply = connection.httpPost(url=listUrl, data=data)
    newObjPath = reply.headers['location']

    newObjID = newObjPath.split('/')[-1]
    return newObjID


def performGenericDelete(connection, listUrl, payloadDict):
    '''
        This will perform a generic DELETE method on a given url

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - url is the address of where the operation will be performed
        - payloadDict is the python dict with the parameters for the operation
    '''
    data = formatDictToJSONPayload(payloadDict)

    reply = connection.httpDelete(url=listUrl, data=data, headers={})
    return reply


def performGenericPatch(connection, url, payloadDict):
    '''
        This will perform a generic PATCH method on a given url

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - url is the address of where the operation will be performed
        - payloadDict is the python dict with the parameters for the operation
    '''
    data = formatDictToJSONPayload(payloadDict)

    reply = connection.httpPatch(url=url, data=data)
    if reply.status_code >= 400:
        raise Exception('patch failed with error {} - {}'.format(reply.status_code, reply.text))
    return reply


def createSession(connection):
    '''
        This method is used to create a new session. It will return the url of the newly created session

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
    '''

    if connection.api_version == 'v1':
        data = {"applicationVersion": connection.ixload_version}
    else:
        data = {"ixLoadVersion": connection.ixload_version}
    session_id = performGenericPost(connection, 'sessions', data)
    performGenericOperation(connection, 'sessions/{}/operations/start'.format(session_id), {})
    return 'sessions/{}'.format(session_id)


def deleteSession(connection, sessionUrl):
    '''
        This method is used to delete an existing session.

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the seession to delete
    '''
    deleteParams = {}
    performGenericDelete(connection, sessionUrl, deleteParams)


def loadRepository(connection, sessionUrl, rxfFilePath):
    '''
        This method will perform a POST request to load a repository.

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the session to load the rxf for
        - rxfFilePath is the local rxf path on the machine that holds the IxLoad instance
    '''

    if 'localhost' not in connection.url and '127.0.0.1' not in connection.url:
        rxfFilePath = uploadFile(connection, rxfFilePath)
    loadTestUrl = "%s/ixload/test/operations/loadTest" % (sessionUrl)
    data = {"fullPath": rxfFilePath}
    performGenericOperation(connection, loadTestUrl, data)


def saveRxf(connection, sessionUrl, rxfFilePath):
    '''
        This method saves the current rxf to the disk of the machine on which the IxLoad instance is running.
        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the session to save the rxf for
        - rxfFilePath is the location where to save the rxf on the machine that holds the IxLoad instance
    '''

    if 'localhost' not in connection.url and '127.0.0.1' not in connection.url:
        raise TgnError('Save configuration not supported on remote servers.')
    saveRxfUrl = "%s/ixload/test/operations/saveAs" % (sessionUrl)
    rxfFilePath = rxfFilePath.replace("\\", "\\\\")
    data = {"fullPath": rxfFilePath, "overWrite": 1}

    performGenericOperation(connection, saveRxfUrl, data)


def runTest(connection, sessionUrl):
    """ Start the currently loaded test. After starting the 'Start Test' action, wait for the action to complete.

        :param connection: connection object that manages the HTTP data transfers between the client and the REST API
        :param sessionUrl: the address of the session that should run the test.
    """
    startRunUrl = "%s/ixload/test/operations/runTest" % (sessionUrl)
    performGenericOperation(connection, startRunUrl, {})


def stopTest(connection, sessionUrl):
    """ Stop the currently running test. After starting the 'Start Test' action, wait for the action to complete.

        :param connection: connection object that manages the HTTP data transfers between the client and the REST API
        :param sessionUrl: the address of the session that should run the test.
    """
    startRunUrl = "%s/ixload/test/operations/abortAndReleaseConfigWaitFinish" % (sessionUrl)
    performGenericOperation(connection, startRunUrl, {})


def getTestCurrentState(connection, sessionUrl):
    '''
    This method gets the test current state. (for example - running, unconfigured, ..)
    Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the session that should run the test.
    '''
    activeTestUrl = "%s/ixload/test/activeTest" % (sessionUrl)
    testObj = connection.httpGet(activeTestUrl)

    return testObj.currentState


def getTestRunError(connection, sessionUrl):
    '''
    This method gets the error that appeared during the last test run.
    If no error appeared (the test ran successfully), the return value will be 'None'.
    Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the session that should run the test.
    '''
    activeTestUrl = "%s/ixload/test/activeTest" % (sessionUrl)
    testObj = connection.httpGet(activeTestUrl)

    return testObj.testRunError


def waitForTestToReachUnconfiguredState(connection, sessionUrl):
    '''
    This method waits for the current test to reach the 'Unconfigured' state.
    This is required in order to make sure that the test, after finishing the run, completes the Clean Up process
    before the IxLoad session is closed.
    Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the session that should run the test.
    '''
    while getTestCurrentState(connection, sessionUrl) != kTestStateUnconfigured:
        time.sleep(0.1)


def pollStats(connection, sessionUrl, watchedStatsDict, pollingInterval=4):
    '''
        This method is used to poll the stats. Polling stats is per request but this method does a continuous poll.

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the session that should run the test
        - watchedStatsDict these are the stats that are being monitored
        - pollingInterval the polling interval is 4 by default but can be overridden.

    '''
    statSourceList = watchedStatsDict.keys()

    # retrieve stats for a given stat dict
    # all the stats will be saved in the dictionary below

    # statsDict format:
    # {
    # 	statSourceName: {
    # 						timestamp:	{
    # 										statCaption : value
    # 									}
    # 					}
    # }
    statsDict = {}

    # remember the timstamps that were already collected - will be ignored in future
    # format { statSource : [2000, 4000, ...] }
    collectedTimestamps = {}
    testIsRunning = True

    # check the test state, and poll stats while the test is still running
    while testIsRunning:

        # the polling interval is configurable. by default, it's set to 4 seconds
        time.sleep(pollingInterval)

        for statSource in statSourceList:
            valuesUrl = "%s/ixload/stats/%s/values" % (sessionUrl, statSource)

            valuesObj = connection.httpGet(valuesUrl)
            valuesDict = valuesObj.getOptions()

            # get just the new timestamps - that were not previously retrieved in another stats polling iteration
            newTimestamps = [int(timestamp) for timestamp in valuesDict.keys() if
                             timestamp not in collectedTimestamps.get(statSource, [])]
            newTimestamps.sort()

            for timestamp in newTimestamps:
                timeStampStr = str(timestamp)

                collectedTimestamps.setdefault(statSource, []).append(timeStampStr)

                timestampDict = statsDict.setdefault(statSource, {}).setdefault(timestamp, {})

                # save the values for the current timestamp, and later print them
                for caption, value in valuesDict[timeStampStr].getOptions().items():
                    if caption in watchedStatsDict[statSource]:
                        timestampDict[caption] = value

        testIsRunning = getTestCurrentState(connection, sessionUrl) == "Running"


def clearChassisList(connection, sessionUrl):
    '''
        This method is used to clear the chassis list. After execution no chassis should be available in the
        chassisList.
        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the session that should run the test
    '''
    chassisListUrl = "%s/ixload/chassischain/chassisList" % sessionUrl
    deleteParams = {}
    performGenericDelete(connection, chassisListUrl, deleteParams)


def addChassisList(connection, sessionUrl, chassisList):
    '''
        This method is used to add one or more chassis to the chassis list.

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the session that should run the test
        - chassisList is the list of chassis that will be added to the chassis chain.
    '''
    chassisListUrl = "%s/ixload/chassisChain/chassisList" % (sessionUrl)

    chassis_ids = []
    for chassisName in chassisList:
        data = {"name": str(chassisName)}
        chassisId = performGenericPost(connection, chassisListUrl, data)

        # refresh the chassis
        refreshConnectionUrl = "%s/%s/operations/refreshConnection" % (chassisListUrl, chassisId)
        performGenericOperation(connection, refreshConnectionUrl, {})
        chassis_ids.append(chassisId)
    return chassis_ids


def assignPorts(connection, sessionUrl, portListPerCommunity):
    """ Assign ports from a connected chassis to the required NetTraffics.

        :param connection: connection object that manages the HTTP data transfers between the client and the REST API
        :param sessionUrl: is the address of the session that should run the test
        :param portListPerCommunity: dictionary mapping NetTraffics to ports {community name: [port list])
    """
    communtiyListUrl = "%s/ixload/test/activeTest/communityList" % sessionUrl

    communityList = connection.httpGet(url=communtiyListUrl)

    for community in communityList:
        portListForCommunity = portListPerCommunity.get(community.name)

        portListUrl = "%s/%s/network/portList" % (communtiyListUrl, community.objectID)

        if portListForCommunity:
            for portTuple in portListForCommunity:
                chassisId, cardId, portId = portTuple
                paramDict = {"chassisId": chassisId, "cardId": cardId, "portId": portId}

                performGenericPost(connection, portListUrl, paramDict)


def getIPRangeListUrlForNetworkObj(connection, networkUrl):
    '''
        This method will return the IP Ranges associated with an IxLoad Network component.

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - networkUrl is the REST address of the network object for which the network ranges will be provided.
    '''
    networkObj = connection.httpGet(networkUrl)

    if isinstance(networkObj, list):
        for obj in networkObj:
            url = "%s/%s" % (networkUrl, obj.objectID)
            rangeListUrl = getIPRangeListUrlForNetworkObj(connection, url)
            if rangeListUrl:
                return rangeListUrl
    else:
        for link in networkObj.links:
            if link.rel == 'rangeList':
                rangeListUrl = re.sub("/api/v0/", "/", link.href)
                return rangeListUrl

        for link in networkObj.links:
            if link.rel == 'childrenList':
                # remove the 'api/v0' elements of the url, since they are not needed for connection http get
                childrenListUrl = re.sub("/api/v0/", "/", link.href)

                return getIPRangeListUrlForNetworkObj(connection, childrenListUrl)

    return None


def changeIpRangesParams(connection, sessionUrl, ipOptionsToChangeDict):
    '''
        This method is used to change certain properties on an IP Range.

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the session that should run the test
        - ipOptionsToChangeDict is the Python dict holding the items in the IP range that will be changed.
            (ipOptionsToChangeDict format -> { IP Range name : { optionName : optionValue } })
    '''
    communtiyListUrl = "%s/ixload/test/activeTest/communityList" % sessionUrl

    communityList = connection.httpGet(url=communtiyListUrl)

    for community in communityList:
        stackUrl = "%s/%s/network/stack" % (communtiyListUrl, community.objectID)

        rangeListUrl = getIPRangeListUrlForNetworkObj(connection, stackUrl)
        rangeList = connection.httpGet(rangeListUrl)

        for rangeObj in rangeList:
            if rangeObj.name in ipOptionsToChangeDict.keys():
                rangeObjUrl = "%s/%s" % (rangeListUrl, rangeObj.objectID)
                paramDict = ipOptionsToChangeDict[rangeObj.name]

                performGenericPatch(connection, rangeObjUrl, paramDict)


def getCommandListUrlForAgentName(connection, sessionUrl, agentName):
    '''
        This method is used to get the commandList url for a provided agent name.

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the session that should run the test
        - agentName is the agent name for which the commandList address is provided
    '''
    communtiyListUrl = "%s/ixload/test/activeTest/communityList" % sessionUrl
    communityList = connection.httpGet(url=communtiyListUrl)

    for community in communityList:
        activityListUrl = "%s/%s/activityList" % (communtiyListUrl, community.objectID)
        activityList = connection.httpGet(url=activityListUrl)

        for activity in activityList:
            if activity.name == agentName:
                # agentActionListUrl = "%s/%s/agent/actionList" % (activityListUrl, activity.objectID)
                agentUrl = "%s/%s/agent" % (activityListUrl, activity.objectID)
                agent = connection.httpGet(agentUrl)

                for link in agent.links:
                    if link.rel in ['actionList', 'commandList']:
                        commandListUrl = re.sub("/api/v0/", "/", link.href)
                        return commandListUrl


def clearAgentsCommandList(connection, sessionUrl, agentNameList):
    '''
        This method clears all commands from the command list of the agent names provided.

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the session that should run the test
        - agentNameList the list of agent names for which the command list will be cleared.
    '''
    deleteParams = {}
    for agentName in agentNameList:
        commandListUrl = getCommandListUrlForAgentName(connection, sessionUrl, agentName)

        if commandListUrl:
            performGenericDelete(connection, commandListUrl, deleteParams)


def addCommands(connection, sessionUrl, commandDict):
    '''
        This method is used to add commands to a certain list of provided agents.

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the session that should run the test
        - commandDict is the Python dict that holds the mapping between agent name and specific commands. (commandDict
            format -> { agent name : [ { field : value } ] })
    '''
    for agentName in commandDict.keys():
        commandListUrl = getCommandListUrlForAgentName(connection, sessionUrl, agentName)

        if commandListUrl:
            for commandParamDict in commandDict[agentName]:
                performGenericPost(connection, commandListUrl, commandParamDict)


def changeActivityOptions(connection, sessionUrl, activityOptionsToChange):
    '''
        This method will change certain properties for the provided activities.

        Args:
        - connection is the connection object that manages the HTTP data transfers between the client and the REST API
        - sessionUrl is the address of the session that should run the test
        - activityOptionsToChange is the Python dict that holds the mapping between agent name and specific properties
            (activityOptionsToChange format: { activityName : { option : value } })
    '''
    communtiyListUrl = "%s/ixload/test/activeTest/communityList" % sessionUrl
    communityList = connection.httpGet(url=communtiyListUrl)

    for community in communityList:
        activityListUrl = "%s/%s/activityList" % (communtiyListUrl, community.objectID)
        activityList = connection.httpGet(url=activityListUrl)

        for activity in activityList:
            if activity.name in activityOptionsToChange.keys():
                activityUrl = "%s/%s" % (activityListUrl, activity.objectID)
                performGenericPatch(connection, activityUrl, activityOptionsToChange[activity.name])


def uploadFile(connection, filename, overwrite=True):
    headers = {'Content-Type': 'multipart/form-data'}
    uploadPath = filename.replace(':', '').replace('\\', '/').lstrip('/')
    params = {'overwrite': overwrite, 'uploadPath': uploadPath, 'filename': filename}
    with open(filename, 'rb') as f:
        connection.httpPost('resources', data=f.read(), params=params, headers=headers)
    return '/mnt/ixload-share/{}'.format(uploadPath)
