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

from openstack.common import gettextutils as u
from oslo.config import cfg
from oslo import messaging


def register_transport_configs(conf, cli=False):
    transport_group = cfg.OptGroup(name='transport',
                                   title="Message Transport")
    transport_opts = [
        cfg.StrOpt('url', help=u._('Message queue url.'),
                   default="rabbit://localhost"),
    ]

    conf.register_group(transport_group)
    if cli:
        conf.register_cli_opts(transport_opts, group=transport_group)
    else:
        conf.register_opts(transport_opts, group=transport_group)


class Transport(object):

    def __init__(self, target, conf=cfg.CONF):
        self._transport = messaging.get_transport(conf, conf.transport.url)
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
