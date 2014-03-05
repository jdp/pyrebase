import json
import os.path
import urlparse

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


class Firebase(object):
    def __init__(self, ref, auth=None):
        self.ref = ref
        self.auth = auth

    @property
    def ref(self):
        return self._ref

    @ref.setter
    def ref(self, value):
        if not value.endswith('/'):
            value += '/'
        self._ref = value.strip()

    def get_ref_url(self):
        """Return the URL of this location.
        """
        return '{}.json'.format(self.ref)

    def get(self, format=None):
        """Return the data at this location.
        """
        params = self.get_params(format=format)
        r = requests.get(self.get_ref_url(), params=params)
        r.raise_for_status()
        return self.decode(r.text)

    def get_priority(self):
        """Return the priority of the data at this location.
        """
        child = self.child('.priority')
        return child.get()

    def set(self, value, priority=None):
        """Set the data at this location.
        """
        params = self.get_params()
        data = self.encode(self.prepare_data(value, priority))
        r = requests.put(self.get_ref_url(), params=params, data=data)
        r.raise_for_status()
        return self.decode(r.text)

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
        data = self.encode(self.prepare_data(value, priority))
        r = requests.post(self.get_ref_url(), params=params, data=data)
        r.raise_for_status()
        resp = self.decode(r.text)
        return self.child(resp['name'])

    def update(self, value, priority=None):
        """Update the data at this location.
        """
        params = self.get_params()
        data = self.encode(self.prepare_data(value, priority))
        r = requests.patch(self.get_ref_url(), params=params, data=data)
        r.raise_for_status()

    def remove(self):
        """Remove this location.
        """
        params = self.get_params()
        r = requests.delete(self.get_ref_url(), params=params)
        r.raise_for_status()

    def child(self, path):
        """Return a child location under this location.
        """
        child_ref = urlparse.urljoin(self.ref, path.lstrip().lstrip('/'))
        return self.__class__(child_ref, auth=self.auth)

    @property
    def parent(self):
        """Return the parent of this location.
        """
        parts = urlparse.urlsplit(self.ref)
        path_up = os.path.split(parts.path.rstrip('/'))[0]
        newparts = (parts.scheme,
                    parts.netloc,
                    path_up,
                    parts.query,
                    parts.fragment)
        parent_ref = urlparse.urlunsplit(newparts)
        return self.__class__(parent_ref, auth=self.auth)

    @property
    def root(self):
        """Return the root location.
        """
        root_ref = urlparse.urljoin(self.ref, '/')
        return self.__class__(root_ref, auth=self.auth)

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

    def encode(self, data):
        return json.dumps(data)

    def decode(self, data):
        return json.loads(data)
