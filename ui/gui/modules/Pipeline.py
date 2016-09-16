from collections import OrderedDict
import collections
import json
import time

from PyQt4 import QtCore, QtGui

from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.Module import CcpnModule
from ccpn.ui.gui.widgets.GroupBox import GroupBox
from ccpn.ui.gui.widgets.Icon import Icon
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.ScrollArea import ScrollArea
from ccpn.ui.gui.widgets.FileDialog import FileDialog
from ccpn.ui.gui.widgets.RadioButtons import RadioButtons

from ccpn.AnalysisMetabolomics.ui.gui.widgets.PipelineWidgets import PipelineDropArea, PipelineBox


Qt = QtCore.Qt
Qkeys = QtGui.QKeySequence

# styleSheets
transparentStyle = "background-color: transparent; border: 0px solid transparent"
selectMethodLabel = '< Select Method >'


class PipelineWorker(QtCore.QObject):
  'Object managing the  auto run pipeline simulation'

  stepIncreased = QtCore.pyqtSignal(int)


  def __init__(self):
    super(PipelineWorker, self).__init__()
    self._step = 0
    self._isRunning = True
    self._maxSteps = 200000


  def task(self):
    if not self._isRunning:
      self._isRunning = True
      self._step = 0

    while self._step < self._maxSteps and self._isRunning == True:
      self._step += 1
      self.stepIncreased.emit(self._step)
      time.sleep(0.1)  # if this time is too small or disabled you won't be able to stop the thread!


  def stop(self):
    self._isRunning = False
    print('Pipeline Thread stopped')



class GuiPipeline(CcpnModule):

  def __init__(self, application=None, pipelineMethods=None, project=None, templates=None, **kw):
    super(GuiPipeline, self)

    nameCount = 0
    for module in application.ui.mainWindow.moduleArea.findAll()[1].values():
      if hasattr(module, 'runPipeline'):
        nameCount += 1

    name = 'Pipeline-' + str(nameCount)

    self.project = project
    self.application = application
    self.mainWindow = application.ui.mainWindow

    self.generalPreferences = self.application.preferences.general
    self.templatePath = self.generalPreferences.auxiliaryFilesPath
    self.currentPipelineBoxNames = []
    self.pipelineSettingsParams = OrderedDict([('name', 'NewPipeline'),
                                               ('rename', 'NewPipeline'),
                                               ('savePath', str(self.generalPreferences.dataPath)),
                                               ('autoRun', False),('addPosit', 'bottom'),
                                               ('autoActive', True),])

    self.templates = self._getPipelineTemplates(templates)
    self.pipelineMethods = self._getPipelineMethods()

    CcpnModule.__init__(self, name=name)

    self._setIcons()
    self._setMainLayout()
    self._setPipelineThread()
    self._setSecondaryLayouts()
    self.pipelineWorker.stepIncreased.connect(self.runPipeline)
    self.currentRunningPipeline = []


  def _setModuleName(self):
    pipelineModules = []
    for module in self.mainWindow.moduleArea.findAll()[1].values():
      print(module)
      if hasattr(module, 'GuiPipeline'):
        print('GuiPipeline')
      if hasattr(module, 'runPipeline'):
        print('runPipeline')
      if isinstance(module, self):
        print('isIST')



  def _getPipelineMethods(self):
    '''
    methods = {name: object}
    name = str will appear in the method pulldown
    obj = any subclass of pipeline Box
    '''
    from ccpn.framework.lib.ExtensionLoader import getPipes

    extensions = getPipes()
    if extensions:
      return {extension.METHODNAME:extension for extension in extensions}
    else:
      return {}


  def _getPipelineTemplates(self, templates):
    if templates is not None:
      return templates
    else:
      return {'Empty':'Empty'}


  def _setAppSpecificMethods(self):
    '''set data in pull down if selected application specific method '''
    filteredMethod = [selectMethodLabel,]
    for method in self.pipelineMethods.values():
      if hasattr(method, 'applicationsSpecific'):
        applicationsSpecific = method.applicationsSpecific(method)
        if self.application.applicationName in applicationsSpecific:
          filteredMethod.append(method.methodName(method))
    self.methodPulldown.setData(sorted(filteredMethod))


  def keyPressEvent(self, KeyEvent):
    if KeyEvent.key() == Qt.Key_Enter:
      self.runPipeline()


  def _setIcons(self):
    self.settingIcon = Icon('icons/applications-system')
    self.saveIcon = Icon('icons/save')
    self.openRecentIcon = Icon('icons/document_open_recent')
    self.goIcon = Icon('icons/play')
    self.stopIcon = Icon('icons/stop')
    self.filterIcon = Icon('icons/edit-find')


  def _setMainLayout(self):
    self.mainFrame = QtGui.QFrame()
    self.mainLayout = QtGui.QVBoxLayout()
    self.mainFrame.setLayout(self.mainLayout)
    self.layout.addWidget(self.mainFrame, 0,0,0,0)


  def _setSecondaryLayouts(self):
    self.settingFrameLayout = QtGui.QHBoxLayout()
    self.goAreaLayout = QtGui.QHBoxLayout()
    self.pipelineAreaLayout = QtGui.QHBoxLayout()
    self.mainLayout.addLayout(self.settingFrameLayout)
    self.mainLayout.addLayout(self.goAreaLayout)
    self.mainLayout.addLayout(self.pipelineAreaLayout)
    self._createSettingButtonGroup()
    self._createPipelineWidgets()
    self._createSettingWidgets()


  def _createSettingButtonGroup(self):
    self.pipelineNameLabel = Label(self, 'NewPipeline')
    self.settingButtons = ButtonList(self, texts=['', '', ''],
                                     callbacks=[self._openSavedPipeline, self._savePipeline , self.settingsPipelineWidgets],
                                     icons=[self.openRecentIcon, self.saveIcon, self.settingIcon],
                                     tipTexts=['', '', '' ], direction='H')
    self.settingFrameLayout.addWidget(self.pipelineNameLabel)

    self._addMenuToOpenButton()
    self.settingButtons.setStyleSheet(transparentStyle)
    self.settingFrameLayout.addStretch(1)
    self.settingFrameLayout.addWidget(self.settingButtons)


  def _setPipelineThread(self):
    self.pipelineThread = QtCore.QThread()
    self.pipelineThread.start()
    self.pipelineWorker = PipelineWorker()
    self.pipelineWorker.moveToThread(self.pipelineThread)


  def openJsonFile(self, path):
    if path is not None:
      with open(str(path), 'r') as jf:
        data = json.load(jf)
      return data


  def _getPathFromDialogBox(self):
    dialog = FileDialog(self, text="Open Pipeline",
                        acceptMode=FileDialog.AcceptOpen, preferences=self.generalPreferences)
    return dialog.selectedFile()


  def _getPipelineBoxesFromFile(self, params, boxesNames):
    pipelineBoxes = []
    for i in params:
      for key, value in i.items():
        if value[0].upper() in boxesNames:
          pipelineMethod = self.pipelineMethods[key]
          pipelineBox = pipelineMethod(parent=self, name = value[0], params = value[1],  project=self.project)
          pipelineBox.setActive(value[2])
          pipelineBoxes.append(pipelineBox)
    return pipelineBoxes


  def _openSavedPipeline(self):
    path = self._getPathFromDialogBox()
    state, params, boxesNames, pipelineSettings = self.openJsonFile(path)
    pipelineBoxes = self._getPipelineBoxesFromFile(params, boxesNames)
    self._closeExistingPipelineBoxes()
    for pipelineBox in pipelineBoxes:
      self.pipelineArea.addBox(pipelineBox)
    self.pipelineArea.restoreState(state)
    self.pipelineSettingsParams = OrderedDict(pipelineSettings)
    self._setSettingsParams()


  def _addMenuToOpenButton(self):
    openButton = self.settingButtons.buttons[0]
    menu = QtGui.QMenu()
    templatesItem = menu.addAction('Templates')
    subMenu = QtGui.QMenu()
    if self.templates is not None:
      for item in self.templates.keys():
        templatesSubItem = subMenu.addAction(item)
      openItem = menu.addAction('Open...', self._openSavedPipeline)
      templatesItem.setMenu(subMenu)
    openButton.setMenu(menu)


  def _closeExistingPipelineBoxes(self):
    boxes = self.pipelineArea.findAll()[1].values()
    if len(boxes)>0:
      for box in boxes:
        box.closeBox()


  def _savePipeline(self):
    '''jsonData = [{pipelineArea.state}, [boxes widgets params], [currentBoxesNames], pipelineSettingsParams]   '''
    currentBoxesNames = list(self.pipelineArea.findAll()[1].keys())
    if len(currentBoxesNames)>0:
      self.jsonData = []
      self.widgetsParams = self._pipelineBoxesWidgetParams(currentBoxesNames)
      self.jsonData.append(self.pipelineArea.saveState())
      self.jsonData.append(self.widgetsParams)
      self.jsonData.append(currentBoxesNames)
      self.jsonData.append(list(self.pipelineSettingsParams.items()))

      self._saveToJson()


  def _saveToJson(self):
    self.jsonPath = str(self.savePipelineLineEdit.text()) + '/' + str(self.pipelineNameLabel.text()) + '.json'
    with open(self.jsonPath, 'w') as fp:
      json.dump(self.jsonData, fp, indent=2)
      fp.close()
    print('File saved in: ', self.jsonPath)


  def _createPipelineWidgets(self):
    self._addMethodPullDownWidget()
    self._addGoButtonWidget()
    self._addPipelineDropArea()


  def _addMethodPullDownWidget(self):
    self.methodPulldown = PulldownList(self, )
    self.methodPulldown.setMinimumWidth(200)
    self.goAreaLayout.addWidget(self.methodPulldown)
    self.setMethodPullDownData()
    self.methodPulldown.installEventFilter(self)


  def setMethodPullDownData(self):
    self.methodPulldownData = [k for k in sorted(self.pipelineMethods.keys())]
    self.methodPulldownData.insert(0, selectMethodLabel)
    self.methodPulldown.setData(self.methodPulldownData)
    self.methodPulldown.activated[str].connect(self._selectMethod)


  def eventFilter(self, source, event):
    '''Filter to disable the wheel event in the methods pulldown. Otherwise each scroll would add a box!'''
    if event.type() == QtCore.QEvent.Wheel:
      return True
    return False


  def _addGoButtonWidget(self):
    '''
    First Two button are reserved for autoRun mode. They are hidden if the setting autoRun is not checked.
    NB the stop callback needs to be a lambda call

    '''
    self.goButton = ButtonList(self, texts=['','',''],icons=[self.stopIcon, self.goIcon, self.goIcon,],
                               callbacks=[lambda:self.pipelineWorker.stop(), self.pipelineWorker.task, self.runPipeline])
    self.goButton.buttons[0].hide()
    self.goButton.buttons[1].hide()
    self.goButton.setStyleSheet(transparentStyle)
    self.goAreaLayout.addWidget(self.goButton, )
    self.goAreaLayout.addStretch(1)


  def _addPipelineDropArea(self):
    self.pipelineArea = PipelineDropArea()
    scroll = ScrollArea(self)
    scroll.setWidget(self.pipelineArea)
    scroll.setWidgetResizable(True)
    self.pipelineAreaLayout.addWidget(scroll)


  def runPipeline(self):
    self.currentRunningPipeline = [('init', None)]  # TODO: Fix this so it feeds an initial DF in
    if len(self.pipelineArea.findAll()[1])>0:
      widgets = self.pipelineArea.orderedBoxes(self.pipelineArea.topContainer)
      for widget in widgets:
        if widget.isActive():
          # TODO: Handle various types of input here, for now, a DF is all
          pipe = widget.pipe
          result = pipe.run(self.currentRunningPipeline[-1][1], **pipe._kwargs)
          method = (pipe, result)
          self.currentRunningPipeline.append(method)


  def _selectMethod(self, selected):

    if str(selected) == selectMethodLabel:
      return

    boxName = self._getSerialName(str(selected))
    self._addMethodBox(boxName, selected)
    self.methodPulldown.setIndex(0)


  def _getSerialName(self, boxName):
    self.currentPipelineBoxNames.append(boxName)
    count = len(self.pipelineArea.findAll()[1])
    if count == 0:
      self.currentPipelineBoxNames = []
    counter = collections.Counter(self.currentPipelineBoxNames)
    return str(boxName) + '-' + str(counter[str(boxName)])


  def _addMethodBox(self, name, selected):
    # This is where we should extract the GUI part of the extension, or create one if needed.
    objMethod = self.pipelineMethods[selected](application=self.application)
    position = self.pipelineSettingsParams['addPosit']

    try:
      pipelineWidget = objMethod.guiModule(parent=self, name=name, params=None, project=self.project)
    except (AttributeError, TypeError):
      pipelineWidget = self._autoGeneratePipelineWidget(objMethod)

    # self.pipelineArea.addDock(pipelineWidget, position=position)
    self.pipelineArea.addPipe(objMethod, position=position)
    autoActive = self.pipelineSettingsParams['autoActive']
    pipelineWidget.label.checkBox.setChecked(autoActive)


  def _autoGeneratePipelineWidget(self, objMethod):
    from functools import partial
    objMethod.widget = widget = PipelineBox(parent=self, pipe=objMethod)
    # ndac = self._getNonDefaultArgCount(objMethod.run) -1  # -1 so we don't count the self arg
    #
    params = objMethod.params
    if params is not None:

      columns = 4
      from collections import Mapping, Iterable
      from ccpn.ui.gui.widgets.Label import Label
      for i, param in enumerate(params):
        assert isinstance(param, Mapping)

        row = int(i/columns)
        column = i%columns

        from ccpn.ui.gui.widgets.Frame import Frame
        frame = Frame(widget)
        frame.setObjectName('autoGeneratedFrame')
        frameColour = '#BEC4F3' if self.application.preferences.general.colourScheme == 'dark' else '#000000'
        frame.setStyleSheet('Frame#autoGeneratedFrame {{margin:5px; border:1px solid {};}}'.format(frameColour))
        widget.mainLayout.addWidget(frame, row, column)

        l = Label(frame, param.get('label', param['variable']), grid=(0, 0))
        l.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        if isinstance(param['value'], str):
          from ccpn.ui.gui.widgets.LineEdit import LineEdit
          le = LineEdit(frame, text=param['value'], grid=(0, 1))
          callback = partial(objMethod._updateRunArgs, param['variable'])
          le.textChanged.connect(callback)
          callback(le.get())

        elif isinstance(param['value'], bool):
          from ccpn.ui.gui.widgets.CheckBox import CheckBox
          cb = CheckBox(frame, grid=(0, 1))
          cb.setChecked(param['value'])
          callback = partial(objMethod._updateRunArgs, param['variable'], cb.get())
          cb.setCallback(callback)
          callback()

        elif isinstance(param['value'], Iterable):
          if isinstance(param['value'][0], str):
            from ccpn.ui.gui.widgets.PulldownList import PulldownList
            pdl = PulldownList(frame, texts=param['value'], grid=(0, 1))
            pdl.set(param.get('default', param['value'][0]))
            callback = partial(objMethod._updateRunArgs, param['variable'])
            pdl.setCallback(callback)
            callback(pdl.get())

          elif isinstance(param['value'][0], Iterable):
            assert all([len(v)==2 for v in param['value']])
            assert all([isinstance(v[0], str) for v in param['value']])
            from ccpn.ui.gui.widgets.PulldownList import PulldownList
            t, o = zip(*param['value'])
            pdl = PulldownList(frame, texts=t, objects=o, grid=(0, 1))
            pdl.set(param.get('default', param['value'][0]))
            callback = partial(objMethod._updateRunArgs, param['variable'])
            pdl.setCallback(callback)
            callback(pdl.get())

          elif isinstance(param['value'][0], int):
            assert len(param['value']) == 2
            from ccpn.ui.gui.widgets.Spinbox import Spinbox
            sb = Spinbox(frame, min=param['value'][0], max=param['value'][1], grid=(0, 1))
            sb.setSingleStep(param.get('stepsize', 1))
            sb.setValue(param.get('default', param['value'][0]))
            callback = partial(objMethod._updateRunArgs, param['variable'])
            sb.valueChanged.connect(callback)
            callback(sb.value())

          elif isinstance(param['value'][0], float):
            assert len(param['value']) == 2
            from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
            dsb = DoubleSpinbox(frame, min=param['value'][0], max=param['value'][1], grid=(0, 1))
            defaultStepSize = (param['value'][1] - param['value'][0])/100
            dsb.setSingleStep(param.get('stepsize', defaultStepSize))
            dsb.setValue(param.get('default', param['value'][0]))
            callback = partial(objMethod._updateRunArgs, param['variable'])
            dsb.valueChanged.connect(callback)
            callback(dsb.value())
          else:
            raise NotImplementedError(param)
        else:
          raise NotImplementedError(param)

    return widget

  def _getNonDefaultArgCount(self, f:callable) -> int:  # TODO: Move this to util
    import inspect
    count = 0
    sig = inspect.signature(f)
    for _, p in sig.parameters.items():
      if p.default == inspect._empty:
        count += 1
    return count

  def _anyArgsVarPositional(self, f:callable) -> int:
    import inspect
    sig = inspect.signature(f)
    for _, p in sig.parameters.items():
      if p.kind == inspect._ParameterKind.VAR_POSITIONAL:
        return True
    return False


  ''' PIPELINE SETTINGS '''

  def _pipelineBoxesWidgetParams(self, currentBoxesNames):
    self.savePipelineParams = []
    for boxName in currentBoxesNames:
      boxMethod = self.pipelineArea.docks[str(boxName)]
      state = boxMethod.isActive()
      params = boxMethod.getWidgetsParams()
      newDict = {boxMethod.methodName(): (boxName, params, state)}
      self.savePipelineParams.append(newDict)
    return self.savePipelineParams


  def _createSettingWidgets(self):
    self.settingsWidgets = []
    self._createSettingsGroupBox()
    self._createAllSettingWidgets()
    self._addWidgetsToLayout(self.settingsWidgets, self.settingWidgetsLayout)
    self.settingFrame.hide()
    self._hideSettingWidget()
    self._setSettingsParams()


  def _createSettingsGroupBox(self):
    self.settingFrame = GroupBox('Pipeline Settings')
    self.settingFrame.setMaximumWidth(300)
    self.settingWidgetsLayout = QtGui.QGridLayout()
    self.settingFrame.setLayout(self.settingWidgetsLayout)
    self.pipelineAreaLayout.addWidget(self.settingFrame, 1)


  def _createAllSettingWidgets(self):
    # R0w 0
    self.pipelineReNameLabel = Label(self, 'Name')
    self.settingsWidgets.append(self.pipelineReNameLabel)
    self.pipelineReNameTextEdit = LineEdit(self, str(self.pipelineNameLabel.text()))
    self.settingsWidgets.append(self.pipelineReNameTextEdit)
    # R0w 1
    self.inputDataLabel = Label(self, 'Input Data')
    self.settingsWidgets.append(self.inputDataLabel)
    self.inputDataPulldownList = PulldownList(self, '')
    self.settingsWidgets.append(self.inputDataPulldownList)
    # R0w 2
    self.autoLabel = Label(self, 'Auto Run')
    self.settingsWidgets.append(self.autoLabel)
    self.autoCheckBox = CheckBox(self,)
    self.settingsWidgets.append(self.autoCheckBox)
    # R0w 3
    self.savePipelineLabel = Label(self, 'Save in')
    self.settingsWidgets.append(self.savePipelineLabel)
    self.savePipelineLineEdit = LineEdit(self, '')
    self.settingsWidgets.append(self.savePipelineLineEdit)
    # R0w 4
    self.addBoxLabel = Label(self, 'Add Method On')
    self.settingsWidgets.append(self.addBoxLabel)
    self.addBoxPosition = RadioButtons(self,texts=['top', 'bottom'], selectedInd=0,direction='h')
    self.addBoxPosition.setMaximumHeight(20)
    self.settingsWidgets.append(self.addBoxPosition)
    # R0w 5
    self.autoActiveLabel = Label(self, 'Auto active')
    self.settingsWidgets.append(self.autoActiveLabel)
    self.autoActiveCheckBox = CheckBox(self, )
    self.autoActiveCheckBox.setChecked(True)
    self.settingsWidgets.append(self.autoActiveCheckBox)

    # R0w 6
    self.filter = Label(self, 'Methods filter')
    self.settingsWidgets.append(self.filter)
    self.filterButton = Button(self, icon = self.filterIcon, callback = self.filterMethodPopup)
    self.filterButton.setStyleSheet(transparentStyle)
    self.settingsWidgets.append(self.filterButton)

    # R0w 7
    self.spacerLabel = Label(self, '')
    self.spacerLabel.setMaximumHeight(1)
    self.settingsWidgets.append(self.spacerLabel)
    self.applyCancelsettingButtons = ButtonList(self, texts=['Cancel', 'Ok'],callbacks=[self._cancelSettingsCallBack, self._okSettingsCallBack], direction='H')
    self.settingsWidgets.append(self.applyCancelsettingButtons)


  def settingsPipelineWidgets(self):
    if self.settingFrame.isHidden():
      self._showSettingWidget()
    else:
      self._cancelSettingsCallBack()


  def _updateSettingsParams(self):
    name = str(self.pipelineReNameTextEdit.text())
    rename = str(self.pipelineReNameTextEdit.text())
    savePath = str(self.savePipelineLineEdit.text())
    autoRun = self.autoCheckBox.get()
    addPosit = self.addBoxPosition.get()
    autoActive = self.autoActiveCheckBox.get()

    params = OrderedDict([
      ('name', name),
      ('rename', rename),
      ('savePath', savePath),
      ('autoRun', autoRun),
      ('addPosit', addPosit),
      ('autoActive', autoActive)
    ])
    self.pipelineSettingsParams = params


  def _setSettingsParams(self):
    widgets = [self.pipelineNameLabel.setText, self.pipelineReNameTextEdit.setText,
               self.savePipelineLineEdit.setText, self.autoCheckBox.setChecked, self.addBoxPosition.set]

    for widget, value in zip(widgets, self.pipelineSettingsParams.values()):
      widget(value)


  def _renamePipeline(self):
    self.pipelineName = self.lineEdit.text()


  def _okSettingsCallBack(self):
    self._displayStopButton()
    self._updateSettingsParams()
    self._setSettingsParams()
    self._hideSettingWidget()


  def _cancelSettingsCallBack(self):
    self._setSettingsParams()
    self._hideSettingWidget()


  def _hideSettingWidget(self):
    self.settingFrame.hide()
    for widget in self.settingsWidgets:
      widget.hide()


  def _showSettingWidget(self):
    self.settingFrame.show()
    for widget in self.settingsWidgets:
      widget.show()


  def _displayStopButton(self):
    if self.autoCheckBox.isChecked():
      self.goButton.buttons[0].show()
      self.goButton.buttons[1].show()
      self.goButton.buttons[2].hide()
    else:
      self.goButton.buttons[0].hide()
      self.goButton.buttons[1].hide()
      self.goButton.buttons[2].show()


  def filterMethodPopup(self):
    FilterMethods(parent=self).exec()


  def _addWidgetsToLayout(self, widgets, layout):
    count = int(len(widgets) / 2)
    self.positions = [[i + 1, j] for i in range(count) for j in range(2)]
    for position, widget in zip(self.positions, widgets):
      i, j = position
      layout.addWidget(widget, i, j)



class FilterMethods(QtGui.QDialog):

  def __init__(self, parent=None,  **kw):
    super(FilterMethods, self).__init__(parent)
    self.pipelineModule = parent
    self._setMainLayout()
    self._setWidgets()
    self._addWidgetsToLayout()


  def _setMainLayout(self):
    self.mainLayout = QtGui.QGridLayout()
    self.setLayout(self.mainLayout)
    self.setWindowTitle("Filter Methods")
    self.resize(250, 300)


  def _setWidgets(self):
    self.selectLabel = Label(self, 'Select All')
    self.selectAllCheckBox = CheckBox(self, )
    self._setSelectionScrollArea()
    self._addMethodCheckBoxes()
    self.applyCancelButtons = ButtonList(self, texts=['Cancel', 'Ok'],
                                                callbacks=[self.reject, self._okButtonCallBack],
                                                direction='H')
    self.selectAllCheckBox.stateChanged.connect(self._checkAllMethods)


  def _addMethodCheckBoxes(self):
    self.allMethodCheckBoxes = []
    for i, method in enumerate(self.pipelineModule.methodPulldownData[1:]):
      self.spectrumCheckBox = CheckBox(self.scrollAreaWidgetContents, text=str(method), grid=(i + 1, 0))
      self.allMethodCheckBoxes.append(self.spectrumCheckBox)
    self.updateMethodCheckBoxes()
    self.updateSelectAllCheckBox()


  def updateMethodCheckBoxes(self):
    for method in self.pipelineModule.methodPulldown.texts:
      for cb in self.allMethodCheckBoxes:
        if cb.text() == method:
          cb.setChecked(True)


  def updateSelectAllCheckBox(self):
    for cb in self.allMethodCheckBoxes:
      if not cb.isChecked():
        return
      else:
        self.selectAllCheckBox.setChecked(True)


  def _checkAllMethods(self, state):
    if len(self.allMethodCheckBoxes)>0:
      for cb in self.allMethodCheckBoxes:
        if state == QtCore.Qt.Checked:
          cb.setChecked(True)
        else:
          cb.setChecked(False)


  def _getSelectedMethods(self):
    methods = [selectMethodLabel, ]
    for cb in self.allMethodCheckBoxes:
      if cb.isChecked():
        method = cb.text()
        methods.append(method)
    return sorted(methods)


  def _setSelectionScrollArea(self):
    self.scrollArea = ScrollArea(self)
    self.scrollArea.setWidgetResizable(True)
    self.scrollAreaWidgetContents = QtGui.QFrame()
    self.scrollArea.setWidget(self.scrollAreaWidgetContents)


  def _addWidgetsToLayout(self):
    self.mainLayout.addWidget(self.selectLabel, 0,0)
    self.mainLayout.addWidget(self.selectAllCheckBox, 0, 1)
    self.mainLayout.addWidget(self.scrollArea, 1, 0, 1, 2)
    self.mainLayout.addWidget(self.applyCancelButtons, 2, 1,)


  def _okButtonCallBack(self):
    self.pipelineModule.methodPulldown.setData(self._getSelectedMethods())
    self.accept()
