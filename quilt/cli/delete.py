# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012  Björn Ricks <bjoern.ricks@googlemail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

from quilt.cli.meta import Command
from quilt.delete import Delete

class DeleteCommand(Command):

    usage = "%prog delete [-r] [--backup] [patch|-n]"
    name  = "delete"

    def add_args(self, parser):
        parser.add_option("-r", help="Remove the deleted patch file from the " \
                                     "patches directory as well.",
                          action="store_true", dest="remove", default=False)
        parser.add_option("-n", help="Delete the next patch after topmost, " \
                                      "rather than the specified or topmost " \
                                      "patch.",
                          action="store_true", dest="next")
        parser.add_option("--backup", help="Rename the patch file to patch~ " \
                                      "rather than deleting it. Ignored if " \
                                      "not used with `-r'.",
                          action="store_true", default=False, dest="backup")

    def run(self, options, args):
        delete = Delete(self.get_cwd(), self.get_pc_dir(),
                        self.get_patches_dir())
        delete.deleted_patch.connect(self.deleted_patch)
        delete.deleting_patch.connect(self.deleting_patch)

        if options.next and len(args) > 0:
            parser.print_usage()
            sys.exit(1)

        if options.next:
            delete.delete_next(options.remove, options.remove)
        else:
            patch = None
            if len(args) > 0:
                patch = args[0]

            delete.delete_patch(patch, options.remove, options.remove)

    def deleted_patch(self, patch):
        print "Removed patch %s" % patch.get_name()

    def deleting_patch(self, patch, applied):
        if applied:
            print "Removing currently applied patch %s" % patch.get_name()
        else:
            print "Removing patch %s" % patch.get_name()
