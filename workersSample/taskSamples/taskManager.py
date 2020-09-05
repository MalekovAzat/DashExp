from . import tasks

import base64
import io
from PIL import Image, ImageDraw

from tools.storageProvider import storageProvider as sp

def provideTask(taskName = '', storage = None):
    if taskName == 'random-noise':
        return tasks.randomNoise
    elif taskName == 'gray-shades':
        return tasks.grayShades
    else:
        return None

taskInfoList = [
    {
        'header': 'Random Noise',
        'name': 'random-noise',
        'desc': ''
    },
    {
        'header': 'Gray Shades',
        'name': 'gray-shades',
        'desc': ''
    },
    {
        'header': 'Task',
        'name': 'Name',
        'desc': ''
    },
]

def executeTask(taskData, savePath = 'download/'):

    print('!@#' ,taskData['taskName'])
    repeatCount = taskData['repValue']
    taskId = taskData['taskId']
    data = taskData['imageData'][0].encode("utf8").split(b";base64,")[1]
    byteImage = base64.b64decode(data)
    image = Image.open(io.BytesIO(byteImage))
    draw = ImageDraw.Draw(image)
    width = image.size[0]
    height = image.size[1]
    
    task = provideTask(taskData['taskName']) 

    pix = image.load()

    for i in range(0, int(repeatCount)):
        progress = int(i / repeatCount * 100)
        sp().setProgress(taskId, progress)
        pix = task(pix, draw, width, height)

    sp().setProgress(taskId, 100)
    savedPath = f'{savePath}result-{taskId}.jpg'
    image = image.convert('RGB')
    image.save(savedPath, 'JPEG')

def main():
    pass

if __name__=="__main__":
    main()