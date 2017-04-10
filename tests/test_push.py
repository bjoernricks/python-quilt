#!/usr/bin/env python
# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os.path
import sys

from helpers import QuiltTest

test_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(test_dir, os.pardir))

from quilt.patch import Patch
from quilt.push import Push
from quilt.utils import Directory, TmpDirectory, File

class PushTest(QuiltTest):

    data_dir = Directory(os.path.join(test_dir, "data", "push"))

    def test_apply_all(self):
        patch1 = Patch("p1.patch")
        patch2 = Patch("p2.patch")

        test_dir = self.data_dir + "test1"

        with TmpDirectory(dir=self.data_dir.get_name()) as tmp_dir:
            tmp_test_dir = tmp_dir + "test1"
            test_dir.copy(tmp_test_dir)

            pc_dir = tmp_test_dir + "pc"
            patches_dir = tmp_test_dir + "patches"

            f1 = tmp_test_dir + File("f1")
            self.assertFalse(f1.exists())
            f2 = tmp_test_dir + File("f2")
            self.assertFalse(f2.exists())

            push = Push(tmp_test_dir.get_name(), pc_dir.get_name(),
                        patches_dir.get_name())

            self.assertEquals(None, push.db.top_patch())
            push.apply_all(quiet=True)
            self.assertEquals(patch2, push.db.top_patch())

            self.assertTrue(f1.exists())
            self.assertTrue(f2.exists())

    def test_apply_next(self):
        patch1 = Patch("p1.patch")
        patch2 = Patch("p2.patch")

        test_dir = self.data_dir + "test2"

        with TmpDirectory(dir=self.data_dir.get_name()) as tmp_dir:
            tmp_test_dir = tmp_dir + "test2"
            test_dir.copy(tmp_test_dir)

            pc_dir = tmp_test_dir + "pc"
            patches_dir = tmp_test_dir + "patches"

            f1 = tmp_test_dir + File("f1")
            self.assertFalse(f1.exists())
            f2 = tmp_test_dir + File("f2")
            self.assertFalse(f2.exists())

            push = Push(tmp_test_dir.get_name(), pc_dir.get_name(),
                        patches_dir.get_name())
            self.assertEquals(None, push.db.top_patch())

            push.apply_next_patch(quiet=True)
            self.assertEquals(patch1, push.db.top_patch())

            self.assertTrue(f1.exists())
            self.assertFalse(f2.exists())

            push.apply_next_patch(quiet=True)
            self.assertEquals(patch2, push.db.top_patch())

            self.assertTrue(f1.exists())
            self.assertTrue(f2.exists())


if __name__ == "__main__":
    PushTest.run_tests()
