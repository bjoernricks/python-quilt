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

from quilt.utils import Directory, File

class Backup(object):

    """ Class to backup files

    This class should be exented in future to support all functions of quilts
    backup-files script.
    """

    def backup_file(self, filename, dest_dir, copy_empty=False):
        file = File(self.filename)
        if file.exists():
            if not copy_empty and file.is_empty():
                return
            if not isinstance(dest_dir, Directory):
                dest_dir = Directory(dest_dir)
            dest_dir.create()
            file.copy(dest_dir)
        else:
            dest_dir = dest_dir + file.get_directory()
            dest_dir.create()
            dest_file = dest_dir + file
            dest_file.touch()

