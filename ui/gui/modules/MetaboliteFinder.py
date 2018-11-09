#=========================================================================================
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
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: CCPN $"
__date__ = "$Date: 2017-04-07 10:28:42 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtCore, QtGui, QtWidgets
from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.CompoundView import CompoundView
from ccpn.ui.gui.widgets.TextEditor import TextEditor
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.LinearRegionsPlot import LinearRegionsPlot
from ccpn.ui.gui.widgets.ListWidget import ListWidget
from ccpn.ui.gui.modules.PeakTable import PeakListTableWidget
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.FileDialog import FileDialog
from ccpn.ui.gui.widgets.Spacer import Spacer
from functools import partial
from ccpn.AnalysisMetabolomics.lib.BMRBquery import peaksToShifts1D, bmrbMultiShiftSearch
import pandas as pd
from ccpn.core.SpectrumHit import SpectrumHitPeakList
from ccpn.core.lib.Notifiers import Notifier
from ccpn.ui.gui.widgets.QuickTable import QuickTable

Qt = QtCore.Qt
Qkeys = QtGui.QKeySequence



class MetaboliteFinderModule(CcpnModule):

  includeSettingsWidget = False
  maxSettingsState = 2
  settingsPosition = 'top'
  className = 'MetaboliteFinderModule'

  def __init__(self, mainWindow, name='BMRB Metabolite Finder', **kwds):
    super(MetaboliteFinderModule, self)
    CcpnModule.__init__(self, mainWindow=mainWindow, name=name)
    self.application = None
    self.project = None
    self.current = None
    self.preferences = None

    if mainWindow is not None:
      self.mainWindow = mainWindow
      self.project = self.mainWindow.project
      self.application = self.mainWindow.application
      self.moduleArea = self.mainWindow.moduleArea
      self.preferences = self.application.preferences
      self.current = self.application.current

    self._createWidgets()

  def _createWidgets(self):
    """ Add all widgets to the layout """
    i = 0
    self.chemicalShiftLabel = Label(self.mainWidget,'Chemical Shifts', grid=(i, 0))
    i+=1
    self.chemicalShiftList = TextEditor(self.mainWidget,  grid=(i, 0))
    self.chemicalShiftList.setMaximumHeight(50)
    i += 1
    self.copyFromCurrentButton = Button(self.mainWidget, 'Copy from current Peak(s)', grid=(i, 0))
    i += 1
    self.searchButton = Button(self.mainWidget,'Search', callback=self._quearyBMRB, grid=(i, 0))
    i += 1
    self.metTable = QuickTable(self.mainWidget, mainWindow=self.mainWindow,
                               selectionCallback=None,
                               actionCallback=None,
                               grid=(i, 0))

  def _shiftsFromCurrentPeaks(self):
    if self.current:
      peaks = self.current.peaks
      shifts = peaksToShifts1D(peaks)
      self.chemicalShiftList.clear()
      text = ''
      for s in shifts:
        text += str(round(s,3)) + ','
      self.chemicalShiftList.setText(text)


  def _quearyBMRB(self):
    text = self.chemicalShiftList.get()
    lstStr = text.split(",")
    shifts = [float(i) for i in lstStr]
    df = bmrbMultiShiftSearch(shifts)
    print(df)
    self._setTable(df)


  def _setTable(self, dataframe):
    "Sets the table with a dataframe from bmrb website results."
    self.metTable.setData(dataframe)




if __name__ == '__main__':
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.widgets.CcpnModuleArea import CcpnModuleArea

  app = TestApplication()

  win = QtWidgets.QMainWindow()

  moduleArea = CcpnModuleArea(mainWindow=None, )
  module = MetaboliteFinderModule(mainWindow=None)
  ala = ['3.771', '1.471']
  data = {'col_1': [3, 2, 1, 0], 'col_2': ['a', 'b', 'c', 'd']}
  df = pd.DataFrame.from_dict(data)
  # module._setTable(df)
  moduleArea.addModule(module)

  win.setCentralWidget(moduleArea)
  win.resize(1000, 500)
  win.setWindowTitle('Testing %s' % module.moduleName)
  win.show()

  app.start()
