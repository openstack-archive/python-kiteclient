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

from kiteclient.openstack.common.crypto import utils as cryptoutils
from kiteclient.openstack.common import jsonutils
from kiteclient.openstack.common import timeutils


class Esek(object):

    def __init__(self, source, destination, b64_data,
                 hashtype='SHA256', key_size=16):
        data = jsonutils.loads(destination.decrypt(b64_data, b64decode=True))

        base_key = base64.b64decode(data['key'])
        key_info = '%s,%s,%s' % (source,
                                 destination.key_name,
                                 data['timestamp'])

        crypto = cryptoutils.HKDF(hashtype=hashtype)
        key_data = crypto.expand(base_key, key_info, key_size * 2)

        self.sig_key = key_data[:key_size]
        self.enc_key = key_data[key_size:]

        # TODO(jamielennox): timestamp validate
        self.timestamp = timeutils.parse_strtime(data['timestamp'])

    def decrypt(self, encrypted, signature, b64decode=True,
                enctype='AES', hashtype='SHA256'):
        crypto = cryptoutils.SymmetricCrypto(enctype=enctype,
                                             hashtype=hashtype)

        data = crypto.decrypt(self.enc_key, encrypted, b64decode=b64decode)

        # b64encode=b64decode looks funny but we only care about the comparison
        # and not the actual data so it doesn't matter if we do it as base64 or
        # bytes, just that they are both the same.
        sig = crypto.sign(self.sig_key, data, b64encode=b64decode)

        if sig != signature:
            raise ValueError("Invalid signature")

        return data
