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

## General packages
import sys
import time
import json
import os

## Custome imports
from OPTIMAQS.utils.signals import Signals
from OPTIMAQS.utils.worker import Worker
from OPTIMAQS.utils.custom_sleep_function import custom_sleep_function
from OPTIMAQS.utils.json_functions import jsonFunctions

### View model imports
from OPTIMAQS.view.camera.camera_gui import CameraGui
from OPTIMAQS.view.dlp.dlp_gui import DLPGui
from OPTIMAQS.view.laser.laser_gui import LaserGui
from OPTIMAQS.view.controller.controller_gui import ControllerGui
from OPTIMAQS.view.electrophysiology.electrophysiology_gui import ElectrophysiologyGui




class AutomationGui(QWidget):
    def __init__(self):
        super(AutomationGui, self).__init__()
        self.automation_ui = uic.loadUi('OPTIMAQS/view/automation/automation.ui', self)
        self.automation_ui.show()
        
        self.actions()
        self.threadpool = QThreadPool()
        
        self.path = jsonFunctions.open_json('OPTIMAQS/config_files/path_init.json')
        self.path_experiment = jsonFunctions.open_json('OPTIMAQS/config_files/last_experiment.json')

        ## can there be a better way than having automation on top of main ?
        self.dlp_gui = DLPGui()
        self.dlp_gui.setGeometry(1200, 400, 500, 100)
        self.camera_gui = CameraGui()
        self.camera_gui.setGeometry(100, 30, 200, 900)
        self.laser_gui = LaserGui()
        self.laser_gui.setGeometry(1200, 250, 500, 100)
#        self.controller_gui = ControllerGui
#        self.electrophysiology_gui = ElectrophysiologyGui()

        ## Init path variables
        if jsonFunctions.find_json('OPTIMAQS/config_files/path_init.json'):
            self.path_init = self.set_main_path_from_config_file()
        else:   
            self.path_init = self.set_main_path_from_user_input()
            
        self.path = None
        self.path_raw_data = None


    def set_main_path_from_config_file(self):
        """
        Set the main path of the experiment from the path saved in the 
        path_init config file. 
        """
        return jsonFunctions.open_json('OPTIMAQS/config_files/path_init.json')


    def actions(self):
        """
        Define actions for buttons and items.
        """
        self.export_experiment_button.clicked.connect(self.export_experiment)
        self.load_experiment_button.clicked.connect(self.load_experiment)
        self.run_experiment_dlp_static_button.clicked.connect(self.run_experiment_dlp_static_image)
        self.run_experiment_dlp_hdmi_button.clicked.connect(self.run_experiment_dlp_hdmi)
        self.end_experiment_function = Signals()
        self.end_experiment_function.finished.connect(self.end_experiment)



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

        ## init perf_counter for timing events
        self.perf_counter_init = time.perf_counter()
        jsonFunctions.write_to_json(self.perf_counter_init, 'OPTIMAQS/config_files/perf_counter_init.json')

        ## generate folder to save the data
        self.path = self.path_init
        self.path_raw_data = self.path + '\\raw_data'
        date = time.strftime("%Y_%m_%d")
        self.path = os.path.join(self.path, date)
        if not os.path.exists(self.path):
            os.makedirs(self.path) ## make a folder with the date of today if it does not already exists
        n = 1
        self.path_temp = os.path.join(self.path, 'experiment_' + str(n))  ## in case of multiple experiments a day, need to create several subdirectory
        while os.path.exists(self.path_temp):                             ## but necesarry to check which one aleady exists
            n += 1
            self.path_temp = os.path.join(self.path, 'experiment_' + str(n))
        self.path = self.path_temp
        self.path_raw_data = self.path + '\\raw_data'
        os.makedirs(self.path)
        os.makedirs(self.path + '\\dlp_images')
        os.makedirs(self.path + '\\raw_data')
        jsonFunctions.write_to_json(self.path, 'OPTIMAQS/config_files/last_experiment.json')

        ## generate log files
        self.info_logfile_path = self.path + "/experiment_{}_info.json".format(n)
        experiment_time = time.asctime(time.localtime(time.time())) 
        self.info_logfile_dict['experiment creation date'] = experiment_time
#        with open(self.info_logfile_path,"w+") as file:       ## store basic info and comments
#            json.dump(self.info_logfile_dict, file)
        jsonFunctions.write_to_json(self.info_logfile_dict, self.info_logfile_path)

        self.timings_logfile_path = self.path + "/experiment_{}_timings.json".format(n)
#        with open(self.timings_logfile_path, "w+") as file:
#            json.dump(self.timings_logfile_dict, file)
        jsonFunctions.write_to_json(self.timings_logfile_dict, self.timings_logfile_path)

        # self.current_folder_label_2.setText(str(self.path)) ## show current directory in the GUI  # this doesn't work here but works in main

    def init_log_dict(self):
        """
        Initialize dictionaries that will populate the json files saving info
        and timings
        """
        ## initilizing dict for timings
        self.timings_logfile_dict = {}
        self.timings_logfile_dict['timer_init'] = {}
        self.timings_logfile_dict['timer_init']['main'] = []
        self.timings_logfile_dict['timer_init']['camera'] = []
        self.timings_logfile_dict['timer_init']['dlp'] = []
        self.timings_logfile_dict['timer_init']['laser'] = []
        self.timings_logfile_dict['timer_init']['ephy'] = []
        self.timings_logfile_dict['timer_init']['ephy_stim'] = [] # do I need this one ?
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

    def dlp_static_image(self):
        ## getting values from automation gui
        mode_index = 0 ## refer to mode_index of the function selection for the dlp
        # print(str(self.dlp_mode_comboBox.currentText())) # this doesn't work here but works in main
        dlp_on = int(self.dlp_time_on_lineEdit.text())
        dlp_off = int(self.dlp_time_off_lineEdit.text())
        dlp_interval = int(self.intervalle_between_sequences_lineEdit.text())
        dlp_sequence = int(self.number_of_sequence_lineEdit.text())
        dlp_repeat_sequence = int(self.number_sequence_repetition_lineEdit.text())

        ## lauching auto protocol
        for i in range(dlp_repeat_sequence):
            for j in range(dlp_sequence):
                self.laser_gui.laser_on()
                custom_sleep_function(1000)
#                if self.electrophysiology_gui.record_electrophysiological_trace_radioButton.isChecked():
#                    self.electrophysiology_gui.ephy_stim_start()
                ## ON
                self.dlp_gui.display_mode(0) ## static image
                self.dlp_gui.choose_action(2) ## display_image 
#                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
                custom_sleep_function(dlp_on)
#                if self.record_electrophysiological_trace_radioButton.isChecked():
#                    self.ephy_stim_end()
                self.dlp_gui.turn_dlp_off()
#                self.timings_logfile_dict['dlp']['off'].append((time.perf_counter() - self.perf_counter_init)*1000)
                custom_sleep_function(dlp_off)
                self.laser_gui.laser_off()
            custom_sleep_function(dlp_interval)
        self.camera_gui.camera_signal.finished.emit()
#        self.ephy_signal.finished.emit()
        self.dlp_gui.dlp_signal.finished.emit()
#        self.end_experiment_function.finished.emit()

    def dlp_static_image_repetition(self):
        experiment_repetition = int(self.experiment_repetition_lineEdit.text())
        for repeat in range(experiment_repetition):
            print(f"experiment repetition number {repeat}")
            self.run_experiment_dlp_static_image()

    def run_experiment_dlp_static_image(self):
        self.initialize_experiment()
        dlp_worker = Worker(self.dlp_static_image)
#        ephy_worker = Worker(self.ephy_recording_thread)
        self.camera_gui.stream()
        custom_sleep_function(2000)
        self.threadpool.start(dlp_worker)  ## in those experiment the dlp function drives the camera and laser stops
        self.recording = True
        self.ephy_data = []
#        if self.record_electrophysiological_trace_radioButton.isChecked():
#            self.recording = True
#            self.threadpool.start(ephy_worker)
#
#            while not self.end_expe:
#                time.sleep(1)
#                QApplication.processEvents()


    def dlp_hdmi(self):
        ## getting value from automation gui
        start_video_sequence = int(self.dlp_start_video_sequence_lineEdit.text())
        
        ## launching auto protocol
        # self.laser_on()
        custom_sleep_function(1000)
        ## ON
        self.dlp_gui.display_mode(2)
        self.dlp_gui.choose_action(1)
        custom_sleep_function(2000) #TODO: estimate length of video instead
        ## OFF
        self.dlp_gui.turn_dlp_off()
        ## DELAY
        custom_sleep_function(delay_between_repetition)
        self.camera_gui.camera_signal.finished.emit()
        self.dlp_gui.dlp_signal.finished.emit()

    def dlp_hdmi_repetition(self):
        number_of_repetition = int(self.number_of_repetition_lineEdit.text())
        delay_between_repetition = int(self.delay_between_repetition_lineEdit.text())
        for i in range(number_of_repetition):
            self.dlp_hdmi()
            
    def run_experiment_dlp_hdmi(self):
        dlp_worker = Worker(self.dlp_hdmi)
        self.camera_gui.stream()
        custom_sleep_function(2000)
        self.threadpool.start(dlp_worker)  
        self.recording = True
        
    def export_experiment(self):
        self.info_logfile_dict['roi'].append(self.roi_list)
        self.info_logfile_dict['exposure time'].append(self.exposure_time_value.value())
        self.info_logfile_dict['binning'].append(self.bin_size)
        self.info_logfile_dict['fps'].append(self.internal_frame_rate)
        self.info_logfile_dict['fov'].append((self.x_init, self.x_dim, self.y_init, self.y_dim))
        jsonFunctions.write_to_json(self.info_logfile_dict, self.info_logfile_path)
#        with open(self.info_logfile_path, "w") as file:
#            file.write(json.dumps(self.info_logfile_dict, default=lambda x:list(x), indent=4, sort_keys=True))

    def load_experiment(self):
        ## experiment json file
        self.path = QFileDialog.getExistingDirectory(None, 'Experiment folder:',
                                                        'C:/', QFileDialog.ShowDirsOnly)[0]
        experiment_path = QFileDialog.getOpenFileName(self, 'Select Experiment file',
                                                        'C:/',"Experiment file (*.json)")[0]
        # experiment_path = '/media/jeremy/Data/Data_Jeremy/2019_10_29/experiment_1/experiment_1_info.json'
        ## load/write camera related stuff
#        with open(experiment_path) as file:
#            self.info_logfile_dict = dict(json.load(file))
        self.info_logfile_dict = jsonFunctions.open_json(self.path)
        self.roi_list = self.info_logfile_dict['roi'][0]
        self.cam.write_exposure(self.info_logfile_dict['exposure time'][0])
        self.cam.write_binning(self.info_logfile_dict['binning'][0])
        self.cam.write_subarray_mode(2)
        self.x_init = self.info_logfile_dict['fov'][0][0]
        self.x_dim = self.info_logfile_dict['fov'][0][1]
        self.y_init = self.info_logfile_dict['fov'][0][2]
        self.y_dim = self.info_logfile_dict['fov'][0][3]
        self.cam.write_subarray_size(self.x_init, self.x_dim, self.y_init, self.y_dim)


    def end_experiment(self):
        print('end experiment signal received')
        self.end_expe = True



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AutomationGui()
    win.showMaximized()
    app.exit(app.exec_())
