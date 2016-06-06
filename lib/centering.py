import numpy as np


def meanCenter(spectrumCluster):

  means = np.mean(spectrumCluster, axis=0)
  meanCentered = spectrumCluster - means
  return meanCentered


def medianCenter(spectrumCluster):

  medians = np.median(spectrumCluster, axis=0)
  medianCentered = spectrumCluster - medians
  return medianCentered
