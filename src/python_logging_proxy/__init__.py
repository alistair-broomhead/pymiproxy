#!/usr/bin/env python

__author__ = 'Alistair Broomhead'
__copyright__ = 'Copyright 2012, Mind Candy Ltd'
__credits__ = ['Alistair Broomhead', 'Nadeem Douba']

__license__ = 'GPL'
__maintainer__ = 'Alistair Broomhead'
__email__ = 'alistair.broomhead@gmail.com'
__status__ = 'Development'

__all__ = [
    'proxy', 'logging_proxy', 'handlers'
]

if __name__ == '__main__':
    from sys import argv
    from logging_proxy import main
    main(None if not argv[1:] else argv[1])
