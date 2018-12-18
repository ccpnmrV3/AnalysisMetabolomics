#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license",
                 "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:23 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b4 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: TJ Ragan $"
__date__ = "$Date: 2017-04-07 10:28:45 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

import numpy as np

from ccpn.AnalysisMetabolomics.lib import centering
from ccpn.AnalysisMetabolomics.lib import normalisation
from ccpn.AnalysisMetabolomics.lib import scaling


def pipeline(spectra, commands):
    osn = []
    oss = []
    osi = []
    for k, v in sorted(spectra.items()):
        osn.append(k)
        oss.append(v[0])
        osi.append(v[1])
    oss = np.asarray(oss)
    osi = np.asarray(osi)

    for command in commands:
        function = command.pop('function')
        method = command.pop('method', None)
        f = functionMap[function]
        if method is not None:
            f = f[method]
        osn, oss, osi = f(osn, oss, osi, **command)

    return {n: np.vstack((s, i)) for n, s, i in zip(osn, oss, osi)}


def _tsa(osn, oss, osi):
    return osn, oss, normalisation.tsa(np.asarray(osi))


def _pqn(osn, oss, osi):
    return osn, oss, normalisation.pqn(np.asarray(osi))


def _polyBaseLine(osn, oss, osi, controlPoints):
    print('polybaseline', controlPoints)
    return osn, oss, osi


def _alignSpectra(osn, oss, osi, targetSpectrum):
    '''
    Allowed values of targetSpectrum are '<All>' for median, or a spectrum pid.
    '''
    print('Align Spectra', targetSpectrum)
    return osn, oss, osi


def _whittakerBaseline(osn, oss, osi, a, lam, controlPoints):
    print('Whittaker Baseline Correction', a, lam, controlPoints)
    return osn, oss, osi


def _segmentalAlign(osn, oss, osi, regions):
    print('Segmental Alignment', regions)
    return osn, oss, osi


def _alignToReference(osn, oss, osi, referencePpm, window):
    print('Align to CS Reference', referencePpm, window)
    return osn, oss, osi


def _whittakerSmooth(osn, oss, osi, a, controlPoints):
    print('Whittaker Smoother', a, controlPoints)
    return osn, oss, osi


def _excludeBaselinePoints(osn, oss, osi, baselineRegion, baselineMultiplier):
    print('excludeBaselinePoints', baselineRegion, baselineMultiplier)
    return osn, oss, osi


def _bin(osn, oss, osi, binWidth):
    print('Bin', binWidth)
    return osn, oss, osi


def _paretoScale(osn, oss, osi):
    return osn, oss, scaling.paretoScale(osi)


def _unitVarianceScale(osn, oss, osi):
    return osn, oss, scaling.unitVarianceScale(np.asarray(osi))


def _refPeakNormalise(osn, oss, osi, peak):
    print('Normalise to reference peak')
    return osn, oss, osi


def _meanCentre(osn, oss, osi):
    return osn, oss, centering.meanCenter(np.asarray(osi))


def _medianCentre(osn, oss, osi):
    return osn, oss, centering.medianCenter(np.asarray(osi))


functionMap = {
    'normalise': {
        'Total Area': _tsa,
        'PQN': _pqn,
        },
    'scale': {
        'Unit Variance': _unitVarianceScale,
        'Pareto': _paretoScale,
        },
    'centre': {
        'Mean': _meanCentre,
        'Median': _medianCentre,
        },
    'Reference Peak': _refPeakNormalise,
    'polyBaseLine': _polyBaseLine,
    'alignSpectra': _alignSpectra,
    'excludeSignalFreeRegions': None,
    'whittakerBaseline': _whittakerBaseline,
    'segmentalAlign': _segmentalAlign,
    'alignToReference': _alignToReference,
    'whittakerSmooth': _whittakerSmooth,
    'excludeBaselinePoints': _excludeBaselinePoints,
    'bin': _bin,
    }
