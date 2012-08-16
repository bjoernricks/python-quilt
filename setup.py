#!/usr/bin/env python
# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012  Björn Ricks <bjoern.ricks@googlemail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 
# 02110-1301 USA

from distutils.core import setup

import quilt

f = open('README.rst', 'r')
README = f.read()

setup(name="python-quilt",
      version=quilt.__version__,
      description="A quilt patchsystem implementation in Python",
      author="Björn Ricks",
      author_email="bjoern.ricks@gmail.com",
      url="http://github.com/bjoernricks/python-quilt",
      scripts=["pquilt"],
      license="LGPLv2.1+",
      packages=["quilt", "quilt.cli"],
      classifiers=["Development Status :: 3 - Alpha",
                   "Environment :: Console",
                   "Intended Audience :: Developers",
                   "Intended Audience :: System Administrators",
                   "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Build Tools",
                   "Topic :: System :: Software Distribution",
                   "Topic :: Utilities",
                   ],
      long_description=README,
      )


