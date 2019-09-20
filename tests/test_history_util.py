import pytest
import falcon
import pymongo
from unittest.mock import Mock, MagicMock, patch
from history.api.models import HistoryUtil

class MockDBCol:
    def collection_names(self):
        return ['service_item','tenant_id']
    
    def __getitem__(self, key):
        return str(key)

class TestHistoryUtil:

    @patch.object(HistoryUtil,'get_db')
    def test_get_collection(self,mock_db):
        mock_db.return_value = MockDBCol()
        mock_db.collection_names.return_value = ['service_item','tenant_id']
        assert HistoryUtil.get_collection('service','item') == 'service_item'

    @patch('history.api.models.HistoryUtil.db')
    def test_get_collection_not_found(self,mock_db):
        with pytest.raises(falcon.HTTPNotFound):
            mock_db.collection_names.return_value = []
            HistoryUtil.get_collection('service','item')

    def test_check_type_string(self):
        assert HistoryUtil.check_type('"test"') == "string"
    
    def test_check_type_int(self):
        assert HistoryUtil.check_type("12") == "int"
    
    def test_check_type_invalid(self):
        with pytest.raises(TypeError):
            assert HistoryUtil.check_type(True) is None
    
    def test_model_value_int(self):
        assert HistoryUtil.model_value("12", "int") == 12
    
    def test_model_value_string(self):
        assert HistoryUtil.model_value("value", "string") == "value"
    
    def test_model_value_wrong_type(self):
        with pytest.raises(ValueError):
            assert HistoryUtil.model_value("value", "int")
