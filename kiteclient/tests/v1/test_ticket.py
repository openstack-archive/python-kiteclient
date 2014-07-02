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
test_ticket
----------------------------------

Tests for `ticket` module.
"""

from kiteclient.tests import base
from kiteclient.tests.v1 import utils
from kiteclient.v1 import esek
from kiteclient.v1 import key
from kiteclient.v1 import ticket

from kiteclient.tests.v1 import utils

import base64
import datetime


class TestTicket(base.TestCase):

    def setUp(self):
        super(base.TestCase, self).setUp()
        self.nonce = 1062304930675487541
        self.stamp = datetime.datetime(2014, 7, 2, 8, 19, 4, 333230)

        key_ses = utils.DummyKeyResponse(gen=20)

        skey_data = "gTqLlW7x2oyNi3k+9YXTpQ=="
        self.srckey = key.Key('testkey', skey_data, session=key_ses)

        dkey_data = "uoUUn/+ZL+hNUwJ0cxTScg=="
        self.dstkey = key.Key('destkey', dkey_data, session=key_ses)

        self.tick_signature = (
            "4cj/JRJmvO9L2UlHu1SBOXIofwu3FEFCILTsznwIkd8=")

        self.tick_metadata = (
            "eyJzb3VyY2UiOiAidGVzdGtleToyMCIsICJkZXN0aW5hdGlvbiI6ICJkZX"
            "N0a2V5OjIwIiwgImV4cGlyYXRpb24iOiAiMjAxNC0wNy0wMlQwOTo1Njoz"
            "NC4zNDI1NTYiLCAiZW5jcnlwdGlvbiI6IHRydWV9")

        self.tick_ticket = (
            "tuKo7NlhkDFyL7YO9mPgtBe4cbJF9TIJfDcPmkCkeo1tee0p8pF2h3wYwn"
            "uC1wlt58lPc5don3ov9h16ncZh8PlIVT9JwSxg1o2tQLcByiTQ+PIqiMBp"
            "7uM0E4RZsPlED7f89gV/fIdz03OGPjh9oiN+yxRFL2UdMN8VKJVjFdkuNm"
            "zpmqbpmxKnkB4vueI3mokdfd3mr1xkYRrw/+L1xseayktgJX0ablgTMpvs"
            "e4V/ssbvZFON/dZMXRrQ4xxWxEI2mVMVq9WkkEPzGaPySZ2TKtWUS/QcFi"
            "OTNbP0hMwx2UuIjrUOX1V3cBUs8u/rJ8LCs8yRIT2xds6aLgPz8c9Z+bNO"
            "6U0LGkDRfKzaV79z+yjZXMbU+m2WYLIY2Cat")

        self.dummy_session = utils.DummyTicketResponse(self.tick_signature,
                                                       self.tick_metadata,
                                                       self.tick_ticket)

    def test_integrity(self):
        tick = ticket.Ticket(self.srckey,
                             self.dstkey.name,
                             timestamp=self.stamp,
                             nonce=self.nonce,
                             session=self.dummy_session)

        good_skey = "uZnhYaRtzA7QdnDN1hVSWw=="
        good_ekey = "fAlG9eGL44ew6q8uTMMKJw=="

        self.assertEqual(good_ekey, tick.b64_ekey)
        self.assertEqual(good_skey, tick.b64_skey)
        self.assertEqual(tick.b64_skey, base64.b64encode(tick.skey))
        self.assertEqual(tick.b64_ekey, base64.b64encode(tick.ekey))

    def test_bad_signature_throws(self):
        bad_signature = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        bad_session = utils.DummyTicketResponse(bad_signature,
                                                self.tick_metadata,
                                                self.tick_ticket)
        self.assertRaises(ValueError,
                          ticket.Ticket,
                          self.srckey,
                          self.dstkey.name,
                          session=bad_session)

    def test_encryption_roundtrip(self):
        tick = ticket.Ticket(self.srckey,
                             self.dstkey.name,
                             timestamp=self.stamp,
                             nonce=self.nonce,
                             session=self.dummy_session)
        message = "MESSAGE"

        enc, sig = tick.encrypt(message, b64encode=True)
        tick_esek = esek.Esek(self.srckey.key_name,
                              self.dstkey,
                              tick.b64_esek)

        new_message = tick_esek.decrypt(enc, sig, b64decode=True)
        self.assertEqual(message,new_message)