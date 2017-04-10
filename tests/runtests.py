#!/usr/bin/env python
# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import sys
import unittest
import optparse

from tests import find_test_modules


def main():
    parser = optparse.OptionParser()
    parser.set_defaults(verbosity=1)
    parser.add_option("-v", "--verbose", action="store_const", const=2,
                      dest="verbosity")
    opts, args = parser.parse_args()

    if args:
        names = args
    else:
        names = find_test_modules()
    if not names:
        print("No tests available")
        sys.exit(1)

    suite = unittest.defaultTestLoader.loadTestsFromNames(names)
    runner = unittest.TextTestRunner(verbosity=opts.verbosity)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    main()
