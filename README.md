#python-logging-proxy - Python Micro Interceptor Proxy with logging

A small and sweet logging man-in-the-middle proxy workig from pymiproxy.


##Introduction

python-logging-proxy is an addition on top of pymiproxy which gtives logging to
a sqlite database, which can then be used as you like.

##Installation Requirements

The following modules are required:

- pyOpenSSL
- pyMIProxy


##Installation

Just run the following command at the command prompt:

```bash
$ sudo pip install python-logging-proxy
```

##Usage

To start python-logging-proxy run:

```bash
$ python -m python_logging_proxy
```

This will log to the command line and also to a sqlite database


##Extending or Implementing python_logging_proxy

Please see the documentation for `pymiproxy` and for the python standard library
`logger` module. The proxy itself can be extended exactly as `pymiproxy`,
either by registering an interceptor or method overloading. As for the logging
it is possible to add filters, handlers etc to the LoggingProxyHandler.logger
class property.


##Kudos

Thanks to the great documentation at python.org, and Nadeem Douba for pymiproxy,
which provides a good chunk the functionality I wanted when I started this
project.

##Contributing

Please feel free to add issues to the github project, fork, pull, push, and
otherwise fold spindle and mutilate - as per the License below. For help with
usage and extenseion please feel free to get in touch either through issues,
or by email.

##License

The MIT License (MIT)

Copyright (c) 2013 Alistair Broomhead

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
