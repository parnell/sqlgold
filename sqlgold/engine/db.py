"""Database manager for sqlalchemy dbs

Notes and terminology
Flush: the flush occurs before any individual SQL statement is 
    issued as a result of a Query or a 2.0-style Session.execute() call, 
    as well as within the Session.commit() call before the transaction is committed. 
    It also occurs before a SAVEPOINT is issued when Session.begin_nested() is used.

"""
import logging
from typing import Any, Dict, Optional, Self
from typing import Sequence as _typing_Sequence
from typing import Set, Type

from sqlalchemy import Engine, create_engine, quoted_name
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.schema import Table
from sqlalchemy.sql import text

from .db_options import DBOptions

sentinel = object()


class DB:
    """manager for interfacing with a database through SQAlchemy"""

    default_sessionmaker: Type[sessionmaker] = sessionmaker
    default_base: Any = None
    default_options: Set[DBOptions] = set()

    def __init__(
        self,
        engine: Engine,
        Base: Any = sentinel,
        session: Session = None,
        sessionmaker: sessionmaker = None,
        session_args: Dict[str, Any] = None,
    ):
        """init the DB instance with the given uri

        Args:
            url (Union[str, URL]): connection uri to use when creating db
        """
        self.engine: Engine = engine
        self.Base: Any = Base
        if Base == sentinel:
            self.Base = DB.default_base

        if not self.engine:
            raise IOError("No url connection")

        logging.debug(f"SQLALCHEMY_URL = {self.engine.url}")
        if session is None:
            session_args = {} if not session_args else session_args
            if sessionmaker is None:
                Session = DB.default_sessionmaker()
            else:
                Session = sessionmaker
            Session.configure(bind=self.engine, **session_args)
            self.Session = Session

    @property
    def url(self):
        return self.engine.url

    @property
    def database(self):
        return self.engine.url.database

    def __repr__(self):
        return f"DB(database={self.url.database})"

    def __str__(self):
        return self.__repr__()

    @classmethod
    def create_connection_url(cls, url) -> str:
        """The connection url without the database

        Args:
            url (_type_): database url

        Returns:
            str: the database url
        """
        return url

    @classmethod
    def create_db(
        cls,
        engine: Engine,
        Base: Any = sentinel,
        create_all: bool = False,
        session: Session = None,
        session_args: Dict[str, Any] = None,
    ) -> Self:
        """Create a db at the specified url

        Args:
            url (Union[str, URL]): database url
            args: Arguments passed to sqlalchemy create_engine
            kwargs: Arguments passed to sqlalchemy create_engine

        Returns:
            Self: The database instance
        """
        db = DB(engine=engine, Base=Base, session=session, session_args=session_args)

        connection_url = cls.create_connection_url(engine.url)
        database = engine.url.database

        engine_for_creating = create_engine(connection_url)
        Session = sessionmaker()
        Session.configure(bind=engine_for_creating)

        with Session.begin() as s:
            s.execute(
                text(f"CREATE DATABASE IF NOT EXISTS {quoted_name(database, True)} ;")
            )
            s.execute(text(f"USE {quoted_name(database, True)};"))

        if Base is not None and (
            create_all or DBOptions.create_all in DB.default_options
        ):
            db.create_all()
        return db

    def create_all(
        self, tables: Optional[_typing_Sequence[Table]] = None, checkfirst: bool = True
    ) -> None:
        """Create all tables stored in the Base metadata.
        Conditional by default, will not attempt to recreate tables already
        present in the target database.

        Args:
            tables (Optional[_typing_Sequence[Table]], optional): Optional list of ``Table`` objects, which is a subset of the total
          tables in the ``MetaData`` (others are ignored). Defaults to None.
            checkfirst (bool, optional): Defaults to True, don't issue CREATEs for tables already present
          in the target database.
        """

        self.Base.metadata.create_all(
            bind=self.engine, tables=tables, checkfirst=checkfirst
        )

    def drop_all(
        self, tables: Optional[_typing_Sequence[Table]] = None, checkfirst: bool = True
    ) -> None:
        """Create all tables stored in the Base metadata.
        Conditional by default, will not attempt to recreate tables already
        present in the target database.

        Args:
            tables (Optional[_typing_Sequence[Table]], optional): Optional list of ``Table`` objects, which is a subset of the total
          tables in the ``MetaData`` (others are ignored). Defaults to None.
            checkfirst (bool, optional): Defaults to True, don't issue CREATEs for tables already present
          in the target database.
        """

        self.Base.metadata.drop_all(
            bind=self.engine, tables=tables, checkfirst=checkfirst
        )

    def drop_db(self, **kwargs):
        """drop the db (delete)"""
        if not self.database:
            return

        stmt = f"DROP DATABASE IF EXISTS {self.database};"
        logging.debug(f"Dropping '{self}'. Statement='{stmt}'")

        self.Base.metadata.drop_all(bind=self.engine)

        with self.Session.begin() as session:
            session.execute(text(stmt))
