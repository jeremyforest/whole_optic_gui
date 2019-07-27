## PyQT5
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, QMessageBox, QProgressBar, QGraphicsScene
from PyQt5.QtGui import QImage, QPixmap, QPen, QPainter
import pyqtgraph as pg
from PyQt5.QtTest import QTest
from whole_optic_gui import Ui_MainWindow

## common dependencies
import numpy as np
import os, time, sys, time
from PIL import Image, ImageDraw
import cv2
import matplotlib.pyplot as plt

# own scripts
import clickable_matplotlib_graph
from camera.camera_control import MainCamera
from dlp.dlp_control import Dlp
# from laser.laser_control import CrystalLaser
# from controler.manipulator_command import Scope


def debug_trace():
  '''Set a tracepoint in the Python debugger that works with Qt'''
  from PyQt5.QtCore import pyqtRemoveInputHook
  from pdb import set_trace
  pyqtRemoveInputHook()
  set_trace()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.retranslateUi(self)

        ###################################
        ##### hardware initialization #####
        ###################################

        ##### camera #####
        if sys.platform == "win32": ## main camera is the hamamatsu camera that only works on windows
           self.cam = MainCamera()
        else:
           print("Main camera / Hamamatsu camera will not work")
        ##### dlp #####
        self.dlp = Dlp()
        self.dlp.connect()
        # ##### laser #####
        # self.laser = CrystalLaser()
        # self.laser.connect()
        # ##### manipulator #####
        # self.scope = Scope()

        ## variable reference for later use
        self.path = None
        self.save_images = False
        self.simulated = False
        self.roi_list = []
        self.dlp_transformation_matrix = []


        ## folder widget
        self.change_folder_button.clicked.connect(self.change_folder)
        self.initialize_experiment_button.clicked.connect(self.initialize_experiment)

        #camera widget
        self.stream_button.clicked.connect(self.stream)
        # self.saving_check.stateChanged.connect(self.save)
        self.replay_button.clicked.connect(self.replay)
        self.exposure_time_bar.valueChanged.connect(self.exposure_time)
        self.binning_combo_box.activated.connect(self.binning)

        #roi
        self.save_ROI_button.clicked.connect(self.roi)
        self.reset_ROI_button.clicked.connect(self.reset_roi)

        self.saved_ROI_image.ui.histogram.hide()
        self.saved_ROI_image.ui.roiBtn.hide()
        self.saved_ROI_image.ui.menuBtn.hide()

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

    def change_folder(self):
        self.path = QFileDialog.getExistingDirectory(None, 'Select the right folder to load the image batch:', 'C:/', QFileDialog.ShowDirsOnly)
        self.current_folder_label_2.setText(str(self.path))

    def initialize_experiment(self):
        self.path = QFileDialog.getExistingDirectory(None, 'Select a folder where you want to store your data:', 'C:/', QFileDialog.ShowDirsOnly)
        date = time.strftime("%d_%m_%Y")
        self.path = os.path.join(self.path, date)
        if not os.path.exists(self.path):
            os.makedirs(self.path) ## make a folder with the date of today if it does not already exists
        n = 1
        self.path_temp = os.path.join(self.path, 'experiment_' + str(n))  ## in case of multiple experiments a day, need to create several subdirectory
        while os.path.exists(self.path_temp):                             ## but necesarry to check which one aleady exists
            n += 1
            self.path_temp = os.path.join(self.path, 'experiment_' + str(n))
        self.path = self.path_temp
        os.makedirs(self.path)

        with open(self.path + "/experiment_{}_info.txt".format(n),"w+") as f:       ## store basic info and comments
            f.write(time.asctime(time.localtime(time.time())))
            f.close()

        self.current_folder_label_2.setText(str(self.path)) ## show current directory in the GUI


        ##get camera parameters     ## get camera parameters to show up in the GUI at initialization
        ## binning, exposure time, array size    what else ?
        ## current dlp dsplay mode
        ## laser state


    def stream(self):       ## stream images in continuous flow
        if self.simulated:
            for i in range(500):
                self.image = np.random.rand(256, 256)
                self.image_reshaped = self.image
    #            timer = pg.QtCore.QTimer(self)  ## timer for updating the image displayed
    #            timer.timeout.connect(self.update)
    #            timer.start(0.01)
                self.graphicsView.setImage(self.image)
                pg.QtGui.QApplication.processEvents()

        else:
            self.cam.start_acquisition()
            for i in range(1000):

                self.images = self.cam.get_images() ## getting the images, sometimes its one other can be more
                if self.images == []:
                    QTest.qWait(500) ## temporary hack - doesn't really work for long exposure time
                    self.images = self.cam.get_images()
                self.image = self.images[0]  ## keeping only the 1st for projetion
                self.image_reshaped = self.image.reshape(2048, 2048) ## needs reshaping

            ### the timer makes it impossible to get new images for whatever reason, when end_acquisition is here and when I
            ### remove it it works but super slow
#            timer = pg.QtCore.QTimer(self)
#            timer.timeout.connect(self.update)
#            timer.start(0.01)

                self.graphicsView.setImage(self.image_reshaped)
                pg.QtGui.QApplication.processEvents()
#                self.save(self.images, i, self.path)

            self.cam.end_acquisition()

    def roi(self):
        axes = (0, 1)
        self.saved_ROI_image.setImage(self.image_reshaped) ## get the image into the ROI graphic interface

        # data, coords = self.graphicsView.roi.getArrayRegion(self.image_reshaped.view(), self.graphicsView.imageItem, axes, returnMappedCoords=True) ## get the roi data and coords
        # self.roi_list.append(coords)

        roi_state = self.graphicsView.roi.getState()
        print(roi_state)
        self.roi_list.append(roi_state)

        pen = QPen(Qt.red, 0.1) ## draw on the image to represent the roi
        for nb in range(len(self.roi_list)):
            r = pg.ROI(pos = (self.roi_list[nb]['pos'][0], self.roi_list[nb]['pos'][1]), \
                                size= (self.roi_list[nb]['size'][0], self.roi_list[nb]['size'][1]), \
                                angle = self.roi_list[nb]['angle'], pen=pen, movable=False, removable=False)
            self.saved_ROI_image.getView().addItem(r)
        self.ROI_label_placeholder.setText(str(len(self.roi_list)))

    def reset_roi(self):
        self.saved_ROI_image.getView().clear()
        self.roi_list = []
        self.ROI_label_placeholder.setText(str(0))

#    def update(self):  ## need to put that in its own thread
#        simulated = False
##        if self.saving_check == Qt.Checked:
##            save_images = True
#        if simulated:
#            for i in range(50):
#                self.image = np.random.rand(256, 256)
#                self.graphicsView.setImage(self.image)
##                if save_images:
##                    self.save(self.images, i, self.path)
#        else:
#            for i in range(50):
#                self.images = self.cam.get_images() ## gettint the images, it can be 1 but also many images grabbed at once
#                self.image = self.images[0]  ## keeping only the 1st image for projection
#                self.image_reshaped = self.image.reshape(2048, 2048) ## needs reshaping
#                self.graphicsView.setImage(self.image_reshaped)

    def save(self, images, i, path): ### npy format
        for y in range(len(images)):
            image = images[y]
            np.save(file = str(path) + '/image{}.npy'.format(str(i)), arr=image)
            print("saved file")

    def replay(self):
        if self.path == None:
            print("select a folder first")
        else:
            images_nb = len(os.listdir(self.path))
            images = []
            for i in range(images_nb):
                image = np.load(str(self.path) + '/image{}.npy'.format(str(i)))
                image_reshaped = image.reshape(2048, 2048)
                images.append(image_reshaped)
            for img in images:
                self.graphicsView.setImage(img.T)
                pg.QtGui.QApplication.processEvents()   ## maybe needs to be recoded in its own thread with the update function ?

    def exposure_time(self, value):
        value /= 100
        self.cam.write_exposure(value)
        read_value = self.cam.read_exposure()
        self.exposure_time_value.display(read_value)

    def binning(self, index):
        if index == 1:
            self.cam.write_binning(1)
        if index == 2:
            self.cam.write_binning(2)
        if index == 4:
            self.cam.write_binning(4)


    ####################
    ##### DLP part #####
    ####################
    def calibration(self):
        ## will ask for the calibration image
        # calibration_image_path = QFileDialog.getOpenFileName(self, 'Open file', 'C:/',"Image files (*.bmp)")[0]
        # debug_trace()
        calibration_image_path = 'C:/Users/barral/Desktop/whole_optic_gui-roi/dlp/Calibration_9pts.bmp'
        # calibration_image_path = "/media/jeremy/Data/CloudStation/Postdoc/Projects/Memory/Computational_Principles_of_Memory/optopatch/equipment/whole_optic_gui/dlp/Calibration_9pts.bmp"
        ## dlp img
        calibration_image = Image.open(calibration_image_path)
        dlp_image = np.asarray(calibration_image, dtype=np.uint8)
        graph = clickable_matplotlib_graph.Clickable_matplotlib_graph(calibration_image_path)
        coords_points_calib_dlp = graph.getCoord()
        ## projecting the calibration image with the dlp to get the camera image
        self.dlp.display_static_image(calibration_image_path[0])
        camera_image = self.cam.get_images()[0].reshape(2048,2048)
        graph = clickable_matplotlib_graph.Clickable_matplotlib_graph(camera_image)
        coords_points_calib_camera = graph.getCoord()
        ## performing the calculs to get the transformation matrix between the camera image and the dlp image
        self.dlp_transformation_matrix = cv2.getPerspectiveTransform(coords_points_calib_camera,coords_points_calib_dlp)
        return self.dlp_transformation_matrix

    def display_mode(self, index):
        self.display_mode_subbox_combobox.clear()
        if index == 0: # static image
            self.dlp.set_display_mode('static')
            self.display_mode_subbox_combobox.addItem('Choose Static Image')
            self.display_mode_subbox_combobox.addItem('Generate Static Image from ROI')
        if index == 1: # internal test pattern
            self.dlp.set_display_mode('internal')
            self.display_mode_subbox_combobox.addItems  (['Solid Blue', 'Solid Black', 'ANSI 4×4 Checkerboard'])
        if index == 2: # hdmi video input
            self.display_mode_subbox_combobox.addItem('Choose HDMI Video Sequence')
        if index == 3: # pattern sequence display
            self.dlp.set_display_mode('pattern')
            self.display_mode_subbox_combobox.addItems(['Generate Pattern Sequence', 'Choose Pattern Sequence To Load'])

    def choose_action(self, index):
        ## Static image mode
        if self.display_mode_combobox.currentIndex() == 0: ## static image
            if index == 0: ## choose static image
                img_path = QFileDialog.getOpenFileName(self, 'Open file', 'C:/',"Image files (*.jpg *.bmp)")
                img = Image.open(img_path[0])
                if img.size == (608, 684):
                    self.dlp.display_static_image(img_path[0])
                else:
                    new_img = cv2.warpPerspective(img, self.dlp_transformation_matrix,(608, 684))
                    cv2.imwrite(img_path[0] + '.bmp', new_img) ## to do : create temp folder for storage/retrieval
                    self.dlp.display_static_image(img_path[0] + '.bmp')
            elif index == 1:  ##generate static image from ROI
                black_image = Image.new('1', (2048,2048), color=0)
                black_image_with_ROI = black_image
                for nb in range(len(self.roi_list)):
                    x0, y0 = (self.roi_list[nb]['pos'][0], self.roi_list[nb]['pos'][1])
                    x1, y1 = (self.roi_list[nb]['pos'][0] + self.roi_list[nb]['size'][0], self.roi_list[nb]['pos'][1] + self.roi_list[nb]['size'][1])
                    draw = ImageDraw.Draw(black_image_with_ROI)
                    draw.rectangle([(x0, y0), (x1, y1)], fill="white", outline=None)
                black_image_with_ROI_warped = cv2.warpPerspective(black_image_with_ROI, self.dlp_transformation_matrix,(608, 684))
                cv2.imwrite('black_image_with_ROI_warped' + '.bmp', black_image_with_ROI_warped) ## to do: save in specific folder for archive
                self.dlp.display_static_image('black_image_with_ROI_warped' + '.bmp')

        ## Internal test pattern mode
        elif self.display_mode_combobox.currentIndex() == 1: ## internal test pattern
            # in order:
            if index == 0:  #solid blue
                self.dlp.turn_on_blue()
            if index == 1: # solid black
                self.dlp.turn_off_light()
            if index == 2: ## ANSI 4×4 Checkerboard
                self.dlp.checkerboard()

        # HDMI Video Input
        elif self.display_mode_combobox.currentIndex == 2:  ## HDMI video sequence
            print("mode not yet implemented")

        ## Pattern sequence mode  ## need to finish when static image generation sure that works
        elif self.display_mode_combobox.currentIndex() == 3:  ## Pattern sequence
            if index == 0: # Generate Pattern Sequence
                black_image = np.zeros((2048, 2048))

                file_out = "test1.bmp"
                img.save(file_out)

            if index == 1: # Choose Pattern Sequence To Load
                pass


    ####################
    #### Laser part ####
    ####################
    def laser_on(self):
        self.laser.turn_on()
    def laser_off(self):
        self.laser.turn_off()

    ########################
    #### Controler part ####
    ########################
    def left(self):
        self.scope.move_left()

    def right(self):
        self.scope.move_right()

    def backward(self):
        self.scope.move_backward()

    def forward(self):
        self.scope.move_forward()

    def up(self):
        self.scope.up()

    def down(self):
        self.scope.down()

    def stop_mouvment(self):
        self.scope.stop_mouvment()

    ####################
    #### Clean exit ####
    ####################
    def bye(self):
        # self.cam.shutdown()
        # self.dlp.disconnect()
        # self.laser.disconnect()
        sys.exit()


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exit(app.exec_())

if __name__ == "__main__":
    main()
