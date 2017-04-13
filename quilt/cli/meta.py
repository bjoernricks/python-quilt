# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from __future__ import print_function

import os
import six
import sys

import quilt

from quilt.db import Db, Series

from quilt.cli.parser import Parser, SubParser, ArgumentsCollectorMetaClass, \
                             Argument

command_map = dict()


def register_command(name, command_class):
    command_map[name] = command_class


def find_command(name):
    return command_map.get(name, None)


def list_commands():
    return sorted(command_map.items())


class CommandMetaClass(ArgumentsCollectorMetaClass):

    def __new__(meta, name, bases, attrs):
        cls = super(CommandMetaClass, meta).__new__(meta, name, bases, attrs)
        if cls.name is not None:
            register_command(cls.name, cls)
        return cls


@six.add_metaclass(CommandMetaClass)
class Command(SubParser):

    name = None
    help = None
    description = None

    def __init__(self):
        super(Command, self).__init__(self.name, help=self.help,
                                      description=self.description or
                                      self.help)
        self.patches_dir = "patches"
        self.pc_dir = ".pc"

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

    def get_defaults(self):
        return {"run": self.run}

    def run(options, args):
        raise NotImplementedError()


class QuiltCli(Parser):

    default_subparsers_kwargs = {
        "title": "list of commands",
        "dest": "command",
        "description": "List of available commands. Use %(prog)s COMMAND "
                       "--help for more info.",
        "help": "Description",
        "metavar": "COMMAND",
    }

    version = Argument("--version", action="version",
                       version="%%(prog)s %s" % quilt.__version__)

    def __init__(self, *args, **kwargs):
        super(QuiltCli, self).__init__(*args, **kwargs)

        for cmd in list_commands():
            self.add_subparser(cmd[1]())

    def run(self):
        args = self.parse_args()
        if args.command:
            args.run(args)
        else:
            self.print_usage()
