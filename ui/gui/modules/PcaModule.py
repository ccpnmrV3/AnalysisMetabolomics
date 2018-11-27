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
from ccpn.util.Logging import getLogger
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
from ccpn.core.Spectrum import Spectrum
from ccpn.core.SpectrumGroup import SpectrumGroup
from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.ListWidget import ListWidget
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Widget import Widget
from ccpn.ui.gui.guiSettings import autoCorrectHexColour, getColours, CCPNGLWIDGET_HEXBACKGROUND, GUISTRIP_PIVOT
from ccpn.ui.gui.widgets.SideBar import _openItemObject
from ccpn.util.Colour import hexToRgb
from collections import OrderedDict
import os
import shutil
import numpy as np
import pandas as pd
from ccpn.AnalysisMetabolomics.lib import normalisation
from ccpn.AnalysisMetabolomics.lib import centering
from ccpn.AnalysisMetabolomics.lib import scaling
from ccpn.AnalysisMetabolomics.lib.decomposition import PCA
from ccpn.AnalysisMetabolomics.lib.persistence import spectraDicToBrukerExperiment
from ccpn.core.lib.Cache import cached
from ccpn.core.lib.SpectrumLib import get1DdataInRange

METABOLOMICS_SAVE_LOCATION = os.path.join('internal','metabolomics')

class Decomposition:
  """
  Base class for the Decomposition Module (the old "interactor"`!)
  """

  def __init__(self, project):
    self.project = project
    self.__pcaModule = None #(the old "presenter"!)
    self.__sources = [] # list of pids
    self.__normalization = None
    self.__centering = None
    self.__scaling = None
    self.__decomp = None # 'Only PCA at the moment'
    self.__data = None
    self.__sourcesChanged = True
    self.__normChanged = True
    self.__centChanged = True
    self.__scalingChanged = True
    self.__deScaleFunc = lambda x: x
    self.availablePlotData = OrderedDict()
    self.model = None # PCA base class
    self.auto = False


  @property
  def pcaModule(self):
    return self.__pcaModule

  @pcaModule.setter
  def pcaModule(self, value):
    self.__pcaModule = value


  def getSpectra(self):
    # Modify to have spectra by drag and drop and not all from project
    sd = []
    sd += [s for s in self.project.spectra if
              (len(s.axisCodes) == 1) and (s.axisCodes[0].startswith('H'))]
    return sd

  def _getRawData(self):
    """ Returns a dataframe containg the 1D array of spectral intensities and the relative pid """
    return self.__data

  @property
  def normalization(self):
    return self.__normalization

  @normalization.setter
  def normalization(self, value):
    self.__normalization = value
    if self.auto:
      self.decompose()

  @property
  def centering(self):
    return self.__centering

  @centering.setter
  def centering(self, value):
    self.__centering = value
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
    """ list of pids"""
    return self.__sources

  @sources.setter
  def sources(self, value):
    self.__sources = value
    if self.auto:
      self.decompose()

  @property
  def scores(self):
    if self.model is not None:
      scores = self.model.scores_
      return scores



  def decompose(self):
    """
    get the data, init the pca model and then plot the results
    """

    data = self.buildSourceData(self.__sources)
    if data is not None:
      if data.shape[0] > 1: # we have enough entries
        data = data.replace(np.nan, 0)
        self.normalize()
        self.center()
        self.scale()
        self.model = PCA(data)
        self._setAvailablePlotData()
      else:
        self.pcaModule.clearPlots()

  def _setAvailablePlotData(self):
    defaults = OrderedDict()
    self.availablePlotData = OrderedDict()
    self.availablePlotData['Component #'] = list(range(len(self.model.scores_)))
    self.availablePlotData['Explained Vairance'] = self.model.explainedVariance_
    for score in self.model.scores_:
      self.availablePlotData[score] = self.model.scores_[score].values
    defaults['xDefaultLeft'] = 'Component'
    defaults['yDefaultLeft'] = 'Explained Vairance'
    defaults['xDefaultRight'] = 'PC1'
    defaults['yDefaultRight'] = 'PC2'

    self.pcaModule.setAvailablePlotData(list(self.availablePlotData.keys()),
                                        **defaults)

  def buildSourceFromSpectra(self, spectra, xRange=[-1,9]):
    """

    :param spectra: list of spectra
    :param xRange: the region of interest in the spectrum
    :return: the sources back
    Sets the __data with a dataframe: each row is a spectrum. Coloumn 1 is the pid, all other columns are spectrum intesities
    """
    spectraDict = OrderedDict()
    for spectrum in list(set(spectra)):
      if spectrum.dimensionCount == 1:
        x,y = get1DdataInRange(spectrum.positions, spectrum.intensities, xRange)
        data = np.array([x,y])
        spectraDict[spectrum] = data
      else:
        getLogger().warning('Not implemented yet. PCA works only with 1D spectra' )
    l = [pd.Series(spectraDict[name][1], name=name) for name in sorted(spectraDict.keys())]
    data = pd.concat(l, axis=1).T
    return data




  # @cached('_buildSourceData', maxItems=256, debug=False)
  def buildSourceData(self, sources, xRange=[-1,9]):
    """

    :param sources: list of pids
    :param xRange: the region of interest in the spectrum
    :return: the sources back
    Sets the __data with a dataframe: each row is a spectrum. Coloumn 1 is the pid, all other columns are spectrum intesities
    """
    self.__sourcesChanged = False

    frames = []
    for pid in sources:
      obj = self.project.getByPid(pid)
      if isinstance(obj, Spectrum):
        frames.append(self.buildSourceFromSpectra([obj], xRange))
      elif isinstance(obj, SpectrumGroup):
        for sp in obj.spectra:
          frames.append(self.buildSourceFromSpectra([sp], xRange))
      else:
        getLogger().warning('PCA not implemented for %s' % obj)
    if len(frames)>0:
      data = pd.concat(frames)
      data = data.replace(np.nan, 0)
      self.__data =  data
    return self.__data

  def normalize(self):
    if self.normalization.upper() == 'PQN':
      self.__data = normalisation.pqn(self.__data)
    elif self.normalization.upper() == 'TSA':
      self.__data = normalisation.tsa(self.__data)
    elif self.normalization.lower() == 'none':
      pass
    else:
      raise NotImplementedError("Only PQN, TSA and 'none' type normalizations currently supported.")


  def center(self):
    if self.centering.lower() == 'mean':
      self.__data = centering.meanCenter(self.__data)
    elif self.centering.lower() == 'median':
      self.__data = centering.medianCenter(self.__data)
    elif self.centering.lower() == 'none':
      pass
    else:
      raise NotImplementedError("Only mean, median and 'none' type centerings currently supported.")

  def scale(self):
    if self.scaling.lower() == 'pareto':
      self.__data, self.__deScaleFunc = scaling.paretoScale(self.__data)
    elif self.scaling.lower() == 'unit variance':
      self.__data, self.__deScaleFunc = scaling.unitVarianceScale(self.__data)
    elif self.scaling.lower() == 'none':
      pass
    else:
      raise NotImplementedError("Only pareto, unit variance and 'none' type scalings currently supported.")




  def saveLoadingsToSpectra(self, prefix='test_pca', descale=True, components=None):
    saveLocation = os.path.join(self.project.path, METABOLOMICS_SAVE_LOCATION, 'pca', prefix)

    sgNames = [sg.name for sg in self.project.spectrumGroups]
    if prefix in sgNames:
      g = self.project.getByPid('SG:' + prefix)
    else:
      g = self.project.newSpectrumGroup(prefix)

    toDeleteSpectra = [s for s in self.project.spectra if s.name.endswith(prefix)]
    for s in toDeleteSpectra:
      s.delete()
    try:
      shutil.rmtree(saveLocation)
    except FileNotFoundError:
      pass

    if components is None:
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





class PcaModule(CcpnModule):
  includeSettingsWidget = True
  maxSettingsState = 2  # states are defined as: 0: invisible, 1: both visible, 2: only settings visible
  settingsPosition = 'left'
  className = 'DecompositionModule'

  def __init__(self, mainWindow, **kwargs):
    CcpnModule.__init__(self,mainWindow=mainWindow, name='PCA',)

    self.mainWindow = mainWindow

    if self.mainWindow: # without mainWindow will open only the Gui
      self.current = self.mainWindow.current
      self.application = self.mainWindow.application
      self.project = self.mainWindow.project
      self.decomposition = Decomposition(self.project)
      self.decomposition.pcaModule = self
      self.decomposition.auto = True

    ####  Main Widgets
    mi = 0 # main (row) index
    labelSource =  Label(self.mainWidget, 'Sources:', grid=(mi,0), gridSpan=(mi+1,0))
    mi += 1
    self.sourceList = ListWidget(self.mainWidget, acceptDrops=True, grid=(mi,0), gridSpan=(mi,0))
    mi += 1
    self.sourceList.setSelectDeleteContextMenu()
    self.sourceList.dropped.connect(self._sourceListDroppedCallback)
    self.sourceList.setMaximumHeight(100)
    self.sourceList.itemSelectionChanged.connect(self._setSourcesSelection)
    self.pcaPlotLeft = PcaPlot(self.mainWidget, pcaModule=self, grid=(mi,0))
    self.pcaPlotRight = PcaPlot(self.mainWidget, pcaModule=self, grid=(mi,1))
    mi += 1
    self.saveButton = Button(self.mainWidget, 'Create PCA SpectrumGroup ', callback=self.saveOutput, grid=(mi, 0),gridSpan=(mi,0))

    #### Settings widgets
    si = 0 # Settings (row) index
    l = Label(self.settingsWidget, 'Output name:', grid=(si, 0))
    self.sgNameEntryBox = LineEdit(self.settingsWidget, text='pca_001', grid=(si, 1))
    si += 1
    ll = Label(self.settingsWidget, 'Descale Components:', grid=(si, 0))
    self.descaleCheck = CheckBox(self.settingsWidget, checked=True, grid=(si, 1))
    si +=1
    l2 = Label(self.settingsWidget, '1. Normalization:', grid=(si,0))
    self.normMethodPulldown = PulldownList(self.settingsWidget, callback=self.setNormalization, grid=(si,1))
    self.normMethodPulldown.setData(['PQN', 'TSA', 'none'])
    self.setNormalization('PQN')
    si += 1
    l3 = Label(self.settingsWidget, '2. Centering:', grid=(si,0))
    self.centMethodPulldown = PulldownList(self.settingsWidget, callback=self.setCentering, grid=(si,1))
    self.centMethodPulldown.setData(['Mean', 'Median', 'none'])
    self.setCentering('mean')
    si += 1
    l4 = Label(self.settingsWidget, '3. Scaling:', grid=(si,0))
    self.scalingMethodPulldown = PulldownList(self.settingsWidget, callback=self.setScaling,  grid=(si,1))
    self.scalingMethodPulldown.setData(['Pareto', 'Unit Variance', 'none'])
    self.setScaling('Pareto')
    si += 1
    l5 = Label(self.settingsWidget, 'Show Exp Graph:', grid=(si, 0))
    self.toggleLeftGraph = CheckBox(self.settingsWidget, checked=True, callback=self._toggleGraph, grid=(si, 1))
    self._toggleGraph()

  def clearPlots(self):
    self.pcaPlotRight.clearPlot()
    self.pcaPlotLeft.clearPlot()

  def _sourceListDroppedCallback(self, *args):
    pass
    #Do that when you drop an item it is also selected

  def _clearSelection(self, listWidget):
    for i in range(listWidget.count()):
      item = listWidget.item(i)
      item.setSelected(False)

  def _toggleGraph(self):
    if self.toggleLeftGraph.isChecked():
      self.pcaPlotLeft.show()
    else:
      self.pcaPlotLeft.hide()

  def setSourceDataOptions(self, sourceData=None):
    self.settings.sourceList.clear()
    if sourceData is not None:
      sdo = [s.name for s in sourceData]
      self.sourceList.addItems(sdo)

  def setNormalization(self, normalization):
    self.normMethodPulldown.select(normalization)
    self.decomposition.normalization = normalization

  def setCentering(self, centering):
    self.centMethodPulldown.select(centering)
    self.decomposition.centering = centering

  def setScaling(self, scaling):
    self.scalingMethodPulldown.select(scaling)
    self.decomposition.scaling = scaling

  def _setSourcesSelection(self):
    """ this starts the pca machinery"""
    if len( self.sourceList.getSelectedTexts()) == 0: # if nothing selected, then do nothing
      self.clearPlots()
      return
    self.decomposition.sources = self.sourceList.getSelectedTexts()

  def refreshPlots(self):
    self._setSourcesSelection()

  def setAvailablePlotData(self, availablePlotData=None,
                           xDefaultLeft=None, yDefaultLeft=None,
                           xDefaultRight=None, yDefaultRight=None):
    # called from decomposition when all data are ready

    if availablePlotData is None:
      availablePlotData = list(self.decomposition.availablePlotData.keys())
      print('availablePlotData',availablePlotData)

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
    """
    return [self.project.getByPid(source).sliceColour
            for source in self.decomposition.sources]

  def getSpectra(self):
    """
    """
    return [self.project.getByPid(sp) for sp in self.decomposition.sources]


  def _mouseClickEvent(self, i):
    " Open the object for the pca point"

    obj = i.object
    if obj is not None:
      _openItemObject(self.mainWindow, [obj])

  def saveOutput(self):
    saveName = self.pcaOutput.sgNameEntryBox.text()
    descale = self.pcaOutput.descaleCheck.isChecked()
    self.decomposition.saveLoadingsToSpectra(prefix=saveName, descale=descale)





class PcaPlot(Widget):
  def __init__(self, parent, pcaModule, **kwargs):
    super().__init__(parent, setLayout=True, **kwargs)
    self.parent = parent
    self.pcaModule = pcaModule
    bc = getColours()[CCPNGLWIDGET_HEXBACKGROUND]
    self.plottingWidget = pg.PlotWidget(self, background=bc)
    self.plotItem = self.plottingWidget.getPlotItem()
    self.plotItem.getAxis('left').setWidth(36)
    self.plotItem.getAxis('bottom').setHeight(24)

    self.getLayout().addWidget(self.plottingWidget, 0,0,1,0)

    label1 = Label(self, 'x:', grid=(1,0))
    self.xAxisSelector = PulldownList(self, callback=self.plotPCA,grid=(1,1))
    label2 = Label(self, 'y:',grid=(2,0))
    self.yAxisSelector = PulldownList(self, callback=self.plotPCA,grid=(2,1))


  def clearPlot(self):
    self.plotItem.clearPlots()

  def plotPCA(self, *args):
    gridColour = getColours()[GUISTRIP_PIVOT]
    xAxisLabel = self.xAxisSelector.currentData()[0]
    yAxisLabel = self.yAxisSelector.currentData()[0]
    self.plotItem.clear()
    xs = self.pcaModule.decomposition.availablePlotData[xAxisLabel]
    ys = self.pcaModule.decomposition.availablePlotData[yAxisLabel]
    if (xAxisLabel.upper().startswith('PC') or yAxisLabel.upper().startswith('PC')): #Remove this
      # colourBrushes = [pg.functions.mkBrush(hexToRgb(hexColour))
      #                  for hexColour in self.getSourceDataColors()]
      for x, y, in zip(xs, ys,):
        plot = self.plotItem.plot([x], [y], pen=None, symbol='o',
                                        )
        plot.curve.setClickable(True)
        # plot.object = object
        # plot.sigClicked.connect(self._mouseClickEvent)
    else:
      self.plotItem.plot(xs, ys, symbol='o', clear=True)

    if xAxisLabel.upper().startswith('PC'):
      self.plotItem.addItem(pg.InfiniteLine(angle=90, pos=0, pen=pg.functions.mkPen(hexToRgb(gridColour), width=1, style=QtCore.Qt.DashLine)))
    if yAxisLabel.upper().startswith('PC'):
      self.plotItem.addItem(pg.InfiniteLine(angle=0, pos=0,  pen=pg.functions.mkPen(hexToRgb(gridColour), width=1, style=QtCore.Qt.DashLine)))

    self.plotItem.setLabel('bottom', xAxisLabel)
    self.plotItem.setLabel('left', yAxisLabel)





if __name__ == '__main__':
  from PyQt5 import QtGui, QtWidgets
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.widgets.CcpnModuleArea import CcpnModuleArea


  app = TestApplication()
  win = QtWidgets.QMainWindow()

  moduleArea = CcpnModuleArea(mainWindow=None)
  #
  module = PcaModule(mainWindow=None, name='My Module')
  moduleArea.addModule(module)

  win.setCentralWidget(moduleArea)
  win.resize(1000, 500)
  win.setWindowTitle('Testing %s' % module.moduleName)
  win.show()


  app.start()
  win.close()
