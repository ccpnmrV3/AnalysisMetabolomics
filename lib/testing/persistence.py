
__author__ = 'TJ Ragan'

import unittest

import pandas as pd

from ccpn.AnalysisMetabolomics.lib import persistence


class TestMetabolomicsPersistenceDict(unittest.TestCase):
  def setUp(self):
    self.pd = persistence.MetabolomicsPersistenceDict()


  def test_MetabolomicsPersistenceDict_shares_state(self):
    self.pd['1'] = 1
    test = persistence.MetabolomicsPersistenceDict(('1', 1))

    self.assertIn('1', self.pd)
    self.assertIn('1', test)


class TestBrukerWriter(unittest.TestCase):
  def setUp(self):
    self.dataSeries = pd.Series([0.2, 0.1], index=[2, 1], name='test spec')
    self.dataSeries.index.rename('ppm', inplace=True)

  def test_bruker1dDict(self):
    d = persistence.bruker1dDict(self.dataSeries, SF=500)
    self.assertEqual(d['SF'], 500)
    self.assertEqual(d['OFFSET'], self.dataSeries.index.max())
    self.assertEqual(d['FTSIZE'], len(self.dataSeries))
    self.assertEqual(d['SI'], len(self.dataSeries))
    self.assertEqual(d['SW_p'], 500)

if __name__ == '__main__':
  unittest.main()
