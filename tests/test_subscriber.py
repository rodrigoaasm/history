from dojot.module.config import Config
import pytest
import json
import pymongo
import unittest
from unittest.mock import Mock, MagicMock, patch, call
from history.subscriber.persister import Persister, LoggingInterface, Auth
from dojot.module import Messenger, Config, Auth


class TestPersister:

    # Testing handle_notification method
    def test_handle_notification_no_timestamp(self):
        # raises exception because does not have "timestamp"
        with pytest.raises(Exception):
            p = Persister()
            message = json.dumps(
                {"ts": 1567704621, "metaAttrsFilter": {"shouldPersist": False}})
            p.handle_notification('admin', message)

    def test_handle_notification_not_persisting(self):
        p = Persister()
        message = json.dumps(
            {"timestamp": 1567704621, "metaAttrsFilter": {"shouldPersist": False}})
        p.handle_notification('admin', message)

    def test_handle_notification_invalid_json(self):
        p = Persister()
        message = "This is a string"
        assert p.handle_notification('admin', message) is None

    def test_handle_notification_persisting(self):
        p = Persister()
        message = json.dumps(
            {"timestamp": 1567704621, "metaAttrsFilter": {"shouldPersist": True}})
        p.handle_notification('admin', message)

    # Testing handle_new_tenant

    @patch.object(Persister, 'create_index_for_tenant')
    def test_handle_new_tenant(self, mock_index_for_tenant):
        message = json.dumps({"tenant": "normal"})
        p = Persister()
        p.handle_new_tenant('admin', message)
        assert mock_index_for_tenant.called

    # Testing handle_event_devices

    @patch.object(Persister, 'create_indexes')
    def test_handle_event_devices_create(self, mock_create_indexes):
        message = json.dumps({
            "event": "create",
            "data": {"id": "e51k"},
            "meta": {"service": "admin"}
        })
        p = Persister()
        p.handle_event_devices('admin', message)
        assert mock_create_indexes.called

    @patch.object(Persister, 'handle_event_data')
    @patch.object(Persister, 'parse_message', return_value='message')
    def test_handle_event_devices_configure(self, mock_event_data, mock_parse_message):
        message = json.dumps({
            "event": "configure"
        })
        p = Persister()
        p.handle_event_devices('admin', message)
        assert mock_event_data.called

    # Testing handle_event_data
    def test_handle_event_data_invalid_json(self):
        p = Persister()
        message = "Test_Message"
        assert p.handle_event_data('admin', message) is None

    def test_handle_event_data_no_data(self):
        message = json.dumps({"data": None})
        assert Persister.handle_event_data(self, 'admin', message) is None

    def test_handle_event_data_no_device_id(self):
        message = json.dumps(
            {"attrs": {"foo": "bar"}, "metadata": {"deviceid": None}})
        assert Persister.handle_event_data(self, 'admin', message) is None

    def test_handle_event_data_no_attrs(self):
        message = json.dumps(
            {"metadata": {"deviceid": "labtemp"}})
        assert Persister.handle_event_data(self, 'admin', message) is None

    def test_handle_event_data_no_timestamp(self):
        with pytest.raises(AttributeError):
            message = json.dumps(
                {"attrs": {"foo": "bar"}, "metadata": {"deviceid": "labtemp"}})
            Persister.handle_event_data(self, 'admin', message)

    def test_handle_event_data_attrs_no_dict(self):
        message = json.dumps({
            "attrs": 80,
            "metadata": {"deviceid": "labtemp", "timestamp": 1567704621, "tenant": "admin"}
        })
        p = Persister()
        p.handle_event_data('admin', message)

    def test_handle_event_data(self):
        message = json.dumps({
            "attrs": {"foo": "bar"},
            "metadata": {"deviceid": "labtemp", "timestamp": 1567704621, "tenant": "admin"}
        })
        p = Persister()
        p.handle_event_data('admin', message)

    # Testing parse_datetime

    def test_parse_datetime_error(self):
        with pytest.raises(TypeError):
            p = Persister()
            p.parse_datetime('1567704621')

    # Testing parse_message

    def test_parse_message(self):
        data = dict({"data": {
            "id": "testid",
            "attrs": {
                    "foo": "bar"
                    }},
            "meta": {"timestamp": 1567704621, "service": "admin"}
        })
        expected_data = json.dumps({
            "attrs": {"foo": "bar"},
            "metadata":
            {"timestamp": 1567704621, "deviceid": "testid", "tenant": "admin"}})
        assert Persister.parse_message(self, data) == expected_data

    # Testing creating_index_for_tenant

    @patch.object(Persister, 'create_indexes')
    def test_create_index_for_tenant(self, mock_create_indexes):
        p = Persister()
        p.create_index_for_tenant('admin')
        assert mock_create_indexes.called

    @patch.object(Persister, 'create_indexes')
    def test_create_index_for_notifications(self, mock_create_index):
        p = Persister()
        p.create_indexes_for_notifications('admin')
        assert mock_create_index.called

    @patch.object(Persister, 'create_indexes')
    def test_init_mongodb(self, mock_create_indexes):
        p = Persister()
        p.init_mongodb('admin_notifications')
        assert mock_create_indexes.called

    @patch.object(pymongo.collection.Collection, 'create_index')
    def test_init_mongodb_create_index(self, mock_create_index):
        p = Persister()
        p.init_mongodb('admin_notifications')
        assert mock_create_index.call_count == 3

    @patch.object(pymongo.collection.Collection, 'create_index')
    @patch.object(pymongo.database.Database, 'command')
    def test_enable_collection_sharding(self, mock_command, mock_create_index):
        p = Persister()
        p.init_mongodb()
        p.enable_collection_sharding('admin_notifications')
        mock_create_index.assert_called_once()
        assert mock_command.call_count == 2


class TestLoggingInterface(unittest.TestCase):

    def test_on_get(self):
        li = LoggingInterface()
        resp = type('obj', (object,), {'body': None, 'status': None})
        li.on_get(None, resp)
        assert resp.body == '{"log_level": "INFO"}'
        assert resp.status == '200 OK'

    def test_on_put(self):
        li = LoggingInterface()
        req = type('obj', (object,), {'params': {'level': 'DEBUG'}})
        resp = type('obj', (object,), {'body': None, 'status': None})
        li.on_put(req, resp)
        assert resp.body == '{"new_log_level": "DEBUG"}'
        assert resp.status == '200 OK'

    @patch('history.subscriber.persister.falcon.HTTPInvalidParam', side_effect=Exception('invalid_param'))
    def test_on_put_invalid(self, mock_invalid_param):
        li = LoggingInterface()
        req = type('obj', (object,), {'params': {'level': 'WARN'}})
        with self.assertRaises(Exception) as context:
            li.on_put(req, None)
        self.assertTrue('invalid_param' in str(context.exception))


@patch.object(Persister, 'create_indexes')
@patch.object(Config, 'load_defaults')
@patch('history.subscriber.persister.Messenger')
def test_persist_all_events(mock_messenger, mock_config, mock_create_indexes):

    from history.subscriber.persister import start_dojot_messenger
    from history import conf

    p = Persister()
    p.create_indexes_for_notifications('admin')

    mock_config.dojot = {
        "management": {
            "user": "dojot-management",
            "tenant": "dojot-management"
        },
        "subjects": {
            "tenancy": "dojot.tenancy",
            "devices": "dojot.device-manager.device",
            "device_data": "device-data"
        }
    }

    # test persist all boolean valued events
    start_dojot_messenger(mock_config, p, False)
    mock_messenger.assert_called_once_with("Persister", mock_config)

    mock_messenger().create_channel.assert_any_call("dojot.notifications", "r")

    mock_messenger().on.assert_any_call(mock_config.dojot['subjects']['tenancy'],"message", p.handle_new_tenant)

    mock_messenger().on.assert_any_call("dojot.notifications", "message",p.handle_notification)

    mock_messenger().create_channel.assert_any_call(mock_config.dojot['subjects']['devices'], "r")

    mock_messenger().create_channel.assert_any_call(mock_config.dojot['subjects']['device_data'], "r")

    mock_messenger().on.assert_any_call(mock_config.dojot['subjects']['devices'],"message", p.handle_event_devices)

    mock_messenger().on.assert_any_call(mock_config.dojot['subjects']['device_data'],"message", p.handle_event_data)


@patch.object(Persister, 'create_indexes')
@patch.object(Config, 'load_defaults')
@patch('history.subscriber.persister.Messenger')
def test_persist_only_notifications(mock_messenger, mock_config, create_indexes):

    from history.subscriber.persister import start_dojot_messenger
    from history import conf
    p = Persister()
    p.create_indexes_for_notifications('admin')

    mock_config.dojot = {
        "management": {
            "user": "dojot-management",
            "tenant": "dojot-management"
        },
        "subjects": {
            "tenancy": "dojot.tenancy",
            "devices": "dojot.device-manager.device",
            "device_data": "device-data"
        }
    }
    # test persist only boolean valued notifications
    start_dojot_messenger(mock_config, p, True)

    mock_messenger.assert_called_once_with("Persister", mock_config)

    mock_messenger().create_channel.assert_any_call("dojot.notifications", "r")

    mock_messenger().on.assert_any_call(mock_config.dojot['subjects']['tenancy'],
                                        "message", p.handle_new_tenant)

    mock_messenger().on.assert_any_call("dojot.notifications", "message",
                                        p.handle_notification)


def test_str2_bool_return_true():
    from history.subscriber.persister import str2_bool

    assert True is str2_bool('true')
    assert True is str2_bool('yes')
    assert True is str2_bool('t')
    assert True is str2_bool('1')


def test_str2_bool_return_false():
    from history.subscriber.persister import str2_bool

    assert False is str2_bool('false')
    assert False is str2_bool('no')
    assert False is str2_bool('f')
    assert False is str2_bool('0')


@patch.object(Auth, 'get_tenants', return_value=None)
@patch.object(Persister, 'init_mongodb')
@patch.object(Persister, 'create_indexes_for_notifications')
@patch('history.subscriber.persister.start_dojot_messenger')
@patch('history.subscriber.persister.falcon.API')
@patch('history.subscriber.persister.simple_server')
def test_persister_main(mock_simple_server, mock_falcon_api, mock_start_dojot_messenger, mock_create_indexes_for_notifications,
                        mock_init_mongodb, mock_get_tenants):
    from history.subscriber.persister import main
    main()
    assert mock_init_mongodb.called
    assert mock_get_tenants.called
    assert mock_create_indexes_for_notifications.called
    assert mock_start_dojot_messenger.called
    assert mock_falcon_api.called
    assert mock_simple_server.make_server.called
