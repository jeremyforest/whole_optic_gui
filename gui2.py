## PyQT5
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, QMessageBox, QProgressBar, QGraphicsScene, QInputDialog
from PyQt5.QtGui import QImage, QPixmap, QPen, QPainter
import pyqtgraph as pg
from PyQt5.QtTest import QTest

from whole_optic_gui import Ui_MainWindow

## common dependencies
import argparse
import numpy as np
import os, time, sys, time
from PIL import Image, ImageDraw, ImageOps
import cv2
import matplotlib.pyplot as plt

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
        ##### gui initialization #####
        ###################################

        ## commande-line options
        self.activate_camera = False
        self.activate_laser = False
        self.activate_dlp = False
        self.activate_controller = False

        parser = argparse.ArgumentParser(description="hardware to load")
        parser.add_argument("--camera", default=False, action="store_true" , help="if you want to load the camera functions")
        parser.add_argument("--laser", default=False, action="store_true" , help="if you want to load the laser functions")
        parser.add_argument("--dlp", default=False, action="store_true" , help="if you want to load the dlp functions")
        parser.add_argument("--controler", default=False, action="store_true" , help="if you want to load the controller functions")
        args = parser.parse_args()

        if args.camera is True:
            self.activate_camera = True
        else:
             print("camera function are not loaded")

        if args.laser is True:
            self.activate_laser = True
        else:
             print("laser function are not loaded")

        if args.dlp is True:
            self.activate_dlp = True
        else:
             print("dlp function are not loaded")

        if args.controler is True:
            self.activate_controller = True
        else:
             print("controler function are not loaded")

        ##### camera #####
        if self.activate_camera is True:
            from camera.camera_control import MainCamera
            self.cam = MainCamera()
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

        ## variable reference for later use
        self.path = None
        self.save_images = False
        self.simulated = True
        self.roi_list = []
        self.camera_to_dlp_matrix = []
        # self.camera_distortion_matrix = []

        ## folder widget
        self.initialize_hardware_button.clicked.connect(self.initialize_hardware)
        self.initialize_experiment_button.clicked.connect(self.initialize_experiment)
        self.change_folder_button.clicked.connect(self.change_folder)

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


    ###################################
    ########## GUI code ###############
    ###################################
    def initialize_hardware(self):
        # initialize camera parameters
        self.x_dim = self.cam.get_subarray_size()[1]
        self.y_dim = self.cam.get_subarray_size()[3]
        self.binning = self.cam.read_binning()
        self.current_binning_size_label_2.setText(str(self.cam.read_binning()))
        self.subarray_label.setText(str(self.cam.get_subarray_size()))
        self.exposure_time_value.display(self.cam.read_exposure())

    def change_folder(self):
        self.path = QFileDialog.getExistingDirectory(None, 'Select the right folder to load the image batch:', 'C:/', QFileDialog.ShowDirsOnly)
        self.current_folder_label_2.setText(str(self.path))

    def initialize_experiment(self):
        self.path = QFileDialog.getExistingDirectory(None, 'Select a folder where you want to store your data:', 'C:/', QFileDialog.ShowDirsOnly)
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
        os.makedirs(self.path)
        os.makedirs(self.path + '/dlp_images')

        with open(self.path + "/experiment_{}_info.txt".format(n),"w+") as f:       ## store basic info and comments
            f.write(time.asctime(time.localtime(time.time())))
            f.close()

        self.current_folder_label_2.setText(str(self.path)) ## show current directory in the GUI

    def save_as_png(self, array, image_name):
        plt.imsave('{}{}.png'.format(self.path, image_name), array, cmap='gray')

    def snap_image(self): ## only takes an image and saves it
        self.cam.start_acquisition()
        self.images.self.cam.get_images()
        self.image = self.images
        self.image_reshaped = self.image.reshape(int(self.x_dim/self.binning),
                                                int(self.y_dim/self.binning)) ## image needs reshaping
        self.graphicsView.setImage(self.image_reshaped)
        image_name = QInputDialog.getText(self, 'Input Dialog', 'File name:')
        self.save_as_png(self.image, image_name)

    def stream(self):
        if self.simulated:
            for i in range(1):
                self.image = np.random.rand(2048, 2048).T
                self.image_reshaped = self.image
                self.graphicsView.setImage(self.image)
                pg.QtGui.QApplication.processEvents()
        else:
            self.cam.start_acquisition()
            self.image_list = []
            for i in range(1000):
                self.images = self.cam.get_images() ## getting the images, sometimes its one other can be more
                while self.images == []:
                    QTest.qWait(500)  ## kind of a hack, need to make a better solution. Also breaks if images empty after that time
                    self.images = self.cam.get_images()
                self.image = self.images[0]  ## keeping only the 1st for projetion
                self.image_reshaped = self.image.reshape(int(self.x_dim/self.binning),
                                                        int(self.y_dim/self.binning)) ## image needs reshaping for show
                for j in range(len(self.images)): ## for saving later
                    self.image_list.append(self.images[j])
                self.graphicsView.setImage(self.image_reshaped)
                pg.QtGui.QApplication.processEvents()
            self.cam.end_acquisition()

        if self.saving_check.isChecked():
            self.save(self.image_list, self.path)

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
        self.saved_ROI_image.setImage(self.image_reshaped)
        self.roi_list = []
        self.ROI_label_placeholder.setText(str(0))

    def save(self, images, path): ### npy format
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
                image_reshaped = self.image.reshape(int(self.x_dim/self.binning),
                                                        int(self.y_dim/self.binning)) ## image needs reshaping for show
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
            self.subarray_label.setText(str(self.cam.get_subarray_size()))

    def update_internal_frame_rate(self):
        self.internal_frame_rate = self.cam.get_internal_frame_rate()
        self.internal_frame_rate_label.setText(str(self.internal_frame_rate))


    ####################
    ##### DLP part #####
    ####################
    def calibration(self):
        ## dlp img
        ## will ask for the calibration image of the dlp
        dlp_image_path = QFileDialog.getOpenFileName(self, 'Open file', 'C:/',"Image files (*.bmp)")[0]
        # dlp_image_path = "/media/jeremy/Data/CloudStation/Postdoc/Projects/Memory/Computational_Principles_of_Memory/optopatch/equipment/whole_optic_gui/dlp/Calibration_9pts.bmp"
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
        self.cam.write_exposure(0.2)
        self.cam.start_acquisition()
        time.sleep(1)
        for i in range(1):
            camera_image = self.cam.get_images()[0].reshape(2048,2048).T
        self.cam.end_acquisition()
        # camera_image_path = "/media/jeremy/Data/CloudStation/Postdoc/Projects/Memory/Computational_Principles_of_Memory/optopatch/equipment/whole_optic_gui/camera/calibration_images/camera_image2.jpeg"
        # camera_image = Image.open(camera_image_path)

        ## converting the image in greylevels to 0/1 bit format using a threshold
        thresh = 230
        fn = lambda x : 255 if x > thresh else 0
        camera_image = Image.fromarray(camera_image)
        camera_image = camera_image.convert('L').point(fn, mode='1')
        camera_image = ImageOps.invert(camera_image.convert('RGB'))
        camera_image = np.asarray(camera_image)
        ## need to tune the cv2 detector for the detection of circles in a large image
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = True
        params.minArea = 50
        params.maxArea = 10000
        params.minDistBetweenBlobs = 20
        params.filterByColor = True
        params.filterByConvexity = False
        params.minCircularity = 0.2
        detector = cv2.SimpleBlobDetector_create(params)
        # keypoints = detector.detect(camera_image)
        isFound_camera, centers_camera = cv2.findCirclesGrid(camera_image, shape, flags = cv2.CALIB_CB_SYMMETRIC_GRID + cv2.CALIB_CB_CLUSTERING, blobDetector=detector)
        if isFound_camera:
            print('found {} circle centers on images'.format(len(centers_camera)))

        ## for debug
        # camera_image_drawn = cv2.drawChessboardCorners(camera_image, shape, centers_camera, isFound_camera)
        # camera_image_drawn = Image.fromarray(camera_image_drawn)
        # camera_image_drawn.show()

        # homography_matrix = cv2.findHomography(centers_camera, centers_dlp)
        # warped_camera_image = cv2.warpPerspective(camera_image, homography_matrix[0], dsize=(608,684))
        # warped_camera_image_drawn = Image.fromarray(warped_camera_image)
        # warped_camera_image_drawn.show()

        ## performing the calculs to get the transformation matrix between the camera image and the dlp image
        self.camera_to_dlp_matrix = cv2.findHomography(centers_camera, centers_dlp)

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

        # ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(centers_camera, centers_dlp, (dlp_image.shape[0], dlp_image.shape[1]), None, None)
        # undist = cv2.undistort(camera_image, mtx, dist, None, mtx)
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
            self.display_mode_subbox_combobox.addItems(['Choose Static Image', 'Generate Static Image from ROI'])
        if index == 1: # internal test pattern
            self.dlp.set_display_mode('internal')
            self.display_mode_subbox_combobox.addItems(['Checkboard small', 'Black', 'White', 'Green', 'Blue', 'Red', 'Vertical lines 1',
                                                        'Horizontal lines 1', 'Vertical lines 2', 'Horizontal lines 2', 'Diagonal lines',
                                                        'Grey Ranp Vertical', 'Grey Ramp Horizontal', 'Checkerboard big'])
        if index == 2: # hdmi video input
            self.display_mode_subbox_combobox.addItem('Choose HDMI Video Sequence')
        if index == 3: # pattern sequence display
            self.dlp.set_display_mode('pattern')
            self.display_mode_subbox_combobox.addItems(['Choose Pattern Sequence To Load', 'Generate Multiple Images with One ROI Per Image'])

    def choose_action(self, index):
        ## Static image mode
        if self.display_mode_combobox.currentIndex() == 0: ## static image
            if index == 0: ## choose static image
                img_path = QFileDialog.getOpenFileName(self, 'Open file', 'C:/',"Image files (*.jpg *.bmp)")
                img = Image.open(img_path[0])
                if img.size == (608,684):
                    self.dlp.display_static_image(img_path[0])
                else:
                    warped_image = cv2.warpPerspective(img, self.camera_to_dlp_matrix[0],(608, 684))
                    center = (608 / 2, 684 / 2)
                    M = cv2.getRotationMatrix2D(center, 180, 1.0)
                    warped_image_rotated = cv2.warpAffine(warped_image, M, (608, 684))
                    cv2.imwrite(img_path[0] + 'warped.bmp', warped_image)
                    self.dlp.display_static_image(img_path[0] + 'warped.bmp')

            elif index == 1:  ##generate static image from ROI
                black_image = Image.new('1', (2048,2048), color=0) ## need to make this dependant upon fov size and not 2048
                black_image_with_ROI = black_image
                for nb in range(len(self.roi_list)):
                    x0, y0 = (self.roi_list[nb]['pos'][0], self.roi_list[nb]['pos'][1])
                    x1, y1 = (self.roi_list[nb]['pos'][0] + self.roi_list[nb]['size'][0], self.roi_list[nb]['pos'][1] + self.roi_list[nb]['size'][1])
                    # x0,y0,x1,y1 = 0, 0, 1000, 2048
                    draw = ImageDraw.Draw(black_image_with_ROI)
                    draw.rectangle([(x0, y0), (x1, y1)], fill="white", outline=None)
                black_image_with_ROI = black_image_with_ROI.convert('RGB') ## for later the warpPerspective function needs a shape of (:,:,3)
                black_image_with_ROI = np.asarray(black_image_with_ROI)
                black_image_with_ROI_warped = cv2.warpPerspective(black_image_with_ROI, self.camera_to_dlp_matrix[0],(608,684))

                center = (608 / 2, 684 / 2)
                M = cv2.getRotationMatrix2D(center, 180, 1.0)
                black_image_with_ROI_warped_rotated = cv2.warpAffine(black_image_with_ROI_warped, M, (608, 684))

                cv2.imwrite(self.path + '/dlp_images' + '/ROI_warped' + '.bmp', black_image_with_ROI_warped_rotated)

        ## Internal test pattern mode
        elif self.display_mode_combobox.currentIndex() == 1: ## internal test pattern
            if index == 0: ## Checkboard small
                self.dlp.checkboard_small()
            if index == 1: # Black
                self.dlp.black()
            if index == 2: ## White
                self.dlp.white()
            if index == 3: ## Green
                self.dlp.green()
            if index == 4: ## Blue
                self.dlp.blue()
            if index == 5: ## Red
                self.dlp.red()
            if index == 6: ## Vertical lines 1
                self.dlp.horizontal_lines_1()
            if index == 7: ## Horizontal lines 1
                self.dlp.vertical_lines_1()
            if index == 8: ## Vertical lines 2
                self.dlp.horizontal_lines_2()
            if index == 9: ## Horizontal lines 2
                self.dlp.vertical_lines_2()
            if index == 10: ## Diagonal lines
                self.dlp.diagonal_lines()
            if index == 11: ## Grey Ramp Vertical
                self.dlp.grey_ramp_vertical()
            if index == 12: ## Grey Ramp Horizontal
                self.dlp.grey_ramp_horizontal()
            if index == 13: ## Checkerboard Big
                self.dlp.checkerboard_big()

        ## HDMI Video Input mode
        elif self.display_mode_combobox.currentIndex == 2:  ## HDMI video sequence
            print("mode not yet implemented")

        ## Pattern sequence mode
        elif self.display_mode_combobox.currentIndex() == 3:  ## Pattern sequence
            if index == 1: # Choose Pattern Sequence To Load
                time, ok = QInputDialog.getInt(self, 'Input Dialog', 'Duration of pattern exposition (in µs)')   ## time to be given in microseconds
                image_folder = QFileDialog.getExistingDirectory(self, 'Select Image Folder where DLP images are stored')
                InputTriggerDelay = 0
                AutoTriggerPeriod = 3333334
                ExposureTime = 3333334
                self.dlp.display_image_sequence(image_folder, InputTriggerDelay, AutoTriggerPeriod, ExposureTime)

            if index == 0: ## Generate Multiple Images with One ROI Per Image
                for nb in range(len(self.roi_list)):
                    black_image = Image.new('1', (2048,2048), color=0) ## need to make this dependant upon fov size and not 2048
                    black_image_with_ROI = black_image
                    x0, y0 = (self.roi_list[nb]['pos'][0], self.roi_list[nb]['pos'][1])
                    x1, y1 = (self.roi_list[nb]['pos'][0] + self.roi_list[nb]['size'][0], self.roi_list[nb]['pos'][1] + self.roi_list[nb]['size'][1])
                    draw = ImageDraw.Draw(black_image_with_ROI)
                    draw.rectangle([(x0, y0), (x1, y1)], fill="white", outline=None)
                    black_image_with_ROI = black_image_with_ROI.convert('RGB') ## for later the warpPerspective function needs a shape of (:,:,3)
                    black_image_with_ROI = np.asarray(black_image_with_ROI)
                    black_image_with_ROI_warped = cv2.warpPerspective(black_image_with_ROI, self.camera_to_dlp_matrix[0],(608, 684))
                    cv2.imwrite(self.path + '/dlp_images' + '/ROI_warped_' + f"{nb}" + '.bmp', black_image_with_ROI_warped)



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
