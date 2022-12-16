import os
from typing import Any, Dict, Self, Type

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from sqlgold.engine.db import DB, sentinel


class Sqlite3DB(DB):
    @classmethod
    def create_db(
        cls,
        engine: Engine,
        Base: Any = sentinel,
        create_all: bool = False,
        session: Session = None,
        sessionmaker: Type[sessionmaker] = None,
        session_args: Dict[str, Any] = None,
    ) -> Self:
        db = Sqlite3DB(
            engine=engine,
            Base=Base,
            session=session,
            sessionmaker=sessionmaker,
            session_args=session_args,
        )
        if create_all and Base is not None:
            db.create_all()
        return db

    def drop_db(self, **kwargs):
        if not self.database:
            return
        if self.database != ":memory:":
            os.remove(self.database)
