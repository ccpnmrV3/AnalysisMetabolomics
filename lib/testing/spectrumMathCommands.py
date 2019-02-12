# This must be the first statemewnt in the file:
from __future__ import unicode_literals, print_function, absolute_import, division


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
import numpy as np
import numpy.testing as npt

from ccpn.AnalysisMetabolomics.lib import commands


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.rawSpectra = np.array([[1, 2, 3],
                                    [4, 5, 6]])

        self.adjustmentSpectrum = np.array([1, 2, 3])
        self.adjustmentCoefficients = np.array([1, 2])

    def test_AdditionByFrequencyCommand(self):
        targetSpectra = np.array([[2, 4, 6],
                                  [5, 7, 9]])
        cmd = commands.Command('add', self.adjustmentSpectrum, 'by frequency')
        processedSpectra = cmd.process(self.rawSpectra)
        npt.assert_array_equal(processedSpectra, targetSpectra)

    def test_UndoAdditionByFrequencyCommand(self):
        targetSpectra = np.array([[2, 4, 6],
                                  [5, 7, 9]])
        cmd = commands.Command('add', self.adjustmentSpectrum, 'by frequency')
        processedSpectra = cmd.unprocess(targetSpectra)
        npt.assert_array_equal(processedSpectra, self.rawSpectra)

    def test_AdditionBySpectrumCommand(self):
        targetSpectra = np.array([[2, 3, 4],
                                  [6, 7, 8]])
        cmd = commands.Command('add', self.adjustmentCoefficients, 'by spectrum')
        processedSpectra = cmd.process(self.rawSpectra)
        npt.assert_array_equal(processedSpectra, targetSpectra)

    def test_UndoAdditionBySpectrumCommand(self):
        targetSpectra = np.array([[2, 3, 4],
                                  [6, 7, 8]])
        cmd = commands.Command('add', self.adjustmentCoefficients, 'by spectrum')
        processedSpectra = cmd.unprocess(targetSpectra)
        npt.assert_array_equal(processedSpectra, self.rawSpectra)

    def test_SubtractionByFrequencyCommand(self):
        targetSpectra = np.array([[0, 0, 0],
                                  [3, 3, 3]])
        cmd = commands.Command('subtract', self.adjustmentSpectrum, 'by frequency')
        processedSpectra = cmd.process(self.rawSpectra)
        npt.assert_array_equal(processedSpectra, targetSpectra)

    def test_UndoSubtractionByFrequencyCommand(self):
        targetSpectra = np.array([[0, 0, 0],
                                  [3, 3, 3]])
        cmd = commands.Command('subtract', self.adjustmentSpectrum, 'by frequency')
        processedSpectra = cmd.unprocess(targetSpectra)
        npt.assert_array_equal(processedSpectra, self.rawSpectra)

    def test_SubtractionBySpectrumCommand(self):
        targetSpectra = np.array([[0, 1, 2],
                                  [2, 3, 4]])
        cmd = commands.Command('subtract', self.adjustmentCoefficients, 'by spectrum')
        processedSpectra = cmd.process(self.rawSpectra)
        npt.assert_array_equal(processedSpectra, targetSpectra)

    def test_UndoSubtractionBySpectrumCommand(self):
        targetSpectra = np.array([[0, 1, 2],
                                  [2, 3, 4]])
        cmd = commands.Command('subtract', self.adjustmentCoefficients, 'by spectrum')
        processedSpectra = cmd.unprocess(targetSpectra)
        npt.assert_array_equal(processedSpectra, self.rawSpectra)

    def test_MultiplicationByFrequencyCommand(self):
        targetSpectra = np.array([[1, 4, 9],
                                  [4, 10, 18]])
        cmd = commands.Command('multiply', self.adjustmentSpectrum, 'by frequency')
        processedSpectra = cmd.process(self.rawSpectra)
        npt.assert_array_equal(processedSpectra, targetSpectra)

    def test_UndoMultiplicationByFrequencyCommand(self):
        targetSpectra = np.array([[1, 4, 9],
                                  [4, 10, 18]])
        cmd = commands.Command('multiply', self.adjustmentSpectrum, 'by frequency')
        processedSpectra = cmd.unprocess(targetSpectra)
        npt.assert_array_equal(processedSpectra, self.rawSpectra)

    def test_MultiplicationBySpectrumCommand(self):
        targetSpectra = np.array([[1, 2, 3],
                                  [8, 10, 12]])
        cmd = commands.Command('multiply', self.adjustmentCoefficients, 'by spectrum')
        processedSpectra = cmd.process(self.rawSpectra)
        npt.assert_array_equal(processedSpectra, targetSpectra)

    def test_UndoMultiplicationBySpectrumCommand(self):
        targetSpectra = np.array([[1, 2, 3],
                                  [8, 10, 12]])
        cmd = commands.Command('multiply', self.adjustmentCoefficients, 'by spectrum')
        processedSpectra = cmd.unprocess(targetSpectra)
        npt.assert_array_equal(processedSpectra, self.rawSpectra)

    def test_DivisionByFrequencyCommand(self):
        targetSpectra = np.array([[1, 1, 1],
                                  [4, 2.5, 2]])
        cmd = commands.Command('divide', self.adjustmentSpectrum, 'by frequency')
        processedSpectra = cmd.process(self.rawSpectra)
        npt.assert_array_equal(processedSpectra, targetSpectra)

    def test_UndoDivisionByFrequencyCommand(self):
        targetSpectra = np.array([[1, 1, 1],
                                  [4, 2.5, 2]])
        cmd = commands.Command('divide', self.adjustmentSpectrum, 'by frequency')
        processedSpectra = cmd.unprocess(targetSpectra)
        npt.assert_array_equal(processedSpectra, self.rawSpectra)

    def test_DivisionBySpectrumCommand(self):
        targetSpectra = np.array([[1, 2, 3],
                                  [2, 2.5, 3]])
        cmd = commands.Command('divide', self.adjustmentCoefficients, 'by spectrum')
        processedSpectra = cmd.process(self.rawSpectra)
        npt.assert_array_equal(processedSpectra, targetSpectra)

    def test_UndoDivisionBySpectrumCommand(self):
        targetSpectra = np.array([[1, 2, 3],
                                  [2, 2.5, 3]])
        cmd = commands.Command('divide', self.adjustmentCoefficients, 'by spectrum')
        processedSpectra = cmd.unprocess(targetSpectra)
        npt.assert_array_equal(processedSpectra, self.rawSpectra)


if __name__ == '__main__':
    unittest.main()
