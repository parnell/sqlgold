# Added SQLAlchemy Functionality
Additional functions for easy database connections


## Pip installation
```sh
python3 -m pip install git+https://github.com/parnell/sqlgold.git
```

# Using
SQLGold to add easy database connectivity options to SQLAlchemy. 

## Code Examples
```python
Base = declarative_base()
DB.default_base = Base

## Different ways of connecting
# Explicit with url
db = create_db("sqlite://")

# Load in from default section of `config.toml` (see below for how to set up config)
db = create_db()

# Load in options from the 'mysql' section of `config.toml` (see below for how to set up config)
db = create_db("mysql")

# Load in options from the 'mysql.test' section of `config.toml` (see below for how to set up config)
db = create_db("mysql.test")

# Pass in database options as a dictionary
db = create_db({"url":"sqlite://"})

```

Full Code Example
```python
from sqlalchemy import select
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from sqlgold import create_db

Base = declarative_base()


class MyClass(Base):
    __tablename__ = "tclass"

    id: Mapped[int] = mapped_column(primary_key=True)


## Connect our db and create our tables
db = create_db("sqlite://", Base=Base, create_all=True)

## Use session as an instance
obj = MyClass()
session = db.Session()
session.add(obj)
session.commit()

# Use Session as a contextmanager
with db.Session() as session:
    obj = MyClass()
    session.add(obj)
    session.commit()

# Use Session as a contextmanager
with db.Session.begin() as session:
    obj = MyClass()
    session.add(obj)
```


For some other full code examples see [examples](https://github.com/parnell/sqlgold/blob/main/examples)


# Configuration 
While you can pass in connection urls, or dictionaries with config variables, you can also set defaults using a `config.toml`, locations can be found in (#Creating the `config.toml` file)
For help with creating initial users see the [DATABASE README](https://github.com/parnell/sqlgold/blob/main/README_DATABASE.md)

## Creating the `config.toml` file
This project uses default options loaded from a `.toml` file. This file is located in the system config directory that is different for every system. 

It will check for the config.toml in the following locations in order.

### Config locations
These locations will be checked in order
* ```~/.config/sqlgold/config.toml```
* ```<config directory for user(system dependent)>/sqlgold/config.toml```



Example `config.toml`
```toml
default="sqlite3" 

[sqlite3] 
url="sqlite:///:memory:"

[mysql] 
url="mysql+pymysql://<username>:<password>@<host>/<database>?charset=utf8mb4"

[logging]
# level: set logging to a valid level
#        "" for nothing, "debug", "info", "warn", "error", "critical" 
level=""
```
