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

from kiteclient import v1


class KiteClient(object):
    """KiteClient class.

    This acts as a client to the kite server and will register a key with
    kite upon creation. A transport class must be provided, message data
    will be read from the transport, decrypted and verified.

    To send a message, data will be encrypted and signed using a kite
    ticket then passed onto the transport. A message is formed thus:

    {
    "sender" : sender key name,
    "body" : encrypted data, base64 encoded,
    "signature" : message signature, base64 encoded,
    "esec" : message esek data
    }
    """

    def __init__(self, name, transport, key=None, session=None,
                 verbose=False):
        self._session = session
        self._transport = transport
        self.verbose = verbose

        if key is None:
            self._key = v1.Key.generate(name, self._session)
        else:
            self._key = v1.Key(name, key, self._session)

    def _get_ticket(self, target):
        ticket = v1.Ticket(self._key, target, session=self._session)
        return ticket

    def send(self, data, target):
        """Create and send a trusted message.

        :param data: the message body
        :param target: the recipient name
        """
        ticket = self._get_ticket(target)
        enc, sig = ticket.encrypt(data)
        message = {
            "sender": self._key.key_name,
            "body": enc,
            "signature": sig,
            "esek": ticket.b64_esek
            }

        if self.verbose:
            print("Sent: %s" % message)

        resp = self._transport.send(message, target)
        return resp

    def recv(self):
        """Receive, verify and decrypt a secure message

        :param data: the secure message data
        """
        message = self._transport.recv()

        if self.verbose:
            print("Received: %s" % message)

        esek = v1.Esek(message["sender"], self._key, message["esek"])
        body = esek.decrypt(message["body"],
                            message["signature"],
                            b64decode=True)
        return body