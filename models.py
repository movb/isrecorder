from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Text, DateTime, Binary
import datetime


Base = declarative_base()


class Meta(Base):
    __tablename__ = 'meta'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    start = Column(DateTime, default=datetime.datetime.utcnow)
    stop = Column(DateTime)

    def __init__(self, name, url):
        self.name = name
        self.url = url
    def __repr__(self):
        return "<Meta('%s', '%s', '%s', '%s')>" % (self.name, self.url, self.start, self.stop)


class MainPlaylist(Base):
    __tablename__ = 'main_playlist'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    body = Column(Text)
    error = Column(String)
    error_code = Column(Integer)
    
    def __init__(self, body, error="", error_code=200):
        self.body = body
        self.error = error
        self.error_code = error_code
    def __repr__(self):
        return "<MainPlaylist('%s','%s', '%s')>" % (self.body, self.error, self.error_code)


class SimplePlaylist(Base):
    __tablename__ = 'simple_playlist'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    body = Column(Text)
    error = Column(String)
    error_code = Column(Integer)

    def __init__(self, name, body, error="", error_code=200):
        self.name = name
        self.body = body
        self.error = error
        self.error_code = error_code

    def __repr__(self):
        return "<SimplePlaylist('%s', '%s', '%s', '%s')>" % (self.name, self.body, self.error, self.error_code)


class Segment(Base):
    __tablename__ = 'segments'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    path = Column(String)
    error = Column(String)
    error_code = Column(Integer)

    def __init__(self, name, path, error="", error_code=200):
        self.name = name
        self.path = path
        self.error = error
        self.error_code = error_code

    def __repr__(self):
        return "<Segment('%s',' %s', '%s', '%s')>" % (self.name, self.path, self.error, self.error_code)


class Key(Base):
    __tablename__ = 'keys'
    id = Column(Integer, primary_key=True)
    path = Column(String)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    data = Column(Binary)
    error = Column(String)
    error_code = Column(Integer)

    def __init__(self, path, data, error="", error_code=200):
        self.path = path
        self.data = data
        self.error = error
        self.error_code = error_code

    def __repr__(self):
        return "<Key('%s',' %s', '%s', '%s')>" % (self.path, self.data, self.error, self.error_code)