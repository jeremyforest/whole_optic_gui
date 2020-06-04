## PyQT5
from PyQt5 import uic
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, pyqtSignal, QThreadPool,  \
                         QObject, QTimer, QEventLoop
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, \
                            QVBoxLayout, QWidget, QSlider, QFileDialog, \
                            QMessageBox, QProgressBar, QGraphicsScene, \
                            QInputDialog, QDialog
from PyQt5.QtGui import QImage, QPixmap, QPen, QPainter
from PyQt5.QtTest import QTest
import pyqtgraph as pg

## General packages
import sys
import time
import os
import json

## Custom imports
from OPTIMAQS.utils.signals import Signals
from OPTIMAQS.utils.worker import Worker
from OPTIMAQS.utils.custom_sleep_function import custom_sleep_function
from OPTIMAQS.utils.debug import Pyqt_debugger

### View model imports
from OPTIMAQS.view.camera.camera_gui import CameraGui
from OPTIMAQS.view.laser.laser_gui import LaserGui
from OPTIMAQS.view.dlp.dlp_gui import DLPGui
from OPTIMAQS.view.controller.controller_gui import ControllerGui
from OPTIMAQS.view.automation.automation_gui import AutomationGui
from OPTIMAQS.view.electrophysiology.electrophysiology_gui import ElectrophysiologyGui


class Camera(CameraGui):
    """
    Class referencing the CameraGui view
    """
    def __init__(self):
        print("loading camera module")
        self.camera_gui = CameraGui()
        self.activate_camera = True

class Laser(LaserGui):
    """
    Class referencing the Laser view
    """
    def __init__(self):
        print("loading laser module")
        self.laser_gui = LaserGui()
        self.activate_laser = True

class DLP(DLPGui):
    """
    Class referencing the DLP view
    """
    def __init__(self):
        print("loading DLP module")
        self.dlp_gui = DLPGui()
        self.activate_dlp = True

class Controller(ControllerGui):
    """
    Class referencing the Controller view
    """
    def __init__(self):
        print("loading Controller module")
        self.controller_gui = ControllerGui()
        self.activate_controller = True

class Automation(AutomationGui):
    """
    Class referencing the Automation view
    """
    def __init__(self):
        print("loading Automation module")
        self.automation_gui = AutomationGui()
        self.activate_automation = True

class Electrophysiology(ElectrophysiologyGui):
    """
    Class referencing the Electrophysiology view
    """
    def __init__(self):
        print("loading Electrophysiology module")
        self.electrophysiology_gui = ElectrophysiologyGui()
        self.activate_electrophysiology = True


class MainWindow(QMainWindow):
    """
    Main view using main_gui.py and centralising GUI functions
    """
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('OPTIMAQS/view/main.ui', self)
        self.show()
        self.menu_bar()
        self.actions()

        ## Gui activation
        self.activate_camera = False
        self.activate_laser = False
        self.activate_dlp = False
        self.activate_controller = False
        self.activate_automation = False
        self.activate_electrophysiology = False


        self.path_init = None
        self.path = None
        self.path_raw_data = None



        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())


    def menu_bar(self):
        """
        Define actions for menu bar items.
        """
        ## Menu
        self.actionQuit.triggered.connect(self.bye)
        ## Load modules
        self.actionCamera.triggered.connect(self.load_camera)
        self.actionLaser.triggered.connect(self.load_laser)
        self.actionDLP.triggered.connect(self.load_dlp)
        self.actionController.triggered.connect(self.load_controller)
        self.actionAutomation.triggered.connect(self.load_automation)
        self.actionElectrophysiology.triggered.connect(self.load_electrophysiology)

    def actions(self):
        """
        Define actions for buttons and items.
        """
        self.initialize_experiment_button.clicked.connect(self.initialize_experiment)
        self.change_folder_button.clicked.connect(self.change_folder)

    def load_camera(self):
        """
        Load the camera view
        """
        self.camera = Camera()

    def load_laser(self):
        """
        Load the laser view
        """
        self.laser = Laser()

    def load_dlp(self):
        """
        Load the dlp view
        """
        self.dlp = DLP()

    def load_controller(self):
        """
        Load the controller view
        """
        self.controller = Controller()

    def load_automation(self):
        """
        Load the automation view
        """
        self.automation = Automation()

    def load_electrophysiology(self):
        """
        Load the electrophysiology view
        """
        self.electrophysiology = Electrophysiology()

    def init_json_dict(self):
        """
        Initialize dictionaries that will populate the json files saving info
        and timings
        """
        ## initilizing dict for timings
        self.timings_logfile_dict = {}
        self.timings_logfile_dict['laser'] = {}
        self.timings_logfile_dict['laser']['on'] = []
        self.timings_logfile_dict['laser']['off'] = []
        self.timings_logfile_dict['dlp'] = {}
        self.timings_logfile_dict['dlp']['on'] = []
        self.timings_logfile_dict['dlp']['off'] = []
        self.timings_logfile_dict['camera'] = []
        self.timings_logfile_dict['camera_bis'] = []
        self.timings_logfile_dict['ephy'] = {}
        self.timings_logfile_dict['ephy']['on'] = []
        self.timings_logfile_dict['ephy']['off'] = []
        self.timings_logfile_dict['ephy_stim'] = {}
        self.timings_logfile_dict['ephy_stim']['on'] = []
        self.timings_logfile_dict['ephy_stim']['off'] = []
        ## initilizing dict for info
        self.info_logfile_dict = {}
        self.info_logfile_dict['experiment creation date'] = None
        self.info_logfile_dict['roi'] = []
        self.info_logfile_dict['exposure time'] = []
        self.info_logfile_dict['binning'] = []
        self.info_logfile_dict['fov'] = []
        self.info_logfile_dict['fps'] = []

    def change_folder(self):
        """
        Change the folder defined as self.path
        """
        self.path = QFileDialog.getExistingDirectory(None, 'Select the folder you want the path to change to:',
                                                        'C:/', QFileDialog.ShowDirsOnly)
        self.path = self.path.replace('/','\\')
        self.path_raw_data = self.path + '\\raw_data'
        self.current_folder_label_2.setText(str(self.path))

    def initialize_experiment(self):
        """
        Initialize/Reinitilize experiment logfiles and variables
        """
        ## reinitilize JSON files
        self.timings_logfile_dict = {}
        self.timings_logfile_dict['laser'] = {}
        self.timings_logfile_dict['laser']['on'] = []
        self.timings_logfile_dict['laser']['off'] = []
        self.timings_logfile_dict['dlp'] = {}
        self.timings_logfile_dict['dlp']['on'] = []
        self.timings_logfile_dict['dlp']['off'] = []
        self.timings_logfile_dict['camera'] = []
        self.timings_logfile_dict['camera_bis'] = []
        self.timings_logfile_dict['ephy'] = {}
        self.timings_logfile_dict['ephy']['on'] = []
        self.timings_logfile_dict['ephy']['off'] = []
        self.timings_logfile_dict['ephy_stim'] = {}
        self.timings_logfile_dict['ephy_stim']['on'] = []
        self.timings_logfile_dict['ephy_stim']['off'] = []

        self.info_logfile_dict = {}
        self.info_logfile_dict['experiment creation date'] = None
        self.info_logfile_dict['roi'] = []
        self.info_logfile_dict['exposure time'] = []
        self.info_logfile_dict['binning'] = []
        self.info_logfile_dict['fov'] = []
        self.info_logfile_dict['fps'] = []

        self.images = []
        self.image_list = []
        self.image_reshaped = []
        self.ephy_data = []

        ## init perf_counter for timing events
        self.perf_counter_init = time.perf_counter()

        ## generate folder to save the data
        if self.path_init == None:
            self.path_init = QFileDialog.getExistingDirectory(None, 'Select a folder where you want to store your data:',
                                                        'C:/', QFileDialog.ShowDirsOnly)
            self.path = self.path_init
        else:
            self.path = self.path_init
        print(self.path)
        self.path_raw_data = self.path + '\\raw_data'
        date = time.strftime("%Y_%m_%d")
        self.path = os.path.join(self.path, date)
        if not os.path.exists(self.path):
            os.makedirs(self.path) ## make a folder with the date of today if it does not already exists
        n = 1
        self.path_temp = os.path.join(self.path, 'experiment_' + str(n))  ## in case of multiple experiments a day, need to create several subdirectory
        while os.path.exists(self.path_temp):                             ## but necesarry to check which one aleady exists
            n += 1
            self.path_temp = os.path.join(self.path, 'experiment_' + str(n))
        self.path = self.path_temp
        self.path_raw_data = self.path + '\\raw_data'
        os.makedirs(self.path)
        os.makedirs(self.path + '\\dlp_images')
        os.makedirs(self.path + '\\raw_data')

        ## generate log files
        self.info_logfile_path = self.path + "/experiment_{}_info.json".format(n)
        experiment_time = time.asctime(time.localtime(time.time()))
        self.info_logfile_dict['experiment creation date'] = experiment_time
        with open(self.info_logfile_path,"w+") as file:       ## store basic info and comments
            json.dump(self.info_logfile_dict, file)

        self.timings_logfile_path = self.path + "/experiment_{}_timings.json".format(n)
        with open(self.timings_logfile_path, "w+") as file:
            json.dump(self.timings_logfile_dict, file)

        self.current_folder_label_2.setText(str(self.path)) ## show current directory in the GUI

    def bye(self):
        """
        Clean exit. Unloads all module and disconnect hardware components
        that were loaded
        """
        if self.activate_camera is True:
            self.cam.shutdown()
        if self.activate_laser is True:
            self.laser.disconnect()
        if self.activate_dlp is True:
            self.dlp.disconnect()
        sys.exit()

def main():
    """
    run application
    """
    app = QApplication(sys.argv)
    win = MainWindow()
    # win.showMaximized()
    app.exit(app.exec_())


if __name__ == "__main__":
        main()
