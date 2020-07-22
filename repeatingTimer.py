from threading import Timer as treadingTimer

def decoratorFactory():
    print('я создаю декораторы и буду вызван только 1 раз чтобы создать функцию')
    def decorator(func):
        print('я декоратор, и буду вызван единственный раз, когда меня используют перед методом')
        def wrapper(obj):
            print('я вызываюсь вместе с твоей функцией', obj)
            func(obj)
            obj.repeat()
        return wrapper
    return decorator

class repeatingTimer():
    def __init__(self, interval=0.01, callback=None):
        self.interval = interval
        self.callback = callback
        self.timer = treadingTimer(interval, self.callback_func)

    def start(self):
        self.timer.start()

    def repeat(self):
        self.timer = treadingTimer(self.interval, self.callback_func)
        self.start()

    def cancel(self):
        self.timer.cancel()

    def setInterval(self, interval):
        if (interval <= 0.1):
            return
        self.interval = interval
        self.timer = treadingTimer(interval, self.callback)

    def setCallback(self, callback):
        self.callback = callback
        self.timer = treadingTimer(self.interval, callback);
    
    @decoratorFactory()
    def callback_func(self):
        self.callback()


def main():
    def testCallback():
        print('test')

    myTimer = repeatingTimer(1, testCallback)
    myTimer.start()

if __name__ == '__main__':
    main()