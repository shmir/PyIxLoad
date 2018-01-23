
import sys
import logging

# cd e:\workspace\python\PyIxLoad\ixload\api

from ixload.api import IxRestUtils, IxLoadUtils

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

connection = IxRestUtils.getConnection('localhost', '8080')
sessionUrl = IxLoadUtils.createSession(connection, '8.01.106.3')

# Always useful...
# IxLoadUtils.deleteSession(connection, 'http://localhost:8080/api/v0/sessions/9')
