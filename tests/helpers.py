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

""" Helpers for the python-quilt test suite """

import unittest

class QuiltTest(unittest.TestCase):
    """ Base class for all TestCases """

    def assert_same_content(self, expected_file, actual_file):
        expected = None
        with open(expected_file, "r") as f:
            expected = f.read()
        with open(actual_fiel, "r") as f:
            actual = f.read()

    @classmethod
    def suite(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
        return suite

    @classmethod
    def run_tests(cls):
        runner = unittest.TextTestRunner()
        runner.run(cls.suite())

