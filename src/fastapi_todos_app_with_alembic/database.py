from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'

# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:password@localhost/postgres'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

# connect_args is for sqlite only, not for postgresql
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()


"""
Changed in version 2.0: 
The DeclarativeBase superclass supersedes the use of the declarative_base() function and registry.generate_base() methods; 
the superclass approach integrates with PEP 484 tools without the use of plugins.
"""

class Base(DeclarativeBase):
    pass