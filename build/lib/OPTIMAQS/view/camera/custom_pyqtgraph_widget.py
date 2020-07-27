
"""
Pyqtgraph widget for import as a custom widget in Qt Designer

Adapted from: https://stackoverflow.com/questions/45872255/embed-a-pyqtgraph-plot-into-a-qt-ui

"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui

class Custom_pyqtgraph_widget(pg.ImageWindow):
    """
    Custom pyqtgraph widget used for the camera view
    """
    def __init__(self, parent=None, **kargs):
        pg.ImageWindow.__init__(self, **kargs)
        self.setParent(parent)
        self.setWindowTitle('camera view')

if __name__ == '__main__':
    w = Custom_pyqtgraph_widget()
    w.show()
    QtGui.QApplication.instance().exec_()
