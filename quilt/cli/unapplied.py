# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.cli.meta import Command
from quilt.db import Db, Series


class UnappliedCommand(Command):

    name = "unapplied"
    help = "Print list of unapplied patches."

    def run(self, args):
        db = Db(self.get_pc_dir())
        top = db.top_patch()
        series = Series(self.get_patches_dir())
        if top is None:
            patches = series.patches()
        else:
            patches = series.patches_after(top)
        for patch in patches:
            print(patch)
