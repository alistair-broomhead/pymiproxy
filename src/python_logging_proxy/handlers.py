"""
SQLiteHandler Taken mainly from
    https://gist.github.com/ykessler/2662203#file_sqlite_handler.py
Some minor reformatting, mostly whitespace, plus change from python string
parameters to sql parameters

StdOutHandler just prints log messages to stdout
"""
import logging
from python_logging_proxy.micro_orm import SQLiteRecord, SQLITE_FILENAME


class SQLiteHandler(logging.Handler):
    """
    Logging handler for SQLite.

    Based on Vinay Sajip's DBHandler class
    (http://www.red-dove.com/python_logging.html)

    This version sacrifices performance for thread-safety:
    Instead of using a persistent cursor, we open/close connections for each
    entry.

    AFAIK this is necessary in multi-threaded applications,
    because SQLite doesn't allow access to objects across threads.
    """

    def __init__(self, db=SQLITE_FILENAME):

        logging.Handler.__init__(self)
        self.db = db
        # Create table if needed:
        SQLiteRecord.init_table(db)

    def emit(self, record):
        # Use default formatting:
        self.format(record)
        if record.exc_info:
            record.exc_text = logging._defaultFormatter\
                                     .formatException(record.exc_info)
        else:
            record.exc_text = ""
        # Insert log record:
        SQLiteRecord(record.created,
                     record.name,
                     record.args['request']['hostname'],
                     record.args['request']['port'],
                     record.levelno,
                     record.levelname,
                     record.msg,
                     record.args,
                     record.module,
                     record.funcName,
                     record.lineno,
                     record.exc_text,
                     record.process,
                     record.thread,
                     record.threadName).insert(self.db)


class StdOutHandler(logging.Handler):
    """
    Logging to stdout.
    """
    def emit(self, record):
        print record.msg % record.args
