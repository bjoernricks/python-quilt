# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.cli.meta import Command
from quilt.db import Series

class SeriesCommand(Command):

    usage = "%prog series"
    name = "series"

    def run(self, option, args):
        series = Series(self.get_patches_dir())
        for patch in series.patches():
            print(patch)
