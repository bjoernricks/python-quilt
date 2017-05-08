# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

import os
import os.path

from quilt.utils import Process, DirectoryParam, _EqBase, File, FileParam, \
                        SubprocessError


class Patch(_EqBase):

    """ Wrapper around the patch util """

    def __init__(self, patch_name, strip=1, reverse=False):
        self.patch_name = patch_name
        self.strip = strip
        self.reverse = reverse

    @DirectoryParam(["patch_dir", "work_dir"])
    def run(self, cwd, patch_dir=None, backup=False, prefix=None,
            reverse=False, work_dir=None, force=False, dry_run=False,
            no_backup_if_mismatch=False, remove_empty_files=False,
            quiet=False, suppress_output=False):
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

        if work_dir:
            cmd.append("-d")
            cmd.append(work_dir.get_name())

        if no_backup_if_mismatch:
            cmd.append("--no-backup-if-mismatch")

        if remove_empty_files:
            cmd.append("--remove-empty-files")

        if force:
            cmd.append("-f")

        cmd.append("-i")
        if patch_dir:
            dir = patch_dir + self.get_name()
            name = dir.get_name()
        else:
            name = self.get_name()
        cmd.append(name)

        if quiet:
            cmd.append("-s")

        if dry_run:
            cmd.append("--dry-run")

        Process(cmd).run(cwd=cwd, suppress_output=suppress_output)

    def get_name(self):
        return self.patch_name

    @DirectoryParam(["patch_dir"])
    def get_header(self, patch_dir=None):
        """ Returns bytes """
        lines = []

        if patch_dir:
            file = patch_dir + File(self.get_name())
            name = file.get_name()
        else:
            name = self.get_name()
        with open(name, "rb") as f:
            for line in f:
                if line.startswith(b"---") or line.startswith(b"Index:"):
                    break
                lines.append(line)

        return b"".join(lines)

    def __eq__(self, other):
        return (isinstance(other, Patch) and self.get_name() ==
                other.get_name())

    def __hash__(self):
        return hash(self.get_name())

    def __str__(self):
        return self.get_name()

    def __repr__(self):
        return "<Patch(%r, %r, %r) id=0x%0x>" % (self.get_name(), self.strip,
                                                 self.reverse, id(self))


class RollbackPatch(object):

    @DirectoryParam(["cwd", "backup_dir"])
    def __init__(self, cwd, backup_dir):
        self.cwd = cwd
        self.backup_dir = backup_dir

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


class Diff(object):
    """ Wrapper around the diff util
    """

    @FileParam(["left", "right"])
    def __init__(self, left, right):
        """ left points to the first file and right to the second file
        """
        self.left = left
        if not self.left.exists():
            self.left = File("/dev/null")

        self.right = right
        if not self.right.exists():
            self.right = File("/dev/null")

    def run(self, cwd, left_label=None, right_label=None, unified=True,
            fd=None):
        cmd = ["diff"]

        if unified:
            cmd.append("-u")

        if left_label:
            cmd.append("--label")
            cmd.append(left_label)

        if right_label:
            if not left_label:
                cmd.append("--label")
                cmd.append(self.right.get_name())
            cmd.append("--label")
            cmd.append(right_label)

        cmd.append(self.left.get_name())
        cmd.append(self.right.get_name())

        try:
            Process(cmd).run(cwd=cwd, stdout=fd)
        except SubprocessError as e:
            if e.get_returncode() > 1:
                raise e

    def equal(self, cwd):
        """ Returns True if left and right are equal
        """
        cmd = ["diff"]
        cmd.append("-q")
        cmd.append(self.left.get_name())
        cmd.append(self.right.get_name())

        try:
            Process(cmd).run(cwd=cwd, suppress_output=True)
        except SubprocessError as e:
            if e.get_returncode() == 1:
                return False
            else:
                raise e
        return True
