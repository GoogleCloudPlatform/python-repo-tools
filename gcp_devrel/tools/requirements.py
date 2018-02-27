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

from packaging.requirements import Requirement
from packaging.specifiers import Specifier
import packaging.version
from pip.req.req_file import parse_requirements
import requests


def get_package_info(package):
    """Gets the PyPI information for a given package."""
    url = 'https://pypi.python.org/pypi/{}/json'.format(package)
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


def read_requirements(req_file):
    """Reads a requirements file.

    Args:
        req_file (str): Filename of requirements file
    """
    items = list(parse_requirements(req_file, session={}))
    result = []

    for item in items:
        # Get line number from item
        line_number = item.comes_from.split(req_file + ' (line ')[1][:-1]
        if item.req:
            item.req.marker = item.markers
            result.append((item.req, line_number))
        else:
            result.append((item, line_number))

    return result


def _get_newest_version(info):
    versions = info['releases'].keys()
    versions = [packaging.version.parse(version) for version in versions]
    versions = [version for version in versions if not version.is_prerelease]
    latest = sorted(versions).pop()
    return latest


def _is_pinned(req):
    """Returns true if requirements have some version specifiers."""
    return (req.specifier is not None) and len(req.specifier) > 0


def _is_version_range(req):
    """Returns true if requirements specify a version range."""

    assert len(req.specifier) > 0
    specs = list(req.specifier)
    if len(specs) == 1:
        # "foo > 2.0" or "foo == 2.4.3"
        return specs[0].operator != '=='
    else:
        # "foo > 2.0, < 3.0"
        return True


def update_req(req):
    """Updates a given req object with the latest version."""

    if not req.name:
        return req, None

    info = get_package_info(req.name)

    if info['info'].get('_pypi_hidden'):
        print('{} is hidden on PyPI and will not be updated.'.format(req))
        return req, None

    if _is_pinned(req) and _is_version_range(req):
        print('{} is pinned to a range and will not be updated.'.format(req))
        return req, None

    newest_version = _get_newest_version(info)
    current_spec = next(iter(req.specifier)) if req.specifier else None
    current_version = current_spec.version if current_spec else None
    new_spec = Specifier(u'=={}'.format(newest_version))
    if not current_spec or current_spec._spec != new_spec._spec:
        req.specifier = new_spec
        update_info = (
            req.name,
            current_version,
            newest_version)
        return req, update_info
    return req, None


def write_requirements(reqs_linenum, req_file):
    """Writes a list of req objects out to a given file."""
    with open(req_file, 'r') as input:
        lines = input.readlines()

    for req in reqs_linenum:
        line_num = int(req[1])

        if hasattr(req[0], 'link'):
            lines[line_num - 1] = '{}\n'.format(req[0].link)
        else:
            lines[line_num - 1] = '{}\n'.format(req[0])

    with open(req_file, 'w') as output:
        output.writelines(lines)


def check_req(req):
    """Checks if a given req is the latest version available."""
    if not isinstance(req, Requirement):
        return None

    info = get_package_info(req.name)
    newest_version = _get_newest_version(info)

    if _is_pinned(req) and _is_version_range(req):
        return None

    current_spec = next(iter(req.specifier)) if req.specifier else None
    current_version = current_spec.version if current_spec else None
    if current_version != newest_version:
        return req.name, current_version, newest_version


def update_requirements_file(req_file, skip_packages):
    reqs = read_requirements(req_file)
    skipped = []
    if skip_packages is not None:
        skipped = [req for req in reqs if req[0].name in skip_packages]
        reqs = [req for req in reqs if req[0].name not in skip_packages]
    reqs_info_linenum = [update_req(req[0]) + (req[1],) for req in reqs]

    updated_reqs = [(x[0], x[2]) for x in reqs_info_linenum]
    write_requirements(updated_reqs + skipped, req_file)
    return [x[1] for x in reqs_info_linenum if x[1]]


def check_requirements_file(req_file, skip_packages):
    """Return list of outdated requirements.

    Args:
        req_file (str): Filename of requirements file
        skip_packages (list): List of package names to ignore.
    """
    reqs = read_requirements(req_file)
    if skip_packages is not None:
        reqs = [req for req in reqs if req.name not in skip_packages]
    outdated_reqs = filter(None, [check_req(req) for req in reqs])
    return outdated_reqs


def update_command(args):
    """Updates all dependencies the specified requirements file."""
    updated = update_requirements_file(
        args.requirements_file, args.skip_packages)

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
    outdated = check_requirements_file(args.requirements_file,
                                       args.skip_packages)

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
    update.add_argument(
        '--skip-packages', nargs='+',
        help="List of packages to ignore during the check")

    check = subparsers.add_parser(
        'check-requirements',
        help=check_command.__doc__)
    check.set_defaults(func=check_command)
    check.add_argument(
        'requirements_file',
        help='Path the the requirements.txt file to check.')
    check.add_argument(
        '--skip-packages', nargs='+',
        help="List of packages to ignore during the check"
    )
