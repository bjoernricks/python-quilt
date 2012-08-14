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
import stat

from quilt.backup import Backup
from quilt.command import Command
from quilt.db import Db, Series
from quilt.error import QuiltError
from quilt.utils import Directory, File

class Add(Command):
    """Command class to add files to the current patch
    """
    def __init__(self, cwd, quilt_pc, quilt_patches):
        super(Add, self).__init__(cwd)
        self.quilt_pc = Directory(quilt_pc)
        self.quilt_patches = Directory(quilt_patches)
        self.db = Db(quilt_pc)
        self.series = Series(quilt_patches)

    def _file_in_patch(self, filename, patch, ignore):
        """ Checks if a backup file of the filename in the current patch
        exists """
        file = self.quilt_pc + File(os.path.join(patch.get_name(), filename))
        if file.exists():
            if ignore:
                return True
            else:
                raise QuiltError("File %s is already in patch %s" % (filename,
                                 patch.get_name()))
        return False

    def _file_in_next_patches(self, filename, patch):
        """ Checks if a backup file of the filename in the applied patches after
        patch exists """

        if not self.db.is_patch(patch):
            # no paches applied
            return

        patches = self.db.patches_after(patch)
        for patch in patches:
            file = self.quilt_pc + File(os.path.join(patch.get_name(),
                                                     filename))
            if file.exists():
                raise QuiltError("File %s is already modified by patch %s" % \
                                 (filename, patch.get_name()))

    def _backup_file(self, filename, patch):
        """ Creates a backup of filename """
        dest_dir = self.quilt_pc + patch.get_name()
        backup = Backup()
        backup.backup_file(filename, dest_dir, copy_empty=True)

    def add_file(self, filename, patch_name=None, ignore=False):
        """ Add file to the patch with patch_name.
        If patch_name is None or empty the topmost patch will be used.
        Adding an already added patch will raise an QuiltError if ignore is
        False.
        """
        file = File(filename)

        if patch_name:
            patch = Patch(patch_name)
        else:
            patch = self.db.top_patch()
            if not patch:
                raise QuiltError("No patches applied.")

        exists = self._file_in_patch(filename, patch, ignore)
        if exists:
            return

        self._file_in_next_patches(filename, patch)

        if file.is_link():
            raise QuiltError("Cannot add symbolic link %s" % filename)

        self._backup_file(filename, patch)

        if file.exists():
            # be sure user can write original file
            os.chmod(filename, file.get_mode() | stat.S_IWUSR | stat.S_IRUSR)

    def add_files(self, filenames, patch_name=None, ignore=False):
        for filename in filenames:
            self.add_file(filename, patch_name, ignore)
