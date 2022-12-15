"""Unit tests for db.py """
import unittest

from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column, declarative_base

from sqlgold.config import set_database_config
from sqlgold.utils._test_db_utils import create_test_db
from sqlgold import create_db

Base = declarative_base()

test_cfg = {
    "default": "sqlite3",
    "sqlite3": {
        "url": "sqlite:///:memory:",
        "test": {"url": "sqlite:///:memory:"},
    },
}
set_database_config(test_cfg)


class TClass(Base):
    __tablename__ = "tclass"

    id: Mapped[int] = mapped_column(primary_key=True)


class TestMysqlConnection(unittest.TestCase):
    def test_dbfactory_create_db_no_options(self):
        db = create_db(Base=Base)
        db.create_all()
        with db.Session() as s:
            s.add(TClass(id=1))
            s.commit()
            l = list(s.scalars(select(TClass)))
            self.assertEqual(len(l), 1)

    def test_dbfactory_create_db_from_dict(self):
        db = create_db({"url": "sqlite:///:memory:"}, Base=Base)
        db.create_all()
        with db.Session() as s:
            s.add(TClass(id=1))
            s.commit()
            l = list(s.scalars(select(TClass)))
            self.assertEqual(len(l), 1)

    def test_dbfactory_create_db_from_section(self):
        db = create_db("sqlite3.test", Base=Base)
        db.create_all()
        with db.Session() as s:
            s.add(TClass(id=1))
            s.commit()
            l = list(s.scalars(select(TClass)))
            self.assertEqual(len(l), 1)

    def test_dbfactory_create_db_from_url(self):
        db = create_db("sqlite:///:memory:", Base=Base)
        db.create_all()
        with db.Session() as s:
            s.add(TClass(id=1))
            s.commit()
            l = list(s.scalars(select(TClass)))
            self.assertEqual(len(l), 1)

    def test_create_db_no_options(self):
        db = create_db(Base=Base)
        db.create_all()
        with db.Session() as s:
            s.add(TClass(id=1))
            s.commit()
            l = list(s.scalars(select(TClass)))
            self.assertEqual(len(l), 1)

    def test_create_db_from_dict(self):
        db = create_db({"url": "sqlite:///:memory:"}, Base=Base)
        db.create_all()
        with db.Session() as s:
            s.add(TClass(id=1))
            s.commit()
            l = list(s.scalars(select(TClass)))
            self.assertEqual(len(l), 1)

    def test_create_db_from_section(self):
        db = create_db("sqlite3.test", Base=Base)
        db.create_all()
        with db.Session() as s:
            s.add(TClass(id=1))
            s.commit()
            l = list(s.scalars(select(TClass)))
            self.assertEqual(len(l), 1)

    def test_create_db_from_url(self):
        db = create_db("sqlite:///:memory:", Base=Base)
        db.create_all()
        with db.Session() as s:
            s.add(TClass(id=1))
            s.commit()
            l = list(s.scalars(select(TClass)))
            self.assertEqual(len(l), 1)

if __name__ == "__main__":
    unittest.main()
