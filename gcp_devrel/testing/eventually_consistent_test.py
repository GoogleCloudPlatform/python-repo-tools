# Copyright 2018 Google LLC
#
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

import pytest

from gcp_devrel.testing import eventually_consistent

test_mark_simple_tries = 0
test_mark_args_tries = 0
test_mark_custom_exception_tries = 0
test_mark_custom_exception_with_tuple_tries = 0


class MyException(Exception):
    pass


@eventually_consistent.mark
def test_mark_simple():
    global test_mark_simple_tries
    test_mark_simple_tries += 1
    if test_mark_simple_tries == 2:
        assert True
    else:
        assert False


@eventually_consistent.mark(tries=2)
def test_mark_args():
    global test_mark_args_tries
    test_mark_args_tries += 1
    if test_mark_args_tries == 2:
        assert True
    else:
        assert False


@eventually_consistent.mark(tries=2, exceptions=MyException)
def test_mark_custom_exception():
    global test_mark_custom_exception_tries
    test_mark_custom_exception_tries += 1
    if test_mark_custom_exception_tries == 2:
        assert True
    else:
        raise MyException


@eventually_consistent.mark(tries=3, exceptions=(MyException, AssertionError))
def test_mark_custom_exceptions_with_tuple():
    global test_mark_custom_exception_with_tuple_tries
    test_mark_custom_exception_with_tuple_tries += 1
    if test_mark_custom_exception_with_tuple_tries == 3:
        assert True
    elif test_mark_custom_exception_with_tuple_tries == 2:
        raise MyException
    else:
        assert False


def test_call_simple():
    tried = 0
    @eventually_consistent.call
    def _():
        nonlocal tried
        tried += 1
        if tried == 2:
            assert True
        else:
            assert False


def test_call_args():
    tried = 0

    @eventually_consistent.call(tries=2)
    def _():
        nonlocal tried
        tried += 1
        if tried == 2:
            assert True
        else:
            assert False


def test_call_args_fail():
    with pytest.raises(AssertionError):
        tried = 0

        @eventually_consistent.call(tries=2)
        def _():
            nonlocal tried
            tried += 1
            if tried == 3:
                assert True
            else:
                assert False


def test_call_custom_exception():
    tried = 0

    @eventually_consistent.call(tries=2, exceptions=MyException)
    def _():
        nonlocal tried
        tried += 1
        if tried == 2:
            assert True
        else:
            raise MyException


def test_call_custom_exception_with_tuple():
    tried = 0

    @eventually_consistent.call(
        tries=3, exceptions=(MyException, AssertionError))
    def _():
        nonlocal tried
        tried += 1
        if tried == 3:
            assert True
        elif tried == 2:
            assert False
        else:
            raise MyException
