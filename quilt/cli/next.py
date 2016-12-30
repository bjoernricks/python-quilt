# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.cli.meta import Command
from quilt.db import Db, Series
from quilt.patch import Patch

class NextCommand(Command):

    usage = "%prog next [patchname]"
    name = "next"

    def run(self, options, args):
        series = Series(self.get_patches_dir())
        if not series.exists():
            self.exit_error("No series file found.")

        db = Db(self.get_pc_dir())

        top = None
        if len(args) == 1:
            patch_name = args[0]
            top = Patch(patch_name)
        else:
            if db.exists():
                top = db.top_patch()

        if not top:
            top = series.first_patch()
            if not top:
                self.exit_error("No patch in series.")
            else:
                print(top)
        else:
            patch = series.patch_after(top)
            if not patch:
                self.exit_error("No patch available after %s." % top)
            else:
                print(patch)
