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
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: rhfogh $"
__date__ = "$Date: 2017-04-07 10:28:45 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets

from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.widgets.Base import Base
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.ListWidget import ListWidget
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Widget import Widget


class PcaWidget(CcpnModule):
  def __init__(self, presenter, mainWindow, **kwargs):
    CcpnModule.__init__(self,mainWindow=mainWindow, name='PCA')
    self.presenter = presenter
    self.mainWindow = mainWindow
    self.settings = PcaSettings(self, presenter=self.presenter)
    self.pcaPlotLeft = PcaPlot(self, presenter=self.presenter)
    self.pcaPlotRight = PcaPlot(self, presenter=self.presenter)
    self.pcaOutput = PcaOutput(self, presenter=self.presenter)

    self.layout.addWidget(self.settings, 0, 0, 1, 2)
    self.layout.addWidget(self.pcaPlotLeft, 1, 0, 2, 1)
    self.layout.addWidget(self.pcaPlotRight, 1, 1, 2, 1)
    self.layout.addWidget(self.pcaOutput, 3, 0, 1, 2)


class PcaSettings(Widget):
  def __init__(self, parent=None, presenter=None, **kwds):
    super().__init__(parent, **kwds)
    self.presenter = presenter

    self.setLayout(QtWidgets.QHBoxLayout())
    column1Layout = QtWidgets.QVBoxLayout()
    self.layout().addLayout(column1Layout)

    column1Layout.addWidget(Label(self, 'Method:'))
    self.decompMethodPulldown = PulldownList(self, callback=presenter.setMethod)
    column1Layout.addWidget(self.decompMethodPulldown)
    # self.goButton = Button(self, 'GO!', hPolicy='fixed', callback=presenter.go)
    # column1Layout.addWidget(self.goButton)
    column1Layout.addStretch()

    column2Layout = QtWidgets.QGridLayout()
    self.layout().addLayout(column2Layout)
    column2Layout.addWidget(Label(self, '1. Normalization:'), 0, 0, 1, 1)
    self.normMethodPulldown = PulldownList(self, callback=presenter.setNormalization)
    column2Layout.addWidget(self.normMethodPulldown, 0, 1, 1, 1)

    column2Layout.addWidget(Label(self, '2. Centering:'), 1, 0, 1, 1)
    self.centMethodPulldown = PulldownList(self, callback=presenter.setCentering)
    column2Layout.addWidget(self.centMethodPulldown, 1, 1, 1, 1)

    column2Layout.addWidget(Label(self, '3. Scaling:'), 2, 0, 1, 1)
    self.scalingMethodPulldown = PulldownList(self, callback=presenter.setScaling)
    column2Layout.addWidget(self.scalingMethodPulldown, 2, 1, 1, 1)

    spectrumGroupsLabel = Label(self, 'SpectrumGroups:')
    self.layout().addWidget(spectrumGroupsLabel)

    self.spectrumGroupsList = ListWidget(self, callback=self._filterBySpectrumGroups)
    self.spectrumGroupsList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    self.spectrumGroupsList.clearSelection = self._clearSpectrumGroupSelection
    self.spectrumGroupsList.setSelectContextMenu()
    self.layout().addWidget(self.spectrumGroupsList)

    spectraLabel = Label(self, 'Spectra Source:')
    self.layout().addWidget(spectraLabel)
    self.sourceList = ListWidget(self, callback=presenter.setSourcesSelection)
    self.sourceList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    self.sourceList.setSelectContextMenu()

    self.layout().addWidget(self.sourceList)

    self.setMaximumHeight(100)

  def _clearSelection(self, listWidget):
    for i in range(listWidget.count()):
      item = listWidget.item(i)
      item.setSelected(False)

  def _clearSpectrumGroupSelection(self):
    print('This function has not been implemented yet.')
    # self._clearSelection(self.spectrumGroupsList)
    # self.sourceList.clear()
    # self.presenter.setSourcesSelection(None)


  def _filterBySpectrumGroups(self, rowClicked):
    sGroups = self.spectrumGroupsList.getSelectedObjects()

    # self.sourceList.hideAllItems()
    self.sourceList.clearSelection()
    self.presenter.setSourcesSelection(None)
    spectra = [sp for sg in sGroups for sp in sg.spectra]
    self.sourceList.showItems([spectrum.name for spectrum in spectra], select=True)

    self.presenter.setSourcesSelection(None)



class PcaPlot(QtWidgets.QWidget):
  def __init__(self, parent=None, presenter=None, **kwargs):
    QtWidgets.QWidget.__init__(self, parent)
    self.setLayout(QtWidgets.QVBoxLayout())
    self.presenter = presenter

    self.plottingWidget = pg.PlotWidget(self)
    self.plotItem = self.plottingWidget.getPlotItem()
    self.plotItem.getAxis('left').setWidth(36)
    self.plotItem.getAxis('bottom').setHeight(24)

    self.layout().addWidget(self.plottingWidget)
    selectorLayout = QtWidgets.QHBoxLayout()

    selectorLayout.addWidget(Label(self, 'x:'))
    self.xAxisSelector = PulldownList(self, callback=self.plot)
    selectorLayout.addWidget(self.xAxisSelector)
    selectorLayout.addWidget(Label(self, 'y:'))
    self.yAxisSelector = PulldownList(self, callback=self.plot)
    selectorLayout.addWidget(self.yAxisSelector)
    selectorLayout.addStretch()

    self.layout().addLayout(selectorLayout)


  def plot(self, *args):

    self.presenter.plot(self, self.xAxisSelector.currentData()[0],
                        self.yAxisSelector.currentData()[0])

  def addXOriginLine(self):
    self.plotItem.addItem(pg.InfiniteLine(angle=0, pos=0,
                          pen=pg.functions.mkPen('w', width=1, style=QtCore.Qt.DashLine)))

  def addYOriginLine(self):
    self.plotItem.addItem(pg.InfiniteLine(angle=90, pos=0,
                          pen=pg.functions.mkPen('w', width=1, style=QtCore.Qt.DashLine)))


class PcaOutput(Widget):
  def __init__(self, parent=None, presenter=None, **kwds):
    super().__init__(parent, **kwds)
    self.presenter = presenter

    self.setLayout(QtWidgets.QHBoxLayout())

    self.sgNameEntryBox = LineEdit(self, text='pca_001')
    self.descaleCheck = CheckBox(self, checked=True, text='Descale Components')
    self.saveButton = Button(self, 'save', callback=self.presenter.saveOutput)

    self.getLayout().addWidget(Label(self, 'Output spectrum group:'))
    self.getLayout().addWidget(self.sgNameEntryBox)
    self.getLayout().addWidget(self.descaleCheck)
    self.getLayout().addStretch()
    self.getLayout().addWidget(self.saveButton)
    self.setMaximumHeight(45)

