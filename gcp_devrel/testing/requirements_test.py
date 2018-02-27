# Copyright 2018 Google Inc.
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
Unit test for requirements.py
"""

from packaging.requirements import Requirement
import pytest

from gcp_devrel.tools import requirements


@pytest.mark.parametrize("test_input,expected", [
    ("foo", False),
    ("foo<2.0", True),
    ("foo==2.0", True),
    ("foo<2.0,>1.0", True),
])
def test__is_pinned(test_input, expected):
    req = Requirement(test_input)
    assert requirements._is_pinned(req) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("foo<2.0", True),
    ("foo==2.0", False),
    ("foo<2.0,>1.0", True),
])
def test__is_version_range(test_input, expected):
    req = Requirement(test_input)
    assert requirements._is_version_range(req) == expected
