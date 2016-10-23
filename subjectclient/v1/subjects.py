# Copyright 2010 Jacob Kaplan-Moss

# Copyright 2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Server interface.
"""

import base64

from oslo_utils import encodeutils
import six
import six.moves.urllib.parse as urlparse

from subjectclient import api_versions
from subjectclient import base
from subjectclient import crypto
from subjectclient import exceptions as exc
from subjectclient.i18n import _
from subjectclient import utils


UPDATE_PARAMS = ('name', 'subject_format', 'tar_format', 'type',
                 'contributor', 'owner', 'size', 'is_public', 'protected',
                 'location', 'checksum', 'phase', 'language', 'properties',
                 'score', 'knowledge', 'belong',
                 # NOTE(bcwaldon: an attempt to update 'deleted' will be
                 # ignored, but we need to support it for backwards-
                 # compatibility with the legacy client library
                 'deleted')

CREATE_PARAMS = UPDATE_PARAMS + ("id", "id")

DEFAULT_PAGE_SIZE = 20

SORT_DIR_VALUES = ('asc', 'desc')
SORT_KEY_VALUES = ('name', 'status', 'subject_format', 'tar_format',
                   'size', 'id', 'created_at', 'updated_at')

OS_REQ_ID_HDR = 'x-ojj-request-id'


class Subject(base.Resource):
    def __repr__(self):
        return "<Subject %s>" % self._info

    def update(self, **fields):
        self.manager.update(self, **fields)

    def delete(self, **kwargs):
        return self.manager.delete(self)

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class SubjectManager(base.BootingManagerWithFind):
    resource_class = Subject

    def list(self, **kwargs):
        """Retrieve a listing of Subject objects.

        :param page_size: Number of images to request in each
                          paginated request.
        :returns: generator over list of Images.
        """

        limit = kwargs.get('limit')
        # NOTE(flaper87): Don't use `get('page_size', DEFAULT_SIZE)` otherwise,
        # it could be possible to send invalid data to the server by passing
        # page_size=None.
        page_size = kwargs.get('page_size') or DEFAULT_PAGE_SIZE

        def paginate(url, page_size, limit=None):
            next_url = url

            while True:
                if limit and page_size > limit:
                    # NOTE(flaper87): Avoid requesting 2000 images when limit
                    # is 1
                    next_url = next_url.replace("limit=%s" % page_size,
                                                "limit=%s" % limit)

                temp_subjects = self._list(next_url, "subjects")
                for subject in temp_subjects:
                    yield subject
                    if limit:
                        limit -= 1
                        if limit <= 0:
                            raise StopIteration

        filters = kwargs.get('filters', {})
        # NOTE(flaper87): We paginate in the client, hence we use
        # the page_size as Glance's limit.
        filters['limit'] = page_size

        tags = filters.pop('tag', [])
        tags_url_params = []

        for tag in tags:
            if not isinstance(tag, six.string_types):
                raise exc.BadRequest("Invalid tag value %s" % tag)

            tags_url_params.append({'tag': encodeutils.safe_encode(tag)})

        for param, value in six.iteritems(filters):
            if isinstance(value, six.string_types):
                filters[param] = encodeutils.safe_encode(value)

        url = '/v1/images?%s' % urlparse.urlencode(filters)

        for param in tags_url_params:
            url = '%s&%s' % (url, urlparse.urlencode(param))

        if 'sort' in kwargs:
            if 'sort_key' in kwargs or 'sort_dir' in kwargs:
                raise exc.BadRequest("The 'sort' argument is not supported"
                                         " with 'sort_key' or 'sort_dir'.")
            url = '%s&sort=%s' % (url,
                                  self._validate_sort_param(
                                      kwargs['sort']))
        else:
            sort_dir = self._wrap(kwargs.get('sort_dir', []))
            sort_key = self._wrap(kwargs.get('sort_key', []))

            if len(sort_key) != len(sort_dir) and len(sort_dir) > 1:
                raise exc.BadRequest(
                    "Unexpected number of sort directions: "
                    "either provide a single sort direction or an equal "
                    "number of sort keys and sort directions.")
            for key in sort_key:
                url = '%s&sort_key=%s' % (url, key)

            for dir in sort_dir:
                url = '%s&sort_dir=%s' % (url, dir)

        if isinstance(kwargs.get('marker'), six.string_types):
            url = '%s&marker=%s' % (url, kwargs['marker'])

        for image in paginate(url, page_size, limit):
            yield image

    def delete(self, subject_id):
        """Delete an image."""
        url = '/v1/subjects/%s' % subject_id
        self._delete(url)

    def create(self, **kwargs):
        """Create an image."""
        resource_url = '/v1/subjects'

        image_data = kwargs.pop('data', None)
        if image_data is not None:
            image_size = utils.get_file_size(image_data)
            if image_size is not None:
                kwargs.setdefault('size', image_size)

        body = {}

        fields = {}
        for field in kwargs:
            if field in CREATE_PARAMS:
                fields[field] = kwargs[field]
            elif field == 'return_req_id':
                continue
            else:
                continue

        body['subject'] = fields

        return self._create(resource_url, body, "subject", **kwargs)

    def upload(self, subject_id, subject_data, subject_size=None):
        """Upload the data for an subject.

        :param subject_id: ID of the image to upload data for.
        :param subject_data: File-like object supplying the data to upload.
        :param subject_size: Unused - present for backwards compatibility
        """
        url = '/v1/images/%s/file' % subject_id
        hdrs = {'Content-Type': 'application/octet-stream'}
        body = subject_data
        self.api.client.put(url, headers=hdrs, body=body)
