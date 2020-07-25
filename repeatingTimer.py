import threading

# decorator for setThe
def createIterableFunction():
    def setInterval(interval):
        def decorator(func):
            def wrapper(*args, **kwargs):
                stopped = threading.Event()
                def loop():
                    while not stopped.wait(interval):
                        func(args, kwargs)
                t = threading.Thread(target=loop)
                # t.daemon = True
                t.start()
                return stopped
            return wrapper
        return decorator
    return setInterval

class iterableTimer():
    def __init__(self, interval, callback):
        createDecWithInterval = createIterableFunction()(interval);
        self.callback = createDecWithInterval(callback)


    def start(self):
        self.controller = self.callback()

    def stop(self):
        self.controller.set()

def main():
    def myCallback(args, kwargs):
        print('HELLO')

    myTimer = iterableTimer(1, myCallback)
    
    myTimer.start()

if __name__ == '__main__':
    main()