# -*- coding: utf-8 -*-
"""
Exposes device information using dojot's modelling
"""
import json
import base64
import logging

import dateutil.parser
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

    db = pymongo.MongoClient(settings.MONGO_DB, replicaSet=settings.REPLICA_SET)

    @staticmethod
    def get_db():
        return HistoryUtil.db['device_history']

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
                raise falcon.HTTPInvalidParam(
                    '%s must be of type %s' % (field, ftype.__name__), field)

class DeviceHistory(object):
    """Service used to retrieve a given device historical data"""

    logger = logging.getLogger('history.' + __name__)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    @staticmethod
    def parse_request(request, attr):
        """ returns mongo compatible query object, based on the query params provided """

        if 'lastN' in request.params.keys():
            limit_val = int(request.params['lastN'])
        elif 'hLimit' in request.params.keys():
            limit_val = int(request.params['hLimit'])
        else:
            raise falcon.HTTPMissingParam('lastN')

        query = {'attr': attr, 'value': {'$ne': ' '}}
        ts_filter = {}
        if 'dateFrom' in request.params.keys():
            ts_filter['$gte'] = dateutil.parser.parse(request.params['dateFrom'])
        if 'dateTo' in request.params.keys():
            ts_filter['$lte'] = dateutil.parser.parse(request.params['dateTo'])
        if len(ts_filter.keys()) > 0:
            query['ts'] = ts_filter

        ls_filter = {"_id" : False, '@timestamp': False, '@version': False}
        sort = [('ts', pymongo.DESCENDING)]

        return {'query': query, 'limit': limit_val, 'filter': ls_filter, 'sort': sort}

    @staticmethod
    def get_single_attr(collection, query):
        cursor = collection.find(query['query'],
                                 query['filter'],
                                 sort=query['sort'],
                                 limit=query['limit'])
        history = []
        for d in cursor:
            entry = d
            entry['ts'] = d['ts'].isoformat() + 'Z'
            history.append(d)
        return history

    @staticmethod
    def on_get(req, resp, device_id):
        HistoryUtil.check_mandatory_query_param(req.params, 'attr')

        collection = HistoryUtil.get_collection(req.context['related_service'], device_id)

        if isinstance(req.params['attr'], list):
            DeviceHistory.logger.info('got list of attrs')
            history = {}
            for attr in req.params['attr']:
                query = DeviceHistory.parse_request(req, attr)
                history[attr] = DeviceHistory.get_single_attr(collection, query)
        else:
            history = DeviceHistory.get_single_attr(
                collection, DeviceHistory.parse_request(req, req.params['attr']))
            if len(history) == 0:
                msg = "No data for the given attribute could be found"
                raise falcon.HTTPNotFound(title="Attr not found", description=msg)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(history)

class STHHistory(object):
    """ Deprecated: implements STH's NGSI-like historical view of data """

    @staticmethod
    def on_get(req, resp, device_type, device_id, attr):
        collection = HistoryUtil.get_collection(req.context['related_service'], device_id)

        query = DeviceHistory.parse_request(req, attr)
        cursor = collection.find(query['query'],
                                 query['filter'],
                                 sort=query['sort'],
                                 limit=query['limit'])
        history = []
        for d in cursor:
            history.insert(0, {
                "attrType": device_type,
                "attrValue": d['value'],
                "recvTime": d['ts'].isoformat() + 'Z'
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
