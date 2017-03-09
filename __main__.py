__author__ = 'TJ!'

from ccpn.framework import Framework
from ccpn.AnalysisMetabolomics.AnalysisMetabolomics import Metabolomics as Application
from ccpn.framework.Version import applicationVersion

if __name__ == '__main__':
  from ccpn.util.GitTools import getAllRepositoriesGitCommit
  applicationVersion = 'development: {AnalysisMetabolomics:.8s}'.format(**getAllRepositoriesGitCommit())

  # argument parser
  parser = Framework.defineProgramArguments()

  # add any additional commandline argument here
  commandLineArguments = parser.parse_args()

  application = Application('AnalysisMetabolomics', applicationVersion, commandLineArguments)
  Framework._getApplication = lambda: application
  application.start()
