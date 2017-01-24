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

from helpers import QuiltTest, StringIO, tmp_mapping

test_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(test_dir, os.pardir))

from quilt.db import PatchSeries, Series
from quilt.db import Patch
from quilt.utils import TmpDirectory

def patch_list(patch_names):
    return [Patch(name) for name in patch_names]

class DbTest(QuiltTest):

    def test_series(self):
        firstpatch = Patch("firstpatch")
        lastpatch = Patch("lastpatch")
        secondpatch = Patch("secondpatch")
        thirdpatch = Patch("thirdpatch")

        db = PatchSeries(os.path.join(test_dir, "data", "db"), "series_test1")

        self.assertEqual(patch_list(["firstpatch", "secondpatch", "thirdpatch",
                          "patchwith.patch", "patchwith.diff",
                          "patchwith", "lastpatch"]),
                          db.patches())
        self.assertEqual(firstpatch, db.first_patch())
        self.assertEqual(lastpatch, db.top_patch())
        self.assertEqual(secondpatch, db.patch_after(firstpatch))
        self.assertTrue(db.is_patch(thirdpatch))
        self.assertFalse(db.is_patch(Patch("notapatch")))
        self.assertEqual([], db.patches_before(firstpatch))
        self.assertEqual(patch_list(["firstpatch", "secondpatch"]),
                         db.patches_before(thirdpatch))
        self.assertEquals(patch_list(["patchwith.patch", "patchwith.diff",
                           "patchwith", "lastpatch"]),
                          db.patches_after(thirdpatch))
        self.assertEquals([], db.patches_after(lastpatch))
        self.assertEquals(None, db.patch_after(lastpatch))
        self.assertEquals(thirdpatch, db.patch_after(secondpatch))
        self.assertEqual(patch_list(["firstpatch", "secondpatch",
                         "thirdpatch"]),
                         db.patches_until(thirdpatch))

        # test re-reading patches list
        db.read()
        self.assertEqual(patch_list(["firstpatch", "secondpatch", "thirdpatch",
                          "patchwith.patch", "patchwith.diff",
                          "patchwith", "lastpatch"]),
                          db.patches())

    def test_patch_args(self):
        with TmpDirectory() as dir:
            series = Series(dir.get_name())
            with open(series.series_file, "wb") as file:
                file.write(
                    b"patch1 -p0 --reverse\n"
                    b"patch2 --strip=0 -R\n"
                )
            series.read()
            [patch1, patch2] = series.patches()
            self.assertEqual(patch1.strip, "0")
            self.assertIs(patch1.reverse, True)
            self.assertEqual(patch2.strip, "0")
            self.assertIs(patch2.reverse, True)

    def test_bad_args(self):
        with TmpDirectory() as dir:
            series = Series(dir.get_name())
            with open(series.series_file, "wb") as file:
                file.write(b"patch -X\n")
            with tmp_mapping(vars(sys)) as tmp_sys:
                tmp_sys.set("stderr", StringIO())
                series.read()
                self.assertIn("-X", sys.stderr.getvalue())

    def test_add_remove(self):
        # test add, remove patches

        firstpatch = Patch("firstpatch")
        lastpatch = Patch("lastpatch")
        newlastpatch = Patch("newlastpatch")

        db = PatchSeries(os.path.join(test_dir, "data", "db"), "series_test1")
        db.add_patch(newlastpatch)
        self.assertTrue(db.is_patch(newlastpatch))
        self.assertEqual(patch_list(["firstpatch", "secondpatch", "thirdpatch",
                          "patchwith.patch", "patchwith.diff",
                          "patchwith", "lastpatch",
                          "newlastpatch"]),
                          db.patches())
        self.assertEqual(newlastpatch, db.top_patch())

        db.remove_patch(newlastpatch)
        self.assertFalse(db.is_patch(newlastpatch))
        self.assertEqual(patch_list(["firstpatch", "secondpatch", "thirdpatch",
                          "patchwith.patch", "patchwith.diff",
                          "patchwith", "lastpatch"]),
                          db.patches())
        self.assertEqual(lastpatch, db.top_patch())

        newfirst1 = Patch("newfirst1")
        newfirst2 = Patch("newfirst2")
        db.add_patches([newfirst1, newfirst2])
        self.assertTrue(db.is_patch(newfirst1))
        self.assertTrue(db.is_patch(newfirst2))
        self.assertEqual(patch_list(["newfirst1", "newfirst2",
                          "firstpatch", "secondpatch", "thirdpatch",
                          "patchwith.patch", "patchwith.diff",
                          "patchwith", "lastpatch"]),
                          db.patches())
        self.assertEqual(lastpatch, db.top_patch())

        newlast1 = Patch("newlast1")
        newlast2 = Patch("newlast2")
        db = PatchSeries(os.path.join(test_dir, "data", "db"), "series_test1")
        db.add_patches([newlast1, newlast2], firstpatch)
        self.assertTrue(db.is_patch(newlast1))
        self.assertTrue(db.is_patch(newlast2))
        self.assertEqual(patch_list(["firstpatch", "newlast1", "newlast2",
                          "secondpatch", "thirdpatch",
                          "patchwith.patch", "patchwith.diff",
                          "patchwith", "lastpatch"]),
                          db.patches())
        self.assertEqual(lastpatch, db.top_patch())

        db = PatchSeries(os.path.join(test_dir, "data", "db"), "series_test1")
        newfirst1 = Patch("newfirst1")
        newfirst2 = Patch("newfirst2")
        db.insert_patches([newfirst1, newfirst2])
        self.assertTrue(db.is_patch(newfirst1))
        self.assertTrue(db.is_patch(newfirst2))
        self.assertEqual(patch_list(["newfirst1", "newfirst2", "firstpatch",
                          "secondpatch", "thirdpatch",
                          "patchwith.patch", "patchwith.diff",
                          "patchwith", "lastpatch"]),
                          db.patches())
        self.assertEqual(newfirst1, db.first_patch())
        self.assertEqual(lastpatch, db.top_patch())

    def test_replace(self):
        db = PatchSeries(os.path.join(test_dir, "data", "db"),
                         "series_replace1")

        self.assertTrue(db.exists())
        self.assertFalse(db.is_empty())
        self.assertEquals(len(db.patches()), 3)

        patch1 = Patch("patch1")
        patch2 = Patch("patch2")
        patch4 = Patch("patch4")
        patch5 = Patch("patch5")

        self.assertTrue(db.is_patch(patch1))
        db.replace(patch1, patch4)
        self.assertFalse(db.is_patch(patch1))
        self.assertTrue(db.is_patch(patch4))

        self.assertTrue(db.is_patch(patch2))
        db.replace(patch2, patch5)
        self.assertFalse(db.is_patch(patch2))
        self.assertTrue(db.is_patch(patch5))

        patchline = db.patch2line[patch5]
        self.assertEquals(patchline.get_comment(), " my comment")


if __name__ == "__main__":
    DbTest.run_tests()
