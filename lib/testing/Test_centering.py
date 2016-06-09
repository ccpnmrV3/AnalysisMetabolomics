__author__ = 'TJ Ragan'

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

