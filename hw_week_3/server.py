#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import uuid
import redis
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from api import method_handler
from store import Store

HOST = "localhost"
PORT = 8080

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500

ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler,
    }
    store = Store()

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        logging.debug(f'CONTEXT: {context}')
        request = None
        try:
            logging.debug('GET DATA STRING')
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            logging.debug(f'DATA STRING RECEIVED: {data_string}')
            request = json.loads(data_string)
            logging.info(f'REQUEST: {request}')
        except ValueError as e:
            logging.info('EXCEPTION: BAD REQUEST')
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.debug("FOR %s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    code, response = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except KeyError:
                    logging.info("EXCEPTION: UNEXPECTED API METHOD")
                    code = INVALID_REQUEST
                except redis.exceptions.ConnectionError as e:
                    logging.exception("REDIS CONNECTION ERROR: %s" % e)
                    code = INTERNAL_ERROR
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"code": code, "response": response}
        else:
            r = {"code": code, "error": response or ERRORS.get(code, "Unknown Error")}
        context.update(r)
        logging.debug(context)
        logging.info(f'RESPONSE: {r}')
        self.wfile.write(json.dumps(r).encode('utf-8'))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=PORT)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer((HOST, opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
