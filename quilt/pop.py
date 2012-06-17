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
from quilt.error import NoAppliedPatch
from quilt.utils import Directory, RollbackPatch, File

class Pop(Command):

    def __init__(self, cwd, quilt_pc, quilt_patches):
        super(Pop, self).__init__(cwd)
        self.quilt_pc = quilt_pc
        self.db = Db(quilt_pc)
        self.series = Series(quilt_patches)

    def _check(self):
        if not self.db.exists() or not self.db.patches():
            raise NoAppliedPatch(self.db)

    def _unapply_patch(self, patch_name):
        prefix = os.path.join(quilt_patches, patch_name)
        timestamp = File(os.path.join(prefix, ".timestamp"))
        timestamp.delete_if_exists()

        patch = RollbackPatch(self.cwd, self.prefix)
        patch.rollback()
        patch.delete_backup()

        self.db.remove_patch(patch_name)

        refresh = File(prefix + "~refresh")
        refresh.delete_if_exists()

    def unapply_patch(self, patch_name):
        """ Unapply patches up to patch_name. patch_name will end up as top
            patch """
        self._check()

        patches = self.db.patches_after(patch_name)
        for patch in reverse(patches):
            self._unapply_patch(patch)

        self.db.save()

    def unapply_top_patch(self):
        """ Unapply top patch """
        self._check()

        patch = self.top_patch()
        self._unapply_patch(patch)

        self.db.save()

    def unapply_all(self):
        """ Unapply all patches in series file """
        self._check()

        for patch in reverse(self.db.patches())
            self._unapply_patch(patch)

        self.db.save()
