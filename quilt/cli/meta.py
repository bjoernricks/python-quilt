# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from __future__ import print_function

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

    def get_cwd(self):
        return os.getcwd()

    def exit_error(self, error, value=1):
        print(error, file=sys.stderr)
        sys.exit(value)
