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
    usage = "%prog previous [patchname]"
    parser = OptionParser(usage=usage)
    (options, pargs) = parser.parse_args(args)

    patches = os.environ.get("QUILT_PATCHES")
    if not patches:
        patches = "patches"

    series = Series(patches)
    db = Db(".pc")

    top = None
    if len(pargs) == 1:
        top = Patch(args[0])
    else:
        if db.exists():
            top = db.top_patch()

    if not top:
        top = series.first_patch()
        if not top:
            print >> sys.stderr, "No patch in series."
            sys.exit(1)
        else:
            print top
    else:
        patch = series.patch_before(top)
        if not patch:
            print >> sys.stderr, "No patch available after %s." % patch
            sys.exit(1)
        else:
            print patch
