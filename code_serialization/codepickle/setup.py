#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


# Function to parse __version__ in `cloudpickle/__init__.py`
def find_version():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'codepickle', '__init__.py'), 'r') as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


dist = setup(
    name='codepickle',
    version=find_version(),
    description='Pickling code object as a source code for portability (cloudpickle as base)',
    author='bankde',
    license='BSD 3-Clause License',
    packages=['codepickle'],
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Distributed Computing',
    ],
    test_suite='tests',
    python_requires='>=3.6',
)
