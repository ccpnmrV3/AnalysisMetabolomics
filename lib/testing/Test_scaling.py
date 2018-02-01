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
__dateModified__ = "$dateModified: 2017-07-07 16:32:23 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b3 $"
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


class TestScaling(unittest.TestCase):

  def test_unitVarianceScale(self):
    rawSpectra = np.array([[1,1,1],
                           [2,3,2]])
    targetSpectra = np.array([[2,1,2],
                              [4,3,4]])

    scaledSpectra, descaleFunc = scaling.unitVarianceScale(rawSpectra)
    npt.assert_array_equal(scaledSpectra, targetSpectra)
    npt.assert_array_almost_equal(descaleFunc(scaledSpectra),
                                  rawSpectra)


  def test_paretoScale(self):
    rawSpectra = np.array([[1,1,1],
                           [3,9,3]])
    targetSpectra = np.array([[1,0.5,1],
                              [3,4.5,3]])

    scaledSpectra, descaleFunc = scaling.paretoScale(rawSpectra)
    npt.assert_array_equal(scaledSpectra, targetSpectra)
    npt.assert_array_almost_equal(descaleFunc(scaledSpectra), rawSpectra)


  def test_autoScale(self):
    rawSpectra = np.array([[1,1,1],
                           [2,3,2]])
    targetSpectra = np.array([[-1,-1,-1],
                              [ 1, 1, 1]])

    scaledSpectra, descaleFunc = scaling.autoScale(rawSpectra)
    npt.assert_array_equal(scaledSpectra, targetSpectra)


  def test_rangeScale(self):
    rawSpectra = np.array([[1,1,1],
                           [2,3,2]])
    targetSpectra = np.array([[1,0.5,1],
                              [2,1.5,2]])

    scaledSpectra = scaling.rangeScale(rawSpectra)
    npt.assert_array_equal(scaledSpectra, targetSpectra)

  def test_levelScale(self):
    rawSpectra = np.array([[1,1,1],
                           [3,7,3]])
    targetSpectra = np.array([[0.5,0.25,0.5],
                              [1.5,1.75,1.5]])

    scaledSpectra = scaling.levelScale(rawSpectra)
    npt.assert_array_equal(scaledSpectra, targetSpectra)

  def test_vastScale(self):
    pass


if __name__ == '__main__':
  unittest.main()

