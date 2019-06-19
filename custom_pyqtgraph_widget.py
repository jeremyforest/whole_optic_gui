
"""
Pyqtgraph widget for import as a custom widget in Qt Designer

Adapted fro0m: https://stackoverflow.com/questions/45872255/embed-a-pyqtgraph-plot-into-a-qt-ui

"""


import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

class Custom_pyqtgraph_widget(pg.ImageWindow):
    def __init__(self, parent=None, **kargs):
        pg.ImageWindow.__init__(self, **kargs)
        self.setParent(parent)
        self.setWindowTitle('camera view')

        # self.image = np.random.rand(256, 256)

if __name__ == '__main__':
    w = Custom_pyqtgraph_widget()
    w.show()
    QtGui.QApplication.instance().exec_()
