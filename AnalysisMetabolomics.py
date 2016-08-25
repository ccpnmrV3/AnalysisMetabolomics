__author__ = 'TJ'

from ccpn.framework.Framework import Framework


class Metabolomics(Framework):
  """Root class for Metabolomics application"""
  def __init__(self, applicationName, applicationVersion, commandLineArguments):
    Framework.__init__(self, applicationName, applicationVersion, commandLineArguments)


  def setupMenus( self ):
    super().setupMenus( )
    menuSpec = ('Metabolomics', [("Decomposition (PCA)", self.showDecompositionModule),
                                 ("Pipeline", self.showPipeline,)
                                 ])
    self.addApplicationMenuSpec(menuSpec)


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
