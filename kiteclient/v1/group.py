# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import base64

import six

from kiteclient.common import meta_data
from kiteclient.common import resource
from kiteclient.openstack.common.crypto import utils as cryptoutils
from kiteclient.openstack.common import jsonutils


class GroupKey(resource.Resource):

    base_path = 'groups'

    def __init__(self, source, destination, timestamp=None, nonce=None,
                 session=None):
        self._group_key = None
        self.source = source
        self._destination = destination
        self._timestamp = timestamp
        self._metadata = None
        self._nonce = nonce

        if session:
            self.create(session)

    def __repr__(self):
        base = 'src: "%s", dst: "%s"' % (self.source.name, self._destination)

        group_key = None
        if self._group_key is not None:
            group_key = self.b64_key
        else:
            group_key = 'Not yet created'

        return '<GroupKey %s %s>' % (base, group_key)

    def create(self, session):
        b64_metadata = meta_data.Metadata(self.source.name,
                                          self._destination,
                                          self._timestamp,
                                          self._nonce).encode()
        b64_signature = self.source.sign(b64_metadata, b64encode=True)

        json = {'metadata': b64_metadata,
                'signature': b64_signature}

        resp = self._http_post(session, json=json).json()

        b64_metadata = resp['metadata']
        b64_group_key = resp['group_key']
        b64_signature = resp['signature']

        sig = self.source.sign(six.b(b64_metadata + b64_group_key),
                               b64encode=True)

        if sig != six.b(b64_signature):
            raise ValueError("invalid signature on group key")

        group_key = self.source.decrypt(b64_group_key, b64decode=True)
        self._group_key = base64.b64encode(group_key)
        self._metadata = jsonutils.loads(base64.b64decode(b64_metadata))

    @property
    def b64_key(self):
        return self._group_key

    @property
    def key(self):
        return base64.b64decode(self._group_key)

    def encrypt(self, data, enctype='AES', hashtype='SHA256', b64encode=True):
        crypto = cryptoutils.SymmetricCrypto(enctype=enctype,
                                             hashtype=hashtype)

        enc = crypto.encrypt(self.key, data, b64encode=b64encode)
        #  sig = crypto.sign(self.skey, data, b64encode=b64encode)
        return enc  # , sig  no signing key? hummmmm


class Group(resource.Resource):

    base_path = 'groups'

    def __init__(self, name, session=None):
        self.name = name
        if session:
            self.create(session)

    def create(self, session):
        resp = self._http_put(session, self.name).json()

        if resp['name'] != self.name:
            raise ValueError('Name was changed in response')

    def getKey(self, source, session):
        return GroupKey(source, self.name, session=session)
