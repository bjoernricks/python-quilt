import os, os.path
from quilt.patch import Patch
from six.moves import cStringIO
import sys

from helpers import QuiltTest, make_file, tmp_mapping, tmp_series

from quilt.delete import Delete
from quilt.cli.delete import DeleteCommand

class Test(QuiltTest):

    def test_next_first(self):
        """ Delete the next patch with only unapplied patches """
        with tmp_series() as [dir, patches]:
            patches.add_patch(Patch("patch"))
            patches.save()
            cmd = Delete(dir, quilt_pc=dir, quilt_patches=patches.dirname)
            cmd.delete_next()
            patches.read()
            self.assertTrue(patches.is_empty())
    
    def test_no_backup_next(self):
        """ Remove the next patch without leaving a backup """
        with tmp_series() as [dir, patches]:
            patches.add_patch(Patch("patch"))
            patches.save()
            patch = os.path.join(patches.dirname, "patch")
            make_file(b"", patch)
            class args:
                next = True
                patch = None
                remove = True
                backup = False
            with tmp_mapping(os.environ) as env, \
                    tmp_mapping(vars(sys)) as tmp_sys:
                env.set("QUILT_PATCHES", patches.dirname)
                env.set("QUILT_PC", dir)
                tmp_sys.set("stdout", cStringIO())
                DeleteCommand().run(args)
            self.assertFalse(os.path.exists(patch))
            self.assertFalse(os.path.exists(patch + "~"))
    
    def test_no_backup_named(self):
        """ Remove a specified patch without leaving a backup """
        with tmp_series() as [dir, patches]:
            patches.add_patch(Patch("patch"))
            patches.save()
            patch = os.path.join(patches.dirname, "patch")
            make_file(b"", patch)
            class args:
                patch = "patch"
                next = False
                remove = True
                backup = False
            with tmp_mapping(os.environ) as env, \
                    tmp_mapping(vars(sys)) as tmp_sys:
                env.set("QUILT_PATCHES", patches.dirname)
                env.set("QUILT_PC", dir)
                tmp_sys.set("stdout", cStringIO())
                DeleteCommand().run(args)
            self.assertFalse(os.path.exists(patch))
            self.assertFalse(os.path.exists(patch + "~"))
