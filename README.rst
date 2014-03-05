Pyrebase
========

Pyrebase is a Firebase_ client library for Python.

Getting Started
---------------

Connecting to a Firebase location and adding data to it is easy. Here's how::

    >>> import pyrebase
    >>> f = pyrebase.Firebase('https://pyrebase.firebaseIO.com/')
    >>> c = f.push({'foo': 'bar'})
    >>> c.ref
    u'https://pyrebase.firebaseIO.com/-JHFR_y14CzSOm8q86G1/'
    >>> c.get()
    {u'foo': u'bar'}

Traversing locations is simple with the ``parent``, ``child``, and ``root`` methods::

    >>> f = pyrebase.Firebase('https://pyrebase.firebaseIO.com/pokemon/bulbasaur')
    >>> f.root.ref
    'https://pyrebase.firebaseIO.com/'
    >>> f.parent.ref
    'https://pyrebase.firebaseIO.com/pokemon/'
    >>> f.parent.parent.ref
    'https://pyrebase.firebaseIO.com/'
    >>> f.parent.child('squirtle').ref
    'https://pyrebase.firebaseIO.com/pokemon/squirtle/'

Remember to use the official `firebase-token-generator`_ package for authentication::

    >>> from firebase_token_generator import create_token
    >>> custom_data = {'pokemon_master': True}
    >>> options = {'admin': True}
    >>> token = create_token('not-a-fake-firebase-secret', custom_data, options)
    >>> f = pyrebase.Firebase('https://pyrebase.firebaseIO.com/', auth=token)
  
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
.. _`firebase-token-generator`: https://pypi.python.org/pypi/firebase-token-generator/1.3.2
