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

import os
import glob
import sys
import unittest
import optparse

test_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(test_dir, os.pardir))

def find_test_modules(dirname):
    names = []
    files = glob.glob(os.path.join(test_dir, "test_*.py"))
    for test_file in files:
            name = os.path.basename(test_file)[:-3]
            names.append(name)
    return names


def main():
    parser = optparse.OptionParser()
    parser.set_defaults(verbosity=1)
    parser.add_option("-v", "--verbose", action="store_const", const=2,
                      dest="verbosity")
    opts, args = parser.parse_args()

    if args:
        names = args
    else:
        names = find_test_modules(test_dir)
    if not names:
        print("No tests available")
        sys.exit(1)

    suite = unittest.defaultTestLoader.loadTestsFromNames(names)
    runner = unittest.TextTestRunner(verbosity=opts.verbosity)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    main()
