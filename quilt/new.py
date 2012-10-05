# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012  Björn Ricks <bjoern.ricks@gmail.com>
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
from quilt.error import PatchAlreadyExists
from quilt.patch import Patch
from quilt.signals import Signal
from quilt.utils import Directory, File


class New(Command):

    patch_created = Signal()

    """ Creates a new patch in the queue """
    def __init__(self, cwd, quilt_pc, quilt_patches):
        super(New, self).__init__(cwd)
        self.quilt_pc = Directory(quilt_pc)
        self.quilt_patches = Directory(quilt_patches)
        self.db = Db(quilt_pc)
        self.series = Series(quilt_patches)

    def create(self, patchname):
        """ Adds a new patch with patchname to the queue

        The new patch will be added after the top patch
        """
        patch = Patch(patchname)
        if self.series.is_patch(patch):
            raise PatchAlreadyExists(self.series, patchname)

        patch_dir = self.quilt_patches
        patch_dir.create()
        patchfile = patch_dir + File(patchname)
        patchfile.touch()

        pc_dir = self.quilt_pc + patchname
        if pc_dir.exists():
            # be sure that the directory is clear
            pc_dir.delete()
        else:
            pc_dir.create()

        top = self.db.top_patch()
        self.series.add_patches([patch], top)
        self.series.save()

        self.patch_created(patch)
