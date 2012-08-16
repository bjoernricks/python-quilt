# vim: fileencoding=utf-8 et sw=4 ts=4 tw=80:

# python-quilt - A Python implementation of the quilt patch system
#
# Copyright (C) 2011, 2012  Björn Ricks <bjoern.ricks@gemail.com>
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

import weakref

class MethodRef(object):

    def __init__(self, func):
        if hasattr(func, "im_self"):
            # it's a method
            self.func = func.im_func
            self.obj = weakref.ref(func.im_self)
        elif hasattr(func, "__self__"):
            # it's a python >= 2.6 method
            self.func = func.__func__
            self.obj = weakref.ref(func.__self__)
        else:
            # it should be a function
            self.func = weakref.ref(func)
            self.obj = None

    def __call__(self, *args, **kwargs):
        if self.obj:
            if not self.obj() is None:
                self.func(self.obj(), *args, **kwargs)
            else:
                return
        else:
            self.func()(*args, **kwargs)

    def dead(self):
        if not self.obj:
            return False
        return self.obj() is None

    def __eq__(self, other):
        if not self.obj:
            return self.func() == other
        else:
            if self.obj() is None:
                return False
            if hasattr(other, "im_func"):
                return self.obj() == other.im_self and \
                        self.func == other.im_func
            elif hasattr(other, "__func__"):
                return self.obj() == other.__self__ and \
                        self.func == other.__func__
            else:
                return False


class Signal(object):

    def __init__(self):
        self.slots = []

    def __call__(self, *args, **kwargs):
        for i, slot in enumerate(self.slots):
            if slot.dead():
                del self.slots[i]
                continue

            slot(*args, **kwargs)

    def connect(self, slot):
        if not slot in self.slots:
            self.slots.append(MethodRef(slot))

    def disconnect(self, slot):
        for i, cur_slot in enumerate(self.slots):
            if cur_slot == slot:
                del self.slots[i]
                return

    def __len__(self):
        self.clean()
        return len(self.slots)

    def clean(self):
        for i, slot in enumerate(self.slots):
            if slot.dead():
                del self.slots[i]


class ForwardSignal(object):

    def __init__(self, signal):
        self.signal = signal

    def connect(self, slot):
        self.signal.connect(slot)

    def disconnect(self, slot):
        self.signal.disconnect(slot)

    def __len__(self):
        return len(self.signal)
