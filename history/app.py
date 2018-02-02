#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
App runner
"""
# System imports
import logging

# Third-party imports
import falcon

# Local imports
from history import settings
from history.api.models import DeviceHistory, STHHistory, AuthMiddleware

LOGGER = logging.getLogger('history.' + __name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.DEBUG)

# Create falcon app
app = falcon.API(middleware=[AuthMiddleware()])
app.add_route('/device/{device_id}/history', DeviceHistory())
app.add_route('/STH/v1/contextEntities/type/{device_type}/id/{device_id}/attributes/{attr}', STHHistory())

# Useful for debugging problems in API, it works with pdb
if __name__ == '__main__':
    from wsgiref import simple_server  # NOQA
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()
