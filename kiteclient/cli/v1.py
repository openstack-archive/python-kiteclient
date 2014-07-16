# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"KDS Client"

import logging
import os

from cliff import command
from cliff import show
from keystoneclient.auth.identity import v2 as v2_auth
from keystoneclient.auth import token_endpoint
from keystoneclient import session
from openstackclient.common import utils

from kiteclient import v1

LOG = logging.getLogger(__name__)

DEFAULT_KDS_API_VERSION = '1'
API_VERSION_OPTION = 'os_kds_api_version'
API_NAME = 'kds'
API_VERSIONS = {
    '1': 'kiteclient.cli.v1.Client'
}


def make_client(instance):
    client_class = utils.get_client_class(API_NAME,
                                          instance._api_version[API_NAME],
                                          API_VERSIONS)
    LOG.debug('instantiating KDS client: %s' % client_class)

    s = session.Session.construct({'verify': instance._verify,
                                   'cacert': instance._cacert,
                                   'insecure': instance._insecure})

    if instance._url:
        s.auth = token_endpoint.Token(instance._url, instance._token)
    else:
        s.auth = v2_auth.Password(instance._auth_url,
                                  instance._username,
                                  instance._password,
                                  tenant_id=instance._project_id,
                                  tenant_name=instance._project_name)

    return client_class(s)


def build_option_parser(parser):
    parser.add_argument(
        '--os-kds-api-version',
        metavar='<kds-api-version>',
        default=os.getenv('OS_KDS_API_VERSION', DEFAULT_KDS_API_VERSION),
        help='KDS API version, default=%s (Env: OS_KDS_API_VERSION)' %
             DEFAULT_KDS_API_VERSION)
    return parser


class Client(object):

    log = logging.getLogger(__name__ + '.Client')

    def __init__(self, sess):
        self.session = sess

    def set_key(self, name, key_data):
        if key_data:
            key = v1.Key(name, key_data, self.session)
        else:
            key = v1.Key.generate(name, self.session)

        return key.key_name, key.generation, key.b64_key

    def create_group(self, name):
        # TODO(tkelsey): implement this when KDS group work is done.
        self.log.warn("create_group not implemented")
        raise NotImplementedError

    def delete_group(self, name):
        # TODO(tkelsey): implement this when KDS group work is done.
        self.log.warn("delete_group not implemented")
        raise NotImplementedError


class KeySet(show.ShowOne):
    """Set a messaging symmetric key in the KDS."""

    log = logging.getLogger(__name__ + '.KeySet')
    columns = ('Name', 'Generation', 'Key')

    def get_parser(self, prog_name):
        parser = super(KeySet, self).get_parser(prog_name)
        parser.add_argument('name',
                            metavar='<name>',
                            help='Name of host')
        parser.add_argument('key',
                            nargs='?',
                            metavar='<key>',
                            help='Base64 key to set')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        kds_client = self.app.client_manager.kds
        data = kds_client.set_key(parsed_args.name, parsed_args.key)

        return self.columns, data


class GroupCreate(show.ShowOne):
    """Create a Group in the KDS."""

    log = logging.getLogger(__name__ + '.GroupCreate')
    columns = ('Name',)

    def get_parser(self, prog_name):
        parser = super(GroupCreate, self).get_parser(prog_name)
        parser.add_argument('name',
                            metavar='<name>',
                            help='Name of the Group to create')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        kds_client = self.app.client_manager.kds
        data = kds_client.create_group(parsed_args.name)

        return self.columns, (data, )


class GroupDelete(command.Command):
    """Delete a Group from the KDS."""

    log = logging.getLogger(__name__ + '.GroupDelete')

    def get_parser(self, prog_name):
        parser = super(GroupDelete, self).get_parser(prog_name)
        parser.add_argument('name',
                            metavar='<name>',
                            help='Name of the Group to delete')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        kds_client = self.app.client_manager.kds
        kds_client.delete_group(parsed_args.name)