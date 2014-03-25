#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# library for Robot Framework to inspect python modules
#

import imp
import os.path
from collections import namedtuple

import edeposit.amqp.serializers as serializers_package
import edeposit.amqp.serializers.serializers as serializers


BASE_PATH = os.path.dirname(__file__)


TestNT = namedtuple("TestNT", ["first", "second"])


class Inspector(object):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def variable_presented(self, modulePath, name):
        module = imp.load_source("module", modulePath)
        value = getattr(module, name)
        if not value:
            raise AssertionError(
                "Module: %s has no variable '%s'!" % (self.modulePath, name)
            )

    def is_type_of(self, element, reference):
        if type(element) != reference:
            raise AssertionError(
                "type(%s) != %s" % (str(type(element)), str(reference))
            )

    def call(self, fn, *args, **kwargs):
        return fn(*args, **kwargs)

    def length(self, val):
        return len(val)

    def has_attribute(self, obj, attr):
        return hasattr(obj, attr)

    def get_globals(self):
        return globals()

    def to_list(self, x):
        return list(x)

    def compare_nt(self, nt1, nt2):
        return nt1 == nt2
