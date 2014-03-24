#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module is just wrapper over python's
`JSON module <http://docs.python.org/2/library/json.html>`_. It allows you to
serialize ``namedtuple`` and other default python data in very comfortable
way - if you initialize it properly, it just works and you don't have to take
care about anything.

Note:
    This module exists only because standard JSON module can't serialize
    ``namedtuple``. If you don't need to serialize ``namedtuple``, you don't
    need this module.

Serialization details
---------------------
``namedtuple`` is serialized to ``dict`` with special property ``__nt_name``,
where the name of the ``namedtuple`` `class` is stored.

Live example::

    >>> from collections import namedtuple
    >>> from edeposit.amqp.serializers import serialize, init_globals
    >>> init_globals(globals())
    >>> 
    >>> Person = namedtuple("Person", ["name", "surname"])
    >>> p = Person("Lishaak", "Bystroushaak")
    >>> p
    Person(name='Lishaak', surname='Bystroushaak')
    >>> serialize(p)
    '{"surname": "Bystroushaak", "name": "Lishaak", "__nt_name": "Person"}'

isinstance
==========
If you try to serialize module from different hierarchy path, than where it
will be deserialized, you may run into problems with ``isinstance()``, which
compares by full path, not just by `class` identity.

Lets take object `p` from previous example::

    >>> p
    Person(name='Lishaak', surname='Bystroushaak')
    >>> type(p)
    <class '__main__.Person'>

As you can see, type of the object is ``<class '__main__.Person'>``. In case
where the ``namedtuple`` `class` would be defined in module ``Y``, you would
get something like ``<class 'Y.Person'>`` and you would run into errors, when
you would try to compare these two for identity.

This is not the issue in normal ``namedtuple`` usage, because you usually
wouldn´t have two definitions of same `class`. In case of desesrialization, you
can run into this problems.

Trivial solution is to compare without full paths, just the names of the
`classes` by using :func:`iiofany`.


API
---
"""
#= Imports ====================================================================
import json
from collections import namedtuple  # has to be imported for deserialization


#= Functions & objects ========================================================
def init_globals(given_globals):
    """
    Initialize global variables, so the module will be able to guess names of
    classes automatically.

    Args:
        given_globals (dict): data returned from ``globals()`` call in your
                              module

    Warning:
        This function has to be called before you can use (de)serialization
        functions!

    Example of initialization::

        import serializers
        serializers.init_globals(globals())
        serializers.serialize(some_crazy_data)
    """
    local_globals = globals()

    for key in given_globals:
        if key not in local_globals:
            local_globals[key] = given_globals[key]


def _serializeNT(data):
    """
    Serialize namedtuples (and other basic python types) to dictionary with
    some special properties.

    Args:
        data (namedtuple/other python types): Data which will be serialized to
             dict.

    Data can be later automatically de-serialized by calling _deserializeNT().
    """
    if isinstance(data, list):
        return map(lambda x: _serializeNT(x), data)

    elif isinstance(data, tuple) and hasattr(data, "_fields"):  # is namedtuple
        serialized = _serializeNT(dict(data._asdict()))
        serialized["__nt_name"] = data.__class__.__name__

        return serialized

    elif isinstance(data, tuple):
        return tuple(map(lambda x: _serializeNT(x), data))

    elif isinstance(data, dict):
        return dict(
            map(
                lambda key: [key, _serializeNT(data[key])],
                data
            )
        )

    return data


def serialize(python_data):
    """
    Serialize class hierarchy into JSON.

    Args:
        data (any): any python type serializable to JSON, with added support of
                    namedtuples

    Returns:
        unicode: JSON string
    """
    return json.dumps(_serializeNT(python_data))


def _deserializeNT(data):
    """
    Deserialize special kinds of dicts from _serializeNT().
    """
    if isinstance(data, list):
        return map(lambda x: _deserializeNT(x), data)

    elif isinstance(data, tuple):
        return tuple(map(lambda x: _deserializeNT(x), data))

    elif isinstance(data, dict) and "__nt_name" in data:  # is namedtuple
        class_name = data["__nt_name"]
        del data["__nt_name"]

        return globals()[class_name](
            **dict(zip(data, _deserializeNT(data.values())))
        )

    elif isinstance(data, dict):
        return dict(
            map(
                lambda key: [key, _deserializeNT(data[key])],
                data
            )
        )

    elif isinstance(data, unicode):
        return data.encode("utf-8")

    return data


def deserialize(json_str):
    """
    Deserialize classes from JSON back to python data.

    Args:
        json_str (str): JSON encoded string.

    Returns:
        any: any python type (make sure you have namedtuples imported)
    """
    return _deserializeNT(json.loads(json_str))


def iiOfAny(instance, classes):
    """
    Returns true, if `instance` is instance of any (iiOfAny) of the `classes`.

    This function doesn't use isinstance() check, it just compares the
    `class` names.

    This can be generaly dangerous, but it is really useful when you are
    comparing class serialized in one module and deserialized in another.

    This causes, that module paths in class internals are different and
    ``isinstance()`` and ``type()`` comparsions thus fails.

    Use this function instead, if you wan't to check what type is your
    deserialized message.

    Args:
        instance (object): class instance you want to know the type
        classes (list): classes, or just one class you want to compare - func
                        automatically converts nonlist/nontuple parameters to
                        list

    Returns:
        bool: True if `instance` **can be** instance of any of the `classes`.
    """
    if type(classes) not in [list, tuple]:
        classes = [classes]

    return any(map(lambda x: type(instance).__name__ == x.__name__, classes))
