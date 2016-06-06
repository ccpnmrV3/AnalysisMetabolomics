import numpy as np

def pqn(spectrumCluster):

  totalNormed = tsa(spectrumCluster)
  avg = totalNormed.mean(axis=0)
  quotients = totalNormed/avg
  medians = np.median(quotients, axis=1)
  pqn = (totalNormed.T/medians).T
  return pqn


def tsa(spectra):

  sums = spectra.sum(axis=1)
  tsa = (spectra.T / sums).T
  return tsa

def getSpectrumCluster(spectra):
  pointCount = spectra[0].totalPointCounts[0]
  array1 = np.empty([len(spectra), pointCount])
  for i in range(len(spectra)):
    array1[i] = spectra[i]._apiDataSource.getSliceData()

  return array1

def updateSpectrumCluster(spectra, spectrumCluster):
  for i in range(len(spectra)):
    plot = spectra[i].spectrumViews[0].plot
    xData = spectra[i].spectrumViews[0].data[0]
    yData = spectrumCluster[i]
    plot.setData(xData, yData)
