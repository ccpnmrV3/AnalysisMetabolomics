"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan"
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification
#=========================================================================================
__author__ = ": rhfogh $"
__date__ = ": 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__version__ = ": 7686 $"

__modifiedBy__ = "$modifiedBy: Ed Brooksbank $"
__dateModified__ = "$dateModified: 2017-04-07 11:41:23 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:45 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================


"""Module Documentation here

"""
#=========================================================================================
#=========================================================================================

#=========================================================================================
#=========================================================================================
__author__ = ": rhfogh $"
__date__ = ": 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__version__ = ": 7686 $"

#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtGui

from ccpn.ui.gui.modules.PeakTable import PeakListSimple
from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Table import ObjectTable, Column


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
