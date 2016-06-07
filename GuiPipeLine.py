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

from PyQt4 import QtGui, QtCore
from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.ListWidget import ListWidget
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Spinbox import Spinbox
import pyqtgraph as pg

from functools import partial


class PolyBaseline(QtGui.QWidget, Base):


  def __init__(self, parent=None, project=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.current = project._appBase.current
    self.orderLabel = Label(self, 'Order ', grid=(0, 0))
    self.orderBox = Spinbox(self, grid=(0, 1))
    self.orderBox.setMinimum(2)
    self.orderBox.setMaximum(5)
    if self.current.spectrumGroup is not None:
      self.controlPointMaximum = max([spectrum.spectrumLimits[0][1] for spectrum in self.current.spectrumGroup.spectra])
      self.controlPointMinimum = min([spectrum.spectrumLimits[0][0] for spectrum in self.current.spectrumGroup.spectra])
    else:
      self.controlPointMaximum = None
      self.controlPointMinimum = None

    self.controlPointStepSize = 0.01
    # self.orderBox.setValue(2)
    self.orderBox.valueChanged.connect(self.updateLayout)
    self.controlPointsLabel = Label(self, 'Control Points ', grid=(0, 2))
    self.pickOnSpectrumButton = Button(self, grid=(0, 9), toggle=True, icon='icons/target3+',hPolicy='fixed')
    self.pickOnSpectrumButton.setChecked(False)
    self.pickOnSpectrumButton.toggled.connect(self.togglePicking)
    # self.mySignal1.connect(self.setSpinBoxSelected)
    self.currentBox = None
    self.linePoints = []


    self.updateLayout(self.orderBox.value())



  def updateLayout(self, value=None):
    if value < 6:
      for j in range(self.layout().rowCount()):
        for k in range(3, self.layout().columnCount()-1):
          item = self.layout().itemAtPosition(j, k)
          if item:
            if item.widget():
              item.widget().hide()
            self.layout().removeItem(item)
      self.controlPointBoxList = []
      self.controlPointBox1 = DoubleSpinbox(self, grid=(0, 3), showButtons=False,
                                            max=self.controlPointMaximum, min=self.controlPointMinimum)
      self.controlPointBox1.setSingleStep(self.controlPointStepSize)
      self.controlPointBoxList.append(self.controlPointBox1)
      self.ppmLabel = Label(self, 'ppm', grid=(0, 4))
      self.controlPointBox2 = DoubleSpinbox(self, grid=(0, 5), showButtons=False,
                                            max=self.controlPointMaximum, min=self.controlPointMinimum)
      self.controlPointBox2.setSingleStep(self.controlPointStepSize)
      self.controlPointBoxList.append(self.controlPointBox2)
      self.ppmLabel = Label(self, 'ppm', grid=(0, 6))
      self.controlPointBox3 = DoubleSpinbox(self, grid=(0, 7), showButtons=False,
                                            max=self.controlPointMaximum, min=self.controlPointMinimum)
      self.controlPointBox3.setSingleStep(self.controlPointStepSize)
      self.controlPointBoxList.append(self.controlPointBox3)
      self.ppmLabel = Label(self, 'ppm', grid=(0, 8))
      if 2 < value <= 5:
        gridArray = [3+x for x in range(2*(value-2))]
        for i in range(0, len(gridArray), 2):
          self.controlPointBox = DoubleSpinbox(self, grid=(1, gridArray[i]), showButtons=False,
                                               max=self.controlPointMaximum, min=self.controlPointMinimum)
          self.controlPointBox.setSingleStep(self.controlPointStepSize)
          self.controlPointBoxList.append(self.controlPointBox)
          self.ppmLabel = Label(self, 'ppm', grid=(1, gridArray[i+1]))
    else:
      pass


  def setValueInValueList(self):
    self.valueList = [controlPointBox.value() for controlPointBox in self.controlPointBoxList]


  def togglePicking(self):
    if self.pickOnSpectrumButton.isChecked():
      self.turnOnPositionPicking()
    elif not self.pickOnSpectrumButton.isChecked():
      self.turnOffPositionPicking()

  def turnOnPositionPicking(self):
    print('picking on')
    self.current.registerNotify(self.setPositions, 'positions')

  def turnOffPositionPicking(self):
    print('picking off')
    self.current.unRegisterNotify(self.setPositions, 'positions')

  def setPositions(self, positions):
    if len(self.linePoints) < len(self.controlPointBoxList):
      line = pg.InfiniteLine(angle=90, pos=self.current.positions[0], movable=True, pen=(0, 0, 100))
      line.sigPositionChanged.connect(self.lineMoved)
      self.current.strip.plotWidget.addItem(line)
      self.linePoints.append(line)
      for i, line in enumerate(self.linePoints):
        self.controlPointBoxList[i].setValue(line.pos().x())
    else:
      print('No more lines can be added')


  def lineMoved(self, line):
    lineIndex = self.linePoints.index(line)
    self.controlPointBoxList[lineIndex].setValue(line.pos().x())


  def getParams(self):
    return {'function': 'polyBaseLine',
            'controlPoints': [x.value() for x in self.controlPointBoxList]}


class NormaliseSpectra(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.project = project
    self.label = Label(self, 'Method ', grid=(0, 0))
    if spectra is None:
      spectra = [spectrum.pid for spectrum in project.spectra]
    self.lenSpectra = len(spectra)
    self.methodPulldownList = PulldownList(self, grid=(0, 1))
    methods = ['Reference Peak',
               'Total Area',
               'PQN']
    self.methodPulldownList.setData(methods)

  def getParams(self):
    return {'function': 'normalise',
            'method': self.methodPulldownList.currentText()}

class AlignToReference(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.windowBoxes = []
    self.current = project._appBase.current
    self.pickOnSpectrumButton = Button(self, grid=(0, 0), toggle=True, icon='icons/target3+',hPolicy='fixed')
    self.pickOnSpectrumButton.setChecked(False)
    self.pickOnSpectrumButton.toggled.connect(self.togglePicking)
    self.region1 = DoubleSpinbox(self, grid=(0, 1))
    self.region2 = DoubleSpinbox(self, grid=(0, 2))
    self.regionBoxes = [self.region1, self.region2]
    self.linePoints = []
    self.lr = None
    self.referenceLabel = Label(self, "Reference", grid=(0, 3))
    self.referencePulldown = PulldownList(self, grid=(0, 4))
    self.referenceBox = DoubleSpinbox(self, grid=(0, 5))


  def togglePicking(self):
    if self.pickOnSpectrumButton.isChecked():
      self.turnOnPositionPicking()
    elif not self.pickOnSpectrumButton.isChecked():
      self.turnOffPositionPicking()

  def turnOnPositionPicking(self):
    print('picking on')
    self.current.registerNotify(self.setPositions, 'positions')
    if self.lr:
      self.current.strip.plotWidget.addItem(self.lr)

  def turnOffPositionPicking(self):
    print('picking off')
    self.current.unRegisterNotify(self.setPositions, 'positions')
    self.current.strip.plotWidget.removeItem(self.lr)


  def setPositions(self, positions):
    if len(self.linePoints) < 2:
      line = pg.InfiniteLine(angle=90, pos=self.current.positions[0], movable=True, pen=(0, 0, 100))
      self.current.strip.plotWidget.addItem(line)
      self.linePoints.append(line)
      for i, line in enumerate(self.linePoints):
        self.regionBoxes[i].setValue(line.pos().x())
    if len(self.linePoints) == 2:
      for linePoint in self.linePoints:
        self.current.strip.plotWidget.removeItem(linePoint)
      if not self.lr:
        self.lr = pg.LinearRegionItem(values=[self.linePoints[0].pos().x(), self.linePoints[1].pos().x()])

        self.current.strip.plotWidget.addItem(self.lr)
        self.lr.sigRegionChanged.connect(self.updateRegion)

  def updateRegion(self):
    region = self.lr.getRegion()
    self.regionBoxes[0].setValue(region[1])
    self.regionBoxes[1].setValue(region[0])

  def getParams(self):
    return {'function': 'alignToReference',
            'window': (self.region1.value(), self.region2.value()),
            'referencePpm': self.referenceBox.value()}



class AlignSpectra(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    spectrumLabel = Label(self, 'Spectrum', grid=(0, 0))
    self.spectrumPulldown = PulldownList(self, grid=(0, ))
    spectra = [spectrum.pid for spectrum in project.spectra]
    spectra.insert(0, '<All>')
    self.spectrumPulldown.setData(spectra)

  def getParams(self):
    return {'function': 'alignSpectra',
            'target': self.spectrumPulldown.currentText()
            }

class WhittakerBaseline(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.linePoints = []
    self.points = []
    self.current = project._appBase.current
    self.pickOnSpectrumButton =  Button(self, grid=(0, 0), toggle=True, icon='icons/target3+',hPolicy='fixed')
    self.pickOnSpectrumButton.setChecked(False)
    self.pickOnSpectrumButton.toggled.connect(self.togglePicking)
    self.checkBoxLabel = Label(self, 'Auto', grid=(0, 1))
    self.checkBox = CheckBox(self, grid=(0, 2))
    self.checkBox.setChecked(False)
    self.aLabel = Label(self, 'a ', grid=(0, 3))
    self.aBox = DoubleSpinbox(self, grid=(0, 4))
    self.lamLabel = Label(self, 'lam ', grid=(0, 5))
    self.lamBox = DoubleSpinbox(self, grid=(0, 6))


  def togglePicking(self):
    if self.pickOnSpectrumButton.isChecked():
      self.turnOnPositionPicking()
    elif not self.pickOnSpectrumButton.isChecked():
      self.turnOffPositionPicking()

  def turnOnPositionPicking(self):
    print('picking on')
    self.current.registerNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.addItem(linePoint)

  def turnOffPositionPicking(self):
    print('picking off')
    self.current.unRegisterNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.removeItem(linePoint)

  def setPositions(self, positions):
    line = pg.InfiniteLine(angle=90, pos=self.current.positions[0], movable=True, pen=(0, 0, 100))
    self.current.strip.plotWidget.addItem(line)
    self.linePoints.append(line)
    self.points.append(line.pos().x())

  def getParams(self):
    return {'function': 'whittakerBaseline',
            'controlPoints': self.points,
            'a': self.aBox.value(),
            'lam': self.lamBox.value()
            }

class SegmentalAlign(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.linePoints = []
    # self.points = []
    self.current = project._appBase.current
    self.pickOnSpectrumButton =  Button(self, grid=(0, 0), toggle=True, icon='icons/target3+',hPolicy='fixed')
    self.pickOnSpectrumButton.setChecked(False)
    self.pickOnSpectrumButton.toggled.connect(self.togglePicking)


  def togglePicking(self):
    if self.pickOnSpectrumButton.isChecked():
      self.turnOnPositionPicking()
    elif not self.pickOnSpectrumButton.isChecked():
      self.turnOffPositionPicking()

  def turnOnPositionPicking(self):
    print('picking on')
    self.current.registerNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.addItem(linePoint)

  def turnOffPositionPicking(self):
    print('picking off')
    self.current.unRegisterNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.removeItem(linePoint)

  def setPositions(self, positions):
    line = pg.InfiniteLine(angle=90, pos=self.current.positions[0], movable=True, pen=(0, 0, 100))
    # line.sigPositionChanged.connect(self.lineMoved)
    self.current.strip.plotWidget.addItem(line)
    self.linePoints.append(line)
    # self.points.append(line.pos().x())

  def getParams(self):
    self.points = [line.pos().x() for line in self.linePoints]
    return {'function': 'segmentalAlign',
            'regions': [self.points[i:i+1] for i in range(0, len(self.points), 1)]}


class ExcludeBaselinePoints(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.pointLabel = Label(self, 'Exclusion Points ', grid=(0, 0))
    self.pointBox1 = Spinbox(self, grid=(0, 1), max=100000000000, min=-100000000000)
    self.pointBox2 = Spinbox(self, grid=(0, 2), max=100000000000, min=-100000000000)
    self.current = project._appBase.current
    self.pickOnSpectrumButton = Button(self, grid=(0, 3), toggle=True, icon='icons/target3+',hPolicy='fixed')
    self.pickOnSpectrumButton.setChecked(False)
    self.multiplierLabel = Label(self, 'Baseline Multipler', grid=(0, 4))
    self.multiplierBox = DoubleSpinbox(self, grid=(0, 5))
    self.pickOnSpectrumButton.toggled.connect(self.togglePicking)
    self.linePoint1 = pg.InfiniteLine(angle=0, pos=self.pointBox1.value(), movable=True, pen=(255, 0, 100))
    self.linePoint2 = pg.InfiniteLine(angle=0, pos=self.pointBox2.value(), movable=True, pen=(255, 0, 100))
    if self.current.strip is not None:
      self.current.strip.plotWidget.addItem(self.linePoint1)
      self.current.strip.plotWidget.addItem(self.linePoint2)
    self.pointBox1.setValue(self.linePoint1.pos().y())
    self.pointBox2.setValue(self.linePoint2.pos().y())
    self.linePoint1.hide()
    self.linePoint1.sigPositionChanged.connect(partial(self.lineMoved, self.pointBox1, self.linePoint1))
    self.linePoint2.hide()
    self.linePoint2.sigPositionChanged.connect(partial(self.lineMoved, self.pointBox2, self.linePoint2))
    self.pointBox1.valueChanged.connect(partial(self.setLinePosition, self.linePoint1, self.pointBox1))
    self.pointBox2.valueChanged.connect(partial(self.setLinePosition, self.linePoint2, self.pointBox2))


  def togglePicking(self):
    if self.pickOnSpectrumButton.isChecked():
      self.turnOnPositionPicking()
    elif not self.pickOnSpectrumButton.isChecked():
      self.turnOffPositionPicking()

  def turnOnPositionPicking(self):
    print('picking on')
    self.linePoint1.show()
    self.linePoint2.show()

  def turnOffPositionPicking(self):
    print('picking off')
    self.linePoint1.hide()
    self.linePoint2.hide()

  def lineMoved(self, box, linePoint):
    box.setValue(linePoint.pos().y())

  def setLinePosition(self, linePoint, pointBox):
    linePoint.setPos(pointBox.value())

  def getParams(self):
    return {'function': 'excludeBaselinePoints',
            'baselineRegion': [self.pointBox1.value(), self.pointBox2.value()],
            'baselineMultiplier': self.multiplierBox.value()}


class AlignSpectra(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.targetLabel = Label(self, 'Target Spectrum ', grid=(0, 0))
    self.targetPulldown = PulldownList(self, grid=(0, 1))
    spectra = [spectrum.pid for spectrum in project.spectra]
    spectra.insert(0, '<All>')
    self.targetPulldown.setData(spectra)

  def getParams(self):
    return {'function': 'alignSpectra',
            'targetSpectrum': self.targetPulldown.currentText()}



class Bin(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.binWidthLabel = Label(self, 'Bin Width (ppm) ', grid=(0, 0))
    self.binWidth = DoubleSpinbox(self, grid=(0, 1))

  def getParams(self):
    return {'function':'bin',
            'binWidth': self.binWidth.value()}

class Centre(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.methodLabel = Label(self, 'Method ', grid=(0, 0), hAlign='r')
    self.methodPulldown = PulldownList(self, grid=(0, 1))
    methods = ['Mean', 'Median']
    self.methodPulldown.setData(methods)

  def getParams(self):
    return {'function': 'centre',
            'method': self.methodPulldown.currentText()}

class Scale(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.methodLabel = Label(self, 'Method ', grid=(0, 0), hAlign='r')
    self.methodPulldown = PulldownList(self, grid=(0, 1))
    methods = ['Unit Variance', 'Pareto']
    self.methodPulldown.setData(methods)

  def getParams(self):
    return {'function':'scale',
            'method': self.methodPulldown.currentText()}

class ExcludeSignalFreeRegions(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.lamLabel = Label(self, 'lam ', grid=(0, 0))
    self.lamBox = DoubleSpinbox(self, grid=(0, 1))

  def getParams(self):
    return {'function': 'excludeSignalFreeRegions',
      'lam': self.lamBox.value()}

class WhittakerSmooth(QtGui.QWidget, Base):
  def __init__(self, parent, project, spectra=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)
    self.linePoints = []
    self.points = []
    self.current = project._appBase.current
    self.pickOnSpectrumButton = Button(self, grid=(0, 0), toggle=True, icon='icons/target3+',hPolicy='fixed')
    self.pickOnSpectrumButton.setChecked(False)
    self.pickOnSpectrumButton.toggled.connect(self.togglePicking)
    self.checkBoxLabel = Label(self, 'Auto', grid=(0, 1))
    self.checkBox = CheckBox(self, grid=(0, 2))
    self.checkBox.setChecked(False)
    self.aLabel = Label(self, 'a ', grid=(0, 3))
    self.aBox = DoubleSpinbox(self, grid=(0, 4))


  def togglePicking(self):
    if self.pickOnSpectrumButton.isChecked():
      self.turnOnPositionPicking()
    elif not self.pickOnSpectrumButton.isChecked():
      self.turnOffPositionPicking()

  def turnOnPositionPicking(self):
    print('picking on')
    self.current.registerNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.addItem(linePoint)

  def turnOffPositionPicking(self):
    print('picking off')
    self.current.unRegisterNotify(self.setPositions, 'positions')
    for linePoint in self.linePoints:
      self.current.strip.plotWidget.removeItem(linePoint)

  def setPositions(self, positions):
    line = pg.InfiniteLine(angle=90, pos=self.current.positions[0], movable=True, pen=(0, 0, 100))
    self.current.strip.plotWidget.addItem(line)
    self.linePoints.append(line)
    self.points.append(line.pos().x())

  def getParams(self):
    return { 'function': 'whittakerSmooth',
      'a': self.aBox.value(),
            'controlPoints': self.points}
