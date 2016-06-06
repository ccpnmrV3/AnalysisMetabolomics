"""Module Documentation here

"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (www.ccpn.ac.uk) 2014 - : 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__credits__ = "Wayne Boucher, Rasmus H Fogh, Simon P Skinner, Geerten W Vuister"
__license__ = ("CCPN license. See www.ccpn.ac.uk/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for license text")
__reference__ = ("For publications, please use reference from www.ccpn.ac.uk/license"
                 " or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")

#=========================================================================================
# Last code modification:
#=========================================================================================
__author__ = ": rhfogh $"
__date__ = ": 2014-06-04 18:13:10 +0100 (Wed, 04 Jun 2014) $"
__version__ = ": 7686 $"

#=========================================================================================
# Start of code
#=========================================================================================

import typing

from functools import reduce
#
# class Pipeline(object):
#   def __init__(self, *args):
#     if args:
#       self._func_list=args
#     else:
#       self._func_list=[]
#
#   def __call__(self, *args, **kwargs):
#     (fargs,fkwargs) = (args,kwargs)
#     for f in self:
#       results = f(*fargs, **fkwargs)
#       if isinstance(results, tuple) and len(results) == 2 and \
#               isinstance(results[0],list) and isinstance(results[1],dict):
#         fargs,kwargs = results
#       else:
#         fargs = [results]
#         fkwargs = {}
#     return results
#
#   def __iter__(self):
#     for f in self._func_list:
#       yield f
#     raise StopIteration
#
#   def __eq__(self, other):
#     return self._func_list == other._func_list
#
#   def __add__(self, other):
#     funcs = other
#     if callable(other):
#        funcs = [other]
#     args = list(self._func_list) + list(funcs)
#     return Pipeline(*args)
#
#   def push(self, f):
#     return self._func_list.insert(0, f)
#
#   def pop(self, *args, **kwargs):
#     return self._func_list.pop(*args, **kwargs)
#
#   def append(self, *args, **kwargs):
#     return self._func_list.append(*args, **kwargs)
#
#
#
#
# def add_1(x, y):
#   return x+y
#
# def mul_2(x):
#     return (x * 2)
#
# def identity(x):
#     return x



def alignSpectra(self, inputData, **args):
  print('alignSpectra', args)

def alignToReference(self, inputData, **args):
  print('alignToReference', args)

def excludeRegions(self, inputData, **args):
  print('excludeRegions', args)

def polyBaseLine(self, inputData, **args):
  print('polyBaseLine', args)

def whittakerBaseline(self, inputData, **args):
  print('whittakerBaseline', args)

def segmentalAlign(self, inputData, **args):
  print('segmentalAlign', args)

def bin(self, inputData, **args):
  print('bin', args)

def excludeSignalFreeRegions(self, inputData, **args):
  print('excludeSignalFreeRegions', args)

def whittakerSmooth(self, inputData, **args):
  print('whittakerSmooth', args)

def excludeBaselinePoints(self, inputData, **args):
  print('excludeBaselinePoints', args)

def normalise(self, inputData, **args):
  print('normalise', args)

def autoScale(self, inputData, **args):
  print('autoScale', args)


def meanCentre(self, inputData, **args):
  print('meanCentre', args)

def scale(self, inputData, **args):
  print('scale', args)