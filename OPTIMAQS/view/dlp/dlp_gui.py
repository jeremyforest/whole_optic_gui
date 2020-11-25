## PyQT5
from PyQt5 import uic
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, pyqtSignal, QThreadPool, QObject, QTimer, QEventLoop
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, \
                            QMessageBox, QProgressBar, QGraphicsScene, QInputDialog, QDialog
from PyQt5.QtGui import QImage, QPixmap, QPen, QPainter
from PyQt5.QtTest import QTest
import pyqtgraph as pg

## general imports
import os
import numpy as np
import json
import time
from PIL import Image, ImageDraw, ImageOps
import cv2
import subprocess
import itertools

## Custom imports
from OPTIMAQS.utils.signals import Signals
from OPTIMAQS.utils.json_functions import jsonFunctions
from OPTIMAQS.utils.worker import Worker
from OPTIMAQS.utils.debug import Pyqt_debugger


class DLPGui(QWidget):
    def __init__(self, path=None, info_logfile_path=None, timings_logfile_path=None):
        """
        GUI for the Digital Light Processor / Digital Micromirror Device
        """
        super(DLPGui, self).__init__()

        ### GUI related
        self.dlp_ui = uic.loadUi('OPTIMAQS/view/dlp/dlp.ui', self)
        self.dlp_ui.show()

        self.path = self.path_experiment = jsonFunctions.open_json(
                                          'OPTIMAQS/config_files/last_experiment.json')
        self.camera_to_dlp_matrix = []
        self.calibration_dlp_camera_matrix_path = 'C:\\Users\\barral\\Desktop\\whole_optic_gui\\OPTIMAQS\\view\\dlp\\calibration_matrix.json'
        if os.path.isfile(self.calibration_dlp_camera_matrix_path):
            print('Calibration matrix already exists, using it as reference')
            with open(self.calibration_dlp_camera_matrix_path) as file:
                self.camera_to_dlp_matrix = np.array(json.load(file))
        else:
            print('no calibration matrix existing. Need to rerun calibration')
        ## initialize dlp
        self.import_dlp_model()
        self.actions()
        self.initialize_dlp_parameters()

        ## JSON files
#        self.info_logfile_path = self.path + '/experiment_' + self.path[-1] + '_info.json'
        self.info_logfile_path = info_logfile_path
        self.info_logfile_dict = {}
        self.info_logfile_dict['roi'] = []

#        self.timings_logfile_path = self.path + '/experiment_' + self.path  [-1] + '_timings.json'
        self.timings_logfile_path = timings_logfile_path
        self.timings_logfile_dict = {}
        self.timings_logfile_dict['dlp'] = {}
        self.timings_logfile_dict['dlp']['on'] = []
        self.timings_logfile_dict['dlp']['off'] = []

        ## timings
        self.perf_counter_init = jsonFunctions.open_json('OPTIMAQS/config_files/perf_counter_init.json')

        ## threads
        self.threadpool = QThreadPool()

    def import_dlp_model(self):
        """
        import dlp model-type script
        """
        try:
            from OPTIMAQS.model.dlp.dlp_control import Dlp
            self.dlp = Dlp()
            self.dlp.connect()
        except:
            print('cannot import dlp model')

    def initialize_dlp_parameters(self):
        """
        Initialize all the dlp variables
        """
        ## custom signals
        self.dlp_signal = Signals()
        self.dlp_signal.finished.connect(self.turn_dlp_off)

    def actions(self):
        """
        Define actions for buttons and items.
        """
        ## DLP control
        self.display_mode_combobox.activated.connect(self.display_mode)
        self.display_mode_subbox_combobox.activated.connect(self.choose_action)

    def reset(self, timings_logfile_path, info_logfile_path, path_experiment):
        self.info_logfile_path = info_logfile_path
        self.timings_logfile_dict = {}
        self.timings_logfile_dict['dlp'] = {}
        self.timings_logfile_dict['dlp']['on'] = []
        self.timings_logfile_dict['dlp']['off'] = []
        
        self.timings_logfile_path = timings_logfile_path
        self.info_logfile_dict = {}
        self.info_logfile_dict['roi'] = []
        
        self.path = path_experiment
        
    def display_mode(self, index):  #TODO:can this be implemented in QDesigner directly  ?
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

    def choose_action(self, index, dlp_image_path=None):
        ## Static image mode
        if self.display_mode_combobox.currentIndex() == 0: ## load image
            if index == 0: ## choose static image
                if dlp_image_path == None:
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
                else:
                    img = Image.open(dlp_image_path)
                    if img.size == (608,684):
                        self.dlp.display_static_image(dlp_image_path)
                        self.dlp.set_display_mode('internal')
                        self.dlp.black()
                    else:
                        warped_image = cv2.warpPerspective(img, self.camera_to_dlp_matrix,(608, 684))
                        warped_flipped_image = cv2.flip(warped_image, 0)
                        cv2.imwrite(dlp_image_path + 'warped.bmp', warped_flipped_image)
                        # self.dlp.display_static_image(self.dlp_image_path[0] + 'warped.bmp')

            elif index == 1:  ##generate static image from ROI
                self.info_logfile_dict = jsonFunctions.open_json(self.info_logfile_path)
                self.roi_list = self.info_logfile_dict['roi']
                black_image = Image.new('1', (2048,2048), color=0) ## 2048 because we want the full fov
                black_image_with_ROI = black_image
                for nb in range(len(self.roi_list[0])):
                    x0, y0 = (self.roi_list[0][nb]['pos'][0], self.roi_list[0][nb]['pos'][1])
                    x1, y1 = (self.roi_list[0][nb]['pos'][0] + self.roi_list[0][nb]['size'][0],
                              self.roi_list[0][nb]['pos'][1] + self.roi_list[0][nb]['size'][1])
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
            self.info_logfile_dict = jsonFunctions.open_json(self.info_logfile_path)
            self.roi_list = self.info_logfile_dict['roi']
            if index == 0: ## Generate ROI Files and Compile Movie From Images
                self.generate_one_image_per_roi(self.roi_list)
                time.sleep(5)
                self.movie_from_images()
                # self.generate_every_paired_combination_movie(self.roi_list)
            elif index == 1: ## Choose HDMI Video Sequence
                ## is the screen number working ? neede to test with dlp screen. shouhld work if dlp is screen 1
                run_vlc_worker = Worker(self.run_vlc)
                self.threadpool.start(run_vlc_worker)

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

    def run_vlc(self):
        vlc_path = "C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe"
        video_path = f"{self.path}/dlp_images/dlp_movie.avi"
        subprocess.call([vlc_path, '--play-and-exit', '-f', '--qt-fullscreen-screennumber=4|5', os.path.abspath(video_path)], shell=False)
        self.timings_logfile_dict['dlp']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)


    def turn_dlp_off(self):
        self.dlp.set_display_mode('internal')
        self.dlp.black()
        self.timings_logfile_dict['dlp']['off'].append((time.perf_counter() - self.perf_counter_init)*1000)
        jsonFunctions.update_timings_to_json(self.timings_logfile_dict, self.timings_logfile_path)
        print('dlp end signal received')

    def generate_one_image_per_roi(self, roi_list):
        for nb in range(len(roi_list[0])):
            black_image = Image.new('1', (2048,2048), color=0)
            black_image_with_ROI = black_image
            x0, y0 = (roi_list[0][nb]['pos'][0], roi_list[0][nb]['pos'][1])
            x1, y1 = (roi_list[0][nb]['pos'][0] + roi_list[0][nb]['size'][0],
                      roi_list[0][nb]['pos'][1] + roi_list[0][nb]['size'][1])
            draw = ImageDraw.Draw(black_image_with_ROI)
            draw.rectangle([(x0, y0), (x1, y1)], fill="white", outline=None)
            black_image_with_ROI = black_image_with_ROI.convert('RGB') ## for later the warpPerspective function needs a shape of (:,:,3)
            black_image_with_ROI = np.asarray(black_image_with_ROI)
            black_image_with_ROI_warped = cv2.warpPerspective(black_image_with_ROI, self.camera_to_dlp_matrix,(608,684))
            black_image_with_ROI_warped_flipped = cv2.flip(black_image_with_ROI_warped, 0)
            cv2.imwrite(self.path + '/dlp_images' + '/ROI_warped_' + f"{nb}" + '.bmp', black_image_with_ROI_warped_flipped)


    def generate_every_paired_combination_movie(self,
                                                roi_list,
                                                time_stim_image=20,
                                                inter_image_interval=200):
        filenames = os.listdir(f"{self.path}/dlp_images/")
        size_image = cv2.imread(f"{self.path}/dlp_images/{filenames[1]}")
        h, v, z = size_image.shape
        fps = 1000
        repeat_stim_image = int(time_stim_image/1000 * fps)
        repeat_black_image = int(inter_image_interval/1000 * fps)

        nb_roi = range(len(roi_list[0]))
        paired_combinations = list(itertools.combinations(nb_roi, 2))

        out = cv2.VideoWriter(f"{self.path}/dlp_images/dlp_movie_paired_combination.avi",
                              cv2.VideoWriter_fourcc(*'MJPG'),
                              fps,
                              (v,h))
        filenames_repeat = []
        for pair in paired_combinations:
            # pair = paired_combinations[0]
            filenames_repeat_temp = []
            for roi in pair:
                # roi = pair[1]
                filenames_repeat_temp.append(np.repeat(filenames[roi], repeat_stim_image))
            filenames_repeat.append(np.array(filenames_repeat_temp).flatten().flatten())
        filenames_repeat = np.array(filenames_repeat).flatten()

        idx_insert = np.arange(0, len(filenames_repeat), repeat_stim_image*2) 
        # idx_insert = np.arange(0, len(paired_combinations), repeat_stim_image)
        black_images = ['b']*repeat_black_image

        for i in idx_insert[::-1]:
            if i == idx_insert[-1]:
                filenames_for_videos = np.insert(filenames_repeat,
                                                 i,
                                                 np.array(black_images))
            else:
                filenames_for_videos = np.insert(filenames_for_videos,
                                                 i,
                                                 np.array(black_images))
        for filename in filenames_for_videos:
            if filename == 'b':
                img = np.uint8(np.zeros((h,v,z)))
            else:
                img = cv2.imread(f"{self.path}/dlp_images/{filename}")
            out.write(img)
        out.release()


    def movie_from_images(self, time_stim_image=25, inter_image_interval=100):
        ## fps = 1000 so that resolution min is 1ms
        ## if stim = 5 ms and delay betwee, stim = 25 ms
        ## nb of stim images = 5/1000*1000 = 5
        ## nb of black images =25/1000*1000 = 25
        filenames = os.listdir(f"{self.path}/dlp_images/")
        size_image = cv2.imread(f"{self.path}/dlp_images/{filenames[1]}")
        h, v, z = size_image.shape
        fps = 1000
        repeat_stim_image = int(time_stim_image/1000 * fps)
        repeat_black_image = int(inter_image_interval/1000 * fps)

        out = cv2.VideoWriter(f"{self.path}/dlp_images/dlp_movie.avi",
                              cv2.VideoWriter_fourcc(*'MJPG'),
                              fps,
                              (v,h))
        filenames_repeat = np.repeat(filenames, repeat_stim_image)
        idx_insert = np.arange(0, len(filenames_repeat), repeat_stim_image)
        black_images = ['b']*repeat_black_image

        for i in idx_insert[::-1]:
            if i == idx_insert[-1]:
                filenames_for_videos = np.insert(filenames_repeat,
                                                 i,
                                                 np.array(black_images))
            else:
                filenames_for_videos = np.insert(filenames_for_videos,
                                                 i,
                                                 np.array(black_images))
        for filename in filenames_for_videos:
            if filename == 'b':
                img = np.uint8(np.zeros((h,v,z)))
            else:
                img = cv2.imread(f"{self.path}/dlp_images/{filename}")
            out.write(img)
        out.release()



    def turn_off(self):
        self.dlp.disconnect()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DLPGui()
    win.showMaximized()
    app.exit(app.exec_())
