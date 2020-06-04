## PyQT5
from PyQt5 import uic
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, pyqtSignal, QThreadPool, QObject, QTimer, QEventLoop
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, \
                            QMessageBox, QProgressBar, QGraphicsScene, QInputDialog, QDialog
from PyQt5.QtGui import QImage, QPixmap, QPen, QPainter
from PyQt5.QtTest import QTest
import pyqtgraph as pg
import sys

from OPTIMAQS.utils.signals import Signals


class AutomationGui(QWidget):
    def __init__(self):
        super(AutomationGui, self).__init__()
        uic.loadUi('OPTIMAQS/view/automation/automation.ui', self)
        self.show()
        self.actions()


    def actions(self):
        """
        Define actions for buttons and items.
        """
        self.export_experiment_button.clicked.connect(self.export_experiment)
        self.load_experiment_button.clicked.connect(self.load_experiment)
        self.run_experiment_button.clicked.connect(self.run_experiment)
        self.end_experiment_function = Signals()
        self.end_experiment_function.finished.connect(self.end_experiment)


    def dlp_auto_control(self):
        ## getting value from gui
        if str(self.dlp_mode_comboBox.currentText()) == 'Static image':
            mode_index = 0 ## refer to mode_index of the function selection for the tlp
        elif str(self.dlp_mode_comboBox.currentText()) == 'HDMI video':
            mode_index = 2
        elif str(self.dlp_mode_comboBox.currentText()) == 'Pattern Sequence':
            mode_index = 3
        print(str(self.dlp_mode_comboBox.currentText()))
        dlp_on = int(self.dlp_time_on_lineEdit.text())
        dlp_off = int(self.dlp_time_off_lineEdit.text())
        dlp_interval = int(self.intervalle_between_sequences_lineEdit.text())
        dlp_sequence = int(self.number_of_sequence_lineEdit.text())
        dlp_repeat_sequence = int(self.number_sequence_repetition_lineEdit.text())

        ## lauching auto protocol
        for i in range(dlp_repeat_sequence):
            for j in range(dlp_sequence):
                self.laser_on()
                custom_sleep_function(1000)
                if self.record_electrophysiological_trace_radioButton.isChecked():
                    self.ephy_stim_start()
                ## ON
                self.display_mode(mode_index)
                if mode_index == 0: ## static image
                    action_index = 2  ## display_image is index 2
                    self.choose_action(action_index)
                if mode_index == 2:  ## hdmi video input
                    action_index = 1 ## display hdmi video sequence is index 1
                    self.choose_action(action_index)
                if mode_index == 3: ## pattern sequence display
                    action_index = 1 ## display pattern sequence is index 1
                    self.choose_action(action_index)
#                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
                custom_sleep_function(dlp_on)
                if self.record_electrophysiological_trace_radioButton.isChecked():
                    self.ephy_stim_end()
                self.turn_dlp_off()
#                self.timings_logfile_dict['dlp']['off'].append((time.perf_counter() - self.perf_counter_init)*1000)
                custom_sleep_function(dlp_off)
            self.laser_off()
            custom_sleep_function(dlp_interval)
        self.camera_signal.finished.emit()
        self.ephy_signal.finished.emit()
        self.dlp_signal.finished.emit()
        self.end_experiment_function.finished.emit()

    def export_experiment(self):
        self.info_logfile_dict['roi'].append(self.roi_list)
        self.info_logfile_dict['exposure time'].append(self.exposure_time_value.value())
        self.info_logfile_dict['binning'].append(self.bin_size)
        self.info_logfile_dict['fps'].append(self.internal_frame_rate)
        self.info_logfile_dict['fov'].append((self.x_init, self.x_dim, self.y_init, self.y_dim))
        with open(self.info_logfile_path, "w") as file:
            file.write(json.dumps(self.info_logfile_dict, default=lambda x:list(x), indent=4, sort_keys=True))

    def load_experiment(self):
        ## experiment json file
        self.path = QFileDialog.getExistingDirectory(None, 'Experiment folder:',
                                                        'C:/', QFileDialog.ShowDirsOnly)[0]
        experiment_path = QFileDialog.getOpenFileName(self, 'Select Experiment file',
                                                        'C:/',"Experiment file (*.json)")[0]
        # experiment_path = '/media/jeremy/Data/Data_Jeremy/2019_10_29/experiment_1/experiment_1_info.json'
        ## load/write camera related stuff
        with open(experiment_path) as file:
            self.info_logfile_dict = dict(json.load(file))
        self.roi_list = self.info_logfile_dict['roi'][0]
        self.cam.write_exposure(self.info_logfile_dict['exposure time'][0])
        self.cam.write_binning(self.info_logfile_dict['binning'][0])
        self.cam.write_subarray_mode(2)
        self.x_init = self.info_logfile_dict['fov'][0][0]
        self.x_dim = self.info_logfile_dict['fov'][0][1]
        self.y_init = self.info_logfile_dict['fov'][0][2]
        self.y_dim = self.info_logfile_dict['fov'][0][3]
        self.cam.write_subarray_size(self.x_init, self.x_dim, self.y_init, self.y_dim)

    def run_experiment(self):
#        experiment_repetition = int(self.experiment_repetition_lineEdit.text())
#        for repeat in range(experiment_repetition):
#            print(f"experiment repetition number {repeat}")
        self.initialize_experiment()
        dlp_worker = Worker(self.dlp_auto_control)
        ephy_worker = Worker(self.ephy_recording_thread)
        self.stream()
        custom_sleep_function(2000)
        self.threadpool.start(dlp_worker)  ## in those experiment the dlp function drives the camera and laser stops
        self.recording = True
        self.ephy_data = []
        if self.record_electrophysiological_trace_radioButton.isChecked():
            self.recording = True
            self.threadpool.start(ephy_worker)
#
#            while not self.end_expe:
#                time.sleep(1)
#                QApplication.processEvents()

    def end_experiment(self):
        print('end experiment signal received')
        self.end_expe = True



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AutomationGui()
    win.showMaximized()
    app.exit(app.exec_())
