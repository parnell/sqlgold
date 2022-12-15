from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Self


from sqlgold.engine.db import DB, sentinel


@dataclass
class DBManager:
    manager : ClassVar[Self] = None
    databases: Dict[str, DB] = field(default_factory=dict)  ## DBs
    main_database: str = None

    main_base: str = None
    bases: Dict[str, Any] = field(default_factory=dict)

    def set_base(self, key: str, Base: Any):
        self.bases[key] = Base

    def get_base(self, key: str, default=sentinel):
        return self.bases.get(key, default)

    def has_main_database(self) -> bool:
        """returns whether the main_database is not None

        Returns:
            bool: has the main database been defined
        """
        return self.main_database is not None

    def set_main_database(self, database_alias: str, db: DB):
        """Set the main_database

        Args:
            database_alias (str): new alias to set as main
        """
        self.main_database = database_alias
        self.set_database(self.main_database, db)

    def set_database(self, database_alias: str, db: DB):
        """Set a alias to a database

        Args:
            database_alias (str): alias for the database
            db (DB): database instance
        """
        self.databases[database_alias] = db

    def get_database(self, database_alias: str):
        return self.databases[database_alias]

    def get_main_database(self) -> DB:
        """Returns the database set as main

        Returns:
            DB: DB instance
        """
        if self.main_database is None:
            raise Exception("Error! No main database specified!")
        return self.databases[self.main_database]

    @staticmethod
    def set_manager(db_manager: DBManager):
        DBManager.manager = db_manager

    @staticmethod
    def get_manager():
        return DBManager.manager

DBManager.set_manager(DBManager())
