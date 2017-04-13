# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.cli.meta import QuiltCli, find_command, list_commands

import quilt.cli.add
import quilt.cli.applied
import quilt.cli.edit
import quilt.cli.delete
import quilt.cli.new
import quilt.cli.next
import quilt.cli.patchimport
import quilt.cli.pop
import quilt.cli.previous
import quilt.cli.push
import quilt.cli.refresh
import quilt.cli.revert
import quilt.cli.series
import quilt.cli.top
import quilt.cli.unapplied
