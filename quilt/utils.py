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

""" Utility classes used by serveral quilt modules """

import functools
import inspect
import os
import os.path
import shutil
import subprocess
import tempfile

from quilt.error import QuiltError


class SubprocessError(QuiltError):

    def __init__(self, command, returncode, output=None):
        self.command = command
        self.returncode = returncode
        self.output = output

    def get_returncode(self):
        return self.returncode

    def __str__(self):
        retval = "Command %s finished with return code %d" % (self.command,
                     self.returncode)
        if self.output:
            retval += "Output was: '%s'" % self.output
        return retval


class Process(object):

    def __init__(self, cmd):
        self.cmd = cmd

    def run(self, suppress_output=False, inputdata=None, **kw):
        """Run command as a subprocess and wait until it is finished.

        The command should be given as a list of strings to avoid problems
        with shell quoting.  If the command exits with a return code other
        than 0, a SubprocessError is raised.
        """
        if inputdata is not None:
            kw["stdin"] = subprocess.PIPE
        if suppress_output:
            kw["stdout"] = open(os.devnull, "w")
            kw["stderr"] = open(os.devnull, "w")
        try:
            process = subprocess.Popen(self.cmd, **kw)
        except OSError, e:
            raise SubprocessError(self.cmd, e.errno, e.strerror)

        if inputdata is not None:
            process.stdin.write(inputdata)
            process.stdin.close()
        ret = process.wait()
        if ret != 0:
            raise SubprocessError(self.cmd, ret)


class Directory(object):
    """Handle directories on filesystems """

    def __init__(self, dirname=None):
        """ Creates a new Directory instance
        """
        self.dirname = dirname

    def exists(self):
        """ Returns True if the directoy exists """
        return os.path.exists(self.dirname)

    def create(self):
        """ Creates the directory and all its parent directories if it does not
        exist yet
        """
        if self.dirname and not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def _content(self, startdir, dirname=None):
        files = []
        dirs = []
        if dirname:
            dir = os.path.join(startdir, dirname)
        else:
            dir = startdir
        contents = os.listdir(dir)
        for content in contents:
            if not dirname:
                name = content
            else:
                name = os.path.join(dirname, content)
            path = os.path.join(dir, content)
            if os.path.isdir(path):
                (newdirs, newfiles) = self._content(startdir, name)
                dirs.append(name)
                files.extend(newfiles)
                dirs.extend(newdirs)
            else:
                files.append(name)
        return (dirs, files)

    def files(self):
        """ Returns all files in this directory and its subdirectories"""
        (dirs, files) = self._content(self.dirname)
        return files

    def content(self):
        """ Returns all directories and files in this directory and its
            subdirectories """
        return self._content(self.dirname)

    def delete(self):
        """ Delete the directory and its content if directory exists"""
        if self.exists():
            shutil.rmtree(self.dirname)

    def get_name(self):
        """ Returns the name of the directory
        """
        return self.dirname

    def get_absdir(self):
        """ Returns this directory with absolute path
        """
        return Directory(os.path.abspath(self.dirname))

    def is_empty(self):
        """ Returns True if the directory doesn't contain any files or
        subdirectories
        """
        contents = os.listdir(self.dirname)
        return len(contents) == 0

    def copy(self, dest, symlinks=False):
        """ Copy to destination directory recursively.
        If symlinks is true, symbolic links in the source tree are represented
        as symbolic links in the new tree, but the metadata of the original
        links is NOT copied; if false or omitted, the contents and metadata of
        the linked files are copied to the new tree.
        """
        if isinstance(dest, Directory):
            dest = dest.get_name()

        shutil.copytree(self.dirname, dest)

    def __add__(self, other):
        if other == None:
            return self
        if isinstance(other, Directory):
            return Directory(os.path.join(self.dirname, other.dirname))
        elif isinstance(other, basestring):
            return Directory(os.path.join(self.dirname, other))
        elif isinstance(other, File):
            return File(os.path.join(self.dirname, other.filename))
        else:
            raise NotImplementedError()

    def __str__(self):
        return self.dirname


class TmpDirectory(Directory):
    """ Creates a temporary directory and can be used as a context manager.
    If used with as a context manager in a with statement the temporary
    directory is deleted automatically.
    """

    def __init__(self, suffix="", prefix="temp", dir=None):
        tmp_dir = tempfile.mkdtemp(suffix, prefix, dir)
        super(TmpDirectory, self).__init__(tmp_dir)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.delete()


class File(object):

    def __init__(self, filename):
        self.filename = filename

    def exists(self):
        return os.path.exists(self.filename)

    def delete(self):
        os.remove(self.filename)

    def delete_if_exists(self):
        if self.exists():
            self.delete()

    def touch(self):
        """ 'Touch' a file. Creates an empty file. """
        open(self.filename, "w").close()

    def link(self, link):
        """ Create hard link as link to this file """
        if isinstance(link, File):
            link = link.filename
        os.link(self.filename, link)

    def copy(self, dest):
        """ Copy file to destination """
        if isinstance(dest, File):
            dest = dest.filename
        elif isinstance(dest, Directory):
            dest = dest.dirname

        shutil.copy2(self.filename, dest)

    def is_empty(self):
        """ Returns True if the size of the file is 0 """
        st = os.stat(self.filename)
        return st.st_size == 0

    def is_link(self):
        return os.path.islink(self.filename)

    def get_name(self):
        """ Returns the name of this file """
        return self.filename

    def get_basename(self):
        """ Return the base name of the file e.g. file if filename is /foo/file.
        If filename doesn't contain a directory get_name and get_basename
        are equal.
        """
        return os.path.basename(self.filename)

    def get_directory(self):
        """ Returns the directory where the file is placed in or None if the
        path to the file doesn't contain a directory
        """
        dirname = os.path.dirname(self.filename)
        if dirname:
            return Directory(dirname)
        else:
            return None

    def get_mode(self):
        return os.stat(self.filename).st_mode

    def get_absfile(self):
        """ Returns the file with an absolute path
        """
        return File(os.path.abspath(self.filename))

    def get_basefile(self):
        """ Returns the file without a path
        """
        return File(self.get_basename())

    def open(self, mode="r", buffering=None):
        return open(self.filename, mode, buffering)

    def __str__(self):
        return self.get_name()


class TmpFile(File):
    """ Tempoary file that is intended to be used within a context manager
    If used with as a context manager in a with statement the temporary
    file is deleted automatically.
    """

    def __init__(self, suffix="", prefix="tmp", dir=None, text=False):
        fd, filename = tempfile.mkstemp(suffix, prefix, dir, text)
        self.fd = fd
        self.file = os.fdopen(fd, "rw")
        super(TmpFile, self).__init__(filename)

    def open(self, mode=None, buffering=None):
        return self.file

    def write(self, string):
        os.write(self.fd, string)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
        self.delete_if_exists()


class FunctionWrapper(object):
    """ FunctionWrapper class to encapsulate function that are decorated by
    a Param class.
    """

    def __init__(self, func, names, cls):
        self.func = func
        self.names = names
        self.cls = cls

    def _get_varnames(self):
        if inspect.isfunction(self.func):
            return inspect.getargspec(self.func)[0]
        elif isinstance(self.func, FunctionWrapper):
            return self.func._get_varnames()

    def __call__(self, *args, **kw):
        newargs = []
        for name, value in zip(self._get_varnames(), args):
            if value and name in self.names and not isinstance(value, self.cls):
                newargs.append(self.cls(value))
            else:
                newargs.append(value)
        for name in self.names:
            value = kw.get(name, None)
            if value and not isinstance(value, self.cls):
                value = self.cls(value)
                kw[name] = value
        return self.func(*newargs, **kw)

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)


class Param(object):
    """ Base class for Parameter class decorators
    """

    cls = None

    def __init__(self, names):
        self.names = names

    def __call__(self, func):
        return FunctionWrapper(func, self.names, self.cls)


class DirectoryParam(Param):
    """ Decorator class to change parameters of methods and functions to a
    Directory class if it's not a Directory yet.

    Usage: @DirectoryParam(["paramname1", "paramname2"])
    """

    cls = Directory


class FileParam(Param):
    """ Decorator class to change parameters of methods and functions to a
    File class if it's not a File yet.

    Usage: @FileParam(["paramname1", "paramname2"])
    """

    cls = File
