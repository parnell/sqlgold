"""Config for SQLGold"""
import logging
import os
from typing import Dict, Union

import tomllib
from appdirs import site_config_dir

appname = "sqlgold"


class Config(dict):
    """Config class, an attr dict that allows referencing by attribute
    Example:
        cfg = Config({"a":1, "b":{"c":3}})
        cfg.a.b.c == cfg["a"]["b"]["c"] # True
    """
    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        self.__dict__ = self


cfg = Config()  ## our config

_attr_dict_dont_overwrite = set([func for func in dir(dict) if getattr(dict, func)])


def make_attr_dict(d: dict):
    """Make an AttrDict (Config) object without any keys
    that will overwrite the normal functions of a

    Args:
        d (dict): _description_

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """
    d = Config(**d)
    for k, v in d.items():
        if k in _attr_dict_dont_overwrite:
            raise Exception(
                f"Error! config key={k} would overwrite a default dict attr/func"
            )
        if isinstance(v, dict):
            d[k] = make_attr_dict(v)
    return d


def set_log_level(level: str):
    """Set logging to the specified level

    Args:
        level (str): log level
    """
    level = level.upper() if level else ""
    if level and level != logging._nameToLevel.get(level):
        logging.basicConfig(level=level)
        logging.debug(f"{appname} logging set to {level.upper()}")


def read_config_dir(config_file_or_appname: str) -> Config:
    """Read the config.toml file from the config directory
        This will be read the first config.toml found in following directories
            - ~/.config/<appname>/config.toml
            - <system config directory>/<appname>/config.toml

    Args:
        config_file_or_appname (str): App name for choosing the config directory

    Returns:
        AttrDict: the parsed config file in a dict format
    """
    check_order = [
        config_file_or_appname,
        f"~/.config/{config_file_or_appname}/config.toml",
        f"{site_config_dir(appname=config_file_or_appname)}/config.toml",
    ]
    for potential_config in check_order:
        potential_config = os.path.expanduser(potential_config)
        if os.path.isfile(potential_config):
            logging.debug(f"{appname} opening {potential_config}")
            with open(potential_config, "r") as fp:
                str_file = fp.read()
                cfg = tomllib.loads(str_file)
            return make_attr_dict(cfg)
    logging.debug(f"No config.toml found. Using blank config")
    return make_attr_dict({})

def set_database_config(appname_path_dict: Union[str, Dict]) -> Config:
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

## Overwrite logging level from environment variables if specified
set_log_level(os.getenv("SG_LOGLEVEL", None))

## Init our cfg
set_database_config(appname)

## Set our log level from config if specified if has not been overwritten from cmd line
if "SG_LOGLEVEL" not in os.environ:
    set_log_level(cfg.get("logging", {}).get("level"))
