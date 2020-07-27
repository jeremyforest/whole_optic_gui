

class Pyqt_debugger():
    def __init__(self):
        pass

    def debug_trace():
      '''Set a tracepoint in the Python debugger that works with Qt'''
      from PyQt5.QtCore import pyqtRemoveInputHook
      from pdb import set_trace
      pyqtRemoveInputHook()
      set_trace()
