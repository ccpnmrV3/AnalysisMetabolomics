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
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-04-07 11:41:23 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: TJ Ragan $"
__date__ = "$Date: 2017-04-07 10:28:45 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import unittest
import numpy as np
import numpy.testing as npt

from ccpn.AnalysisMetabolomics.lib import normalisation
from ccpn.AnalysisMetabolomics.lib import centering
from ccpn.AnalysisMetabolomics.lib import scaling


class TestCentering(unittest.TestCase):

  def test_meanCenter(self):
    rawSpectra = np.array([[1,1,1],
                           [1,1,1],
                           [4,7,1]])
    targetSpectra = np.array([[-1,-2,0],
                              [-1,-2,0],
                              [ 2, 4,0]])

    centeredSpectra = centering.meanCenter(rawSpectra)
    npt.assert_array_equal(centeredSpectra, targetSpectra)


  def test_medianCenter(self):
    rawSpectra = np.array([[1,1,1],
                           [1,1,1],
                           [4,7,1]])
    targetSpectra = np.array([[0,0,0],
                              [0,0,0],
                              [3,6,0]])

    centeredSpectra = centering.medianCenter(rawSpectra)
    npt.assert_array_equal(centeredSpectra, targetSpectra)



if __name__ == '__main__':
  unittest.main()

