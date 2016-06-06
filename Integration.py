"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - : 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                 " or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = ": rhfogh $"
__date__ = ": 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__version__ = ": 7686 $"

#=========================================================================================
# Start of code
#=========================================================================================

import numpy
import pyqtgraph as pg
from PyQt4 import QtGui

from ccpn.AnalysisMetabolomics.IntegralAssignment import IntegralTable
from ccpn.ui.gui.modules.GuiTableGenerator import GuiTableGenerator
from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.RadioButton import RadioButton

class IntegrationWidget(QtGui.QWidget, Base):

  def __init__(self, parent=None, project=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.pickButtonLabel = Label(self, 'Pick', grid=(0, 0))
    self.current = project._appBase.current
    self.linePoints = []
    self.integrationRegions = []
    self.pickOnSpectrumButton = Button(self, grid=(0, 1), toggle=True, icon='icons/target3+',hPolicy='fixed', callback=self.togglePicking)
    self.pickOnSpectrumButton.setChecked(False)
    self.currentAreaLabel = Label(self, 'Current Area ID ', grid=(0, 2))
    self.idLineEdit = LineEdit(self, grid=(0, 3))
    self.rangeLabel1 = Label(self, 'range ', grid=(0, 4))
    # self.rangeLabel2 = Label(self, 'Insert range here', grid=(0, 5))
    self.goButton = Button(self, 'GO', grid=(0, 5), callback=self.getParams)
    self.peakInAreaLabel = Label(self, 'Peaks in Area ', grid=(1, 0))
    columns = [('#', 'serial'), ('Height', lambda pk: self.getPeakHeight(pk)),
               ('Volume', lambda pk: self.getPeakVolume(pk)),
               ('Details', 'comment')]

    tipTexts=['Peak serial number', 'Magnitude of spectrum intensity at peak center (interpolated), unless user edited',
              'Integral of spectrum intensity around peak location, according to chosen volume method',
              'Textual notes about the peak']
    self.peakTable = GuiTableGenerator(self, objectLists=project.peakLists, columns=columns,
                                       selector=None, tipTexts=tipTexts, callback=self.tableCallback)
    self.layout().addWidget(self.peakTable, 1, 1, 3, 5)

  def togglePicking(self):
    if self.pickOnSpectrumButton.isChecked():
      self.turnOnPositionPicking()
    elif not self.pickOnSpectrumButton.isChecked():
      self.turnOffPositionPicking()

  def turnOnPositionPicking(self):
    self.current.registerNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.addItem(linePoint)
    for integrationRegion in self.integrationRegions:
      self.current.strip.plotWidget.addItem(integrationRegion)

  def turnOffPositionPicking(self):
    self.current.unRegisterNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.removeItem(linePoint)
    for integrationRegion in self.integrationRegions:
      self.current.strip.plotWidget.removeItem(integrationRegion)

  def setPositions(self, positions):
    if len(self.linePoints) % 2 == 0 or len(self.linePoints) == 0:
      line = pg.InfiniteLine(angle=90, pos=self.current.positions[0], movable=True, pen=(0, 0, 100))
      self.current.strip.plotWidget.addItem(line)
      self.linePoints.append(line)
    else:
      newIntegrationArea = pg.LinearRegionItem(values=[self.linePoints[-1].pos().x(), self.current.positions[0]])
      line = pg.InfiniteLine(angle=90, pos=self.current.positions[0], movable=True, pen=(0, 0, 100))
      self.current.strip.plotWidget.addItem(newIntegrationArea)
      self.current.strip.plotWidget.removeItem(self.linePoints[-1])
      self.integrationRegions.append(newIntegrationArea)
      self.linePoints.append(line)

  def tableCallback(self):
    pass

  def getParams(self):
    integralLines = [(i.lines[0].pos().x(), i.lines[1].pos().x()) for i in self.integrationRegions]
    spectra = [spectrumView.spectrum for spectrumView in self.current.strip.spectrumViews]
    for spectrum in spectra:
      spectrumData = spectrum._apiDataSource.get1dSpectrumData()
      for integralPair in integralLines:
        xPositions = numpy.where(numpy.logical_and(numpy.array(spectrumData[0])<integralPair[0], numpy.array(spectrumData[0])>integralPair[1]))
        yData = numpy.cumsum(spectrumData[1][xPositions[0]])
        xData = spectrumData[0][xPositions]
        self.current.strip.plotWidget.plot(xData, yData, pen=(0, 128, 0))




class IntegrationTable(QtGui.QWidget, Base):

  def __init__(self, parent=None, project=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)

    self.radioButton1 = RadioButton(self, grid=(0, 0), hAlign='r', callback=self.setupSpectralView)
    self.radioButton1.setChecked(True)
    self.label1 = Label(self, 'By Spectrum', grid=(0, 1), hAlign='l')
    self.radioButton2 = RadioButton(self, grid=(0, 2), hAlign='r', callback=self.setupAreaView)
    self.label2 = Label(self, 'By Area', grid=(0, 3), hAlign='l')
    self.integralTable = IntegralTable(self, project)
    self.layout().addWidget(self.integralTable, 1, 0, 2, 5)
    self.integralTable.label = Label(self.integralTable, 'Spectrum', grid=(0, 0))
    self.integralTable.peakListPulldown = PulldownList(self.integralTable, grid=(0, 1))
    self.project = project
    self.setupSpectralView()


  def setupSpectralView(self):
    self.integralTable.label.setText('Spectrum')
    self.integralTable.peakListPulldown.setData([spectrum.pid for spectrum in self.project.spectra])

  def setupAreaView(self):
    self.integralTable.label.setText('Area')
    self.integralTable.peakListPulldown.setData([])
