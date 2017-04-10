#!/usr/bin/env python
# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os.path

from helpers import QuiltTest

from quilt.patch import Patch
from quilt.pop import Pop
from quilt.utils import Directory, TmpDirectory, File

test_dir = os.path.dirname(__file__)


class PopTest(QuiltTest):

    data_dir = Directory(os.path.join(test_dir, "data", "pop"))

    def test_unapply_all(self):
        patch2 = Patch("p2.patch")

        test_dir = self.data_dir + "test1"

        with TmpDirectory(dir=self.data_dir.get_name()) as tmp_dir:
            tmp_test_dir = tmp_dir + "test1"
            test_dir.copy(tmp_test_dir)

            pc_dir = tmp_test_dir + "pc"

            f1 = tmp_test_dir + File("f1")
            self.assertTrue(f1.exists())
            f2 = tmp_test_dir + File("f2")
            self.assertTrue(f2.exists())

            pop = Pop(tmp_test_dir.get_name(), pc_dir.get_name())

            self.assertEquals(patch2, pop.db.top_patch())
            pop.unapply_all()
            self.assertEquals(None, pop.db.top_patch())

            self.assertFalse(f1.exists())
            self.assertFalse(f2.exists())

    def test_apply_next(self):
        patch1 = Patch("p1.patch")
        patch2 = Patch("p2.patch")

        test_dir = self.data_dir + "test1"

        with TmpDirectory(dir=self.data_dir.get_name()) as tmp_dir:
            tmp_test_dir = tmp_dir + "test2"

            test_dir.copy(tmp_test_dir)

            pc_dir = tmp_test_dir + "pc"

            f1 = tmp_test_dir + File("f1")
            self.assertTrue(f1.exists())
            f2 = tmp_test_dir + File("f2")
            self.assertTrue(f2.exists())

            pop = Pop(tmp_test_dir.get_name(), pc_dir.get_name())
            self.assertEquals(patch2, pop.db.top_patch())

            pop.unapply_top_patch()
            self.assertEquals(patch1, pop.db.top_patch())

            self.assertTrue(f1.exists())
            self.assertFalse(f2.exists())

            pop.unapply_top_patch()
            self.assertEquals(None, pop.db.top_patch())

            self.assertFalse(f1.exists())
            self.assertFalse(f2.exists())


if __name__ == "__main__":
    PopTest.run_tests()
