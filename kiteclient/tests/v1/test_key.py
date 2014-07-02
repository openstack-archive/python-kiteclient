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
test_key
----------------------------------

Tests for `key` module.
"""

from kiteclient.tests import base
from kiteclient.tests.v1 import utils
from kiteclient.v1 import key

import base64

import six


class TestKey(base.TestCase):

    def setUp(self):
        super(base.TestCase, self).setUp()
        self.dummy_session = utils.DummyKeyResponse(gen=3)
        self.test_key_name = "testkey"
        self.test_key_b64key = "uoUUn/+ZL+hNUwJ0cxTScg=="

    def test_createkey_with_session(self):
        srckey = key.Key(self.test_key_name,
                         self.test_key_b64key,
                         session=self.dummy_session)

        key_id = "%s:%s" % (self.test_key_name,
                            self.dummy_session.generation)

        self.assertEqual(key_id, srckey.key_name)
        self.assertEqual(six.b("uoUUn/+ZL+hNUwJ0cxTScg=="),
                         base64.b64encode(srckey.key))

    def test_createkey_with_generation(self):
        srckey = key.Key(self.test_key_name,
                         self.test_key_b64key,
                         generation=self.dummy_session.generation)

        key_id = "%s:%s" % (self.test_key_name,
                            self.dummy_session.generation)

        self.assertEqual(key_id, srckey.key_name)
        self.assertEqual(six.b("uoUUn/+ZL+hNUwJ0cxTScg=="),
                         base64.b64encode(srckey.key))

    def test_bad_key_generation(self):
        self.assertRaises(RuntimeError,
                          key.Key,
                          self.test_key_name,
                          self.test_key_b64key,
                          generation=1,
                          session=self.dummy_session)

    def test_encryption_roundtrip(self):
        srckey = key.Key(self.test_key_name,
                         self.test_key_b64key,
                         session=self.dummy_session)
        plain_text = six.b("MESSAGE")
        crypt_text = srckey.encrypt(plain_text)
        self.assertNotEqual(plain_text, crypt_text)
        self.assertEqual(plain_text, srckey.decrypt(crypt_text))

    def test_generate(self):
        srckey = key.Key.generate(self.test_key_name,
                                  self.dummy_session)

        key_id = "%s:%s" % (self.test_key_name,
                            self.dummy_session.generation)

        self.assertEqual(key_id, srckey.key_name)
        self.assertNotEqual(None, srckey.key)