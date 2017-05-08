# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.cli.meta import Command
from quilt.cli.parser import OptionArgument
from quilt.db import Db, Series


class SeriesCommand(Command):

    name = "series"
    help = "Print the names of all patches in the series file."

    v = OptionArgument(action="store_true", help="""indicate applied (+)
        and topmost (=) patches""")

    def run(self, args):
        series = Series(self.get_patches_dir())
        if args.v:
            applied = Db(self.get_pc_dir()).patches()
            for patch in applied[:-1]:
                print("+ " + patch.get_name())
            if applied:
                print("= " + applied[-1].get_name())
                patches = series.patches_after(applied[-1])
            else:
                patches = series.patches()
            for patch in patches:
                print("  " + patch.get_name())
        else:
            for patch in series.patches():
                print(patch.get_name())
