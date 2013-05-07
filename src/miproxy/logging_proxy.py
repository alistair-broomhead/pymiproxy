#!/usr/bin/env python
from httplib import HTTPResponse

from sys import argv
from proxy import ProxyHandler

from handlers import SQLiteHandler, StdOutInfoHandler
from logging import Logger

SQLITE_HANDLER = SQLiteHandler(db="http_proxy.sqlite")
STDOUT_HANDLER = StdOutInfoHandler()
LOGGER = Logger(__name__)
LOGGER.addHandler(STDOUT_HANDLER)
LOGGER.addHandler(SQLITE_HANDLER)


class LoggingProxyHandler(ProxyHandler):

    def do_COMMAND(self):
        conn_data = {'hostname': self.hostname, 'port': self.port}

        # Is this an SSL tunnel?
        if not self.is_connect:
            try:
                # Connect to destination
                self._connect_to_host()
            except Exception, e:
                self.send_error(500, str(e))
                return
            # Extract path

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

        # Parse response
        h = HTTPResponse(self._proxy_sock)
        h.begin()
        res_d = {'status': h.status,
                 'reason': h.reason,
                 'req_version': req_d['req_version'],
                 'msg': h.msg,
                 'trans_enc': (h.msg['Transfer-Encoding']
                               if 'Transfer-Encoding' in h.msg
                               else '[NO-ENCODING]')}

        # Get rid of the pesky header
        del h.msg['Transfer-Encoding']

        # Time to relay the message across
        res = '%(req_version)s %(status)s %(reason)s\r\n%(msg)s\r\n' % res_d
        res_d['data'] = h.read()
        res += res_d['data']

        # Let's close off the remote end
        h.close()
        self._proxy_sock.close()

        # Relay the message
        self.request.sendall(self.mitm_response(res))

        req_d.update(conn_data)
        LOGGER.info('REQUEST: %s', req_d)

        res_d.update(conn_data)
        LOGGER.info('RESPONSE: %s', res_d)


if __name__ == '__main__':
    from proxy import AsyncMitmProxy
    proxy = None
    RequestHandlerClass = LoggingProxyHandler
    if not argv[1:]:
        proxy = AsyncMitmProxy(RequestHandlerClass=LoggingProxyHandler)
    else:
        proxy = AsyncMitmProxy(RequestHandlerClass=LoggingProxyHandler,
                               ca_file=argv[1])
    try:
        proxy.serve_forever()
    except KeyboardInterrupt:
        proxy.server_close()
