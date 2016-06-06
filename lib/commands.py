import numpy as np

class Command(object):

  def __init__(self, method, methodSpec, how):
    self.method = method

    if method == 'add':
      self.selectedMath = self.add
      self.reverseSelectedMath = self.subtract
    if method == 'subtract':
      self.selectedMath = self.subtract
      self.reverseSelectedMath = self.add
    if method == 'multiply':
      self.selectedMath = self.multiply
      self.reverseSelectedMath = self.divide
    if method == 'divide':
      self.selectedMath = self.divide
      self.reverseSelectedMath = self.multiply

    self.how = how
    self.methodSpec = methodSpec

    if how == 'by spectrum':
      self.methodSpec = self.methodSpec[:, np.newaxis]

  def add(self, targetSpec):
    return np.add(targetSpec, self.methodSpec)

  def subtract(self, targetSpec):
    return np.subtract(targetSpec, self.methodSpec)

  def multiply(self, targetSpec):
    return np.multiply(targetSpec, self.methodSpec)

  def divide(self, targetSpec):
    return np.divide(targetSpec, self.methodSpec)


  def process(self, targetSpec):
    return self.selectedMath(targetSpec)

  def unprocess(self, targetSpec):
    return self.reverseSelectedMath(targetSpec)
