# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os

from quilt.cli.meta import Command
from quilt.pop import Pop

class PopCommand(Command):

    usage = "%prog pop [-a] [patch]"
    name = "pop"

    def add_args(self, parser):
        parser.add_option("-a", "--all", help="remove all applied patches",
                        action="store_true")

    def run(self, options, args):
        pop = Pop(os.getcwd(), self.get_pc_dir())
        pop.unapplying.connect(self.unapplying)
        pop.unapplied.connect(self.unapplied)
        pop.empty_patch.connect(self.empty_patch)

        if options.all:
            pop.unapply_all()
        elif not args:
            pop.unapply_top_patch()
        else:
            pop.unapply_patch(args[0])

    def unapplying(self, patch):
        print("Removing patch %s" % patch.get_name())

    def unapplied(self, patch):
        if not patch:
            print("No patches applied")
        else:
            print("Now at patch %s" % patch.get_name())

    def empty_patch(self, patch):
        print("Patch %s appears to be empty, removing" % patch.get_name())
