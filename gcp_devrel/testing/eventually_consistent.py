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
Tools for dealing with eventually consistent tests.
"""

from google.cloud import exceptions
from retrying import retry

WAIT_EXPONENTIAL_MULTIPLIER_DEFAULT = 1000
WAIT_EXPONENTIAL_MAX_DEFAULT = 30000
STOP_MAX_ATTEMPT_NUMBER_DEFAULT = 10


def _retry_on_exception(exception_class):
    def inner(e):
        if isinstance(e, exception_class):
            print('Retrying due to eventual consistency.')
            return True
        return False
    return inner


def mark(*args, **kwargs):
    """Marks an entire test as eventually consistent and retries.

    Args:
        tries: The number of retries.
        exceptions: The exceptions on which it will retry. It can be
            single value or a tuple.
        wait_exponential_multiplier: The exponential multiplier in
            milliseconds.
        wait_exponential_max: The maximum wait before the next try in
            milliseconds.
    """
    __tracebackhide__ = True
    tries = kwargs.get('tries', STOP_MAX_ATTEMPT_NUMBER_DEFAULT)
    retry_exceptions = kwargs.get(
        'exceptions', (AssertionError, exceptions.GoogleCloudError))
    wait_exponential_multiplier = kwargs.get(
        'wait_exponential_multiplier', WAIT_EXPONENTIAL_MULTIPLIER_DEFAULT)
    wait_exponential_max = kwargs.get(
        'wait_exponential_max', WAIT_EXPONENTIAL_MAX_DEFAULT)
    # support both `@mark` and `@mark()` syntax
    if len(args) == 1 and callable(args[0]):
        return retry(
            wait_exponential_multiplier=wait_exponential_multiplier,
            wait_exponential_max=wait_exponential_max,
            stop_max_attempt_number=tries,
            retry_on_exception=_retry_on_exception(retry_exceptions))(args[0])

    # `mark()` syntax
    def inner(f):
        __tracebackhide__ = True
        return retry(
            wait_exponential_multiplier=wait_exponential_multiplier,
            wait_exponential_max=wait_exponential_max,
            stop_max_attempt_number=tries,
            retry_on_exception=_retry_on_exception(retry_exceptions))(f)
    return inner


def call(*args, **kwargs):
    """Call a given function and treat it as eventually consistent.

    The function will be called immediately and retried with exponential
    backoff up to the listed amount of times.

    By default, it only retries on AssertionErrors, but can be told to retry
    on other errors.

    Args:
        tries: The number of retries.
        exceptions: The exceptions on which it will retry. It can be
            single value or a tuple.
        wait_exponential_multiplier: The exponential multiplier in
            milliseconds.
        wait_exponential_max: The maximum wait before the next try in
            milliseconds.

    Examples:

        @eventually_consistent.call
        def _():
            results = client.query().fetch(10)
            assert len(results) == 10

        @eventually_consistent.call(tries=2)
        def _():
            results = client.query().fetch(10)
            assert len(results) == 10

        @eventually_consistent.call(tries=2, exceptions=SomeException)
        def _():
            # It might throw SomeException
            results = client.query().fetch(10)

    """
    __tracebackhide__ = True
    tries = kwargs.get('tries', STOP_MAX_ATTEMPT_NUMBER_DEFAULT)
    retry_exceptions = kwargs.get('exceptions', AssertionError)
    wait_exponential_multiplier = kwargs.get(
        'wait_exponential_multiplier', WAIT_EXPONENTIAL_MULTIPLIER_DEFAULT)
    wait_exponential_max = kwargs.get(
        'wait_exponential_max', WAIT_EXPONENTIAL_MAX_DEFAULT)

    # support both `@call` and `@call()` syntax
    if len(args) == 1 and callable(args[0]):
        return retry(
            wait_exponential_multiplier=wait_exponential_multiplier,
            wait_exponential_max=wait_exponential_max,
            stop_max_attempt_number=tries,
            retry_on_exception=_retry_on_exception(
                retry_exceptions))(args[0])()

    # `@call()` syntax
    def inner(f):
        __tracebackhide__ = True
        return retry(
            wait_exponential_multiplier=wait_exponential_multiplier,
            wait_exponential_max=wait_exponential_max,
            stop_max_attempt_number=tries,
            retry_on_exception=_retry_on_exception(retry_exceptions))(f)()
    return inner
