#!/usr/bin/env python
# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from setuptools import setup

from codecs import open

import os

import quilt

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), 'r', encoding="utf-8") as f:
    README = f.read()

setup(
    name="python-quilt",
    version=quilt.__version__,
    description="A quilt patch system implementation in Python",
    author="Björn Ricks",
    author_email="bjoern.ricks@gmail.com",
    install_requires=["six"],
    url="http://github.com/bjoernricks/python-quilt",
    scripts=["pquilt"],
    license="MIT",
    packages=["quilt", "quilt.cli"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities",
    ],
    long_description=README,
    keywords="patch quilt python cli",
    test_suite="tests.pquilt_test_suite",
)
