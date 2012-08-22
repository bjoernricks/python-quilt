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

from quilt.command import Command
from quilt.db import Db, Series
from quilt.error import QuiltError
from quilt.patch import Patch, Diff
from quilt.signals import Signal
from quilt.utils import Directory, File, TmpFile

INDEX_LINE = \
    "==================================================================="

class Refresh(Command):
    """ Command class to refresh (add or remove chunks) a patch
    """

    edit_patch = Signal()
    refreshed = Signal()

    def __init__(self, cwd, quilt_pc, quilt_patches):
        super(Refresh, self).__init__(cwd)
        self.quilt_pc = Directory(quilt_pc)
        self.quilt_patches = Directory(quilt_patches)
        self.db = Db(quilt_pc)
        self.series = Series(quilt_patches)

    def refresh(self, patch_name=None, edit=False):
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
        patch_file = self.quilt_patches + File(patch.get_name())
        files = pc_dir.content()[1]

        with TmpFile(prefix="pquilt-") as tmpfile:
            f = tmpfile.open()

            if patch_file.exists():
                header = patch.get_header(self.quilt_patches)
                tmpfile.write(header)

            for file_name in files:
                if file_name == ".timestamp":
                    continue
                orig_file = pc_dir + File(file_name)
                new_file = File(file_name)
                left_label, right_label, index = self._get_labels(orig_file,
                                                                  new_file)
                self._write_index(tmpfile, index)

                diff = Diff(orig_file, new_file)
                diff.run(self.cwd, fd=f, left_label=left_label,
                         right_label=right_label)

            if tmpfile.is_empty():
                raise QuiltError("Nothing to refresh.")

            if edit:
                self.edit_patch(tmpfile)
                tpatch = Patch(tmpfile.get_name())
                tpatch.run(pc_dir.get_name(), dry_run=True, quiet=True)

            if patch_file.exists():
                diff = Diff(patch_file, tmpfile)
                if diff.equal(self.cwd):
                    raise QuiltError("Nothing to refresh.")

            tmpfile.copy(patch_file)

        timestamp = pc_dir + File(".timestamp")
        timestamp.touch()

        refresh = self.quilt_pc + File(patch.get_name() + "~refresh")
        refresh.delete_if_exists()

        self.refreshed(patch)

    def _get_labels(self, old_file, new_file):
        dir = os.path.basename(self.cwd)

        old_file_name = old_file.get_name()
        new_file_name =  new_file.get_name()
        old_hdr = dir + ".orig/" + old_file_name
        new_hdr = dir + "/" + new_file_name

        index = new_hdr

        if not old_file.exists() or old_file.is_empty():
            old_hdr = "/dev/null"

        if not new_file.exists() or new_file.is_empty():
            old_hdr = new_hdr
            new_hdr = "/dev/null"

        return (old_hdr, new_hdr, index)

    def _write_index(self, f, index):
        f.write("Index: ")
        f.write(index)
        f.write("\n")
        f.write(INDEX_LINE)
        f.write("\n")
