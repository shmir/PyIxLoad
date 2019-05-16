"""
@author yoram@ignissoft.com
"""

from os import path
import time
import requests

from trafficgenerator.tgn_utils import TgnError
from trafficgenerator.tgn_tcl import get_args_pairs


class IxlRestWrapper(object):

    def __init__(self, logger):
        """ Init IXL REST package.

        :param looger: application logger.
        """

        self.logger = logger

    def request(self, command, url, **kwargs):
        self.logger.debug('{} - {} - {}'.format(command.__name__, url, kwargs))
        response = command(url, **kwargs)
        self.logger.debug('{}'.format(response))
        if response.status_code == 400:
            raise TgnError('failed to {} {} {} - status code {}\n{}'.
                           format(command.__name__, url, kwargs, response.status_code, response.text))
        return response

    def stripApiAndVersionFromURL(self, url):
        urlElements = url.split('/')
        if 'api' in url:
            # strip the api/v0 part of the url
            urlElements = urlElements[2:]

        return '/'.join(urlElements)

    def waitForActionToFinish(self, replyObj, actionUrl):
        actionResultURL = replyObj.headers['location']
        if actionResultURL:
            actionResultURL = self.stripApiAndVersionFromURL(actionResultURL)
            actionFinished = False

            while not actionFinished:
                actionStatusObj = self.get(self.server_url + actionResultURL)
                self.logger.info(actionStatusObj.state.lower())

                if self.version > '8.50':
                    status = not (actionStatusObj.state.lower() == 'in_progress')
                    actionStatusObj.status = actionStatusObj.state
                else:
                    status = (actionStatusObj.state.lower() == 'finished')

                if status:
                    if 'success' in actionStatusObj.status.lower():
                        actionFinished = True
                    else:
                        errorMsg = "Error while executing action '%s'." % actionUrl
                        if actionStatusObj.status.lower() == 'error':
                            errorMsg += actionStatusObj.error
                        raise TgnError(errorMsg)
                else:
                    time.sleep(1)

    def get(self, url):
        response = self.request(requests.get, url)
        return _WebObject(response.json())

    def post(self, url, data=None):
        return self.request(requests.post, url, json=data)

    def delete(self, url):
        return self.request(requests.delete, url, headers={'Content-Type': 'application/json'})

    def operation(self, url, data=None):
        response = self.post(url, data)
        self.waitForActionToFinish(response, url)
        return response

    #
    # IxLoad built in commands ordered alphabetically.
    #

    def connect(self, ip, port, version):
        self.version = version
        self.server_url = 'http://{}:{}/api/'.format(ip, port)
        response = self.post(self.server_url + 'v1/sessions', {"applicationVersion": version})
        session_id = response.headers['location'].split('/')[-1]
        self.session_url = self.server_url + 'v1/sessions/' + session_id
        self.operation(self.session_url + '/operations/start', {})

    def disconnect(self):
        self.delete(self.session_url)

    def new(self, obj_type, **attributes):
        if obj_type == 'ixTestController':
            return self.session_url + '/ixload'
        elif obj_type == 'ixRepository':
            resource_url = self.session_url + 'resources'
            upload_path = 'c:/temp/ixLoadGatewayUploads' + path.split(attributes['name'])[1]
            self.IxLoadUtils.uploadFile(self.connection, resource_url, attributes['name'], upload_path)
            self.IxLoadUtils.loadRepository(self.connection, self.session_url, upload_path)

    def config(self, obj_ref, **attributes):
        self.selfCommand(obj_ref, 'config', get_args_pairs(attributes))


def _WebObject(value):
    '''
        Method used for creating a wrapper object corresponding to the JSON string received on a GET request.
    '''
    if isinstance(value, dict):
        result = WebObject(**value)
    elif isinstance(value, list):
        result = WebList(entries=value)
    else:
        result = value
    return result


class WebList(list):
    '''
        Using this class a JSON list will be transformed in a list of WebObject instances.
    '''

    def __init__(self, entries=[]):
        '''
            Create a WebList from a list of items that are processed by the _WebObject function
        '''
        for item in entries:
            self.append(_WebObject(item))


class WebObject(object):
    '''
        A WebObject instance will have its fields set to correspond to the JSON format received on a GET request.
        for example: a response in the format: {"caption": "http"} will return an object that has obj.caption="http"
    '''
    def __init__(self, **entries):
        '''
            Create a WebObject instance by providing a dict having a property - value structure.
        '''
        self.jsonOptions = {}
        for key, value in entries.iteritems():
            webObj = _WebObject(value)
            self.jsonOptions[key] = webObj
            self.__dict__[key] = webObj

    def getOptions(self):
        '''
            Get the JSON dictionary which represents the WebObject Instance
        '''
        return self.jsonOptions
