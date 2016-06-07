__author__ = 'TJ Ragan'

from collections import OrderedDict
import os
import shutil

import pandas as pd

from ccpn.AnalysisMetabolomics.lib import normalisation
from ccpn.AnalysisMetabolomics.lib import centering
from ccpn.AnalysisMetabolomics.lib import scaling
from ccpn.AnalysisMetabolomics.lib import decomposition
from ccpn.AnalysisMetabolomics.lib.persistence import spectraDicToBrukerExperiment

METABOLOMICS_SAVE_LOCATION = os.path.join('internal','metabolomics')

class Decomposition:

  def __init__(self, framework, presenter=None):
    self.project = framework.project
    self.__presenter = None
    self.presenter = presenter

    self.__sources = []
    self.__normalization = None
    self.__centering = None
    self.__scaling = None
    self.__decomp = None
    self.__data = None

    self.__sourcesChanged = True
    self.__normChanged = True
    self.__centChanged = True
    self.__scalingChanged = True
    self.__deScaleFunc = lambda x: x

    self.availablePlotData = OrderedDict()

    self.registerNotifiers()

    self.method = 'PCA'
    self.model = None
    self.auto = False


  # def __del__(self):
  #   self.deRegisterNotifiers()


  def registerNotifiers(self):
    self.project.registerNotifier('Spectrum', 'create', self.refreshSourceDataOptions)
    self.project.registerNotifier('Spectrum', 'change', self.refreshSourceDataOptions)
    self.project.registerNotifier('Spectrum', 'rename', self.refreshSourceDataOptions)
    self.project.registerNotifier('Spectrum', 'delete', self.refreshSourceDataOptions)


  # def deRegisterNotifiers(self):
  #   self.project._unregisterNotify(self.refreshSourceDataOptions, 'ccp.nmr.Nmr.DataSource', 'postInit')
  #   self.project._unregisterNotify(self.refreshSourceDataOptions, 'ccp.nmr.Nmr.DataSource', 'delete')
  #   self.project._unregisterNotify(self.refreshSourceDataOptions, 'ccp.nmr.Nmr.DataSource', 'setName')


  @property
  def presenter(self):
    return self.__presenter

  @presenter.setter
  def presenter(self, value):
    self.__presenter = value
    if value is not None:
      self.refreshSourceDataOptions()

  @property
  def method(self):
    return self.__decomp

  @method.setter
  def method(self, value):
    if value.upper() == 'PCA':
      self.__decomp = value.upper()
    else:
      raise NotImplementedError('PCA is the only currently implemented decomposition method.')

  # def reg(self):
  #   project.allSpectra.register(self.refreshSourceDataOptions, 'new')

  def refreshSourceDataOptions(self, *args):
    if self.presenter is not None:
      self.presenter.setSourceDataOptions(self.getSourceData())


  def getSourceData(self):
    sd = []
    sd += [s for s in self.project.spectra if
              (len(s.axisCodes) == 1) and (s.axisCodes[0].startswith('H'))]
    # if self.project.spectra:
    #   raise Exception
    # print(self.project.spectra)
    # print(list([s.axisCodes for s in self.project.spectra]))
    # print(sd)
    return sd


  @property
  def normalization(self):
    return self.__normalization

  @normalization.setter
  def normalization(self, value):
    self.__normalization = value
    # self.__normChanged = True
    # self.__centChanged = True
    # self.__scalingChanged = True
    if self.auto:
      self.decompose()

  @property
  def centering(self):
    return self.__centering

  @centering.setter
  def centering(self, value):
    self.__centering = value
    # self.__centChanged = True
    # self.__scalingChanged = True
    if self.auto:
      self.decompose()

  @property
  def scaling(self):
    return self.__scaling

  @scaling.setter
  def scaling(self, value):
    self.__scaling = value
    # self.__scalingChanged = True
    if self.auto:
      self.decompose()

  @property
  def sources(self):
    return self.__sources

  @sources.setter
  def sources(self, value):
    self.__sources = value
    # self.__sourcesChanged = True
    # self.__normChanged = True
    # self.__centChanged = True
    # self.__scalingChanged = True
    if self.auto:
      self.decompose()


  def buildSourceData(self):
    self.__sourcesChanged = False
    sd = OrderedDict()
    for d in self.__sources:
      sd[d] = self.project.getByPid('SP:{}'.format(d))._apiDataSource.get1dSpectrumData()
    l = [pd.Series(sd[name][1], index=sd[name][0], name=name) for name in sorted(sd.keys())]
    self.__data = pd.concat(l, axis=1).T

  def normalize(self):
    if self.normalization.upper() == 'PQN':
      self.__data = normalisation.pqn(self.__data)
    elif self.normalization.upper() == 'TSA':
      self.__data = normalisation.tsa(self.__data)
    elif self.normalization.lower() == 'none':
      pass
    else:
      raise NotImplementedError("Only PQN, TSA and 'none' type normalizations currently supported.")
    # self.__normChanged = False


  def center(self):
    if self.centering.lower() == 'mean':
      self.__data = centering.meanCenter(self.__data)
    elif self.centering.lower() == 'median':
      self.__data = centering.medianCenter(self.__data)
    elif self.centering.lower() == 'none':
      pass
    else:
      raise NotImplementedError("Only mean, median and 'none' type centerings currently supported.")
    # self.__centChanged = False


  def scale(self):
    if self.scaling.lower() == 'pareto':
      self.__data, self.__deScaleFunc = scaling.paretoScale(self.__data)
    elif self.scaling.lower() == 'unit variance':
      self.__data, self.__deScaleFunc = scaling.unitVarianceScale(self.__data)
    elif self.scaling.lower() == 'none':
      pass
    else:
      raise NotImplementedError("Only pareto, unit variance and 'none' type scalings currently supported.")
    # self.__scalingChanged = False


  def decompose(self):
    if len(self.__sources) > 1:
      # if self.__sourcesChanged:
      #   self.buildSourceData()
      # if self.__normChanged:
      #   self.normalize()
      # if self.__centChanged:
      #   self.center()
      # if self.__scalingChanged:
      #   self.scale()
      self.buildSourceData()
      self.normalize()
      self.center()
      self.scale()
      self.model = getattr(decomposition, self.__decomp)(self.__data)
      self.setAvailablePlotData()


  def setAvailablePlotData(self):
    defaults = OrderedDict()
    if self.method == 'PCA':
      self.availablePlotData = OrderedDict()
      self.availablePlotData['Component #'] = list(range(len(self.model.scores_)))
      self.availablePlotData['Explained Vairance'] = self.model.explainedVariance_
      for score in self.model.scores_:
        self.availablePlotData[score] = self.model.scores_[score].values


      defaults['xDefaultLeft'] = 'Component'
      defaults['yDefaultLeft'] = 'Explained Vairance'
      defaults['xDefaultRight'] = 'PC1'
      defaults['yDefaultRight'] = 'PC2'
    else:
      raise NotImplementedError('Only PCA output is currently supported.')
    self.presenter.setAvailablePlotData(list(self.availablePlotData.keys()),
                                        **defaults)


  def saveLoadingsToSpectra(self, prefix='test_pca', descale=True, components=None):
    saveLocation = os.path.join(self.project.path, METABOLOMICS_SAVE_LOCATION, 'pca', prefix)

    sgNames = [sg.name for sg in self.project.spectrumGroups]
    if prefix in sgNames:
      g = self.project.getByPid('SG:' + prefix)
    else:
      g = self.project.newSpectrumGroup(prefix)
      # TODO: Wayne: deleted spectra should be removed from spectrum groups!

    toDeleteSpectra = [s for s in self.project.spectra if s.name.endswith(prefix)]
    for s in toDeleteSpectra:
      s.delete()
    try:
      shutil.rmtree(saveLocation)
    except FileNotFoundError:
      pass

    if components is None:
      # TODO: Generalize beyond PCA
      components = self.model.loadings_

    if descale:
      components = components.apply(self.__deScaleFunc, axis=1)

    spectraDicToBrukerExperiment(components, saveLocation)

    loadingsSpectra = []
    for d in next(os.walk(saveLocation))[1]:
      loadedSpectrum = self.project.loadData(os.path.join(saveLocation, d))[0]
      loadingsSpectra.append(loadedSpectrum)
      newSpectrumName = loadedSpectrum.pid.split('-')[0][3:] + '-' + prefix
      loadedSpectrum.rename(newSpectrumName)
    g.spectra = loadingsSpectra


  @property
  def loadings(self):
    return None

  @property
  def scores(self):
    return None
