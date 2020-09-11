import dash_devices
import dash_html_components as html
import dash_bootstrap_components as dbc
import json
from dash_devices.dependencies import Input, Output, State, MATCH, ALL

from tools import componentCreator as cc, WorkersManager as wm
from taskSamples import taskManager as tm
from tools.storageProvider import storageProvider as sp

import datetime

def redisCallback(message):
    print(message)


def getTaskId(message):
    return message['channel'].decode('utf-8').split(':')[1].split('-')[1]


class dashApp():
    def __init__(self, app):
        self.app = app
        self.app.config.suppress_callback_exceptions = True
        self.wm = wm.WorkersManager()
        sp().createEmptyList('workersInfo', 4)

        self.app.layout = html.Div([
            cc.createTaskListTemplate(self.app, tm.taskInfoList, self.taskButtonClickedCallback),
            cc.createReportListTemplate(self.app),
            cc.createBindingComponent(self.app, 'internal', self.updateReportListCallback),
            cc.createBindingProgressComponent(self.app, 'internal-progress', self.updateTaskProgressCallback),
            cc.createRefreshComponent(self.app, 'refresh-component', self.refreshCallback),
        ],
            style={
            'display': 'flex',
            'flex-wrap': 'wrap',
            'justify-content': 'space-around',
            'overflow':  'hidden',
        })

        self.createCallbacks()
        sp().setCallbackForKeyChange(self.rediskeyChangeCallback, 'task-*')
        sp().setCallbackForKeyChange(self.taskProgressChangeCallback, 'progress-*')

    def createCallbacks(self):
        @self.app.callback(
            Output({'type': 'abort-button', 'index': MATCH}, 'id'),
            [
                Input({'type': 'abort-button', 'index': MATCH}, 'n_clicks')
            ],
            [
                State({'type': 'abort-button', 'index': MATCH}, 'id'),
            ],
        )
        def f(n_clicks, buttonId):
            if (n_clicks):
                taskId = buttonId['index']
                self.wm.restartWorkerByTask(taskId)
                sp().updateTaskStatus(taskId, 'in-aborted')
            return buttonId

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

    def refreshCallback(self, val):
        return [
            cc.createInQueueList(), 
            cc.createInProgressList(),
            cc.createInCompletedList(),
            cc.createInAbortedList(),
        ]

    def updateTaskProgressCallback(self, taskInfo, inProgressList):
        taskId = taskInfo.split(':')[0].split('-')[1]
        taskProgress = int(float(taskInfo.split(':')[1]))
        return [
            Output(f'progress-{taskId}', 'value', taskProgress),
            Output(f'progress-{taskId}', 'children',
                   f'{taskProgress}%' if taskProgress >= 5 else '')
        ]

    def updateReportListCallback(self, taskInfo):
        taskId = taskInfo.split(':')[0].split('-')[1]
        taskStatus = taskInfo.split(':')[1]

        if taskStatus == 'in-queue':
            sp().moveElement(toList='in-queue', value=taskId)
            return Output('in-queue-list', 'children', cc.createInQueueList())

        elif taskStatus == 'in-progress':
            sp().moveElement(fromList='in-queue', toList='in-progress', value=taskId)
            return [
                Output('in-queue-list', 'children', cc.createInQueueList()),
                Output('in-progress-list', 'children',
                       cc.createInProgressList())
            ]
        elif taskStatus == 'in-completed':
            sp().moveElement(fromList='in-progress', toList='in-completed', value=taskId)
            return [
                Output('in-progress-list', 'children',
                       cc.createInProgressList()),
                Output('in-completed-list', 'children',
                       cc.createInCompletedList())
            ]
        elif taskStatus == 'in-aborted':
            sp().moveElement(fromList=[
                'in-progress', 'in-queue'], toList='in-aborted', value=taskId)
            return [
                Output('in-queue-list', 'children', cc.createInQueueList()),
                Output('in-progress-list', 'children',
                       cc.createInProgressList()),
                Output('in-aborted-list', 'children',
                       cc.createInAbortedList()),
            ]
        else:
            print(f'Bad task status {taskStatus} for task {taskId}')


if __name__ == '__main__':
    app = dashApp(__name__)
    app.run_server(debug=True, host='0.0.0.0', port=5000)
