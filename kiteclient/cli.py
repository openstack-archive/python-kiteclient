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

from __future__ import print_function

import client
from keystoneclient.auth import token_endpoint
from keystoneclient import session
from openstack.common import gettextutils as u
from openstack.common import log as logging
from oslo.config import cfg
import transport

import sys

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def main():
    client.register_kiteclient_configs(CONF, cli=True)
    transport.register_transport_configs(CONF, cli=True)

    CONF.register_cli_opt(
        cfg.BoolOpt('listen', short="l",
                    help=u._('Listen for incoming messages.'),
                    default=False))

    CONF.register_cli_opt(
        cfg.StrOpt('target', short="t",
                   help=u._('Target to send messages to.')))

    CONF.register_cli_opt(
        cfg.StrOpt('message', short="m",
                   help=u._('Message to send.')))

    CONF(sys.argv[1:])

    if not CONF.kiteclient.name:
        print("--kiteclient-name is required.")
        return -1

    # TODO(tkelsey): use keystone properly.
    name = CONF.kiteclient.name
    host = CONF.kiteclient.kite_host
    port = CONF.kiteclient.kite_port
    kite = "http://%s:%s/v1" % (host, port)
    auth = token_endpoint.Token(kite, 'aToken')

    transport_obj = transport.Transport(target=name)
    session_obj = session.Session(auth=auth)
    client_obj = client.KiteClient(transport_obj, conf=CONF,
                                   session=session_obj)

    if CONF.listen:
        message = client_obj.recv()
        print(message)

    else:
        if not CONF.target or not CONF.message:
            print("Message body and target are required.")
            return -1

        else:
            targ = CONF.target
            body = CONF.message
            resp = client_obj.send(body, targ)
            print(resp)