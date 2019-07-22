from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, QMessageBox, QProgressBar, QInputDialog
from PyQt5.QtGui import QImage
import pyqtgraph as pg
from PyQt5.QtTest import QTest

import numpy as np
import os, time, sys, time
import matplotlib.pyplot as plt

from whole_optic_gui import Ui_MainWindow
import argparse

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
        self.simulated = True

        ## folder widget
        self.change_folder_button.clicked.connect(self.change_folder)
        self.initialize_experiment_button.clicked.connect(self.initialize_experiment)

        #camera widget
        self.snap_image_button.clicked.connect(self.snap_image)
        self.stream_button.clicked.connect(self.stream)
        self.replay_button.clicked.connect(self.replay)
        self.exposure_time_bar.valueChanged.connect(self.exposure_time)
        self.binning_combo_box.activated.connect(self.binning)

        ## dlp widget
        self.display_internal_pattern_combobox.activated.connect(self.internal_test_pattern)

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


    def save_as_png(self, array, image_name):
        plt.imsave('{}{}.png'.format(self.path, image_name), array, cmap='gray')

    def snap_image(self):
        self.cam.start_acquisition()
        self.images.self.cam.get_images()
        self.image = self.images
        self.image_reshaped = self.image.reshape(2048, 2048)
        self.graphicsView.setImage(self.image_reshaped)
        image_name = QInputDialog.getText(self, 'Input Dialog', 'File name:')
        self.save_as_png(self.image, image_name)

    def stream(self):
        if self.simulated:
            for i in range(10):
                self.image = np.random.rand(256, 256)

    #            timer = pg.QtCore.QTimer(self)  ## timer for updating the image displayed
    #            timer.timeout.connect(self.update)
    #            timer.start(0.01)

                self.graphicsView.setImage(self.image)
                pg.QtGui.QApplication.processEvents()
        else:
            self.cam.start_acquisition()
            for i in range(1000):
                self.images = self.cam.get_images() ## getting the images, sometimes its one other can be more
                while self.images == []:
                    QTest.qWait(500)  ## kind of a hack, need to make a better solution. Also breaks if images empty after that time
                    self.images = self.cam.get_images()
                self.image = self.images[0]  ## keeping only the 1st for projetion
                self.image_reshaped = self.image.reshape(2048, 2048) ## image needs reshaping for show
                for j in range(len(self.images)): ## for saving later
                    self.image_list.append(self.images[i])
                self.graphicsView.setImage(self.image_reshaped)
                pg.QtGui.QApplication.processEvents()
            self.cam.end_acquisition()

        if self.saving_check.isChecked():
            self.save(self.image_list, self.path)

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
                image = np.load(str(self.path) + '/image{}.npy'.format(str(i)))
                image_reshaped = image.reshape(2048, 2048)
                images.append(image_reshaped)
            for img in images:
                self.graphicsView.setImage(img.T)
                pg.QtGui.QApplication.processEvents()   ## maybe needs to be recoded in ints own thread with the update function ?

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

    def internal_test_pattern(self, index):
		### these indexes are the ones in the gui file at the end
        if index == 0:
            pass
        elif index == 2:
            self.dlp.turn_off_light()
        elif index == 1:
            self.dlp.turn_on_blue()



    ####################
    #### Laser part ####
    ####################
    def laser_on(self):
        self.laser.turn_on()
    def laser_off(self):
        self.laser.turn_off()

    #######################
    #### Controler part ####
    #######################
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
