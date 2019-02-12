#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2019"
__credits__ = ("Ed Brooksbank, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license")
__reference__ = ("Skinner, S.P., Fogh, R.H., Boucher, W., Ragan, T.J., Mureddu, L.G., & Vuister, G.W.",
                 "CcpNmr AnalysisAssign: a flexible platform for integrated NMR analysis",
                 "J.Biomol.Nmr (2016), 66, 111-124, http://doi.org/10.1007/s10858-016-0060-y")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:23 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b5 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: TJ Ragan $"
__date__ = "$Date: 2017-04-07 10:28:45 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================


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
