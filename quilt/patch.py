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

    def __init__(self, cwd, patch_file, strip=1, backup=False, prefix=None):
        cmd = ["patch"]
        cmd.append("-p" + str(strip))
        if backup:
            cmd.append("--backup")
        if prefix:
            cmd.append("--prefix")
            if not prefix[-1] == os.sep:
                prefix += os.sep
            cmd.append(prefix)
        cmd.append("-i")
        cmd.append(patch_file)

        Process(cmd).run(cwd=cwd)


class RollbackPatch(object):

    def __init__(self, cwd, backup_dir):
        self.cwd = Directory(cwd)
        self.backup_dir = Directory(backup_dir)
        (dirs, files) = self.backup_dir.content()

        for dir in dirs:
            newdir = self.cwd + dir
            if not newdir.exists():
                newdir.create()

        for file in files:
            file = File(file)
            backup_file = self.backup_dir + file
            rollback_file = self.cwd + file
            if rollback_file.exists():
                rollback_file.delete()
            backup_file.link(rollback_file)
