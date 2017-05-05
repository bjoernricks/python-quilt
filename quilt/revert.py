# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os

from quilt.backup import Backup
from quilt.command import Command
from quilt.db import Db, Series
from quilt.error import QuiltError
from quilt.patch import Diff, Patch
from quilt.signals import Signal
from quilt.utils import Directory, File, SubprocessError, TmpDirectory


class Revert(Command):

    """Command class to remove files from the current patch
    """

    file_reverted = Signal()
    file_unchanged = Signal()

    def __init__(self, cwd, quilt_pc, quilt_patches):
        super(Revert, self).__init__(cwd)
        self.quilt_pc = Directory(quilt_pc)
        self.quilt_patches = Directory(quilt_patches)
        self.db = Db(quilt_pc)
        self.series = Series(quilt_patches)

    def _file_in_patch(self, filename, patch):
        """ Checks if a backup file of the filename in the current patch
        exists and raises a QuiltError if not.
        """
        pc_dir = self.quilt_pc + patch.get_name()
        file = pc_dir + File(filename)
        if not file.exists():
            raise QuiltError("File %s is not in patch %s" % (filename,
                             patch.get_name()))

    def _file_in_next_patches(self, filename, patch):
        """ Checks if a backup file of the filename in the applied patches after
        patch exists """

        if not self.db.is_patch(patch):
            # no patches applied
            return

        patches = self.db.patches_after(patch)
        for patch in patches:
            file = self.quilt_pc + File(os.path.join(patch.get_name(),
                                                     filename))
            if file.exists():
                raise QuiltError("File %s is modified by patch %s" %
                                 (filename, patch.get_name()))

    def _apply_patch_temporary(self, tmpdir, file, patch):
        backup = Backup()
        backup_file = backup.backup_file(file, tmpdir)
        patch_file = self.quilt_patches + File(patch.get_name())

        if patch_file.exists() and not patch_file.is_empty():
            try:
                patch.run(self.cwd, self.quilt_patches.get_absdir(),
                          work_dir=tmpdir, no_backup_if_mismatch=True,
                          remove_empty_files=True, force=True,
                          quiet=True, suppress_output=True,
                )
            except SubprocessError:
                pass  # Expected to fail if there are other files in patch
        return backup_file

    def revert_file(self, filename, patch_name=None):
        """ Revert not added changes of filename.
        If patch_name is None or empty the topmost patch will be used.
        """
        file = File(filename)

        if patch_name:
            patch = Patch(patch_name)
        else:
            patch = self.db.top_patch()

            if not patch:
                raise QuiltError("No patch available. Nothing to revert.")

        self._file_in_patch(filename, patch)
        self._file_in_next_patches(filename, patch)
        pc_dir = self.quilt_pc + patch.get_name()
        pc_file = pc_dir + file

        if not file.exists() and pc_file.is_empty():
            # new and empty file will be reverted
            pc_file.delete()
            self.file_reverted(file, patch)
            return

        with TmpDirectory(prefix="pquilt-") as tmpdir:
            # apply current patch in temporary directory to revert changes of
            # file that aren't committed in the patch
            tmp_file = self._apply_patch_temporary(tmpdir, pc_file, patch)
            if tmp_file and tmp_file.exists() and not tmp_file.is_empty():

                diff = Diff(file, tmp_file)
                if diff.equal(self.cwd):
                    self.file_unchanged(file, patch)
                    return

                dir = file.get_directory()
                if not dir:
                    dir = Directory(os.getcwd())
                else:
                    dir.create()
                tmp_file.copy(dir)
                self.file_reverted(file, patch)
            else:
                self.file_unchanged(file, patch)

    def revert_files(self, filenames, patch_name=None):
        for filename in filenames:
            self.revert_file(filename, patch_name)
