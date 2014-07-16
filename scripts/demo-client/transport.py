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

from oslo.config import cfg
from oslo import messaging


class Transport(object):

    def __init__(self, target, url):
        self._transport = messaging.get_transport(cfg.CONF, url)
        self._target = messaging.Target(topic=target,
                                        server='server1',
                                        version='1.0')
        self.timeout = 2
        self.retry = True

    def send(self, msg, target):
        msg_ctxt = {}
        targ = messaging.Target(topic=target,
                                server='server1',
                                version='1.0')

        result = self._transport._send(targ, msg_ctxt, msg,
                                       wait_for_reply=True,
                                       timeout=self.timeout,
                                       )
        return result

    def recv(self):
        listener = self._transport._listen(self._target)
        message = listener.poll()
        message.reply(reply="OK")
        message.acknowledge()
        return message.message
