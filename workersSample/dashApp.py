import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import json
from dash.dependencies import Input, Output, State

from tools import componentCreator, WorkersManager
from taskSamples import taskManager

class dashApp(dash.Dash):
    def __init__(self, name):
        dash.Dash.__init__(self, name, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.m_taskCount = 4
        self._createLayout()
        # важная строчка, отключает все предупреждениях о коллбеках для несуществующих элементов
        self.config.suppress_callback_exceptions = True
        self.m_workerManager = WorkersManager.WorkersManager()

    def run_server(self, debug):
        dash.Dash.run_server(self,debug=debug);

    def _createLayout(self):
        # left part
        accordionItems = [
            componentCreator.createAccordionItem(self, i, upload_component = True, counter_component = True) for i in range (1, self.m_taskCount+1)
        ]
        componentCreator.subscribeTaskHandler(self, 'task-info', self.m_taskCount, task_callback=self._handleStartWorkRequest, handler_id='in-progress-task-container')
        componentCreator.generateCallbacksForTaskReports(self, max_task_report = 30)

        self.layout = html.Div(id='app-layout',children = [
            html.Div(
                id="task-creator",
                children=[
                    html.Label(children=[
                        'Task Creator'
                        ],
                        style={
                            'display': 'block',
                            'padding': '20px',
                            'font-weight': 'bolder',
                            'text-align':'center',
                        }
                    ),
                    *accordionItems,
                ],
                style={
                    'min-width':'450px',
                    'max-width': '500px',
                }
            ),
            html.Div(
                id="task-executor",
                children=[
                    html.Label(children=[
                        'Task Queue'
                        ],
                        style={
                            'display': 'block',
                            'padding': '20px',
                            'font-weight': 'bolder',
                            'text-align':'center',
                        }
                    ),
                    html.Div(
                        id="server-information",
                        style={
                            'padding': '5px',
                        }
                    ),
                    componentCreator.createContainerForTasks(self, containter_id='in-progress-task', header='In progress'),
                    componentCreator.createContainerForTasks(self, containter_id='done-task', header='Done'),
                    componentCreator.createContainerForTasks(self, containter_id='aborted-task', header='Aborted'),
                ],
                style={
                    'min-width':'450px',
                    'max-width': '500px',
                }
            ),
        ],
        style={
            'display':'flex',
            'flex-wrap': 'wrap',
            'justify-content': 'space-around',
            'overflow':  'hidden',
        }
        )

    def _handleStartWorkRequest(self, *args):
        callbackContext = dash.callback_context
        if not callbackContext.triggered:
            return ''
        
        triggeredItem =  callbackContext.triggered[0]
        taskInfo = triggeredItem['value']

        currentChildrens = args[-1]
        if (taskInfo != ''):
            print('!@#', taskInfo)
            taskInfo = json.loads(taskInfo)
            # need to start task and create an UI element
            taskId = self._startTask(taskInfo)
            currentChildrens.insert(int(0), componentCreator.createTaskReport(self, buinding_id=taskId, header=taskInfo['taskName']))
        return currentChildrens
        
        
    def _startTask(self, taskInfo):
        task = taskManager.provideTask(taskInfo['taskName'])
        # componentCreator.
        return self.m_workerManager.startTask(taskInfo, task)

if __name__=='__main__':
    app = dashApp(__name__)
    app.run_server(debug=True)