import os.path
from quilt.db import Db
from quilt.patch import Patch

from helpers import QuiltTest, make_file, run_cli, tmp_series

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
    
    def test_next_after(self):
        """ Delete the successor to the topmost patch """
        with tmp_series() as [dir, series]:
            series.add_patch(Patch("topmost"))
            series.add_patch(Patch("unapplied"))
            series.save()
            db = Db(dir)
            db.add_patch(Patch("topmost"))
            db.save()
            cmd = Delete(dir, db.dirname, series.dirname)
            cmd.delete_next()
            series.read()
            [patch] = series.patches()
            self.assertEqual(patch, Patch("topmost"))
    
    def test_no_backup_next(self):
        """ Remove the next patch without leaving a backup """
        with tmp_series() as [dir, patches]:
            patches.add_patch(Patch("patch"))
            patches.save()
            patch = os.path.join(patches.dirname, "patch")
            make_file(b"", patch)
            run_cli(DeleteCommand,
                dict(next=True, patch=None, remove=True, backup=False),
                patches.dirname, applied=dir)
            self.assertFalse(os.path.exists(patch))
            self.assertFalse(os.path.exists(patch + "~"))
    
    def test_no_backup_named(self):
        """ Remove a specified patch without leaving a backup """
        with tmp_series() as [dir, patches]:
            patches.add_patch(Patch("patch"))
            patches.save()
            patch = os.path.join(patches.dirname, "patch")
            make_file(b"", patch)
            run_cli(DeleteCommand,
                dict(patch="patch", next=False, remove=True, backup=False),
                patches.dirname, applied=dir)
            self.assertFalse(os.path.exists(patch))
            self.assertFalse(os.path.exists(patch + "~"))
