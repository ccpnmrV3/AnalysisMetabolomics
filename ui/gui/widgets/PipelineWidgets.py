
from PyQt4 import QtCore, QtGui
from pyqtgraph.dockarea.DockArea import DockArea
from pyqtgraph.dockarea.DockDrop import DockDrop
from pyqtgraph.dockarea.Dock import DockLabel, Dock, VerticalLabel
from pyqtgraph.dockarea.Container import SplitContainer
from ccpn.ui.gui.widgets.Module import CcpnModule
from ccpn.framework.lib.Pipe import Pipe



PipelineBoxDragStyle = """Dock > QWidget {border: 1px solid #78FF00; border-radius: 1px;}"""

PipelineBoxLabelStyle = """PipelineBoxLabel{
                                                  background-color : #60B41D;
                                                  color : #000000;
                                                  border-top-right-radius: 1r;
                                                  border-top-left-radius: 1r;
                                                  border-bottom-right-radius: 0px;
                                                  border-bottom-left-radius: 0px;
                                                  border-width: 0px;
                                                  border-bottom: 0px;
                                                  padding-left: 1px;
                                                  padding-right: 1px;
                                                  }"""


class VContainer(SplitContainer):

  def __init__(self, area):
    SplitContainer.__init__(self, area, QtCore.Qt.Vertical)


  def type(self):
    return 'vertical'


  def updateStretch(self):
    ##Set the stretch values for this container to reflect its contents
    #print "updateStretch", self
    x = 0
    y = 0
    sizes = []
    for i in range(self.count()):
        wx, wy = self.widget(i).stretch()
        y += wy
        x = max(x, wx)
        sizes.append(wy)
        #print "  child", self.widget(i), wx, wy
    self.setStretch(x, y)

    #print sizes
    tot = float(sum(sizes))
    if tot == 0:
        scale = 1.0
    else:
        scale = self.height() / tot

    self.setSizes([int(s*scale) for s in sizes])

    self.setCollapsible(0, False)
    self.setCollapsible(1, False)



class PipelineDropAreaOverlay(QtGui.QWidget):
  """Overlay widget that draws drop areas during a drag-drop operation"""

  def __init__(self, parent):
    QtGui.QWidget.__init__(self, parent)
    self.dropArea = None
    self.hide()
    self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)


  def setDropArea(self, area):
    self.dropArea = area
    if area is None:
      self.hide()
    else:
      # self.hide()
      ## Resize overlay to just the region where drop area should be displayed.
      ## This works around a Qt bug--can't display transparent widgets over QGLWidget
      prgn = self.parent().rect()
      rgn = QtCore.QRect(prgn)
      w = min(10, prgn.width() / 3.)
      h = min(10, prgn.height() / 3.)

      if self.dropArea == 'top':
        rgn.setHeight(h)
      elif self.dropArea == 'bottom':
        rgn.setTop(rgn.top() + prgn.height() - h)
      else:
        rgn.setHeight(0)

      self.setGeometry(rgn)
      self.show()

    self.update()
    self.update()


  def paintEvent(self, ev):
    if self.dropArea is None:
      return
    p = QtGui.QPainter(self)
    rgn = self.rect()

    p.setBrush(QtGui.QBrush(QtGui.QColor(120, 255, 0, 50)))
    p.setPen(QtGui.QPen(QtGui.QColor(123, 245, 150), 3))
    p.drawRect(rgn)



class PipelineDropArea(DockArea):
  def __init__(self, **kw):
    super(PipelineDropArea, self).__init__(self)
    self.setStyleSheet("""QSplitter{background-color: transparent;}
                          QSplitter::handle:vertical {background-color: transparent;height: 1px;}""")

  def dragEnterEvent(self, ev):
    src = ev.source()
    ev.ignore()


  def addPipe(self, pipe:Pipe, position='bottom'):
    self.addDock(pipe.widget, position=position)


  def addBox(self, box=None, position='bottom', relativeTo=None, **kwds):
    """With these settings the user can close all the boxes from the label 'close box' or pop up and
     when re-add a new box it makes sure there is a container available.
    """

    if box is None:
      box = PipelineBox(name='New PipelineBox', **kwds)

    if position is None:
      position = 'bottom'
    neededContainer = {'bottom': 'vertical','top': 'vertical',}[position]

    if relativeTo is None:
      neighbor = None
      container = self.addContainer(neededContainer, self.topContainer)

    if relativeTo is None or relativeTo is self:
      if self.topContainer is None:
        container = self
        neighbor = None
      else:
        container = self.topContainer
        neighbor = None
    else:
      if isinstance(relativeTo, str):
        relativeTo = self.boxes[relativeTo]
      container = self.getContainer(relativeTo)
      neighbor = relativeTo

    if neededContainer != container.type() and container.type() == 'tab':
      neighbor = container
      container = container.container()

    if neededContainer != container.type():
      if neighbor is None:
        container = self.addContainer(neededContainer, self.topContainer)
      else:
        container = self.addContainer(neededContainer, neighbor)

    insertPos = { 'bottom': 'after','top': 'before',}[position]

    if container is not None:
      container.insert(box, insertPos, neighbor)
    else:
      container = self.topContainer
      container.insert(box, insertPos, neighbor)
    box.area = self
    self.docks[box.name()] = box
    return box


  def makeContainer(self, typ):
    new = VContainer(self)
    new.setCollapsible(1,False)
    return new


  def apoptose(self):
    pass


  def orderedBoxes(self, obj):
    if isinstance(obj, Dock):
      return (obj)
    else:
      boxes = []
      for i in range(obj.count()):
        boxes.append(self.orderedBoxes(obj.widget(i)))
      return boxes



class PipelineBox(Dock, DockDrop):

  def __init__(self, pipe:Pipe, **kw):
    self.pipe = pipe
    super(PipelineBox, self).__init__(self.pipe.METHODNAME, self)
    self.ccpnModule = False
    self.pipelineBox = True
    self.autoOrient = False
    self._updateLabel(self.pipe.METHODNAME)
    self.dragStyle = PipelineBoxDragStyle
    self.overlay = PipelineDropAreaOverlay(self)
    self._setMainLayout()

  def _setMainLayout(self):
    self.mainFrame = QtGui.QFrame()
    self.mainLayout = QtGui.QGridLayout()
    self.mainFrame.setLayout(self.mainLayout)
    self.layout.addWidget(self.mainFrame, 0, 0, 0, 0)


  def implements(self, name=None):
    if name is None:
      return ['PipelineBox']
    else:
      return name == 'PipelineBox'


  def _updateLabel(self, name):
    self.label.deleteLater()  # delete original Label
    self.label = PipelineBoxLabel(name.upper(), self)
    self.label.closeButton.clicked.connect(self.closeBox)
    # self.label.arrowDownButton.clicked.connect(self.moveBoxDown)
    # self.label.arrowUpButton.clicked.connect(self.moveBoxUp)
    self.moveLabel = True
    self.orientation = 'horizontal'


  def closeBox(self):
      self.setParent(None)
      self.label.setParent(None)


  def name(self):
    return self.label.name


  def rename(self, newName):
    self.label.name = newName


  def moveBoxDown(self):
    name = self.name()
    boxes = self.pipelineArea.childState(self.pipelineArea.topContainer)[1]
    boxesNames = []
    for i, box in enumerate(boxes):
      boxesNames.append(box[1])
    i= boxesNames.index(name)
    count = len(boxes)
    j = i
    while j < count-1:
      next = self.pipelineArea.docks[str(boxesNames[i + 1])]
      self.pipelineArea.moveDock(self, 'bottom', next)
      j+=1


  def moveBoxUp(self):
    name = self.name()
    boxes = self.pipelineArea.childState(self.pipelineArea.topContainer)[1]
    boxesNames = []
    for i, box in enumerate(boxes):
      boxesNames.append(box[1])
    i = boxesNames.index(name)
    j = i
    while j > 0:
      next = self.pipelineArea.docks[str(boxesNames[i - 1])]
      self.pipelineArea.moveDock(self, 'top', next)
      j = j - 1


  def startDrag(self):
    # if len(self.pipelineArea.findAll()[1].keys()) > 1:
      self.drag = QtGui.QDrag(self)
      mime = QtCore.QMimeData()
      self.drag.setMimeData(mime)
      self.widgetArea.setStyleSheet(self.dragStyle)
      self.update()
      action = self.drag.exec_()
      self.updateStyle()


  def dragEnterEvent(self, ev):
    src = ev.source()
    if hasattr(src, 'implements') and src.implements('PipelineBox'):
      ev.accept()
    else:
      ev.ignore()


  def dragMoveEvent(self, *args):
    DockDrop.dragMoveEvent(self, *args)


  def dragLeaveEvent(self, *args):
    DockDrop.dragLeaveEvent(self, *args)


  def dropEvent(self, *args):
    DockDrop.dropEvent(self, *args)


  def setActive(self, state):
    self.label.checkBox.setChecked(state)


  def isActive(self):
    checkBox = self.label.checkBox
    if checkBox.isChecked():
      return True
    else:
      return False



class PipelineBoxLabel(DockLabel, VerticalLabel):
  def __init__(self, name,  *args):
    super(PipelineBoxLabel, self).__init__(name, showCloseButton=True, *args)
    QtGui.QLabel.__init__(self)
    self.updateStyle()
    self.setExtraButtons()
    self.name = name


  def updateStyle(self):
    self.hStyle =  PipelineBoxLabelStyle
    self.setStyleSheet(self.hStyle)


  def setExtraButtons(self):
    # self.lineEdit = QtGui.QLineEdit(self)
    # self.lineEdit.setMaximumHeight(15)
    # self.lineEdit.setMinimumWidth(50)
    # self.lineEdit.setStyleSheet("""QLineEdit {background-color: white; color:black;}""")
    # self.lineEdit.hide()
    self.checkBox = QtGui.QCheckBox(self)
    self.checkBox.setMaximumHeight(15)
    self.checkBox.setStyleSheet("""QCheckBox {background-color: transparent;}""")


    self.activeLabel = QtGui.QPushButton(self)
    self.activeLabel.setText('Active')
    self.activeLabel.setStyleSheet("""QPushButton {background-color: transparent;
                                                  color:black;
                                                  border: 0px solid transparent}""")

    self.closeButton = QtGui.QPushButton(self)
    self.closeButton.setStyleSheet("""QPushButton {background-color: transparent;
                                                  color:black;
                                                  border: 0px solid transparent}}""")
    self.closeButton.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_TitleBarCloseButton))
    self.closeButton.setMaximumHeight(15)
    self.activeLabel.clicked.connect(self.checkActiveBox)


  def checkActiveBox(self):
    if self.checkBox.isChecked():
      self.checkBox.setChecked(False)
    else:
      self.checkBox.setChecked(True)


  def mousePressEvent(self, ev):

    if ev.button() == QtCore.Qt.LeftButton:
      self.pressPos = ev.pos()
      self.startedDrag = False
      ev.accept()


  def mouseDoubleClickEvent(self, ev):
    if ev.button() == QtCore.Qt.LeftButton:
      pass


  def resizeEvent(self, ev):
    size = ev.size().height()

    pos = QtCore.QPoint(ev.size().width() -60, 0)
    self.activeLabel.move(pos)
    # self.lineEdit.move(pos)

    pos = QtCore.QPoint(ev.size().width() - 80, 0)
    self.checkBox.move(pos)

    pos = QtCore.QPoint(ev.size().width() - 20, 0)
    self.closeButton.move(pos)

    super(DockLabel, self).resizeEvent(ev)


  def mouseMoveEvent(self, ev):
    if not self.startedDrag and (ev.pos()).manhattanLength() > QtGui.QApplication.startDragDistance():
      self.dock.startDrag()
    ev.accept()


  def paintEvent(self, ev):
    p = QtGui.QPainter(self)
    rgn = self.contentsRect()
    align = self.alignment()
    self.hint = p.drawText(rgn, align, self.name)
    p.end()

    self.setMaximumHeight(self.hint.height())
    self.setMinimumHeight(15)
    self.setMaximumWidth(16777215)
