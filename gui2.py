## PyQT5
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, pyqtSignal, QThreadPool, QObject, QTimer, QEventLoop
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, QMessageBox, QProgressBar, QGraphicsScene, QInputDialog
from PyQt5.QtGui import QImage, QPixmap, QPen, QPainter
from PyQt5.QtTest import QTest
import pyqtgraph as pg

## QTDesigner
from whole_optic_gui import Ui_MainWindow

## common dependencies
import argparse
import numpy as np
import math
import time
import os
import sys
from PIL import Image, ImageDraw, ImageOps
import cv2
import matplotlib.pyplot as plt
import json
from datetime import datetime, timezone
from multiprocessing import Process
import traceback
import subprocess
import PyDAQmx

def debug_trace():
  '''Set a tracepoint in the Python debugger that works with Qt'''
  from PyQt5.QtCore import pyqtRemoveInputHook
  from pdb import set_trace
  pyqtRemoveInputHook()
  set_trace()


class Signals(QObject):
    '''
    Adapted from https://www.learnpyqt.com/courses/concurrent-execution/multithreading-pyqt-applications-qthreadpool/
    Defines the signals available.
    Supported signals are:
    finished
        No data
    error
        `tuple` (exctype, value, traceback.format_exc() )
    result
        `object` data returned from processing, anything
    '''
    start = pyqtSignal()
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

class Worker(QRunnable):
    '''
    From https://www.learnpyqt.com/courses/concurrent-execution/multithreading-pyqt-applications-qthreadpool/
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = Signals()

        # Add the callback to our kwargs
        #self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

def custom_sleep_function(ms):
    c = time.perf_counter()
    while (time.perf_counter() - c)*1000 < ms:
        QApplication.processEvents()   #### this should probably be put in its own thread to avoid forcing gui update
#        pass
    return (time.perf_counter() - c)*1000

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.retranslateUi(self)

        ## gui initialization ##
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        ## commande-line options ##
        self.activate_camera = False
        self.activate_laser = False
        self.activate_dlp = False
        self.activate_controller = False
        self.activate_electrophysiology = False

        parser = argparse.ArgumentParser(description="hardware to load")
        parser.add_argument("--camera", default=False, action="store_true" , help="to load the camera functions")
        parser.add_argument("--laser", default=False, action="store_true" , help="to load the laser functions")
        parser.add_argument("--dlp", default=False, action="store_true" , help="to load the dlp functions")
        parser.add_argument("--controler", default=False, action="store_true" , help="to load the controller functions")
        parser.add_argument("--ephy", default=False, action="store_true", help="to load the bridge and voltage clamp amplifier")
        args = parser.parse_args()

        if args.camera is True:
            self.activate_camera = True
        else:
             print("camera functions are not loaded")

        if args.laser is True:
            self.activate_laser = True
        else:
             print("laser functions are not loaded")

        if args.dlp is True:
            self.activate_dlp = True
        else:
             print("dlp functions are not loaded")

        if args.controler is True:
            self.activate_controller = True
        else:
             print("controler functions are not loaded")

        if args.ephy is True:
            self.activate_electrophysiology = True
        else:
            print("bridge functions are not loaded")

        ##### camera #####
        if self.activate_camera is True:
            from camera.camera_control import MainCamera
            self.cam = MainCamera()
            ## initialize camera parameters
            ## fov
            self.x_dim = self.cam.get_subarray_size()[1]
            self.x_init = self.cam.get_subarray_size()[0]
            self.y_dim = self.cam.get_subarray_size()[3]
            self.y_init = self.cam.get_subarray_size()[2]
            self.subarray_label.setText(str(self.cam.get_subarray_size()))
            ## binning
            self.bin_size = self.cam.read_binning()
            self.current_binning_size_label_2.setText(str(self.cam.read_binning()))
            ## counters initialization (exposure time and fps)
            self.exposure_time_value.display(self.cam.read_exposure())
            self.internal_frame_rate = self.cam.get_internal_frame_rate()
            self.internal_frame_rate_label.setText(str(self.internal_frame_rate))
            ## set property as wanted
            self.cam.hcam.setPropertyValue('defect_correct_mode', 1)  ## necessary ?
            print(self.cam.hcam.getPropertyValue('defect_correct_mode'))
            self.cam.hcam.setPropertyValue('hot_pixel_correct_level', 2)   ## necessary ?
            print(self.cam.hcam.getPropertyValue('hot_pixel_correct_level'))
            ## custom signals
            self.camera_signal = Signals()
            self.camera_signal.start.connect(self.stream)
            self.camera_signal.finished.connect(self.stop_stream)
        ##### dlp #####
        if self.activate_dlp is True:
            from dlp.dlp_control import Dlp
            self.dlp = Dlp()
            self.dlp.connect()
            ## custom signals
            self.dlp_signal = Signals()
            self.dlp_signal.finished.connect(self.turn_dlp_off)
        ##### laser #####
        if self.activate_laser is True:
            from laser.laser_control import CrystalLaser
            self.laser = CrystalLaser()
            self.laser.connect()
            ## custom signals
            self.laser_signal = Signals()
            self.laser_signal.start.connect(self.laser_on)
            self.laser_signal.finished.connect(self.laser_off)
        ##### manipulator #####
        if self.activate_controller is True:
            from controler.manipulator_command import Controler
            self.controler = Controler()
        ##### electrophysiology #####
        if self.activate_electrophysiology is True:
            import PyDAQmx
            self.ephy_signal = Signals()
            self.ephy_signal.start.connect(self.start_recording)
            self.ephy_signal.finished.connect(self.stop_recording)
            self.recording = False
            self.ephy_graph = False
            

        ## variable reference for later use
        self.path_init = None
        self.path = None
        self.path_raw_data = None
        self.save_images = False
        self.simulated = False
        self.roi_list = []
        self.camera_to_dlp_matrix = []
        self.camera_distortion_matrix = []
        self.dlp_image_path = []
        self.calibration_dlp_camera_matrix_path = 'dlp\\calibration_matrix.json'
        ## load calibration matrix
        self.calibration()
        self.images = []
        self.image_list = []
        self.image_reshaped = []
        self.ephy_data = []
        self.end_expe = False
        self.channel_number=[2,6,10,14,16,18,20,22]
        self.sampling_rate=1000

        ## folder widget (top left)
        self.initialize_experiment_button.clicked.connect(self.initialize_experiment)
        self.change_folder_button.clicked.connect(self.change_folder)

        ## initilizing JSON files
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
        
        self.times_bis = []

        ## camera widget
        self.snap_image_button.clicked.connect(self.snap_image)
        self.stream_button.clicked.connect(self.stream)
        self.replay_button.clicked.connect(self.replay)
        self.exposure_time_bar.valueChanged.connect(self.exposure_time)
        self.binning_combo_box.activated.connect(self.binning)
        self.subArray_mode_radioButton.toggled.connect(self.subarray)
        self.update_internal_frame_rate_button.clicked.connect(self.update_internal_frame_rate)
        self.stop_stream_button.clicked.connect(self.stop_stream)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)

        ## roi
        self.save_ROI_button.clicked.connect(self.roi)
        self.reset_ROI_button.clicked.connect(self.reset_roi)
        self.saved_ROI_image.ui.histogram.hide()
        self.saved_ROI_image.ui.roiBtn.hide()
        self.saved_ROI_image.ui.menuBtn.hide()
        self.export_ROI_button.clicked.connect(self.export_roi)

        ## dlp widget
        self.display_mode_combobox.activated.connect(self.display_mode)
        self.display_mode_subbox_combobox.activated.connect(self.choose_action)
        self.calibration_button.clicked.connect(self.calibration)

        ## laser widget
        self.laser_on_button.clicked.connect(self.laser_on)
        self.laser_off_button.clicked.connect(self.laser_off)

        ## scope widget
        self.x_axis_left_button.clicked.connect(self.left)
        self.x_axis_right_button.clicked.connect(self.right)
        self.y_axis_backward_button.clicked.connect(self.backward)
        self.y_axis_forward_button.clicked.connect(self.forward)
        self.z_axis_up.clicked.connect(self.up)
        self.z_axis_down.clicked.connect(self.down)
        self.stop_mouvment_button.clicked.connect(self.stop_mouvment)

        ## menu bar connection
        self.actionQuit.triggered.connect(self.bye)

        ## automation
        self.export_experiment_button.clicked.connect(self.export_experiment)
        self.load_experiment_button.clicked.connect(self.load_experiment)
        self.run_experiment_button.clicked.connect(self.run_experiment)
        self.end_experiment_function = Signals()
        self.end_experiment_function.finished.connect(self.end_experiment)

        ## electrophysiology
        self.record_trace_button.clicked.connect(self.init_voltage)
        self.display_trace_button.clicked.connect(self.graph_voltage)
        self.stimulation_button.clicked.connect(self.ephy_stim)
        self.close_graph_button.clicked.connect(self.close_graph_windows)


    ####################################
    ###### thread utils functions ######
    ####################################
    def progress_fn(self, n):
        print("%d%% done" % n)

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("Thread Completed!")

    def print_test(self):
        print('testing_signals')

    ###################################
    ########## GUI code ###############
    ###################################

    def change_folder(self):
        self.path = QFileDialog.getExistingDirectory(None, 'Select the folder you want the path to change to:',
                                                        'C:/', QFileDialog.ShowDirsOnly)
        self.path = self.path.replace('/','\\')
        self.path_raw_data = self.path + '\\raw_data'
        self.current_folder_label_2.setText(str(self.path))

    def initialize_experiment(self):
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

    def save_as_png(self, array, image_name):
        plt.imsave('{}{}.png'.format(self.path, image_name), array, cmap='gray')

    def snap_image(self): ## only takes an image and saves it
        self.cam.start_acquisition()
        for i in range(1):
            self.images, self.times = self.cam.get_images()
            while self.images == []:
                self.images, self.times = self.cam.get_images() ## break the function if no image (due to the lauching time of the camera)
            self.cam.end_acquisition()
            self.image = self.images[0]
            self.image_reshaped = self.image.reshape(int(self.y_dim/self.bin_size),
                                                    int(self.x_dim/self.bin_size))
            self.graphicsView.setImage(self.image_reshaped)
            image_name = QInputDialog.getText(self, 'Input Dialog', 'File name:')
            self.save_as_png(self.image_reshaped, image_name)

    def stream(self):
         self.timings_logfile_dict['camera'] = []
         self.timings_logfile_dict['camera_bis'] = []
         image_processing_worker = Worker(self.processing_images)
         image_processing_worker.signals.result.connect(self.print_output)
         image_processing_worker.signals.finished.connect(self.thread_complete)
         self.threadpool.start(image_processing_worker)
         self.timer.start(10)

    def stop_stream(self):
        print('camera end signal received')
        self.acquire_images = False

    def processing_images(self):
        self.acquire_images = True
        self.cam.start_acquisition()
        image_acquired = 0
        self.timings_logfile_dict['camera_bis'].append(datetime.now().timestamp())
        self.timings_logfile_dict['camera_bis'].append((time.perf_counter() - self.perf_counter_init)*1000)
#        self.timings_logfile_dict['camera_bis'].append(self.times_bis)
        while self.acquire_images:
            if self.acquire_images == False:
                break
            # if image_acquired == 800:
            #     break
            else:
                self.images, self.times = self.cam.get_images()  ## getting the images, getting 0, 1 or >1 images
                while self.images == []:
                    self.images, self.times = self.cam.get_images() ## break the function if no image (due to the lauching time of the camera)
                self.image = self.images[0]  ## keeping only the 1st image for GUI display
                self.image_reshaped = self.image.reshape(int((self.y_dim/self.bin_size)),
                                                        int(self.x_dim/self.bin_size))  ## image needs reshaping for show
                print(f"Acquired {image_acquired} images")
                image_acquired += 1
                if self.saving_check.isChecked(): ## for saving data after end of acquisition, uses less memory if no saving
                    for j in range(len(self.images)):
                        self.image_list.append(self.images[j])
                    self.timings_logfile_dict['camera'].append(self.times)
#        self.timings_logfile_dict['camera_bis'].append(self.times_bis)
        self.cam.end_acquisition()
        self.saving_images(self.images, self.times)
#        self.camera_signal.finished.emit()  ## not sure this is needed

    def update_plot(self):
        if self.image_reshaped == []:
            pass
        else:
            self.graphicsView.setImage(self.image_reshaped)

    def saving_images(self, images, times):
        if self.saving_check.isChecked():
            ## saving images
            save_images_worker = Worker(self.save, self.image_list, self.path_raw_data)
            save_images_worker.signals.result.connect(self.print_output)
            save_images_worker.signals.finished.connect(self.thread_complete)
            #save_images_worker.signals.progress.connect(self.progress_fn)
            self.threadpool.start(save_images_worker)
            ## saving images times
            with open(self.timings_logfile_path, "w") as file:
                file.write(json.dumps(self.timings_logfile_dict, default=lambda x:list(x), indent=4, sort_keys=True))
            ## saving experiment info
            self.info_logfile_dict['roi'].append(self.roi_list)
            self.info_logfile_dict['exposure time'].append(self.exposure_time_value.value())
            self.info_logfile_dict['binning'].append(self.bin_size)
            self.info_logfile_dict['fps'].append(self.internal_frame_rate)
            self.info_logfile_dict['fov'].append((self.x_init, self.x_dim, self.y_init, self.y_dim))
            with open(self.info_logfile_path, "w") as file:
                file.write(json.dumps(self.info_logfile_dict, default=lambda x:list(x), indent=4, sort_keys=True))


    def roi(self):
        axes = (0, 1)
        self.saved_ROI_image.setImage(self.image_reshaped) ## get the image into the ROI graphic interface
        # data, coords = self.graphicsView.roi.getArrayRegion(self.image_reshaped.view(), self.graphicsView.imageItem, axes, returnMappedCoords=True) ## get the roi data and coords
        # self.roi_list.append(coords)
        roi_state = self.graphicsView.roi.getState()
        roi_state['pos'][0] = roi_state['pos'][0] + self.x_init
        roi_state['pos'][1] = roi_state['pos'][1] + self.y_init
        self.roi_list.append(roi_state)

        pen = QPen(Qt.red, 0.1) ## draw on the image to represent the roi
        for nb in range(len(self.roi_list)):
            r = pg.ROI(pos = (self.roi_list[nb]['pos'][0], self.roi_list[nb]['pos'][1]), \
                                size= (self.roi_list[nb]['size'][0], self.roi_list[nb]['size'][1]), \
                                angle = self.roi_list[nb]['angle'], pen=pen, movable=False, removable=False)
            self.saved_ROI_image.getView().addItem(r)
        self.ROI_label_placeholder.setText(str(len(self.roi_list)))

    def export_roi(self):
        self.info_logfile_dict['roi'].append(self.roi_list)
        with open(self.info_logfile_path, 'w') as file:
            file.write(json.dumps(self.info_logfile_dict, default=lambda x:list(x), indent=4, sort_keys=True))

    def reset_roi(self):
        self.saved_ROI_image.getView().clear()
        self.saved_ROI_image.setImage(self.image_reshaped)
        self.roi_list = []
        self.ROI_label_placeholder.setText(str(0))

    def save(self, images, path): ### npy format
        for i in range(len(images)):
            image = images[i]
            np.save(file = str(path) + '/image{}.npy'.format(str(i)), arr=image)
            print("saved file")

    def replay(self):
        if self.path == None:
            print("select a folder first")
        else:
            images_nb = len(os.listdir(self.path))
            images = []
            for i in range(images_nb):
                image = np.load(str(self.path) + '/raw_data/image{}.npy'.format(str(i)))
                image_reshaped = image.reshape(int(math.sqrt(image.shape[0])), int(math.sqrt(image.shape[0])))
                images.append(image_reshaped)
            for img in images:
                self.graphicsView.setImage(img)
                pg.QtGui.QApplication.processEvents()   ## maybe needs to be recoded in its own thread with the update function ?

    def exposure_time(self, value):
        value /= 1000
        self.cam.write_exposure(value)
        read_value = self.cam.read_exposure()
        self.exposure_time_value.display(read_value)

    def binning(self, index):
        if index == 0:
            self.cam.write_binning(1)
        if index == 1:
            self.cam.write_binning(2)
        if index == 2:
            self.cam.write_binning(4)
        self.current_binning_size_label_2.setText(str(self.cam.read_binning()))
        self.bin_size = self.cam.read_binning()

    def subarray(self):
        if self.subArray_mode_radioButton.isChecked():
            self.cam.write_subarray_mode(2)
            self.x_init,ok = QInputDialog.getInt(self,"new x origin value","enter a number")
            self.x_dim,ok = QInputDialog.getInt(self,"new x dimension value","enter a number")
            self.y_init,ok = QInputDialog.getInt(self,"new y origin value","enter a number")
            self.y_dim,ok = QInputDialog.getInt(self,"new y dimension value","enter a number")
            self.cam.write_subarray_size(self.x_init, self.x_dim, self.y_init, self.y_dim)
            self.cam.write_subarray_size(self.x_init, self.x_dim, self.y_init, self.y_dim) ## updating 2 times as 1 time sometimes doesn't work
            self.subarray_label.setText(str(self.cam.get_subarray_size()))

    def update_internal_frame_rate(self):
        self.internal_frame_rate = self.cam.get_internal_frame_rate()
        self.internal_frame_rate_label.setText(str(self.internal_frame_rate))


    ####################
    ##### DLP part #####
    ####################
    def calibration(self):
        if os.path.isfile(self.calibration_dlp_camera_matrix_path):
            print('Calibration matrix already exists, using it as reference')
            self.calibration_dlp_camera_matrix_path = 'C:/Users/barral/Desktop/whole_optic_gui-custom_signals/dlp/calibration_matrix.json'
            with open(self.calibration_dlp_camera_matrix_path) as file:
                self.camera_to_dlp_matrix = np.array(json.load(file))
        else:
            print('Calibration matrix doesnt exist. Generating calibration now')
            ## dlp img
            ## will ask for the calibration image of the dlp
            dlp_image_path = QFileDialog.getOpenFileName(self, 'Open file', 'C:/',"Image files (*.bmp)")[0]
            # dlp_image_path = "/media/jeremy/Data/CloudStation/Postdoc/Projects/Memory/Computational_Principles_of_Memory/optopatch/equipment/whole_optic_gui/dlp/calibration_images/Calibration_9pts.bmp"
            dlp_image = Image.open(dlp_image_path)
            dlp_image = ImageOps.invert(dlp_image.convert('RGB'))
            dlp_image = np.asarray(dlp_image)
            dlp_image = cv2.resize(dlp_image, (608,684))
            shape = (3, 3)
            isFound_dlp, centers_dlp = cv2.findCirclesGrid(dlp_image, shape, flags = cv2.CALIB_CB_SYMMETRIC_GRID + cv2.CALIB_CB_CLUSTERING)
            if isFound_dlp:
                print('found {} circle centers on images'.format(len(centers_dlp)))
            # show = cv2.drawChessboardCorners(dlp_image, shape, centers_dlp, isFound_dlp) ## if ever need to put chessboard

            ## projecting the calibration image with the dlp to get the camera image
            self.dlp.display_static_image(dlp_image_path)
            time.sleep(2)
            self.cam.write_exposure(0.10)
            self.cam.start_acquisition()
            time.sleep(1)
            for i in range(1):
                camera_image = self.cam.get_images()[0][0].reshape(self.x_dim,self.y_dim).T ##\ do I need to invert the dim here ? 
            self.cam.end_acquisition()
            # camera_image_path = "/media/jeremy/Data/CloudStation/Postdoc/Projects/Memory/Computational_Principles_of_Memory/optopatch/equipment/whole_optic_gui/camera/calibration_images/camera_image2.jpeg"
            # camera_image = Image.open(camera_image_path)

            ## converting the image in greylevels to 0/1 bit format using a threshold
            thresh = 250
            fn = lambda x : 255 if x > thresh else 0
            camera_image = Image.fromarray(camera_image)
            camera_image = camera_image.convert('L').point(fn, mode='1')
            camera_image = ImageOps.invert(camera_image.convert('RGB'))
            camera_image = np.asarray(camera_image)
            ## need to tune the cv2 detector for the detection of circles in a large image
            params = cv2.SimpleBlobDetector_Params()
            params.filterByArea = True
            params.minArea = 100
            params.maxArea = 10000
            params.minDistBetweenBlobs = 100
            params.filterByColor = False
            params.filterByConvexity = False
            params.minCircularity = 0.1
            detector = cv2.SimpleBlobDetector_create(params)
            # keypoints = detector.detect(camera_image)
            isFound_camera, centers_camera = cv2.findCirclesGrid(camera_image, shape, flags = cv2.CALIB_CB_SYMMETRIC_GRID + cv2.CALIB_CB_CLUSTERING, blobDetector=detector)
            if isFound_camera:
                print('found {} circle centers on images'.format(len(centers_camera)))

            ## for debug
            camera_image_drawn = cv2.drawChessboardCorners(camera_image, shape, centers_camera, isFound_camera)
            camera_image_drawn = Image.fromarray(camera_image_drawn)
            camera_image_drawn.show()

        # homography_matrix = cv2.findHomography(centers_camera, centers_dlp)
        # warped_camera_image = cv2.warpPerspective(camera_image, homography_matrix[0], dsize=(608,684))
        # warped_camera_image_drawn = Image.fromarray(warped_camera_image)
        # warped_camera_image_drawn.show()

        ## performing the calculs to get the transformation matrix between the camera image and the dlp image
            try:
                self.camera_to_dlp_matrix = cv2.findHomography(centers_camera, centers_dlp)[0]
                with open(self.calibration_dlp_camera_matrix_path, "w") as file:
                    file.write(json.dumps(self.camera_to_dlp_matrix.tolist()))
            except:
                pass


        # four_corners_camera = centers_camera[0],centers_camera[2], centers_camera[6],centers_camera[8]
        # four_corners_camera = np.array([[center for [center] in four_corners_camera]])
        # four_corners_dlp = centers_dlp[0], centers_dlp[2], centers_dlp[6], centers_dlp[8]
        # four_corners_dlp = np.array([[center for [center] in four_corners_dlp]])
        # self.camera_to_dlp_matrix = cv2.getPerspectiveTransform(four_corners_camera, four_corners_dlp)

        ########################
        ## getting the camera distortion matrix
        # centers_camera = np.array([[center for [center] in centers_camera]])
        # centers_dlp = np.array([[center for [center] in centers_dlp]])
        # centers_dlp = centers_dlp.reshape(1,9,2)
        #
        # new_dim = np.zeros((1,9,1)) ## calibrateCamera function requires input in 3D
        # centers_camera = np.concatenate((centers_camera, new_dim), axis=2)
        #
        # centers_camera = centers_camera.astype('float32') ## opencv is weird and if input are not specifically in float32 it will beug
        # centers_dlp = centers_dlp.astype('float32')
        #
        # ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(centers_camera, centers_dlp, (dlp_image.shape[0], dlp_image.shape[1]), None, None)
        # undist = cv2.undistort(camera_image, mtx, dist, None, mtx)  # example of how to undistord an image
        # Image.fromarray(undist)
        ########################

        ## getting the outline of the dlp onto the camera interface ##
        # dlp_to_camera_matrix = cv2.findHomography(centers_dlp, centers_camera )
        # x0, y0, x1, y1 = centers_dlp[4][0][0]-608/2, centers_dlp[4][0][1]-684/2, centers_dlp[4][0][0]+608/2, centers_dlp[4][0][1]+684/2
        # cv2.warpPerspective(black_image_with_ROI, self.camera_to_dlp_matrix[0],(608,684))
        # draw = ImageDraw.Draw(self.graphcsView)
        # draw.rectangle([(x0, y0), (x1, y1)], fill="white", outline=None)

        return self.camera_to_dlp_matrix

    def display_mode(self, index):
        self.display_mode_subbox_combobox.clear()
        if index == 0: # static image
            self.dlp.set_display_mode('static')
            self.display_mode_subbox_combobox.addItems(
                        ['Load Static Image',
                        'Generate Static Image From ROI',
                        'Display Static Image',
                        'Display Static Image On Timer'])
        if index == 1: # internal test pattern
            self.dlp.set_display_mode('internal')
            self.display_mode_subbox_combobox.addItems(
                        ['Checkboard Small',
                        'Black',
                        'White',
                        'Green',
                        'Blue',
                        'Red',
                        'Vertical Lines 1',
                        'Horizontal Lines 1',
                        'Vertical Lines 2',
                        'Horizontal Lines 2',
                        'Diagonal Lines',
                        'Grey Ranp Vertical',
                        'Grey Ramp Horizontal',
                        'Checkerboard Big'])
        if index == 2: # hdmi video input
            self.dlp.set_display_mode('hdmi')
            self.display_mode_subbox_combobox.addItems(
                        ['Generate ROI Files and Compile Movie From Images',
                        'Choose HDMI Video Sequence'])
        if index == 3: # pattern sequence display
            self.dlp.set_display_mode('pattern')
            self.display_mode_subbox_combobox.addItems(
                        ['Choose Pattern Sequence To Load',
                        'Choose Pattern Sequence To Display',
                        'Generate Multiple Images with One ROI Per Image'])

    def choose_action(self, index):
        ## Static image mode
        if self.display_mode_combobox.currentIndex() == 0: ## load image
            if index == 0: ## choose static image
                self.dlp_image_path = QFileDialog.getOpenFileName(self,
                                    'Open file', 'C:/',"Image files (*.jpg *.bmp)")
                img = Image.open(self.dlp_image_path[0])
                if img.size == (608,684):
                    self.dlp.display_static_image(self.dlp_image_path[0])
                    self.dlp.set_display_mode('internal')
                    self.dlp.black()
                else:
                    warped_image = cv2.warpPerspective(img, self.camera_to_dlp_matrix,(608, 684))
                    warped_flipped_image = cv2.flip(warped_image, 0)
                    cv2.imwrite(self.dlp_image_path[0] + 'warped.bmp', warped_flipped_image)
                    # self.dlp.display_static_image(self.dlp_image_path[0] + 'warped.bmp')

            elif index == 1:  ##generate static image from ROI
                black_image = Image.new('1', (2048,2048), color=0) ## 2048 because we want the full fov
                black_image_with_ROI = black_image
                for nb in range(len(self.roi_list)):
                    x0, y0 = (self.roi_list[nb]['pos'][0], self.roi_list[nb]['pos'][1])
                    x1, y1 = (self.roi_list[nb]['pos'][0] + self.roi_list[nb]['size'][0],
                                self.roi_list[nb]['pos'][1] + self.roi_list[nb]['size'][1])
                    draw = ImageDraw.Draw(black_image_with_ROI)
                    draw.rectangle([(x0, y0), (x1, y1)], fill="white", outline=None)
                black_image_with_ROI = black_image_with_ROI.convert('RGB') ## for later the warpPerspective function needs a shape of (:,:,3)
                black_image_with_ROI = np.asarray(black_image_with_ROI)
                black_image_with_ROI_warped = cv2.warpPerspective(black_image_with_ROI,
                                                    self.camera_to_dlp_matrix,(608,684))

                center = (608 / 2, 684 / 2)
                M = cv2.getRotationMatrix2D(center, 270, 1.0)
                black_image_with_ROI_warped = cv2.warpAffine(black_image_with_ROI_warped, M, (608, 684))

                black_image_with_ROI_warped_flipped = cv2.flip(black_image_with_ROI_warped, 0)
                cv2.imwrite(self.path + '/dlp_images' + '/ROI_warped' + '.bmp',
                                                    black_image_with_ROI_warped_flipped)

            elif index == 2: ### display static image
                self.dlp.set_display_mode('static')
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)

            elif index == 3: ## display static image on on/off timer set by the user
                worker = Worker(self.dlp_auto_control)
                self.dlp_auto_control.signals.result.connect(self.print_output)
                self.dlp_auto_control.signals.finished.connect(self.thread_complete)
                #dlp_auto_control.signals.progress.connect(self.progress_fn)
                self.threadpool.start(worker)
                self.dlp_signal.finished.emit()
                self.camera_signal.finished.emit()
                self.laser_signal.finished.emit()


        ## Internal test pattern mode
        elif self.display_mode_combobox.currentIndex() == 1: ## internal test pattern
            if index == 0: ## Checkboard small
                self.dlp.checkboard_small()
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
            if index == 1: # Black
                self.dlp.black()
                self.timings_logfile_dict['dlp']['off'].append((time.perf_counter() - self.perf_counter_init)*1000)
            if index == 2: ## White
                self.dlp.white()
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
            if index == 3: ## Green
                self.dlp.green()
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
            if index == 4: ## Blue
                self.dlp.blue()
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
            if index == 5: ## Red
                self.dlp.red()
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
            if index == 6: ## Vertical lines 1
                self.dlp.horizontal_lines_1()
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
            if index == 7: ## Horizontal lines 1
                self.dlp.vertical_lines_1()
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
            if index == 8: ## Vertical lines 2
                self.dlp.horizontal_lines_2()
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
            if index == 9: ## Horizontal lines 2
                self.dlp.vertical_lines_2()
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
            if index == 10: ## Diagonal lines
                self.dlp.diagonal_lines()
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
            if index == 11: ## Grey Ramp Vertical
                self.dlp.grey_ramp_vertical()
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
            if index == 12: ## Grey Ramp Horizontal
                self.dlp.grey_ramp_horizontal()
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
            if index == 13: ## Checkerboard Big
                self.dlp.checkerboard_big()
                self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)

        ## HDMI Video Input mode
        elif self.display_mode_combobox.currentIndex() == 2:  ## HDMI video sequence
            if index == 0: ## Generate ROI Files and Compile Movie From Images
                self.generate_one_image_per_roi(self.roi_list)
                time.sleep(5)
                self.movie_from_images()
            elif index == 1: ## Choose HDMI Video Sequence
                vlc_path = "C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe"
                video_path = f"{self.path}\\dlp_images\\dlp_movie.avi"
                ## is the screen number working ? neede to test with dlp screen. need to adapt screen number
                subprocess.call([vlc_path, '--ignore-config', '--play-and-exit', '--fullscreen', '--qt-fullscreen-screennumber=1', video_path], shell=True)

        ## Pattern sequence mode
        elif self.display_mode_combobox.currentIndex() == 3:  ## Pattern sequence
            if index == 0: # Choose Pattern Sequence To Load
                time_stim, ok = QInputDialog.getInt(self, 'Input Dialog', 'Duration of pattern exposition (in µs)')   ## time to be given in microseconds
                image_folder = QFileDialog.getExistingDirectory(self, 'Select Image Folder where DLP images are stored')[0]
                InputTriggerDelay = 0
                AutoTriggerPeriod = 3333334
                ExposureTime = 3333334

            if index == 1: ## Choose Pattern Sequence to Display
                print(image_folder)
                self.dlp.display_image_sequence(image_folder, InputTriggerDelay, AutoTriggerPeriod, ExposureTime)

            if index == 2: ## Generate Multiple Images with One ROI Per Image
                self.generate_one_image_per_roi(self.roi_list)

    def turn_dlp_off(self):
        self.dlp.set_display_mode('internal')
        self.dlp.black()
        self.timings_logfile_dict['dlp']['off'].append((time.perf_counter() - self.perf_counter_init)*1000)
        print('dlp end signal received')

    def generate_one_image_per_roi(self, roi_list):
        for nb in range(len(self.roi_list)):
            black_image = Image.new('1', (2048,2048), color=0)
            black_image_with_ROI = black_image
            x0, y0 = (self.roi_list[nb]['pos'][0], self.roi_list[nb]['pos'][1])
            x1, y1 = (self.roi_list[nb]['pos'][0] + self.roi_list[nb]['size'][0], self.roi_list[nb]['pos'][1] + self.roi_list[nb]['size'][1])
            draw = ImageDraw.Draw(black_image_with_ROI)
            draw.rectangle([(x0, y0), (x1, y1)], fill="white", outline=None)
            black_image_with_ROI = black_image_with_ROI.convert('RGB') ## for later the warpPerspective function needs a shape of (:,:,3)
            black_image_with_ROI = np.asarray(black_image_with_ROI)
            black_image_with_ROI_warped = cv2.warpPerspective(black_image_with_ROI, self.camera_to_dlp_matrix,(608,684))
            black_image_with_ROI_warped_flipped = cv2.flip(black_image_with_ROI_warped, 0)
            cv2.imwrite(self.path + '/dlp_images' + '/ROI_warped_' + f"{nb}" + '.bmp', black_image_with_ROI_warped_flipped)

    def movie_from_images(self):
        filenames = os.listdir(f"{self.path}/dlp_images/")
        size_image = cv2.imread(f"{self.path}/dlp_images/{filenames[1]}")
        h, v, z = size_image.shape
        fps = 1  ## if 100 then 1 frame last 10 ms
        out = cv2.VideoWriter(f"{self.path}/dlp_images/dlp_movie.avi", cv2.VideoWriter_fourcc(*'MJPG'), fps, (v,h))  #MJPG
#        out = cv2.VideoWriter(f"{path}/dlp_images/dlp_movie.avi", -1, fps, size)
        for filename in filenames:
            print(f'writing image {filename} in video')
            img = cv2.imread(f"{self.path}/dlp_images/{filename}")
            out.write(img)
        out.release()

    ####################
    ####    Laser   ####
    ####################
    def laser_on(self):
        self.laser.turn_on()
        self.timings_logfile_dict['laser']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)

    def laser_off(self):
        self.laser.turn_off()
        self.timings_logfile_dict['laser']['off'].append((time.perf_counter() - self.perf_counter_init)*1000)

    ########################
    ####   Controler    ####
    ########################
    def left(self):
        self.scope.move_left()
        self.coordinate_label_2.setText(self.scope.get_coordinates())

    def right(self):
        self.scope.move_right()
        self.coordinate_label_2.setText(self.scope.get_coordinates())

    def backward(self):
        self.scope.move_backward()
        self.coordinate_label_2.setText(self.scope.get_coordinates())

    def forward(self):
        self.scope.move_forward()
        self.coordinate_label_2.setText(self.scope.get_coordinates())

    def up(self):
        self.scope.up()
        self.coordinate_label_2.setText(self.scope.get_coordinates())

    def down(self):
        self.scope.down()
        self.coordinate_label_2.setText(self.scope.get_coordinates())

    def stop_mouvment(self):
        self.scope.stop_mouvment()
        self.coordinate_label_2.setText(self.scope.get_coordinates())


    ####################
    #### Automation  ###
    ####################
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
#                self.laser_on()
                custom_sleep_function(1000)
                if self.record_electrophysiological_trace_radioButton.isChecked():
                    self.start_stimulation()
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
                    self.end_stimulation()
                self.turn_dlp_off()
#                self.timings_logfile_dict['dlp']['off'].append((time.perf_counter() - self.perf_counter_init)*1000)
                custom_sleep_function(dlp_off)
#            self.laser_off()
            custom_sleep_function(dlp_interval)
        self.camera_signal.finished.emit()
        if self.record_electrophysiological_trace_radioButton.isChecked():
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

    ########################################
    #### Classical electrophysiology  ######
    ########################################
    ## TO DO: need to make more dynamic
    
    def init_voltage(self):
        ## reading voltage
        self.analog_input = PyDAQmx.Task()
        self.read = PyDAQmx.int32()
        self.data_ephy = np.zeros((len(self.channel_number), self.sampling_rate), dtype=np.float64)
        for channel in self.channel_number:
            self.analog_input.CreateAIVoltageChan(f'Dev1/ai{channel}',
                                                        "",
                                                        PyDAQmx.DAQmx_Val_Cfg_Default,
                                                        -10.0,
                                                        10.0,
                                                        PyDAQmx.DAQmx_Val_Volts,
                                                        None)
        self.analog_input.CfgSampClkTiming("",
                            self.sampling_rate,  ## sampling rate
                            PyDAQmx.DAQmx_Val_Rising,  ## active edge
                            PyDAQmx.DAQmx_Val_FiniteSamps, ## sample mode
                            1000) ## nb of sample to acquire
        self.analog_input.StartTask()
        
        ## stimulating
#        self.analog_output = PyDAQmx.Task()
#        self.analog_output.CreateAOVoltageChan("Dev1/ao0",
#                                "",
#                                -10.0,
#                                10.0,
#                                PyDAQmx.DAQmx_Val_Volts,
#                                None)
#        self.analog_output.CfgSampClkTiming("",
#                    self.sampling_rate,  ## sampling rate
#                    PyDAQmx.DAQmx_Val_Rising,  ## active edge
#                    PyDAQmx.DAQmx_Val_ContSamps, ## sample mode
#                    1000) ## nb of sample to acquire
#        self.analog_output.StartTask()
        
        self.pulse = np.zeros(1, dtype=np.uint8)
        self.write_digital_lines = PyDAQmx.Task()
        self.write_digital_lines.CreateDOChan("/Dev1/port0/line3","",PyDAQmx.DAQmx_Val_ChanForAllLines)
        self.write_digital_lines.StartTask()
        
    def start_recording(self):
        self.analog_input.ReadAnalogF64(self.sampling_rate,   ## number of sample per channel
                                    10.0,  ## timeout in s
                                    PyDAQmx.DAQmx_Val_GroupByChannel,  ## fillMode (interleave data acqcuisition or not?)
                                    self.data_ephy,   #The array to store read data into
                                    self.data_ephy.shape[0]*self.data_ephy.shape[1],  ## length of the data array
                                    PyDAQmx.byref(self.read),None) ## total number of data points read per channel
        print(f"Acquired {self.read.value} points")
        self.analog_input.StopTask()
        print(self.data_ephy.shape)
        
        self.timings_logfile_dict['ephy']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
        return self.data_ephy

    def graph_voltage(self):
        self.x = range(self.sampling_rate)
        self.start_recording()
#        colors = ['g', 'r', 'c', 'm', 'y', 'k', 'w']
#        self.voltage_plot = pg.plot(self.x, self.data_ephy[0], pen='b')
#        if self.data_ephy.shape[0] > 1:
#            for channel, color in zip(range(self.data_ephy.shape[0]-1), colors):
#                    self.voltage_plot.plot(self.x, self.data_ephy[channel]+1, pen = color)
        self.plot = pg.GraphicsWindow(title="Electrophysiology")
        self.voltage_plot = self.plot.addPlot(title='Voltage')

        self.curve0 = self.voltage_plot.plot(self.x, self.data_ephy[0], pen='b')
        self.curve1 = self.voltage_plot.plot(self.x, self.data_ephy[1], pen='g')
        self.curve2 = self.voltage_plot.plot(self.x, self.data_ephy[2], pen='r')
        self.curve3 = self.voltage_plot.plot(self.x, self.data_ephy[3], pen='c')
        
        self.curve4 = self.voltage_plot.plot(self.x, self.data_ephy[4], pen='m')
        self.curve5 = self.voltage_plot.plot(self.x, self.data_ephy[5], pen='y')
        self.curve6 = self.voltage_plot.plot(self.x, self.data_ephy[6], pen='k')
        self.curve7 = self.voltage_plot.plot(self.x, self.data_ephy[7], pen='w')
        
        self.voltage_plot.addLegend()
        self.voltage_plot.showGrid(x=True, y=True)
        self.plot.setBackground('w')
        pg.setConfigOptions(antialias=True)
        self.ephy_graph = True
        
        self.timer_ephy = QTimer()
        self.timer_ephy.timeout.connect(self.update_plot_ephy)
        self.timer_ephy.start(1000)

    def update_plot_ephy(self):
        if self.ephy_graph==False:
            self.timer_ephy.stop()

        self.start_recording()
#        self.voltage_plot.enableAutoRange('xy', False)
#        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
#        debug_trace()
#        for channel, color in zip(range(self.data_ephy.shape[0]), colors):
#        for channel in range(self.data_ephy.shape[0]):
#            self.voltage_plot.setData(1000, self.data_ephy[channel])
#            self.voltage_plot.plot(self.x, self.data_ephy[channel], clear=True, pen=color)
        self.curve0.setData(self.x, self.data_ephy[0])
        self.curve1.setData(self.x, self.data_ephy[1])
        self.curve2.setData(self.x, self.data_ephy[2])
        self.curve3.setData(self.x, self.data_ephy[3])
        
        self.curve4.setData(self.x, self.data_ephy[4])
        self.curve5.setData(self.x, self.data_ephy[5])
        self.curve6.setData(self.x, self.data_ephy[6])
        self.curve7.setData(self.x, self.data_ephy[7])

        
    def close_graph_windows(self):
        print('closing ephy plot and stopping recording')
        self.ephy_graph = False
        self.timer_ephy.stop()
        self.stop_recording()
        self.plot.close()

    def stop_recording(self):
        print('ephy end signal received')
        self.recording = False
        self.save_ephy_data(self.ephy_data)
        self.analog_input.StopTask()
        self.timings_logfile_dict['ephy']['off'].append((time.perf_counter() - self.perf_counter_init)*1000)

    def save_ephy_data(self, data):
        np.save(file = f"{self.path}/voltage.npy", arr = data)
#        np.savetxt(f"{self.path}/voltage.txt", data)

    def ephy_recording_thread(self):
#        if self.record_electrophysiological_trace_radioButton.isChecked():
        while self.recording:
            self.data_ephy = self.start_recording()
#            self.graph_voltage()
            self.ephy_data.append(self.data_ephy)

    def start_stimulation(self):
        print('stimulation start')
#        set_voltage_value = 5.
#        self.stim_data = np.array([5]*1000)
#        self.stim_data[1:100] = 0
#        self.stim_data[900:1000] = 0
#        self.stim_data = np.array([5])
#        n=1000
#        sampsPerChanWritten=PyDAQmx.int32()
#
#        self.analog_output.WriteAnalogScalarF64(1, 10.0, set_voltage_value, None)
#        self.analog_output.WriteAnalogF64(1000, 0, 10.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.stim_data, PyDAQmx.byref(sampsPerChanWritten), None)
#        self.analog_output.WriteAnalogF64(n, 0, 10.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.stim_data, PyDAQmx.byref(sampsPerChanWritten), None)
#        self.analog_output.StartTask()
        
        self.timings_logfile_dict['ephy_stim']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)


        self.pulse[0]=1
        self.write_digital_lines.WriteDigitalLines(1, 1, 5.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse, None, None)

    def end_stimulation(self):
#        self.analog_output.StopTask()
        self.timings_logfile_dict['ephy_stim']['off'].append((time.perf_counter() - self.perf_counter_init)*1000)
        print('stimulation end')
        
        self.pulse[0]=0
        self.write_digital_lines.WriteDigitalLines(1, 1, 5.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse , None, None)
        
    def ephy_stim(self):
        self.start_stimulation()
        custom_sleep_function(200)
        self.end_stimulation()



    ####################
    #### Clean exit ####
    ####################
    def bye(self):
        if self.activate_camera is True:
            self.cam.shutdown()
        if self.activate_laser is True:
            self.laser.disconnect()
        if self.activate_dlp is True:
            self.dlp.disconnect()
        if self.activate_controller is True:
            pass
        sys.exit()


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
#    win.show()
    win.showMaximized()
    app.exec_()
    app.exit(app.exec_())

if __name__ == "__main__":
    main()
