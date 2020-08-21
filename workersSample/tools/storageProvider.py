import redis

class storageProvider(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(СomponentCreator, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.m_storage = redis.Redis()

    def set(self, key,value):
        self.m_storage[key] = value

    def get(self,key):
        if key in self.m_storage:
            return self.m_storage.get(key)
        return None

    def createDataForTask(taskNumber):
        self.m_storage[f'task-{self.m_lastTaskNumber}-progress'] = 0
        self.m_storage[f'task-{self.m_lastTaskNumber}-output'] = 0
    
    def resetDataForTast(taskNumber):
        pass