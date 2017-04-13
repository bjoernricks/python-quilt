# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# See LICENSE comming with the source of python-quilt for details.

""" Test operations that list patches """

import os
import os.path
import sys

from contextlib import contextmanager
from unittest import TestCase

from six.moves import cStringIO

from helpers import tmp_mapping

from quilt.cli.next import NextCommand
from quilt.cli.previous import PreviousCommand


class C(object):
    patch = None


class Test(TestCase):

    def test_previous_only_unapplied(self):
        with self._setup_test_data(), \
                tmp_mapping(vars(sys)) as tmp_sys:
            tmp_sys.set("stderr", cStringIO())
            with self.assertRaises(SystemExit) as caught:
                PreviousCommand().run(C())
            self.assertEqual(caught.exception.code, 1)
            self.assertIn("No patches applied", sys.stderr.getvalue())

    def test_next_topmost(self):
        with self._setup_test_data(), \
                tmp_mapping(vars(sys)) as tmp_sys:
            tmp_sys.set("stdout", cStringIO())
            NextCommand().run(C())
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
