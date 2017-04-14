#!/usr/bin/env python
# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os.path
from six.moves import cStringIO
import sys

from helpers import QuiltTest, make_file, tmp_mapping, tmp_series

test_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(test_dir, os.pardir))

from quilt.db import Db, DBError, DB_VERSION, PatchSeries
from quilt.db import Patch
from quilt.utils import TmpDirectory


def patch_list(patch_names):
    return [Patch(name) for name in patch_names]


class DbTest(QuiltTest):

    def test_patch_equivalence(self):
        a = Patch("same")
        self.assertTrue(a == a)
        self.assertFalse(a != a)
        
        b = Patch("same")
        self.assertTrue(a == b)
        self.assertFalse(a != b)
        self.assertEqual(hash(a), hash(b))
        
        c = Patch("different")
        self.assertTrue(a != c)
        self.assertFalse(a == c)
    
    def test_version(self):
        version = "234\n"
        self.assertTrue(version.startswith(format(DB_VERSION)))
        with TmpDirectory() as dir:
            make_file(version.encode("ascii"), dir.get_name(), ".version")
            self.assertRaises(DBError, Db, dir.get_name())

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
        self.assertEqual(secondpatch, db.patch_before(thirdpatch))
        self.assertTrue(db.is_patch(thirdpatch))
        self.assertFalse(db.is_patch(Patch("notapatch")))
        self.assertEqual([], db.patches_before(firstpatch))
        self.assertEqual(patch_list(["firstpatch", "secondpatch"]),
                         db.patches_before(thirdpatch))
        self.assertEqual(patch_list(["patchwith.patch", "patchwith.diff",
                          "patchwith", "lastpatch"]),
                          db.patches_after(thirdpatch))
        self.assertEqual([], db.patches_after(lastpatch))
        self.assertEqual(None, db.patch_after(lastpatch))
        self.assertEqual(thirdpatch, db.patch_after(secondpatch))
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
        with tmp_series() as [dir, series]:
            make_file(
                b"patch1 -p0 --reverse\n"
                b"patch2 --strip=0 -R\n", series.series_file)
            series.read()
            [patch1, patch2] = series.patches()
            self.assertEqual(patch1.strip, "0")
            self.assertIs(patch1.reverse, True)
            self.assertEqual(patch2.strip, "0")
            self.assertIs(patch2.reverse, True)

    def test_bad_args(self):
        with tmp_series() as [dir, series]:
            make_file(b"patch -X\n", series.series_file)
            with tmp_mapping(vars(sys)) as tmp_sys:
                tmp_sys.set("stderr", cStringIO())
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
        self.assertEqual(len(db.patches()), 3)

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
        self.assertEqual(patchline.get_comment(), " my comment")


if __name__ == "__main__":
    DbTest.run_tests()
