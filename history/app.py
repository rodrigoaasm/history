#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
App runner
"""
# System imports
# Third-party imports
import falcon

# Local imports
from history import conf, Logger
from history.api.models import DeviceHistory, STHHistory, AuthMiddleware, NotificationHistory, LoggingInterface

#init logger
logger = Logger.Log(conf.log_level).color_log()

# Create falcon app
app = falcon.API(middleware=[AuthMiddleware()])
app.add_route('/device/{device_id}/history', DeviceHistory())
app.add_route('/notifications/history', NotificationHistory())
app.add_route('/STH/v1/contextEntities/type/{device_type}/id/{device_id}/attributes/{attr}', STHHistory())
app.add_route('/log', LoggingInterface())
logger.info('Preparing API routes..')


# Useful for debugging problems in API, it works with pdb
if __name__ == '__main__':
    from wsgiref import simple_server  # NOQA
    httpd = simple_server.make_server('127.0.0.1', 8008, app)
    httpd.serve_forever()
