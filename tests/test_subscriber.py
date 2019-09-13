import pytest
import json
import pymongo
from unittest.mock import Mock, MagicMock, patch
from history.subscriber.persister import Persister

class TestPersister:

    #Testing handle_notification mehod    
    def test_handle_notification_no_timestamp(self):
        # raises exception because does not have "timestamp"
        with pytest.raises(Exception):
            p = Persister()        
            message = json.dumps({"ts": 1567704621,"metaAttrsFilter":{"shouldPersist": False}})
            p.handle_notification('admin',message)
    
    def test_handle_notification_not_persisting(self):
        p = Persister()        
        message = json.dumps({"timestamp": 1567704621,"metaAttrsFilter":{"shouldPersist": False}})
        p.handle_notification('admin',message)
    
    def test_handle_notification_invalid_json(self):
        p = Persister()        
        message = "This is a string"
        assert p.handle_notification('admin',message) is None
    
    def test_handle_notification_persisting(self):
        p = Persister()        
        message = json.dumps({"timestamp": 1567704621,"metaAttrsFilter":{"shouldPersist": True}})
        p.handle_notification('admin',message)

    
    #Testing handle_new_tenant
    
    @patch.object(Persister,'create_index_for_tenant')
    def test_handle_new_tenant(self,mock_index_for_tenant):
        message = json.dumps({"tenant":"normal"})
        p = Persister()
        p.handle_new_tenant('admin',message)
        assert mock_index_for_tenant.called

    
    #Testing handle_event_devices
    
    @patch.object(Persister,'create_indexes')
    def test_handle_event_devices_create(self,mock_create_indexes):
        message = json.dumps({
            "event":"device.create",
            "data":{"id":"e51k"},
            "meta":{"service":"admin"}
        })
        p = Persister()
        p.handle_event_devices('admin',message)
        assert mock_create_indexes.called


    @patch.object(Persister,'handle_event_data')
    @patch.object(Persister,'parse_message',return_value='message')
    def test_handle_event_devices_configure(self,mock_event_data,mock_parse_message):
        message = json.dumps({
            "event":"configure"
        })
        p = Persister()
        p.handle_event_devices('admin',message)
        assert mock_event_data.called

    #Testing handle_event_data
    def test_handle_event_data_invalid_json(self):
        p = Persister()
        message = "Test_Message"
        assert p.handle_event_data('admin',message) is None

    def test_handle_event_data_no_data(self):
        message = json.dumps({"data":None})
        assert Persister.handle_event_data(self,'admin', message) is None

    def test_handle_event_data_no_device_id(self):
        message = json.dumps({"data":{"foo":"bar"},"metadata":{"deviceid":None}})
        assert Persister.handle_event_data(self,'admin', message) is None
    
    def test_handle_event_data_no_timestamp(self):
        with pytest.raises(AttributeError):
            message = json.dumps({"data":{"foo":"bar"},"metadata":{"deviceid":"labtemp"}})
            Persister.handle_event_data(self,'admin', message)
    
    def test_handle_event_data_attrs_no_dict(self):
        message = json.dumps({
            "attrs":80,
            "metadata":{"deviceid":"labtemp","timestamp":1567704621,"tenant":"admin"}
            })
        p = Persister()
        p.handle_event_data('admin', message)

    def test_handle_event_data(self):
        message = json.dumps({
            "attrs":{"foo":"bar"},
            "metadata":{"deviceid":"labtemp","timestamp":1567704621,"tenant":"admin"}
            })
        p = Persister()
        p.handle_event_data('admin', message)

    
    #Testing parse_datetime
    
    def test_parse_datetime_error(self):
        with pytest.raises(TypeError):
            p = Persister()
            p.parse_datetime('1567704621')

    
    #Testing parse_message
    
    def test_parse_message(self):
        data = dict({"data":{
                "id":"testid",
                "attrs":{
                    "foo":"bar"
                }},
            "meta":{"timestamp":1567704621,"service":"admin"}
            })
        expected_data = json.dumps({
            "attrs":{"foo":"bar"},
            "metadata":
            {"timestamp":1567704621,"deviceid":"testid","tenant":"admin"}})        
        assert Persister.parse_message(self,data) == expected_data

    
    #Testing creating_index_for_tenant

    @patch.object(Persister,'create_indexes')
    def test_create_index_for_tenant(self,mock_create_indexes):
        p = Persister()
        p.create_index_for_tenant('admin')
        assert mock_create_indexes.called
    
    @patch.object(Persister,'create_indexes')
    def test_create_index_for_notifications(self,mock_create_index):
        p = Persister()
        p.create_indexes_for_notifications('admin')
        assert mock_create_index.called 
