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
from quilt.utils import Directory, File

class Import(Command):
    """ Command class to import patches into the patch queue """

    def __init__(self, cwd, quilt_pc, quilt_patches):
        super(Import, self).__init__(cwd)
        self.quilt_pc = Directory(quilt_pc)
        self.db = Db(quilt_pc)
        self.series = Series(quilt_patches)

    def _import_patches(self, patches, reverse=False, strip=None):
        top = self.db.top_patch()
        if top is None:
            self.series.insert_patches(patches)
        else:
            self.series.add_patches(patches, top)

    def import_patch(self, patch_name, new_name=None):
        """ Import patch into the patch queue
        The patch is inserted after the current top applied patch
        """
        if not new_name:
            dir_name = os.path.dirname(new_name)
            name = os.path.basename(new_name)
            dest_dir = self.quilt_pc + Directory(dir_name)
            dest_dir.create()
        else:
            name = os.path.basename(patch_name)
            dest_dir = self.quilt_pc

        patch_file = File(patch_name)
        dest_file = dest_dir + File(name)
        patch_file.copy(dest_file)
        self.series.add_patches([name])

    def import_patches(self, patches):
        """ Import several patches into the patch queue """

        dest_dir = self.quilt_pc

        for patch in patches:
            patch_name = os.path.basename(patch)
            patch_file = File(patch_name)
            dest_file = dest_dir + File(patch_name)
            patch_file.copy(dest_file)

        self.series.add_patches(patches)
