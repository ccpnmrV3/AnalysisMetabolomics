__author__ = 'TJ'

from ccpn.framework.lib.SvnRevision import applicationVersion
from ccpn.framework.Framework import defineProgramArguments, Framework

applicationName = 'Metabolomics'


class Metabolomics(Framework):
  """Root class for Metabolomics application"""
  def __init__(self, applicationName, applicationVersion, commandLineArguments):
    Framework.__init__(self, applicationName, applicationVersion, commandLineArguments)

  def _setupMenus(self):
    super()._setupMenus()
    menuSpec = ('Metabolomics', [("Decomposition (PCA)", self.showDecompositionModule),
                                ])
    self.addApplicationMenuSpec(menuSpec)

  def showDecompositionModule(self):
    from ccpn.AnalysisMetabolomics.Decomposition import Decomposition
    from ccpn.AnalysisMetabolomics.ui.gui.modules.DecompositionModule import DecompositionModule

    self.decomposition = Decomposition(framework=self)
    self.ui.decompositionModule = DecompositionModule(framework=self,
                                                      interactor=self.decomposition,
                                                      parent=self.ui)
    self.decomposition.presenter = self.ui.decompositionModule
    self.ui.mainWindow.moduleArea.addModule(self.ui.decompositionModule.widget, position='bottom')


if __name__ == '__main__':

  # argument parser
  parser = defineProgramArguments()

  # add any additional commandline argument here
  commandLineArguments = parser.parse_args()

  program = Metabolomics(applicationName, applicationVersion, commandLineArguments)
  program.start()
