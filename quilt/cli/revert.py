# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os

from quilt.revert import Revert
from quilt.cli.meta import Command

class RevertCommand(Command):

    usage = "%prog revert [-p patch] file1 [...]"
    name = "revert"
    min_args = 1

    def add_args(self, parser):
        parser.add_option("-p", help="revert changes in the named patch",
                          metavar="PATCH", dest="patch")

    def run(self, options, args):
        revert = Revert(os.getcwd(), self.get_pc_dir(), self.get_patches_dir())
        revert.file_reverted.connect(self.file_reverted)
        revert.file_unchanged.connect(self.file_unchanged)
        revert.revert_files(args, options.patch)

    def file_reverted(self, file, patch):
        print("Changes to %s in patch %s reverted" % (file.get_name(),
                                                      patch.get_name()))
    def file_unchanged(self, file, patch):
        print("File %s is unchanged" % file.get_name())
