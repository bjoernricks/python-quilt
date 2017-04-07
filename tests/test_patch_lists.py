""" Test operations that list patches """

from contextlib import contextmanager
import os, os.path
from six.moves import cStringIO
import sys
from unittest import TestCase

from helpers import tmp_mapping

from quilt.cli.next import NextCommand
from quilt.cli.previous import PreviousCommand

class Test(TestCase):

    def test_previous_only_unapplied(self):
        with self._setup_test_data(), \
                tmp_mapping(vars(sys)) as tmp_sys:
            tmp_sys.set("stderr", cStringIO())
            with self.assertRaises(SystemExit) as caught:
                PreviousCommand().run(None, [])
            self.assertEqual(caught.exception.code, 1)
            self.assertIn("No patches applied", sys.stderr.getvalue())
    
    def test_next_topmost(self):
        with self._setup_test_data(), \
                tmp_mapping(vars(sys)) as tmp_sys:
            tmp_sys.set("stdout", cStringIO())
            NextCommand().run(None, [])
            self.assertEqual("p1.patch\n", sys.stdout.getvalue())
    
    @contextmanager
    def _setup_test_data(self):
        data = os.path.join(os.path.dirname(__file__), "data")
        patches = os.path.join(data, "push", "test2", "patches")
        no_applied = os.path.join(data, "push", "test2")
        
        with tmp_mapping(os.environ) as env:
            env.set("QUILT_PATCHES", patches)
            env.set("QUILT_PC", no_applied)
            yield
