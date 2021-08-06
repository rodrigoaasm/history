import pytest
import falcon
import json
from unittest.mock import MagicMixin, MagicMock

from history.api.response_util import validate_accept_header, build_response_body

class TestResponseUtil:
    
    mock_history = {
        "attr1": [
            {
                "attr": "attr1",
                "value": "teste",
                "device_id": "teste",
                "ts": "2021-08-03T20:38:13.389000Z",
                "metadata": {}
            }
        ],
        "attr2": [
            {
                "attr": "attr2",
                "value": "teste",
                "device_id": "teste",
                "ts": "2021-08-03T20:38:13.389000Z",
                "metadata": {}
            }
        ]
    }
    
    def test_validate_accept_header__should_not_raised_exception__when_http_accept_is_supported(self):
        request = MagicMock();
        request.client_accepts = lambda accept : True
        
        validate_accept_header(request)
        
    def test_validate_accept_header__should_raised_http_not_acceptable_exception__when_http_accept_is_not_supported(self):
        request = MagicMock();
        request.client_accepts = lambda accept : False;
        with pytest.raises(falcon.HTTPNotAcceptable):
            validate_accept_header(request)

    def test_build_response_body__should_return_a_json__when_accept_is_json(self):
        request = MagicMock();
        request.client_accepts = lambda accept : accept == "application/json"

        assert build_response_body(request, self.mock_history) == json.dumps(self.mock_history)
            
    def test_build_response_body__should_return_a_csv__when_accept_is_csv(self):
        request = MagicMock();
        request.client_accepts = lambda accept : accept == "text/csv"
        except_csv = '"attr","value","device_id","ts"\n"attr1","teste","teste","2021-08-03T20:38:13.389000Z"\n'

        assert build_response_body(request, self.mock_history["attr1"]) == except_csv
            
    def test_build_response_body__should__return_a_csv__when_accept_is_csv_and_a_parser_entered(self):
        request = MagicMock();
        request.client_accepts = lambda accept : accept == "text/csv"             
        mock_parse = lambda history : self.mock_history["attr1"] + self.mock_history["attr2"]
        except_csv = '"attr","value","device_id","ts"\n"attr1","teste","teste","2021-08-03T20:38:13.389000Z"\n"attr2","teste","teste","2021-08-03T20:38:13.389000Z"\n'

        assert build_response_body(request, self.mock_history,mock_parse) == except_csv
            
    def test_build_response_body__should_raised_a_http_not_acceptable_exception__when_accept_is_not_supported(self):
        request = MagicMock();
        request.client_accepts = lambda accept : False;
        with pytest.raises(falcon.HTTPNotAcceptable):
            build_response_body(request, self.mock_history)


