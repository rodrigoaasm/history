import pytest
import falcon
import json
import unittest
from unittest.mock import Mock, MagicMock, patch
from history import app
from history.api import models
from history.api.models import DeviceHistory, STHHistory, AuthMiddleware, NotificationHistory, HistoryUtil
from falcon import testing

class TestHistory():  
    
    """Testing AuthMiddleware"""
    def test_decode_base_64(self):
        result = AuthMiddleware._decode_base64('dGhpcyBpcyBhIHRlc3Q=')
        assert result == b'this is a test'

    def test_process_request_no_token(self):
        with pytest.raises(falcon.HTTPUnauthorized):
            req = Mock()
            req.get_header.return_value = None
            resp = json.dumps({"body":""})
            authmidd = AuthMiddleware()
            authmidd.process_request(req,resp)
    
    def test_process_request_invalid_token(self):
        with pytest.raises(falcon.HTTPUnauthorized):
            req = MagicMock()
            req.headers['authorization'] = 'dGhpcyBpcyBhIHRlc3Q='
            req.context['related_service'] = None
            resp = json.dumps({"body":""})
            authmidd = AuthMiddleware()
            authmidd.process_request(req,resp)

    def test_parse_token_none(self):
        authmidd = AuthMiddleware()
        assert authmidd._parse_token(None) == None
    
#    def test_parse_token_random():
#        authmidd = AuthMiddleware()
#        assert authmidd._parse_token('dGhpcyBpcy.BhIHRlc3Q=') == None

    """ 
    Testing HistoryUtil
    """
    @patch('history.api.models.HistoryUtil.db')
    def test_get_collection(self,mock_db):
        mock_db.collection_names.return_value = ['service_item','tenant_id']
        assert HistoryUtil.get_collection('service','item') == 'service_item'

    @patch('history.api.models.HistoryUtil.db')
    def test_get_collection_not_found(self,mock_db):
        with pytest.raises(falcon.HTTPNotFound):
            mock_db.collection_names.return_value = []
            HistoryUtil.get_collection('service','item')

    def test_check_type_string(self):
        assert HistoryUtil.check_type("") == "string"
    
    def test_check_type_int(self):
        assert HistoryUtil.check_type("12") == "int"
    
    def test_check_type_invalid(self):
        with pytest.raises(TypeError):
            assert HistoryUtil.check_type(True) == None
    
    def test_model_value_int(self):
        assert HistoryUtil.model_value("12", "int") == 12
    
    def test_model_value_string(self):
        assert HistoryUtil.model_value("value", "string") == "value"
    
    def test_model_value_wrong_type(self):
        with pytest.raises(ValueError):
            assert HistoryUtil.model_value("value", "int")
        