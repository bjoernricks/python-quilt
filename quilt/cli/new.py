# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import sys
import os.path

from optparse import OptionParser

from quilt.cli.meta import Command
from quilt.error import PatchAlreadyExists
from quilt.new import New

class NewCommand(Command):

    min_args = 1
    usage = "%prog new patchname"
    name = "new"

    def run(self, options, args):
        newpatch = args[0]

        new = New(self.get_cwd(), self.get_pc_dir(), self.get_patches_dir())
        try:
            new.create(newpatch)
        except PatchAlreadyExists as e:
            print(e)
