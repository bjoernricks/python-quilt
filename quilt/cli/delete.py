# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.cli.meta import Command
from quilt.cli.parser import Argument, OptionArgument
from quilt.delete import Delete


class DeleteCommand(Command):

    name = "delete"
    help = "Remove the specified or topmost patch from the series file."

    remove = OptionArgument("-r", action="store_true", dest="remove",
                            default=False,
                            help="Remove the deleted patch file from the "
                            "patches directory as well.")
    backup = OptionArgument("--backup",
                            action="store_true", default=False, dest="backup",
                            help="Rename the patch file to patch~ rather than "
                            "deleting it. Ignored if not used with `-r'.")
    next = OptionArgument("-n", action="store_true", dest="next",
                          help="Delete the next unapplied patch, "
                          "rather than the specified or topmost patch.")
    patch = Argument(nargs="?")

    def run(self, args):
        delete = Delete(self.get_cwd(), self.get_pc_dir(),
                        self.get_patches_dir())
        delete.deleted_patch.connect(self.deleted_patch)
        delete.deleting_patch.connect(self.deleting_patch)

        if args.next and args.patch:
            self.exit_error("-n parameter doesn't take an argument")

        if args.next:
            delete.delete_next(args.remove, args.backup)
        else:
            delete.delete_patch(args.patch, args.remove, args.backup)

    def deleted_patch(self, patch):
        print("Removed patch %s" % patch.get_name())

    def deleting_patch(self, patch, applied):
        if applied:
            print("Removing currently applied patch %s" % patch.get_name())
        else:
            print("Removing patch %s" % patch.get_name())
