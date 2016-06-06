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

from PyQt4 import QtCore, QtGui

from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.Module import CcpnModule
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.RadioButton import RadioButton
from ccpn.ui.gui.widgets.Spinbox import Spinbox

from ccpn.ui.gui.modules.PeakTable import PeakListSimple

import pyqtgraph as pg

class AutoPick(QtGui.QWidget, Base):

  def __init__(self, parent=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)

    self.pickingLabel = Label(self, 'Autopick method', grid=(0, 0))
    self.methodPulldown = PulldownList(self, grid=(0, 1))
    self.goButton = Button(self, 'Go', grid=(2, 0), gridSpan=(1, 2))
    self.baselineLabel = Label(self, 'Baseline ', grid=(0, 2))
    self.baselineBox = Spinbox(self, grid=(0, 3))
    self.baselineLabel = Label(self, 'Gap ', grid=(0, 4))
    self.gapBox = DoubleSpinbox(self, grid=(0, 5))
    self.updateLayout()


  def updateLayout(self):
    for k in range(1, self.layout().columnCount()):
      item = self.layout().itemAtPosition(2, k)
      if item:
        if item.widget():
          item.widget().hide()
        self.layout().removeItem(item)
    for i in range(0, 8, 2):
      self.label1 = Label(self, 'Label 1', grid=(2, i))
      self.box1 = DoubleSpinbox(self, grid=(2, i+1))


class Fit(QtGui.QWidget, Base):

  def __init__(self, parent=None, strip=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)

    self.lineShapeLabel = Label(self, 'Lineshape ', grid=(0, 0))
    self.lineShapePulldown = PulldownList(self, grid=(0, 1))
    self.autoFitButton = Button(self, 'Autofit Selected', grid=(1, 0), gridSpan=(1, 2))
    self.ppmLabel = Label(self, 'ppm', grid=(0, 2))
    self.ppmBox = DoubleSpinbox(self, grid=(0, 3))
    self.linewidthLabel = Label(self, 'linewidth', grid=(0, 4))
    self.linewidthBox = DoubleSpinbox(self, grid=(0, 5))
    self.intensityLabel = Label(self, 'intensity', grid=(0, 6))
    self.intensityBox = Spinbox(self, grid=(0, 7))
    self.updateLayout()

  def updateLayout(self):
    for k in range(2, self.layout().columnCount()):
      item = self.layout().itemAtPosition(1, k)
      if item:
        if item.widget():
          item.widget().hide()
        self.layout().removeItem(item)
    for i in range(2, 8, 2):
      self.label1 = Label(self, 'Label 1', grid=(1, i))
      self.box1 = DoubleSpinbox(self, grid=(1, i+1))


class PickandFit(QtGui.QWidget, Base):
  def __init__(self, parent=None, strip=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.strip = strip
    tabWidget = QtGui.QTabWidget()
    tabWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
    tabWidget.addTab(AutoPick(self), "Autopick")
    tabWidget.addTab(Fit(self, strip), "Fit")
    self.layout().addWidget(tabWidget)


class PickandFitTable(QtGui.QWidget, Base):

  def __init__(self, parent=None, project=None, fitModule=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)

    # self.radioButton1 = RadioButton(self, grid=(0, 0))
    # self.label1 = Label(self, 'By Spectrum', grid=(0, 1))
    # self.radioButton2 = RadioButton(self, grid=(0, 2))
    # self.label2 = Label(self, 'By Area', grid=(0, 1))
    self.peakList = PeakListSimple(self, project, grid=(0, 0), gridSpan=(1, 4), callback=self.tableCallback)
    self.peakList.subtractPeakListsButton.hide()
    self.fitModule = fitModule

  def tableCallback(self, peak, row:int, col:int):
    if not peak:
      return
    centrePoint = 5.0
    self.positions1 = [centrePoint+2, centrePoint-2]
    self.positions2 = [centrePoint+2.5, centrePoint-2.5]
    self.positions3 = [1e9, 1e5]
    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
    self.lr1 = pg.LinearRegionItem(values=[self.positions1[0], self.positions1[1]], brush=brush)
    dashedLine1 = pg.InfiniteLine(angle=90, pos=self.positions2[0], movable=True)
    dashedLine2 = pg.InfiniteLine(angle=90, pos=self.positions2[1], movable=True)
    self.lr3 = pg.LinearRegionItem(values=[self.positions3[0], self.positions3[1]], orientation=pg.LinearRegionItem.Horizontal, brush=brush)
    dashedLine1.setPen(style=QtCore.Qt.DashLine, color='g')
    dashedLine2.setPen(style=QtCore.Qt.DashLine, color='g')
    for line in self.lr1.lines:
      line.setPen(color='b')
    self.fitModule.strip.plotWidget.addItem(self.lr1)
    self.fitModule.strip.plotWidget.addItem(dashedLine1)
    self.fitModule.strip.plotWidget.addItem(dashedLine2)
    self.fitModule.strip.plotWidget.addItem(self.lr3)
    self.lr1.sigRegionChanged.connect(self.lr1Moved)
    self.lr3.sigRegionChanged.connect(self.lr3Moved)
    self.lr1.setBounds([self.positions2[1]+0.5, self.positions2[0]-0.5])
    self.lr1.sigRegionChangeFinished.connect(self.setDashedLineBoundaries)
    dashedLine1.setBounds([self.positions1[0], None])
    dashedLine2.setBounds([None, self.positions1[1]])
    dashedLine1.sigPositionChanged.connect(self.lr2Moved)
    dashedLine2.sigPositionChanged.connect(self.lr2Moved)
    dashedLine1.sigPositionChangeFinished.connect(self.setRegionLimits)
    dashedLine2.sigPositionChangeFinished.connect(self.setRegionLimits)
    self.dashedLines = [dashedLine1, dashedLine2]

  #
  def lr1Moved(self):

    if self.lr1.lines[0].pos().x() !=  self.lr1.lines[1].pos().x():
      if self.lr1.lines[0].pos().x() < self.positions1[1]:
        diff = self.positions1[1] - self.lr1.lines[0].pos().x()
        self.positions1[1] -= diff
        self.positions1[0] += diff
        self.lr1.lines[1].setPos(self.positions1[0])

      if self.lr1.lines[0].pos().x() > self.positions1[1]:
        diff = self.positions1[1] - self.lr1.lines[0].pos().x()
        self.positions1[1] -= diff
        self.positions1[0] += diff
        self.lr1.lines[1].setPos(self.positions1[0])

      if self.lr1.lines[1].pos().x() > self.positions1[0]:
        diff = self.positions1[0] - self.lr1.lines[1].pos().x()
        self.positions1[1] += diff
        self.positions1[0] -= diff
        self.lr1.lines[0].setPos(self.positions1[1])

      if self.lr1.lines[1].pos().x() < self.positions1[0]:
        diff = self.positions1[0] - self.lr1.lines[1].pos().x()
        self.positions1[1] += diff
        self.positions1[0] -= diff
        self.lr1.lines[0].setPos(self.positions1[1])

  def lr2Moved(self):
    if self.dashedLines[0].pos().x() < self.positions2[1]:
      diff = self.positions2[1] - self.dashedLines[0].pos().x()
      self.positions2[1] -= diff
      self.positions2[0] += diff
      self.dashedLines[1].setPos(self.positions2[0])

    if self.dashedLines[0].pos().x() > self.positions2[1]:
      diff = self.positions2[1] - self.dashedLines[0].pos().x()
      self.positions2[1] -= diff
      self.positions2[0] += diff
      self.dashedLines[1].setPos(self.positions2[0])

    if self.dashedLines[1].pos().x() > self.positions2[0]:
      diff = self.positions2[0] - self.dashedLines[1].pos().x()
      self.positions2[1] += diff
      self.positions2[0] -= diff
      self.dashedLines[0].setPos(self.positions1[1])

    if self.dashedLines[1].pos().x() < self.positions2[0]:
      diff = self.positions2[0] - self.dashedLines[1].pos().x()
      self.positions2[1] += diff
      self.positions2[0] -= diff
      self.dashedLines[0].setPos(self.positions2[1])

  def setDashedLineBoundaries(self):
    self.dashedLines[0].setBounds([self.positions1[0], None])
    self.dashedLines[1].setBounds([None, self.positions1[1]])

  def setRegionLimits(self):
    self.lr1.setBounds([self.positions2[0]-0.5, self.positions2[1]+0.5])

  def lr3Moved(self):

    if self.lr3.lines[0].pos().y() < self.positions3[1]:
      diff = self.positions3[1] - self.lr3.lines[0].pos().y()
      self.positions3[1] -= diff
      self.positions3[0] += diff
      self.lr3.lines[1].setPos(self.positions3[0])

    if self.lr3.lines[0].pos().y() > self.positions3[1]:
      diff = self.positions3[1] - self.lr3.lines[0].pos().y()
      self.positions3[1] -= diff
      self.positions3[0] += diff
      self.lr3.lines[1].setPos(self.positions3[0])

    if self.lr3.lines[1].pos().y() > self.positions3[0]:
      diff = self.positions3[0] - self.lr3.lines[1].pos().y()
      self.positions3[1] += diff
      self.positions3[0] -= diff
      self.lr3.lines[0].setPos(self.positions3[1])

    if self.lr3.lines[1].pos().y() < self.positions3[0]:
      diff = self.positions3[0] - self.lr3.lines[1].pos().y()
      self.positions3[1] += diff
      self.positions3[0] -= diff
      self.lr3.lines[0].setPos(self.positions3[1])