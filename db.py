from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from models import *


class DB:
    engine = None
    session = None
    session_factory = None

    def __init__(self, dburi):
        self.engine = create_engine(dburi, echo=False, pool_recycle=3600, echo_pool=True,
                                    connect_args={'check_same_thread':False})
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine, checkfirst=True)
        self.session_factory = sessionmaker(bind=self.engine)

    def get_session(self):
        return scoped_session(self.session_factory)