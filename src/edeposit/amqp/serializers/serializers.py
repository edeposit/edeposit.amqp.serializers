#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
It can also serialize any namedtuple to JSON.
"""
#= Imports ====================================================================
import json
from collections import namedtuple  # has to be imported for deserialization


#= Functions & objects ========================================================
def init_globals(given_globals):
    """
    Initialize global variables, so the module will be able to guess names of
    classes authomatically.

    Args:
        given_globals (dict): data returned from ``globals()`` call in your
                              module

    Warning:
        This function has to be called before you can use (de)serialization
        functions!

    Example:
        import serializers
        serializers.init_globals(globals())
        serializers.serialize(som_crazy_data)
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

    Note:
        This is necessary, because standard JSON module can't serialize
        namedtuples.

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

    Note:
        This is necessary, because standard JSON module can't serialize
        namedtuples.

    Args:
        json_str (str): JSON encoded string.

    Returns:
        any: any python type (make sure you have namedtuples imported)
    """
    return _deserializeNT(json.loads(json_str))
