__author__ = 'TJ'

from ccpn.core.lib.Version import applicationVersion
from ccpn.framework.Framework import defineProgramArguments
from ccpn.AnalysisMetabolomics.AnalysisMetabolomics import Metabolomics


if __name__ == '__main__':

  # argument parser
  parser = defineProgramArguments()

  # add any additional commandline argument here
  commandLineArguments = parser.parse_args()

  program = Metabolomics('Metabolomics', applicationVersion, commandLineArguments)
  program.start()
