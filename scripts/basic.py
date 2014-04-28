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

import logging

from keystoneclient.auth import token_endpoint
from keystoneclient import session

from kiteclient import v1

logging.basicConfig(level=logging.DEBUG)

message = 'MESSAGE'

auth = token_endpoint.Token('http://localhost:9109/v1', 'aToken')
s = session.Session(auth=auth)

srckey = v1.Key.generate('testkey', session=s)
print("source", srckey)

dstkey = v1.Key.generate('destkey', session=s)
print("dest", dstkey)

tick = v1.Ticket(srckey, dstkey.name, session=s)
print("ticket", tick)

enc, sig = tick.encrypt(message, b64encode=True)

esek = v1.Esek(srckey.key_name, dstkey, tick.b64_esek)
new_message = esek.decrypt(enc, sig, b64decode=True)

assert message == new_message

print(new_message)
