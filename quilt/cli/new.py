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
import os.path

from optparse import OptionParser

from quilt.db import Series, Db
from quilt.patch import Patch
from quilt.utils import File, Directory

from quilt.cli.meta import Command

class NewCommand(Command):

    min_args = 1
    usage = "%prog new patchname"
    name = "new"

    def run(self, options, args):
        newpatch = args[0]

        series = Series(self.get_patches_dir())
        if series.is_patch(Patch(newpatch)):
            print >> sys.stderr, "Patch %s already exists" % newpatch
            sys.exit(1)

        patch_dir = Directory(self.get_patches_dir())
        patch_dir.create()
        patchfile = patch_dir + File(newpatch)
        patchfile.touch()

        db = Db(self.get_pc_dir())
        if not db.exists():
            db.create()

        pc_dir = Directory(os.path.join(self.get_pc_dir(), newpatch))
        if pc_dir.exists():
            # be sure that the directory is clear
            pc_dir.delete()
        pc_dir.create()

        top = db.top_patch()
        series.add_patches([Patch(newpatch)], top)
        series.save()
