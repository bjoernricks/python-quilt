# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os

from quilt.cli.meta import Command
from quilt.cli.parser import Argument, OptionArgument
from quilt.revert import Revert


class RevertCommand(Command):

    name = "revert"
    help = "Revert  uncommitted  changes  to  the  topmost  or  named  " \
           "patch for the specified file(s)."

    patch = OptionArgument("-p", metavar="PATCH", dest="patch",
                           help="revert changes in the named patch")
    file = Argument(nargs="+")

    def run(self, args):
        revert = Revert(os.getcwd(), self.get_pc_dir(), self.get_patches_dir())
        revert.file_reverted.connect(self.file_reverted)
        revert.file_unchanged.connect(self.file_unchanged)
        revert.revert_files(args.file, args.patch)

    def file_reverted(self, file, patch):
        print("Changes to %s in patch %s reverted" % (file.get_name(),
                                                      patch.get_name()))

    def file_unchanged(self, file, patch):
        print("File %s is unchanged" % file.get_name())
