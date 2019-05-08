#!/usr/bin/env python
"""
A simple webserver for data preparation.

This script should be run from the command line with 2 arguments:

  * the survey_id to use
  * a tcp port number

It will run a webserver on the specified port and allow the user
to paste indicator formulas (compatible with the specified survey)
into a text field. The formulas will then be checked and errors
shown. If the formulas are correct, the user can select the
survey responses (by number and submit date) for which the
indicators shall be calculated and exported in JSON format.

The resulting JSON file is to be used in the visualization app.
"""

import json
import base64
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import BaseServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
from pprint import pprint

from . import indicators
from . import responses
from .files import get_indicator_definitions, export_all

def get_html_page(html_content):
    return """<head>
<title>Data extractor</title>
</head>
<body>
<h1>Data extractor</h1>
{}
</body>
""".format(html_content)


def get_html_form_formulas(text="# Example\nIND1: '''(CIGOV1 + CIGOV2) / 2'''"):
     return """
<form id="form_formulas" action="/formulas" method="post">
    <label class="grey" for="log">Please enter the indicator formulas</label><br />
    <textarea name="formulas" style="width:99%" id="formulas" rows="30" cols="60">{}</textarea><br>
    <input type="submit" id="submitbtn" name="submit" value="SUBMIT" class="button"><br />
</form>
""".format(text)


def get_html_form_responses(formulas, response_ids_submitdates=None):
    if not response_ids_submitdates:
        return 'Sorry, no COMPLETE responses found.'
    options = []
    for id in sorted(response_ids_submitdates.keys()):
        sd = response_ids_submitdates[id]
        options.append('         <option value="%s">%s (%s)</option>'
                                         % (str(id), str(id), str(sd)))
    options_html = '\n'.join(options)
    return """<br />
<form id="form_responses" action="/responses" method="post">
    <input type="hidden" name="formulas" id="formulas" value="{}" />
    <label class="grey" for="log">Please select the responses to export</label><br />
    <select multiple size="10" name="response_ids" id="response_ids">\n
{}
    </select>
    <input type="submit" id="submitbtn" name="submit" value="SUBMIT" class="button"><br />
</form>
""".format(base64.b64encode(json.dumps(formulas).encode('utf-8')).decode('utf-8'), options_html)


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        default_indicator_definitions = get_indicator_definitions()
        self.wfile.write(get_html_page(get_html_form_formulas(
            default_indicator_definitions)).encode('utf-8'))

    def parse_POST(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(
                self.rfile.read(length),
                keep_blank_values=1
            )
        else:
            postvars = {}
        res = {}
        for k, vals in postvars.items():
            res[k.decode('utf-8')] = [v.decode('utf-8') for v in vals]
        return res

    def do_POST(self):
        try:
            postvars = self.parse_POST()
        except Exception as e:
            print('Invalid request', str(e))
            self.do_GET()
        if self.path == '/formulas':
            try:
                formulas = postvars.get('formulas')[0]
            except:
                self.do_GET()
            status_ok, problems, _ = indicators.check_indicators(survey_id, formulas)
            if status_ok:
                r = responses.get_responses(survey_id)
                if r:
                    _, resp_meta = r
                    response_ids_submitdates = responses.get_response_ids_submitdates(resp_meta)
                    html = get_html_form_responses(formulas, response_ids_submitdates)
                else:
                    html = 'Formulas seem ok.<br />But sorry, no COMPLETE responses yet.'
            else:
                html = get_html_form_formulas(text=formulas)
                ind_errors = []
                for ind_name in problems:
                    ind_errors.append('____________ indicator %s ____________\n' % ind_name
                                      + '\n'.join(problems[ind_name]))
                all_error_msgs = '\n\n'.join(ind_errors)
                html += '<pre>' + all_error_msgs + '</pre>'
        elif self.path == '/responses':
            formulas_ = postvars.get('formulas')[0]
            res = None
            if postvars.get('response_ids'):
                response_ids = [int(float(id)) for id in postvars.get('response_ids')]
                formulas = json.loads(base64.b64decode(formulas_).decode('utf-8'))
                _, _, inds = indicators.check_indicators(survey_id, formulas)
                res = responses.get_responses(survey_id)
            if res is not None:
                resp, resp_meta = res
                ind_vals, errors = indicators.calculate_indicators(survey_id, inds, resp, response_ids)
                result = {
                    'indicators': {ind.name: ind.formula for ind in inds},
                    'responses': {id: resp[id] for id in response_ids},
                    'results': ind_vals,
                    'errors': errors,
                }
            else:
                result = 'Error. Sorry, no result.'
            #pprint(result)
            html = '<pre>\n%s\n</pre>' % json.dumps(result, indent=4, sort_keys=True)
            export_all(result)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(get_html_page(html).encode('utf-8'))


def main(HandlerClass = RequestHandler,
        ServerClass = HTTPServer,
        port=8000):
    server_address = ('', port)  # (address, port)
    httpd = ServerClass(server_address, HandlerClass)
    sa = httpd.socket.getsockname()
    print('Serving HTTP on', sa[0], 'port', sa[1], '...')
    httpd.serve_forever()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('Usage:   python server.py {survey_id} {webserver_port}')
    else:
        survey_id = sys.argv[1]
        port = int(float(sys.argv[2]))
        main(port=port)
