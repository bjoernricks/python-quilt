# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os

from quilt.cli.meta import Command
from quilt.cli.parser import Argument, OptionArgument
from quilt.patchimport import Import


class PatchImportCommand(Command):

    name = "import"
    help = "Import external patches."

    patchname = OptionArgument("-P", metavar="NAME", dest="patchname",
                               help="Import patch as NAME. This option can "
                               "only be used when importing a single patch.")
    patchfile = Argument(nargs="+")

    def run(self, args):
        importp = Import(os.getcwd(), self.get_pc_dir(),
                         self.get_patches_dir())

        if args.patchname:
            if len(args.patchfile) > 1:
                self.exit_error("It's only possible to rename a patch if one "
                                "patch will be imported.")
            importp.import_patch(args.patchfile[0], args.patchname)
        else:
            importp.import_patches(args.patchfile)
