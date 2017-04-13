# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os

from quilt.cli.meta import Command
from quilt.cli.parser import Argument, OptionArgument
from quilt.pop import Pop


class PopCommand(Command):

    name = "pop"
    help = "Remove patch(es) from the stack of applied patches."

    all = OptionArgument("-a", "--all", dest="all", action="store_true",
                         help="remove all applied patches")

    patch = Argument(nargs="?")

    def run(self, args):
        pop = Pop(os.getcwd(), self.get_pc_dir())
        pop.unapplying.connect(self.unapplying)
        pop.unapplied.connect(self.unapplied)
        pop.empty_patch.connect(self.empty_patch)

        if args.all:
            pop.unapply_all()
        elif args.patch:
            pop.unapply_patch(args.patch)
        else:
            pop.unapply_top_patch()

    def unapplying(self, patch):
        print("Removing patch %s" % patch.get_name())

    def unapplied(self, patch):
        if not patch:
            print("No patches applied")
        else:
            print("Now at patch %s" % patch.get_name())

    def empty_patch(self, patch):
        print("Patch %s appears to be empty, removing" % patch.get_name())
