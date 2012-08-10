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

import getopt
import os.path

from quilt.error import QuiltError
from quilt.patch import Patch


DB_VERSION = 2

class DBError(QuiltError):
    pass


class InvalidPatchError(QuiltError):
    pass

class PatchLine(object):

    """ Represents a line in a series files """

    def __init__(self, patch):
        """ patch can be either a string or a Patch object """
        self.comment = ""
        self.patch = None
        self.line = ""
        if isinstance(patch, basestring):
            self._parse_line(patch)
        elif isinstance(patch, Patch):
            self.patch = patch
            self.line = patch.get_name()

    def _parse_line(self, line):
        line = line.rstrip("\r\n")
        self.line = line

        if line.rstrip().startswith("#"):
            self.comment = line
            return

        if not line.strip():
            # empty line
            return

        if "#" in line:
            patchline, self.comment = line.split("#", 1)
        else:
            patchline = line

        patchline = patchline.strip()
        if not patchline:
            return

        patch_args = None
        strip = 1
        reverse = False

        if " " in patchline:
            patch_name, patch_args = patchline.split(" ", 1)
        else:
            patch_name = patchline

        if patch_args:
            try:
                opts, args = getopt.getopt(patch_args, "p:R", ["strip=",
                                                               "reverse"])
                for o, a in opts:
                    if o in ["p", "strip"]:
                        strip = a
                    elif o in ["R", "reverse"]:
                        reverse = True
            except getopt.GetoptError, err:
                print >> sys.stderr, err

        self.patch = Patch(patch_name, strip, reverse)

    def get_patch(self):
        return self.patch

    def get_comment(self):
        return self.comment

    def __str__(self):
        return self.line


class PatchSeries(object):

    def __init__(self, dirname, filename):
        self.dirname = dirname
        self.filename = filename
        self.series_file = os.path.join(dirname, filename)
        self.read()

    def _check_patch(self, patch):
        if not self.is_patch(patch):
            raise InvalidPatchError("Patch %s is not known." % patch)

    def exists(self):
        """ Returns True if series file exists """
        return os.path.exists(self.series_file)

    def read(self):
        """ Reads all patches from the series file """
        self.patchlines = []
        self.patch2line = dict()
        if self.exists():
            with open(self.series_file, "r") as f:
                for line in f:
                    self.add_patch(line)

    def save(self):
        """ Saves current patches list in the series file """
        with open(self.series_file, "w") as f:
            for patchline in self.patchlines:
                f.write(str(patchline))
                f.write("\n")

    def add_patch(self, patch):
        """ Add a patch to the patches list """
        patchline = PatchLine(patch)
        patch = patchline.get_patch()
        if patch:
            self.patch2line[patch] = patchline
        self.patchlines.append(patchline)

    def _add_patches(self, patches):
        for patch_name in patches:
            self.add_patch(patch_name)

    def insert_patches(self, patches):
        """ Insert list of patches at the front of the curent patches list """
        patchlines = []
        for patch_name in patches:
            patchline = PatchLine(patch_name)
            patch = patchline.get_patch()
            if patch:
                self.patch2line[patch] = patchline
            patchlines.append(patchline)
        patchlines.extend(self.patchlines)
        self.patchlines = patchlines

    def add_patches(self, patches, after=None):
        """ Add a list of patches to the patches list """
        if after is None:
            self.insert_patches(patches)
        else:
            self._check_patch(after)
            patchlines = self._patchlines_before(after)
            patchlines.append(self.patch2line[after])
            for patch in patches:
                patchline = PatchLine(patch)
                patchlines.append(patchline)
                self.patch2line[patchline.get_patch()] = patchline
            patchlines.extend(self._patchlines_after(after))
            self.patchlines = patchlines

    def remove_patch(self, patch):
        """ Remove a patch from the patches list """
        self._check_patch(patch)
        patchline = self.patch2line[patch]
        del self.patch2line[patch]
        self.patchlines.remove(patchline)

    def top_patch(self):
        """ Returns the last patch from the patches list or None if the list
            is empty """
        patches = self.patches()
        if not patches:
            return None
        return patches[-1]

    def first_patch(self):
        """ Returns the first patch from the patches list or None if the list
            is empty """
        patches = self.patches()
        if not patches:
            return None
        return patches[0]

    def patches(self):
        """ Returns the list of patches """
        return [line.get_patch() for line in self.patchlines if \
                line.get_patch()]

    def _patchlines_after(self, patch):
        self._check_patch(patch)
        patchline = self.patch2line[patch]
        index = self.patchlines.index(patchline) + 1
        if index >= len(self.patchlines):
            return []
        return self.patchlines[index:]

    def _patchlines_before(self, patch):
        self._check_patch(patch)
        patchline = self.patch2line[patch]
        index = self.patchlines.index(patchline)
        return self.patchlines[:index]

    def _patchlines_until(self, patch):
        self._check_patch(patch)
        patchline = self.patch2line[patch]
        index = self.patchlines.index(patchline) + 1
        return self.patchlines[:index]

    def patches_after(self, patch):
        """ Returns a list of patches after patch from the patches list """
        return [line.get_patch() for line in self._patchlines_after(patch) if \
                line.get_patch()]

    def patch_after(self, patch):
        """ Returns the patch followed by patch from the patches list or None if
        no patch after can be found.
        """
        patches = self.patches_after(patch)
        if patches:
            return patches[0]
        return None

    def patches_before(self, patch):
        """ Returns a list of patches before patch from the patches list """
        return [line.get_patch() for line in self._patchlines_before(patch) \
                if line.get_patch()]

    def patch_before(self, patch):
        """ Returns the patch before patch from the patches list or None if no
        patch before can be found.
        """
        patches = self.patches_before(patch)
        if patches:
            return patches[0]
        return None

    def patches_until(self, patch):
        """ Returns a list of patches before patch from the patches list
        including the provided patch
        """
        return [line.get_patch() for line in self._patchlines_until(patch) if \
                line.get_patch()]

    def is_patch(self, patch):
        """ Returns True if patch is in the list of patches. Otherwise it
            returns False.
        """
        return patch in self.patch2line


class Db(PatchSeries):

    """ Represents the "Database" of quilt which contains the list of current
        applied patches
    """

    def __init__(self, dirname):
        self.version_file = os.path.join(dirname, ".version")
        if os.path.exists(self.version_file):
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
        with open(version_file, "r") as f:
            version = f.read(1)

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
