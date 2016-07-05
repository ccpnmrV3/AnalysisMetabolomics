__author__ = 'TJ Ragan'

from collections import OrderedDict, namedtuple

import pyqtgraph as pg
from ccpn.AnalysisMetabolomics.ui.gui.widgets.PcaWidget import PcaWidget

from ccpn.util.Colour import hexToRgb

class DecompositionModule:
  """
  The bridge between the Qt world and the python world.

  Ideally, there are no Qt or pyqtgrpah specific calls here.
  """

  def __init__(self, application, parent=None, interactor=None):
    self.widget = PcaWidget(parent=parent.mainWindow, presenter=self)
    self.interactor = interactor
    self.project = application.project
    self.current = application.current

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


  def setSourceDataOptions(self, sourceData=None):
    self.widget.settings.sourceList.clear()
    if sourceData is not None:
      sdo = [s.name for s in sourceData]
      self.widget.settings.sourceList.addItems(sdo)


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


  def plot(self, target, xAxisLabel, yAxisLabel):
    x = self.interactor.availablePlotData[xAxisLabel]
    y = self.interactor.availablePlotData[yAxisLabel]

    if (xAxisLabel.upper().startswith('PC') or
        yAxisLabel.upper().startswith('PC')):
      colourBrushes = [pg.functions.mkBrush(hexToRgb(hexColour))
                       for hexColour in self.getSourceDataColors()]
      target.plotItem.plot(x, y, pen=None, symbol='o',
                           symbolBrush=colourBrushes, clear=True)
    else:
      target.plotItem.plot(x, y, symbol='o', clear=True)

    if xAxisLabel.upper().startswith('PC'):
      target.addYOriginLine()
    if yAxisLabel.upper().startswith('PC'):
      target.addXOriginLine()

    target.plotItem.setLabel('bottom', xAxisLabel)
    target.plotItem.setLabel('left', yAxisLabel)


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
