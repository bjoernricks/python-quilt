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

import os.path
import sys

from helpers import QuiltTest

test_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(test_dir, os.pardir))

from quilt.patch import Patch
from quilt.pop import Pop
from quilt.utils import Directory, TmpDirectory, File

class PopTest(QuiltTest):

    data_dir = Directory(os.path.join(test_dir, "data", "pop"))

    def test_unapply_all(self):
        patch1 = Patch("p1.patch")
        patch2 = Patch("p2.patch")

        test_dir = self.data_dir + "test1"

        with TmpDirectory(dir=self.data_dir.get_name()) as tmp_dir:
            tmp_test_dir = tmp_dir + "test1"
            test_dir.copy(tmp_test_dir)

            pc_dir = tmp_test_dir + "pc"
            patches_dir = tmp_test_dir + "patches"

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
            patches_dir = tmp_test_dir + "patches"

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


def suite():
    return PopTest.suite()

if __name__ == "__main__":
    PopTest.run_tests()
