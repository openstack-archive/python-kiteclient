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

from Crypto import Random

from kiteclient.common import resource
from kiteclient.openstack.common.crypto import utils as cryptoutils


class Key(resource.Resource):

    base_path = 'keys'

    def __init__(self, name, b64_key, generation=None, session=None):
        self.name = name
        self.b64_key = b64_key
        self.generation = generation

        if session:
            self.create(session)

    @classmethod
    def generate(cls, name, session=None):
        b64_key = base64.b64encode(Random.new().read(16))
        return cls(name, b64_key, session=session)

    @property
    def key(self):
        return base64.b64decode(self.b64_key)

    @key.setter
    def key(self, val):
        self.b64_key = base64.b64encode(val)

    @property
    def key_name(self):
        return '%s:%d' % (self.name, self.generation)

    def __repr__(self):
        return '<Key %s - %s>' % (self.key_name, self.b64_key)

    def sign(self, data, hashtype='SHA256', b64encode=True):
        crypto = cryptoutils.SymmetricCrypto(hashtype=hashtype)
        return crypto.sign(self.key, data, b64encode=b64encode)

    def encrypt(self, data, enctype='AES', b64encode=True):
        crypto = cryptoutils.SymmetricCrypto(enctype=enctype)
        return crypto.encrypt(self.key, data, b64encode=b64encode)

    def decrypt(self, data, enctype='AES', b64decode=True):
        crypto = cryptoutils.SymmetricCrypto(enctype=enctype)
        return crypto.decrypt(self.key, data, b64decode=b64decode)

    def create(self, session):
        if self.generation:
            raise RuntimeError('This key has already been assigned a '
                               'generation meaning it has already been '
                               'created. Cannot create again')

        resp = self._http_put(session, self.name,
                              json={'key': self.b64_key}).json()

        if resp['name'] != self.name:
            raise ValueError('Name was changed in response')

        self.generation = resp['generation']
