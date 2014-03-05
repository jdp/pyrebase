import os.path
import random
import string

import pytest

import pyrebase


def test_wrap_mapping():
    data = 1
    wrapped = pyrebase.wrap_mapping(data)
    assert wrapped['.value'] == 1

    data = {'foo': 'bar'}
    wrapped = pyrebase.wrap_mapping(data)
    assert '.value' not in wrapped
    assert data == wrapped


def test_ref():
    f = pyrebase.Firebase('https://pyrebase.firebaseIO.com')
    assert f.ref == 'https://pyrebase.firebaseIO.com/'
    f = pyrebase.Firebase('https://pyrebase.firebaseIO.com/')
    assert f.ref == 'https://pyrebase.firebaseIO.com/'


class MockTransport(object):
    def __init__(self):
        self.mapping = {}

    def normalize(self, ref):
        if not ref.endswith('/'):
            return ref + '/'
        return ref

    def get(self, ref, params):
        try:
            data = self.mapping[self.normalize(ref)]
        except KeyError:
            return
        return data

    def set(self, ref, params, data):
        if pyrebase.is_mapping(data):
            if '.priority' in data:
                priority_ref = os.path.join(os.path.dirname(self.normalize(ref)), '.priority')
                priority = data.pop('.priority')
                self.set(priority_ref, params, priority)
            if '.value' in data:
                data = data['.value']
        self.mapping[self.normalize(ref)] = data
        return data

    def push(self, ref, params, data):
        name = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(16))
        pushed_ref = os.path.join(os.path.dirname(ref), name)
        self.set(pushed_ref, params, data)
        return {'name': name}

    def update(self, ref, params, data):
        self.mapping[self.normalize(ref)].update(data)
        return data

    def remove(self, ref, params):
        del self.mapping[self.normalize(ref)]


@pytest.fixture(params=[MockTransport()])
def firebase(request):
    import pyrebase
    return pyrebase.Firebase('https://pyrebase.firebaseIO.com/', transport=request.param)


def test_child(firebase):
    c = firebase.child('-Izjg-FkP7eXLa1EXVAi')
    assert c.ref == 'https://pyrebase.firebaseIO.com/-Izjg-FkP7eXLa1EXVAi/'

    c = firebase.child('foo/bar')
    assert c.ref == 'https://pyrebase.firebaseIO.com/foo/bar/'

    c = firebase.child('.')
    assert c.ref == 'https://pyrebase.firebaseIO.com/'

    c = firebase.child('..')
    assert c.ref == 'https://pyrebase.firebaseIO.com/'

    c = firebase.child('foo/bar/..')
    assert c.ref == 'https://pyrebase.firebaseIO.com/foo/'

    c = firebase.child('foo/../bar')
    assert c.ref == 'https://pyrebase.firebaseIO.com/bar/'


def test_child_priority(firebase):
    c = firebase.child('-Izjg-FkP7eXLa1EXVAi').child('.priority')
    assert c.ref == 'https://pyrebase.firebaseIO.com/-Izjg-FkP7eXLa1EXVAi/.priority/'


def test_nested_child(firebase):
    c = firebase.child('-Izjg-FkP7eXLa1EXVAi').child('-Izjh72mPJj7xJm0e4kQ')
    assert c.ref == 'https://pyrebase.firebaseIO.com/-Izjg-FkP7eXLa1EXVAi/-Izjh72mPJj7xJm0e4kQ/'
    c = firebase.child('-Izjg-FkP7eXLa1EXVAi/-Izjh72mPJj7xJm0e4kQ')
    assert c.ref == 'https://pyrebase.firebaseIO.com/-Izjg-FkP7eXLa1EXVAi/-Izjh72mPJj7xJm0e4kQ/'


def test_parent(firebase):
    assert firebase.ref == firebase.parent.ref

    child = firebase.child('-Izjg-FkP7eXLa1EXVAi/-Izjh72mPJj7xJm0e4kQ')
    parent = child.parent
    assert parent.ref == 'https://pyrebase.firebaseIO.com/-Izjg-FkP7eXLa1EXVAi/'
    root = parent.parent
    assert root.ref == 'https://pyrebase.firebaseIO.com/'


def test_root(firebase):
    c = firebase.child('-Izjg-FkP7eXLa1EXVAi/-Izjh72mPJj7xJm0e4kQ')
    assert c.root.ref == firebase.ref


def test_prepare_data(firebase):
    simple_payload = 'foo'
    prepared = firebase.prepare_data(simple_payload, None)
    assert prepared == simple_payload

    prepared = firebase.prepare_data(simple_payload, 1)
    assert prepared['.value'] == 'foo'
    assert prepared['.priority'] == 1.0

    complex_payload = {'foo': 'bar'}
    prepared = firebase.prepare_data(complex_payload, None)
    assert prepared == complex_payload
    assert '.value' not in prepared

    prepared = firebase.prepare_data(complex_payload, 2)
    assert '.value' not in prepared
    assert prepared['foo'] == 'bar'
    assert prepared['.priority'] == 2.0


def test_set(firebase):
    assert firebase.set(True) == True
    assert firebase.child('bar').set('foo') == 'foo'
    assert firebase.set([1, 2, 3]) == [1, 2, 3]
    assert firebase.set({'foo': 'bar'}) == {'foo': 'bar'}

    assert firebase.set('foo', priority=5) == 'foo'


def test_get(firebase):
    firebase.set('foo')
    assert firebase.get() == 'foo'


def test_set_priority(firebase):
    firebase.set('foo')
    assert firebase.set_priority(5) == 5


def test_get_priority(firebase):
    firebase.set('foo', priority=5)
    assert firebase.get_priority() == 5


def test_push(firebase):
    c = firebase.push('foo')
    assert c.ref != firebase.ref
    assert c.get() == 'foo'

    c = firebase.push('bar', priority=3)
    assert c.get() == 'bar'
    assert c.get_priority() == 3


def test_update(firebase):
    firebase.set({'foo': 'bar'})
    assert firebase.get() == {'foo': 'bar'}
    assert firebase.update({'baz': 'quux'}) == {'baz': 'quux'}
    assert firebase.get() == {'foo': 'bar', 'baz': 'quux'}


def test_remove(firebase):
    c = firebase.push('foo')
    c.remove()
    assert c.get() is None
