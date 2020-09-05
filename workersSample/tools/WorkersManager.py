from taskSamples import taskManager

import multiprocessing as mp
from tools.storageProvider import storageProvider as sp
import time
import uuid 

# for internal usage
def pusherFunc(internalQ, taskQ):
    print('hello by internal')
    while True:
        newTask = internalQ.get()
        print('newTask', newTask)
        sp().updateTaskStatus(newTask['taskId'], 'in-queue')
        taskQ.put(newTask)

def workerFunc(taskQ):
    print('--worker started--')
    while True:
        newTask = taskQ.get()
        sp().updateTaskStatus(newTask['taskId'], 'in-progress')
        
        taskManager.executeTask(newTask)

        sp().updateTaskStatus(newTask['taskId'], 'in-completed')

class WorkersManager():
    def __init__(self, /, workersCount = 4, maxActiveTaskCount = 100):
        self.workersCount = workersCount
        
        self.taskQueue = mp.Queue(maxActiveTaskCount)
        self.internalQueue = mp.Queue(maxActiveTaskCount)
        self.activeWorkersCount = 0
        self.usedIds = []
        self.freeIds = [i for i in range(1, maxActiveTaskCount + 1)]
        
        self.queuePusher = mp.Process(target=pusherFunc, args=(self.internalQueue, self.taskQueue))
        self.queuePusher.start()

        self.workers = [mp.Process(target=workerFunc, args=(self.taskQueue,))  for i in range(0, workersCount)]
        for worker in self.workers:
            worker.start()

    def hasFreeWorker(self):
        return self.activeWorkersCount < self.workersCount

    def getUnicId(self):   
        return str(uuid.uuid1()).replace("-", "")

    def push(self, taskInfo):
        taskId = self.getUnicId()
        if taskId:
            taskInfo['taskId'] = taskId
            self.internalQueue.put(taskInfo)
            
    def startTask(self, task, *args):
        pass
        # if self._hasFreeWorker():
        #     unicId = self._getUnicId()
        #     worker = mp.Process(target=task, args=(*args, unicId))
        #     sp().createData(unicId)

        #     worker.start()

        #     self.m_workers.append(worker)

        #     return unicId
        # return None
        
def main():
    workersManager = WorkersManager(workersCount=4)

if __name__ == "__main__":
    main()
