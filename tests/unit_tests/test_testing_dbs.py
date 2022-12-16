"""Unit tests for db.py """
import unittest

from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column

from sqlgold.config import set_database_config
from sqlgold.utils.test_db_utils import create_test_db
from sqlgold import declarative_base

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


class TestTestingDBs(unittest.TestCase):

    def test_create_test_db_no_options(self):
        with create_test_db() as db:
            pass

    def test_create_test_db_from_url(self):
        with create_test_db(url="sqlite:///:memory:") as db:
            pass


if __name__ == "__main__":
    unittest.main()
