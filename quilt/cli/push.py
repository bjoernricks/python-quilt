# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.cli.meta import Command
from quilt.cli.parser import Argument, OptionArgument
from quilt.push import Push


class PushCommand(Command):

    name = "push"
    help = " Apply  patch(es)  from the series file."

    all = OptionArgument("-a", dest="all", action="store_true",
                         help="apply all patches in series")
    force = OptionArgument("-f", dest="force", action="store_true",
                           default=False,
                           help="Force apply, even if the patch has rejects.")
    patch = Argument(nargs="?")

    def run(self, args):
        push = Push(self.get_cwd(), self.get_pc_dir(), self.get_patches_dir())
        push.applying_patch.connect(self.applying_patch)
        push.applied.connect(self.applied)
        push.applied_empty_patch.connect(self.applied_empty_patch)

        if args.all:
            push.apply_all(args.force)
        elif args.patch:
            push.apply_patch(args.patch, args.force)
        else:
            push.apply_next_patch(args.force)

    def applying_patch(self, patch):
        print("Applying patch %s" % patch.get_name())

    def applied(self, patch):
        print("Now at patch %s" % patch.get_name())

    def applied_empty_patch(self, patch, exists):
        if exists:
            print("Patch %s appears to be empty; applied" % patch.get_name())
        else:
            print("Patch %s does not exist; applied empty patch" %
                  patch.get_name())
