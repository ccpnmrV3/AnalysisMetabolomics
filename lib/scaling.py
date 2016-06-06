import numpy as np
from .centering import meanCenter


def varianceScale(spectrumCluster, power):
  stdevs = np.std(spectrumCluster, axis=0)
  scaled = spectrumCluster / (stdevs ** power)
  return scaled


def unitVarianceScale(spectra):
  return varianceScale(spectra, power=1)


def paretoScale(spectra):
  return varianceScale(spectra, power=0.5)


def rangeScale(spectra):
  specMins = spectra.min(axis=0)
  specMaxs = spectra.max(axis=0)
  diffs = specMaxs - specMins
  scaled = spectra / diffs
  return scaled


def vastScale(spectra):
  means = np.mean(spectra, axis=0)
  stdevs = np.std(spectra, axis=0)
  vScale = means / stdevs
  scaled = unitVarianceScale(spectra) * vScale
  return scaled


def levelScale(spectra):
  means = np.mean(spectra, axis=0)
  scaled = spectra / means
  return scaled


def autoScale(spectra):
  mc = meanCenter(spectra)
  scaled = unitVarianceScale(mc)
  return scaled
