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

import os.path

from quilt.error import QuiltError


DB_VERSION = 2

class DBError(QuiltError):
    pass


class InvalidPatchError(QuiltError):
    pass


class PatchSeries(object):

    def __init__(self, dirname, filename):
        self._patches = []
        self.series_file = os.path.join(dirname, filename)

    def exists(self):
        return os.path.exists(self.series_file)

    def read(self):
        with open(self.series_file, "r") as f:
            self._patches = f.readlines()

    def save(self):
        with open(self.series_file, "w") as f:
            for patch in self._patches:
                f.write(patch)

    def add_patch(self, patch_name):
        self._patches.append(patch_name)

    def remove_patch(self, patch_name):
        self._patches.remove(patch_name)

    def top_patch(self):
        if not self._patches:
            return None
        return self._patches[-1]

    def first_patch(self):
        if not self._patches:
            return None
        return self._patches[0]

    def patches(self):
        return self._patches

    def patches_after(self, patch_name):
        if patch_name not in self._patches:
            raise InvalidPatchError("Patch %r is not known.")
        index = self._patches.index(patch_name)
        return self._patches[index+1:]

    def patch_after(self, patch_name):
        if patch_name not in self._patches:
            raise InvalidPatchError("Patch %r is not known.")
        index = self._patches.index(patch_name)
        return self._patches[index+1]


class Db(PatchSeries):

    def __init__(self, dirname):
        if os.path.exists(dirname):
            self.check_version(version_file)
        super(Db, self).__init__(dirname, "applied-patches")

    def _create_version(self, version_file):
        with open(version_file, "w") as f:
            f.write(str(DB_VERSION))

    def create(self):
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        version_file = os.path.join(dirname, ".version")
        self._create_version(version_file)

    def applied_patches(self):
        return self.patches()

    def check_version(self, version_file):
        try:
            f = open(version_file, "r")
            version = f.read(1)
        finally:
            f.close()
        if not version == str(DB_VERSION):
            raise DBError("The quilt meta-data version of %r is not supported "
                          "by python-quilt. Python-quilt only supports "
                          "version %r" % (version, DB_VERSION))


class Series(PatchSeries):

    def __init__(self, dirname):
        super(Series, self).__init__(dirname, "series")
