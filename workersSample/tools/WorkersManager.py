from taskSamples import taskManager

import multiprocessing as mp
from tools.storageProvider import storageProvider as sp
import time
import uuid 

# for internal usage
def pusherFunc(internalQ, taskQ):
    while True:
        newTask = internalQ.get()
        # print('newTask', newTask)
        sp().updateTaskStatus(newTask['taskId'], 'in-queue')
        taskQ.put(newTask)

def workerFunc(workerNumber, taskQ):
    print(f'--Worker-{workerNumber} started--')

    while True:
        newTask = taskQ.get()
        if sp().taskStatus(newTask['taskId']) == 'in-aborted':
            continue

        sp().updateExecutedTask(workerNumber, newTask['taskId'])
        sp().updateTaskStatus(newTask['taskId'], 'in-progress')
        
        taskManager.executeTask(newTask)

        sp().updateExecutedTask(workerNumber, '')
        sp().updateTaskStatus(newTask['taskId'], 'in-completed')

class WorkersManager():
    def __init__(self, /, workersCount = 4, maxActiveTaskCount = 100):
        self.taskQueue = mp.Queue(maxActiveTaskCount)
        self.internalQueue = mp.Queue(maxActiveTaskCount)

        self.queuePusher = mp.Process(target=pusherFunc, args=(self.internalQueue, self.taskQueue))
        self.queuePusher.start()

        self.workers = [mp.Process(target=workerFunc, args=(i, self.taskQueue,))  for i in range(0, workersCount)]
        for worker in self.workers:
            worker.start()

    def getUnicId(self):
        return str(uuid.uuid1()).replace("-", "")

    def push(self, taskInfo):
        taskId = self.getUnicId()
        if taskId:
            taskInfo['taskId'] = taskId
            self.internalQueue.put(taskInfo)

    def restartWorkerByTask(self, taskId):
        workerNumber = sp().getWorkerNumberByTask(taskId)
        if workerNumber == None:
            return
        
        self.workers[workerNumber].kill()
        self.workers[workerNumber] = mp.Process(target=workerFunc, args=(workerNumber, self.taskQueue))
        self.workers[workerNumber].start()

        
def main():
    workersManager = WorkersManager(workersCount=4)

if __name__ == "__main__":
    main()
