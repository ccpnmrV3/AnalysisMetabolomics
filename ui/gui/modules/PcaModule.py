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
DefaultPC1 = 'PC1'
DefaultPC2 = 'PC2'
PC = 'PC'
none = 'none'
# Normalisation types
PQN = 'PQN'
TSA = 'TSA'
#  Centering
mean = 'mean'
median = 'median'
#
pareto = 'pareto'
variance = 'unit variance'


class Decomposition:
  """
  Base class for the Decomposition Module (the old "interactor"`!)
  """

  def __init__(self, project):
    self.project = project
    self.__pcaModule = None #(the old "presenter"!)
    self.__sources = [] # list of pids
    self.__normalization = PQN
    self.__centering = mean
    self.__scaling = pareto
    self.__decomp = None # 'Only PCA at the moment'
    self.__data = None
    self.__sourcesChanged = True
    self.__normChanged = True
    self.__centChanged = True
    self.__scalingChanged = True
    self.__deScaleFunc = lambda x: x
    self.availablePlotData = OrderedDict()
    self.model = None # PCA base class
    self.auto = True


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
    success = False
    data = self.buildSourceData(self.__sources)
    if data is not None:
      if data.shape[0] > 1: # we have enough entries
        data_ = data.replace(np.nan, 0)
        normalisedData = self.normalize(data_)
        centeredData = self.center(normalisedData)
        scaledData = self.scale(centeredData)
        data = scaledData.replace(np.nan, 0)
        self.model = PCA(data)
        success = True
    return success


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

  def normalize(self, data):
    if self.normalization.upper() == PQN:
      data = normalisation.pqn(data)
    elif self.normalization.upper() == TSA:
      data = normalisation.tsa(data)
    elif self.normalization.lower() == none:
      pass
    else:
      raise NotImplementedError("Only PQN, TSA and 'none' type normalizations currently supported.")
    return data

  def center(self, data):
    if self.centering.lower() == mean:
      data = centering.meanCenter(data)
    elif self.centering.lower() == median:
      data = centering.medianCenter(data)
    elif self.centering.lower() == none:
      pass
    else:
      raise NotImplementedError("Only mean, median and 'none' type centerings currently supported.")
    return data

  def scale(self, data):
    if self.scaling.lower() == pareto:
      data, self.__deScaleFunc = scaling.paretoScale(data)
    elif self.scaling.lower() == variance:
      data, self.__deScaleFunc = scaling.unitVarianceScale(data)
    elif self.scaling.lower() == none:
      pass
    else:
      raise NotImplementedError("Only pareto, unit variance and 'none' type scalings currently supported.")
    return data

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
    self.decomposition = None

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


    # self.pcaPlotRight = PcaScatterWidget(self.mainWidget, pcaModule=self, grid=(mi,1), gridSpan=(mi,0))

    bc = getColours()[CCPNGLWIDGET_HEXBACKGROUND]
    gridColour = getColours()[GUISTRIP_PIVOT]

    self._view = pg.GraphicsLayoutWidget()
    self._plotItem = self._view.addPlot()
    self.scatterPlot = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120), bc =bc)
    self.scatterPlot.sigClicked.connect(self._plotClicked)

    self._plotItem.addItem(self.scatterPlot)

    self.xLine = pg.InfiniteLine(angle=90, pos=0, pen=pg.functions.mkPen(hexToRgb(gridColour), width=1, style=QtCore.Qt.DashLine))
    self._plotItem.addItem(self.xLine)
    self.yLine = pg.InfiniteLine(angle=0, pos=0,pen=pg.functions.mkPen(hexToRgb(gridColour), width=1, style=QtCore.Qt.DashLine))
    self._plotItem.addItem(self.yLine)
    self.mainWidget.getLayout().addWidget(self._view, mi,0)

    mi += 1
    self.saveButton = Button(self.mainWidget, 'Create PCA SpectrumGroup ', callback=self.saveOutput, grid=(mi, 0),gridSpan=(mi,0))

    #### Settings widgets
    si = 0 # Settings (row) index
    l = Label(self.settingsWidget, 'Output name:', grid=(si, 0))
    self.sgNameEntryBox = LineEdit(self.settingsWidget, text='pca', grid=(si, 1))
    si += 1
    l = Label(self.settingsWidget, 'x:', grid=(si, 0))
    self.xAxisSelector = PulldownList(self.settingsWidget, callback=self._axisChanged, grid=(si, 1))
    si += 1
    l = Label(self.settingsWidget, 'y:', grid=(si, 0))
    self.yAxisSelector = PulldownList(self.settingsWidget, callback=self._axisChanged, grid=(si, 1))
    si += 1
    l = Label(self.settingsWidget, 'Descale Components:', grid=(si, 0))
    self.descaleCheck = CheckBox(self.settingsWidget, checked=True, grid=(si, 1))
    si +=1
    l = Label(self.settingsWidget, 'Normalization:', grid=(si,0))
    self.normMethodPulldown = PulldownList(self.settingsWidget, callback=self._setNormalization, grid=(si,1))
    self.normMethodPulldown.setData([PQN, TSA, none])
    si += 1
    l = Label(self.settingsWidget, 'Centering:', grid=(si,0))
    self.centMethodPulldown = PulldownList(self.settingsWidget, callback=self._setCentering, grid=(si,1))
    self.centMethodPulldown.setData([mean, median, none])
    si += 1
    l = Label(self.settingsWidget, 'Scaling:', grid=(si,0))
    self.scalingMethodPulldown = PulldownList(self.settingsWidget, callback=self.setScaling,  grid=(si,1))
    self.scalingMethodPulldown.setData([pareto, variance, none])
    si += 1


  def getPcaResults(self):
    """ gets the results from the base class decomposition """

    if self.decomposition is not None:
      scoresDF = self.decomposition.scores
      if scoresDF is not None:
        if scoresDF.shape[0] > 1: #No point in plotting
          return scoresDF


  def plotPCAresults(self, dataFrame, xAxisLabel='PC1', yAxisLabel='PC2'):
    """

    :param dataFrame: in the format from the PCA Class
          index: Pid --> obj or str of pid
          Column: #  --> serial
          Column: variance --> explained variance
          Columns: PCx  x= 1 to the end. Eg. PC1, PC2, etc
    :return:  transform the dataFrame in the plottable data format and plot it on the scatterPlot

    """
    if dataFrame is None:
      self.scatterPlot.clear()
      return
    spots = []
    for obj, row in dataFrame.iterrows():
      dd = {'pos': [0, 0], 'data': 'pid', 'brush': pg.mkBrush(255, 255, 255, 120), 'symbol': 'o', 'size': 10, }

      dd['pos'] = [row[xAxisLabel], row[yAxisLabel]]
      dd['data'] = obj
      if hasattr(obj, 'sliceColour'):
        dd['brush'] = pg.functions.mkBrush(hexToRgb(obj.sliceColour))
      spots.append(dd)
    self._plotSpots(spots)
    self._plotItem.setLabel('bottom', xAxisLabel)
    self._plotItem.setLabel('left', yAxisLabel)




  def _plotSpots(self, spots):
    """
    plots the data in the format requested by the ScatterPlot widget
    :param spots: a list of dict with these Key:value
                [{
                'pos': [0, 0], # [x,y] which will be the single spot position
                'data': 'pid', any python object. pid for PCA
                'brush': pg.mkBrush(255, 255, 255, 120), the colour of the spot
                'symbol': 'o', will give the shape of the spot
                'size': 10,
                'pen' = pg.mkPen(None)
                 }, ...]
    :return:
    """
    self.scatterPlot.clear()
    self.scatterPlot.addPoints(spots)

  def _plotClicked(self, plot, points):
    """
    :param plot:
    :param points: all points under the mouse click.
    :return:
    """
    if len(points)>1:
      return
    for point in points: # not sure if we want open the same. Maybe up to a limit of n?
      # point.setPen('b', width=1)
      obj = point.data()
      if obj is not None:
        _openItemObject(self.mainWindow, [obj])


  def _sourceListDroppedCallback(self, ll):
    if len(ll)>0:
      data = ll[0]
      pids = data.get('pids')
      self.sourceList.selectItems(pids)

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

  def _setNormalization(self, normalization):
    if self.decomposition:
      self.normMethodPulldown.select(normalization)
      self.decomposition.normalization = normalization
      if self.getPcaResults() is not None:
        self.refreshPlot()

  def _setCentering(self, centering):
    if self.decomposition:
      self.centMethodPulldown.select(centering)
      self.decomposition.centering = centering
      if self.getPcaResults() is not None:
        self.refreshPlot()

  def setScaling(self, scaling):
    if self.decomposition:

      self.scalingMethodPulldown.select(scaling)
      self.decomposition.scaling = scaling
      if self.getPcaResults() is not None:
        self.refreshPlot()

  def _setAxes(self, scores):
    """ Set X and Y axes from the PCA scores dataFrame.
     This because we don't know at priory how many PC we will have. Defaults PC1 and PC2"""
    if scores is not None:
      labels = scores.keys()
      self.xAxisSelector.setData(list(labels))
      self.yAxisSelector.setData(list(labels))
      self.xAxisSelector.select(DefaultPC1)
      self.yAxisSelector.select(DefaultPC2)
    else:
      self.scatterPlot.clear()

  def _clearPlot(self):

    self.scatterPlot.clear()
    self.scatterPlot.viewTransformChanged()
    self.decomposition.sources = []
    self.xAxisSelector.setData([])
    self.yAxisSelector.setData([])


  def _setSourcesSelection(self):
    """ this starts the pca machinery"""
    if len( self.sourceList.getSelectedTexts()) == 0: # if nothing selected, then do nothing
      self._clearPlot()
      return

    elif len(self.sourceList.getSelectedTexts()) == 1: # only SG is allowed a single selection
      obj = self.project.getByPid(self.sourceList.getSelectedTexts()[0])
      if not isinstance(obj, SpectrumGroup):
        self._clearPlot()
        return

    self.decomposition.sources = self.sourceList.getSelectedTexts()
    self._setAxes(scores = self.getPcaResults())
    self._axisChanged()

  def _axisChanged(self, *args):
    """callback from axis pulldowns """
    x = self.xAxisSelector.getText()
    y = self.yAxisSelector.getText()
    self.plotPCAresults(self.decomposition.scores, xAxisLabel=x, yAxisLabel=y)

  def refreshPlot(self, ):
    self._setSourcesSelection()


  def saveOutput(self):
    saveName = self.pcaOutput.sgNameEntryBox.text()
    descale = self.pcaOutput.descaleCheck.isChecked()
    self.decomposition.saveLoadingsToSpectra(prefix=saveName, descale=descale)






if __name__ == '__main__':
  from PyQt5 import QtGui, QtWidgets
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.widgets.CcpnModuleArea import CcpnModuleArea




  data = np.empty(5, dtype=[('x_pos', float), ('y_pos', float)])
  x = data['x_pos'] = np.random.normal(size=5)
  y = data['y_pos'] = np.random.normal(size=5) + data['x_pos'] * 0.1
  objs = ['A','B','C','D','E']

  app = TestApplication()
  win = QtWidgets.QMainWindow()

  moduleArea = CcpnModuleArea(mainWindow=None)
  module = PcaModule(mainWindow=None, name='My Module')
  moduleArea.addModule(module)


  n = 5
  pos = np.random.normal(size=(2, n), scale=1e-5)
  spots = [{'pos': pos[:, i], 'data': 1} for i in range(n)] + [{'pos': [0, 0], 'data': 1}]
  module._plotSpots(spots)


  win.setCentralWidget(moduleArea)
  win.resize(1000, 500)
  win.setWindowTitle('Testing %s' % module.moduleName)
  win.show()


  app.start()
  win.close()
