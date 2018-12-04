"""Module Documentation here



Warning: this module can be overloaded with too many operations and plots hierarchies from PyQtGraph.
Could be beneficial to split in more classes or custom subclasses.


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
from functools import partial
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
from ccpn.core.Spectrum import Spectrum
from ccpn.core.SpectrumGroup import SpectrumGroup
from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.widgets.HLine import HLine
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.Tabs import Tabs
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.Menu import Menu
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.ListWidget import ListWidget
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.ui.gui.widgets.CustomExportDialog import CustomExportDialog
from ccpn.ui.gui.widgets.BarGraph import CustomViewBox
from ccpn.ui.gui.lib.mouseEvents import \
  leftMouse, shiftLeftMouse, controlLeftMouse, controlShiftLeftMouse, \
  middleMouse, shiftMiddleMouse, controlMiddleMouse, controlShiftMiddleMouse, \
  rightMouse, shiftRightMouse, controlRightMouse, controlShiftRightMouse
from ccpn.ui.gui.guiSettings import autoCorrectHexColour, getColours, CCPNGLWIDGET_HEXBACKGROUND,\
  GUISTRIP_PIVOT, DIVIDER, CCPNGLWIDGET_SELECTAREA, CCPNGLWIDGET_HIGHLIGHT
from ccpn.ui.gui.widgets.SideBar import _openItemObject
from ccpn.util.Colour import hexToRgb,rgbaRatioToHex
from collections import OrderedDict
from ccpn.core.lib.Notifiers import Notifier
from ccpn.framework.Current import PCAcompontents
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

PREFIX = 'PCA_output'
PCA_inROI_ = 'PCA_ROI_'

DefaultRoi = [[0, 0], [10, 10]]#

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
std = 'std'
#
pareto = 'pareto'
variance = 'unit variance'

# colours
BackgroundColour = getColours()[CCPNGLWIDGET_HEXBACKGROUND]
OriginAxes = pg.functions.mkPen(hexToRgb(getColours()[GUISTRIP_PIVOT]), width=1, style=QtCore.Qt.DashLine)
SelectedPoint = pg.functions.mkPen(rgbaRatioToHex(*getColours()[CCPNGLWIDGET_HIGHLIGHT]), width=5)

ROIline = rgbaRatioToHex(*getColours()[CCPNGLWIDGET_SELECTAREA])



def percentage(percent, whole):
  return (percent * whole) / 100.0


class Decomposition:
  """
  Base class for the Decomposition Module (the old "interactor"`!)
  """

  def __init__(self, project):
    self.project = project
    self.__sources = [] # list of pids
    self.__normalization = PQN # str
    self.__centering = mean # str
    self.__scaling = pareto # str
    self.__data = None  #will be a dataframe containg the 1D array of spectral intensities and the relative pid
    self.__sourcesChanged = True
    self.__normChanged = True
    self.__centChanged = True
    self.__scalingChanged = True
    self.__deScaleFunc = lambda x: x
    self.model = None # PCA base class
    self.auto = True # if auto will init the decomposition


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
      self.decompose(self.__data)

  @property
  def centering(self):
    return self.__centering

  @centering.setter
  def centering(self, value):
    self.__centering = value
    if self.auto:
      self.decompose(self.__data)

  @property
  def scaling(self):
    return self.__scaling

  @scaling.setter
  def scaling(self, value):
    self.__scaling = value
    # self.__scalingChanged = True
    if self.auto:
      self.decompose(self.__data)

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
    """ scores as a pandas dataframe """

    if self.model is not None:
      scores = self.model.scores_
      return scores

  @property
  def variance(self):
    """ Variance as a pandas dataframe"""
    if self.model is not None:
      variance = self.model.explainedVariance_
      return variance

  @property
  def loadings(self):
    """ loadings as a pandas dataframe"""
    if self.model is not None:
      loadings = self.model.loadings_
      return loadings


  def decompose(self, data = None):
    """
    get the data, init the pca model and then plot the results
    """
    success = False
    if data is None:
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



  @cached('_buildSourceData', maxItems=256, debug=False)
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

  @staticmethod
  def splitDataWithinRange(scores, xLabel, yLabel, minX, maxX, minY, maxY):
    """
    :param scores: dataframe with all scores
    :param xLabel: label1 , eg PC1
    :param yLabel: label1 , eg PC2
    :param minX:  min value for Y
    :param maxX:  Max value for X
    :param minY: min value for Y
    :param maxY: max value for Y
    :return:  inners  dataframe like scores but containing only the values within the ranges  and
              outers (rest) not included in inners
    """

    bools = scores[xLabel].between(minX, maxX, inclusive=True) & scores[yLabel].between(minY, maxY, inclusive=True)
    inners = scores[bools]
    outers = scores[-bools]
    filteredInners = inners.filter(items=[xLabel, yLabel])
    filteredOuters = outers.filter(items=[xLabel, yLabel])

    return  filteredInners, filteredOuters

  def createSpectrumGroupFromScores(self, spectra, prefix=PREFIX):
    """

    :param outlinersDataFrame:
    :return: a spectrumGroup with the spectra which had outliners values
    """

    # need to check if they are all spectra
    sgNames = [sg.name for sg in self.project.spectrumGroups if sg.name.startswith(prefix)]
    prefix += str(len(sgNames)+1)
    if not self.project.getByPid('SG:'+prefix):
      g = self.project.newSpectrumGroup(prefix, spectra)
    else:
      g = self.project.newSpectrumGroup(prefix+prefix, spectra)
    return g


  def saveLoadingsToSpectra(self, prefix=PREFIX, descale=True, components=None):
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
    self._exportDialog = None
    self.application = None


    if self.mainWindow: # without mainWindow will open only the Gui
      self.current = self.mainWindow.current
      self.application = self.mainWindow.application
      self.project = self.mainWindow.project
      self.decomposition = Decomposition(self.project)
      self.decomposition.auto = True

      # notifiers

      self._selectPCAcompNotifier = Notifier(self.current, [Notifier.CURRENT], targetName=PCAcompontents
                                             , onceOnly=True, callback=self._selectCurrentPCAcompNotifierCallback)

    ####  Main Widgets

    mi = 0 # main (row) index
    labelSource =  Label(self.mainWidget, 'Sources:', grid=(mi,0), gridSpan=(mi+1,0))
    mi += 1
    self.sourceList = ListWidget(self.mainWidget, acceptDrops=True, grid=(mi,0), gridSpan=(mi,0))
    self.sourceList.setSelectDeleteContextMenu()
    self.sourceList.dropped.connect(self._sourceListDroppedCallback)
    self.sourceList.setMaximumHeight(100)
    self.sourceList.itemSelectionChanged.connect(self._setSourcesSelection)
    mi += 1

    self.tabWidget = Tabs(self.mainWidget, grid=(mi, 0), gridSpan=(1, 3))
    ## 1 Tab Scatter
    self.scatterFrame = Frame(self.mainWidget, setLayout=True)
    self.scatterFrame.setContentsMargins(1, 10, 1, 10)
    self._setScatterTabWidgets(layoutParent=self.scatterFrame)
    self.tabWidget.addTab(self.scatterFrame, 'Scatter')

    ## 2 Tab Vectors Disabled as not implemented yet
    self.vectorFrame = Frame(self.mainWidget, setLayout=True)
    self.vectorFrame.setContentsMargins(1, 10, 1, 10)
    self._setVectorTabWidgets(layoutParent=self.vectorFrame)
    self.tabWidget.addTab(self.vectorFrame, 'Vectors')

    ## 3 Tab Variance 
    self.varianceFrame = Frame(self.mainWidget, setLayout=True)
    self.varianceFrame.setContentsMargins(1, 10, 1, 10)
    self._setVarianceTabWidgets(layoutParent=self.varianceFrame)
    self.tabWidget.addTab(self.varianceFrame, 'Variance')

    ### Other buttons
    mi += 1
    self.buttonList = ButtonList(self.mainWidget, texts=['Save as dataset', 'Export...'], callbacks=[None,None],
                                 grid=(mi, 0))
    self.buttonList.setEnabled(False)

    #### Settings widgets
    self._setSettingsWidgets()

    self._selectedObjs = [] # This list is used to set the current PCAcomponent.
                            # The components are extended in a list for speeding up the multiSelections and reducing the notifier load.
                            # This will also allow selection if current doesn't exist, e.g. if this module is used as stand alone GUI
                            # for plotting.
    if self.current:
      self._selectedObjs = list(self.current.pcaComponents)


  def _setSettingsWidgets(self):
    """
    Creates all the settings widgets
    """
    si = 0  # Settings (row) index
    l = Label(self.settingsWidget, 'Name:', grid=(si, 0))
    self.sgNameEntryBox = LineEdit(self.settingsWidget, text='pca', grid=(si, 1))
    si += 1

    l = Label(self.settingsWidget, 'Descale Components:', grid=(si, 0))
    self.descaleCheck = CheckBox(self.settingsWidget, checked=True, grid=(si, 1))
    si += 1
    l = Label(self.settingsWidget, 'Normalisation:', grid=(si, 0))
    self.normMethodPulldown = PulldownList(self.settingsWidget, callback=self._setNormalization, grid=(si, 1))
    self.normMethodPulldown.setData([PQN, TSA, none])
    si += 1
    l = Label(self.settingsWidget, 'Centring:', grid=(si, 0))
    self.centMethodPulldown = PulldownList(self.settingsWidget, callback=self._setCentering, grid=(si, 1))
    self.centMethodPulldown.setData([mean, median, none])
    si += 1
    l = Label(self.settingsWidget, 'Scaling:', grid=(si, 0))
    self.scalingMethodPulldown = PulldownList(self.settingsWidget, callback=self.setScaling, grid=(si, 1))
    self.scalingMethodPulldown.setData([pareto, variance, none])
    si += 1
    HLine(self.settingsWidget, grid=(si, 0), gridSpan=(0, 2), colour=getColours()[DIVIDER], height=5)

    l = Label(self.settingsWidget, 'ROI:', grid=(si, 0))
    self.roiCheckbox = CheckBox(self.settingsWidget, checked=False, callback=self._toggleROI, grid=(si, 1))
    self._toggleROI()

    si += 1
    l = Label(self.settingsWidget, 'Centre:', grid=(si, 0))
    self.roiMethodPulldown = PulldownList(self.settingsWidget, callback=self._roiPresetCallBack, grid=(si, 1))
    self.roiMethodPulldown.setData([mean, median, std], objects=[np.mean, np.median, np.std])
    si += 1
    l = Label(self.settingsWidget, '%:', grid=(si, 0))
    self.roiPercValue = Spinbox(self.settingsWidget, value=10, min=1, grid=(si, 1))
    self.roiPercValue.valueChanged.connect(self._roiPresetCallBack)

  ########### Generic functions to 'talk' with the decomposition base class ############

  def getPcaResults(self):
    """ gets the results from the base class decomposition """

    if self.decomposition is not None:
      scoresDF = self.decomposition.scores
      if scoresDF is not None:
        if scoresDF.shape[0] > 1: #No point in plotting
          return scoresDF

  def getVarianceResults(self):
    """ gets the results from the base class decomposition """

    if self.decomposition is not None:
      varianceDF = self.decomposition.variance
      if varianceDF is not None:
        if varianceDF.shape[0] > 1: #No point in plotting
          return varianceDF


  def getVectorsResults(self):
    """ gets the results from the base class decomposition """

    if self.decomposition is not None:
      vectorsDF = self.decomposition.loadings
      if vectorsDF is not None:
        if vectorsDF.shape[0] > 1:
          return vectorsDF

  ########### Create all widgets for each tab ############

  def _setScatterTabWidgets(self, layoutParent):
    ### Scatter Plot setup
    self._scatterView = pg.GraphicsLayoutWidget()
    self._scatterView.setBackground(BackgroundColour)
    self._plotItem = self._scatterView.addPlot()
    self._scatterViewbox = self._plotItem.vb
    self._addScatterSelectionBox()
    self._scatterViewbox.mouseClickEvent = self._scatterViewboxMouseClickEvent
    self._scatterViewbox.mouseDragEvent = self._scatterMouseDragEvent
    self._scatterViewbox.scene().sigMouseMoved.connect(self.mouseMoved) #use this if you need the mouse Posit
    self._plotItem.setMenuEnabled(False)

    self.scatterPlot = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
    self.scatterPlot.sigClicked.connect(self._plotClicked)
    self.roi = pg.ROI(*DefaultRoi, pen=ROIline)
    self._setROIhandles()
    self.roi.sigRegionChangeFinished.connect(self.getROIdata)
    self.xLine = pg.InfiniteLine(angle=90, pos=0, pen=OriginAxes)
    self.yLine = pg.InfiniteLine(angle=0, pos=0, pen=OriginAxes)

    self._plotItem.addItem(self.scatterPlot)
    self._plotItem.addItem(self.roi)
    self._plotItem.addItem(self.xLine)
    self._plotItem.addItem(self.yLine)
    layoutParent.getLayout().addWidget(self._scatterView)

    f = Frame(layoutParent, setLayout=True, grid=(1,0))
    self.xAxisSelector = Spinbox(f, prefix='X: PC', min=1, grid=(0, 0))
    self.yAxisSelector = Spinbox(f, prefix='Y: PC', min=1, grid=(0, 1))
    self.yAxisSelector.valueChanged.connect(self._axisChanged)
    self.xAxisSelector.valueChanged.connect(self._axisChanged)

  def _setVectorTabWidgets(self, layoutParent):
    ### Scatter Plot setup
    self._vectorsView = pg.GraphicsLayoutWidget()
    self._vectorsView.setBackground(BackgroundColour)
    self.vectorsPlot = self._vectorsView.addPlot()
    self._vectorsViewbox = self.vectorsPlot.vb
    self.vectorsPlot.setMenuEnabled(False)
    self.vectorsPlot.setLabel('bottom', 'Points')
    layoutParent.getLayout().addWidget(self._vectorsView)
    self.xVectorSelector = Spinbox(layoutParent, prefix='PC', grid=(1, 0))
    self.xVectorSelector.valueChanged.connect(self._xVectorSelectorChanged)

  def _setVarianceTabWidgets(self, layoutParent):
    ### Scatter Plot setup
    self._varianceView = pg.GraphicsLayoutWidget()
    self._varianceView.setBackground(BackgroundColour)
    self.variancePlot = self._varianceView.addPlot()
    self._varianceViewbox = self.variancePlot.vb
    self.variancePlot.setMenuEnabled(False)
    self.variancePlot.setLabel('bottom', 'PC component')
    self.variancePlot.setLabel('left', 'Variance')
    layoutParent.getLayout().addWidget(self._varianceView)


  ########### ROI box for scatter Plot ############

  def _roiPresetCallBack(self, *args):
    v = self.roiMethodPulldown.getObject()
    perc = self.roiPercValue.get()
    self.presetROI(v, perc)

  def _roiMouseActionCallBack(self, *args):
    """ called by the context menu. Sets the settings checkbox, The settings CB will do the actual work"""
    self.roiCheckbox.set(not self.roiCheckbox.get())
    self._toggleROI()

  def _toggleROI(self,*args):
    """ Toggle the ROI from the scatter plot"""
    v = self.roiCheckbox.get()
    if v:
      self.roi.show()
    else:
      self.roi.hide()

  def _setROIhandles(self):
    """ sets the handle in each corners, no matter the roi sizes """
    self.roi.addScaleHandle([1, 1], [0.5, 0.5], name = 'topRight')
    self.roi.addScaleHandle([0, 1], [1, 0],     name = 'topLeft')
    self.roi.addScaleHandle([0, 0], [0.5, 0.5], name = 'bottomLeft')
    self.roi.addScaleHandle([1, 0], [0, 1],     name = 'bottomRight'),

  def getROIdata(self):
    """
    the values for the ROI
    (getState returns a dict ['pos']  left bottom corner, ['size'] the size of RO1 and ['angle'] for this RectROI is 0)
    :return: a list of rectangle coordinates in the format minX, maxX, minY, maxY
    """
    state = self.roi.getState()
    pos = state['pos']
    size = state['size']
    xMin = pos[0]
    xMax = pos[0]+size[0]
    yMin = pos[1]
    yMax = pos[1] + size[1]
    return [xMin, xMax, yMin, yMax]

  def presetROI(self, func = np.median, percent=20):
    """
    Apply the function (default np.mean) to the currently displayed plot data
    to get the x,y values for setting the ROI box.
    :param func: a function applicable to the x,y data
    :return: set the ROI on the scatter plot
    """

    x, y = self.scatterPlot.getData()
    if not len(x)>0 and not len(y)> 0:
      return

    xR = func(x)
    yR = func(y)
    xRange = np.max(x) - np.min(x)
    yRange = np.max(y) - np.min(y)

    xperc = percentage(percent, xRange)
    yperc = percentage(percent, yRange)

    xMin = xR - xperc
    yMin = yR - yperc
    xMax = xR + xperc
    yMax = yR + yperc

    self.setROI(xMin, xMax, yMin, yMax)

  def setROI(self, xMin,xMax,yMin,yMax):
    """
    a conversion mechanism to the internal roi setState
    :param xMin:
    :param xMax:
    :param yMin:
    :param yMax:
    :return:  set the ROI box
     """

    state = {'pos':[], 'size':[], 'angle':0}
    xSize = abs(xMin) + xMax
    ySize = abs(yMin) + yMax
    state['pos'] = [xMin,yMin]
    state['size'] = [xSize, ySize]
    self.roi.setState(state)

  ## Scatter Selection box

  def _addScatterSelectionBox(self):
    self._scatterSelectionBox = QtWidgets.QGraphicsRectItem(0, 0, 1, 1)
    self._scatterSelectionBox.setPen(pg.functions.mkPen((255, 0, 255), width=1))
    self._scatterSelectionBox.setBrush(pg.functions.mkBrush(255, 100, 255, 100))
    self._scatterSelectionBox.setZValue(1e9)
    self._scatterViewbox.addItem(self._scatterSelectionBox, ignoreBounds=True)
    self._scatterSelectionBox.hide()

  def _updateScatterSelectionBox(self, p1:float, p2:float):
    """
    Updates drawing of selection box as mouse is moved.
    """
    vb = self._scatterViewbox
    r = QtCore.QRectF(p1, p2)
    r = vb.childGroup.mapRectFromParent(r)
    self._scatterSelectionBox.setPos(r.topLeft())
    self._scatterSelectionBox.resetTransform()
    self._scatterSelectionBox.scale(r.width(), r.height())
    self._scatterSelectionBox.show()
    minX = r.topLeft().x()
    minY = r.topLeft().y()
    maxX = minX+r.width()
    maxY = minY+r.height()
    return [minX,maxX,minY,maxY]


  def _scatterMouseDragEvent(self, event):
    """
    Re-implementation of PyQtGraph mouse drag event to allow custom actions off of different mouse
    drag events. Same as spectrum Display. Check Spectrum Display View Box for more documentation.

    """
    if leftMouse(event):
      pg.ViewBox.mouseDragEvent(self._scatterViewbox, event)

    elif controlLeftMouse(event):
      self._updateScatterSelectionBox(event.buttonDownPos(), event.pos())
      event.accept()
      if not event.isFinish():
        self._updateScatterSelectionBox(event.buttonDownPos(), event.pos())

      else: ## the event is finished.
        pts = self._updateScatterSelectionBox(event.buttonDownPos(), event.pos())
        if self.decomposition:
          i, o = self.decomposition.splitDataWithinRange(self.getPcaResults(),
                                                         *self._getSelectedAxesLabels(), *pts)
          self._selectedObjs.extend(i.index)
          self._selectScatterPoints()
        self._resetSelectionBox()

    else:
      self._resetSelectionBox()
      event.ignore()

  def _resetSelectionBox(self):
    "Reset/Hide the boxes "
    self._successiveClicks = None
    self._scatterSelectionBox.hide()
    self._scatterViewbox.rbScaleBox.hide()



  def _clearScatterSelection(self):
    self._selectedObjs = []
    self._selectScatterPoints()

  def _selectScatterPoints(self):
    self.scatterPlot.clear()
    if self.current:
      self.current.pcaComponents = self._selectedObjs
    else: # do selection same. E.g. if used as stand alone module
      self.plotPCAscatterResults(self.getPcaResults(), *self._getSelectedAxesLabels(), highLight=self._selectedObjs)

  def _invertScatterSelection(self):
    invs = [point.data() for point in self.scatterPlot.points() if point.data() not in self._selectedObjs]
    self._selectedObjs= invs
    self._selectScatterPoints()

  def _selectFromROI(self):

    scores = self.getPcaResults()
    if scores is not None:
      roi = self.getROIdata()
      i,o = self.decomposition.splitDataWithinRange(scores, *self._getSelectedAxesLabels(), *roi)
      if i is not None:
        self._selectedObjs = i.index
        self._selectScatterPoints()


  def _createGroupSelection(self):
    """ Create groups from selection. Implemented only for Spectrum Group """
    if all(isinstance(x, Spectrum) for x in self._selectedObjs):
      self.decomposition.createSpectrumGroupFromScores(self._selectedObjs)
    else:
      getLogger().warn('Impossible to create groups. This functionality works only with spectra')

  def _openSelected(self):
    try:
      _openItemObject(self.mainWindow, self._selectedObjs)
    except:
      getLogger().warn('Impossible to create Groups')

  def _getObjFromPoints(self, points=None):
    if points is None:
      points = self.scatterPlot.points()
    df = pd.DataFrame(points, index = [point.data() for point in points], columns=['item'])
    return df

  def _selectCurrentPCAcompNotifierCallback(self, data):
    """ called when a PCA components gets in current"""
    self._selectedObjs = list(self.current.pcaComponents)
    self.plotPCAscatterResults(self.getPcaResults(), *self._getSelectedAxesLabels(), highLight=self._selectedObjs)

  ########### PCA scatter Plot related  ############

  def _getSelectedAxesLabels(self):
    xl = PC + str(self.xAxisSelector.get())
    yl = PC + str(self.yAxisSelector.get())
    return [xl,yl]

  def plotPCAscatterResults(self, dataFrame, xAxisLabel='PC1', yAxisLabel='PC2', highLight=None):
    """

    :param dataFrame: in the format from the PCA Class
          index: Pid --> obj or str of pid
          Columns: PCx  x= 1 to the end. Eg. PC1, PC2, etc
    :return:  transform the dataFrame in the plottable data format and plot it on the scatterPlot

    """
    if highLight is None:
      highLight = self._selectedObjs

    if dataFrame is None:
      self.scatterPlot.clear()
      return
    spots = []
    for obj, row in dataFrame.iterrows():
      dd = {'pos': [0, 0], 'data': 'obj', 'brush': pg.mkBrush(255, 255, 255, 120), 'symbol': 'o', 'size': 10, 'pen':None}
      dd['pos'] = [row[xAxisLabel], row[yAxisLabel]]
      dd['data'] = obj
      if hasattr(obj, 'sliceColour'):
        dd['brush'] = pg.functions.mkBrush(hexToRgb(obj.sliceColour))
      if obj in highLight:
        dd['pen'] = SelectedPoint
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

  def _setAxes(self, scores):
    """ Set X and Y axes from the PCA scores dataFrame.
     This because we don't know at priory how many PC we will have. Defaults PC1 and PC2"""
    if scores is not None:
      maxPC = scores.shape[1]
      if maxPC>1:
        self.xAxisSelector.setMaximum(maxPC)
        self.yAxisSelector.setMaximum(maxPC)
        self.xAxisSelector.set(1)
        self.yAxisSelector.set(2)

    else:
      self.scatterPlot.clear()

  def _clearPlots(self):
    """ Clear the scatter plot and the decomposition sources. """
    self.scatterPlot.clear()
    self.vectorsPlot.clear()
    self.variancePlot.clear()
    self.scatterPlot.viewTransformChanged()
    self.decomposition.sources = []

  def _axisChanged(self, *args):
    """callback from axis pulldowns which will replot the scatter"""
    self.plotPCAscatterResults(self.getPcaResults(), *self._getSelectedAxesLabels(), highLight=self._selectedObjs)

  def refreshPlots(self):
    """ Refreshes all module by resetting the sources"""
    self._setSourcesSelection()

  def _createGroupFromROI(self, inside=True):

    xsel = self.xAxisSelector.get()
    ysel = self.yAxisSelector.get()
    xl = PC + str(xsel)
    yl = PC + str(ysel)
    scores = self.getPcaResults()
    if scores is not None:
      roi = self.getROIdata()
      i,o = self.decomposition.splitDataWithinRange(scores, xl, yl, *roi)
      if inside:
        self.decomposition.createSpectrumGroupFromScores(list(i.index))
      else:
        self.decomposition.createSpectrumGroupFromScores(list(i.index))

  def _scatterViewboxMouseClickEvent(self, event):

    if event.button() == QtCore.Qt.RightButton:
      event.accept()
      self._raiseScatterContextMenu(event)

    elif event.button() == QtCore.Qt.LeftButton:
      self._clearScatterSelection()
      event.accept()

  def mouseMoved(self, event):
    """
    use this if you need for example display the mouse coords on display
    :param event:
    :return:
    """
    pass
    # position = event
    # if self._scatterViewbox.sceneBoundingRect().contains(position):
    #   mousePoint = self._scatterViewbox.mapSceneToView(position)
    #   x = mousePoint.x()
    #   y =  mousePoint.y()


  def _showExportDialog(self, viewBox):
    """
    :param viewBox: the viewBox obj for the selected plot
    :return:
    """
    if self._exportDialog is None:
      self._exportDialog = CustomExportDialog(viewBox.scene(), titleName='Exporting')
    self._exportDialog.show(viewBox)

  def _raiseScatterContextMenu(self, ev):

    self._scatterContextMenu = Menu('', None, isFloatWidget=True)
    self._scatterContextMenu.addAction('Reset View', self._plotItem.autoRange)
    self._scatterContextMenu.addSeparator()

    # Selection
    self.resetSelectionAction = QtGui.QAction("Clear selection", self,
                                              triggered=self._clearScatterSelection)
    self._scatterContextMenu.addAction(self.resetSelectionAction)

    self.invertSelectionAction = QtGui.QAction("Invert selection", self,
                                              triggered=self._invertScatterSelection)
    self._scatterContextMenu.addAction(self.invertSelectionAction)


    self.groupSelectionAction = QtGui.QAction("Create Group from selection", self,
                                           triggered=self._createGroupSelection)

    self._scatterContextMenu.addAction(self.groupSelectionAction)
    self._openSelectedAction = QtGui.QAction("Open selected", self,
                                              triggered=self._openSelected)

    self._scatterContextMenu.addAction(self._openSelectedAction)
    self._scatterContextMenu.addSeparator()

    self._scatterContextMenu.addSeparator()
    self.exportAction = QtGui.QAction("Export image...", self, triggered=partial(self._showExportDialog, self._scatterViewbox))
    self._scatterContextMenu.addAction(self.exportAction)

    self._scatterContextMenu.exec_(ev.screenPos().toPoint())

  ########### Variance Plot ############

  def plotVariance(self, varianceDataFrame):
    # scoresDF.insert(0,'Variance',self.explainedVariance_.values)
    # scoresDF.insert(0,'#',np.arange(1,scoresDF.shape[0]+1))
    if varianceDataFrame is not None:
      x = np.arange(1,varianceDataFrame.shape[0]+1)
      y = varianceDataFrame
      self.variancePlot.plot(x, y, symbol='o', clear=True)
    else:
      self.variancePlot.clear()


  ########### Vectors Plot ############

  def _setVectorSelector(self, vectorsDataFrame):
    if vectorsDataFrame is not None:
      vMax = vectorsDataFrame.shape[0]
      self.xVectorSelector.set(1)
      self.xVectorSelector.setMinimum(1)
      self.xVectorSelector.setMaximum(vMax)

  def _xVectorSelectorChanged(self, value):
    self.plotVectors(self.decomposition.loadings, value )

  def plotVectors(self, vectorsDataFrame, pcComponent):

    pcComponentLabel = PC+str(pcComponent)
    if pcComponentLabel in vectorsDataFrame.index:
      if vectorsDataFrame is not None:
        y = vectorsDataFrame.ix[pcComponentLabel]
        self.vectorsPlot.plot(y.values, pen='r',clear=True,)
      else:
        self.vectorsPlot.clear()

  ########### Settings widgets callback  ############

  def _setSourcesSelection(self):
    """ When selecting the item in the source ListWidget it starts the pca machinery
    The Source widgets checks if has enough item to start, otherwise it clears itself.
    """

    if len(self.sourceList.getSelectedTexts()) == 0:  # if nothing selected, then do nothing
      self._clearPlots()
      return

    elif len(self.sourceList.getSelectedTexts()) == 1:  # only SG is allowed a single selection
      obj = self.project.getByPid(self.sourceList.getSelectedTexts()[0])
      if not isinstance(obj, SpectrumGroup):
        self._clearPlots()
        return

    self.decomposition.sources = self.sourceList.getSelectedTexts()
    self._setAxes(scores=self.getPcaResults())
    self._axisChanged()
    self._roiPresetCallBack()
    self._setVectorSelector(self.getVectorsResults())
    self.plotVariance(varianceDataFrame=self.getVarianceResults())

  def _sourceListDroppedCallback(self, ll):
    if len(ll)>0:
      data = ll[0]
      pids = data.get('pids')
      self.sourceList.selectItems(pids)

  def _setNormalization(self, normalization):
    if self.decomposition:
      self.normMethodPulldown.select(normalization)
      self.decomposition.normalization = normalization
      if self.getPcaResults() is not None:
        self.refreshPlots()

  def _setCentering(self, centering):
    if self.decomposition:
      self.centMethodPulldown.select(centering)
      self.decomposition.centering = centering
      if self.getPcaResults() is not None:
        self.refreshPlots()

  def setScaling(self, scaling):
    if self.decomposition:

      self.scalingMethodPulldown.select(scaling)
      self.decomposition.scaling = scaling
      if self.getPcaResults() is not None:
        self.refreshPlots()


  def saveOutput(self):
    saveName = self.sgNameEntryBox.text()
    descale = self.descaleCheck.isChecked()
    self.decomposition.saveLoadingsToSpectra(prefix=saveName, descale=descale)


  def _closeModule(self):
    """Re-implementation of closeModule function from CcpnModule to unregister notification """
    if self._selectPCAcompNotifier is not None:
      self._selectPCAcompNotifier.unRegister()
    super(PcaModule, self)._closeModule()


if __name__ == '__main__':
  from PyQt5 import QtGui, QtWidgets
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.widgets.CcpnModuleArea import CcpnModuleArea

  n = 300
  pos = np.random.normal(size=(2, n), scale=1e-5)
  spots = [{'pos': pos[:, i], 'data': 1} for i in range(n)] + [{'pos': [0, 0], 'data': 1}]


  app = TestApplication()
  win = QtWidgets.QMainWindow()

  moduleArea = CcpnModuleArea(mainWindow=None)
  module = PcaModule(mainWindow=None, name='My Module')
  moduleArea.addModule(module)


  module.scatterPlot.addPoints(spots)

  win.setCentralWidget(moduleArea)
  win.resize(1000, 500)
  win.setWindowTitle('Testing %s' % module.moduleName)
  win.show()


  app.start()
  win.close()
