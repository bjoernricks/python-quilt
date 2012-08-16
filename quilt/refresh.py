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

from quilt.command import Command
from quilt.db import Db, Series
from quilt.error import QuiltError
from quilt.patch import Patch, Diff
from quilt.utils import Directory, File, TmpFile

class Refresh(Command):
    """ Command class to refresh (add or remove chunks) a patch
    """
    def __init__(self, cwd, quilt_pc, quilt_patches):
        super(Refresh, self).__init__(cwd)
        self.quilt_pc = Directory(quilt_pc)
        self.quilt_patches = Directory(quilt_patches)
        self.db = Db(quilt_pc)
        self.series = Series(quilt_patches)

    def refresh(self, patch_name=None):
        """ Refresh patch with patch_name or applied top patch if patch_name is
        None
        """
        if patch_name:
            patch = Patch(patch_name)
        else:
            patch = self.db.top_patch()

            if not patch:
                raise QuiltError("No patch applied. Nothing to refresh.")

        pc_dir = self.quilt_pc + patch.get_name()
        files = pc_dir.content()[1]

        with TmpFile(prefix="pquilt-") as tmpfile:
            f = tmpfile.open()
            for file_name in files:
                if file_name == ".timestamp":
                    continue
                orig_file = pc_dir + File(file_name)
                new_file = File(file_name)
                diff = Diff(orig_file, new_file)
                diff.run(self.cwd, fd=f)

            if tmpfile.is_empty():
                raise QuiltError("Nothing to refresh.")

            tmpfile.copy(self.quilt_patches + File(patch.get_name()))

        timestamp = pc_dir + File(".timestamp")
        timestamp.touch()

        refresh = self.quilt_pc + File(patch.get_name() + "~refresh")
        refresh.delete_if_exists()
