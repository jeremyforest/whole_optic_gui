## PyQT5
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, pyqtSignal, QThreadPool, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, QMessageBox, QProgressBar, QGraphicsScene, QInputDialog
from PyQt5.QtGui import QImage, QPixmap, QPen, QPainter
from PyQt5.QtTest import QTest
import pyqtgraph as pg

## QTDesigner
from whole_optic_gui import Ui_MainWindow

## common dependencies
import argparse
import numpy as np
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
import math

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
        self.kwargs['progress_callback'] = self.signals.progress

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




class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.retranslateUi(self)

        ###################################
        ##### gui initialization #####
        ###################################

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        camera_signal_end = Signals()
        dlp_signal_end = Signals()
        laser_signal_end = Signals()

        ## commande-line options
        self.activate_camera = False
        self.activate_laser = False
        self.activate_dlp = False
        self.activate_controller = False
        self.activate_bridge = False

        parser = argparse.ArgumentParser(description="hardware to load")
        parser.add_argument("--camera", default=False, action="store_true" , help="to load the camera functions")
        parser.add_argument("--laser", default=False, action="store_true" , help="to load the laser functions")
        parser.add_argument("--dlp", default=False, action="store_true" , help="to load the dlp functions")
        parser.add_argument("--controler", default=False, action="store_true" , help="to load the controller functions")
        parser.add_argument("--bridge", default=False, action="store_true", help="to load the bridge and voltage clamp amplifier")
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

        if args.bridge is True:
            self.activate_bridge = True
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
            self.binning = self.cam.read_binning()
            self.current_binning_size_label_2.setText(str(self.cam.read_binning()))
            ## exposure time
            self.exposure_time_value.display(self.cam.read_exposure())
            ## set property as wanted
            self.cam.hcam.setPropertyValue('defect_correct_mode', 1)  ## necessary ?
            print(self.cam.hcam.getPropertyValue('defect_correct_mode'))
            self.cam.hcam.setPropertyValue('hot_pixel_correct_level', 2)   ## necessary ?
            print(self.cam.hcam.getPropertyValue('hot_pixel_correct_level'))
        ##### dlp #####
        if self.activate_dlp is True:
            from dlp.dlp_control import Dlp
            self.dlp = Dlp()
            self.dlp.connect()
        ##### laser #####
        if self.activate_laser is True:
            from laser.laser_control import CrystalLaser
            self.laser = CrystalLaser()
            self.laser.connect()
        ##### manipulator #####
        if self.activate_controller is True:
            from controler.manipulator_command import Scope
            self.scope = Scope()
        ##### bridge #####
        if self.activate_bridge is True:
            from electrophysiology.ephys_stim_for_gate import Stim
            self.bridge = Stim()
            self.bridge.connect()

        ## variable reference for later use
        self.path = None
        self.path_raw_data = None
        self.save_images = False
        self.simulated = False
        self.roi_list = []
        self.camera_to_dlp_matrix = []
        self.camera_distortion_matrix = []
        self.dlp_image_path = []
        self.calibration_dlp_camera_matrix_path = 'dlp/calibration_matrix.json'

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
        self.timings_logfile_dict['ephys'] = {}
        self.timings_logfile_dict['ephys']['on'] = []
        self.timings_logfile_dict['ephys']['off'] = []

        self.info_logfile_dict = {}
        self.info_logfile_dict['experiment creation date'] = None
        self.info_logfile_dict['roi'] = []
        self.info_logfile_dict['exposure time'] = []
        self.info_logfile_dict['binning'] = []
        self.info_logfile_dict['fov'] = []
        self.info_logfile_dict['fps'] = []

        ## camera widget
        self.snap_image_button.clicked.connect(self.snap_image)
        self.stream_button.clicked.connect(self.stream)
        self.replay_button.clicked.connect(self.replay)
        self.exposure_time_bar.valueChanged.connect(self.exposure_time)
        self.binning_combo_box.activated.connect(self.binning)
        self.subArray_mode_radioButton.toggled.connect(self.subarray)
        self.update_internal_frame_rate_button.clicked.connect(self.update_internal_frame_rate)

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

        ## electrophysiology
        self.stim_button.clicked.connect(self.stim)


    ###################################
    ####### utils functions ###########
    ###################################
    def progress_fn(self, n):
        print("%d%% done" % n)

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("Thread Completed!")

    ###################################
    ########## GUI code ###############
    ###################################

    def change_folder(self):
        self.path = QFileDialog.getExistingDirectory(None, 'Select the folder you want the path to change to:',
                                                        'C:/', QFileDialog.ShowDirsOnly)
        self.path_raw_data = self.path + '/raw_data'
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
        self.timings_logfile_dict['ephys'] = {}
        self.timings_logfile_dict['ephys']['on'] = []
        self.timings_logfile_dict['ephys']['off'] = []

        self.info_logfile_dict = {}
        self.info_logfile_dict['experiment creation date'] = None
        self.info_logfile_dict['roi'] = []
        self.info_logfile_dict['exposure time'] = []
        self.info_logfile_dict['binning'] = []
        self.info_logfile_dict['fov'] = []
        self.info_logfile_dict['fps'] = []

        ## generate folder to save the data
        self.path = QFileDialog.getExistingDirectory(None, 'Select a folder where you want to store your data:',
                                                        'C:/', QFileDialog.ShowDirsOnly)
        self.path_raw_data = self.path + '/raw_data'
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
        self.path_raw_data = self.path + '/raw_data'
        os.makedirs(self.path)
        os.makedirs(self.path + '/dlp_images')
        os.makedirs(self.path + '/raw_data')

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
            self.cam.end_acquisition()
            self.image = self.images[0]
            self.image_reshaped = self.image.reshape(int(self.x_dim/self.binning),
                                                    int(self.y_dim/self.binning)) ## image needs reshaping
            self.graphicsView.setImage(self.image_reshaped)
            image_name = QInputDialog.getText(self, 'Input Dialog', 'File name:')
            self.save_as_png(self.image_reshaped, image_name)

    def stream(self):
         self.images = []
         self.image_list = []
         self.timings_logfile_dict['camera'] = []
         image_processing_worker = Worker(self.processing_images)
         image_processing_worker.signals.result.connect(self.print_output)
         image_processing_worker.signals.finished.connect(self.thread_complete)
         image_processing_worker.signals.progress.connect(self.progress_fn)
         self.threadpool.start(image_processing_worker)

    def stop_stream(self):
        # self.image_processing_worker.terminate
        acquire_images = False

    def processing_images(self):    #,progress_callback):
        acquire_images = True
        self.cam.start_acquisition()
        image_acquired = 0
        while acquire_images:
            self.stop_stream_button.clicked.connect(self.stop_stream)
            if acquire_images == False:
                break
            else:
                self.images, self.times = self.cam.get_images()  ## getting the images, getting 0, 1 or >1 images
                self.image = self.images[0]  ## keeping only the 1st image for GUI display
                self.image_reshaped = self.image.reshape(int(self.x_dim/self.binning),
                                                        int(self.y_dim/self.binning))  ## image needs reshaping for show
                self.graphicsView.setImage(self.image_reshaped)
                # progress_callback.emit(n*100/4)
                print(f"Acquired {image_acquired} images")
                image_acquired += 1
                if self.saving_check.isChecked(): ## for saving data after end off acquisition
                    for j in range(len(images)):
                        self.image_list.append(images[j])
                    self.timings_logfile_dict['camera'].append(times)
        self.cam.end_acquisition()
        self.saving_images(self.images, self.times)

    def saving_images(self, images, times):
        if self.saving_check.isChecked():
            ## saving images
            save_images_worker = Worker(self.save, self.image_list, self.path_raw_data)
            save_images_worker.signals.result.connect(self.print_output)
            save_images_worker.signals.finished.connect(self.thread_complete)
            save_images_worker.signals.progress.connect(self.progress_fn)
            self.threadpool.start(save_images_worker)
            ## saving images times
            with open(self.timings_logfile_path, "w") as file:
                file.write(json.dumps(self.timings_logfile_dict, default=lambda x:list(x), indent=4))
            ## saving experiment info
            self.info_logfile_dict['roi'].append(self.roi_list)
            self.info_logfile_dict['exposure time'].append(self.exposure_time_value.value())
            self.info_logfile_dict['binning'].append(self.binning)
            self.info_logfile_dict['fps'].append(self.internal_frame_rate)
            self.info_logfile_dict['fov'].append((self.x_init, self.x_dim, self.y_init, self.y_dim))
            with open(self.info_logfile_path, "w") as file:
                file.write(json.dumps(self.info_logfile_dict, default=lambda x:list(x), indent=4))


    def roi(self):
        axes = (0, 1)
        self.saved_ROI_image.setImage(self.image_reshaped) ## get the image into the ROI graphic interface

        # data, coords = self.graphicsView.roi.getArrayRegion(self.image_reshaped.view(), self.graphicsView.imageItem, axes, returnMappedCoords=True) ## get the roi data and coords
        # self.roi_list.append(coords)

        roi_state = self.graphicsView.roi.getState()
        # print(roi_state)
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
            file.write(json.dumps(self.info_logfile_dict, default=lambda x:list(x), indent=4))

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
        self.binning = self.cam.read_binning()

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
            self.calibration_dlp_camera_matrix_path = 'C:/Users/barral/Desktop/whole_optic_gui-log_implementation_and_threading/dlp/calibration_matrix.json'
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
                camera_image = self.cam.get_images()[0][0].reshape(self.x_dim,self.y_dim).T
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
            self.display_mode_subbox_combobox.addItems(['Load Static Image',
                                                        'Generate Static Image from ROI',
                                                        'Display Static Image',
                                                        'Display Stati Image on Timer'])
        if index == 1: # internal test pattern
            self.dlp.set_display_mode('internal')
            self.display_mode_subbox_combobox.addItems(['Checkboard small',
                                                        'Black',
                                                        'White',
                                                        'Green',
                                                        'Blue',
                                                        'Red',
                                                        'Vertical lines 1',
                                                        'Horizontal lines 1',
                                                        'Vertical lines 2',
                                                        'Horizontal lines 2',
                                                        'Diagonal lines',
                                                        'Grey Ranp Vertical',
                                                        'Grey Ramp Horizontal',
                                                        'Checkerboard big'])
        if index == 2: # hdmi video input
            self.display_mode_subbox_combobox.addItem('Choose HDMI Video Sequence')
        if index == 3: # pattern sequence display
            self.dlp.set_display_mode('pattern')
            self.display_mode_subbox_combobox.addItems(['Choose Pattern Sequence To Load',
                                                        'Choose Pattern Sequence To Display',
                                                        'Generate Multiple Images with One ROI Per Image'])

    def choose_action(self, index):
        ## Static image mode
        if self.display_mode_combobox.currentIndex() == 0: ## load image
            if index == 0: ## choose static image
                self.dlp_image_path = QFileDialog.getOpenFileName(self, 'Open file', 'C:/',"Image files (*.jpg *.bmp)")
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
                black_image = Image.new('1', (2048,2048), color=0) ## need to make this dependant upon fov size and not 2048
                black_image_with_ROI = black_image
                for nb in range(len(self.roi_list)):
                    x0, y0 = (self.roi_list[nb]['pos'][0], self.roi_list[nb]['pos'][1])
                    x1, y1 = (self.roi_list[nb]['pos'][0] + self.roi_list[nb]['size'][0], self.roi_list[nb]['pos'][1] + self.roi_list[nb]['size'][1])
                    # x0,y0,x1,y1 = 100,800, 1000, 1000
                    draw = ImageDraw.Draw(black_image_with_ROI)
                    draw.rectangle([(x0, y0), (x1, y1)], fill="white", outline=None)
                black_image_with_ROI = black_image_with_ROI.convert('RGB') ## for later the warpPerspective function needs a shape of (:,:,3)
                black_image_with_ROI = np.asarray(black_image_with_ROI)
                black_image_with_ROI_warped = cv2.warpPerspective(black_image_with_ROI, self.camera_to_dlp_matrix,(608,684))

                center = (608 / 2, 684 / 2)
                M = cv2.getRotationMatrix2D(center, 270, 1.0)
                black_image_with_ROI_warped = cv2.warpAffine(black_image_with_ROI_warped, M, (608, 684))

                black_image_with_ROI_warped_flipped = cv2.flip(black_image_with_ROI_warped, 0)
                cv2.imwrite(self.path + '/dlp_images' + '/ROI_warped' + '.bmp', black_image_with_ROI_warped_flipped)

            elif index == 2: ### display static image
                self.dlp.set_display_mode('static')
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())

            elif index == 3: ## display static image on on/off timer set by the user
                worker = Worker(self.dlp_auto_control)
                dlp_auto_control.signals.result.connect(self.print_output)
                dlp_auto_control.signals.finished.connect(self.thread_complete)
                dlp_auto_control.signals.progress.connect(self.progress_fn)
                self.threadpool.start(worker)


        ## Internal test pattern mode
        elif self.display_mode_combobox.currentIndex() == 1: ## internal test pattern
            if index == 0: ## Checkboard small
                self.dlp.checkboard_small()
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())
            if index == 1: # Black
                self.dlp.black()
                self.timings_logfile_dict['dlp']['off'].append(time.time_ns())
            if index == 2: ## White
                self.dlp.white()
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())
            if index == 3: ## Green
                self.dlp.green()
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())
            if index == 4: ## Blue
                self.dlp.blue()
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())
            if index == 5: ## Red
                self.dlp.red()
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())
            if index == 6: ## Vertical lines 1
                self.dlp.horizontal_lines_1()
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())
            if index == 7: ## Horizontal lines 1
                self.dlp.vertical_lines_1()
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())
            if index == 8: ## Vertical lines 2
                self.dlp.horizontal_lines_2()
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())
            if index == 9: ## Horizontal lines 2
                self.dlp.vertical_lines_2()
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())
            if index == 10: ## Diagonal lines
                self.dlp.diagonal_lines()
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())
            if index == 11: ## Grey Ramp Vertical
                self.dlp.grey_ramp_vertical()
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())
            if index == 12: ## Grey Ramp Horizontal
                self.dlp.grey_ramp_horizontal()
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())
            if index == 13: ## Checkerboard Big
                self.dlp.checkerboard_big()
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())

        ## HDMI Video Input mode
        elif self.display_mode_combobox.currentIndex == 2:  ## HDMI video sequence
            print("mode not yet implemented")

        ## Pattern sequence mode
        elif self.display_mode_combobox.currentIndex() == 3:  ## Pattern sequence
            if index == 0: # Choose Pattern Sequence To Load
                debug_trace()
                time_stim, ok = QInputDialog.getInt(self, 'Input Dialog', 'Duration of pattern exposition (in µs)')   ## time to be given in microseconds
                image_folder = QFileDialog.getExistingDirectory(self, 'Select Image Folder where DLP images are stored')[0]
                InputTriggerDelay = 0
                AutoTriggerPeriod = 3333334
                ExposureTime = 3333334

            if index == 1: ## Choose Pattern Seauence to Display
                print(image_folder)
                self.dlp.display_image_sequence(image_folder, InputTriggerDelay, AutoTriggerPeriod, ExposureTime)

            if index == 2: ## Generate Multiple Images with One ROI Per Image
                for nb in range(len(self.roi_list)):
                    black_image = Image.new('1', (2048,2048), color=0) ## need to make this dependant upon fov size and not 2048
                    black_image_with_ROI = black_image
                    x0, y0 = (self.roi_list[nb]['pos'][0], self.roi_list[nb]['pos'][1])
                    x1, y1 = (self.roi_list[nb]['pos'][0] + self.roi_list[nb]['size'][0], self.roi_list[nb]['pos'][1] + self.roi_list[nb]['size'][1])
                    draw = ImageDraw.Draw(black_image_with_ROI)
                    draw.rectangle([(x0, y0), (x1, y1)], fill="white", outline=None)
                    black_image_with_ROI = black_image_with_ROI.convert('RGB') ## for later the warpPerspective function needs a shape of (:,:,3)
                    black_image_with_ROI = np.asarray(black_image_with_ROI)
                    black_image_with_ROI_warped = cv2.warpPerspective(black_image_with_ROI, self.camera_to_dlp_matrix,(608,684))
                    black_image_with_ROI_warped_flipped = cv2.flip(black_image_with_ROI_warped, 0)
                    cv2.imwrite(self.path + '/dlp_images' + '/ROI_warped_' + f"{nb}" + '.bmp', black_image_with_ROI_warped)

    def dlp_auto_control(self, dlp_on=50, dlp_off=500, dlp_sequence=1, dlp_repeat_sequence=1, dlp_interval=1):
        for i in range(dlp_repeat_sequence):
            for j in range(dlp_sequence):
                ## ON
                self.dlp.set_display_mode('static')
                self.timings_logfile_dict['dlp']['on'].append(time.time_ns())
                time.sleep(dlp_on/1000)
                ## OFF
                self.dlp.set_display_mode('internal')
                self.dlp.black()
                self.timings_logfile_dict['dlp']['off'].append(time.time_ns())
                time.sleep(dlp_off/1000)
            time.sleep(dlp_interval/1000)
        dlp_signal_end.finished()

    ####################
    ####    Laser   ####
    ####################
    def laser_on(self):
        self.laser.turn_on()
        self.timings_logfile_dict['laser']['on'].append(time.time_ns())

    def laser_off(self):
        self.laser.turn_off()
        self.timings_logfile_dict['laser']['off'].append(time.time_ns())


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

    def export_experiment(self):
        self.info_logfile_dict['roi'].append(self.roi_list)
        self.info_logfile_dict['exposure time'].append(self.exposure_time_value.value())
        self.info_logfile_dict['binning'].append(self.binning)
        self.info_logfile_dict['fps'].append(self.internal_frame_rate)
        self.info_logfile_dict['fov'].append((self.x_init, self.x_dim, self.y_init, self.y_dim))
        with open(self.info_logfile_path, "w") as file:
            file.write(json.dumps(self.info_logfile_dict, default=lambda x:list(x), indent=4))

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
        self.initialize_experiment()
        dlp_worker = Worker(self.dlp_auto_control)
        self.threadpool.start(dlp_worker)
        self.laser_on()
        self.stream()
        dlp_signal_end.finished.connect(laser_off)
        laser_signal_end.finished.connect(stop_stream)



    ########################################
    #### Classical electrophysiology  ######
    ########################################
    def stim_on(self):
        self.bridge.stim_on()
        self.timings_logfile_dict['ephys']['on'] = []

    def stim_off(self):
        self.bridge.stim_off()
        self.timings_logfile_dict['ephys']['off'] = []

    def stim(self):
        self.stim_on()
        time.sleep(0.5)
        self.stim_off()

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
    win.show()
    app.exit(app.exec_())

if __name__ == "__main__":
    main()
