# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2013 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

"""
This module contains classes to parse arguments from a command line
interface

Example:

    class MySubParser(SubParser):
        all = OptionArgument("-a")
        none = OptionArgument()

        group = ArgumentGroup(title="TGroup", argument_names=["none", "all"])

    class MySubSubParser(SubParser):
        new = OptionArgument()

    class MyParser(Parser):

        group1 = ArgumentGroup(title="MyGroup", argument_names=["abc"])

        abc = OptionArgument(type=int)
        hij = OptionArgument("--old")

    mysubparser = MySubParser("cmd1", help="my cmd1")
    mysubsubparser = MySubSubParser("sub1", help="subsub1")
    mysubparser.add_subparser(mysubsubparser)
    myparser = MyParser()
    myparser.add_subparser(mysubparser)
    print(myparser.parse_args())
"""

import argparse
import copy

import six


def get_declared_instances_list(bases, attrs, collect_cls, instance_attr):
    instances = [(name, attrs.pop(name)) for name, obj in attrs.copy().items()
                 if isinstance(obj, collect_cls)]
    instances.sort(key=lambda x: x[1].creation_counter)
    for base in bases[::-1]:
        if hasattr(base, instance_attr):
            instances = getattr(base, instance_attr) + instances
    return instances


def get_declared_instances_dict(bases, attrs, collect_cls, instance_attr):
    instances = {}
    for name, obj in attrs.copy().items():
        if isinstance(obj, collect_cls):
            instances[name] = attrs.pop(name)
    for base in bases[::-1]:
        if hasattr(base, instance_attr):
            instances.update(getattr(base, instance_attr))
    return instances


def get_first_declared_instance(bases, attrs, collect_cls, instance_attr):
    for name, obj in attrs.copy().items():
        if isinstance(obj, collect_cls):
            return name, attrs.pop(name)
    for base in bases[::-1]:
        if hasattr(base, instance_attr):
            return getattr(base, instance_attr)
    return None


class ArgumentsCollectorMetaClass(type):

    """ MetaClass to collect defined arguments and groups """

    def __new__(cls, name, bases, attrs):
        """
        Collects all Argument and Group instances and sets them as
        base_arguments respectively base_argument_groups in the new created
        class. Arguments mentioned in the Group instances will be not added to
        base_arguments.
        """
        arguments = get_declared_instances_dict(bases, attrs, Argument,
                                                "base_arguments")
        groups = get_declared_instances_list(bases, attrs, ArgumentGroup,
                                             "base_argument_groups")
        subparsers = get_declared_instances_dict(bases, attrs, BaseSubParser,
                                                 "base_subparsers")
        sgroup = get_first_declared_instance(bases, attrs, SubParserGroup,
                                             "subparser_group")
        new_class = super(ArgumentsCollectorMetaClass, cls).__new__(
            cls, name, bases, attrs)

        if groups:
            for name, group in groups:
                group.set_name(name)
                for arg_name in group.argument_names:
                    arg = arguments.pop(arg_name)
                    arg.set_name(arg_name)
                    group.add_argument(arg)
        new_class.base_argument_groups = groups

        if not sgroup and subparsers:
            sgroup = None, SubParserGroup(subparser_names=[key for key in
                                                           subparsers.keys()])

        if sgroup:
            name, group = sgroup
            group.set_name(name)
            for sname in group.subparser_names:
                sparser = subparsers.pop(sname)
                sparser.set_name(sname)
                group.add_subparser(sparser)
            new_class.subparser_group = group

        args = []
        if arguments:
            for name, arg in arguments.items():
                arg.set_name(name)
                args.append((name, arg))

        args.sort(key=lambda x: x[1].creation_counter)
        new_class.base_arguments = args

        new_class.base_subparsers = subparsers

        return new_class


class ArgumentGroup(object):

    """
    A class to declare argument groups at a class

    Usage:
        class MyParser(Parser):
            cmd1 = OptionalArgument()
            cmd2 = OptionalArgument()

            group = ArgumentGroup(title="group of possible commands",
                                  argument_names=["cmd1", "cmd2"])
    """

    creation_counter = 0

    def __init__(self, title=None, description=None, argument_names=None):
        """
        Constructs a ArgumentGroup instance

        @param title The title of the group displayed as headline
        @param description A detailed description of the argument group
        @param argument_names A list of strings containing the Arguments to be
                              grouped
        """
        self.title = title
        self.description = description
        self.argument_names = argument_names or []
        self.arguments = []
        self.creation_counter = ArgumentGroup.creation_counter
        ArgumentGroup.creation_counter += 1

    def add_to_parser(self, parser):
        """
        Adds the group and its arguments to a argparse.ArgumentParser instance

        @param parser A argparse.ArgumentParser instance
        """
        self.group = parser.add_argument_group(self.title, self.description)
        for arg in self.arguments:
            arg.add_to_parser(self.group)

    def set_name(self, name):
        """
        Sets the name of this group. Normally this method should not be called
        directly. It is used by the ArgumentsCollectorMetaClass.

        @param name A string for a name
        """
        self.name = name

    def add_argument(self, arg):
        """
        Adds a Argument to this group.
        Normally this method should not be called directly.
        It is used by the ArgumentsCollectorMetaClass.

        @parma arg An Argument instance to be added to this group.
        """
        self.arguments.append(arg)


class SubParserGroup(object):

    """
    A class to add subparsers to a parser in a declerative fashion
    """

    creation_counter = 0

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.creation_counter = Argument.creation_counter
        self.subparser_names = kwargs.pop("subparser_names", None) or []
        self.subparsers = []
        Argument.creation_counter += 1

    def _get_kwargs(self):
        kwargs = {}

        if self.name is not None:
            kwargs["dest"] = self.name

        kwargs.update(self.kwargs)
        return kwargs

    def _get_args(self):
        return self.args

    def set_name(self, name):
        """
        Sets the name of this SubParser

        Normally this method should not be called directly.
        It is used by the ArgumentsCollectorMetaClass.

        :param name A string for a name
        """
        self.name = name

    def add_subparser(self, parser):
        """
        Adds a SubParser to this group
        Normally this method should not be called directly.
        It is used by the ArgumentsCollectorMetaClass.

        :param arg An Argument instance to be added to this group.
        """
        self.subparsers.append(parser)

    def add_to_parser(self, parser):
        parser.set_subparsers_args(*self._get_args(), **self._get_kwargs())
        for sparser in self.subparsers:
            parser.add_subparser(sparser)


class Argument(object):

    """
    A class to declare positional arguments at a class

    Usage:
        class MyParser(Parser):

            arg1 = Argument(help="A first string argument")
            arg2 = Argument(type=int)
            arg3 = Argument(nargs=2)
    """

    creation_counter = 0

    def __init__(self, *args, **kwargs):
        """
        Constructs an Argument instance

        args and kwargs are passed directly to
        argparse.ArgumentParser.add_argument
        """
        self.args = args
        self.kwargs = kwargs
        self.creation_counter = Argument.creation_counter
        Argument.creation_counter += 1

    def _get_kwargs(self):
        if self.args:
            return self.kwargs

        kwargs = {"dest": self.name}
        kwargs.update(self.kwargs)
        return kwargs

    def _get_args(self):
        return self.args

    def add_to_parser(self, parser):
        """
        Adds the argument to an argparse.ArgumentParser instance

        @param parser An argparse.ArgumentParser instance
        """
        kwargs = self._get_kwargs()
        args = self._get_args()
        parser.add_argument(*args, **kwargs)

    def set_name(self, name):
        """
        Sets the name of this Argument.
        Normally this method should not be called directly.
        It is used by the ArgumentsCollectorMetaClass.

        @param name A string for a name
        """
        self.name = name


class OptionArgument(Argument):

    """
    A class to declare (optional) arguments at a class

    Usage:
        class MyParser(Parser):

            arg1 = OptionArgument(help="A first string argument")
            arg2 = OptionArgument(type=int)
            arg3 = OptionArgument(nargs=2)
            arg4 = OptionArgument(required=True)
    
    By default, the option name is taken from the attribute name and prefixed
    with two dashes, or one dash if the name is a single character:
    
    verbose = OptionArgument(action="store_true")  # usage: [--verbose]
    v = OptionArgument(action="store_true")  # usage: [-v]
    """

    prefix_chars = "--"

    def _get_args(self):
        args = self.args
        if not args:
            if self.prefix_chars == "--" and len(self.name) == 1:
                args = ("-" + self.name,)
            else:
                args = (self.prefix_chars + self.name,)
        return args


class BaseSubParser(object):

    def __init__(self, *args, **kwargs):
        super(BaseSubParser, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.name = None
        self.defaults = {}

    def set_name(self, name):
        """
        Sets the name of this Subparse.
        Normally this method should not be called directly.
        It is used by the ArgumentsCollectorMetaClass.

        :param name A string for a name
        """
        self.name = name

    def _get_kwargs(self):
        return self.kwargs

    def _get_args(self):
        if self.name:
            return (self.name,) + self.args
        return self.args

    def get_defaults(self):
        return self.defaults

    def add_to_parser(self, subparsers):
        """
        Adds this SubParser to the subparsers created by
        argparse.ArgumentParser.add_subparsers method.

        @param subparsers Normally a _SubParsersAction instance created by
        argparse.ArgumentParser.add_subparsers method
        """
        parser = subparsers.add_parser(*self._get_args(), **self._get_kwargs())
        parser.set_defaults(**self.get_defaults())
        for name, group in self.base_argument_groups:
            group.add_to_parser(parser)
        for name, arg in self.base_arguments:
            arg.add_to_parser(parser)
        self.add_subparsers(parser)


class SubParsersMixin(object):

    """
    A mixin class intended to add subparsers to parser
    """

    default_subparsers_kwargs = {
        "title": "list of commands",
    }

    default_subparsers_args = []

    def __init__(self, *args, **kwargs):
        self.subparsers = []
        self.subparsers_args = []
        self.subparsers_kwargs = {}
        self.default_subparsers_kwargs = copy.copy(
            self.default_subparsers_kwargs)
        self.default_subparsers_args = copy.copy(
            self.default_subparsers_args)
        super(SubParsersMixin, self).__init__(*args, **kwargs)

    def set_subparsers_args(self, *args, **kwargs):
        """
        Sets args and kwargs that are passed when creating a subparsers group
        in an argparse.ArgumentParser i.e. when calling
        argparser.ArgumentParser.add_subparsers
        """
        self.subparsers_args = args
        self.subparsers_kwargs = kwargs

    def add_subparser(self, parser):
        """
        Adds a SubParser instance to the list of subparsers

        @param parser A SubParser instance
        """
        self.subparsers.append(parser)

    def get_default_subparsers_kwargs(self):
        """
        Returns the default kwargs to be passed to
        argparse.ArgumentParser.add_subparsers
        """
        return self.default_subparsers_kwargs

    def get_default_subparsers_args(self):
        """
        Returns the default args to be passed to
        argparse.ArgumentParser.add_subparsers
        """
        return self.default_subparsers_args

    def add_subparsers(self, parser):
        """
        Adds the subparsers to an argparse.ArgumentParser

        @param parser An argparse.ArgumentParser instance
        """
        sgroup = getattr(self, "subparser_group", None)
        if sgroup:
            sgroup.add_to_parser(self)

        if not self.subparsers:
            return

        args = self.subparsers_args or self.get_default_subparsers_args()
        kwargs = self.subparsers_kwargs or self.get_default_subparsers_kwargs()
        subs = parser.add_subparsers(*args, **kwargs)

        for subparser in self.subparsers:
            subparser.add_to_parser(subs)


@six.add_metaclass(ArgumentsCollectorMetaClass)
class Parser(SubParsersMixin):

    """
    Main class to create cli parser

    Most of the time your parser should be directly be derived from this class.
    """

    def __init__(self, *args, **kwargs):
        super(Parser, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def create_argparser(self):
        """
        Method to create and initalize an argparser.ArgumentParser
        """
        parser = argparse.ArgumentParser(*self.args, **self.kwargs)
        for name, group in self.base_argument_groups:
            group.add_to_parser(parser)
        for name, arg in self.base_arguments:
            arg.add_to_parser(parser)
        self.add_subparsers(parser)
        self.parser = parser

    def parse_args(self, *args, **kwargs):
        self.create_argparser()
        return self.parser.parse_args(*args, **kwargs)

    def parse_known_args(self, *args, **kwargs):
        self.create_argparser()
        return self.parser.parse_known_args(*args, **kwargs)

    def print_usage(self, *args, **kwargs):
        self.create_argparser()
        self.parser.print_usage(*args, **kwargs)

    def print_version(self, *args, **kwargs):
        self.create_argparser()
        self.parser.print_version(*args, **kwargs)

    def print_help(self, *args, **kwargs):
        self.create_argparser()
        self.parser.print_help(*args, **kwargs)


@six.add_metaclass(ArgumentsCollectorMetaClass)
class SubParser(SubParsersMixin, BaseSubParser):

    """
    A subparser class

    Usage:
        Cmd1Parser(SubParser):
            optarg1 = OptionalArgument()

        MyParser(Parser):
            arg1 = Argument("name")

        parser = MyParser()
        parser.add_subparser(Cmd1Parser("cmd1", help="my cmd1"))
    """
