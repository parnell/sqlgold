from sqlalchemy import select
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from sqlgold import create_db

Base = declarative_base()


class MyClass(Base):
    """Create your SQLAlchemy class as normal"""

    __tablename__ = "tclass"

    id: Mapped[int] = mapped_column(primary_key=True)


## Connect our db and create our tables
db = create_db("sqlite://", Base=Base, create_all=True)

## Use session as an instance
obj = MyClass(id=1)
session = db.Session()
session.add(obj)
session.commit()
dbobjs = session.scalars(select(MyClass)).all()
assert len(dbobjs) == 1

# Cleanup
session.delete(obj)
session.commit()

# Use Session as a contextmanager
with db.Session() as session:
    obj = MyClass(id=1)
    session.add(obj)
    session.commit()
    dbobjs = session.scalars(select(MyClass)).all()
    assert len(dbobjs) == 1

    # Cleanup
    session.delete(obj)
    session.commit()

