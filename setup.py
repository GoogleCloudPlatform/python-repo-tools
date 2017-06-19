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

import io

from setuptools import find_packages, setup


with io.open('README.rst', 'r') as fh:
    long_description = fh.read()

setup(
    name='gcp-devrel-py-tools',

    version='0.0.8',

    description='Tools for Cloud Platform Python libraries and samples.',
    long_description=long_description,
    url='https://github.com/GoogleCloudPlatform/python-repo-tools',

    author='Jon Wayne Parrott',
    author_email='jonwayne@google.com',

    license='Apache Software License',

    classifiers=[
        'Operating System :: POSIX',
    ],

    packages=find_packages(),

    install_requires=[
        'requests', 'retrying', 'setuptools>=25.0.0', 'packaging'],

    entry_points={
        'console_scripts': [
            'gcp-devrel-py-tools=gcp_devrel.tools:main',
        ],
    },
)
