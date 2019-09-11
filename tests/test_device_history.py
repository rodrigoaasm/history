import pytest
import falcon
from unittest.mock import MagicMock, Mock, patch
from history.api.models import DeviceHistory

class TestDeviceHistory:
    
    #TODO: find way to test this
    
    def test_parse_request(self):
        request = MagicMock()
        request.params.keys.return_value = ['lastN','dateFrom','dateTo']
        req_dict = {"lastN":2,"dateFrom":"20190901" ,"dateTo":"20190910"}
        request.params.__getitem__.side_effect = lambda key: req_dict[key]
        assert DeviceHistory.parse_request(request,'test')
    
    def test_parse_request_invalid_lastN(self):
        with pytest.raises(falcon.HTTPInvalidParam):
            request = MagicMock()
            request.params.keys.return_value = ['lastN','dateFrom','dateTo']
            req_dict = {"lastN":"test"}
            request.params.__getitem__.side_effect = lambda key: req_dict[key]
            DeviceHistory.parse_request(request,"test")

    def test_parse_request_invalid_hLimit(self):
        with pytest.raises(falcon.HTTPInvalidParam):
            request = MagicMock()
            request.params.keys.return_value = ['hLimit','dateFrom','dateTo']
            req_dict = {"hLimit":"test"}
            request.params.__getitem__.side_effect = lambda key: req_dict[key]
            DeviceHistory.parse_request(request,"test")
