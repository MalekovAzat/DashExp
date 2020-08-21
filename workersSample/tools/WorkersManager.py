from taskSamples import taskManager

import multiprocessing as mp

import time

def template_target(q):
    print('start Process')
    item = q.get()
    while True:
        item = q.get()
        print('Get an item', item**512**10)
        print('end Task')

class WorkersManager():
    def __init__(self, /, target=None, workersCount = 4, max_task_count = 30, daemon=False):
        if target==None:
            target = template_target
        self.m_workersCount = workersCount
        self.m_isDaemon = daemon
        
        # may be need 
        # self.m_queue = mp.Queue(max_task_count)
        self.m_taskQueue = []
        self.m_workers = []
        self.m_lastTaskNumber = 1
        # self.m_emptyId = [i for i in range(1, workersCount + 1)]
        self.m_busyWorkers = 0

        # lizy initialization
        # self.m_workers = [mp.Process(target=target, args=(self.m_queue,), daemon=daemon) for index in range(1, workersCount + 1)]

    def _hasFreeWorker(self):
        return self.m_busyWorkers < self.m_workersCount

    def startTask(self, task, *args):
        if self._hasFreeWorker():
            worker = mp.Process(target=task, args=args)
            worker.start()
            self.m_busyWorkers += 1
            self.m_workers.append(worker)
            self._createStorageForTask()
            self.m_lastTaskNumber+=1
            return self.m_lastTaskNumber - 1
        return -1

    def _createStorageForTask(self):
        self.m_storage[f'task-{self.m_lastTaskNumber}-iterationCount'] = 0
        self.m_storage[f'task-{self.m_lastTaskNumber}-currentIteration'] = 0
        self.m_storage[f'task-{self.m_lastTaskNumber}-output'] = 0

    def join(self):
        if self.m_isDaemon:
            return
        for worker in self.m_workers:
            worker.join()
        
def main():
    workersManager = WorkersManager(target=template_target, daemon=False)

if __name__ == "__main__":
    main()
