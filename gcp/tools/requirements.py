# Copyright 2016 Google Inc.
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

"""
Checks and updates dependencies to ensure they are the latest version.
"""
import sys

from pip.req.req_file import parse_requirements
from pkg_resources import Requirement
import requests


def get_package_info(package):
    """Gets the PyPI information for a given package."""
    url = 'https://pypi.python.org/pypi/{}/json'.format(package)
    r = requests.get(url)
    r.raise_for_status()
    return r.json()['info']


def read_requirements(req_file):
    """Reads a requirements file."""
    return [x.req for x in parse_requirements(req_file, session={})]


def update_req(req):
    """Updates a given req object with the latest version."""
    info = get_package_info(req.project_name)
    newest_version = info['version']
    current_spec = req.specs[0] if req.specs else ('==', 'unspecified')
    new_spec = ('==', newest_version)
    if current_spec != new_spec:
        req.specs = new_spec
        update_info = (req.project_name, current_spec[1], newest_version)
        return req, update_info
    return req, None


def write_requirements(reqs, req_file):
    """Writes a list of req objects out to a given file."""
    with open(req_file, 'w') as f:
        for req in reqs:
            f.write('{}\n'.format(req))


def check_req(req):
    """Checks if a given req is the latest version available."""
    info = get_package_info(req.project_name)
    newest_version = info['version']
    current_spec = req.specs[0] if req.specs else ('==', 'unspecified')
    if current_spec[1] != newest_version:
        return req.project_name, current_spec[1], newest_version


def update_requirements_file(req_file):
    reqs = read_requirements(req_file)
    reqs_and_info = [update_req(req) for req in reqs]
    write_requirements([x[0] for x in reqs_and_info], req_file)
    return [x[1] for x in reqs_and_info if x[1]]


def check_requirements_file(req_file):
    reqs = read_requirements(req_file)
    outdated_reqs = filter(None, [check_req(req) for req in reqs])
    return outdated_reqs


def update_command(args):
    """Updates all dependencies the specified requirements file."""
    updated = update_requirements_file(args.requirements_file)

    if updated:
        print('Updated requirements in {}:'.format(args.requirements_file))

        for item in updated:
            print(' * {} from {} to {}.'.format(*item))
    else:
        print('All dependencies in {} are up-to-date.'.format(
            args.requirements_file))


def check_command(args):
    """Checks that all dependencies in the specified requirements file are
    up to date."""
    outdated = check_requirements_file(args.requirements_file)

    if outdated:
        print('Requirements in {} are out of date:'.format(
            args.requirements_file))

        for item in outdated:
            print(' * {} is {} latest is {}.'.format(*item))

        sys.exit(1)
    else:
        print('Requirements in {} are up to date.'.format(
            args.requirements_file))


def register_commands(subparsers):
    update = subparsers.add_parser(
        'update-requirements',
        help=update_command.__doc__)
    update.set_defaults(func=update_command)
    update.add_argument(
        'requirements_file',
        help='Path the the requirements.txt file to update.')

    update = subparsers.add_parser(
        'check-requirements',
        help=check_command.__doc__)
    update.set_defaults(func=check_command)
    update.add_argument(
        'requirements_file',
        help='Path the the requirements.txt file to check.')
