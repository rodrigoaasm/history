import pytest
import falcon
import datetime
from unittest.mock import MagicMock, Mock, patch
from history.api.models import DeviceHistory, HistoryUtil


class TestDeviceHistory:
   
    def test_parse_request__should_return_valid_query__when_firstN_is_entered(self):
        request = MagicMock()
        request.params.keys.return_value = ['firstN', 'dateFrom', 'dateTo']
        req_content = {"firstN": 2, "dateFrom": "20190901", "dateTo": "20190910"}
        request.params.__getitem__.side_effect = lambda key: req_content[key]
        assert DeviceHistory.parse_request(request, 'test')

    def test_parse_request__should_return_a_valid_query__when_lastN_is_entered(self):
        request = MagicMock()
        request.params.keys.return_value = ['lastN','dateFrom','dateTo']
        req_content = {"lastN":2,"dateFrom":"20190901" ,"dateTo":"20190910"}
        request.params.__getitem__.side_effect = lambda key: req_content[key]
        assert DeviceHistory.parse_request(request,'test')
     
    def test_parse_request_should_raised_invalid_param_exception_when_firstN_is_not_number(self):
        with pytest.raises(falcon.HTTPInvalidParam):
            request = MagicMock()
            request.params.keys.return_value = ['firstN', 'dateFrom', 'dateTo']
            req_content = {"firstN": "test"}
            request.params.__getitem__.side_effect = lambda key: req_content[key]
            DeviceHistory.parse_request(request, "test")

    def test_parse_request_should_raised_invalid_param_exception_when_lastN_is_not_number(self):
        with pytest.raises(falcon.HTTPInvalidParam):
            request = MagicMock()
            request.params.keys.return_value = ['lastN','dateFrom','dateTo']
            req_content = {"lastN":"test"}
            request.params.__getitem__.side_effect = lambda key: req_content[key]
            DeviceHistory.parse_request(request,"test")

    def test_parse_request_should_raised_invalid_param_exception_when_hLimit_is_not_number(self):
        with pytest.raises(falcon.HTTPInvalidParam):
            request = MagicMock()
            request.params.keys.return_value = ['hLimit','dateFrom','dateTo']
            req_content = {"hLimit":"test"}
            request.params.__getitem__.side_effect = lambda key: req_content[key]
            DeviceHistory.parse_request(request,"test")
                      
    def test_csv_response_parser__should_return_all_properties_concatenated_in_array(self): 
        mock_history = {
            "test" : [{ "id" : 1 }, { "id" : 2 }],
            "test1" : [{ "id" : 3 }, {"id" : 4 }]
        }        
        except_history = [{ "id" : 1 }, { "id" : 2 }, { "id" : 3 }, {"id" : 4 }]    
        history_concatenated = DeviceHistory.csv_response_parser(mock_history)
        
        assert except_history == history_concatenated
        
    @patch('requests.get')   
    def test_get_attrs_should_return_attrs_list(self,mock_get):
        mock_get.return_value.text = """{ 
            "attrs": { 
                "1": [
                    {
                        "created": "2018-08-02T12:52:14.569559+00:00",
                        "id": 1,
                        "label": "attr1",
                        "static_value": "",
                        "template_id": "1",
                        "type": "dynamic",
                        "value_type": "float"
                    },
                    {
                        "created": "2018-08-02T12:52:14.605001+00:00",
                        "id": 4,
                        "label": "attr2",
                        "static_value": "MQTT",
                        "template_id": "1",
                        "type": "meta",
                        "value_type": "string"
                    }
                ]
            },
            "created": "2018-08-02T12:52:29.310182+00:00",
            "id": "b374a5",
            "label": "MyAwesomeDevice",
            "templates": [
                1
            ]
        }"""       
        attrs_list = DeviceHistory.get_attrs('device_id','token')
        
        assert attrs_list == ['attr1', 'attr2']           

    def test_get_single_attr__should_return_a_valid_history(self):
        collection = MagicMock()
                
        mock_data =  [
            {
                "attr": "attr1",
                "value": "teste",
                "device_id": "teste",
                "ts": datetime.datetime.now(),
                "metadata": {}
            },
            {
                "attr": "attr1",
                "value": "teste",
                "device_id": "teste",
                "ts": datetime.datetime.now(),
                "metadata": {}
            }
        ]
        collection.find = lambda query, filter, sort, limit : mock_data
        query = { "query": "", "filter": "", "sort": "", "limit": ""}
        assert DeviceHistory.get_single_attr(collection, query)  
              
    
    @patch('history.api.models.HistoryUtil.get_collection')    
    @patch('history.api.models.DeviceHistory.get_single_attr')
    def test_on_get_single_attr__should_raised_an_http_not_found_exception(self,mock_historyu_get_collection, mock_get_single_attr):
        request = MagicMock()
        request.params.keys.return_value = ['attr']
        request.params.return_value = ['value']
        response = falcon.Response()
        mock_historyu_get_collection.return_value = { }
        with pytest.raises(falcon.HTTPNotFound):
            mock_get_single_attr.return_value = []
            DeviceHistory.on_get(request,response,'testid')
    
    @patch('history.api.models.HistoryUtil.get_collection')    
    @patch('history.api.models.DeviceHistory.parse_request')
    @patch('history.api.response_util.validate_accept_header')           
    @patch('history.api.models.DeviceHistory.get_attrs') 
    @patch('history.api.response_util.build_response_body')
    
    def test_on_get__should_return_a_response_with_code_200__when_no_attr_was_specified(self,mock_get_collection, mock_get_attrs, mock_parse_request, 
        mock_validate_accept_header, mock_build_response_body):
         with patch('history.api.models.DeviceHistory.get_single_attr') as mock_get_attr:
            request = MagicMock()
            request.params.keys.return_value = []
            request.get_header.return_value = 'token'
            request.params.return_value = ['value']
            response = falcon.Response()
            
            attr_list = ['attr1','attr2']
            mock_get_attrs.return_value = attr_list
            mock_parse_request.return_value = None
            mock_get_attr.return_value = ''
            mock_build_response_body.return_value = { "teste" : "teste" }
            
            DeviceHistory.on_get(request, response, 'test')

            assert response.status == falcon.HTTP_200   
              
    @patch('history.api.models.HistoryUtil.get_collection')
    @patch('history.api.models.DeviceHistory.get_attrs')
    @patch('history.api.models.DeviceHistory.parse_request')
    @patch('history.api.response_util.validate_accept_header')
    @patch('history.api.response_util.build_response_body')      
    def test_on_get__should_return_a_response_with_code_200__when_one_attr_was_specified(self,mock_get_collection, mock_get_attrs, mock_parse_request, 
        mock_validate_accept_header, mock_build_response_body):
        with patch('history.api.models.DeviceHistory.get_single_attr') as mock_get_attr:
            request = MagicMock()
            request.params.keys.return_value = ['attr']
            request.get_header.return_value = 'token'
            request.params.return_value = ['value']
            response = falcon.Response()
            
            attr_list = ['attr1','attr2']
            mock_get_attrs.__getitem__.side_effect = lambda key: attr_list[key]
            mock_parse_request.return_value = None
            mock_get_attr.return_value = 'retorno'
            mock_build_response_body.return_value = {}
            
            DeviceHistory.on_get(request, response, 'test')

            assert response.status == falcon.HTTP_200    
            
    @patch('history.api.models.HistoryUtil.get_collection')
    @patch('history.api.models.DeviceHistory.get_attrs')
    @patch('history.api.models.DeviceHistory.parse_request')
    @patch('history.api.response_util.validate_accept_header')
    @patch('history.api.response_util.build_response_body')      
    def test_on_get__should_return_a_response_with_code_200__when_attrs_list_was_specified(self,mock_get_collection, mock_get_attrs, mock_parse_request, 
        mock_validate_accept_header, mock_build_response_body):
        with patch('history.api.models.DeviceHistory.get_single_attr') as mock_get_attr:
            request = MagicMock()
            #request.params.keys.return_value = ['attr']
            request.get_header.return_value = 'token'
            request.params = {"attr": ["test","test1"]}
            response = falcon.Response()
            
            attr_list = ['attr1','attr2']
            mock_get_attrs.__getitem__.side_effect = lambda key: attr_list[key]
            mock_parse_request.return_value = None
            mock_get_attr.return_value = 'retorno'
            mock_build_response_body.return_value = {}
            
            DeviceHistory.on_get(request, response, 'test')

            assert response.status == falcon.HTTP_200  
            
    