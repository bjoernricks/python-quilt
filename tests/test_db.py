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
import shutil

from helpers import QuiltTest

test_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(test_dir, os.pardir))

from quilt.db import PatchSeries

class DbTest(QuiltTest):

    def test_series(self):
        db = PatchSeries(os.path.join(test_dir, "data", "db"), "series_test1")

        self.assertEqual(["firstpatch", "secondpatch", "thirdpatch", 
                          "patchwith.patch", "patchwith.diff",
                          "patchwith param1 param2", "lastpatch"],
                          db.patches())
        self.assertEqual("firstpatch", db.first_patch())
        self.assertEqual("lastpatch", db.top_patch())
        self.assertEqual("secondpatch", db.patch_after("firstpatch"))
        self.assertTrue(db.is_patch("thirdpatch"))
        self.assertFalse(db.is_patch("notapatch"))
        self.assertEqual([], db.patches_before("firstpatch"))
        self.assertEqual(["firstpatch", "secondpatch"],
                         db.patches_before("thirdpatch"))
        self.assertEquals(["patchwith.patch", "patchwith.diff",
                           "patchwith param1 param2", "lastpatch"],
                          db.patches_after("thirdpatch"))
        self.assertEquals([], db.patches_after("lastpatch"))
        self.assertEquals(None, db.patch_after("lastpatch"))

        # test re-reading patches list
        db.read()
        self.assertEqual(["firstpatch", "secondpatch", "thirdpatch",
                          "patchwith.patch", "patchwith.diff",
                          "patchwith param1 param2", "lastpatch"],
                          db.patches())

    def test_add_remove(self):
        # test add, remove patches
        db = PatchSeries(os.path.join(test_dir, "data", "db"), "series_test1")
        db.add_patch("newlastpatch")
        self.assertTrue(db.is_patch("newlastpatch"))
        self.assertEqual(["firstpatch", "secondpatch", "thirdpatch",
                          "patchwith.patch", "patchwith.diff",
                          "patchwith param1 param2", "lastpatch",
                          "newlastpatch"],
                          db.patches())
        self.assertEqual("newlastpatch", db.top_patch())

        db.remove_patch("newlastpatch")
        self.assertFalse(db.is_patch("newlastpatch"))
        self.assertEqual(["firstpatch", "secondpatch", "thirdpatch",
                          "patchwith.patch", "patchwith.diff",
                          "patchwith param1 param2", "lastpatch"],
                          db.patches())
        self.assertEqual("lastpatch", db.top_patch())

        db.add_patches(["newlast1", "newlast2"])
        self.assertTrue(db.is_patch("newlast1"))
        self.assertTrue(db.is_patch("newlast2"))
        self.assertEqual(["firstpatch", "secondpatch", "thirdpatch",
                          "patchwith.patch", "patchwith.diff",
                          "patchwith param1 param2", "lastpatch",
                          "newlast1", "newlast2"],
                          db.patches())
        self.assertEqual("newlast2", db.top_patch())

        db = PatchSeries(os.path.join(test_dir, "data", "db"), "series_test1")
        db.add_patches(["newlast1", "newlast2"], "firstpatch")
        self.assertTrue(db.is_patch("newlast1"))
        self.assertTrue(db.is_patch("newlast2"))
        self.assertEqual(["firstpatch", "newlast1", "newlast2",
                          "secondpatch", "thirdpatch",
                          "patchwith.patch", "patchwith.diff",
                          "patchwith param1 param2", "lastpatch"],
                          db.patches())
        self.assertEqual("lastpatch", db.top_patch())

        db = PatchSeries(os.path.join(test_dir, "data", "db"), "series_test1")
        db.insert_patches(["newfirst1", "newfirst2"])
        self.assertTrue(db.is_patch("newfirst1"))
        self.assertTrue(db.is_patch("newfirst2"))
        self.assertEqual(["newfirst1", "newfirst2", "firstpatch",
                          "secondpatch", "thirdpatch",
                          "patchwith.patch", "patchwith.diff",
                          "patchwith param1 param2", "lastpatch"],
                          db.patches())
        self.assertEqual("newfirst1", db.first_patch())
        self.assertEqual("lastpatch", db.top_patch())



def suite():
    return DbTest.suite()

if __name__ == "__main__":
    DbTest.run_tests()
