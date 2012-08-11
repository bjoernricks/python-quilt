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

import sys

from quilt.cli.meta import Command
from quilt.db import Db, Series
from quilt.patch import Patch
from quilt.utils import File, Directory

class NextCommand(Command):

    usage = "%prog next [patchname]"
    name = "next"

    def run(self, options, args):
        patch_name = args[0]

        series = Series(self.get_patches_dir())
        if not series.exists():
            self.exit_error("No series file found.")

        db = Db(self.get_pc_dir())

        top = None
        if len(args) == 1:
            top = Patch(patch_name)
        else:
            if db.exists():
                top = db.top_patch()

        if not top:
            top = series.first_patch()
            if not top:
                self.exit_error("No patch in series.")
            else:
                print top
        else:
            patch = series.patch_after(top)
            if not patch:
                self.exit_error("No patch available after %s." % patch_name)
            else:
                print patch
