from redis import StrictRedis
import multiprocessing as mp
import threading as tr

class storageProvider(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(storageProvider, cls).__new__(cls)
        return cls.instance

    def __init__(self, max_reports_count = 100):
        self.storage = StrictRedis(host='localhost', port=6379)
        # self.lock = mp.Lock()
        self.lock = tr.Lock()

    def updateTaskStatus(self, taskId, status):
        self.storage[f'task-{taskId}'] = status

    def updateExecutedTask(self, worker, taskId):
        self.storage.lset('workersInfo', worker, taskId)

    def taskStatus(self, taskId):
        return self.storage.get(f'task-{taskId}').decode('utf-8') if f'task-{taskId}' in self.storage else None
    
    def taskProgress(self, taskId):
        return self.storage.get(f'progress-{taskId}').decode('utf-8') if f'task-{taskId}' in self.storage else None

    def setProgress(self, taskNumber, progress):
        self.storage[f'progress-{taskNumber}'] = progress
    
    def set(self, key,value):
        self.storage[key] = value

    def get(self, key):
        if key in self.storage:
            return self.storage.get(key).decode('utf-8')
        return None

    def getWorkerNumberByTask(self, taskId, start=0, end=-1):
        workersTask = [i.decode('utf-8') for i in self.storage.lrange('workersInfo', start, end)]
        if taskId in workersTask:
            return workersTask.index(taskId)
        return None

    def setCallbackForKeyChange(self, callback, pattern="*"):
        pubsub = self.storage.pubsub()
        pubsub.psubscribe(**{f'__keyspace@0__:{pattern}': callback})
        pubsub.run_in_thread(sleep_time=.01)
    
    # setters and getters for lists

    def createEmptyList(self, listName, size):
        self.storage.lpush(listName, *['' for i in range(0, size)])

    def pushToList(self, listName, value):
        self.storage.lpush(listName, value)
    
    def valuesFromList(self, listName, start=0, end=-1):
        return [i.decode('utf-8') for i in self.storage.lrange(listName, start, end)]

    def removeFromList(self, listName, element):
        return self.storage.lrem(listName, 1, element)

    def moveElement(self,/, fromList='', toList='', value=''):
        self.lock.acquire()
        if isinstance(fromList, list):
            for i in fromList:
                self.removeFromList(i, value)
        elif isinstance(fromList, str) and fromList != '':
            self.removeFromList(fromList, value)

        if toList != '':
            self.pushToList(toList, value)
        self.lock.release()
