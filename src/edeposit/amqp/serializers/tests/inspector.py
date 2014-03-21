#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# library for Robot Framework to inspect python modules
#

import imp
import edeposit.amqp.aleph as aleph
import edeposit.amqp.aleph.export as export
import edeposit.amqp.aleph.convertor as convertor

import os.path


BASE_PATH = os.path.dirname(__file__)
EXAMPLE_PATH = BASE_PATH + "/"
EXAMPLE_PATH += "resources/aleph_data_examples/xml_outputs/example4.xml"


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

    def aleph_request(self, request):
        def blank_fn(result, uuid):
            return result

        return aleph.reactToAMQPMessage(
            request,
            blank_fn,
            "0"
        )

    def greater_or_equal_than(self, lvalue, rvalue):
        if int(lvalue) < int(rvalue):
            raise AssertionError(str(lvalue) + " is not >= " + str(rvalue))

    def length(self, val):
        return len(val)

    def test_JSON_convertor(self):
        data = ""
        with open(EXAMPLE_PATH) as f:
            data = f.read()

        epub = aleph.convertors.toEPublication(data)
        epub2 = aleph.convertors.fromJSON(aleph.convertors.toJSON(epub))

        assert(epub == epub2)