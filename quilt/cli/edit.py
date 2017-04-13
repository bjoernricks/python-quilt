# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os

from quilt.add import Add
from quilt.cli.meta import Command
from quilt.cli.parser import Argument
from quilt.utils import SubprocessError, Process


class EditCommand(Command):

    name = "edit"
    help = "Edit the specified file(s) in $EDITOR after adding it (them) to " \
           "the topmost patch."

    file = Argument(nargs="+")

    def run(self, args):
        cwd = self.get_cwd()
        add = Add(cwd, self.get_pc_dir(), self.get_patches_dir())
        add.add_files(args.file, ignore=True)

        editor = os.environ.get("EDITOR", "vi")

        for filename in args.file:
            try:
                cmd = [editor, filename]
                Process(cmd).run(cwd=cwd)
            except SubprocessError as e:
                self.exit_error(e, value=e.returncode)
