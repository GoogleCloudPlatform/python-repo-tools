# Copyright 2015, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tools for dealing with flaky tests.
"""
from __future__ import absolute_import

import functools

try:
    from google.cloud.exceptions import GoogleCloudError
except ImportError:
    class GoogleCloudError(Exception):
        pass

from flaky import flaky as _flaky
import pytest


def client_library_errors(e, *args):
    """Used by mark_flaky to retry on remote service errors."""
    exception_class, exception_instance, traceback = e

    return isinstance(
        exception_instance,
        (GoogleCloudError,))


def flaky(f=None, max_runs=5, filter=None):
    """Makes a test retry on remote service errors."""
    if not f:
        return functools.partial(flaky, max_runs=max_runs, filter=filter)

    return _flaky(max_runs=3, rerun_filter=filter)(
        pytest.mark.flaky(pytest.mark.slow(f)))
