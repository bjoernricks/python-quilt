# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012  Björn Ricks <bjoern.ricks@gmail.com>
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

import os

from quilt.cli.meta import Command
from quilt.refresh import Refresh
from quilt.utils import SubprocessError, Process

class RefreshCommand(Command):

    usage = "%prog refresh [patch]"
    name = "refresh"

    def run(self, options, args):
        refresh = Refresh(os.getcwd(), self.get_pc_dir(),
                          self.get_patches_dir())

        refresh.refreshed.connect(self.refreshed)

        if options.edit:
            refresh.edit_patch.connect(self.edit_patch)

        patch_name = None
        if len(args) > 0:
            patch_name = args[0]

        refresh.refresh(patch_name, options.edit)

    def add_args(self, parser):
        parser.add_option("-e", "--edit", help="open patch in editor before " \
                          "refreshing", dest="edit", action="store_true",
                          default=False)

    def edit_patch(self, tmpfile):
        editor = os.environ.get("EDITOR", "vi")
        try:
            cmd = [editor]
            cmd.append(tmpfile.get_name())
            Process(cmd).run(cwd=os.getcwd())
        except SubprocessError, e:
            self.exit_error(e, value=e.returncode)

    def refreshed(self, patch):
        print "Patch %s refreshed" % patch.get_name()
