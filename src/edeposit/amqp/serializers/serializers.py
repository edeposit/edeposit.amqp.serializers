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


def toJSON(structure):
    """
    Convert structure to json.

    This is necessary, because standard JSON module can't serialize
    namedtuples.

    Args:
        structure (namedtuple/basic python types): data which will be
                  serialized to JSON.

    Returns:
        str: with serialized data.
    """
    return json.dumps(_serializeNT(structure))


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


def fromJSON(json_data):
    """
    Convert JSON string back to python structures.

    This is necessary, because standard JSON module can't serialize
    namedtuples.

    Args:
        json_data (str): JSON string.

    Returns:
        python data/nameduple: with deserialized data.
    """
    return _deserializeNT(json.loads(json_data))

def serialize(data):
    """
    Serialize class hierarchy into JSON.

    Args:
        data (any): any python type serializable to JSON, with added support of
                    namedtuples

    Returns:
        unicode: JSON string
    """
    return toJSON(data)


def deserialize(data):
    """
    Deserialize classes from JSON data.

    Args:
        data (str): python data serialized to JSON

    Returns:
        any: any python typ (make sure you have namedtuples imported)
    """
    return fromJSON(data)

def test_JSON_convertor(self):
    data = ""
    with open(EXAMPLE_PATH) as f:
        data = f.read()

    epub = aleph.convertors.toEPublication(data)
    epub2 = aleph.convertors.fromJSON(aleph.convertors.toJSON(epub))

    assert(epub == epub2)
