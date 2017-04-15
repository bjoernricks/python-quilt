# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# See LICENSE comming with the source of python-quilt for details.

import os

from helpers import make_file
from unittest import TestCase

import quilt.refresh

from quilt.db import Db, Patch
from quilt.utils import TmpDirectory


class Test(TestCase):

    def test_refresh(self):
        with TmpDirectory() as dir:
            old_dir = os.getcwd()
            try:
                os.chdir(dir.get_name())
                db = Db(".pc")
                db.create()
                backup = os.path.join(".pc", "patch")
                os.mkdir(backup)
                make_file(b"", backup, "file")
                db.add_patch(Patch("patch"))
                db.save()
                make_file(b"", "patch")
                make_file(b"added\n", "file")
                cmd = quilt.refresh.Refresh(".", ".pc", ".")
                cmd.refresh()
                with open("patch", "r") as patch:
                    self.assertTrue(patch.read(30))
            finally:
                os.chdir(old_dir)
