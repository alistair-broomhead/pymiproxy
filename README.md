#python-logging-proxy - Python Micro Interceptor Proxy with logging

A small and sweet man-in-the-middle proxy capable of doing HTTP and HTTP over SSL, forked and extended from https://github.com/allfro/pymiproxy.


##Introduction

pymiproxy is a small, lightweight, man-in-the-middle proxy capable of performing HTTP and HTTPS (or SSL) inspection. The
proxy provides a built-in certificate authority that is capable of generating certificates for SSL-based destinations.
Pymiproxy is also extensible and provides two methods for extending the proxy: method overloading, and a pluggable
interface. It is ideal for situations where you're in dire need of a cool proxy to tamper with out- and/or in-bound HTTP
data. python-logging-proxy is an addition on top of this which gtives logging to a sqlite database, which can then be used as you like.

##Installation Requirements

The following modules are required:

- pyOpenSSL


##Installation

Just run the following command at the command prompt:

```bash
$ sudo python setup.py install
```

##Usage

The module offers a few examples in the code. In brief, pymiproxy can be run right-away by issuing the following command
at the the command-prompt:

```bash
$ python -m python_logging_proxy.proxy
```

This will invoke pymiproxy with the ```DebugInterceptor``` plugin which simply outputs the first 100 bytes of each request
and response. The proxy runs on port 8080 and listens on all addresses. Go ahead and give it a try.

To start python-logging-proxy run:

```bash
$ python -m python_logging_proxy.logging_proxy
```

This will log to the command line and also to a sqlite database


##Extending or Implementing python_logging_proxy

There are two ways of extending the proxy:


- Develop and register an Interceptor plugin; or
- Overload the ```mitm_request```, and ```mitm_response``` methods in the ```ProxyHandler``` class.


The decision on which method you choose to use is entirely dependant on whether or not you wish to push the data being
intercepted through a set of interceptors or not.

###Interceptor Plugins

There are currently two types of interceptor plugins:

- ```RequestInterceptorPlugins```: executed prior to sending the request to the remote server; and
- ```ResponseInterceptorPlugins```: executed prior to sending the response back to the client.

The following flow is taken by python-logging-proxy in this mode:

1. Client request received
2. Client request parsed
3. Client request processed/transformed by Request Interceptor plugins
4. Updated request sent to remote server
5. Response received by remote server
6. Response processed/transformed by Response Interceptor plugins
7. Updated response sent to client

You can register as many plugins as you wish. However, keep in mind that plugins are executed in the order that they are
registered in. Take care in how you register your plugins if the result of one plugin is dependent on the result of
another.

The following is a simple code example of how to run the proxy with plugins:

    from python_logging_proxy.proxy import RequestInterceptorPlugin, ResponseInterceptorPlugin, AsyncMitmProxy

    class DebugInterceptor(RequestInterceptorPlugin, ResponseInterceptorPlugin):

            def do_request(self, data):
                print '>> %s' % repr(data[:100])
                return data

            def do_response(self, data):
                print '<< %s' % repr(data[:100])
                return data


    if __name__ == '__main__':
        proxy = None
        if not argv[1:]:
            proxy = AsyncMitmProxy()
        else:
            proxy = AsyncMitmProxy(ca_file=argv[1])
        proxy.register_interceptor(DebugInterceptor)
        try:
            proxy.serve_forever()
        except KeyboardInterrupt:
            proxy.server_close()

###Method Overloading

The alternate approach to extending the proxy functionality is to subclass the ProxyHandler class and overload the
```mitm_request``` and ```mitm_response``` methods. The following is a quick example:

    from python_logging_proxy.proxy import AsyncMitmProxy

    class MitmProxyHandler(ProxyHandler):

        def mitm_request(self, data):
            print '>> %s' % repr(data[:100])
            return data

        def mitm_response(self, data):
            print '<< %s' % repr(data[:100])
            return data


    if __name__ == '__main__':
        proxy = None
        if not argv[1:]:
            proxy = AsyncMitmProxy(RequestHandlerClass=MitmProxyHandler)
        else:
            proxy = AsyncMitmProxy(RequestHandlerClass=MitmProxyHandler, ca_file=argv[1])
        try:
            proxy.serve_forever()
        except KeyboardInterrupt:
            proxy.server_close()

Note: In both cases, the methods that process the data need to return the data back to the proxy handler. Otherwise,
you'll get an exception.

##Kudos

Thanks to the great documentation at python.org, GnuCitizen's PDP for the ideas, the pyOpenSSL group for making a great
OpenSSL API, and last but not least Nadeem Douba for pymiproxy, which this extends.

##Contributing

For anything in proxy.py please contact the maintainer of https://github.com/allfro/pymiproxy about pulling your changes, and let me know to pull those from him. For changes to any other modules, please contact me directly.

