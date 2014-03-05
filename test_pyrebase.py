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


@pytest.fixture
def firebase():
    import pyrebase
    return pyrebase.Firebase('https://pyrebase.firebaseIO.com/')


def test_ref_url(firebase):
    assert firebase.get_ref_url() == 'https://pyrebase.firebaseIO.com/.json'


def test_child(firebase):
    c = firebase.child('-Izjg-FkP7eXLa1EXVAi')
    assert c.get_ref_url() == 'https://pyrebase.firebaseIO.com/-Izjg-FkP7eXLa1EXVAi/.json'


def test_child_priority(firebase):
    c = firebase.child('-Izjg-FkP7eXLa1EXVAi').child('.priority')
    assert c.get_ref_url() == 'https://pyrebase.firebaseIO.com/-Izjg-FkP7eXLa1EXVAi/.priority/.json'


def test_nested_child(firebase):
    c = firebase.child('-Izjg-FkP7eXLa1EXVAi').child('-Izjh72mPJj7xJm0e4kQ')
    assert c.get_ref_url() == 'https://pyrebase.firebaseIO.com/-Izjg-FkP7eXLa1EXVAi/-Izjh72mPJj7xJm0e4kQ/.json'
    c = firebase.child('-Izjg-FkP7eXLa1EXVAi/-Izjh72mPJj7xJm0e4kQ')
    assert c.get_ref_url() == 'https://pyrebase.firebaseIO.com/-Izjg-FkP7eXLa1EXVAi/-Izjh72mPJj7xJm0e4kQ/.json'


def test_parent(firebase):
    assert firebase.get_ref_url() == firebase.parent.get_ref_url()

    child = firebase.child('-Izjg-FkP7eXLa1EXVAi/-Izjh72mPJj7xJm0e4kQ')
    parent = child.parent
    assert parent.get_ref_url() == 'https://pyrebase.firebaseIO.com/-Izjg-FkP7eXLa1EXVAi/.json'
    root = parent.parent
    assert root.get_ref_url() == 'https://pyrebase.firebaseIO.com/.json'


def test_root(firebase):
    f = firebase.child('-Izjg-FkP7eXLa1EXVAi/-Izjh72mPJj7xJm0e4kQ')
    assert f.root.get_ref_url() == firebase.get_ref_url()


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
