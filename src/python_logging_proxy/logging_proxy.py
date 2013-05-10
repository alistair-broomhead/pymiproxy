#!/usr/bin/env python
from httplib import HTTPResponse
from sys import argv
from logging import Logger

from python_logging_proxy.proxy import ProxyHandler
from python_logging_proxy.handlers import (SQLiteHandler,
                                           StdOutHandler,
                                           SQLITE_FILENAME)


class LoggingProxyHandler(ProxyHandler):
    logger = Logger(__name__)

    def _get_request(self):
        req_d = {'command': self.command,
                 'path': self.path,
                 'req_version': self.request_version,
                 'headers': self.headers}
        # Build request including headers
        req = '%(command)s %(path)s %(req_version)s\r\n%(headers)s\r\n' % req_d
        # Append message body if present to the request
        if 'Content-Length' in self.headers:
            req += self.rfile.read(int(self.headers['Content-Length']))
        # Send it down the pipe!
        self._proxy_sock.sendall(self.mitm_request(req))
        print req
        # Time to relay the message across
        return req_d

    def _get_response(self):

        # Parse response
        h = HTTPResponse(self._proxy_sock)
        h.begin()
        res_d = {'status': h.status,
                 'reason': h.reason,
                 'req_version': self.request_version,
                 'msg': h.msg,
                 'trans_enc': (h.msg['Transfer-Encoding']
                               if 'Transfer-Encoding' in h.msg
                               else '[NO-ENCODING]')}
        # Get rid of the pesky header
        del h.msg['Transfer-Encoding']

        res = '%(req_version)s %(status)s %(reason)s\r\n%(msg)s\r\n' % res_d
        res_d['data'] = h.read()
        res += res_d['data']
        # Let's close off the remote end
        h.close()
        self._proxy_sock.close()
        # Relay the message
        self.request.sendall(self.mitm_response(res))
        print res
        return res_d

    def do_COMMAND(self):
        # Is this an SSL tunnel?
        if not self.is_connect:
            try:
                # Connect to destination
                self._connect_to_host()
            except Exception, e:
                self.send_error(500, str(e))
                return
            # Extract path

        conn_data = {'hostname': self.hostname, 'port': self.port}
        req_d = self._get_request()
        res_d = self._get_response()

        # Do our logging
        req_d['headers'] = req_d['headers'].__dict__
        del req_d['headers']['fp']
        req_d.update(conn_data)
        res_d['msg'] = res_d['msg'].__dict__
        del res_d['msg']['fp']
        res_d.update(conn_data)

        transferred = {"request": req_d, "response": res_d}
        self.logger.info("REQUEST: %(request)s\nRESPONSE: %(response)s",
                         transferred)

LoggingProxyHandler.logger.addHandler(StdOutHandler())
LoggingProxyHandler.logger.addHandler(SQLiteHandler(db=SQLITE_FILENAME))


if __name__ == '__main__':
    from python_logging_proxy.proxy import AsyncMitmProxy
    proxy = None
    if not argv[1:]:
        proxy = AsyncMitmProxy(RequestHandlerClass=LoggingProxyHandler)
    else:
        proxy = AsyncMitmProxy(RequestHandlerClass=LoggingProxyHandler,
                               ca_file=argv[1])
    try:
        proxy.serve_forever()
    except KeyboardInterrupt:
        proxy.server_close()
