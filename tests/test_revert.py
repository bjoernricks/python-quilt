import os, os.path

from helpers import make_file, tmp_series
from unittest import TestCase

import quilt.revert

from quilt.db import Db, Patch
from quilt.refresh import Refresh


class Test(TestCase):

    def test_unreverted(self):
        """ Test when the patch modifies unreverted files """
        with tmp_series() as [dir, series]:
            old_dir = os.getcwd()
            try:
                os.chdir(dir)
                db = Db(dir)
                db.add_patch(Patch("patch"))
                db.save()
                originals = os.path.join(db.dirname, "patch")
                os.mkdir(originals)
                make_file(b"unreverted original\n", originals, "unreverted")
                make_file(b"reverted original\n", originals, "reverted")
                make_file(b"unreverted patched\n", dir, "unreverted")
                make_file(b"reverted patched\n", dir, "reverted")
                Refresh(dir, db.dirname, series.dirname).refresh()
                make_file(b"unreverted change\n", dir, "unreverted")
                make_file(b"reverted change\n", dir, "reverted")
                cmd = quilt.revert.Revert(dir, db.dirname, series.dirname)
                cmd.revert_file("reverted")
                with open(os.path.join(dir, "reverted"), "rb") as file:
                    self.assertEqual(file.read(), b"reverted patched\n")
                with open(os.path.join(dir, "unreverted"), "rb") as file:
                    self.assertEqual(file.read(), b"unreverted change\n")
            finally:
                os.chdir(old_dir)
