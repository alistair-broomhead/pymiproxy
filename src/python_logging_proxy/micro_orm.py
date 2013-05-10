import sqlite3
from os import path
SQLITE_FILENAME = path.join(path.expanduser('~'),
                            '.python-logging-proxy.sqlite')

__author__ = 'Alistair Broomhead'


class SQLiteRecord(object):
    initial_sql = """CREATE TABLE IF NOT EXISTS log(
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
                   )"""

    db = SQLITE_FILENAME
    seen_entries = set()

    @classmethod
    def init_table(cls, db=None):
        with sqlite3.connect(db if db is not None else cls.db) as conn:
            conn.execute(cls.initial_sql)

    @classmethod
    def get_entry(cls, created, db=None):
        with sqlite3.connect(db if db is not None else cls.db) as conn:
            curs = conn.cursor()
            curs.execute("SELECT * FROM log WHERE Created=?", created)
            data = curs.fetchone()
        cls.seen_entries.add(data[0])
        return cls(*data)

    @classmethod
    def get_all(cls, db=None):
        with sqlite3.connect(db if db is not None else cls.db) as conn:
            curs = conn.cursor()
            curs.execute("SELECT * FROM log")
            while True:
                data = curs.fetchone()
                if data is None:
                    break
                cls.seen_entries.add(data[0])
                yield cls(*data)

    @classmethod
    def get_unseen(cls, db=None):
        with sqlite3.connect(db if db is not None else cls.db) as conn:
            curs = conn.cursor()
            curs.execute("SELECT * FROM log")
            while True:
                data = curs.fetchone()
                if data is None:
                    break
                if data[0] not in cls.seen_entries:
                    cls.seen_entries.add(data[0])
                    yield cls(*data)

    insertion_sql = """INSERT INTO log(
                        Created,
                        Name,
                        HostName,
                        Port,
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
                   ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? );
                   """

    @property
    def as_row(self):
        return (self.created,
                self.name,
                self.host_name,
                self.port,
                self.log_level,
                self.log_level_name,
                repr(self.message),
                self.args,
                self.module,
                self.func_name,
                self.line_no,
                self.exception,
                self.process,
                self.thread,
                self.threadName)

    def insert(self, db=None):
        with sqlite3.connect(db if db is not None else self.db) as conn:
            conn.execute(self.insertion_sql, self.as_row)

    def __init__(self,
                 created,
                 name,
                 host_name,
                 port,
                 log_level,
                 log_level_name,
                 message,
                 args,
                 module,
                 func_name,
                 line_no,
                 exception,
                 process,
                 thread,
                 threadName):
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
