from collections import deque
from typing import Iterable


class unique_deque(deque):
    """ only append and popleft"""
    def __init__(self, *args, **kwargs):
        super().__init__(args, **kwargs)
        self.items = set()

    def append(self, x):
        if x not in self.items:
            super().append(x)
            self.items.add(x)

    def appendleft(self, x):
        if x not in self.items:
            super().appendleft(x)
            self.items.add(x)

    def popleft(self):
        elem = super().popleft()
        self.items.remove(elem)
        return elem

    def pop(self, i=...):
        elem = super().pop(i)
        self.items.remove(elem)
        return elem

    def extend(self, iterable: Iterable):
        for i in iterable:
            self.append(i)

    def extendleft(self, iterable: Iterable):
        for i in iterable:
            self.appendleft(i)

    def __contains__(self, item):
        return item in self.items
