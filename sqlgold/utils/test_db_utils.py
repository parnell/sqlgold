"""DB Utility class for testing """
import atexit
import inspect
import logging
import os
import uuid
from contextlib import contextmanager
from typing import Any, Dict, Union

from sqlgold.config import Config
from sqlgold.config import cfg as default_cfg
from sqlgold.config import make_attr_dict, read_config_dir
from sqlgold.engine.create import create_db

cfg = {"not_set":True}

def set_base(base: Any):
    from sqlgold import DB
    DB.default_base=base

def set_test_config(appname_path_dict: Union[str, Dict]) -> Config:
    """Set the config.toml to use

    Args:
        appname_path_dict (str): Set the config for SQLAlchemy Extensions.
        Can be passed with the following.
            Dict: updates cfg with the given dict
            str: a path to a .toml file
            str: appname to search for the config.toml in the the application config dir

    Returns:
        Config: A config object (an attribute dictionary)
    """
    cfg.clear()
    if isinstance(appname_path_dict, dict):
        newcfg = make_attr_dict(appname_path_dict)
    else:
        newcfg = read_config_dir(appname_path_dict)
    cfg.update(newcfg)
    return cfg


_ensure_dropped_test_dbs = {}


def _make_db_name(username: str, random_suffix: bool):
    funcname_stack_number = None
    for i in range(len(inspect.stack()) - 1, 0, -1):
        if inspect.stack()[i][3] == "__enter__":
            funcname_stack_number = i + 1
            break

    if not funcname_stack_number:
        raise Exception("Couldn't auto determine a database name. Please specify one")

    stack = inspect.stack()[funcname_stack_number]
    ## Make our name. Either from the calling functions
    ## Or label it the name of the module and linenumber
    fn = stack[3]
    if fn == "<module>":
        filename = os.path.basename(stack.filename)
        filename, __ = os.path.splitext(filename)
        ln = stack[2]
        fn = f"{filename}_line_{ln}"

    suf = f"_{uuid.uuid4().hex[:4]}" if random_suffix else ""
    database = f"{username}_{fn}{suf}"
    if len(database) > 64:
        end_index = 64 - len(f"{username}_{suf}")  # length without fn
        database = f"{username}_{fn[:end_index]}{suf}"
    return database


def _create_test_db_from_params(
    config: Dict = None,
    config_section: str = None,
    database: str = None,
    username: str = None,
    password: str = None,
    driver: str = None,
    host: str = None,
    suffix: str = "",
    random_suffix: bool = False,
    **kwargs,
):
    if config is not None:
        base_cfg = config.copy()
    else:
        config = default_cfg.copy() if "not_set" in cfg else cfg
        dr = driver if driver else config["default"]
        config_section = config_section if config_section else f"{dr}.test"
        sections = config_section.split(".")
        d = config[sections[0]]
        try:
            for s in sections[1:]:
                d = d[s]
        except KeyError as e:
            e.add_note(f"'{config_section}' was not found in cfg")
            raise
        base_cfg = d.copy()
    if "url" in base_cfg:
        return create_db(base_cfg["url"], **kwargs)

    # fmt: off
    if driver: base_cfg["driver"] = driver
    if username: base_cfg["username"] = username
    if password: base_cfg["password"] = password
    if host: base_cfg["host"] = host
    # fmt: on

    if not database:
        database = _make_db_name(
            username=base_cfg["username"], random_suffix=random_suffix
        )

    base_cfg["database"] = database
    assert len(database) <= 64

    db = create_db(base_cfg, **kwargs)
    return db


def count(db, cls):
    with db.Session() as s:
        return int(s.query(cls).count())


@contextmanager
def create_test_db(
    url: str = None,
    config: Dict = None,
    config_section: str = None,
    database: str = None,
    username: str = None,
    password: str = None,
    driver: str = None,
    host: str = None,
    drop: bool = True,
    suffix: str = "",
    random_suffix: bool = False,
    **kwargs
):
    """Create a temporary db for testing. This db will by default be dropped/deleted
    When out of scope.
    When nothing is passed in it will use the database type specified in
    the config.toml in default in the "test" section, .e.g `sqlite3.test`

    Args:
        url (str, optional): _description_. Defaults to None.
        config (Dict, optional): _description_. Defaults to None.
        config_section (str, optional): _description_. Defaults to None.
        database (str, optional): _description_. Defaults to None.
        username (str, optional): _description_. Defaults to None.
        password (str, optional): _description_. Defaults to None.
        driver (str, optional): _description_. Defaults to None.
        host (str, optional): _description_. Defaults to None.
        drop (bool, optional): _description_. Defaults to True.
        suffix (str, optional): _description_. Defaults to "".
        random_suffix (bool, optional): _description_. Defaults to False.

    Yields:
        DB: A db instance for testing
    """
    if not url:
        db = _create_test_db_from_params(
            config=config,
            config_section=config_section,
            database=database,
            username=username,
            password=password,
            driver=driver,
            host=host,
            suffix=suffix,
            random_suffix=random_suffix,
            **kwargs
        )
    else:
        db = create_db(url, **kwargs)

    url_str = db.engine.url
    if drop:
        _ensure_dropped_test_dbs[url_str] = db
    try:
        db.create_all()
        yield db
    finally:
        if drop:
            db.drop_db()
            _ensure_dropped_test_dbs.pop(url_str, None)


@atexit.register
def cleanup():
    for db in _ensure_dropped_test_dbs.values():
        logging.debug(f"Dropping an unclosed db '{db.database}'")
        try:
            db.drop_db()
        except:
            pass
