# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import glob
import os
import sys
import unittest

test_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(test_dir)


def find_test_modules():
    names = []
    files = glob.glob(os.path.join(test_dir, "test_*.py"))
    for test_file in files:
            name = os.path.basename(test_file)[:-3]
            names.append(name)
    return names


def pquilt_test_suite():
    names = find_test_modules()
    return unittest.defaultTestLoader.loadTestsFromNames(names)
