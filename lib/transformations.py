__author__ = 'simon1'

import numpy as np


def logTransform(spectrumCluster):
  return np.log10(spectrumCluster)


def powerTransform(spectrumCluster, power=0.5):
  return spectrumCluster ** power
