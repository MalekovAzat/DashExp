from redis import StrictRedis

class storageProvider(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(storageProvider, cls).__new__(cls)
        return cls.instance

    def __init__(self, max_reports_count = 100):
        self.storage = StrictRedis(host='localhost', port=6379)
        
    def updateTaskStatus(self, taskId, status):
        self.storage[f'task-{taskId}'] = status

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

    def setCallbackForKeyChange(self, callback, pattern="*"):
        pubsub = self.storage.pubsub()
        pubsub.psubscribe(**{f'__keyspace@0__:{pattern}': callback})
        pubsub.run_in_thread(sleep_time=.01)
    
    # def createData(self, taskNumber):
    #     self.m_storage[f'task-{taskNumber}-progress'] = ''
    #     self.m_storage[f'task-{taskNumber}-output'] = ''
    #     self.m_storage[f'task-{taskNumber}-status'] = self.m_status['executing']

    # def setOutput(self, taskNumber, output):
    #     self.m_storage[f'task-{taskNumber}-output'] = output

    # def setCompeted(self, taskNumber):
    #     self.m_storage[f'task-{taskNumber}-status'] = self.m_status['complited']
    
    # def setAborted(self, taskNumber):
    #     self.m_storage[f'task-{taskNumber}-status'] = self.m_status['aborted']

    # def resetDataForTest(self, taskNumber):
    #     pass