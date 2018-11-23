"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:24 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b4 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: rhfogh $"
__date__ = "$Date: 2017-04-07 10:28:45 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets

from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.ListWidget import ListWidget
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Widget import Widget
from ccpn.ui.gui.guiSettings import autoCorrectHexColour, getColours, CCPNGLWIDGET_HEXBACKGROUND
from collections import OrderedDict, namedtuple
from ccpn.ui.gui.widgets.SideBar import _openSpectrumDisplay
from ccpn.util.Colour import hexToRgb
from collections import OrderedDict
import os
import shutil
import numpy as np
import pandas as pd
from ccpn.AnalysisMetabolomics.lib import normalisation
from ccpn.AnalysisMetabolomics.lib import centering
from ccpn.AnalysisMetabolomics.lib import scaling
from ccpn.AnalysisMetabolomics.lib import decomposition
from ccpn.AnalysisMetabolomics.lib.persistence import spectraDicToBrukerExperiment
from ccpn.core.lib.Cache import cached
from ccpn.core.lib.SpectrumLib import get1DdataInRange

METABOLOMICS_SAVE_LOCATION = os.path.join('internal','metabolomics')

class Decomposition:
  """
  Base class for the Decomposition Module (the old "interactor"`!)
  Get the scores from console as dataframe: application.decomposition.model.scores_
  """

  def __init__(self, project):
    self.project = project
    self.__pcaModule = None #(the old "presenter"!)
    self.__sources = []
    self.__normalization = None
    self.__centering = None
    self.__scaling = None
    self.__decomp = None
    self.__data = None
    self.__sourcesChanged = True
    self.__normChanged = True
    self.__centChanged = True
    self.__scalingChanged = True
    self.__deScaleFunc = lambda x: x
    self.availablePlotData = OrderedDict()
    self.registerNotifiers()
    self.method = 'PCA'
    self.model = None
    self.auto = False


  def registerNotifiers(self):
    # TODO put inside the gui module
    self.project.registerNotifier('Spectrum', 'create', self.refreshSourceDataOptions)
    self.project.registerNotifier('Spectrum', 'change', self.refreshSourceDataOptions)
    self.project.registerNotifier('Spectrum', 'rename', self.refreshSourceDataOptions)
    self.project.registerNotifier('Spectrum', 'delete', self.refreshSourceDataOptions)
    self.project.registerNotifier('SpectrumGroup', 'create', self.refreshSpectrumGroupFilter)
    self.project.registerNotifier('SpectrumGroup', 'change', self.refreshSpectrumGroupFilter)
    self.project.registerNotifier('SpectrumGroup', 'rename', self.refreshSpectrumGroupFilter)
    self.project.registerNotifier('SpectrumGroup', 'delete', self.refreshSpectrumGroupFilter)


  def deRegisterNotifiers(self):
    # TODO put inside the gui module
    pass


  @property
  def pcaModule(self):
    return self.__pcaModule

  @pcaModule.setter
  def pcaModule(self, value):
    self.__pcaModule = value
    if value is not None:
      self.refreshSourceDataOptions()
      self.refreshSpectrumGroupFilter()

  @property
  def method(self):
    return self.__decomp

  @method.setter
  def method(self, value):
    if value.upper() == 'PCA':
      self.__decomp = value.upper()
    else:
      raise NotImplementedError('PCA is the only currently implemented decomposition method.')

  def refreshSourceDataOptions(self, *args):
    if self.pcaModule is not None:
      self.pcaModule.setSourceDataOptions(self.getSourceData())

  def refreshSpectrumGroupFilter(self, *args):
    if self.pcaModule is not None:
      self.pcaModule.setSpectrumGroups(self.getSpectrumGroups())

  def getSpectrumGroups(self):
    sg = [s for s in self.project.spectrumGroups]
    return sg

  def getSourceData(self):
    sd = []
    sd += [s for s in self.project.spectra if
              (len(s.axisCodes) == 1) and (s.axisCodes[0].startswith('H'))]
    # if self.project.spectra:
    #   raise Exception
    # print(self.project.spectra)
    # print(list([s.axisCodes for s in self.project.spectra]))
    # print(sd)

    return sd

  def _getData(self):
    return self.__data

  @property
  def normalization(self):
    return self.__normalization

  @normalization.setter
  def normalization(self, value):
    self.__normalization = value
    # self.__normChanged = True
    # self.__centChanged = True
    # self.__scalingChanged = True
    if self.auto:
      self.decompose()

  @property
  def centering(self):
    return self.__centering

  @centering.setter
  def centering(self, value):
    self.__centering = value
    # self.__centChanged = True
    # self.__scalingChanged = True
    if self.auto:
      self.decompose()

  @property
  def scaling(self):
    return self.__scaling

  @scaling.setter
  def scaling(self, value):
    self.__scaling = value
    # self.__scalingChanged = True
    if self.auto:
      self.decompose()

  @property
  def sources(self):
    return self.__sources

  @sources.setter
  def sources(self, value):
    self.__sources = value
    # self.__sourcesChanged = True
    # self.__normChanged = True
    # self.__centChanged = True
    # self.__scalingChanged = True
    if self.auto:
      self.decompose()

  @cached('_buildSourceData', maxItems=256, debug=False)
  def buildSourceData(self, sources, xRange=[-1,9]):
    self.__sourcesChanged = False
    sd = OrderedDict()

    for d in sources:
      spectrum = self.project.getByPid('SP:{}'.format(d))
      x,y = get1DdataInRange(spectrum.positions, spectrum.intensities, xRange)
      data = np.array([x,y])
      sd[d] = data
    l = [pd.Series(sd[name][1], name=name) for name in sorted(sd.keys())]
    data = pd.concat(l, axis=1).T
    data = data.replace(np.nan, 0)
    self.__data =  data
    return sources

  def normalize(self):
    if self.normalization.upper() == 'PQN':
      self.__data = normalisation.pqn(self.__data)
    elif self.normalization.upper() == 'TSA':
      self.__data = normalisation.tsa(self.__data)
    elif self.normalization.lower() == 'none':
      pass
    else:
      raise NotImplementedError("Only PQN, TSA and 'none' type normalizations currently supported.")
    # self.__normChanged = False


  def center(self):
    if self.centering.lower() == 'mean':
      self.__data = centering.meanCenter(self.__data)
    elif self.centering.lower() == 'median':
      self.__data = centering.medianCenter(self.__data)
    elif self.centering.lower() == 'none':
      pass
    else:
      raise NotImplementedError("Only mean, median and 'none' type centerings currently supported.")
    # self.__centChanged = False


  def scale(self):
    if self.scaling.lower() == 'pareto':
      self.__data, self.__deScaleFunc = scaling.paretoScale(self.__data)
    elif self.scaling.lower() == 'unit variance':
      self.__data, self.__deScaleFunc = scaling.unitVarianceScale(self.__data)
    elif self.scaling.lower() == 'none':
      pass
    else:
      raise NotImplementedError("Only pareto, unit variance and 'none' type scalings currently supported.")
    # self.__scalingChanged = False


  def decompose(self):
    if len(self.__sources) > 1:
      # if self.__sourcesChanged:
      #   self.buildSourceData()
      # if self.__normChanged:
      #   self.normalize()
      # if self.__centChanged:
      #   self.center()
      # if self.__scalingChanged:
      #   self.scale()
      self.buildSourceData(self.__sources)
      self.normalize()
      self.center()
      self.scale()
      # self.__decomp -->   PCA decomposition
      # decomposition -->  module 'ccpn.AnalysisMetabolomics.lib.decomposition
      # self.__data --> intensities as array

      data = self.__data.replace(np.nan, 0)

      self.model = getattr(decomposition, self.__decomp)(data)
      self.setAvailablePlotData()


  def setAvailablePlotData(self):
    defaults = OrderedDict()
    if self.method == 'PCA':
      self.availablePlotData = OrderedDict()
      self.availablePlotData['Component #'] = list(range(len(self.model.scores_)))
      self.availablePlotData['Explained Vairance'] = self.model.explainedVariance_
      for score in self.model.scores_:
        self.availablePlotData[score] = self.model.scores_[score].values


      defaults['xDefaultLeft'] = 'Component'
      defaults['yDefaultLeft'] = 'Explained Vairance'
      defaults['xDefaultRight'] = 'PC1'
      defaults['yDefaultRight'] = 'PC2'
    else:
      raise NotImplementedError('Only PCA output is currently supported.')
    self.pcaModule.setAvailablePlotData(list(self.availablePlotData.keys()),
                                        **defaults)


  def saveLoadingsToSpectra(self, prefix='test_pca', descale=True, components=None):
    saveLocation = os.path.join(self.project.path, METABOLOMICS_SAVE_LOCATION, 'pca', prefix)

    sgNames = [sg.name for sg in self.project.spectrumGroups]
    if prefix in sgNames:
      g = self.project.getByPid('SG:' + prefix)
    else:
      g = self.project.newSpectrumGroup(prefix)
      # TODO: Wayne: deleted spectra should be removed from spectrum groups!

    toDeleteSpectra = [s for s in self.project.spectra if s.name.endswith(prefix)]
    for s in toDeleteSpectra:
      s.delete()
    try:
      shutil.rmtree(saveLocation)
    except FileNotFoundError:
      pass

    if components is None:
      # TODO: Generalize beyond PCA
      components = self.model.loadings_

    if descale:
      components = components.apply(self.__deScaleFunc, axis=1)

    spectraDicToBrukerExperiment(components, saveLocation)

    loadingsSpectra = []
    for d in next(os.walk(saveLocation))[1]:
      loadedSpectrum = self.project.loadData(os.path.join(saveLocation, d))[0]
      loadingsSpectra.append(loadedSpectrum)
      newSpectrumName = loadedSpectrum.pid.split('-')[0][3:] + '-' + prefix
      loadedSpectrum.rename(newSpectrumName)
    g.spectra = loadingsSpectra


  @property
  def loadings(self):
    return None

  @property
  def scores(self):
    return None


class PcaModule(CcpnModule):
  includeSettingsWidget = True
  maxSettingsState = 2  # states are defined as: 0: invisible, 1: both visible, 2: only settings visible
  settingsPosition = 'left'
  className = 'DecompositionModule'

  def __init__(self, mainWindow, **kwargs):
    CcpnModule.__init__(self,mainWindow=mainWindow, name='PCA',)

    self.mainWindow = mainWindow
    self.current = self.mainWindow.current
    self.application = self.mainWindow.application
    self.project = self.mainWindow.project
    self.settings = PcaSettings(self)
    self.pcaPlotLeft = PcaPlot(self)
    self.pcaPlotRight = PcaPlot(self)
    self.pcaOutput = PcaOutput(self)
    self.decomposition = Decomposition(self.project)
    self.decomposition.pcaModule = self

    self.layout.addWidget(self.settings, 0, 0, 1, 2)
    self.layout.addWidget(self.pcaPlotLeft, 1, 0, 2, 1)
    self.layout.addWidget(self.pcaPlotRight, 1, 1, 2, 1)
    self.layout.addWidget(self.pcaOutput, 3, 0, 1, 2)
    self.__method = None
    self.__normalization = None
    self.__scaling = None
    self.__centering = None

    self.setupWidget()
    self.setMethod('PCA')
    self.setNormalization('PQN')
    self.setCentering('mean')
    self.setScaling('Pareto')
    self.decomposition.auto = True

  def setupWidget(self):
    self.settings.decompMethodPulldown.setData(['PCA', ])
    self.settings.normMethodPulldown.setData(['PQN', 'TSA', 'none'])
    self.settings.centMethodPulldown.setData(['Mean', 'Median', 'none'])
    self.settings.scalingMethodPulldown.setData(['Pareto', 'Unit Variance', 'none'])
    self.decomposition.refreshSourceDataOptions()
    self.decomposition.refreshSpectrumGroupFilter()

  def setSourceDataOptions(self, sourceData=None):
    self.settings.sourceList.clear()
    if sourceData is not None:
      sdo = [s.name for s in sourceData]
      self.settings.sourceList.addItems(sdo)

  def setSpectrumGroups(self, spectrumGroups=None):
    self.settings.spectrumGroupsList.clear()
    if spectrumGroups is not None:
      self.settings.spectrumGroupsList.setObjects(spectrumGroups)

  def setMethod(self, method):
    self.__method = method
    self.settings.decompMethodPulldown.select(method)
    self.decomposition.method = method

  def getMethod(self):
    return self.__method

  def getNormalization(self):
    return self.__normalization

  def setNormalization(self, normalization):
    self.__normalization = normalization
    self.settings.normMethodPulldown.select(normalization)
    self.decomposition.normalization = normalization

  def getCentering(self):
    return self.__centering

  def setCentering(self, centering):
    self.__centering = centering
    self.settings.centMethodPulldown.select(centering)
    self.decomposition.centering = centering

  def getScaling(self):
    return self.__scaling

  def setScaling(self, scaling):
    self.__scaling = scaling
    self.settings.scalingMethodPulldown.select(scaling)
    self.decomposition.scaling = scaling

  def setSourcesSelection(self, rowClicked):
    # should actually pass the selection to the interactor and have it bump back up...

    self.decomposition.sources = [s.text() for s in self.settings.sourceList.selectedItems()]

  def setAvailablePlotData(self, availablePlotData=None,
                           xDefaultLeft=None, yDefaultLeft=None,
                           xDefaultRight=None, yDefaultRight=None):
    if availablePlotData is None:
      availablePlotData = list(self.decomposition.availablePlotData.keys())

    self.pcaPlotLeft.xAxisSelector.setData(availablePlotData)
    self.pcaPlotLeft.yAxisSelector.setData(availablePlotData)
    self.pcaPlotRight.xAxisSelector.setData(availablePlotData)
    self.pcaPlotRight.yAxisSelector.setData(availablePlotData)

    self.pcaPlotLeft.xAxisSelector.select(xDefaultLeft)
    self.pcaPlotLeft.yAxisSelector.select(yDefaultLeft)
    self.pcaPlotRight.xAxisSelector.select(xDefaultRight)
    self.pcaPlotRight.yAxisSelector.select(yDefaultRight)

  def getSourceDataColors(self):
    """
    Should this move to the interactors???
    """
    return [self.project.getByPid('SP:{}'.format(source)).sliceColour
            for source in self.decomposition.sources]

  def getSpectra(self):
    """
    """
    return [self.project.getByPid('SP:{}'.format(source))
            for source in self.decomposition.sources]

  def plot(self, target, xAxisLabel, yAxisLabel):
    target.plotItem.clear()
    xs = self.decomposition.availablePlotData[xAxisLabel]
    ys = self.decomposition.availablePlotData[yAxisLabel]
    if (xAxisLabel.upper().startswith('PC') or
        yAxisLabel.upper().startswith('PC')):
      colourBrushes = [pg.functions.mkBrush(hexToRgb(hexColour))
                       for hexColour in self.getSourceDataColors()]
      for x, y, spectrum, brush in zip(xs, ys, self.getSpectra(), colourBrushes):
        plot = target.plotItem.plot([x], [y], pen=None, symbol='o',
                                    symbolBrush=brush, )
        plot.curve.setClickable(True)
        plot.spectrum = spectrum
        plot.sigClicked.connect(self._mouseClickEvent)
    else:
      target.plotItem.plot(xs, ys, symbol='o', clear=True)

    if xAxisLabel.upper().startswith('PC'):
      target.addYOriginLine()
    if yAxisLabel.upper().startswith('PC'):
      target.addXOriginLine()

    target.plotItem.setLabel('bottom', xAxisLabel)
    target.plotItem.setLabel('left', yAxisLabel)

  def _mouseClickEvent(self, i):
    " Open a spectrum for the pca point"

    spectrum = i.spectrum
    spectrumDisplay = _openSpectrumDisplay(self.mainWindow, spectrum)

  def saveOutput(self):
    saveName = self.pcaOutput.sgNameEntryBox.text()
    descale = self.pcaOutput.descaleCheck.isChecked()
    self.decomposition.saveLoadingsToSpectra(prefix=saveName, descale=descale)


class PcaSettings(Widget):
  def __init__(self, parent=None, **kwds):
    super().__init__(parent, **kwds)
    self.parent = parent

    self.setLayout(QtWidgets.QHBoxLayout())
    column1Layout = QtWidgets.QVBoxLayout()
    self.layout().addLayout(column1Layout)

    column1Layout.addWidget(Label(self, 'Method:'))
    self.decompMethodPulldown = PulldownList(self, callback=parent.setMethod)
    column1Layout.addWidget(self.decompMethodPulldown)
    # self.goButton = Button(self, 'GO!', hPolicy='fixed', callback=parent.go)
    # column1Layout.addWidget(self.goButton)
    column1Layout.addStretch()

    column2Layout = QtWidgets.QGridLayout()
    self.layout().addLayout(column2Layout)
    column2Layout.addWidget(Label(self, '1. Normalization:'), 0, 0, 1, 1)
    self.normMethodPulldown = PulldownList(self, callback=parent.setNormalization)
    column2Layout.addWidget(self.normMethodPulldown, 0, 1, 1, 1)

    column2Layout.addWidget(Label(self, '2. Centering:'), 1, 0, 1, 1)
    self.centMethodPulldown = PulldownList(self, callback=parent.setCentering)
    column2Layout.addWidget(self.centMethodPulldown, 1, 1, 1, 1)

    column2Layout.addWidget(Label(self, '3. Scaling:'), 2, 0, 1, 1)
    self.scalingMethodPulldown = PulldownList(self, callback=parent.setScaling)
    column2Layout.addWidget(self.scalingMethodPulldown, 2, 1, 1, 1)

    spectrumGroupsLabel = Label(self, 'SpectrumGroups:')
    self.layout().addWidget(spectrumGroupsLabel)

    self.spectrumGroupsList = ListWidget(self, callback=self._filterBySpectrumGroups)
    self.spectrumGroupsList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    self.spectrumGroupsList.clearSelection = self._clearSpectrumGroupSelection
    self.spectrumGroupsList.setSelectContextMenu()
    self.layout().addWidget(self.spectrumGroupsList)

    spectraLabel = Label(self, 'Spectra Source:')
    self.layout().addWidget(spectraLabel)
    self.sourceList = ListWidget(self, callback=parent.setSourcesSelection)
    self.sourceList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    self.sourceList.setSelectContextMenu()

    self.layout().addWidget(self.sourceList)

    self.setMaximumHeight(100)

  def _clearSelection(self, listWidget):
    for i in range(listWidget.count()):
      item = listWidget.item(i)
      item.setSelected(False)

  def _clearSpectrumGroupSelection(self):
    print('This function has not been implemented yet.')
    # self._clearSelection(self.spectrumGroupsList)
    # self.sourceList.clear()
    # self.parent.setSourcesSelection(None)


  def _filterBySpectrumGroups(self, rowClicked):
    sGroups = self.spectrumGroupsList.getSelectedObjects()

    # self.sourceList.hideAllItems()
    self.sourceList.clearSelection()
    self.parent.setSourcesSelection(None)
    spectra = [sp for sg in sGroups for sp in sg.spectra]
    self.sourceList.showItems([spectrum.name for spectrum in spectra], select=True)

    self.parent.setSourcesSelection(None)



class PcaPlot(QtWidgets.QWidget):
  def __init__(self, parent=None, **kwargs):
    QtWidgets.QWidget.__init__(self, parent)
    self.setLayout(QtWidgets.QVBoxLayout())
    self.parent = parent
    bc = getColours()[CCPNGLWIDGET_HEXBACKGROUND]
    self.plottingWidget = pg.PlotWidget(self, background=bc)
    self.plotItem = self.plottingWidget.getPlotItem()
    self.plotItem.getAxis('left').setWidth(36)
    self.plotItem.getAxis('bottom').setHeight(24)

    self.layout().addWidget(self.plottingWidget)
    selectorLayout = QtWidgets.QHBoxLayout()

    selectorLayout.addWidget(Label(self, 'x:'))
    self.xAxisSelector = PulldownList(self, callback=self.plot)
    selectorLayout.addWidget(self.xAxisSelector)
    selectorLayout.addWidget(Label(self, 'y:'))
    self.yAxisSelector = PulldownList(self, callback=self.plot)
    selectorLayout.addWidget(self.yAxisSelector)
    selectorLayout.addStretch()

    self.layout().addLayout(selectorLayout)


  def plot(self, *args):
    # goes to /ui/gui/modules/DecompositionModule.py
    self.parent.plot(self, self.xAxisSelector.currentData()[0],
                        self.yAxisSelector.currentData()[0])

  def addXOriginLine(self):
    self.plotItem.addItem(pg.InfiniteLine(angle=0, pos=0,
                          pen=pg.functions.mkPen('w', width=1, style=QtCore.Qt.DashLine)))

  def addYOriginLine(self):
    self.plotItem.addItem(pg.InfiniteLine(angle=90, pos=0,
                          pen=pg.functions.mkPen('w', width=1, style=QtCore.Qt.DashLine)))


class PcaOutput(Widget):
  def __init__(self, parent=None, **kwds):
    super().__init__(parent, **kwds)
    self.parent = parent

    self.setLayout(QtWidgets.QHBoxLayout())

    self.sgNameEntryBox = LineEdit(self, text='pca_001')
    self.descaleCheck = CheckBox(self, checked=True, text='Descale Components')
    self.saveButton = Button(self, 'save', callback=self.parent.saveOutput)

    self.getLayout().addWidget(Label(self, 'Output spectrum group:'))
    self.getLayout().addWidget(self.sgNameEntryBox)
    self.getLayout().addWidget(self.descaleCheck)
    self.getLayout().addStretch()
    self.getLayout().addWidget(self.saveButton)
    self.setMaximumHeight(45)

