# -*- coding: utf-8 -*-
"""
Exposes device information using dojot's modelling
"""
# System imports
import json
import base64
import logging
# Third-party imports
import falcon
import pymongo

# Local imports
from history import settings

class AuthMiddleware(object):

    def __init__(self):
        self.logger = logging.getLogger('history.' + __name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.DEBUG)

    def process_request(self, req, resp):
        challenges = ['Token type="JWT"']
        token = req.get_header('authorization')
        if token is None:
            description = ('Please provide an auth token as part of the request.')
            raise falcon.HTTPUnauthorized('Authentication required', description, challenges)

        req.context['related_service'] = self._parse_token(token)
        if req.context['related_service'] is None:
            description = ('The provided auth token is not valid. '
                           'Please request a new token and try again.')
            raise falcon.HTTPUnauthorized('Authentication required', description, challenges)


    @staticmethod
    def _decode_base64(data):
        """
            Decode base64, padding being optional.
            :param data: Base64 data as an ASCII byte string
            :returns: The decoded byte string.
        """
        missing_padding = len(data) % 4
        if missing_padding != 0:
            data += b'='* (4 - missing_padding)
        return base64.decodestring(data)


    def _parse_token(self, token):
        """
            Parses the authorization token, returning the service to be used as tenant id

            :param token: JWT token to be parsed
            :returns: Service to be used on API calls, or None if token is invalid
        """
        if not token or len(token) == 0:
            return None

        payload = token.split('.')[1]
        try:
            data = json.loads(AuthMiddleware._decode_base64(payload))
            return data['service']
        except Exception as exception:
            self.logger.error(exception)
            return None

class DeviceHistory(object):
    """Service used to retrieve a given device historical data"""

    @staticmethod
    def get_db():
        return settings.MONGO_DB['device_history']

    @staticmethod
    def get_collection(service, device_id):
        db = DeviceHistory.get_db()
        collection_name = "%s_%s" % (service, device_id)
        if collection_name in db.collection_names():
            return db["%s_%s" % (service, device_id)]
        else:
            raise falcon.HTTPNotFound(title="Device not found", description="No data for the given device could be found")

    @staticmethod
    def check_mandatory_query_param(params, field, ftype=str):
        if (field not in params.keys()) or (len(params[field]) == 0):
            raise falcon.HTTPMissingParam(field)

        if type(params[field]) is not ftype:
            raise falcon.HTTPInvalidParam('%s must be of type %s' % (field, ftype.__name__), field)

    @staticmethod
    def on_get(req, resp, device_id):
        DeviceHistory.check_mandatory_query_param(req.params, 'lastN', int)
        DeviceHistory.check_mandatory_query_param(req.params, 'attr')

        collection = DeviceHistory.get_collection(req.context['related_service'], device_id)
        ls_filter = {"_id" : False, '@timestamp': False, '@version': False}
        sort = [('ts', pymongo.DESCENDING)]
        query = {'attr': req.params['attr']}
        limit_val = int(req.params['lastN'])
        cursor = collection.find(query, ls_filter, sort=sort, limit=limit_val)
        history = []
        for d in cursor:
            history.append(d)

        if len(history) == 0:
            raise falcon.HTTPNotFound(title="Attr not found", description="No data for the given attribute could be found")

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(history)
