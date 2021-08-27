from queue import Queue
from threading import Thread, Event
import time
import numpy as np
import numba as nb

class TestThread(Thread):
    def __init__(self, q: Queue, e: Event):
        super(TestThread, self).__init__()
        self.q = q
        self.e = e
        self.e.set()

    def run(self):
        while self.e.is_set():
            print(111)
            if self.q.qsize() > 0:
                data = self.q.get()
                print("get data:", data)
            self.e.clear()
            self.e.wait()
        print("done")


@nb.jit(nopython=True)
def test(a, b):
    res = []
    for e in a:
        res.append(e * b)
    return res


if __name__ == '__main__':
    a = {
        3:12,
        1:2,
        2:4
    }

    sorted_keys = sorted(a.keys())

    print(a[sorted_keys[0]])





