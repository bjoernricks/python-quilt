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
from quilt.error import NoPatchesInSeries, AllPatchesApplied, QuiltError
from quilt.patch import Patch, RollbackPatch
from quilt.signals import Signal
from quilt.utils import SubprocessError, File, Directory

class Push(Command):

    applying = Signal()
    applying_patch = Signal()
    applied = Signal()
    applied_patch = Signal()
    applied_empty_patch = Signal()

    def __init__(self, cwd, quilt_pc, quilt_patches):
        super(Push, self).__init__(cwd)
        self.quilt_pc = Directory(quilt_pc)
        self.quilt_patches = Directory(quilt_patches)
        self.db = Db(quilt_pc)
        self.series = Series(quilt_patches)

    def _apply_patch(self, patch, force=False, quiet=False):
        patch_name = patch.get_name()
        pc_dir = self.quilt_pc + patch_name
        patch_file = self.quilt_patches + File(patch_name)
        refresh = File(pc_dir.get_name() + "~refresh")

        if refresh.exists():
            raise QuiltError("Patch %s needs to be refreshed" % \
                                  patch_name)

        forced = False
        self.applying_patch(patch)

        if patch_file.exists():
            try:
                patch.run(self.cwd, patch_dir=self.quilt_patches, backup=True,
                        prefix=pc_dir.get_name(), quiet=quiet)
                refresh.delete_if_exists()
            except SubprocessError, e:
                refresh.touch()

                if not force:
                    patch = RollbackPatch(self.cwd, pc_dir)
                    patch.rollback()
                    patch.delete_backup()
                    raise QuiltError("Patch %s does not apply" % patch_name)
                else:
                    forced = True

        self.db.add_patch(patch)

        if pc_dir.exists():
            timestamp = pc_dir + File(".timestamp")
            timestamp.touch()
        else:
            pc_dir.create()

        if not patch_file.exists():
            self.applied_empty_patch(patch, False)
        elif pc_dir.is_empty():
            self.applied_empty_patch(patch, True)
        elif forced:
            raise QuiltExceptions("Applied patch %s (forced; needs " \
                                    "refresh)" % patch.get_name())
        else:
            self.applied_patch(patch)

    def _check(self):
        if not self.series.exists() or not self.series.patches():
            raise NoPatchesInSeries(self.series)

    def apply_patch(self, patch_name, force=False, quiet=False):
        """ Apply all patches up to patch_name """
        self._check()
        patch = Patch(patch_name)
        patches = self.series.patches_until(patch)[:]

        applied = self.db.applied_patches()
        for patch in applied:
            if patch in patches:
                patches.remove(applied)

        if not patches:
            raise AllPatchesApplied(self.series, self.db.top_patch())

        self.applying(patch)

        for cur_patch in patches:
            self._apply_patch(cur_patch, force, quiet)

        self.db.save()

        self.applied(self.db.top_patch())

    def apply_next_patch(self, force=False, quiet=False):
        """ Apply next patch in series file """
        self._check()
        top = self.db.top_patch()
        if not top:
            patch = self.series.first_patch()
        else:
            patch = self.series.patch_after(top)

        if not patch:
            raise AllPatchesApplied(self.series, top)

        self.applying(patch)

        self._apply_patch(patch, force, quiet)

        self.db.save()

        self.applied(self.db.top_patch())

    def apply_all(self, force=False, quiet=False):
        """ Apply all patches in series file """
        self._check()
        top = self.db.top_patch()
        if top:
            patches = self.series.patches_after(top)
        else:
            patches = self.series.patches()

        if not patches:
            raise AllPatchesApplied(self.series, top)

        for patch in patches:
            self.applying(patch)
            self._apply_patch(patch, force, quiet)

        self.db.save()

        self.applied(self.db.top_patch())
