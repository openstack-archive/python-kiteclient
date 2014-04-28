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

from kiteclient.common import utils


class Resource(object):

    base_path = None

    @classmethod
    def _http_request(cls, session, method, path=None, **kwargs):
        headers = kwargs.setdefault('headers', {})
        headers['Accept'] = 'application/json'

        endpoint_filter = kwargs.setdefault('endpoint_filter', {})
        endpoint_filter.setdefault('service_type', 'kds')

        if path:
            path = utils.urljoin(cls.base_path, path)
        else:
            path = cls.base_path

        return session.request(path, method, **kwargs)

    @classmethod
    def _http_get(cls, session, *args, **kwargs):
        return cls._http_request(session, 'GET', *args, **kwargs)

    @classmethod
    def _http_post(cls, session, *args, **kwargs):
        return cls._http_request(session, 'POST', *args, **kwargs)

    @classmethod
    def _http_put(cls, session, *args, **kwargs):
        return cls._http_request(session, 'PUT', *args, **kwargs)

    @classmethod
    def _http_patch(cls, session, *args, **kwargs):
        return cls._http_request(session, 'PATCH', *args, **kwargs)

    @classmethod
    def _http_delete(cls, session, *args, **kwargs):
        return cls._http_request(session, 'DELETE', *args, **kwargs)

    @classmethod
    def _http_head(cls, session, *args, **kwargs):
        return cls._http_request(session, 'HEAD', *args, **kwargs)
