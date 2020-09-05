import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import json
from dash_devices.dependencies import Input, Output, State

from tools import componentCreator as cc, WorkersManager as wm
from taskSamples import taskManager as tm
from tools.storageProvider import storageProvider as sp

def redisCallback(message):
    print(message)

def getTaskId(message):
    return message['channel'].decode('utf-8').split(':')[1].split('-')[1]

class dashApp():
    def __init__(self, app):
        
        self.app = app

        # TODO: на этом моменте должны запуститься 4 потока
        self.wm = wm.WorkersManager()

        self.app.layout = html.Div([
            cc.createTaskListTemplate(self.app, tm.taskInfoList, self.taskButtonClickedCallback),
            cc.createReportListTemplate(self.app),
            cc.createBindingComponent(self.app, 'internal', self.updateReportListCallback),
            cc.createBindingProgressComponent(self.app, 'internal-progress', self.updateTaskProgressCallback)
        ],
        style={
            'display':'flex',
            'flex-wrap': 'wrap',
            'justify-content': 'space-around',
            'overflow':  'hidden',
        })  

        # важная строчка, отключает все предупреждениях о коллбеках для несуществующих элементов
        self.app.config.suppress_callback_exceptions = True
        sp().setCallbackForKeyChange(self.rediskeyChangeCallback, 'task-*')
        sp().setCallbackForKeyChange(self.taskProgressChangeCallback, 'progress-*')

    def taskButtonClickedCallback(self, n_clicks, repValue, imageData, taskName):
        if repValue and imageData:
            task = {
                'repValue': repValue,
                'imageData': imageData,
                'taskName': taskName
            }
            self.wm.push(task)

    def rediskeyChangeCallback(self, message):
        taskId = getTaskId(message)
        self.app.push_mods({
            'internal': {
                'children': f'task-{taskId}:{sp().taskStatus(taskId)}'
            }
        })

    def taskProgressChangeCallback(self, message):
        taskId = getTaskId(message)
        self.app.push_mods({
            'internal-progress': {
                'children': f'progress-{taskId}:{sp().taskProgress(taskId)}'
            }
        })
        
    def updateTaskProgressCallback(self, taskInfo, inProgressList):
        taskId = taskInfo.split(':')[0].split('-')[1]
        taskProgress = float(taskInfo.split(':')[1])
        return [
            Output(f'progress-{taskId}', 'value', taskProgress),
            Output(f'progress-{taskId}', 'children', f'{taskProgress}%' if taskProgress >= 5 else '')
        ]

    # построение UI элемента
    def updateReportListCallback(self, taskInfo, inQueueList, inProgressList, inCompletedList, inAbortedList):
        taskId = taskInfo.split(':')[0].split('-')[1]
        taskStatus = taskInfo.split(':')[1]

        if taskStatus == None:
            print('Bad task Id', taskId)
            return
        if taskStatus == 'in-queue':
            return Output('in-queue-list', 'children', self.addInQueueList(taskId, inQueueList))

        elif taskStatus == 'in-progress':
            return [
                Output('in-queue-list', 'children', self.removeFromList(taskId, inQueueList)),
                Output('in-progress-list', 'children', self.addInProgressList(taskId, inProgressList))
            ]
        elif taskStatus == 'in-completed':
            return [
                Output('in-progress-list', 'children', self.removeFromList(taskId, inProgressList)),
                Output('in-completed-list', 'children', self.addInCompletedList(taskId, inCompletedList))
            ]
        elif taskStatus == 'in-aborted':
            return [
                Output('in-queue-list', 'children', self.removeFromList(taskId, inQueueList)),
                Output('in-progress-list', 'children', self.removeFromList(taskId, inProgressList)),
                Output('in-aborted-list', 'children', self.addInAbortedList(taskId, inAbortedList))
            ]
        else:
            print(f'Bad task status {taskStatus} for task {taskId}')
    
    def addInQueueList(self, taskId, childList):
        childList.insert(0, cc.createTaskInQueueReport(taskId))
        return childList
    
    def addInProgressList(self, taskId, childList):
        childList.insert(0, cc.createTaskInProgressReport(taskId))
        return childList

    def addInCompletedList(self, taskId, childList):
        childList.insert(0, cc.createTaskInCompletedReport(taskId))
        return childList

    def addInAbortedList(self, taskId, childList):
        childList.insert(0, cc.createTaskInAbortedReport(taskId))
        return childList
    
    # TODO: распарсить элемент правильно чтобы там можно было получить объект
    #  common method
    def removeFromList(self, taskId, childList):
        taskName = f'task-{taskId}'
        removedCard = None
        """ Template of list
        [
           {
              "props": {
                 "children": [
                    {
                       "props": {
                          "children": "Task 3",
                          "style": {
                             "padding": "10px"
                          }
                       },
                       "type": "P",
                       "namespace": "dash_html_components"
                    },
                    {
                       "props": {
                          "children": "added: 02/09/2020 23:50:37",
                          "className": "text-secondary",
                          "style": {
                             "margin-left": "10px",
                             "font-size": "0.8em"
                          }
                       },
                       "type": "P",
                       "namespace": "dash_html_components"
                    }
                 ],
                 "id": "task-3",
                 "className": "shadow bg-light",
                 "style": {
                    "padding": "5px",
                    "margin": "10px 0",
                    "border-radius": "5px"
                 }
              },
              "type": "Div",
              "namespace": "dash_html_components"
           },
           {
              "props": {},
              "type": "Div",
              "namespace": "dash_html_components"
           }
        ]
        """
        for cardIndex in range(0, len(childList)):
            if childList[cardIndex]['props']['id'] == taskName:
                removedCard = childList[cardIndex]
            
        if removedCard != None:
            childList.remove(removedCard)
        return childList

if __name__=='__main__':
    app = dashApp(__name__)
    app.run_server(debug=True, host='0.0.0.0', port=5000)