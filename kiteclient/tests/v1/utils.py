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


class DummyKeyResponse(object):

    def __init__(self, gen=1):
        self.generation = gen
        self.name = ""

    def request(self, path, method, **kwargs):
        self.name = path.split('/')[-1]
        return self

    def json(self):
        return {"generation": self.generation,
                "name": self.name}


class DummyTicketResponse(object):

    def __init__(self, signature, metadata, ticket):
        self.signature = signature
        self.metadata = metadata
        self.ticket = ticket

    def request(self, path, method, **kwargs):
        return self

    def json(self):
        return {"signature": self.signature,
                "metadata": self.metadata,
                "ticket" : self.ticket}