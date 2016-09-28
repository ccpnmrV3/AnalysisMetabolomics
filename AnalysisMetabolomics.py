__author__ = 'TJ'

from ccpn.framework.Framework import Framework


class Metabolomics(Framework):
  """Root class for Metabolomics application"""
  def __init__(self, applicationName, applicationVersion, commandLineArguments):
    Framework.__init__(self, applicationName, applicationVersion, commandLineArguments)


  def setupMenus( self ):
    super().setupMenus( )
    menuSpec = ('Metabolomics', [("Decomposition (PCA)", self.showDecompositionModule),
                                 # ("Pipeline", self.showScreeningPipeline,),
                                 ("Peak Fitting", self.showPeakFittingModule,),
                                 (),
                                 ("Pipeline", self.showMetabolomicsPipeline,),
                                 ])
    self.addApplicationMenuSpec(menuSpec)
  #   self._patchInIntegrals()
  #
  #
  # def _patchInIntegrals(self):
  #   spectrumMenuPos = [i[0] for i in self._menuSpec].index('Spectrum')
  #   self._menuSpec[spectrumMenuPos][1].insert(4,
  #                                             ("Integrate",
  #                                              self.showIntegrationModule,
  #                                              [('shortcut', 'in'), ('enabled', False)]
  #                                             ))
  #
  #   viewMenuPos = [i[0] for i in self._menuSpec].index('View')
  #   self._menuSpec[viewMenuPos][1].insert(5,
  #                                         ("Integral Table",
  #                                          self.showIntegralTable,
  #                                          [('shortcut', 'it'),('enabled', False)])
  #                                         )
  #
  # from ccpn.ui.gui.widgets.Module import CcpnModule
  # def showIntegrationModule(self, position:str='bottom', relativeTo:CcpnModule=None):
  #   spectrumDisplay = self.ui.mainWindow.createSpectrumDisplay(self.project.spectra[0])
  #   from ccpn.AnalysisMetabolomics.Integration import IntegrationTable, IntegrationWidget
  #   spectrumDisplay.integrationWidget = IntegrationWidget(spectrumDisplay.module,
  #                                                         project=self.project, grid=(2, 0), gridSpan=(1, 4))
  #   spectrumDisplay.integrationTable = IntegrationTable(spectrumDisplay.module,
  #                                                       project=self.project, grid=(0, 4), gridSpan=(3, 1))
  #   self.current.strip = spectrumDisplay.strips[0]
  #   if self.ui.mainWindow.blankDisplay:
  #     self.ui.mainWindow.blankDisplay.setParent(None)
  #     self.ui.mainWindow.blankDisplay = None
  #
  #
  # from ccpn.core.IntegralList import IntegralList
  # def showIntegralTable(self, position:str='bottom', relativeTo:CcpnModule=None, selectedList:IntegralList=None):
  #   logParametersString = "position={position}, relativeTo={relativeTo}, selectedList={selectedList}".format(
  #     position="'"+position+"'" if isinstance(position, str) else position,
  #     relativeTo="'"+relativeTo+"'" if isinstance(relativeTo, str) else relativeTo,
  #     selectedList="'" + selectedList + "'" if isinstance(selectedList, str) else selectedList,)
  #
  #   self._startCommandBlock('application.showIntegralTable({})'.format(logParametersString))
  #   try:
  #     self.ui.showIntegralTable(position=position, relativeTo=relativeTo, selectedList=selectedList)
  #   finally:
  #     self._endCommandBlock()


  def showMetabolomicsPipeline(self, position='bottom', relativeTo=None):
    from ccpn.AnalysisMetabolomics.ui.gui.modules.Pipeline import GuiPipeline
    pipelineMethods = None
    guiPipeline = GuiPipeline(application=self, pipelineMethods=pipelineMethods,
                              project=self.project, templates=None)
    mainWindow = self.ui.mainWindow
    mainWindow.moduleArea.addModule(guiPipeline, position='bottom')
    self.ui.mainWindow.pythonConsole.writeConsoleCommand("application.showMetabolomicsPipeline()")
    self.project._logger.info("application.showMetabolomicsPipeline()")


  def showDecompositionModule(self):
    from ccpn.AnalysisMetabolomics.Decomposition import Decomposition
    from ccpn.AnalysisMetabolomics.ui.gui.modules.DecompositionModule import DecompositionModule

    self.decomposition = Decomposition(application=self)
    self.ui.decompositionModule = DecompositionModule(application=self,
                                                      interactor=self.decomposition,
                                                      parent=self.ui)
    self.decomposition.presenter = self.ui.decompositionModule
    self.ui.mainWindow.moduleArea.addModule(self.ui.decompositionModule.widget, position='bottom')


  def showPipeline(self, position='bottom', relativeTo=None):
    from ccpn.ui.gui.modules.PipelineModule import GuiPipeline
    from ccpn.AnalysisScreen import guiPipeline as _gp
    guiPipeline = GuiPipeline(application=self, pipelineMethods=_gp.__all__, project=self.project)
    self.ui.mainWindow.moduleArea.addModule(guiPipeline, position=position)

    self.ui.mainWindow.pythonConsole.writeConsoleCommand("application.showMetabolomicsPipeline()")
    self.project._logger.info("application.showMetabolomicsPipeline()")


  def showPeakFittingModule(self):
    # from ccpn.AnalysisMetabolomics.PeakFitting import PeakFitting
    # from ccpn.AnalysisMetabolomics.ui.gui.modules.PeakFittingModule import PeakFittingModule
    #
    # self.peakFitting = PeakFitting(application=self)
    # self.ui.peakFittingModule = PeakFittingModule(application=self,
    #                                                   interactor=self.peakFitting,
    #                                                   parent=self.ui)
    # self.peakFitting.presenter = self.ui.peakFittingModule
    # self.ui.mainWindow.moduleArea.addModule(self.ui.peakFittingModule.widget, position='bottom')

    print('Interactive peak demo')
    # from application.metabolomics.presenters.peaks import InteractiveDemoPresenter
    from ccpn.AnalysisMetabolomics.ui.gui.modules.PeakFittingModule import InteractiveDemoPresenter
    self.peakDemoModule = InteractiveDemoPresenter(interactor=None,
                                                   parent=self,
                                                   project=self.project)
    self.ui.mainWindow.moduleArea.addModule(self.peakDemoModule.widget, position='bottom')
