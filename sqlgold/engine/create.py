"""Factory for creating DB instances"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any, Dict, Type, Union

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine
from sqlalchemy.engine import make_url as sa_make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import text

from sqlgold.config import cfg
from sqlgold.dialects.mysql import MysqlDB
from sqlgold.dialects.sqlite3 import Sqlite3DB
from sqlgold.engine.db import DB, sentinel
from sqlgold.exceptions import ConfigException
from sqlgold.managers.db_manager import DBManager


class DriverType(StrEnum):
    """Class for distinguishing between implemented drivers for db connections"""

    nospecific = auto()
    mysql = auto()
    sqlite3 = auto()

    @staticmethod
    def from_str(driver_str: str) -> DriverType:
        """Create a DriverType from a string

        Args:
            dialect_str (str): the driver string

        Returns:
            DriverType: The
        """
        try:
            return DriverType(driver_str)
        except:
            if driver_str in ("mysql+pymysql", "mariadb", "pymysql"):
                return DriverType.mysql
            if driver_str in ("sqlite"):
                return DriverType.sqlite3
            return DriverType.nospecific


@dataclass
class DBFactory:
    """Factory for creating DB instances."""

    @staticmethod
    def create_db_from_engine(
        engine: Engine,
        Base: Any = sentinel,
        create_all: bool = False,
        session: Session = None,
        sessionmaker: Type[sessionmaker] = None,
        session_args: Dict[str, Any] = None,
    ) -> DB:
        from sqlgold.engine.db import DB

        """Create a database connection from the given url

        Args:
            url (Union[str, URL]): the url of the database
            args: Arguments passed to sqlalchemy create_engine
            kwargs: Arguments passed to sqlalchemy create_engine

        Returns:
            DB: A DB instance or one of it's subclasses
        """
        dt = DriverType.from_str(engine.url.drivername)

        if dt == DriverType.mysql:
            db = MysqlDB.create_db(
                engine,
                Base=Base,
                create_all=create_all,
                session=session,
                sessionmaker=sessionmaker,
                session_args=session_args,
            )
        elif dt == DriverType.sqlite3:
            db = Sqlite3DB.create_db(
                engine,
                Base=Base,
                create_all=create_all,
                session=session,
                sessionmaker=sessionmaker,
                session_args=session_args,
            )
        else:
            db = DB.create_db(
                engine,
                Base=Base,
                create_all=create_all,
                session=session,
                sessionmaker=sessionmaker,
                session_args=session_args,
            )

        return db

    @staticmethod
    def create_db_from_url(
        url: Union[str, URL],
        Base: Any = sentinel,
        create_all: bool = False,
        session: Session = None,
        sessionmaker: Type[sessionmaker] = None,
        session_args: Dict[str, Any] = None,
        *args,
        **kwargs,
    ) -> DB:
        engine = create_engine(url, *args, **kwargs)
        return DBFactory.create_db_from_engine(
            engine,
            Base=Base,
            create_all=create_all,
            session=session,
            sessionmaker=sessionmaker,
            session_args=session_args,
        )

    @staticmethod
    def create_db_from_dict(
        config: Dict,
        Base: Any = sentinel,
        create_all: bool = False,
        session: Session = None,
        sessionmaker: Type[sessionmaker] = None,
        session_args: Dict[str, Any] = None,
        *args,
        **kwargs,
    ) -> DB:
        """Create a database connection from the given options

        Args:
            config (Dict): a dict of config options
            args: Arguments passed to sqlalchemy create_engine
            kwargs: Arguments passed to sqlalchemy create_engine

        Returns:
            DB: A DB instance or one of it's subclasses
        """
        ## If a url is specified use that
        if "url" in config:
            return DBFactory.create_db_from_url(
                config["url"],
                Base=Base,
                create_all=create_all,
                session=session,
                sessionmaker=sessionmaker,
                session_args=session_args,
                *args,
                **kwargs,
            )
        ## Otherwise try to create the url
        url = (
            f"{config['driver']}://{config['username']}:{config['password']}@"
            f"{config['host']}/{config['database']}?{config.get('suffix', '')}"
        )
        return DBFactory.create_db_from_url(
            url,
            Base=Base,
            create_all=create_all,
            session=session,
            sessionmaker=sessionmaker,
            session_args=session_args,
            *args,
            **kwargs,
        )

    @staticmethod
    def create_db_from_section(
        config_section: str,
        Base: Any = sentinel,
        create_all: bool = False,
        session: Session = None,
        sessionmaker: Type[sessionmaker] = None,
        session_args: Dict[str, Any] = None,
        *args,
        **kwargs,
    ) -> DB:
        """Create a database connection from the given options

        Args:
            config_section (str): None or a string section that specifies
                the table in the config.toml
            args: Arguments passed to sqlalchemy create_engine
            kwargs: Arguments passed to sqlalchemy create_engine

        Returns:
            DB: A DB instance or one of it's subclasses
        """
        sections = config_section.split(".")
        d = cfg[sections[0]]
        for s in sections[1:]:
            d = d[s]
        return DBFactory.create_db_from_dict(
            d,
            Base=Base,
            create_all=create_all,
            session=session,
            sessionmaker=sessionmaker,
            session_args=session_args,
            *args,
            **kwargs,
        )

    @staticmethod
    def _create_db(
        section_dict_url: Union[str, Dict, URL] = None,
        Base: Any = sentinel,
        create_all: bool = False,
        session: Session = None,
        sessionmaker: Type[sessionmaker] = None,
        session_args: Dict[str, Any] = None,
        *args,
        **kwargs,
    ) -> DB:
        """Create a database connection from the given options

        Args:
            section_dict_url (Union[str, Dict, URL], optional): Can be one of the following
                1: None or a string section that specifies the table in the config.toml
                2: a dict of config options
                3: the url of the database
                Defaults to None.
            args: Arguments passed to sqlalchemy create_engine
            kwargs: Arguments passed to sqlalchemy create_engine

        Raises:
            ConfigException: Section inside config not found
            ValueError: invalid section_dict_url data type

        Returns:
            DB: A DB instance or one of it's subclasses
        """
        if not section_dict_url:
            ## Nothing was passed, use default config options
            if not "default" in cfg:
                raise ConfigException("ConfigException: no 'default' section was set!")
            return DBFactory.create_db_from_section(
                cfg["default"],
                Base=Base,
                create_all=create_all,
                session=session,
                sessionmaker=sessionmaker,
                session_args=session_args,
                *args,
                **kwargs,
            )
        elif isinstance(section_dict_url, dict):
            return DBFactory.create_db_from_dict(
                section_dict_url,
                Base=Base,
                create_all=create_all,
                session=session,
                sessionmaker=sessionmaker,
                session_args=session_args,
                *args,
                **kwargs,
            )
        elif isinstance(section_dict_url, str):
            if "://" in section_dict_url:
                return DBFactory.create_db_from_url(
                    section_dict_url,
                    Base=Base,
                    create_all=create_all,
                    session=session,
                    sessionmaker=sessionmaker,
                    session_args=session_args,
                    *args,
                    **kwargs,
                )
            else:
                return DBFactory.create_db_from_section(
                    section_dict_url,
                    Base=Base,
                    create_all=create_all,
                    session=session,
                    sessionmaker=sessionmaker,
                    session_args=session_args,
                    *args,
                    **kwargs,
                )
        else:
            raise ValueError(
                f"DBFactory.create_db passed an invalid argument "
                f"'{section_dict_url}' with type "
                f"'{type(section_dict_url)}'"
            )

    @staticmethod
    def create_db(
        section_dict_url: Union[str, Dict, URL] = None,
        Base: Any = sentinel,
        create_all: bool = False,
        alias: str = None,
        session: Session = None,
        sessionmaker: Type[sessionmaker] = None,
        session_args: Dict[str, Any] = None,
        *args,
        **kwargs,
    ) -> DB:
        """Create a database connection from the given options

        Args:
            section_dict_url (Union[str, Dict, URL], optional): Can be one of the following
                1: None or a string section that specifies the table in the config.toml
                2: a dict of config options
                3: the url of the database
                Defaults to None.
            alias: An alias for this db that can be used for retrieval later
            If not specified the string or hash of section_dict_url will
            be used
            args: Arguments passed to sqlalchemy create_engine
            kwargs: Arguments passed to sqlalchemy create_engine

        Raises:
            ConfigException: Section inside config not found
            ValueError: invalid section_dict_url data type

        Returns:
            DB: A DB instance or one of it's subclasses
        """
        dbmanager = DBManager.get_manager()
        if alias is None:
            alias = str(section_dict_url)
        if DB.default_base is None or DB.default_base == sentinel:
            DB.default_base = Base
            dbmanager.set_base(alias, Base)
        if Base == sentinel:
            Base = dbmanager.get_base(alias)

        db = DBFactory._create_db(
            section_dict_url=section_dict_url,
            Base=Base,
            create_all=create_all,
            session=session,
            sessionmaker=sessionmaker,
            session_args=session_args,
            *args,
            **kwargs,
        )

        dbmanager.set_database(alias, db)
        if not dbmanager.has_main_database():
            dbmanager.set_main_database(alias, db)
        return db


def create_db(
    section_dict_url: Union[str, Dict, URL] = None,
    Base: Any = sentinel,
    create_all: bool = False,
    alias: str = None,
    session: Session = None,
    sessionmaker: Type[sessionmaker] = None,
    session_args: Dict[str, Any] = None,
    *args,
    **kwargs,
) -> DB:
    """Create a database connection from the given options

    Args:
        section_dict_url (Union[str, Dict, URL], optional): Can be one of the following
            1: None or a string section that specifies the table in the config.toml
            2: a dict of config options
            3: the url of the database
            Defaults to None.
        alias: An alias for this db that can be used for retrieval later
        If not specified the string or hash of section_dict_url will
        be used
        args: Arguments passed to sqlalchemy create_engine
        kwargs: Arguments passed to sqlalchemy create_engine

    Raises:
        ConfigException: Section inside config not found
        ValueError: invalid section_dict_url data type

    Returns:
        DB: A DB instance or one of it's subclasses
    """
    return DBFactory.create_db(
        section_dict_url=section_dict_url,
        Base=Base,
        create_all=create_all,
        session=session,
        sessionmaker=sessionmaker,
        alias=alias,
        session_args=session_args,
        *args,
        **kwargs,
    )
