# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012  Björn Ricks <bjoern.ricks@googlemail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

import os
import sys

from optparse import OptionParser

from quilt.db import Db, Series

command_map = dict()

def register_command(name, command_class):
    command_map[name] = command_class

def find_command(name):
    return command_map.get(name, None)

def list_commands():
    return sorted(command_map.items())


class CommandMetaClass(type):

    def __new__(meta, name, bases, dict):
        cls = type.__new__(meta, name, bases, dict)
        if cls.name is not None:
            register_command(cls.name, cls)
        return cls


class Command(object):

    __metaclass__ = CommandMetaClass

    min_args = 0
    usage = ""
    patches_dir = "patches"
    pc_dir = ".pc"
    name = None

    def parse(self, args):
        parser = OptionParser(usage=self.usage)

        self.add_args(parser)

        (options, pargs) = parser.parse_args(args)

        if len(pargs) < self.min_args:
            parser.print_usage()
            sys.exit(1)

        self.run(options, pargs)

    def run(self, options, args):
        raise NotImplementedError()

    def add_args(self, parser):
        pass

    def get_patches_dir(self):
        patches_dir = os.environ.get("QUILT_PATCHES")
        if not patches_dir:
            patches_dir = self.patches_dir
        return patches_dir

    def get_pc_dir(self):
        pc_dir = os.environ.get("QUILT_PC")
        if not pc_dir:
            pc_dir = self.pc_dir
        return pc_dir

    def get_db(self):
        return Db(self.get_pc_dir())

    def get_series(self):
        return Series(self.get_patches_dir())

    def exit_error(self, error, value=1):
        print >> sys.stderr, error
        sys.exit(value)
