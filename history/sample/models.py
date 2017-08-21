# -*- coding: utf-8 -*-
"""
Exposes device information using dojot's modelling
"""
import json
import base64
import logging
import falcon
import pymongo
from history import settings

class AuthMiddleware(object):
    """
        Middleware used to populate context with relevant JWT-sourced information.
        Also used to validate and refuse requests that do not contain valid tokens associated
        with them.
    """

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


class HistoryUtil(object):

    @staticmethod
    def get_db():
        # TODO should come from conf, not method
        return settings.MONGO_DB['device_history']

    @staticmethod
    def get_collection(service, device_id):
        db = HistoryUtil.get_db()
        collection_name = "%s_%s" % (service, device_id)
        if collection_name in db.collection_names():
            return db["%s_%s" % (service, device_id)]
        else:
            raise falcon.HTTPNotFound(title="Device not found",
                                      description="No data for the given device could be found")

    @staticmethod
    def check_mandatory_query_param(params, field, ftype=None):
        if (field not in params.keys()) or (len(params[field]) == 0):
            raise falcon.HTTPMissingParam(field)

        if ftype is not None:
            if not ftype(params[field]):
                print("failed to validate field %s %s" % (field, params[field]))
                raise falcon.HTTPInvalidParam('%s must be of type %s' % (field, ftype.__name__), field)

class DeviceHistory(object):
    """Service used to retrieve a given device historical data"""

    @staticmethod
    def on_get(req, resp, device_id):
        HistoryUtil.check_mandatory_query_param(req.params, 'lastN', int)
        HistoryUtil.check_mandatory_query_param(req.params, 'attr')

        collection = HistoryUtil.get_collection(req.context['related_service'], device_id)
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

class STHHistory(object):
    """ Deprecated: implements STH's NGSI-like historical view of data """

    @staticmethod
    def on_get(req, resp, device_type, device_id, attr):
        HistoryUtil.check_mandatory_query_param(req.params, 'lastN', int)

        collection = HistoryUtil.get_collection(req.context['related_service'], device_id)
        ls_filter = {"_id" : False, '@timestamp': False, '@version': False}
        sort = [('ts', pymongo.DESCENDING)]
        query = {'attr': attr, 'value': {'$ne': ' '}}
        limit_val = int(req.params['lastN'])
        cursor = collection.find(query, ls_filter, sort=sort, limit=limit_val)

        history = []

        if cursor.count() > 0:
            print cursor[0]
            device_type = cursor[0]['device_type']

        for d in cursor:
            history.append({
                "attrType": d['type'],
                "attrValue": d['value'],
                "recvTime": d['ts']
            })

        ngsi_body = {
            "contextResponses": [
                {
                    "contextElement": {
                        "attributes": [{
                            "name": attr,
                            "values": history
                        }],
                        "id": device_id,
                        "isPattern": False,
                        "type": device_type
                    },
                    "statusCode": {"code": "200", "reasonPhrase": "OK"}
                }
            ]
        }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(ngsi_body)
