# -*- coding: utf-8 -*-
import json
import io
import falcon
import pandas as pd

def validate_accept_header(request):
    """ Validates if the http accept header is supported by the api """
    if not (request.client_accepts("application/json") or request.client_accepts("text/csv")):
        raise falcon.HTTPNotAcceptable("Not Acceptable")
    return
    

def build_response_body(request, history, csv_parser= None):
    """ Format the response according to the type entered in http accept header.
        It is possible enter a method to perform specific formatting of a route before parsing csv
    """
    if request.client_accepts("application/json"):
        return json.dumps(history)
    elif request.client_accepts('text/csv'):
        history_parsed = csv_parser(history) if csv_parser else history
        csv_buffer = io.StringIO();
        history_normalized = pd.json_normalize(history_parsed)
        history_normalized.to_csv(csv_buffer, index=False, encoding="utf-8")
        return csv_buffer.getvalue()
    
    raise falcon.HTTPNotAcceptable("Not Acceptable")
    
    