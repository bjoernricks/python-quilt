# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.


class QuiltError(Exception):
    pass


class NoPatchesInSeries(QuiltError):

    def __init__(self, series):
        self.series = series

    def __str__(self):
        return "No patch in series"


class NoAppliedPatch(QuiltError):

    def __init__(self, series):
        self.series = series

    def __str__(self):
        return "No patches applied"


class AllPatchesApplied(QuiltError):

    def __init__(self, series, top=None):
        self.series = series
        self.top = top

    def __str__(self):
        if not self.top:
            return "All patches are already applied"
        return "File series fully applied, ends at patch %s" % \
            self.top.get_name()


class UnknownPatch(QuiltError):

    def __init__(self, series, patch):
        self.series = series
        self.patch = patch

    def __str__(self):
        return "Patch %s is not in series" % self.patch.get_name()


class PatchAlreadyExists(QuiltError):

    def __init__(self, series, patchname):
        self.series = series
        self.patchname = patchname

    def __str__(self):
        return "Patch %s already exists" % self.patchname
