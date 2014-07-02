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

"""
test_esek
----------------------------------

Tests for `esek` module.
"""

from kiteclient.openstack.common.crypto import utils as cryptoutils
from kiteclient.tests import base
from kiteclient.v1 import esek
from kiteclient.v1 import key

import utils

import base64


class TestEsek(base.TestCase):

    def setUp(self):
        super(base.TestCase, self).setUp()
        key_ses = utils.DummyKeyResponse(gen=20)

        skey_data = "gTqLlW7x2oyNi3k+9YXTpQ=="
        self.srckey = key.Key('testkey', skey_data, session=key_ses)

        dkey_data = "uoUUn/+ZL+hNUwJ0cxTScg=="
        self.dstkey = key.Key('destkey', dkey_data, session=key_ses)

        self.skey = "uZnhYaRtzA7QdnDN1hVSWw=="
        self.ekey = "fAlG9eGL44ew6q8uTMMKJw=="

        self.esek_data = (
            "LZ6WWNvCot49sEhnwn0Is/xGWYGQF72rCw8emEKHGmZpDcSQ4K0c5Ld0+fmR"
            "T8PjzozEzWK97gNJQHZWSAh1JhmvMO+bjkUNlEdepOjTXrIW6QxdNvMY+Bkd"
            "dDwrkKga4wZnoGgeMgK+B7cdGsQ8yAPE3vDjbpmIOvHjHXniCUs=")

    def _encrypt(self, data):
        crypto = cryptoutils.SymmetricCrypto(enctype='AES',
                                             hashtype='SHA256')
        enc = crypto.encrypt(base64.b64decode(self.ekey),
                             data, b64encode=True)
        sig = crypto.sign(base64.b64decode(self.skey),
                          data, b64encode=True)
        return enc, sig

    def test_integrity(self):
        esek_obj = esek.Esek(self.srckey.key_name,
                             self.dstkey,
                             self.esek_data)
        b64_sig_key = base64.b64encode(esek_obj.sig_key)
        b64_enc_key = base64.b64encode(esek_obj.enc_key)
        self.assertEqual(self.skey, b64_sig_key)
        self.assertEqual(self.ekey, b64_enc_key)

    def test_decryption(self):
        esek_obj = esek.Esek(self.srckey.key_name,
                             self.dstkey,
                             self.esek_data)

        message = "MESSAGE"
        enc, sig = self._encrypt(message)
        new_message = esek_obj.decrypt(enc, sig)
        self.assertEqual(message, new_message)

    def test_bad_signature_throws(self):
        esek_obj = esek.Esek(self.srckey.key_name,
                             self.dstkey,
                             self.esek_data)
        message = "MESSAGE"
        enc, _ = self._encrypt(message)
        sig = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        self.assertRaises(ValueError, esek_obj.decrypt, enc, sig)