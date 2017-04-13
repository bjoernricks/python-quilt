# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.cli.meta import Command
from quilt.error import NoAppliedPatch


class AppliedCommand(Command):

    name = "applied"
    help = "Print all applied patches."

    def run(self, args):
        db = self.get_db()

        if not db.top_patch():
            raise NoAppliedPatch(db)

        for patch in db.applied_patches():
            print(patch)
