# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os.path
import stat

from quilt.backup import Backup
from quilt.command import Command
from quilt.db import Db, Series
from quilt.error import QuiltError, NoAppliedPatch
from quilt.signals import Signal
from quilt.utils import Directory, File


class Add(Command):

    """Command class to add files to the current patch
    """

    file_added = Signal()

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
            # no patches applied
            return

        patches = self.db.patches_after(patch)
        for patch in patches:
            file = self.quilt_pc + File(os.path.join(patch.get_name(),
                                                     filename))
            if file.exists():
                raise QuiltError("File %s is already modified by patch %s" %
                                 (filename, patch.get_name()))

    def _backup_file(self, file, patch):
        """ Creates a backup of file """
        dest_dir = self.quilt_pc + patch.get_name()
        file_dir = file.get_directory()
        if file_dir:
            #TODO get relative path
            dest_dir = dest_dir + file_dir
        backup = Backup()
        backup.backup_file(file, dest_dir, copy_empty=True)

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
                raise NoAppliedPatch(self.db)

        exists = self._file_in_patch(filename, patch, ignore)
        if exists:
            return

        self._file_in_next_patches(filename, patch)

        if file.is_link():
            raise QuiltError("Cannot add symbolic link %s" % filename)

        self._backup_file(file, patch)

        if file.exists():
            # be sure user can write original file
            os.chmod(filename, file.get_mode() | stat.S_IWUSR | stat.S_IRUSR)

        self.file_added(file, patch)

    def add_files(self, filenames, patch_name=None, ignore=False):
        for filename in filenames:
            self.add_file(filename, patch_name, ignore)
