## PyQT5
from PyQt5 import uic
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, pyqtSignal, QThreadPool, QObject, QTimer, QEventLoop
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, \
                            QMessageBox, QProgressBar, QGraphicsScene, QInputDialog, QDialog
from PyQt5.QtGui import QImage, QPixmap, QPen, QPainter
from PyQt5.QtTest import QTest
import pyqtgraph as pg
import sys

## general import
import time

## custom import
from OPTIMAQS.utils.json_functions import jsonFunctions
from OPTIMAQS.utils.signals import Signals


class LaserGui(QWidget):
    def __init__(self, info_logfile_path=None, timings_logfile_path=None):
        super(LaserGui, self).__init__()
        uic.loadUi('OPTIMAQS/view/laser/laser.ui', self)
        self.show()
        self.import_laser_model()
        self.initialize_laser_parameters()
        self.actions()
        
        self.info_logfile_path = info_logfile_path
        self.timings_logfile_path = timings_logfile_path 
        
        
        self.path = jsonFunctions.open_json('OPTIMAQS/config_files/last_experiment.json')
#        self.timings_logfile_path = self.path + '/experiment_' + self.path[-1] + '_timings.json'
        self.timings_logfile_path = timings_logfile_path
        self.timings_logfile_dict = {}
        self.timings_logfile_dict['laser'] = {}
        self.timings_logfile_dict['laser']['on'] = []
        self.timings_logfile_dict['laser']['off'] = []

        ## timings
        self.perf_counter_init = jsonFunctions.open_json('OPTIMAQS/config_files/perf_counter_init.json')


    def import_laser_model(self):
        """
        import laser model-type script
        """
        from OPTIMAQS.model.laser.laser_model import CrystalLaser
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

    def reset(self, timings_logfile_path, info_logfile_path):
        self.info_logfile_path = info_logfile_path
        self.timings_logfile_path = timings_logfile_path
        self.timings_logfile_dict = {}
        self.timings_logfile_dict['laser'] = {}
        self.timings_logfile_dict['laser']['on'] = []
        self.timings_logfile_dict['laser']['off'] = []

    def laser_on(self):
        self.laser.turn_on()
        self.timings_logfile_dict['laser']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)

    def laser_off(self):
        self.laser.turn_off()
        self.timings_logfile_dict['laser']['off'].append((time.perf_counter() - self.perf_counter_init)*1000)
        jsonFunctions.append_to_json(self.timings_logfile_dict, self.timings_logfile_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LaserGui()
    win.showMaximized()
    app.exit(app.exec_())
