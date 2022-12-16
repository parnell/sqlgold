from typing import Any, Dict, Self, Type

from sqlalchemy import Engine, create_engine, quoted_name
from sqlalchemy.engine import make_url as sa_make_url
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker as sa_sessionmaker
from sqlalchemy.sql import text

from sqlgold.engine.db import DB, sentinel


class MysqlDB(DB):
    @classmethod
    def create_connection_url(cls, url):
        url = sa_make_url(url)
        return f"{url.drivername}://{url.username}:{url.password}@{url.host}"

    @classmethod
    def create_db(
        cls,
        engine: Engine,
        Base: Any = sentinel,
        create_all: bool = False,
        session: Session = None,
        sessionmaker: Type[sa_sessionmaker] = None,
        session_args: Dict[str, Any] = None,
    ) -> Self:

        connection_url = cls.create_connection_url(engine.url)
        database = engine.url.database

        Session = sa_sessionmaker()
        engine_for_creating = create_engine(connection_url)
        Session.configure(bind=engine_for_creating)

        charset = engine.url.query.get("charset", "utf8mb4")
        stmt = f"CREATE DATABASE IF NOT EXISTS {quoted_name(database, True)} CHARACTER SET = '{charset}';"

        with Session.begin() as s:
            s.execute(text(stmt))
            s.execute(text(f"USE {quoted_name(database, True)};"))
        engine_for_creating.dispose()
        db = MysqlDB(
            engine=engine,
            Base=Base,
            session=session,
            sessionmaker=sessionmaker,
            session_args=session_args,
        )

        if create_all and Base is not None:
            db.create_all()
        return db
