# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

""" Helpers for the python-quilt test suite """

import unittest

class QuiltTest(unittest.TestCase):
    """ Base class for all TestCases """

    @classmethod
    def suite(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
        return suite

    @classmethod
    def run_tests(cls):
        runner = unittest.TextTestRunner()
        runner.run(cls.suite())

class tmp_mapping:
    """ Context manager for temporarily altering a mapping """
    
    def __init__(self, target):
        self.target = target
        self.orig = dict()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        while self.orig:
            (key, value) = self.orig.popitem()
            if value is None:
                del self.target[key]
            else:
                self.target[key] = value
    
    def set(self, key, value):
        self.orig.setdefault(key, self.target.get(key))
        self.target[key] = value
