import logging
import re

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from dataclasses import dataclass
from sqlgold.config import Config, cfg, set_database_config
from sqlgold.orm.decl_base import Base
from sqlgold.orm.session_extension import extended_sessionmaker
from sqlgold.engine.db import DB
from sqlalchemy.orm import Session, sessionmaker

from typing import Self, Type
from abc import abstractclassmethod
from sqlalchemy.engine import make_url as sa_make_url
from sqlalchemy import quoted_name


@dataclass
class MysqlDB(DB):
    
    @classmethod
    def create_connection_url(cls, url):
        url = sa_make_url(url)
        return f"{url.drivername}://{url.username}:{url.password}@{url.host}"

    @classmethod
    def create_db(cls, ourl: str, *args, **kwargs) -> Self:
        url = sa_make_url(ourl)
        connection_url = cls.create_connection_url(url)
        database = url.database

        Session = sessionmaker()
        engine = create_engine(connection_url)
        Session.configure(bind=engine)
        
        # encoding = re.search(r"charset=(\w+)", url.query)
        charset = url.query.get("charset", "utf8mb4")
        stmt = (
            f"CREATE DATABASE IF NOT EXISTS {quoted_name(database, True)} CHARACTER SET = '{charset}';"
        )
        with Session.begin() as s:
            s.execute(text(stmt))
        
            s.execute(text(f"USE {quoted_name(database, True)};"))
        engine.dispose()
        return MysqlDB(url=url)

