# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.command import Command
from quilt.db import Db, Series
from quilt.error import NoPatchesInSeries, NoAppliedPatch, UnknownPatch, \
                        QuiltError
from quilt.patch import Patch
from quilt.pop import Pop
from quilt.signals import Signal
from quilt.utils import Directory, File


class Delete(Command):

    """Command class to delete patches
    """

    deleting_patch = Signal()
    deleted_patch = Signal()

    def __init__(self, cwd, quilt_pc, quilt_patches):
        super(Delete, self).__init__(cwd)
        self.quilt_pc = Directory(quilt_pc)
        self.quilt_patches = Directory(quilt_patches)
        self.db = Db(quilt_pc)
        self.series = Series(quilt_patches)
        self.pop = Pop(cwd, quilt_pc)

    def _delete_patch(self, patch, remove=False, backup=False):
        if self.series.is_empty():
            raise NoPatchesInSeries(self.series)
        if not self.series.is_patch(patch):
            raise UnknownPatch(self.series, patch)

        applied = self.db.top_patch() == patch
        self.deleting_patch(patch, applied)

        if applied:
            self.pop._unapply_patch(patch)
            self.db = self.pop.db
            self.db.save()

        self.series.remove_patch(patch)
        self.series.save()

        patch_file = self.quilt_patches + File(patch.get_name())

        if remove:
            if backup:
                patch_file.copy(File(patch_file.get_name() + "~"))

            patch_file.delete_if_exists()

        self.deleted_patch(patch)

    def delete_next(self, remove=False, backup=False):
        """ Delete next unapplied patch
        If remove is True the patch file will also be removed. If remove and
        backup are True a copy of the deleted patch file will be made.
        """
        patch = self.db.top_patch()
        if patch:
            after = self.series.patch_after(patch)
        else:
            after = self.series.first_patch()
        if not after:
            raise QuiltError("No next patch")

        self._delete_patch(after, remove=remove, backup=backup)

    def delete_patch(self, patch_name=None, remove=False, backup=False):
        """ Delete specified patch from the series
        If remove is True the patch file will also be removed. If remove and
        backup are True a copy of the deleted patch file will be made.
        """
        if patch_name:
            patch = Patch(patch_name)
        else:
            patch = self.db.top_patch()
            if not patch:
                raise NoAppliedPatch(self.db)

        self._delete_patch(patch, remove=remove, backup=backup)
