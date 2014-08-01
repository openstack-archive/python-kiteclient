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
import transport

from kiteclient.openstack.common import gettextutils as u

import optparse


def main():
    usage = "usage: %prog [options] name [-l | target message]"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-v", "--verbose", dest="verbose",
                      help=u._("Be verbose."), action="store_true",
                      default=False)

    parser.add_option('--kite_host',
                      help=u._('Kite server host address.'),
                      default="localhost"),

    parser.add_option('--kite_port',
                      help=u._('Kite server port number.'),
                      default="9109"),

    parser.add_option('--key', "-k",
                      help=u._('Optional base64 encoded key.')),

    parser.add_option('--queue', "-q",
                      help=u._('Message queue url.'),
                      default="rabbit://localhost"),

    parser.add_option('--listen', "-l",
                      help=u._('Listen for incoming messages.'),
                      action="store_true", default=False),

    (options, args) = parser.parse_args()

    if not args:
        parser.print_usage()
        return -1

    # NOTE(tkelsey): using developer interface to remove the need to run
    # a keystone server.
    name = args[0]
    host = options.kite_host
    port = options.kite_port
    kite = "http://%s:%s/v1" % (host, port)
    auth = token_endpoint.Token(kite, 'aToken')

    transport_obj = transport.Transport(target=name, url=options.queue)
    session_obj = session.Session(auth=auth)
    client_obj = client.KiteClient(name, transport_obj,
                                   key=options.key,
                                   session=session_obj,
                                   verbose=options.verbose)

    if options.listen:
        try:
            message = client_obj.recv()
            print(message)
        except KeyboardInterrupt:
            pass

    else:
        if len(args) < 3:
            print("target and message are required when not listening")
            parser.print_usage()
            return -1

        else:
            targ = args[1]
            body = args[2]
            resp = client_obj.send(body, targ)
            print(resp)

if __name__ == "__main__":
    main()