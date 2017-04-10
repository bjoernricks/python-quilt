# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.command import Command
from quilt.db import Db
from quilt.error import NoAppliedPatch, QuiltError
from quilt.patch import RollbackPatch, Patch
from quilt.signals import Signal
from quilt.utils import Directory, File


class Pop(Command):

    unapplying = Signal()
    unapplied = Signal()
    unapplied_patch = Signal()
    empty_patch = Signal()

    def __init__(self, cwd, quilt_pc):
        super(Pop, self).__init__(cwd)
        self.quilt_pc = Directory(quilt_pc)
        self.db = Db(quilt_pc)

    def _check(self, force=False):
        if not self.db.exists() or not self.db.patches():
            raise NoAppliedPatch(self.db)
        if not force:
            patch = self.db.top_patch()
            pc_dir = self.quilt_pc + patch.get_name()
            refresh = File(pc_dir.get_name() + "~refresh")
            if refresh.exists():
                raise QuiltError("Patch %s needs to be refreshed first." %
                                 patch.get_name())

    def _unapply_patch(self, patch):
        self.unapplying(patch)

        patch_name = patch.get_name()
        pc_dir = self.quilt_pc + patch_name
        timestamp = pc_dir + File(".timestamp")
        timestamp.delete_if_exists()

        if pc_dir.is_empty():
            pc_dir.delete()
            self.empty_patch(patch)
        else:
            unpatch = RollbackPatch(self.cwd, pc_dir)
            unpatch.rollback()
            unpatch.delete_backup()

        self.db.remove_patch(patch)

        refresh = File(pc_dir.get_name() + "~refresh")
        refresh.delete_if_exists()

        self.unapplied_patch(patch)

    def unapply_patch(self, patch_name, force=False):
        """ Unapply patches up to patch_name. patch_name will end up as top
            patch """
        self._check(force)

        patches = self.db.patches_after(Patch(patch_name))
        for patch in reversed(patches):
            self._unapply_patch(patch)

        self.db.save()

        self.unapplied(self.db.top_patch())

    def unapply_top_patch(self, force=False):
        """ Unapply top patch """
        self._check(force)

        patch = self.db.top_patch()
        self._unapply_patch(patch)

        self.db.save()

        self.unapplied(self.db.top_patch())

    def unapply_all(self, force=False):
        """ Unapply all patches """
        self._check(force)

        for patch in reversed(self.db.applied_patches()):
            self._unapply_patch(patch)

        self.db.save()

        self.unapplied(self.db.top_patch())
