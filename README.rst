Introduction
============

This package provides functions to (de)serialize namedtuple to JSON.


`Full module documentation <http://edepositamqpserializers.readthedocs.org/en/latest/py-modindex.html>`_ is hosted at the `readthedocs <http://edepositamqpserializers.readthedocs.org/>`_.


Installation
------------

Module is hosted at `PYPI <http://pypi.python.org>`_, and can be easily installed using `PIP <http://en.wikipedia.org/wiki/Pip_%28package_manager%29>`_:

::

    pip install edeposit.amqp.serializers

Source codes can be found at `GitHub <https://github.com/>`_: https://github.com/jstavel/edeposit.amqp.serializers.

Content
-------
So far, module provides only one submodule:

edeposit.amqp.serializers.serializers
+++++++++++++++++++++++++++++++++++++

Serialization/deserialization functions to ``serialize()`` and ``deserialize()`` `namedtuples` to the JSON and back. Module needs to be initialized first by calling ``init_globals(globals())``.

All three functions are imported in ``__init__.py``, so you don't need to call ``edeposit.amqp.serializers.serializers`` - just ``edeposit.amqp.serializers`` will do.

Acceptance tests
----------------

`Robot Framework <http://robotframework.org/>`__ is used to test the sources, which are stored in ``src/edeposit/amqp/serializers/tests`` directory.

You can run them manually (from the root of the package):

::

    $ pybot -W 80 --pythonpath src/edeposit/amqp/serializers/tests/:src src/edeposit/amqp/serializers/tests/

Or continuously using nosier:

::

    $ nosier -p src -b 'export' "pybot -W 80 --pythonpath src/edeposit/amqp/serializers/tests/ --pythonpath src src/edeposit/amqp/serializers/tests/"

.. Status of acceptance tests
.. ++++++++++++++++++++++++++

.. You can see the results of the tests here:

.. http://edeposit-amqp-serializers.readthedocs.org/cs/latest/\_downloads/log.html

.. http://edeposit-amqp-serializers.readthedocs.org/cs/latest/\_downloads/report.html

.. Results are currently (21.03.2014) outdated, but some form of continuous integration framework will be used in the future.