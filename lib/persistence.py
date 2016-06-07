__author__ = 'TJ Ragan'

import os
from collections import OrderedDict

import numpy as np

class Borg:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state


class MetabolomicsPersistenceDict(OrderedDict):
  class __Inner(OrderedDict):
    pass
  instance = None

  def __new__(cls, *args, **kwargs):
    if cls.instance is None:
      cls.instance = cls.__Inner(*args, **kwargs)
    return cls.instance


def bruker1dDict(refDF=None, SF=1, FTSIZE=None, SW_p=None, OFFSET=None):
  procs = {'BYTORDP': 0, # Byte order, little (0) or big (1) endian
           'XDIM': 0, # Block size for 2D & 3D data
           'SF': SF, # Spectral reference frequency (center of spectrum)
           'FTSIZE': FTSIZE, # Size of FT output.  Same as SI except for strip plotting.
           'AXNUC': '<1H>',
           'WDW': 1, # Window multiplication mode
           'BC_mod': 0, # Baseline correction mode (em, gm, sine, qsine, trap, user(?), sinc, qsinc, traf, trafs(JMR 71 1987, 237))
           'LB': 0.0, # Lorentzian broadening size (Hz)
           'GB': 0.0, # Gaussian broadening factor
           'SSB': 0.0, # Sine bell shift pi/ssb.  =1 for sine and =2 for cosine.  values <2 default to sine
           'TM1': 0.0, # End of the rising edge of trapezoidal, takes a value from 0-1, must be less than TM2
           'TM2': 1.0, # Beginings of the falling edge of trapezoidal, takes a value from 0-1, must be greater than TM1
          }
  procs['SW_p'] = SW_p # Spectral width of processed data in Hz
  procs['OFFSET'] = OFFSET # ppm value of left-most point in spectrum
  if refDF is not None:
    ppmMin, ppmMax = refDF.columns.min(), refDF.columns.max()
    swPpm = float(ppmMax) - float(ppmMin)
    procs['SW_p'] = swPpm * procs['SF']
    procs['OFFSET'] = ppmMax
    procs['FTSIZE'] = len(refDF.columns)
    procs['SI'] = len(refDF.columns)

  return procs



def writeBruker(directory, dic, data):
    procDir = 'pdata/1'
    realFileName = '1r'
    try:
        os.makedirs(os.path.join(directory, procDir))
    except FileExistsError:
        pass

    specMax2 = np.log2(data.max())
    factor = int(29-specMax2)
    data = data * 2**factor
    dic['NC_proc'] = -factor

    with open(os.path.join(directory, procDir, 'procs'), 'w') as f:
        for k in sorted(dic.keys()):
            f.write('##${}= {}\n'.format(k, dic[k]))

    with open(os.path.join(directory, procDir, realFileName), 'wb') as f:
        f.write(data.astype('<i4').tobytes())


def spectraDicToBrukerExperiment(spectraDF, directoryName, **kwargs):
  if isinstance(spectraDF, dict):
    l = [pd.Series(spectraDF[name][1], index=spectraDF[name][0], name=name)
         for name in sorted(spectraDF.keys())]

    spectraDF = pd.concat(l, axis=1).T
  procs = bruker1dDict(spectraDF, SF=500)
  for pcName in spectraDF.index:
    writeBruker(os.path.join(directoryName, pcName), procs, spectraDF.ix[pcName].values)

