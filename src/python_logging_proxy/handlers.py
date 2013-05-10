"""
SQLiteHandler Taken mainly from
    https://gist.github.com/ykessler/2662203#file_sqlite_handler.py
Some minor reformatting, mostly whitespace, plus change from python string
parameters to sql parameters

StdOutHandler just prints log messages to stdout
"""
import sqlite3
import logging
import time
from os import path


SQLITE_FILENAME = path.join(path.expanduser('~'),
                            '.python-logging-proxy.sqlite')


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

    initial_sql = """CREATE TABLE IF NOT EXISTS log(
                        Created text,
                        Name text,
                        LogLevel int,
                        LogLevelName text,
                        Message text,
                        Args text,
                        Module text,
                        FuncName text,
                        LineNo int,
                        Exception text,
                        Process int,
                        Thread text,
                        ThreadName text
                   )"""

    insertion_sql = """INSERT INTO log(
                        Created,
                        Name,
                        LogLevel,
                        LogLevelName,
                        Message,
                        Args,
                        Module,
                        FuncName,
                        LineNo,
                        Exception,
                        Process,
                        Thread,
                        ThreadName
                   ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? );
                   """

    def __init__(self, db=SQLITE_FILENAME):

        logging.Handler.__init__(self)
        self.db = db
        # Create table if needed:
        conn = sqlite3.connect(self.db)
        conn.execute(SQLiteHandler.initial_sql)
        conn.commit()

    def formatDBTime(self, record):
        record.dbtime = time.strftime("%Y-%m-%d %H:%M:%S",
                                      time.localtime(record.created))

    def emit(self, record):

        # Use default formatting:
        self.format(record)
        # Set the database time up:
        self.formatDBTime(record)
        if record.exc_info:
            record.exc_text = logging._defaultFormatter\
                                     .formatException(record.exc_info)
        else:
            record.exc_text = ""
        # Insert log record:
        conn = sqlite3.connect(self.db)
        params = (record.dbtime,
                  record.name,
                  record.levelno,
                  record.levelname,
                  record.msg,
                  repr(record.args),
                  record.module,
                  record.funcName,
                  record.lineno,
                  record.exc_text,
                  record.process,
                  record.thread,
                  record.threadName)
        conn.execute(self.insertion_sql, params)
        conn.commit()


class StdOutHandler(logging.Handler):
    """
    Logging to stdout.
    """
    def emit(self, record):
        print record.msg % record.args
