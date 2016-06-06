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


class TestScaling(unittest.TestCase):

  def test_unitVarianceScale(self):
    rawSpectra = np.array([[1,1,1],
                           [2,3,2]])
    targetSpectra = np.array([[2,1,2],
                              [4,3,4]])

    scaledSpectra = scaling.unitVarianceScale(rawSpectra)
    npt.assert_array_equal(scaledSpectra, targetSpectra)

  def test_paretoScale(self):
    rawSpectra = np.array([[1,1,1],
                           [3,9,3]])
    targetSpectra = np.array([[1,0.5,1],
                              [3,4.5,3]])

    scaledSpectra = scaling.paretoScale(rawSpectra)
    npt.assert_array_equal(scaledSpectra, targetSpectra)

  def test_autoScale(self):
    rawSpectra = np.array([[1,1,1],
                           [2,3,2]])
    targetSpectra = np.array([[-1,-1,-1],
                              [ 1, 1, 1]])

    scaledSpectra = scaling.autoScale(rawSpectra)
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

