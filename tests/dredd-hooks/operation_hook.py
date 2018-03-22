import dredd_hooks as hooks
import json

from history.subscriber.kafkaSubscriber import DeviceHandler, DataHandler

@hooks.before_each
def create__device(transaction):

    _create_device = {
        "event": "create",
        "meta": {
            "service": "admin"
        },
        "data": {
            "id": "labtemp",
            "label": "Device 1",
            "templates": [1, 2, 3],
            "attrs": {
            },
            "created": "2018-02-06T10:43:40.890330+00:00"
        }
    }
    dev_handler = DeviceHandler()
    dev_handler.handle_event(json.dumps(_create_device))

    _update_data = {
        "metadata": {
            "deviceid": "labtemp",
            "protocol": "mqtt",
            "payload": "json"
        },
        "attrs": {
            "temperature": "22.12"
        }
    }
    data_handler = DataHandler("admin")
    data_handler.handle_event(json.dumps(_update_data))
