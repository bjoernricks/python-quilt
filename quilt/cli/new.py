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

def parse(args):
    usage = "%prog new patchname"
    parser = OptionParser(usage=usage)
    (options, pargs) = parser.parse_args(args)

    if len(args) != 1:
        parser.print_usage()
        sys.exit(1)

    newpatch = args[0]

    patches = os.environ.get("QUILT_PATCHES")
    if not patches:
        patches = "patches"

    series = Series(patches)
    if series.is_patch(newpatch):
        print >> sys.stderr, "Patch %s already exists" % newpatch
        sys.exit(2)

    patch_dir = Directory(patches)
    patch_dir.create()
    patchfile = patch_dir + File(newpatch)
    patchfile.touch()

    db = Db(".pc")
    top = db.top_patch()
    series.add_patches([Patch(newpatch)], top)
    series.save()

