# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.cli.meta import Command
from quilt.db import Db

class TopCommand(Command):

    usage = "%prog top"
    name = "top"

    def run(self, options, args):
        db = Db(self.get_pc_dir())
        top = db.top_patch()
        if not top:
            self.exit_error("No patches applied.")

        print(top)
