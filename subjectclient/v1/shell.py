# Copyright 2010 Jacob Kaplan-Moss

# Copyright 2011 OpenStack Foundation
# Copyright 2013 IBM Corp.
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

from __future__ import print_function

import argparse
import copy
import datetime
import functools
import getpass
import locale
import logging
import os
import sys
import time
import warnings

from oslo_utils import encodeutils
from oslo_utils import netutils
from oslo_utils import strutils
from oslo_utils import timeutils
from oslo_utils import uuidutils
import six

import subjectclient
from subjectclient import api_versions
from subjectclient import base
from subjectclient import client
from subjectclient import exceptions
from subjectclient.i18n import _
from subjectclient.i18n import _LE
from subjectclient import shell
from subjectclient import utils
from subjectclient.v1 import availability_zones
from subjectclient.v1 import quotas
from subjectclient.v1 import servers


logger = logging.getLogger(__name__)


def _key_value_pairing(text):
    try:
        (k, v) = text.split('=', 1)
        return (k, v)
    except ValueError:
        msg = _LE("'%s' is not in the format of 'key=value'") % text
        raise argparse.ArgumentTypeError(msg)


def _meta_parsing(metadata):
    return dict(v.split('=', 1) for v in metadata)


# Copyright 2012 OpenStack Foundation
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

import functools
import sys

from oslo_utils import strutils

from subjectclient._i18n import _
import os

DATA_FIELDS = ('location', 'copy_from', 'file')
TYPE_FORMATS = 'Acceptable formats: program, choice, judge.'
SUBJECT_FORMATS = 'Acceptable formats: src, template, subject, answer.'
TAR_FORMATS = ('Acceptable formats: rar, tar, tar.gz, zip.')
PHASE = ('Beginner, Intermediate, Advanced, Challenge')
LANGUAGE = ('C/C++, JAVA, Python, GO, JavaScript, Ruby, Lua')

_bool_strict = functools.partial(strutils.bool_from_string, strict=True)


@utils.arg('--id', metavar='<SUBJECT_ID>',
           help='ID of image to reserve.')
@utils.arg('--name', metavar='<NAME>',
           help='Name of image.')
@utils.arg('--belong', metavar='<subject_id>',
           help='be related to who.')
@utils.arg('--subject-format', metavar='<TAR_FORMAT>',
           help='Disk format of subject. ' + TAR_FORMATS)
@utils.arg('--tar-format', metavar='<TAR_FORMAT>',
           help='Disk format of subject. ' + TAR_FORMATS)
@utils.arg('--type', metavar='<type>',
           help='type of subject. ' + TYPE_FORMATS)
@utils.arg('--owner', metavar='<TENANT_ID>',
           help='Tenant who should own image.')
@utils.arg('--size', metavar='<SIZE>', type=int,
           help=('Size of image data (in bytes). Only used with'
                 ' \'--location\' and \'--copy_from\'.'))
@utils.arg('--location', metavar='<IMAGE_URL>',
           help=('URL where the data for this image already resides. For '
                 'example, if the image data is stored in swift, you could '
                 'specify \'swift+http://tenant%%3Aaccount:key@auth_url/'
                 'v1.0/container/obj\'. '
                 '(Note: \'%%3A\' is \':\' URL encoded.)'))
@utils.arg('--file', metavar='<FILE>',
           help=('Local file that contains subject to be uploaded during'
                 ' creation. Alternatively, subjects can be passed to the '
                 'client via stdin.'))
@utils.arg('--checksum', metavar='<CHECKSUM>',
           help=('Hash of image data used Glance can use for verification.'
                 ' Provide a md5 checksum here.'))
@utils.arg('--contributor', metavar='<contributor>',
           help=('the contributor of this subject.'))
@utils.arg('--phase', metavar='<phase>',
           help=('the phase of this subject.' + PHASE))
@utils.arg('--language', metavar='<language>',
           help=('the language of this subject.' + LANGUAGE))
@utils.arg('--score', metavar='<score>',
           help=('the score of this subject.'))
@utils.arg('--knowledge', metavar='<knowledge>',
           help=('the knowledge points of this subject.'))
@utils.arg('--is-public',
           type=_bool_strict, metavar='{True,False}',
           help='Make subject accessible to the public.')
@utils.arg('--is-protected',
           type=_bool_strict, metavar='{True,False}',
           help='Prevent subject from being deleted.')
@utils.arg('--property', metavar="<key=value>", action='append', default=[],
           help=("Arbitrary property to associate with image. "
                 "May be used multiple times."))
@utils.arg('--progress', action='store_true', default=False,
           help='Show upload progress bar.')
def do_subject_create(gc, args):
    """Create a new subject."""
    _args = [(x[0].replace('-', '_'), x[1]) for x in vars(args).items()]
    fields = dict(filter(lambda x: x[1] is not None,
                         _args))

    raw_properties = fields.pop('property', [])
    for datum in raw_properties:
        key, value = datum.split('=', 1)
        fields[key] = value

    file_name = fields.pop('file', None)
    if file_name is not None and os.access(file_name, os.R_OK) is False:
        utils.exit("File %s does not exist or user does not have read "
                   "privileges to it" % file_name)
    image = gc.subjects.create(**fields)
    try:
        if utils.get_data_file(args) is not None:
            args.id = image['id']
            args.size = None
            do_subject_upload(gc, args)
            image = gc.subjects.get(args.id)
    finally:
        utils.print_image(image)