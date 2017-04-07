#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan"
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Ed Brooksbank $"
__dateModified__ = "$dateModified: 2017-04-07 11:41:24 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: TJ Ragan $"
__date__ = "$Date: 2017-04-07 10:28:45 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
from __future__ import unicode_literals, print_function, absolute_import, division


import unittest
import numpy as np
import numpy.testing as npt

from ccpn.AnalysisMetabolomics.lib import commands


class MyTestCase( unittest.TestCase ):
  def setUp(self):
    self.rawSpectra = np.array([[1,2,3],
                                [4,5,6]])

    self.adjustmentSpectrum = np.array([1,2,3])
    self.adjustmentCoefficients = np.array([1,2])


  def test_AdditionByFrequencyCommand( self ):
    targetSpectra = np.array([[2,4,6],
                              [5,7,9]])
    cmd = commands.Command('add', self.adjustmentSpectrum, 'by frequency')
    processedSpectra = cmd.process(self.rawSpectra)
    npt.assert_array_equal(processedSpectra, targetSpectra)

  def test_UndoAdditionByFrequencyCommand( self ):
    targetSpectra = np.array([[2,4,6],
                              [5,7,9]])
    cmd = commands.Command('add', self.adjustmentSpectrum, 'by frequency')
    processedSpectra = cmd.unprocess(targetSpectra)
    npt.assert_array_equal(processedSpectra, self.rawSpectra)

  def test_AdditionBySpectrumCommand( self ):
    targetSpectra = np.array([[2,3,4],
                              [6,7,8]])
    cmd = commands.Command('add', self.adjustmentCoefficients, 'by spectrum')
    processedSpectra = cmd.process(self.rawSpectra)
    npt.assert_array_equal(processedSpectra, targetSpectra)

  def test_UndoAdditionBySpectrumCommand( self ):
    targetSpectra = np.array([[2,3,4],
                              [6,7,8]])
    cmd = commands.Command('add', self.adjustmentCoefficients, 'by spectrum')
    processedSpectra = cmd.unprocess(targetSpectra)
    npt.assert_array_equal(processedSpectra, self.rawSpectra)


  def test_SubtractionByFrequencyCommand( self ):
    targetSpectra = np.array([[0,0,0],
                              [3,3,3]])
    cmd = commands.Command('subtract', self.adjustmentSpectrum, 'by frequency')
    processedSpectra = cmd.process(self.rawSpectra)
    npt.assert_array_equal(processedSpectra, targetSpectra)

  def test_UndoSubtractionByFrequencyCommand( self ):
    targetSpectra = np.array([[0,0,0],
                              [3,3,3]])
    cmd = commands.Command('subtract', self.adjustmentSpectrum, 'by frequency')
    processedSpectra = cmd.unprocess(targetSpectra)
    npt.assert_array_equal(processedSpectra, self.rawSpectra)

  def test_SubtractionBySpectrumCommand( self ):
    targetSpectra = np.array([[0,1,2],
                              [2,3,4]])
    cmd = commands.Command('subtract', self.adjustmentCoefficients, 'by spectrum')
    processedSpectra = cmd.process(self.rawSpectra)
    npt.assert_array_equal(processedSpectra, targetSpectra)

  def test_UndoSubtractionBySpectrumCommand( self ):
    targetSpectra = np.array([[0,1,2],
                              [2,3,4]])
    cmd = commands.Command('subtract', self.adjustmentCoefficients, 'by spectrum')
    processedSpectra = cmd.unprocess(targetSpectra)
    npt.assert_array_equal(processedSpectra, self.rawSpectra)


  def test_MultiplicationByFrequencyCommand( self ):
    targetSpectra = np.array([[1, 4, 9],
                              [4,10,18]])
    cmd = commands.Command('multiply', self.adjustmentSpectrum, 'by frequency')
    processedSpectra = cmd.process(self.rawSpectra)
    npt.assert_array_equal(processedSpectra, targetSpectra)

  def test_UndoMultiplicationByFrequencyCommand( self ):
    targetSpectra = np.array([[1, 4, 9],
                              [4,10,18]])
    cmd = commands.Command('multiply', self.adjustmentSpectrum, 'by frequency')
    processedSpectra = cmd.unprocess(targetSpectra)
    npt.assert_array_equal(processedSpectra, self.rawSpectra)

  def test_MultiplicationBySpectrumCommand( self ):
    targetSpectra = np.array([[1, 2, 3],
                              [8,10,12]])
    cmd = commands.Command('multiply', self.adjustmentCoefficients, 'by spectrum')
    processedSpectra = cmd.process(self.rawSpectra)
    npt.assert_array_equal(processedSpectra, targetSpectra)

  def test_UndoMultiplicationBySpectrumCommand( self ):
    targetSpectra = np.array([[1, 2, 3],
                              [8,10,12]])
    cmd = commands.Command('multiply', self.adjustmentCoefficients, 'by spectrum')
    processedSpectra = cmd.unprocess(targetSpectra)
    npt.assert_array_equal(processedSpectra, self.rawSpectra)


  def test_DivisionByFrequencyCommand( self ):
    targetSpectra = np.array([[1,1  ,1],
                              [4,2.5,2]])
    cmd = commands.Command('divide', self.adjustmentSpectrum, 'by frequency')
    processedSpectra = cmd.process(self.rawSpectra)
    npt.assert_array_equal(processedSpectra, targetSpectra)

  def test_UndoDivisionByFrequencyCommand( self ):
    targetSpectra = np.array([[1,1  ,1],
                              [4,2.5,2]])
    cmd = commands.Command('divide', self.adjustmentSpectrum, 'by frequency')
    processedSpectra = cmd.unprocess(targetSpectra)
    npt.assert_array_equal(processedSpectra, self.rawSpectra)

  def test_DivisionBySpectrumCommand( self ):
    targetSpectra = np.array([[1,2  ,3],
                              [2,2.5,3]])
    cmd = commands.Command('divide', self.adjustmentCoefficients, 'by spectrum')
    processedSpectra = cmd.process(self.rawSpectra)
    npt.assert_array_equal(processedSpectra, targetSpectra)

  def test_UndoDivisionBySpectrumCommand( self ):
    targetSpectra = np.array([[1,2  ,3],
                              [2,2.5,3]])
    cmd = commands.Command('divide', self.adjustmentCoefficients, 'by spectrum')
    processedSpectra = cmd.unprocess(targetSpectra)
    npt.assert_array_equal(processedSpectra, self.rawSpectra)

if __name__ == '__main__':
  unittest.main( )
