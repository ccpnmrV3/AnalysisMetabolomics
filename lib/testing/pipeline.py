__author__ = 'TJ Ragan'

import unittest
import numpy as np
import numpy.testing as npt

from ccpn.AnalysisMetabolomics.lib.pipeline import pipeline
from ccpn.AnalysisMetabolomics.lib import normalisation


class TestPipeline(unittest.TestCase):
  def setUp(self):
    self.spectra = {'SP1-1': np.array([[3,2,1], [1,1,1]]),
                    'SP1-2': np.array([[3,2,1], [1,1,1]]),
                    'SP1-3': np.array([[3,2,1], [4,7,1]]),
                   }
    self.orderedSpectralNames = []
    orderedSpectralShifts = []
    orderedSpectralIntensities = []
    for k, v in sorted(self.spectra.items()):
      self.orderedSpectralNames.append(k)
      orderedSpectralShifts.append(v[0])
      orderedSpectralIntensities.append(v[1])
    self.orderedSpectralShifts = np.asarray(orderedSpectralShifts)
    self.orderedSpectralIntensities = np.asarray(orderedSpectralIntensities)


  def test_empty_pipeline_does_nothing(self):
    output = pipeline(self.spectra, [])

    self.assertEqual(len(output), len(self.spectra))
    for k,v in output.items():
      inSpec = self.spectra[k]
      npt.assert_array_equal(v, inSpec)


  def test_pipeline_with_single_tsa_command(self):
    commands = [{'function': 'normalise', 'method': 'Total Area'}]
    output = pipeline(self.spectra, commands)
    o = []
    for k, v in sorted(output.items()):
      o.append(v[1])
    npt.assert_array_equal(np.asarray(o), normalisation.tsa(self.orderedSpectralIntensities))

  def test_pipeline_with_single_pqn_command(self):
    commands = [{'function': 'normalise', 'method': 'PQN'}]
    output = pipeline(self.spectra, commands)
    o = []
    for k, v in sorted(output.items()):
      o.append(v[1])
    npt.assert_array_equal(np.asarray(o), normalisation.pqn(self.orderedSpectralIntensities))


  def _test_pipeline_with_single_polyBaseline_command(self):
    commands = [{'function': 'polyBaseLine', 'controlPoints': [2.0, 1.0, 0.0]}]
    output = pipeline(self.spectra, commands)

if __name__ == '__main__':
  unittest.main()
