# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.add import Add
from quilt.cli.meta import Command
from quilt.utils import SubprocessError, Process

class EditCommand(Command):

    usage = "%prog edit file1 [...]"
    name = "edit"
    min_args = 1

    def run(self, options, args):
        add = Add(self.get_cwd(), self.get_pc_dir(), self.get_patches_dir())
        add.add_files(args, ignore=True)

        editor = os.environ.get("EDITOR", "vi")

        for filename in args:
            try:
                cmd = [editor]
                cmd.append(filename)
                Process(cmd).run(cwd=cwd)
            except SubprocessError as e:
                self.exit_error(e, value=e.returncode)
