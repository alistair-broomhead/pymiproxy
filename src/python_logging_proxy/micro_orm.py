import sqlite3
from os import path
from collections import OrderedDict
from contextlib import contextmanager
from abc import ABCMeta, abstractproperty, abstractmethod

__author__ = 'Alistair Broomhead'

identity = lambda x: x


class SQLBase(object):
    db = path.join(path.expanduser('~'),
                   'python-logging-proxy.sqlite')
    sql_schema = abstractproperty(lambda _: '')
    sql_insert = abstractproperty(lambda _: '')
    _flds = abstractproperty(lambda _: {})

    @property
    def as_row(self):
        return tuple(func(getattr(self, key))
                     for (key, func) in self._flds.items())

    def _process_init_kwargs(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __init__(self, **kwargs):
        self._process_init_kwargs(**kwargs)

    def _identifying_data(self):
        return ''

    def __repr__(self):
        return "<%(class_name)s%(ident)s at %(hex_id)s>" % \
               {'class_name': type(self).__name__,
                'hex_id': hex(id(self)),
                'ident': self._identifying_data()}

    @classmethod
    @contextmanager
    def _conn_db(cls, db=None):
        with sqlite3.connect(db if db is not None else cls.db) as conn:
            yield conn

    @classmethod
    def init_table(cls, db=None):
        with cls._conn_db(db) as conn:
            conn.execute(cls.sql_schema)

    def insert(self, db=None):
        with self._conn_db(db) as conn:
            conn.execute(self.sql_insert, self.as_row)


def _SQLiteRecord_fields():
    sql_schema = """CREATE TABLE IF NOT EXISTS log(
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
    sql_insert = """INSERT INTO log( Created, Name, HostName, Port,
                                    LogLevel, LogLevelName, Message, Args,
                                    Module, FuncName, LineNo, Exception,
                                    Process, Thread, ThreadName )
                   VALUES (         ?, ?, ?, ?,
                                    ?, ?, ?, ?,
                                    ?, ?, ?, ?,
                                    ?, ?, ? ); """
    _flds = OrderedDict([('created', identity),
                         ('name', identity),
                         ('host_name', identity),
                         ('port', identity),
                         ('log_level', identity),
                         ('log_level_name', identity),
                         ('message', identity),
                         ('args', repr),
                         ('module', identity),
                         ('func_name', identity),
                         ('line_no', identity),
                         ('exception', identity),
                         ('process', identity),
                         ('thread', identity),
                         ('threadName', identity)])
    return sql_schema, sql_insert, _flds


class SQLiteRecord(SQLBase):
    sql_schema, sql_insert, _flds = _SQLiteRecord_fields()
    seen_entries = OrderedDict()

    def _identifying_data(self):
        return " for %(path)s at %(created)r =: %(response)r" % \
               {'path': self.args['request']['path'].split('?')[0],
                'created': self.created,
                'response': self.args['response']['data']}

    def __init__(self, created, name, host_name, port, log_level,
                 log_level_name, message, args, module, func_name, line_no,
                 exception, process, thread, threadName):
        super(SQLiteRecord, self).__init__(created=created,
                                           name=name,
                                           host_name=host_name,
                                           port=port,
                                           log_level=log_level,
                                           log_level_name=log_level_name,
                                           message=message,
                                           args=args,
                                           module=module,
                                           func_name=func_name,
                                           line_no=line_no,
                                           exception=exception,
                                           process=process,
                                           thread=thread,
                                           threadName=threadName)
        if isinstance(self.args, basestring):
            self.args = eval(self.args)

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
    def summary(self):
            req = self.args['request']
            res = self.args['response']
            return {'name': req['path'],
                    'size': len(res['data']),
                    'start_time': req['time'],
                    'end_time': res['time'],
                    'time_taken': res['time'] - req['time']}


class HttpSession(SQLBase):
    sql_schema = ("CREATE TABLE IF NOT EXISTS events(Start float PRIMARY KEY,"
                  "Name text UNIQUE, End float)")
    sql_insert = "INSERT INTO events(Start, Name, End) VALUES ( ?, ?, ? );"
    _flds = OrderedDict([('start', identity),
                         ('name', identity),
                         ('end', identity)])
    __names = OrderedDict()
    start = None
    end = None
    name = None

    @classmethod
    def _see(cls, data):
        start, name, _ = data
        if name not in cls.__names:
            cls.__names[name] = start
        return cls(*data)

    def update_end_from_db(self):
        new_self = self.get_entry(start=self.start)
        self.end = new_self.end

    def update_db(self, db=None):
        if self.name in self._names:
            with self._conn_db(db) as conn:
                curs = conn.cursor()
                curs.execute("UPDATE events SET End=? WHERE Start=?",
                             (self.end, self.start))
        else:
            self.insert(db)


    @classmethod
    def get_entry(cls, start=None, name=None, db=None):
        if start is None:
            assert name is not None, "get_entry needs a start time or a name"
            start = self._names[name]
        with cls._conn_db(db) as conn:
            curs = conn.cursor()
            return cls._see(curs.fetchone("SELECT * FROM events WHERE Start=?",
                                          (start,)))

    @classmethod
    def get_all(cls, db=None):
        with cls._conn_db(db) as conn:
            curs = conn.cursor()
            return tuple(cls._see(event) for event in
                         curs.execute("SELECT * FROM events"))

    @property
    def _names(self, db=None):
        self.__names.clear()
        with self._conn_db(db) as conn:
            curs = conn.cursor()
            for name, start in curs.execute("SELECT Name, Start from events"):
                self.__names[name] = start
        return self.__names

    @property
    def summary(self):
        assets = [event.summary for event in self.events]
        ret = {'name': self.name,
               'start_time': self.start,
               'asset_num': len(assets),
               'assets': assets,
               'cummulative_time': sum([a['time_taken'] for a in assets]),
               'cummulative_size': sum([a['size'] for a in assets])}
        if self.end is not None:
            ret['status'] = 'Complete'
            ret['wall_time'] = self.end - self.start
            ret['end_time'] = self.end
        else:
            ret['status'] = 'Incomplete'
            from time import time
            if self.events:
                end = max(event.args['response']['time']
                          for event in self.events)
            else:
                from time import time
                end = time()
            ret['wall_time'] = end - self.start
        return ret

    def __init__(self, start, name, end=None):
        super(HttpSession, self).__init__(start=start, name=name, end=end)

    @property
    def events(self):
        if not hasattr(self, '_events'):
            return self.get_events()
        return self._events

    def get_events(self, db=None):
        sql = "SELECT * FROM log WHERE Created>=?"
        times = [self.start]
        if self.end is not None:
            times.append(self.end)
            sql += " AND Created<=?"
        times = tuple(times)
        events = []
        with self._conn_db(db) as conn:
            data = conn.cursor().execute(sql, times)
            for event in data:
                events.append(SQLiteRecord(*event))
        self._events = tuple(events)
        return events
