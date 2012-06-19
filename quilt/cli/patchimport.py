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

from optparse import OptionParser

from quilt.error import QuiltError
from quilt.patchimport import Import

def parse(args):
    usage = "%prog import"
    parser = OptionParser(usage=usage)
    parser.add_option("-P", metavar="NAME", help="Import patch as NAME. This " \
                      "option can only be used when importing a single patch.",
                      dest="patchname")
    (options, pargs) = parser.parse_args(args)

    patches = os.environ.get("QUILT_PATCHES")
    if not patches:
        patches = "patches"

    if len(pargs) < 1:
        raise QuiltError("No patch is specified to be imported")

    importp = Import(os.getcwd(), ".pc", patches)

    if options.patchname:
        if len(pargs) > 1:
            raise QuiltError("It's only possible to rename a patch if one "
                             "patch will be imported.")
        importp.import_patch(pargs[0], options.patchname)
    else:
        importp.import_patches(pargs)
