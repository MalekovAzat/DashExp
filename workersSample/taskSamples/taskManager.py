from . import tasks

import base64
import io
from PIL import Image, ImageDraw
import numpy as np
import math
import json
import moviepy.editor

import numpy as np

from tools.storageProvider import storageProvider as sp

def provideTask(taskName = '', storage = None):
    if taskName == 'random-noise':
        return tasks.randomNoise
    elif taskName == 'gray-shades':
        return tasks.grayShades
    else:
        return None

# available values in uiInfo

taskInfoList = [
    # Gray shades task
    {
        'header': 'Gray Shades',
        'id': 'gray-shades',
        'desc': '',
        'interface': [
            {
                'name': 'upload',
                'id': 'gray-shades-upload',
                'prop': 'contents',
                'kargs': {
                    'multiple': False,
                }
            },
            {
                'id': 'gray-shades-input',
                'name': 'labelWithInput',
                'prop': 'value',
                'kargs': {
                    'labelText': 'Number of repetitions',
                }
            },
            {
                'id': 'gray-shades-start-button',
                'name': 'button',
                'prop': 'n_clicks',

                'kargs': {
                    'text': 'Start Task'
                }
            }
        ]
    },
    # Calculate k*sin(2*x)
    {
        'header': 'Calculate k*sin(2*x)',
        'id': 'calc-sin',
        'desc': 'Drowing chart for k*sin(x)',
        'interface': [
            {
                'id': 'calc-sin-input-1',
                'name': 'labelWithInput',
                'prop': 'value',
                
                'kargs': {
                    'labelText': 'Left border',
                }
            },
            {
                'id': 'calc-sin-input-2',
                'name': 'labelWithInput',
                'prop': 'value',
                
                'kargs': {
                    'labelText': 'Right border',
                }
            },
            {
                'id': 'calc-sin-input-3',
                'name': 'labelWithInput',
                'prop': 'value',
                
                'kargs': {
                    'labelText': 'Coefficient',
                }
            },
            {
                'id': 'calc-sin-input-4',
                'name': 'labelWithInput',
                'prop': 'value',
                
                'kargs': {
                    'labelText': 'Count of points',
                }
            },
            {
                'id': 'calc-sin-start-button',
                'name': 'button',
                'prop': 'n_clicks',
                
                'kargs': {
                    'text': 'Start Task'
                }
            }
        ]
    },
    # Read the table
    {
        'header': 'Read the table',
        'id': 'read-table',
        'desc': '',
        'interface': [
            {
                'id': 'read-table-upload',
                'name': 'upload',
                'prop': 'contents',

                'kargs': {
                    'multiple': False,
                }
            },
            {
                'id': 'read-table-start-button',
                'name': 'button',
                'prop': 'n_clicks',

                'kargs': {
                    'text': 'Start Task'
                }
            }
        ]
    },
    # Video by images
    {
        'header': 'Video by images',
        'id': 'video-by-image',
        'desc': '',
        'interface': [
            {
                'id': 'video-by-image-upload',
                'name': 'upload',
                'prop': 'contents',

                'kargs': {
                    'multiple': True,
                }
            },
            {
                'id': 'video-by-image-start-button',
                'name': 'button',
                'prop': 'n_clicks',

                'kargs': {
                    'text': 'Start Task'
                }
            }
        ]
    }
]


def executeTask(task):
    taskName = task['taskName']

    if not taskName:
        return

    if taskName == 'gray-shades':
        imageTask(task)
    elif taskName == 'calc-sin':
        calcSinTask(task)
    elif taskName == 'read-table':
        readTable(task)
    elif taskName == 'video-by-image':
        videoByImageTask(task)
    else:
        print('Invalid task name')
        return

def imageTask(taskInfo, savePath = 'download/'):
    repeatCount = taskInfo['args'][1]
    taskId = taskInfo['taskId']
    data = taskInfo['args'][0].encode("utf8").split(b";base64,")[1]
    byteImage = base64.b64decode(data)
    image = Image.open(io.BytesIO(byteImage))
    draw = ImageDraw.Draw(image)
    width = image.size[0]
    height = image.size[1]
    pix = image.load()
    task = provideTask(taskInfo['taskName'])

    for i in range(0, int(repeatCount)):
        progress = int(i / repeatCount * 100)
        sp().setProgress(taskId, progress)
        pix = task(pix, draw, width, height)

    sp().setProgress(taskId, 100)
    savedPath = f'{savePath}result-{taskId}.jpg'
    image = image.convert('RGB')
    image.save(savedPath, 'JPEG')
    sp().setInfo(taskId, [savedPath, taskInfo['taskName']])

def calcSinTask(taskInfo):
    taskId = taskInfo['taskId']
    leftBorder = float(taskInfo['args'][0])
    rightBorder = float(taskInfo['args'][1])
    coeff = float(taskInfo['args'][2])
    counOfPoints = int(float(taskInfo['args'][3]))
    xRange = np.linspace(leftBorder, rightBorder, num=counOfPoints).tolist()

    def calcSin(x, coeff):
        return coeff*math.sin(2 * x)

    sinValues = []
    for x in xRange:
        sinValues.append(calcSin(x, coeff)) 

    sp().setProgress(taskId, 100)
    sp().setInfo(taskId, [json.dumps({'x': xRange, 'y': sinValues}), taskInfo['taskName']])
    
def readTable(taskInfo):
    taskId = taskInfo['taskId']
    sp().setProgress(taskId, 100)
    sp().setInfo(taskId, [taskInfo['args'][0], taskInfo['taskName']])
    
def videoByImageTask(taskInfo, savePath='download/'):
    taskId = taskInfo['taskId']

    writeToPath = f'{savePath}task-{taskId}.mp4'

    imageInfoList = taskInfo['args'][0]

    # gif = []
    images = []

    for image in imageInfoList:
        data = image.encode("utf8").split(b";base64,")[1]
        byteImage = base64.b64decode(data)
        image = Image.open(io.BytesIO(byteImage))
        image = image.convert("RGB")
        image = np.asarray(image, dtype=np.float32)
        image = image[:, :, :3]
        images.append(image)

    print(images[0].shape)
    # images = np.array(image).shape
    clip = moviepy.editor.ImageSequenceClip(images, fps=10)

    clip.write_videofile(writeToPath)
    # gif[0].save(writeToPath, save_all=True, optimize=False, append_images=gif[1:], loop=0)

    sp().setProgress(taskId, 100)
    sp().setInfo(taskId, [writeToPath, taskInfo['taskName']])

def main():
    pass

if __name__=="__main__":
    main()