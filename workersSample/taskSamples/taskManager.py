from . import tasks

def provideTask(taskName = ''):
    if taskName == "randomNoise":
        return tasks.randomNoise
    else:
        return None

def main():
    pass

if __name__=="__main__":
    main()