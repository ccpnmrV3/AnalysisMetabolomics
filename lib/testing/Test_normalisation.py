__author__ = 'TJ Ragan'

import unittest
import numpy as np
import numpy.testing as npt

from ccpn.AnalysisMetabolomics.lib import normalisation
from ccpn.AnalysisMetabolomics.lib import centering
from ccpn.AnalysisMetabolomics.lib import scaling


class TestNormalisation(unittest.TestCase):

  def test_TSA(self):
    rawSpectra = np.array([[0,1,0],
                           [0,2,0]])


    targetSpectra = np.array([[0,1,0],
                              [0,1,0]])

    normalizedSpectra = normalisation.tsa(rawSpectra)
    npt.assert_array_equal(normalizedSpectra, targetSpectra)


  def test_PQN(self):
    rawSpectra = np.ones([2,3])
    rawSpectra[0,1] = 2

    normalizedSpectra = normalisation.pqn(rawSpectra)
    self.assertEqual(normalizedSpectra[0,0], normalizedSpectra[1,0])
    self.assertNotEqual(normalizedSpectra[0,1], normalizedSpectra[1,1])
    self.assertEqual(normalizedSpectra[0,2], normalizedSpectra[1,2])



if __name__ == '__main__':
  unittest.main()

