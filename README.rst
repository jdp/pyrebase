Pyrebase
========

Pyrebase is a Firebase_ client library for Python.

Getting Started
---------------

Connecting to a Firebase location is easy. Here's how::

    >>> import pyrebase
    >>> f = pyrebase.Firebase('https://pyrebase.firebaseIO.com/')
    >>> c = f.push({'foo': 'bar'})
    >>> c.ref
    u'https://pyrebase.firebaseIO.com/-JHFR_y14CzSOm8q86G1/'
    >>> c.get()
    {u'foo': u'bar'}

Tests
-----

Pyrebase is tested with pytest_. To run the tests, use this command::

    $ make test

License
-------

Copyright 2014 Justin Poliey

`ISC License`_

.. _Firebase: http://www.firebase.com/
.. _pytest: http://pytest.org/
.. _`ISC License`: http://opensource.org/licenses/ISC
