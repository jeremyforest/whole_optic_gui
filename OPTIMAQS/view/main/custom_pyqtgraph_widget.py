
"""
Pyqtgraph widget for import as a custom widget in Qt Designer

Adapted from: https://stackoverflow.com/questions/45872255/embed-a-pyqtgraph-plot-into-a-qt-ui

"""

import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np


class Custom_pyqtgraph_widget(pg.ImageView):
    """
    Custom pyqtgraph widget used for the camera view
    """
    def __init__(self, parent=None, **kargs):
        super().__init__()
#        import pdb; pdb.set_trace()
        self.ui.graphicsView.setAntialiasing = False
        self.ui.graphicsView.background = 'None'
        self.ui.histogram.hide()
        self.ui.roiPlot.autoPixelRange
        



if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = Custom_pyqtgraph_widget()
    w.show()
    QtGui.QApplication.instance().exec_()
