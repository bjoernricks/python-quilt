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
        self.dirname = dirname
        self.filename = filename
        self.series_file = os.path.join(dirname, filename)
        self.read()

    def _check_patch(self, patch_name):
        if not self.is_patch(patch_name):
            raise InvalidPatchError("Patch %r is not known.")

    def exists(self):
        """ Returns True if series file exists """
        return os.path.exists(self.series_file)

    def read(self):
        """ Reads all patches from the series file """
        if self.exists():
            with open(self.series_file, "r") as f:
                for line in f:
                    line = line[:-1]
                    self._patches.append(line)

    def save(self):
        """ Saves current patches list in the series file """
        with open(self.series_file, "w") as f:
            for patch in self._patches:
                f.write(patch)

    def add_patch(self, patch_name):
        """ Add a patch to the patches list """
        self._patches.append(patch_name)

    def remove_patch(self, patch_name):
        """ Remove a patch from the patches list """
        self._patches.remove(patch_name)

    def top_patch(self):
        """ Returns the last patch from the patches list or None if the list
            is empty """
        if not self._patches:
            return None
        return self._patches[-1]

    def first_patch(self):
        """ Returns the first patch from the patches list or None if the list
            is empty """
        if not self._patches:
            return None
        return self._patches[0]

    def patches(self):
        """ Returns the list of patches """
        return self._patches

    def patches_after(self, patch_name):
        """ Returns a list of patches after patch name from the patches list """
        self._check_patch(patch_name)
        index = self._patches.index(patch_name)
        return self._patches[index+1:]

    def patch_after(self, patch_name):
        """ Returns the patch followed by patch name from the patches list """
        self._check_patch(patch_name)
        index = self._patches.index(patch_name)
        return self._patches[index+1]

    def patches_before(self, patch_name):
        """ Returns a list of patches before patch name from the patches list """
        self._check_patch(patch_name)
        index = self._patches.index(patch_name)
        return self._patches[:index]

    def is_patch(self, patch_name):
        """ Returns True if patch name is in the list of patches. Otherwise it
            returns False.
        """
        return patch_name in self._patches


class Db(PatchSeries):

    """ Represents the "Database" of quilt which contains the list of current
        applied patches
    """

    def __init__(self, dirname):
        self.version_file = os.path.join(dirname, ".version")
        if os.path.exists(dirname):
            self.check_version(self.version_file)
        super(Db, self).__init__(dirname, "applied-patches")

    def _create_version(self, version_file):
        with open(version_file, "w") as f:
            f.write(str(DB_VERSION))

    def create(self):
        """ Creates the dirname and inserts a .version file """
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)
        self._create_version(self.version_file)

    def save(self):
        """ Create version file and save applied patches """
        self.create()
        super(Db, self).save()

    def applied_patches(self):
        """ Lists all applied patches """
        return self.patches()

    def check_version(self, version_file):
        """ Checks if the .version file in dirname has the correct supported
            version number """
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

    """ Represents the series file of quilt which contains the patches to be
        applied
    """

    def __init__(self, dirname):
        super(Series, self).__init__(dirname, "series")
