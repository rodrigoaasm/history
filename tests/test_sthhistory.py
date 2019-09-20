import pytest
import falcon
import json
from unittest.mock import patch, Mock, MagicMock
from history.api.models import STHHistory, DeviceHistory

class TestSTHH:

    @patch('pymongo.collection.Collection')
    @patch('history.api.models.HistoryUtil.get_collection')
    @patch('history.api.models.DeviceHistory.parse_request')
    def test_on_get(self, mock_pymongo_find, mock_get_collection, mock_parse_request):
        response = falcon.Response()
        request = MagicMock()
        request.context.return_value= None
        mock_pymongo_find.find.return_value = {
            "id":0,
            "attrs":[{
                "value":"plim",
                "ts":1567704621
            },
            {
                "value": "plom",
                "ts": 1567701021
            }]
        }
        mock_get_collection.return_value = mock_pymongo_find.return_value
        mock_parse_request.return_value = {"query":"","filter":"","sort":0,"limit":0}

        STHHistory.on_get(request,response,'test_device','test_id','blim')
        assert response.status == falcon.HTTP_200
