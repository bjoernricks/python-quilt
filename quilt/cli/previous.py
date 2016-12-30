# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.cli.meta import Command
from quilt.db import Series, Db
from quilt.patch import Patch

class PreviousCommand(Command):

    usage = "%prog previous [patchname]"
    name = "previous"

    def run(self, options, args):
        series = Series(self.get_patches_dir())
        db = Db(self.get_pc_dir())

        top = None
        if len(args) > 0:
            top = Patch(args[0])
        else:
            if db.exists():
                top = db.top_patch()

        if not top:
            self.exit_error("No patches applied.")
        else:
            patch = series.patch_before(top)
            if not patch:
                self.exit_error("No patch available before %s." % top)
            else:
                print(patch)
