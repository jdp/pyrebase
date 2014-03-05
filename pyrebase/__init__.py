import json
import os.path

try:
    from urlparse import urljoin, urlsplit, urlunsplit
except ImportError:
    from urllib.parse import urljoin, urlsplit, urlunsplit

import requests


try:
    import collections
    def is_mapping(v):
        return isinstance(v, collections.Mapping)
except ImportError:
    def is_mapping(v):
        return isinstance(v, dict)


def wrap_mapping(value):
    """Return the wrapped version of a Firebase value.

    Non-mapping types need to be sent over the wire wrapped in a mapping type
    keyed by `.value` if they are to be prioritized.
    """
    if not is_mapping(value):
        return {'.value': value}
    return value


class ServerValue:
    TIMESTAMP = 'timestamp'


class HTTPTransport(object):
    def get(self, ref_url, params):
        r = requests.get(ref_url, params=params)
        r.raise_for_status()
        return self.decode(r.text)

    def set(self, ref_url, params, data):
        r = requests.put(ref_url, params=params, data=self.encode(data))
        r.raise_for_status()
        return self.decode(r.text)

    def push(self, ref_url, params, data):
        r = requests.post(ref_url, params=params, data=self.encode(data))
        r.raise_for_status()
        return self.decode(r.text)

    def update(self, ref_url, params, data):
        r = requests.patch(ref_url, params=params, data=self.encode(data))
        r.raise_for_status()
        return self.decode(r.text)

    def remove(self, ref_url, params):
        r = requests.delete(ref_url, params=params)
        r.raise_for_status()

    def encode(self, data):
        return json.dumps(data)

    def decode(self, data):
        return json.loads(data)


class Firebase(object):
    def __init__(self, ref, auth=None, transport=None):
        self.ref = ref
        self.auth = auth
        if transport is None:
            transport = HTTPTransport()
        self.transport = transport

    @property
    def ref(self):
        return self._ref

    @ref.setter
    def ref(self, value):
        if not value.endswith('/'):
            value += '/'
        self._ref = value.strip()

    @property
    def _ref_url(self):
        """Return the URL of this location.
        """
        return self.ref + '.json'

    def get(self, format=None):
        """Return the data at this location.
        """
        params = self.get_params(format=format)
        return self.transport.get(self._ref_url, params)

    def get_priority(self):
        """Return the priority of the data at this location.
        """
        child = self.child('.priority')
        return child.get()

    def set(self, value, priority=None):
        """Set the data at this location.
        """
        params = self.get_params()
        data = self.prepare_data(value, priority)
        return self.transport.set(self._ref_url, params, data)

    def set_priority(self, priority):
        """Set a priority for the data at this Firebase location.
        """
        child = self.child('.priority')
        return child.set(priority)

    def set_server_value(self, sv):
        """Set a server value at this location.
        """
        return self.set({'.sv': sv})

    def push(self, value, priority=None):
        """Create a new child location under this location.
        """
        params = self.get_params()
        data = self.prepare_data(value, priority)
        pushed = self.transport.push(self._ref_url, params, data)
        return self.child(pushed['name'])

    def update(self, value, priority=None):
        """Update the data at this location.
        """
        params = self.get_params()
        data = self.prepare_data(value, priority)
        return self.transport.update(self._ref_url, params, data)

    def remove(self):
        """Remove this location.
        """
        params = self.get_params()
        return self.transport.remove(self._ref_url, params)

    def _factory(self, ref):
        return self.__class__(ref, auth=self.auth, transport=self.transport)

    def child(self, path):
        """Return a child location under this location.
        """
        child_ref = urljoin(self.ref, path.lstrip().lstrip('/'))
        return self._factory(child_ref)

    @property
    def parent(self):
        """Return the parent of this location.
        """
        parts = urlsplit(self.ref)
        path_up = os.path.split(parts.path.rstrip('/'))[0]
        newparts = (parts.scheme,
                    parts.netloc,
                    path_up,
                    parts.query,
                    parts.fragment)
        parent_ref = urlunsplit(newparts)
        return self._factory(parent_ref)

    @property
    def root(self):
        """Return the root location.
        """
        root_ref = urljoin(self.ref, '/')
        return self._factory(root_ref)

    def get_params(self, **params):
        if self.auth and 'auth' not in params:
            params['auth'] = self.auth
        return params

    def prepare_data(self, value, priority):
        """Return a representation of `value` prepared to send to Firebase.
        """
        if priority is not None:
            value = wrap_mapping(value)
            value['.priority'] = float(priority)
        return value
