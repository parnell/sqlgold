from typing import Any, Callable, Optional, Type

from sqlalchemy.orm.decl_api import (
  DeclarativeMeta,
  _TypeAnnotationMapType,
  clsregistry,
  declarative_base,
)
from sqlalchemy.orm.decl_base import _declarative_constructor
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.sql.schema import MetaData
from sqlgold.engine.db import DB, sentinel


def register_declarative_base(
    *,
    metadata: Optional[MetaData] = None,
    mapper: Optional[Callable[..., Mapper[Any]]] = None,
    cls: Type[Any] = object,
    name: str = "Base",
    class_registry: Optional[clsregistry._ClsRegistryType] = None,
    type_annotation_map: Optional[_TypeAnnotationMapType] = None,
    constructor: Callable[..., None] = _declarative_constructor,
    metaclass: Type[Any] = DeclarativeMeta,
) -> Any:
    r"""Construct a base class for declarative class definitions.
    The new base class will be given a metaclass that produces
    appropriate :class:`~sqlalchemy.schema.Table` objects and makes
    the appropriate :class:`_orm.Mapper` calls based on the
    information provided declaratively in the class and any subclasses
    of the class.
    .. versionchanged:: 2.0 Note that the :func:`_orm.declarative_base`
       function is superseded by the new :class:`_orm.DeclarativeBase` class,
       which generates a new "base" class using subclassing, rather than
       return value of a function.  This allows an approach that is compatible
       with :pep:`484` typing tools.
    The :func:`_orm.declarative_base` function is a shorthand version
    of using the :meth:`_orm.registry.generate_base`
    method.  That is, the following::
        from sqlalchemy.orm import declarative_base
        Base = declarative_base()
    Is equivalent to::
        from sqlalchemy.orm import registry
        mapper_registry = registry()
        Base = mapper_registry.generate_base()
    See the docstring for :class:`_orm.registry`
    and :meth:`_orm.registry.generate_base`
    for more details.
    .. versionchanged:: 1.4  The :func:`_orm.declarative_base`
       function is now a specialization of the more generic
       :class:`_orm.registry` class.  The function also moves to the
       ``sqlalchemy.orm`` package from the ``declarative.ext`` package.
    :param metadata:
      An optional :class:`~sqlalchemy.schema.MetaData` instance.  All
      :class:`~sqlalchemy.schema.Table` objects implicitly declared by
      subclasses of the base will share this MetaData.  A MetaData instance
      will be created if none is provided.  The
      :class:`~sqlalchemy.schema.MetaData` instance will be available via the
      ``metadata`` attribute of the generated declarative base class.
    :param mapper:
      An optional callable, defaults to :class:`_orm.Mapper`. Will
      be used to map subclasses to their Tables.
    :param cls:
      Defaults to :class:`object`. A type to use as the base for the generated
      declarative base class. May be a class or tuple of classes.
    :param name:
      Defaults to ``Base``.  The display name for the generated
      class.  Customizing this is not required, but can improve clarity in
      tracebacks and debugging.
    :param constructor:
      Specify the implementation for the ``__init__`` function on a mapped
      class that has no ``__init__`` of its own.  Defaults to an
      implementation that assigns \**kwargs for declared
      fields and relationships to an instance.  If ``None`` is supplied,
      no __init__ will be provided and construction will fall back to
      cls.__init__ by way of the normal Python semantics.
    :param class_registry: optional dictionary that will serve as the
      registry of class names-> mapped classes when string names
      are used to identify classes inside of :func:`_orm.relationship`
      and others.  Allows two or more declarative base classes
      to share the same registry of class names for simplified
      inter-base relationships.
    :param type_annotation_map: optional dictionary of Python types to
        SQLAlchemy :class:`_types.TypeEngine` classes or instances.  This
        is used exclusively by the :class:`_orm.MappedColumn` construct
        to produce column types based on annotations within the
        :class:`_orm.Mapped` type.
        .. versionadded:: 2.0
        .. seealso::
            :ref:`orm_declarative_mapped_column_type_map`
    :param metaclass:
      Defaults to :class:`.DeclarativeMeta`.  A metaclass or __metaclass__
      compatible callable to use as the meta type of the generated
      declarative base class.
    .. seealso::
        :class:`_orm.registry`
    """
    base = declarative_base(
        metadata=metadata,
        mapper=mapper,
        cls=cls,
        name=name,
        class_registry=class_registry,
        type_annotation_map=type_annotation_map,
        constructor=constructor,
        metaclass=metaclass,
    )
    if DB.default_base is None or DB.default_base == sentinel:
      DB.default_base = base
    return base
