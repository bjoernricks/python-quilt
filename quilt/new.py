# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

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

        The new patch will be added as the topmost applied patch.
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

        # create empty .pc/<patchname> directory as quilt does too
        pc_dir.create()

        top = self.db.top_patch()
        # add new patch after the current topmost applied patch
        self.series.add_patches([patch], top)
        # "apply" patch
        self.db.add_patch(patch)

        # create patches/series files
        self.series.save()
        # create .pc/.version and .pc/applied-patches files
        self.db.save()

        self.patch_created(patch)
