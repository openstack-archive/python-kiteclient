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
import struct

from Crypto import Random
import six

from kiteclient.common import resource
from kiteclient.openstack.common.crypto import utils as cryptoutils
from kiteclient.openstack.common import jsonutils
from kiteclient.openstack.common import timeutils


class _Metadata(object):

    def __init__(self, source, destination, timestamp=None, nonce=None):
        self.source = source
        self.destination = destination
        self.timestamp = timestamp or timeutils.utcnow()
        self.nonce = nonce or self.gen_nonce()

    @classmethod
    def gen_nonce(cls):
        return struct.unpack('Q', Random.new().read(8))[0]

    def get_data(self):
        return {'source': self.source,
                'destination': self.destination,
                'timestamp': timeutils.strtime(self.timestamp),
                'nonce': self.nonce}

    def encode(self):
        data = self.get_data()
        return base64.b64encode(six.b(jsonutils.dumps(data)))


class Ticket(resource.Resource):

    base_path = 'tickets'

    def __init__(self, source, destination, timestamp=None, nonce=None,
                 session=None):
        self.source = source
        self._destination = destination
        self._timestamp = timestamp
        self._nonce = nonce

        self._ticket = None
        self._metadata = None

        if session:
            self.create(session)

    def create(self, session):
        b64_metadata = _Metadata(self.source.name, self._destination,
                                 self._timestamp, self._nonce).encode()
        b64_signature = self.source.sign(b64_metadata, b64encode=True)

        json = {'metadata': b64_metadata,
                'signature': b64_signature}

        resp = self._http_post(session, json=json).json()

        b64_metadata = resp['metadata']
        b64_ticket = resp['ticket']
        b64_signature = resp['signature']

        sig = self.source.sign(six.b(b64_metadata + b64_ticket),
                               b64encode=True)

        if sig != six.b(b64_signature):
            raise ValueError("invalid signature on ticket")

        data = self.source.decrypt(b64_ticket, b64decode=True)
        self._ticket = jsonutils.loads(data)
        self._ticket['skey'] = six.b(self._ticket['skey'])
        self._ticket['ekey'] = six.b(self._ticket['ekey'])
        self._ticket['esek'] = six.b(self._ticket['esek'])
        self._metadata = jsonutils.loads(base64.b64decode(b64_metadata))

    def __repr__(self):
        base = 'src: "%s", dst: "%s"' % (self.source.name, self._destination)

        if self._ticket:
            ticket = 'skey: "%s", ekey: "%s"' % (self.b64_skey, self.b64_ekey)
        else:
            ticket = 'Not yet created'

        return '<Ticket %s %s>' % (base, ticket)

    @property
    def expiration(self):
        return self._metadata["expiration"]

    @property
    def b64_skey(self):
        return self._ticket['skey']

    @property
    def skey(self):
        return base64.b64decode(self.b64_skey)

    @property
    def b64_ekey(self):
        return self._ticket['ekey']

    @property
    def ekey(self):
        return base64.b64decode(self.b64_ekey)

    @property
    def b64_esek(self):
        return self._ticket['esek']

    @property
    def esek(self):
        return base64.b64decode(self.b64_esek)

    def encrypt(self, data, enctype='AES', hashtype='SHA256', b64encode=True):
        crypto = cryptoutils.SymmetricCrypto(enctype=enctype,
                                             hashtype=hashtype)

        enc = crypto.encrypt(self.ekey, data, b64encode=b64encode)
        sig = crypto.sign(self.skey, data, b64encode=b64encode)
        return enc, sig
