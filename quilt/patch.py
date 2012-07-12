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
import os.path

from quilt.utils import Process, Directory, File

class Patch(object):

    """ Wrapper arround the patch util """

    def __init__(self, patch_name, strip=1, reverse=False):
        self.patch_name = patch_name
        self.strip = strip
        self.reverse = reverse

    def run(self, cwd, backup=False, prefix=None, reverse=False):
        cmd = ["patch"]
        cmd.append("-p" + str(self.strip))
        if backup:
            cmd.append("--backup")
        if prefix:
            cmd.append("--prefix")
            if not prefix[-1] == os.sep:
                prefix += os.sep
            cmd.append(prefix)
        reverse = reverse != self.reverse
        if reverse:
            cmd.append("-R")
        cmd.append("-i")
        cmd.append(self.patch_file)
        Process(cmd).run(cwd=cwd)


class RollbackPatch(object):

    def __init__(self, cwd, backup_dir):
        self.cwd = Directory(cwd)
        self.backup_dir = Directory(backup_dir)

    def rollback(self, keep=False):
        (dirs, files) = self.backup_dir.content()

        for dir in dirs:
            newdir = self.cwd + dir
            if not newdir.exists():
                newdir.create()

        for file in files:
            file = File(file)
            backup_file = self.backup_dir + file
            rollback_file = self.cwd + file

            if not keep:
                rollback_file.delete_if_exists()
            if not backup_file.is_empty():
                backup_file.copy(rollback_file)

    def delete_backup(self):
        self.backup_dir.delete()
