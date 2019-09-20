import pytest
import falcon
import json
from unittest.mock import Mock, MagicMock, patch
from history.api.models import AuthMiddleware

class TestAuthMiddleware:

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
    
    @patch.object(AuthMiddleware,'_parse_token')
    def test_process_request_invalid_token(self, mock_parse_token):
        with pytest.raises(falcon.HTTPUnauthorized):
            req = MagicMock()
            headers = {'authorization':'dGhpcyBpcyBhIHRlc3Q='}
            context = {'related_service':None}
            req.headers.__getitem__.side_effect = lambda key: headers[key]
            req.context.__getitem__.side_effect = lambda key: context[key]
            resp = falcon.Response()
            authmidd = AuthMiddleware()
            authmidd.process_request(req,resp)

    def test_parse_token_none(self):
        authmidd = AuthMiddleware()
        assert authmidd._parse_token(None) is None
