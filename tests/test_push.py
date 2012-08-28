#!/usr/bin/env python
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

import os.path
import sys

from helpers import QuiltTest

test_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(test_dir, os.pardir))

from quilt.patch import Patch
from quilt.push import Push
from quilt.utils import Directory, TmpDirectory

class PushTest(QuiltTest):

    data_dir = Directory(os.path.join(test_dir, "data", "push"))

    def test_apply_all(self):
        patch1 = Patch("p1.patch")
        patch2 = Patch("p2.patch")

        test_dir = self.data_dir + "test1"

        with TmpDirectory(dir=self.data_dir.get_name()) as tmp_dir:
            tmp_test_dir = tmp_dir + "test1"
            test_dir.copy(tmp_test_dir)

            pc_dir = tmp_test_dir + "pc"
            patches_dir = tmp_test_dir + "patches"


            push = Push(tmp_test_dir.get_name(), pc_dir.get_name(),
                        patches_dir.get_name())

            self.assertEquals(None, push.db.top_patch())
            push.apply_all()
            self.assertEquals(patch2, push.db.top_patch())


def suite():
    return PushTest.suite()

if __name__ == "__main__":
    PushTest.run_tests()
