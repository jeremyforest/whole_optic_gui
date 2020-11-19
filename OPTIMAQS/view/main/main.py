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
pg.setConfigOptions(imageAxisOrder='row-major')

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
from OPTIMAQS.utils.json_functions import jsonFunctions

### View model imports
from OPTIMAQS.view.camera.camera_gui import CameraGui
from OPTIMAQS.view.laser.laser_gui import LaserGui
from OPTIMAQS.view.dlp.dlp_gui import DLPGui
from OPTIMAQS.view.controller.controller_gui import ControllerGui
from OPTIMAQS.view.automation.automation_gui import AutomationGui
from OPTIMAQS.view.electrophysiology.electrophysiology_gui import ElectrophysiologyGui




class MainWindow(QMainWindow):
    """
    Main view using main_gui.py and centralising GUI functions
    """
    def __init__(self):
        super().__init__()
        self.main_ui = uic.loadUi('OPTIMAQS/view/main/main.ui', self)
        self.show()
        self.menu_bar()
        self.actions()

        ## Which module is turned on ?
        self.activate_camera = False
        self.activate_laser = False
        self.activate_dlp = False
        self.activate_controller = False
        self.activate_automation = False
        self.activate_electrophysiology = False

        ## Init path variables
        if jsonFunctions.find_json('OPTIMAQS/config_files/path_init.json'):
            self.path_init = self.set_main_path_from_config_file()
        else:
            self.path_init = self.set_main_path_from_user_input()

        self.path = None
        self.path_raw_data = None
        self.n_experiment = 1

        self.initialize_experiment()


    def menu_bar(self):
        """
        Define actions for menu bar items.
        """
        ## Menu
        self.actionQuit.triggered.connect(self.bye)
        self.actionInitialize_experiment.triggered.connect(self.initialize_experiment)
        ## Load modules
        self.actionCamera.triggered.connect(self.load_camera)
        self.actionLaser.triggered.connect(self.load_laser)
        self.actionDLP.triggered.connect(self.load_dlp)
        self.actionController.triggered.connect(self.load_controller)
        self.actionAutomation.triggered.connect(self.load_automation)
        self.actionElectrophysiology.triggered.connect(self.load_electrophysiology)
        ## Config
        self.actionChange_default_path.triggered.connect(self.set_main_path_from_user_input)
        ##Analysis
#        self.actionNetwork_connections.triggered.connect(self.networkConnections)

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
        print("loading camera module")
        self.camera_gui = CameraGui(path = self.path,
                                    path_raw_data = self.path_raw_data,
                                    info_logfile_path = self.info_logfile_path,
                                    timings_logfile_path = self.timings_logfile_path)
        self.camera_gui.setGeometry(100, 30, 200, 900)
        self.activate_camera = True

    def load_laser(self):
        """
        Load the laser view
        """
        print("loading laser module")
        self.laser_gui = LaserGui(info_logfile_path = self.info_logfile_path,
                                  timings_logfile_path = self.timings_logfile_path)
        self.laser_gui.setGeometry(1200, 250, 500, 100)
        self.activate_laser = True

    def load_dlp(self):
        """
        Load the dlp view
        """
        print("loading DLP module")
        self.dlp_gui = DLPGui(info_logfile_path = self.info_logfile_path,
                              timings_logfile_path = self.timings_logfile_path)
        self.dlp_gui.setGeometry(1200, 400, 500, 100)
        self.activate_dlp = True

    def load_controller(self):
        """
        Load the controller view
        """
        print("loading Controller module")
        self.controller_gui = ControllerGui()
        self.activate_controller = True

    def load_automation(self):
        """
        Load the automation view
        """
        print("loading Automation module")
        self.automation_gui = AutomationGui(info_logfile_path = self.info_logfile_path,
                                            timings_logfile_path = self.timings_logfile_path)
        self.automation_gui.setGeometry(1200, 700, 500, 100)
        self.activate_automation = True

    def load_electrophysiology(self):
        """
        Load the electrophysiology view
        """
        print("loading Electrophysiology module")
        self.electrophysiology_gui = ElectrophysiologyGui()
        self.activate_electrophysiology = True

    def init_log_dict(self):
        """
        Initialize dictionaries that will populate the json files saving info
        and timings
        """
        ## initilizing dict for timings
        self.timings_logfile_dict = {}
#        self.timings_logfile_dict['timer_init'] = {}
#        self.timings_logfile_dict['timer_init']['main'] = []
#        self.timings_logfile_dict['timer_init']['camera'] = []
#        self.timings_logfile_dict['timer_init']['dlp'] = []
#        self.timings_logfile_dict['timer_init']['laser'] = []
#        self.timings_logfile_dict['timer_init']['ephy'] = []
#        self.timings_logfile_dict['timer_init']['ephy_stim'] = [] # do I need this one ?
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

    def set_main_path_from_config_file(self):
        """
        Set the main path of the experiment from the path saved in the
        path_init config file.
        """
        return jsonFunctions.open_json('OPTIMAQS/config_files/path_init.json')

    def save_main_path_to_config_file(self):
        """
        Save the path_init variable in the path_init config file
        """
        return jsonFunctions.write_to_json(self.path_init, 'OPTIMAQS/config_files/path_init.json')

    def set_main_path_from_user_input(self):
        """
        Set the path_init variable from user input and save it in the path_init
        config file
        """
        self.path_init = QFileDialog.getExistingDirectory(None,
                                          'Select the folder you want the path to change to:',
                                          'C:/', QFileDialog.ShowDirsOnly)
        jsonFunctions.write_to_json(self.path_init, 'OPTIMAQS/config_files/path_init.json')

    def change_folder(self):
        """
        Change the folder defined as self.path
        """
        self.path = QFileDialog.getExistingDirectory(None, 'Select the folder you want the path to change to:',
                                                        'C:/', QFileDialog.ShowDirsOnly)
        self.path = self.path.replace('/','\\')
        self.path_raw_data = self.path + '\\raw_data'
        self.current_folder_label_2.setText(str(self.path))
        jsonFunctions.write_to_json(self.path, 'OPTIMAQS/config_files/last_experiment.json')


#    def initialize_experiment(self):
#        self.load_automation()
#        self.automation_gui.initialize_experiment()

    def initialize_experiment(self):
        """
        Initialize/Reinitilize experiment logfiles and variables
        """
        ## reinitilize JSON files
        self.init_log_dict()

        self.images = []
        self.image_list = []
        self.image_reshaped = []
        self.ephy_data = []
        self.run_nb = 0

        ## init perf_counter for timing events
        self.perf_counter_init = time.perf_counter()
        jsonFunctions.write_to_json(self.perf_counter_init, 
                                    'OPTIMAQS/config_files/perf_counter_init.json')

        ## generate folder to save the data
        self.path = self.path_init
        self.path_raw_data = self.path + '\\raw_data'
        date = time.strftime("%Y_%m_%d")
        self.path = os.path.join(self.path, date)
        if not os.path.exists(self.path):
            os.makedirs(self.path) ## make a folder with the date of today if it does not already exists
        self.path_temp = os.path.join(self.path, 'experiment_' + str(self.n_experiment))  ## in case of multiple experiments a day, need to create several subdirectory
        while os.path.exists(self.path_temp):                             ## but necesarry to check which one aleady exists
            self.n_experiment += 1
            self.path_temp = os.path.join(self.path, 'experiment_' + str(self.n_experiment))
        self.path = self.path_temp
        self.path_raw_data = self.path + '\\raw_data'
        os.makedirs(self.path)
        os.makedirs(self.path + '\\dlp_images')
        os.makedirs(self.path + '\\raw_data')
        jsonFunctions.write_to_json(self.path, 'OPTIMAQS/config_files/last_experiment.json')

        ## generate log files
        self.info_logfile_path = self.path + "/experiment_{}_info.json".format(self.n_experiment)
        experiment_time = time.asctime(time.localtime(time.time())) 
        self.info_logfile_dict['experiment creation date'] = experiment_time
#        with open(self.info_logfile_path,"w+") as file:       ## store basic info and comments
#            json.dump(self.info_logfile_dict, file)
        jsonFunctions.write_to_json(self.info_logfile_dict, self.info_logfile_path)

        self.timings_logfile_path = self.path + "/experiment_{}_timings.json".format(self.n_experiment)
#        with open(self.timings_logfile_path, "w+") as file:
#            json.dump(self.timings_logfile_dict, file)
        jsonFunctions.write_to_json(self.timings_logfile_dict, self.timings_logfile_path)

        self.current_folder_label_2.setText(str(self.path)) ## show current directory in the GUI
        
        
        if self.activate_automation:
            self.automation_gui.reset(self.info_logfile_path, self.timings_logfile_path,
                                      self.path)

#    def initialize_experiment(self):
#        """
#        Initialize/Reinitilize experiment logfiles and variables
#        """
#        ## reinitilize JSON files
#        self.init_log_dict()
#
#        self.images = []
#        self.image_list = []
#        self.image_reshaped = []
#        self.ephy_data = []
#
#        ## init perf_counter for timing events
#        self.perf_counter_init = time.perf_counter()
#        jsonFunctions.write_to_json(self.perf_counter_init, 'OPTIMAQS/config_files/perf_counter_init.json')
#
#        ## generate folder to save the data
#        self.path = self.path_init
#        self.path_raw_data = self.path + '\\raw_data'
#        date = time.strftime("%Y_%m_%d")
#        self.path = os.path.join(self.path, date)
#        if not os.path.exists(self.path):
#            os.makedirs(self.path) ## make a folder with the date of today if it does not already exists
#        n = 1
#        self.path_temp = os.path.join(self.path, 'experiment_' + str(n))  ## in case of multiple experiments a day, need to create several subdirectory
#        while os.path.exists(self.path_temp):                             ## but necesarry to check which one aleady exists
#            n += 1
#            self.path_temp = os.path.join(self.path, 'experiment_' + str(n))
#        self.path = self.path_temp
#        self.path_raw_data = self.path + '\\raw_data'
#        os.makedirs(self.path)
#        os.makedirs(self.path + '\\dlp_images')
#        os.makedirs(self.path + '\\raw_data')
#        jsonFunctions.write_to_json(self.path, 'OPTIMAQS/config_files/last_experiment.json')
#
#        ## generate log files
#        self.info_logfile_path = self.path + "/experiment_{}_info.json".format(n)
#        experiment_time = time.asctime(time.localtime(time.time()))
#        self.info_logfile_dict['experiment creation date'] = experiment_time
##        with open(self.info_logfile_path,"w+") as file:       ## store basic info and comments
##            json.dump(self.info_logfile_dict, file)
#        jsonFunctions.write_to_json(self.info_logfile_dict, self.info_logfile_path)
#
#        self.timings_logfile_path = self.path + "/experiment_{}_timings.json".format(n)
##        with open(self.timings_logfile_path, "w+") as file:
##            json.dump(self.timings_logfile_dict, file)
#        jsonFunctions.write_to_json(self.timings_logfile_dict, self.timings_logfile_path)
#
#        self.current_folder_label_2.setText(str(self.path)) ## show current directory in the GUI

#    def networkConnections(self):
#        """
#        Will run the merging_experiemnt script of the analysis pipeline to
#        perform averaging of neuronal network activation and see which neurons
#        are linked to the stimulated neuron(s)
#        """
#        experiment_start = QtWidgets.QInputDialog.getInt(
#                            self, 'Input Dialog',
#                            'Number of the experiment to start averaging from:')
#        experiment_end = QtWidgets.QInputDialog.getInt(
#                            self, 'Input Dialog',
#                            'Number of the experiment to end the averaging:')
#        merging = 'python merging_experiments.py'
#        convert_to_image = 'python convert_npy_to_png.py'
#        subprocess.call([merging,   f'--main_folder_path {self.path}',
#                                f'--experiments {experiment_start}',
#                                f'--experiments {experiment_end}',
#                                '--estimate_connections'])
#        subprocess.call([convert_to_image,
#                        f'experiment_merged_{experiment_start}_{experiment_end}_manual',
#                        f'{self.path}')






    def bye(self):
        """
        Clean exit. Unloads all module and disconnect hardware components
        that were loaded
        """
        if self.activate_camera is True:
            self.camera_gui.turn_off()
        if self.activate_laser is True:
            self.laser_gui.turn_off()
        if self.activate_dlp is True:
            self.dlp_gui.turn_off()
        sys.exit()


def main():
    """
    run application
    """
    app = QApplication(sys.argv)
    win = MainWindow()
    win.setGeometry(1200, 30, 500, 100)
    app.exit(app.exec_())


if __name__ == "__main__":
        main()
