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

import os
import sys

from optparse import OptionParser

from quilt.add import Add

def parse(args):
    usage = "%prog add [-p patch] file1 [...]"
    parser = OptionParser(usage=usage)
    parser.add_option("-p", help="patch to add files to",
                      metavar="PATCH", dest="patch")

    (options, pargs) = parser.parse_args(args)

    if len(args) != 1:
        parser.print_usage()
        sys.exit(1)

    patches = os.environ.get("QUILT_PATCHES")
    if not patches:
        patches = "patches"

    add = Add(os.getcwd(), ".pc", patches)
    add.add_files(pargs, options.patch)
