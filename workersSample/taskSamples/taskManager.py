from . import tasks

import base64
import io
from PIL import Image, ImageDraw

def provideTask(taskName = '', storage = None):
    if taskName == 'randomNoise':
        return tasks.randomNoise
    elif taskName == 'grayShades':
        return tasks.grayShades
    else:
        return None

def executeTask(taskData ,taskNumber = 0, savePath = ''):
    repeatCount = taskData['repeatCount']
    data = taskData['imageData'][0].encode("utf8").split(b";base64,")[1]

    byteImage = base64.b64decode(data)
    image = Image.open(io.BytesIO(byteImage))
    draw = ImageDraw.Draw(image)
    width = image.size[0] #Определяем ширину. 
    height = image.size[1]
    
    task = provideTask(taskData['taskName'])    

    # storage[f'task-{taskNumber}-iterationCount'] = repeatCount
    pix = image.load()
    for i in range(0, int(repeatCount)):
        # storage[f'task-{taskNumber}-currentIteration'] = i
        pix = task(pix, draw, width, height)

    image=image.convert('RGB')
    image.save(f'{savePath}ResultFor-{taskNumber}.jpg', 'JPEG')

def main():
    pass

if __name__=="__main__":
    main()