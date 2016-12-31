import runpy
import sys
from unittest import TestCase

from helpers import StringIO, tmp_mapping

class Test(TestCase):

    def test_registration(self):
        with tmp_mapping(vars(sys)) as temp_sys:
            temp_sys.set("argv", ["pquilt", "push", "--help"])
            temp_sys.set("stdout", StringIO())
            try:
                runpy.run_path("pquilt", run_name="__main__")
            except SystemExit as exit:
                self.assertEqual(exit.code, 0)
            self.assertGreater(sys.stdout.getvalue(), "")
