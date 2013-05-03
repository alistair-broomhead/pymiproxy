#!/usr/bin/env python
from httplib import HTTPResponse
from socket import socket
from ssl import wrap_socket

from sys import argv
from proxy import ProxyHandler, UnsupportedSchemeException
from urlparse import urlparse, urlunparse, ParseResult


def print_to(heading, data):
    with open('logging-proxy.log', 'a') as logfile:
        logfile.write(heading)
        logfile.write("\n")
        logfile.write(data)
        logfile.write("\n")


class LoggingProxyHandler(ProxyHandler):

    def _connect_to_host(self):
        # Get hostname and port to connect to
        if self.is_connect:
            self.hostname, self.port = self.path.split(':')
        else:
            u = urlparse(self.path)
            if u.scheme != 'http':
                raise UnsupportedSchemeException('Unknown scheme %s' %
                                                 repr(u.scheme))
            self.hostname = u.hostname
            self.port = u.port or 80
            #Todo something where we log the response
            # noinspection PyArgumentList
            self.path = urlunparse(
                ParseResult(
                    scheme='',
                    netloc='',
                    params=u.params,
                    path=u.path or '/',
                    query=u.query,
                    fragment=u.fragment
                )
            )

        # Connect to destination
        self._proxy_sock = socket()
        self._proxy_sock.settimeout(10)
        self._proxy_sock.connect((self.hostname, int(self.port)))

        # Wrap socket if SSL is required
        if self.is_connect:
            self._proxy_sock = wrap_socket(self._proxy_sock)

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

        #Todo something where we log the request

        # Build request
        req = '%s %s %s\r\n' % (self.command, self.path, self.request_version)

        # Add headers to the request
        req += '%s\r\n' % self.headers

        # Append message body if present to the request
        if 'Content-Length' in self.headers:
            req += self.rfile.read(int(self.headers['Content-Length']))

        # Send it down the pipe!
        self._proxy_sock.sendall(self.mitm_request(req))

        # Parse response
        h = HTTPResponse(self._proxy_sock)
        h.begin()

        # Get rid of the pesky header
        del h.msg['Transfer-Encoding']

        # Time to relay the message across
        res = '%s %s %s\r\n' % (self.request_version, h.status, h.reason)
        res += '%s\r\n' % h.msg
        res += h.read()

        # Let's close off the remote end
        h.close()
        self._proxy_sock.close()

        # Relay the message
        self.request.sendall(self.mitm_response(res))


if __name__ == '__main__':
    from proxy import AsyncMitmProxy, DebugInterceptor
    proxy = None
    RequestHandlerClass = LoggingProxyHandler
    if not argv[1:]:
        proxy = AsyncMitmProxy(RequestHandlerClass=LoggingProxyHandler)
    else:
        proxy = AsyncMitmProxy(RequestHandlerClass=LoggingProxyHandler,
                               ca_file=argv[1])
    proxy.register_interceptor(DebugInterceptor)
    try:
        proxy.serve_forever()
    except KeyboardInterrupt:
        proxy.server_close()