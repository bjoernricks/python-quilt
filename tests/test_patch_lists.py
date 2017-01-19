# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# See LICENSE comming with the source of python-quilt for details.

""" Test operations that list patches """

import os.path
import sys

from unittest import TestCase

from quilt.db import Db
from quilt.patch import Patch
from six.moves import cStringIO

from helpers import run_cli, tmp_mapping, tmp_series

from quilt.cli.next import NextCommand
from quilt.cli.previous import PreviousCommand
from quilt.cli.series import SeriesCommand


class Test(TestCase):

    def test_previous_only_unapplied(self):
        env = self._setup_test_data()
        with tmp_mapping(vars(sys)) as tmp_sys:
            tmp_sys.set("stderr", cStringIO())
            with self.assertRaises(SystemExit) as caught:
                run_cli(PreviousCommand, dict(patch=None), *env)
            self.assertEqual(caught.exception.code, 1)
            self.assertIn("No patches applied", sys.stderr.getvalue())

    def test_next_topmost(self):
        env = self._setup_test_data()
        output = run_cli(NextCommand, dict(patch=None), *env)
        self.assertEqual("p1.patch\n", output)

    def _setup_test_data(self):
        data = os.path.join(os.path.dirname(__file__), "data")
        patches = os.path.join(data, "push", "test2", "patches")
        no_applied = os.path.join(data, "push", "test2")
        return (patches, no_applied)

    def test_series_v(self):
        with tmp_series() as [dir, series]:
            applied = Db(dir)
            applied.add_patch(Patch("applied.patch"))
            applied.add_patch(Patch("topmost.patch"))
            applied.save()
            series.add_patches(applied.applied_patches())
            series.add_patch(Patch("unapplied.patch"))
            series.save()
            output = run_cli(SeriesCommand, dict(v=True),
                series.dirname, applied.dirname)
        self.assertMultiLineEqual(output,
            "+ applied.patch\n"
            "= topmost.patch\n"
            "  unapplied.patch\n")
