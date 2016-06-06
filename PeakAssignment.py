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
from ccpn.ui.gui.widgets.Table import ObjectTable, Column
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.RadioButton import RadioButton
from ccpn.ui.gui.widgets.Spinbox import Spinbox

from ccpn.ui.gui.modules.GuiTableGenerator import GuiTableGenerator
from ccpn.ui.gui.modules.PeakTable import PeakListSimple

import pyqtgraph as pg

class PeakAssignment(QtGui.QWidget, Base):

  def __init__(self, parent=None, project=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)

    self.peaksLabel = Label(self, 'Peaks', grid=(0, 0), gridSpan=(1, 3))
    self.assignLabel = Label(self, 'Fit', grid=(1, 4))
    self.assignButton = Button(self, '<--', grid=(2, 4))
    self.assignAndMoveButton = Button(self, '<-- + A', grid=(3, 4))
    self.deassignLabel = Label(self, 'Deassign', grid=(1, 5))
    self.deassignButton = Button(self, 'X', grid=(2, 5))
    self.deassignAndMoveButton = Button(self, 'X + P', grid=(3, 5))
    self.suggestionSourceLabel = Label(self, 'Suggestion Source ', grid=(0, 6), gridSpan=(1, 1))
    self.suggestionSourcePulldown = PulldownList(self, grid=(0, 7), gridSpan=(1, 2))
    self.peakTable = PeakListSimple(self, project, callback=self.callback,  grid=(1, 0), gridSpan=(4, 3))
    self.substanceTable = SubstanceTable(self, grid=(1, 6), gridSpan=(4, 3))

  def callback(self):
    pass


  def assignPeak(self):
    peakObject = self.peakTable.peakTable.getCurrentObject()
    substanceObject = self.substanceTable.substanceTable.getCurrentObject()
    peakObject.assignDimension(axisCode='H', value=[substanceObject.substance])

  def deassignPeak(self):
    peakObject = self.peakTable.peakTable.getCurrentObject()
    peakObject.dimensionNmrAtoms = [[]]

  def assignAndMove(self):
    self.assignPeak()
    if self.peakTable.peakTable.getCurrentRow() == 0:
      currentRow = 1
    else:
      currentRow = self.peakTable.peakTable.getCurrentRow()
    self.peakTable.peakTable.selectRow(currentRow)

  def deassignAndMove(self):
    self.deassignPeak()
    if self.peakTable.peakTable.getCurrentRow() == 0:
      currentRow = 1
    else:
      currentRow = self.peakTable.peakTable.getCurrentRow()
    self.peakTable.peakTable.selectRow(currentRow)


class SubstanceTable(QtGui.QWidget, Base):
  def __init__(self, parent=None, **kw):
    QtGui.QWidget.__init__(self, parent)
    Base.__init__(self, **kw)

    substanceTableColumns = [Column('substance', 'substance'), Column('atom', 'atom'), Column('cs', 'cs')]

    tipTexts2 = ['substance Id', 'substance atom', 'substance cs']
    substanceList = [Substance('1', '2', '3'), Substance('1', '2', '3'), Substance('1', '2', '3')]
    self.substanceLists = [substanceList]

    self.substanceTable = ObjectTable(self, columns=substanceTableColumns,
                              callback=self.substanceCallback,
                              objects=substanceList)

  def substanceCallback(self):
    pass

class Substance(object):
  def __init__(self, substance, atom, cs):
    self.substance = substance
    self.atom = atom
    self.cs = cs
