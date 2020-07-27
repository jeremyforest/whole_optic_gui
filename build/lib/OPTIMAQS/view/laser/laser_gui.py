## PyQT5
from PyQt5 import uic
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, pyqtSignal, QThreadPool, QObject, QTimer, QEventLoop
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, \
                            QMessageBox, QProgressBar, QGraphicsScene, QInputDialog, QDialog
from PyQt5.QtGui import QImage, QPixmap, QPen, QPainter
from PyQt5.QtTest import QTest
import pyqtgraph as pg
import sys



class LaserGui(QWidget):
    def __init__(self):
        super(LaserGui, self).__init__()
        uic.loadUi('OPTIMAQS/view/laser/laser.ui', self)
        self.show()
        self.import_laser_model()
        self.initialize_laser_parameters()
        self.actions()


    def import_laser_model(self):
        """
        import laser model-type script
        """
        from model.laser.laser_control import CrystalLaser
        self.laser = CrystalLaser()
        self.laser.connect()


    def initialize_laser_parameters(self):
        """
        Initialize all the laser variables
            """
        ## custom signals
        self.laser_signal = Signals()
        self.laser_signal.start.connect(self.laser_on)
        self.laser_signal.finished.connect(self.laser_off)

    def actions(self):
        """
        Define actions for buttons and items.
        """
        self.laser_on_button.clicked.connect(self.laser_on)
        self.laser_off_button.clicked.connect(self.laser_off)

    def laser_on(self):
        self.laser.turn_on()
        self.timings_logfile_dict['laser']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)

    def laser_off(self):
        self.laser.turn_off()
        self.timings_logfile_dict['laser']['off'].append((time.perf_counter() - self.perf_counter_init)*1000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LaserGui()
    win.showMaximized()
    app.exit(app.exec_())
