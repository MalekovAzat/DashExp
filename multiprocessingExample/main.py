import multiprocessing as mp
import time 
# заупустить 8 воркеров и поставить их в ожидание пока в очереди не появится новое задание, если появится то пускаем по новой

# буем передавать словарь?
def taskImitation(condition, dataPool):
    while True:
        print('start')
        condition.acquire()
        condition.wait()
        print(dataPool.get())
        condition.release()

def producer(condition, dataPool):
    while True:
        condition.acquire()
        print('start creating something')
        time.sleep(5)
        for i in range(0,10):
            dataPool.put(i)
        condition.notify_all()
        condition.release()

def main():
    # создаем пулл процессов
    condition = mp.Condition()
    dataPool = mp.Queue(1000)
    print(condition)
    workers = [mp.Process(target=taskImitation, args=(condition, dataPool)) for i in range(1, 9)]
    producerW = mp.Process(target=producer, args=(condition, dataPool))
    producerW.start()
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()

    print('hello')
if __name__=='__main__':
    main()