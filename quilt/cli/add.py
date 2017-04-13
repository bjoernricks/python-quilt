# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os

from quilt.add import Add
from quilt.cli.meta import Command
from quilt.cli.parser import Argument, OptionArgument


class AddCommand(Command):

    name = "add"
    help = "Add one or more files to the topmost or named patch."

    patch = OptionArgument("-p", help="patch to add files to",
                           metavar="PATCH", dest="patch")
    file = Argument(nargs="+")

    def add_args(self, parser):
        parser.add_option("-p", help="patch to add files to",
                          metavar="PATCH", dest="patch")

    def run(self, args):
        add = Add(os.getcwd(), self.get_pc_dir(), self.get_patches_dir())
        add.file_added.connect(self.file_added)
        add.add_files(args.file, args.patch)

    def file_added(self, file, patch):
        print("File %s added to patch %s" %
              (file.get_name(), patch.get_name()))
