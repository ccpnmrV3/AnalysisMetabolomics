__author__ = 'TJ Ragan'

import numpy as np
import pandas as pd
from scipy.linalg import svd
from scipy import stats

import sklearn.decomposition


class PCA_old:
  '''
  For expediency, we're using the scikit-learn PCA algorithm, which mean centers just before the
  SVD step.  In the future we should implement our own to remove the forced mean centering.
  '''
  def __init__(self, spectra, nComponents=None):
    self.inputSpectra = spectra
    self.nComponents = nComponents
    self._translateData()
    self.fittedModel = self._fitPcaModel()

  @property
  def loadings(self):
    loadings = self._fittedPcaModel.components_.T
    columnNames = ['PC{}'.format(i+1) for i in range(loadings.shape[1])]
    loadingsDF = pd.DataFrame(loadings, index=self._inputDF.columns, columns=columnNames)
    loadingsDF.columns.rename('Principle Components', inplace=True)
    loadingsDF.index.rename('ppm', inplace=True)
    return loadingsDF

  @property
  def scores(self):
    scores = self._fittedPcaModel.transform(self._inputDF)
    colNames = ['PC{}'.format(i+1) for i in range(scores.shape[1])]
    scoresDF = pd.DataFrame(scores, index=self._inputDF.index, columns=colNames)
    scoresDF.columns.rename('Principle Components', inplace=True)
    scoresDF.index.rename('samples', inplace=True)
    return scoresDF

  @property
  def explainedVariance(self):
    return self._fittedPcaModel.explained_variance_ratio_


  def _translateData(self):
    l = [pd.Series(self.inputSpectra[name][1], index=self.inputSpectra[name][0], name=name)
         for name in sorted(self.inputSpectra.keys())]

    self._inputDF = pd.concat(l, axis=1).T


  def _fitPcaModel(self):
    self._fittedPcaModel = sklearn.decomposition.PCA(n_components=self.nComponents)
    self._fittedPcaModel.fit(self._inputDF)



class PCA:

  def __init__(self, dataFrame, nComponents=None, confidenceLimit=0.95):
    self.inputDF = dataFrame
    self.nComponents = nComponents
    self.confidenceLimit = confidenceLimit


  def _fitPcaModel(self):
    X = np.asarray(self.inputDF)
    try:
      assert len(X.shape) == 2
    except:
      raise ValueError('PCA must be done on 2D array.')

    U, S, V = svd(X, full_matrices=False)

    self._calculateEigenvalues(S)
    self._calculateLoadings(V)


  def _calculateEigenvalues(self, S):
    eigenvalues = S ** 2 / (self.inputDF.shape[0] - 1)
    pcStrings = ['PC{}'.format(x) for x in range(1, self.inputDF.shape[1] + 1)]
    eigenvalues = pd.Series(eigenvalues, index=pcStrings)
    eigenvalues.index.rename('Principle Components', inplace=True)
    self.__eigenvalues_ = eigenvalues


  def _calculateLoadings(self, V):
    self.__loadings_ = pd.DataFrame(V)
    self.__loadings_.columns = self.inputDF.columns
    if self.__loadings_.columns.name is None:
      self.__loadings_.columns.rename('Features', inplace=True)
    self.__loadings_.index = ['PC{}'.format(x) for x in range(1, self.inputDF.shape[1]+1)]
    self.__loadings_.index.rename('Principle Components', inplace=True)


  @property
  def nComponents(self):
    return self.__nComponents
  @nComponents.setter
  def nComponents(self, n):
    if n is None:
      self.__nComponents = min(self.inputDF.shape)
    elif (n < 0) or (n%1):
      raise ValueError('Number of components must be a positive integer.')
    elif n > min(self.inputDF.shape):
      self.__nComponents = min(self.inputDF.shape)
    else:
      self.__nComponents = n


  @property
  def confidenceLimit(self):
    return self.__confLimit
  @confidenceLimit.setter
  def confidenceLimit(self, cl):
    if 0 < cl < 1:
      self.__confLimit = cl
    elif 1 < cl < 100:
      self.__confLimit = cl/100
    else:
      raise ValueError('Confidence Limits should be a value between 0 and 1.')


  @property
  def loadings_(self):
    return self.__loadings_[:self.nComponents]


  @property
  def explainedVariance_(self):
    explainedVariance = self.eigenvalues_ / np.sum(self.eigenvalues_)
    pcStrings = ['PC{}'.format(x) for x in range(1, self.inputDF.shape[1] + 1)]
    explainedVariance = pd.Series(explainedVariance, index=pcStrings)
    return explainedVariance[:self.nComponents]


  @property
  def scores_(self):
    scores = np.dot(self.inputDF, self.loadings_.T)
    scoresDF = pd.DataFrame(scores)
    scoresDF.columns = ['PC{}'.format(x) for x in range(1, scoresDF.shape[1]+1)]
    scoresDF.columns.rename('Principle Components', inplace=True)
    scoresDF.index = self.inputDF.index
    if scoresDF.index.name is None:
      scoresDF.index.rename('Observations', inplace=True)
    return scoresDF


  @property
  def eigenvalues_(self):
    return self.__eigenvalues_[:self.nComponents]


  @property
  def residualEigenvalues_(self):
    return self.__eigenvalues_[self.nComponents:]


  @property
  def predictions_(self):
    return np.dot(self.scores_, self.loadings_)


  @property
  def residuals_(self):
    return self.inputDF - self.predictions_


  @property
  def qScores_(self):
    return (np.sum(self.residuals_**2, axis=0), np.sum(self.residuals_**2, axis=1))


  @property
  def t2Scores_(self):
    tconDF_F = self.inputDF.copy()
    mp = np.sqrt(1/ (np.diag(np.dot(self.scores_.T, self.scores_)) /
                      (self.loadings_.shape[1] - 1)))
    tconDF_F[:] = np.dot(np.dot(self.scores_, np.diag(mp)), self.loadings_)

    tconDF_M = self.inputDF.copy()
    mp = np.sqrt(1 / (np.diag(np.dot(self.scores_.T, self.scores_)) /
                      (self.scores_.shape[0] - 1)))
    tconDF_M[:] = np.dot(np.dot(self.scores_, np.diag(mp)), self.loadings_)

    return (np.sum(np.power(tconDF_F, 2), axis=0).T,
            np.sum(np.power(tconDF_M, 2), axis=1).T)


  @property
  def t2ConfLimit(self):
    """
    from http://users.stat.umn.edu/~gary/classes/5401/handouts/11.hotellingt.handout.pdf
    """
    nComponents = self.nComponents or self.inputDF.shape[1]
    nMeasurements = self.inputDF.shape[0]

    criticalValue = stats.f.ppf(self.confidenceLimit, nComponents, nMeasurements-nComponents)
    return ((nMeasurements-1) * nComponents / (nMeasurements-nComponents)) * criticalValue


  @property
  def qConfLimit(self):
    """
    From:
    J. Edward Jackson and Govind S. Mudholkar Technometrics
    Vol. 21, No. 3 (Aug., 1979), pp. 341-349
    http://www.jstor.org/stable/1267757?seq=1#page_scan_tab_contents
    :return:
    """

    if self.nComponents is None or (self.nComponents == min(self.inputDF.shape)):
      return None

    theta1 = np.sum(self.residualEigenvalues_)
    theta2 = np.sum(self.residualEigenvalues_ ** 2)
    theta3 = np.sum(self.residualEigenvalues_ ** 3)

    h0 = 1 - (2 * theta1 * (theta3 / (3 * theta2**2)))
    ca = stats.norm.ppf(self.confidenceLimit)

    qAlpha = theta1 * (((ca * np.sqrt(2 * theta2 * (h0**2))) / theta1) + 1 +
                       ((theta2 * h0 * (h0-1)) / (theta1**2)))**(1 / h0)  # Eq 3.4
    return qAlpha


  @property
  def confidenceLimits_(self):

    nMeasurements = self.inputDF.shape[0]

    df = pd.DataFrame()
    for nDim in range(1, len(self.eigenvalues_)+1):
      p = nDim  # What is p???
      ppf = stats.f.ppf(self.confidenceLimit, nDim, nMeasurements-p)
      df[nDim] = np.sqrt(self.eigenvalues_ * (nMeasurements-1) * p / (nMeasurements-p) * ppf)
    df.columns.rename('nDim', inplace=True)
    df.index.rename('Principle Components', inplace=True)
    return df
