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
from quilt.patch import Patch
from quilt.utils import Directory, File

class Import(Command):
    """ Command class to import patches into the patch queue """

    def __init__(self, cwd, quilt_pc, quilt_patches):
        super(Import, self).__init__(cwd)
        self.quilt_pc = Directory(quilt_pc)
        self.quilt_patches = Directory(quilt_patches)
        self.db = Db(quilt_pc)
        self.series = Series(quilt_patches)

    def _import_patches(self, patches, reverse=False, strip=None):
        top = self.db.top_patch()
        patchlist = []
        for patch in patches:
            patchlist.append(Patch(patch, reverse=reverse, strip=strip))
        self.series.add_patches(patchlist, top)
        self.series.save()

    def import_patch(self, patch_name, new_name=None):
        """ Import patch into the patch queue
        The patch is inserted after the current top applied patch
        """
        if new_name:
            dir_name = os.path.dirname(new_name)
            name = os.path.basename(new_name)
            dest_dir = self.quilt_patches + Directory(dir_name)
            dest_dir.create()
        else:
            name = os.path.basename(patch_name)
            dest_dir = self.quilt_patches

        patch_file = File(patch_name)
        dest_file = dest_dir + File(name)
        patch_file.copy(dest_file)
        self._import_patches([name])

    def import_patches(self, patches):
        """ Import several patches into the patch queue """

        dest_dir = self.quilt_patches
        patch_names = []

        for patch in patches:
            patch_name = os.path.basename(patch)
            patch_file = File(patch)
            dest_file = dest_dir + File(patch_name)
            patch_file.copy(dest_file)
            patch_names.append(patch_name)

        self._import_patches(patch_names)
