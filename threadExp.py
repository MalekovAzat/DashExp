from multiprocessing import Process, Queue
import time

def f(q):
    q.put([42, None, 'hello'])
    time.sleep(3)


if __name__ == '__main__':
    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    p.join()
    print(q.get())    # prints "[42, None, 'hello']"
    