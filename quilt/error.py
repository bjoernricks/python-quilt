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

class QuiltError(Exception):
    pass


class NoPatchesInSeries(QuiltError):

    def __str__(self):
        return "No patch in series file %s" % self.args[0].series_file


class NoAppliedPatch(QuiltError):

    def __str__(self):
        return "No applied patch in file %s" % self.args[0].series_file


class AllPatchesApplied(QuiltError):

    def __str__(self):
        return "All patches are already applied"
