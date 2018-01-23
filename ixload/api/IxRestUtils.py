
"""
IxRestUtils is a collection of classes that offer a generic wrapper around a raw REST API.

It handles:
- Creating a connection;
- Running HTTP methods for an active connection

Abstracting the RAW HTTP input / output to tangible objects that will act as an interface to the REST API.
"""

import requests

from urlparse import urljoin


# Gets a Connection instance, that will be used to make the HTTP requests to the application
def getConnection(server, port):
    connectionUrl = 'http://{}:{}/'.format(server, port)
    conn = Connection(connectionUrl, "v0")
    return conn


# Converts a given python dict instance to a string JSON payload that can be sent to a REST API.
def formatDictToJSONPayload(dictionary):
    jsonPayload = "{"
    optionsList = []
    for key, val in dictionary.items():
        valStr = str(val)
        if type(val) is str:
            valStr = '"%s"' % val
        if type(val) is bool:
            valStr = valStr.lower()
        optionsList.append('"%s":%s' % (key, valStr))

    jsonPayload += ",".join(optionsList)
    jsonPayload += "}"

    return jsonPayload


class Connection(object):
    '''
        Class that executes the HTTP requests to the application instance.
        It handles creating the HTTP session and executing HTTP methods.

    '''
    kHeaderContentType = "content-type"
    kContentJson = "application/json"

    def __init__(self, siteUrl, apiVersion):
        '''
            Args:
            - siteUrl is the actual url to which the Connection instance will be made.
            - apiVersion is the actual version of the REST API that the Connection instance will use.

            The HTTP session will be created when the first http request is made.
        '''

        self.httpSession = None
        # final url for the connection will have the format: "http://IP:PORT/api/versionNo"
        self.url = Connection.urljoin(siteUrl, "api")
        self.url = Connection.urljoin(self.url, apiVersion)

    def _getHttpSession(self):
        '''
            This is a lazy initializer for the HTTP session.
            It does not need to be active until it is required.
        '''
        if self.httpSession is None:
            self.httpSession = requests.Session()
        return self.httpSession

    @classmethod
    def urljoin(cls, base, end):
        """ Join two URLs. If the second URL is absolute, the base is ignored.

        Use this instead of urlparse.urljoin directly so that we can customize its behavior if necessary.
        Currently differs in that it
            1. appends a / to base if not present.
            2. casts end to a str as a convenience
        """
        if base and not base.endswith("/"):
            base = base + "/"
        return urljoin(base, str(end))

    def httpRequest(self, method, url="", data="", params={}, headers={}):
        '''
            Args:

            - Method (mandatory) represents the HTTP method that will be executed.
            - url (optional) is the url that will be appended to the application url.
            - data (optional) is the data that needs to be sent along with the HTTP method as the JSON payload
            - params (optional) the payload python dict not necessary if data is used.
            - headers (optional) these are the HTTP headers that will be sent along with the request. If left blank
                will use default

            Method for making a HTTP request. The method type (GET, POST, PATCH, DELETE) will be sent as a parameter.
            Along with the url and request data. The HTTP response is returned
        '''
        headers[Connection.kHeaderContentType] = Connection.kContentJson

        absUrl = Connection.urljoin(self.url, url)
        result = self._getHttpSession().request(method, absUrl, data=str(data), params=params, headers=headers)
        return result

    def httpGet(self, url="", data="", params={}, headers={}):
        '''
            Method for calling HTTP GET. This will return a WebObject that has the fields returned
            in JSON format by the GET operation.
        '''
        reply = self.httpRequest("GET", url, data, params, headers)
        return _WebObject(reply.json())

    def httpPost(self, url="", data="", params={}, headers={}):
        '''
            Method for calling HTTP POST. Will return the HTTP reply.
        '''
        return self.httpRequest("POST", url, data, params, headers)

    def httpPatch(self, url="", data="", params={}, headers={}):
        '''
            Method for calling HTTP PATCH. Will return the HTTP reply.
        '''
        return self.httpRequest("PATCH", url, data, params, headers)

    def httpDelete(self, url="", data="", params={}, headers={}):
        '''
            Method for calling HTTP DELETE. Will return the HTTP reply.
        '''
        return self.httpRequest("DELETE", url, data, params, headers)


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
