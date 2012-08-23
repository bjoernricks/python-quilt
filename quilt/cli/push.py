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
from quilt.push import Push

class PushCommand(Command):

    usage = "%prog push [-a] [patch]"
    name = "push"

    def add_args(self, parser):
        parser.add_option("-a", "--all", help="apply all patches in series",
                          action="store_true")
        parser.add_option("-f", "--force", help="Force apply, even if the " \
                                                "patch has rejects.",
                          action="store_true", default=False)

    def run(self, options, args):
        push = Push(self.get_cwd(), self.get_pc_dir(), self.get_patches_dir())
        push.applying_patch.connect(self.applying_patch)
        push.applied.connect(self.applied)
        push.applied_empty_patch.connect(self.applied_empty_patch)

        if options.all:
            push.apply_all(options.force)
        elif not args:
            push.apply_next_patch(options.force)
        else:
            push.apply_patch(args[0], options.force)

    def applying_patch(self, patch):
        print "Applying patch %s" % patch.get_name()

    def applied(self, patch):
        print "Now at patch %s" % patch.get_name()

    def applied_empty_patch(self, patch, exists):
        if exists:
            print "Patch %s appears to be empty; applied" % patch.get_name()
        else:
            print "Patch %s does not exist; applied empty patch" % \
                  patch.get_name()
