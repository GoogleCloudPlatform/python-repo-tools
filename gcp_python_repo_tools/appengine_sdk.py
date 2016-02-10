# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Fetches the most recent GAE SDK and extracts it to the given directory."""

import os
import re
from StringIO import StringIO
import zipfile

import requests


SDK_RELEASES_URL = (
    'https://www.googleapis.com/storage/v1/b/appengine-sdks/o?prefix=featured')
PYTHON_RELEASE_RE = re.compile(
    r'featured/google_appengine_(\d+?)\.(\d+?)\.(\d+?)\.zip')


def get_gae_versions():
    """Gets a list of all of the available Python SDK versions, sorted with
    the newest last."""
    r = requests.get(SDK_RELEASES_URL)
    r.raise_for_status()

    releases = r.json().get('items', {})

    # We only care about the Python releases, which all are in the format
    # "featured/google_appengine_{version}.zip". We'll extract the version
    # number so we can sort the list by version, and finally get the download
    # URL.
    versions_and_urls = []
    for release in releases:
        match = PYTHON_RELEASE_RE.match(release['name'])

        if not match:
            continue

        versions_and_urls.append(
            (match.groups(), release['mediaLink']))

    return sorted(versions_and_urls, key=lambda x: x[0])


def download_sdk(url):
    """Downloads the SDK and returns a file-like object for the zip content."""
    r = requests.get(url)
    r.raise_for_status()
    return StringIO(r.content)


def extract_zip(zip, destination):
    zip_contents = zipfile.ZipFile(zip)

    if not os.path.exists(destination):
        os.makedirs(destination)

    zip_contents.extractall(destination)


def download_command(args):
    """Downloads and extracts the latest App Engine SDK to the given
    destination."""
    if os.path.exists(os.path.join(args.destination, 'google_appengine')):
        print('App Engine SDK already exists at {}.'.format(
            args.destination))
        return

    latest_version = get_gae_versions().pop()

    print('Downloading App Engine SDK {}'.format('.'.join(latest_version[0])))

    zip = download_sdk(latest_version[1])

    print('Extracting SDK to {}'.format(args.destination))

    extract_zip(zip, args.destination)

    print('App Engine SDK installed.')


def register_commands(subparsers):
    download = subparsers.add_parser(
        'download-appengine-sdk',
        help=download_command.__doc__)
    download.set_defaults(func=download_command)
    download.add_argument(
        'destination',
        help='Path to install the App Engine SDK')
