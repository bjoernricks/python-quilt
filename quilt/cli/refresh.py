# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os

from quilt.cli.meta import Command
from quilt.refresh import Refresh
from quilt.utils import SubprocessError, Process

class RefreshCommand(Command):

    usage = "%prog refresh [patch]"
    name = "refresh"

    def run(self, options, args):
        refresh = Refresh(os.getcwd(), self.get_pc_dir(),
                          self.get_patches_dir())

        refresh.refreshed.connect(self.refreshed)

        if options.edit:
            refresh.edit_patch.connect(self.edit_patch)

        patch_name = None
        if len(args) > 0:
            patch_name = args[0]

        refresh.refresh(patch_name, options.edit)

    def add_args(self, parser):
        parser.add_option("-e", "--edit", help="open patch in editor before " \
                          "refreshing", dest="edit", action="store_true",
                          default=False)

    def edit_patch(self, tmpfile):
        editor = os.environ.get("EDITOR", "vi")
        try:
            cmd = [editor]
            cmd.append(tmpfile.get_name())
            Process(cmd).run(cwd=os.getcwd())
        except SubprocessError as e:
            self.exit_error(e, value=e.returncode)

    def refreshed(self, patch):
        print("Patch %s refreshed" % patch.get_name())
