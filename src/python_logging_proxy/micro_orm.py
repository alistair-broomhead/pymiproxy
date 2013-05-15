import sqlite3
from os import path
from collections import OrderedDict
from contextlib import contextmanager

SQLITE_FILENAME = path.join(path.expanduser('~'),
                            '.python-logging-proxy.sqlite')

__author__ = 'Alistair Broomhead'


class SQLiteRecord(object):

    def __repr__(self):
        path = self.args['request']['path']
        data = self.args['response']['data']
        return "<SQLiteRecord for " \
               "%(path)s at " \
               "%(created)r =: " \
               "%(response)r at " \
               "%(hex_id)s>" %\
               {'hex_id': hex(id(self)),
                'path': path.split('?')[0],
                'created': self.created,
                'response': data}

    def __init__(self,
                 created, name, host_name, port,
                 log_level, log_level_name, message,
                 args, module, func_name, line_no,
                 exception, process, thread, threadName):
        self.created = created
        self.name = name
        self.host_name = host_name
        self.port = port
        self.log_level = log_level
        self.log_level_name = log_level_name
        self.message = message
        if isinstance(args, basestring):
            self.args = eval(args)
        else:
            self.args = args
        self.module = module
        self.func_name = func_name
        self.line_no = line_no
        self.exception = exception
        self.process = process
        self.thread = thread
        self.threadName = threadName

    db = SQLITE_FILENAME
    seen_entries = OrderedDict()

    # noinspection PyPropertyDefinition
    @classmethod
    def last_seen(cls, recheck=False, db=None):
        if recheck:
            for _ in cls.get_unseen(db):
                pass
        key = next(reversed(cls.seen_entries))
        return cls.seen_entries[key]

    @classmethod
    def _see(cls, data):
        if data[0] not in cls.seen_entries:
            cls.seen_entries[data[0]] = SQLiteRecord(*data)
        return cls.seen_entries[data[0]]

    @classmethod
    @contextmanager
    def _conn_db(cls, db=None):
        with sqlite3.connect(db if db is not None else cls.db) as conn:
            yield conn

    @classmethod
    def init_table(cls, db=None):
        with cls._conn_db(db) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS log(
                        Created float PRIMARY KEY,
                        Name text,
                        HostName text,
                        Port int,
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
                   )""")

    @classmethod
    def get_entry(cls, created, db=None):
        with cls._conn_db(db) as conn:
            curs = conn.cursor()
            curs.execute("SELECT * FROM log WHERE Created=?", (created,))
            data = curs.fetchone()
        yield cls._see(data)

    @classmethod
    def get_all(cls, db=None):
        unseen = cls.get_unseen(db)
        for k in cls.seen_entries:
            yield cls.seen_entries[k]
        for entry in unseen:
            yield entry

    @classmethod
    def get_unseen(cls, db=None):
        created = cls.last_seen().created if cls.seen_entries else 0
        with cls._conn_db(db) as conn:
            curs = conn.cursor()
            for row in curs.execute("SELECT * FROM log WHERE Created>?",
                                    (created,)):
                yield cls._see(row)

    @property
    def as_row(self):
        return (self.created,
                self.name,
                self.host_name,
                self.port,
                self.log_level,
                self.log_level_name,
                self.message,
                repr(self.args),
                self.module,
                self.func_name,
                self.line_no,
                self.exception,
                self.process,
                self.thread,
                self.threadName)

    def insert(self, db=None):
        with self._conn_db(db) as conn:
            conn.execute(
                """INSERT INTO log( Created, Name, HostName, Port,
                                    LogLevel, LogLevelName, Message, Args,
                                    Module, FuncName, LineNo, Exception,
                                    Process, Thread, ThreadName )
                   VALUES (         ?, ?, ?, ?,
                                    ?, ?, ?, ?,
                                    ?, ?, ?, ?,
                                    ?, ?, ? ); """,
                self.as_row)
