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

auth = token_endpoint.Token('http://localhost:9109/v1', 'aToken')
s = session.Session(auth=auth)

group = v1.group.Group('testgroup', session=s)
keyA = v1.Key.generate('testgroup.testkeyA', session=s)
keyB = v1.Key.generate('testgroup.testkeyB', session=s)

tickA = v1.group.GroupKey(keyA, "testgroup", session=s)
tickB = group.getKey(keyB, session=s)

print("-----------------------------------------------------------------")
print(keyA)
print("gkey A", tickA)
print("-----------------------------------------------------------------")
print(keyB)
print("gkey B", tickB)
print("-----------------------------------------------------------------")
