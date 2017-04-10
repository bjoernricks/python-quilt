# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2012 - 2017 Björn Ricks <bjoern.ricks@gmail.com>
#
# See LICENSE comming with the source of python-quilt for details.

from quilt.utils import File, DirectoryParam, FileParam


class Backup(object):

    """ Class to backup files

    This class should be exented in future to support all functions of quilts
    backup-files script.
    """

    @DirectoryParam(["dest_dir"])
    @FileParam(["file"])
    def backup_file(self, file, dest_dir, copy_empty=False):
        """ Backup file in dest_dir Directory.
        The return value is a File object pointing to the copied file in the
        destination directory or None if no file is copied.

        If file exists and it is not empty it is copied to dest_dir.
        If file exists and it is empty the file is copied only if copy_empty is
        True.
        If file does not exist and copy_empty is True a new file in dest_dir
        will be created.
        In all other cases no file will be copied and None is returned.
        """
        if file.exists():
            if not copy_empty and file.is_empty():
                return None
            dest_dir.create()
            file.copy(dest_dir)
            return dest_dir + file.get_basefile()
        elif copy_empty:
            # create new file in dest_dir
            dest_dir = dest_dir + file.get_directory()
            dest_dir.create()
            dest_file = dest_dir + file.get_basefile()
            dest_file.touch()
            return dest_file
        else:
            return None

    @DirectoryParam(["src_dir", "dest_dir"])
    def backup_files(self, src_dir, dest_dir, filenames, copy_empty=False):
        for filename in filenames:
            src_file = src_dir + File(filename)

            if not src_file.exists():
                continue
            if src_file.is_empty() and not copy_empty:
                continue
            self.backup_file(src_file, dest_dir)

    @DirectoryParam(["src_dir", "dest_dir"])
    def backup_dir(self, src_dir, dest_dir, copy_empty=False):
        for file_name in src_dir.files():
            file = File(file_name)
            file_dir = file.get_directory()
            if file_dir:
                dest = dest_dir + file_dir
            else:
                dest = dest_dir
            self.backup_file(file, dest, copy_empty)
