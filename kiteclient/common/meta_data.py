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

from kiteclient.openstack.common import jsonutils
from kiteclient.openstack.common import timeutils


class Metadata(object):

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
