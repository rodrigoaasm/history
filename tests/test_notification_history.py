import pytest
import falcon
import json
import unittest
import history
import datetime
import pymongo
import dateutil.parser
from unittest.mock import Mock, MagicMock, patch
from history import app
from history.api import models
from history.api.models import NotificationHistory, HistoryUtil
from falcon import testing

class TestNotificationHistory:

    @patch.object(HistoryUtil,'get_collection')
    @patch('history.api.models.NotificationHistory.get_query')
    @patch('history.api.models.NotificationHistory.get_notifications')
    def test_notification_on_get(self,mock_hutil,mock_getquery,mock_get_notifications):
        req = MagicMock()
        req.context.return_value = {}
        resp = falcon.Response()
        mock_hutil.return_value = {}
        mock_getquery.return_value = {}
        mock_get_notifications.return_value= {}
        NotificationHistory.on_get(req,resp)
        assert resp.status == falcon.HTTP_200
    
    def test_get_query_ts(self):
        with patch.object(HistoryUtil,'model_value') as mock_model_value:
            mock_model_value.return_value = 'bar'
            ts_filter = {}
            ts_filter['$gte'] = dateutil.parser.parse("2021-07-13T21:31:04.912000Z")
            ts_filter['$lte'] = dateutil.parser.parse("2021-07-13T21:31:45.560000Z")
            filter_query = {"key": "foo", "dateFrom": "2021-07-13T21:31:04.912000Z", "dateTo": "2021-07-13T21:31:45.560000Z"}
            returned_query = NotificationHistory.get_query(filter_query)
            expected_query = {'query': {'metaAttrsFilter.key': 'bar', 'ts': ts_filter}, 'limit_val': 0, 'sort': [('ts', -1)], 'filter': {'_id': False, '@timestamp': False, '@version': False}}
            assert returned_query == expected_query
    
    def test_get_query_limit(self):
        with patch.object(HistoryUtil,'model_value') as mock_model_value:
            mock_model_value.return_value = 'bar'
            filter_query = {"key": "foo", "limit": 15}
            returned_query = NotificationHistory.get_query(filter_query)
            expected_query = {'query': {'metaAttrsFilter.key': 'bar'}, 'limit_val': 15, 'sort': [('ts', -1)], 'filter': {'_id': False, '@timestamp': False, '@version': False}}
            assert returned_query == expected_query
    
    @patch('pymongo.collection.Collection.find')
    def test_get_notifications(self, mock_find):
        mock_find.return_value = {"meta":[
            {"ts":1567704621},
            {"ts":1567701021},
            {"ts":1567099821}]
        }
        query = {"query":"","filter":"","limit_val":0,"sort":0}
        assert NotificationHistory.get_notifications(mock_find,query) == []            
