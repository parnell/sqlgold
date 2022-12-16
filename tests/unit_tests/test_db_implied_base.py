"""Unit tests for db.py """
import unittest

from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column

from sqlgold.config import set_database_config
from sqlgold.utils.test_db_utils import create_test_db
from sqlgold import create_db


test_cfg = {
    "default": "sqlite3",
    "sqlite3": {
        "url": "sqlite:///:memory:",
        "test": {"url": "sqlite:///:memory:"},
    },
}
set_database_config(test_cfg)

from sqlgold.managers.db_manager import DBManager


class TestMysqlConnection(unittest.TestCase):

    def test_create_db_implied_base_from_declarative_base(self):
        DBManager.set_manager(DBManager())
        from sqlgold.orm import declarative_base
        Base = declarative_base()
        
        class TClass(Base):
            __tablename__ = "tclass"

            id: Mapped[int] = mapped_column(primary_key=True)

        db = create_db({"url": "sqlite:///:memory:"}, create_all=True)
        with db.Session() as s:
            s.add(TClass(id=1))
            s.commit()
            l = list(s.scalars(select(TClass)))
            self.assertEqual(len(l), 1)


    def test_create_db_implied_base(self):
        DBManager.set_manager(DBManager())
        from sqlalchemy.orm import declarative_base
        Base = declarative_base()
        class TClass(Base):
            __tablename__ = "tclass"

            id: Mapped[int] = mapped_column(primary_key=True)

        db = create_db({"url": "sqlite:///:memory:"}, Base=Base, create_all=True)
        with db.Session() as s:
            s.add(TClass(id=1))
            s.commit()
            l = list(s.scalars(select(TClass)))
            self.assertEqual(len(l), 1)
        db.engine.dispose()

        ## No base specified but should work as normal
        ## with a new db. specifying a different sqlite to get a 
        ## different implied alias
        db = create_db({"url": "sqlite://"}, create_all=True)
        with db.Session() as s:
            s.add(TClass(id=1))
            s.commit()
            l = list(s.scalars(select(TClass)))
            self.assertEqual(len(l), 1)

if __name__ == "__main__":
    unittest.main()
