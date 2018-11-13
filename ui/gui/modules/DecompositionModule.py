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
__author__ = "$Author: TJ Ragan $"
__date__ = "$Date: 2017-04-07 10:28:45 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from collections import OrderedDict, namedtuple

import pyqtgraph as pg
from ccpn.AnalysisMetabolomics.ui.gui.widgets.PcaWidget import PcaWidget
from ccpn.ui.gui.widgets.SideBar import _openSpectrumDisplay
from ccpn.util.Colour import hexToRgb

class DecompositionModule:
  """
  The bridge between the Qt world and the python world.

  Ideally, there are no Qt or pyqtgrpah specific calls here.
  """

  def __init__(self, application, mainWindow, interactor=None):
    self.widget = PcaWidget(mainWindow=mainWindow, presenter=self)
    self.interactor = interactor
    self.project = application.project
    self.current = application.current
    self.mainWindow = mainWindow

    self.__method = None
    self.__normalization = None
    self.__scaling = None
    self.__centerign = None

    self.setupWidget()
    self.setMethod('PCA')
    self.setNormalization('PQN')
    self.setCentering('mean')
    self.setScaling('Pareto')
    self.interactor.auto = True

    # self.plotLeft('left', None, None)


  def setupWidget(self):
    self.widget.settings.decompMethodPulldown.setData(['PCA',])
    self.widget.settings.normMethodPulldown.setData(['PQN', 'TSA', 'none'])
    self.widget.settings.centMethodPulldown.setData(['Mean', 'Median', 'none'])
    self.widget.settings.scalingMethodPulldown.setData(['Pareto', 'Unit Variance', 'none'])
    self.interactor.refreshSourceDataOptions()
    self.interactor.refreshSpectrumGroupFilter()


  def setSourceDataOptions(self, sourceData=None):
    self.widget.settings.sourceList.clear()
    if sourceData is not None:
      sdo = [s.name for s in sourceData]
      self.widget.settings.sourceList.addItems(sdo)

  def setSpectrumGroups(self, spectrumGroups=None):
    self.widget.settings.spectrumGroupsList.clear()
    if spectrumGroups is not None:
      self.widget.settings.spectrumGroupsList.setObjects(spectrumGroups)


  def setMethod(self, method):
    self.__method = method
    self.widget.settings.decompMethodPulldown.select(method)
    self.interactor.method = method

  def getMethod(self):
    return self.__method


  def getNormalization(self):
    return self.__normalization

  def setNormalization(self, normalization):
    self.__normalization = normalization
    self.widget.settings.normMethodPulldown.select(normalization)
    self.interactor.normalization = normalization


  def getCentering(self):
    return self.__centering

  def setCentering(self, centering):
    self.__centering = centering
    self.widget.settings.centMethodPulldown.select(centering)
    self.interactor.centering = centering


  def getScaling(self):
    return self.__scaling

  def setScaling(self, scaling):
    self.__scaling = scaling
    self.widget.settings.scalingMethodPulldown.select(scaling)
    self.interactor.scaling = scaling



  def setSourcesSelection(self, rowClicked):
    # should actually pass the selection to the interactor and have it bump back up...

    self.interactor.sources = [s.text() for s in self.widget.settings.sourceList.selectedItems()]


  def setAvailablePlotData(self, availablePlotData=None,
                           xDefaultLeft=None, yDefaultLeft=None,
                           xDefaultRight=None, yDefaultRight=None):
    if availablePlotData is None:
      availablePlotData = list(self.interactor.availablePlotData.keys())

    self.widget.pcaPlotLeft.xAxisSelector.setData(availablePlotData)
    self.widget.pcaPlotLeft.yAxisSelector.setData(availablePlotData)
    self.widget.pcaPlotRight.xAxisSelector.setData(availablePlotData)
    self.widget.pcaPlotRight.yAxisSelector.setData(availablePlotData)

    self.widget.pcaPlotLeft.xAxisSelector.select(xDefaultLeft)
    self.widget.pcaPlotLeft.yAxisSelector.select(yDefaultLeft)
    self.widget.pcaPlotRight.xAxisSelector.select(xDefaultRight)
    self.widget.pcaPlotRight.yAxisSelector.select(yDefaultRight)

  def getSourceDataColors(self):
    """
    Should this move to the interactors???
    """
    return [self.project.getByPid('SP:{}'.format(source)).sliceColour
            for source in self.interactor.sources]

  def getSpectra(self):
    """
    """
    return [self.project.getByPid('SP:{}'.format(source))
            for source in self.interactor.sources]

  def plot(self, target, xAxisLabel, yAxisLabel):
    target.plotItem.clear()
    xs = self.interactor.availablePlotData[xAxisLabel]
    ys = self.interactor.availablePlotData[yAxisLabel]
    if (xAxisLabel.upper().startswith('PC') or
        yAxisLabel.upper().startswith('PC')):
      colourBrushes = [pg.functions.mkBrush(hexToRgb(hexColour))
                       for hexColour in self.getSourceDataColors()]
      for x, y, spectrum, brush in zip(xs, ys, self.getSpectra(), colourBrushes):
        plot = target.plotItem.plot([x], [y], pen=None, symbol='o',
                             symbolBrush=brush,)
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
    saveName = self.widget.pcaOutput.sgNameEntryBox.text()
    descale = self.widget.pcaOutput.descaleCheck.isChecked()
    self.interactor.saveLoadingsToSpectra(prefix=saveName, descale=descale)

  # def plotLeft(self, side, xAxisDataLabel, yAxisDataLabel):
  #   if side.lower() in ('left', 'l'):
  #     p = self.widget.pcaPlotLeft.plotItem
  #   elif side.lower() in ('right', 'r'):
  #     p = self.widget.pcaPlotRight.plotItem
  #   else:
  #     raise ValueError('Must choose left or right plot.')
  #
  #   # x = xAxisDataLabel
  #   # y = yAxisDataLabel
  #   # p.plot(x, y)
  #
  #   p.setLabel('left', xAxisDataLabel, units='%')
  #   p.setLabel('bottom', yAxisDataLabel)
