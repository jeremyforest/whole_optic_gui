from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, QMessageBox, QProgressBar
from PyQt5.QtGui import QImage
import pyqtgraph as pg

import numpy as np
import os, time, sys, time

from whole_optic_gui import *
from camera.camera_control import MainCamera

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.retranslateUi(self)

        ##camera initilization
        if sys.platform == "win32": ## main camera is the hamamatsu camera that only works on windows
            self.cam = MainCamera()
        else:
            print("Main camera / Hamamatsu camera will not work")

        ## variable reference for later use
        self.path = None


        ## folder widget
        self.change_folder_button.clicked.connect(self.change_folder)
        self.initialize_experiment_button.clicked.connect(self.initialize_experiment)

        #camera widget
        self.stream_button.clicked.connect(self.stream)
        # self.saving_check.stateChanged.connect(self.save)
        self.replay_button.clicked.connect(self.replay)
        self.exposure_time_bar.valueChanged.connect(self.exposure_time)

        self.binning_combo_box.addItem("1x1", 1)
        self.binning_combo_box.addItem("2x2", 2)
        self.binning_combo_box.addItem("4x4", 4)
        self.binning_combo_box.activated.connect(self.binning)

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



    def stream(self):       ## stream images in continuous flow
        simulated = True
        if simulated:
            self.image = np.random.rand(256, 256)
            timer = pg.QtCore.QTimer(self)  ## timer for updating the image displayed
            timer.timeout.connect(self.update)
            timer.start(0.01)
        else:
            self.cam.start_acquisition()
            self.images = self.cam.get_images() ## gettint the images, sometimes its one other can be more
            self.image = self.images[0]  ## keeping only the 1st for projetion
            self.image_reshaped = self.image.reshape(2048, 2048) ## needs reshaping
            timer = pg.QtCore.QTimer(self)
            timer.timeout.connect(self.update)
            timer.start(0.01)
            self.cam.end_acquisition()

    def update(self):  ## need to put that in its own thread
        simulated = True
        if self.saving_check == Qt.Checked:
            save_images = True
        if simulated:
            for i in range(50):
                self.image = np.random.rand(256, 256)
                self.graphicsView.setImage(self.image)
                if save_images:
                    self.save(self.images, i, self.path)
        else:
            for i in range(100):
                self.images = self.cam.get_images() ## gettint the images, it can be 1 but also many images grabbed at once
                self.image = self.images[0]  ## keeping only the 1st image for projection
                self.image_reshaped = self.image.reshape(2048, 2048) ## needs reshaping
                self.graphicsView.setImage(self.image_reshaped)

    def save(self, images, i, path): ### npy format
        for y in range(len(images)):
            image = images[y]
            np.save(file = str(path) + '/image{}.npy'.format(str(i)), arr=image)
            print("saved file")

    def replay(self):
        if path == None:
            print("select a folder first")
        else:
            images_nb = len(os.listdir(self.path))
            images = []
            for i in range(images_nb):
                image = np.load(str(eslf.path) + '/image{}.npy'.format(str(i)))
                image_reshaped = image.reshape(2048, 2048)
                images.append(image_reshaped)
            for img in images:
                print(img)
                self.graphicsView.setImage(img.T)
                pg.QtGui.QApplication.processEvents()   ## maybe needs to be recoded in ints own thread with the update function ?

    def exposure_time(self, value):
        value /= 10
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

    def bye(self):
        self.cam.shutdown()
        sys.exit()




def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exit(app.exec_())

if __name__ == "__main__":
    main()
