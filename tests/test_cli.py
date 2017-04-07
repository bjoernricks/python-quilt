import runpy
from six.moves import cStringIO
import sys
from unittest import TestCase

from helpers import tmp_mapping

class Test(TestCase):

    def test_registration(self):
        with tmp_mapping(vars(sys)) as temp_sys:
            temp_sys.set("argv", ["pquilt", "push", "--help"])
            temp_sys.set("stdout", cStringIO())
            try:
                runpy.run_path("pquilt", run_name="__main__")
            except SystemExit as exit:
                self.assertEqual(exit.code, 0)
            self.assertGreater(sys.stdout.getvalue(), "")
