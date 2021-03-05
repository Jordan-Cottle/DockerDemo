"""
This module contains utilities for managing database sessions.

Session is a `session_maker` connected to the configured database engine.

inject_session is a function that will set up `Session` instances for each flask request
as a before_request handler

close_session is a function that will commit and close the database session at the end of a request
"""
import os

from flask import g
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

ENGINE = create_engine(f"sqlite:///data/auth.db", echo=True)
Session = sessionmaker(bind=ENGINE)


def inject_session():
    """ Add a session to the flask request context. """

    g.session = Session()


def close_session(response):
    """ Commit and close out a session at the end of a flask request. """

    try:
        g.session.commit()
    except Exception as error:
        print(f"An error with the database has ocurred: {error!r}")
        raise
    finally:
        g.session.close()

    return response


Base = declarative_base()


class User(Base):
    """ Track users in DB. """

    __tablename__ = "User"
    id = Column(Integer, primary_key=True)
    active_token = Column(String(36), unique=True, index=True)
    name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    salt = Column(String, nullable=False)


Base.metadata.create_all(ENGINE)
