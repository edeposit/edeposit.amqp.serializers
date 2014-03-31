#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module is just wrapper over python's
`JSON module <http://docs.python.org/2/library/json.html>`_. It allows you to
serialize :py:func:`collections.namedtuple` and other default python data in
very comfortable way - if you initialize it properly, it just works and you
don't have to take care about anything.

Note:
    This module exists only because standard JSON module can't serialize
    :py:func:`collections.namedtuple`. If you don't need to serialize 
    :py:func:`collections.namedtuple`, you don't need this module.

Serialization details
---------------------
:py:func:`collections.namedtuple` is serialized to :py:class:`dict` with special
property ``__nt_name``, where the name of the :py:func:`collections.namedtuple`
`class` is stored.

Live example::

    >>> from collections import namedtuple
    >>> from edeposit.amqp.serializers import serialize
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
will be deserialized, you may run into problems with :py:func:`isinstance`,
which compares by full path, not just by `class` identity.

Lets take object `p` from previous example::

    >>> p
    Person(name='Lishaak', surname='Bystroushaak')
    >>> type(p)
    <class '__main__.Person'>

As you can see, type of the object is ``<class '__main__.Person'>``. In case
where the :py:func:`collections.namedtuple` `class` would be defined in module
``Y``, you would get something like ``<class 'Y.Person'>`` and you would run
into errors, when you would try to compare these two for identity.

This is not the issue in normal :py:func:`collections.namedtuple` usage, because
you usually wouldn´t have two definitions of same `class`. In case of
desesrialization, you can run into this problems.

Trivial solution is to compare without full paths, just the names of the
`classes` by using :func:`iiOfAny`.


API
---
"""
#= Imports ====================================================================
import json
from collections import namedtuple  # has to be imported for deserialization


#= Functions & objects ========================================================
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
        data (any): any python type serializable to :py:mod:`json`, with added
                    support of :py:func:`collections.namedtuple`

    Returns:
        unicode: :py:mod:`json` string
    """
    return json.dumps(_serializeNT(python_data))


def _deserializeNT(data, glob):
    """
    Deserialize special kinds of dicts from _serializeNT().
    """
    if isinstance(data, list):
        return map(lambda x: _deserializeNT(x, glob), data)

    elif isinstance(data, tuple):
        return tuple(map(lambda x: _deserializeNT(x, glob), data))

    elif isinstance(data, dict) and "__nt_name" in data:  # is namedtuple
        class_name = data["__nt_name"]
        del data["__nt_name"]

        # given globals
        if class_name in glob:
            return glob[class_name](
                **dict(zip(data, _deserializeNT(data.values(), glob)))
            )

        # "local" (package) globals
        return globals()[class_name](
            **dict(zip(data, _deserializeNT(data.values(), glob)))
        )

    elif isinstance(data, dict):
        return dict(
            map(
                lambda key: [key, _deserializeNT(data[key], glob)],
                data
            )
        )

    elif isinstance(data, unicode):
        return data.encode("utf-8")

    return data


def deserialize(json_str, glob):
    """
    Deserialize classes from JSON back to python data.

    Args:
        json_str (str): :py:mod:`json` encoded string.
        glob (dict):    Output from :py:func:`globals` call - your context of
                        variables.

    Call example::

        deserialize(data, globals())

    Warning:
        Call the :py:func:`globals` every time, you call this function, because
        your variable context could change. Also don't pass a blank dict - it
        may work sometimes, but fail unpredictably later.

    Returns:
        any: any python type (make sure you have namedtuples imported)
    """
    return _deserializeNT(json.loads(json_str), glob)


def iiOfAny(instance, classes):
    """
    Returns true, if `instance` is instance of any (iiOfAny) of the `classes`.

    This function doesn't use :py:func:`isinstance` check, it just compares the
    `class` names.

    This can be generaly dangerous, but it is really useful when you are
    comparing class serialized in one module and deserialized in another.

    This causes, that module paths in class internals are different and
    :py:func:`isinstance` and :py:func:`type` comparsions thus fails.

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
