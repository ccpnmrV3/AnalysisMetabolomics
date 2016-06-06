__author__ = 'TJ Ragan'

import unittest

import numpy as np
import numpy.testing as npt
import pandas as pd

from ccpn.AnalysisMetabolomics.lib.decomposition import PCA


class TestPCA(unittest.TestCase):
  def setUp(self):
    self.spectra = {'SP1-1': np.array([[2,1], [-1,-1]]),
                    'SP1-2': np.array([[2,1], [-2,-1]]),
                    'SP1-3': np.array([[2,1], [-3,-2]]),
                    'SP1-4': np.array([[2,1], [1,1]]),
                    'SP1-5': np.array([[2,1], [2,1]]),
                    'SP1-6': np.array([[2,1], [3,2]]),
                   }
    l = [pd.Series(self.spectra[name][1], index=self.spectra[name][0], name=name)
         for name in sorted(self.spectra.keys())]

    self.inputDF = pd.concat(l, axis=1).T
    self.inputDF.index.rename('spectra', inplace=True)
    self.inputDF.columns.rename('ppm', inplace=True)


    inDF_centered = self.inputDF - self.inputDF.mean()
    self.inDF_proc = inDF_centered / inDF_centered.std()

    self.pca = PCA(self.inDF_proc)


  def _test_storedData(self):
    # print(self.pca.inputDF)
    pdt.assert_index_equal(self.pca.inputDF.columns, pd.Index([2,1]))
    pdt.assert_index_equal(self.pca.inputDF.index, pd.Index(['SP1-1', 'SP1-2', 'SP1-3',
                                                             'SP1-4', 'SP1-5', 'SP1-6']))

  # TODO: accept named columns and indices as default instead of changing to features and measurements
  def test_loadings(self):
    pdt.assert_index_equal(self.pca.loadings_.columns, pd.Index([2, 1], name='ppm'))
    pdt.assert_index_equal(self.pca.loadings_.index, pd.Index(['PC1',
                                                               'PC2'],
                                                              name='Principle Components'))
    npt.assert_array_almost_equal(self.pca.loadings_.values,
                                  np.array([[0.707107,  0.707107],
                                            [0.707107, -0.707107]]))

  def test_scores(self):
    pdt.assert_index_equal(self.pca.scores_.columns, pd.Index(['PC1', 'PC2'], name='Principle Components'))
    pdt.assert_index_equal(self.pca.scores_.index, pd.Index(['SP1-1',
                                                             'SP1-2',
                                                             'SP1-3',
                                                             'SP1-4',
                                                             'SP1-5',
                                                             'SP1-6'],
                                                            name='spectra'))
    npt.assert_array_almost_equal(self.pca.scores_.values,
                                  np.array([[-0.755243,  0.157628],
                                            [-1.054050, -0.141179],
                                            [-1.809292,  0.016449],
                                            [ 0.755243, -0.157628],
                                            [ 1.054050,  0.141179],
                                            [ 1.809292, -0.016449]]))

  def test_explainedVariance(self):
    pdt.assert_index_equal(self.pca.scores_.columns, pd.Index(['PC1', 'PC2'], name='Principle Components'))
    npt.assert_array_almost_equal(self.pca.explainedVariance_.values,
                                  np.array([0.99099, 0.00901]))

  def test_eigenvalues(self):
    pdt.assert_index_equal(self.pca.scores_.columns, pd.Index(['PC1', 'PC2'], name='Principle Components'))
    npt.assert_array_almost_equal(self.pca.eigenvalues_.values,
                                  np.array([1.981981, 0.018019]))

  def test_residualEigenvalues(self):
    self.pca.nComponents = 1
    pdt.assert_index_equal(self.pca.residualEigenvalues_.index, pd.Index(['PC2'], name='Principle Components'))
    npt.assert_array_almost_equal(self.pca.residualEigenvalues_.values,
                                  np.array([0.018019]))

  def test_qScores_aka_SumOfSquaresResiduals_by_Features(self):
    self.pca.nComponents = 1
    pdt.assert_index_equal(self.pca.qScores_[0].index, pd.Index([2,1], name='ppm'))
    npt.assert_array_almost_equal(self.pca.qScores_[0].values,
                                  np.array([0.045049, 0.045049]))

  def test_qScores_aka_SumOfSquaresResiduals_by_Measurements(self):
    self.pca.nComponents = 1
    pdt.assert_index_equal(self.pca.qScores_[1].index, pd.Index(['SP1-1',
                                                                 'SP1-2',
                                                                 'SP1-3',
                                                                 'SP1-4',
                                                                 'SP1-5',
                                                                 'SP1-6'],
                                                                name='spectra'))
    npt.assert_array_almost_equal(self.pca.qScores_[1].values,
                                  np.array([0.024847, 0.019931, 0.000271, 0.024847, 0.019931, 0.000271]))


  def test_t2Scores_aka_Hotellings_by_Features(self):
    self.pca.nComponents = 1
    pdt.assert_index_equal(self.pca.t2Scores_[0].index, pd.Index([2,1], name='ppm'))
    npt.assert_array_almost_equal(self.pca.t2Scores_[0].values,
                                  np.array([0.5, 0.5]))

  def test_t2Scores_aka_Hotellings_by_Measurements(self):
    self.pca.nComponents = 1
    pdt.assert_index_equal(self.pca.qScores_[1].index, pd.Index(['SP1-1',
                                                                 'SP1-2',
                                                                 'SP1-3',
                                                                 'SP1-4',
                                                                 'SP1-5',
                                                                 'SP1-6'],
                                                                name='spectra'))
    npt.assert_array_almost_equal(self.pca.t2Scores_[1].values,
                                  np.array([0.287789, 0.560561, 1.65165, 0.287789, 0.560561, 1.65165]))

  def test_t2ConfLimit(self):
    self.assertAlmostEqual(self.pca.t2ConfLimit, 17.36068, 5)

  def test_confidenceLimits(self):
    npt.assert_array_almost_equal(self.pca.confidenceLimits_[1].values, np.array([3.6189, 0.3451]), 4)
    npt.assert_array_almost_equal(self.pca.confidenceLimits_[2].values, np.array([5.8659, 0.5593]), 4)

  def test_qConfLimit(self):
    self.assertIsNone(self.pca.qConfLimit)
    self.pca.nComponents = 1
    self.assertAlmostEqual(self.pca.qConfLimit, 0.0675, 4)



if __name__ == '__main__':
  unittest.main()
