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
test_group
----------------------------------

Tests for `group` module.
"""

from kiteclient.tests import base
from kiteclient.tests.v1 import utils
from kiteclient.v1 import group
from kiteclient.v1 import key

import base64
import datetime

import six


class TestTicket(base.TestCase):

    def setUp(self):
        super(base.TestCase, self).setUp()
        self.nonce = 1062304930675487541
        self.stamp = datetime.datetime(2014, 11, 2, 8, 19, 4, 333230)

        key_ses = utils.DummyKeyResponse(gen=12)

        skey_data = "mIu9E64f0FyJo/BfNCRVGw=="
        self.srckey = key.Key('testkeyA', skey_data, session=key_ses)

        self.gkey_signature = (
            "MD2/BRMAlaabYugGkaLXeqrs6RDnKfoDhcJ/2Ty6xco=")

        self.gkey_metadata = (
            "eyJzb3VyY2UiOiAidGVzdGdyb3VwLnRlc3RrZXlBOjEyIiwgImRlc3Rpbm"
            "F0aW9uIjogInRlc3Rncm91cDo0IiwgImV4cGlyYXRpb24iOiAiMjAxNC0w"
            "OS0xMlQxMzowMjo1Mi44NTk2MTYiLCAiZW5jcnlwdGlvbiI6IHRydWV9")

        self.group_key = (
            "bar6L/o/otlfs+X36x6QW2UZVwAMx/fBOFZhdjB8PtkhZwVd2Z/t7GJ4Ki"
            "yB2lgP")

        self.dummy_session = utils.DummyGroupKeyResponse(self.gkey_signature,
                                                         self.gkey_metadata,
                                                         self.group_key)

    def test_integrity(self):
        gkey = group.GroupKey(self.srckey,
                              "testgroup",
                              timestamp=self.stamp,
                              nonce=self.nonce,
                              session=self.dummy_session)

        # decrypted group key
        group_key = six.b("Z6D3jvXWG2Ybg15EfamkEQ==")

        self.assertEqual(group_key, gkey.b64_key)
        self.assertEqual(gkey.b64_key, base64.b64encode(gkey.key))

    def test_bad_signature_throws(self):
        bad_signature = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        bad_session = utils.DummyGroupKeyResponse(bad_signature,
                                                  self.gkey_metadata,
                                                  self.group_key)
        self.assertRaises(ValueError,
                          group.GroupKey,
                          self.srckey,
                          "testgroup",
                          session=bad_session)
