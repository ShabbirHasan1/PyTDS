from queue import Queue
from threading import Thread, Event
import time


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


if __name__ == '__main__':
    q = Queue()
    q.put("a")
    while q.not_empty:
        pass











