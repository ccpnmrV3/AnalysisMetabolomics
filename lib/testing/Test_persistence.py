
__author__ = 'TJ Ragan'

import unittest

import pandas as pd

from ccpn.AnalysisMetabolomics.lib import persistence


class TestBrukerWriter(unittest.TestCase):
  def setUp(self):
    series = pd.Series([0.2, 0.1], index=[2, 1], name='test spec')
    series.index.rename('ppm', inplace=True)
    self.spectrumDF = series.to_frame().T

  def test_bruker1dDict(self):
    d = persistence.bruker1dDict(self.spectrumDF, SF=500)
    self.assertEqual(d['SF'], 500)
    self.assertEqual(d['OFFSET'], self.spectrumDF.columns.max())
    self.assertEqual(d['FTSIZE'], len(self.spectrumDF.columns))
    self.assertEqual(d['SI'], len(self.spectrumDF.columns))
    self.assertEqual(d['SW_p'], 500)

if __name__ == '__main__':
  unittest.main()
