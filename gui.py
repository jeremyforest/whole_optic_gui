from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, QMessageBox, QProgressBar
from PyQt5.QtGui import QImage
import pyqtgraph as pg

import numpy as np
import matplotlib.pyplot as plt
import os, time

from camera.camera_control import MainCamera


def debug_trace():
  '''Set a tracepoint in the Python debugger that works with Qt'''
  from PyQt5.QtCore import pyqtRemoveInputHook
  from pdb import set_trace
  pyqtRemoveInputHook()
  set_trace()


class StartWindow(QMainWindow):
    def __init__(self, camera=None):
        super().__init__()

        ## organization
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)
        self.setGeometry(100, 100, 800, 800)


        self.stream_button = QPushButton('Stream', self.central_widget)
        self.layout.addWidget(self.stream_button)
        self.stream_button.clicked.connect(self.stream)

        self.replay_button = QPushButton('Replay', self.central_widget)
        self.layout.addWidget(self.replay_button)
        self.replay_button.clicked.connect(self.replay)

        # self.progress = QProgressBar(self)
        # self.replay_button.clicked.connect(self.progress)

        self.display_image_widget = pg.ImageView()
        self.layout.addWidget(self.display_image_widget)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0,100)
        self.layout.addWidget(self.slider)
        self.slider.valueChanged.connect(self.exposure_time)

        self.camera = MainCamera()

    def save(self, images, i, path): ### npy format
        for y in range(len(images)):
            image = images[y]
            np.save(file = str(path) + '/image{}.npy'.format(str(i)), arr=image)
            print("saved file")

    def stream(self, simulated = False):
        simulated = False
        save = False
        if simulated:
            for i in range(100):
                self.image = np.random.rand(256, 256)
                self.display_image_widget.setImage(self.image.T)
                pg.QtGui.QApplication.processEvents()
        else:
            self.camera.start_acquisition()
            if save:
                path = QFileDialog.getxistingDirectory(None, 'Select a folder for saving the files:', 'C:/Users/barral/Desktop/camera/data', QFileDialog.ShowDirsOnly)
            for i in range(100):
                self.images = self.camera.get_images() ## gettint the images, sometimes its one other can be more
                print(self.images)
                self.image = self.images[0]  ## keeping only the 1st for projetion
                self.image_reshaped = self.image.reshape(2048, 2048) ## needs reshaping
                self.display_image_widget.setImage(self.image_reshaped.T)
                if save:
                    print(self.images)
                    self.save(self.images, i, path)   ## we want to save all the images not only the first of each import batches
                pg.QtGui.QApplication.processEvents()

                axes = (0, 1)
                data, coords = self.display_image_widget.roi.getArrayRegion(self.image_reshaped.view(),
                                                                            self.display_image_widget.imageItem,
                                                                            axes, returnMappedCoords=True)
                debug_trace()
#                roi = pg.ROI([0,0],[1,1],pen=pg.mkPen('r',width=2))
#                self.display_image_widget.addItem(roi)
#                def getcoordinates(roi):
#                    data2,xdata = roi.getArrayRegion(self.image_reshaped,self.display_image_widget.imageItem,returnMappedCoords=True)
#                    print(xdata)
#                roi.sigRegionChanged.connect(getcoordinates)

            self.camera.end_acquisition()

    def replay(self):
        path = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:/', QFileDialog.ShowDirsOnly)
        if path == None:
            pass
        else:
            images_nb = len(os.listdir(path))
            images = []
            for i in range(images_nb):
                image = np.load(str(path) + '/image{}.npy'.format(str(i)))
                image_reshaped = image.reshape(2048, 2048)
                images.append(image_reshaped)
            for img in images:
                print(img)
                self.display_image_widget.setImage(img.T)
                pg.QtGui.QApplication.processEvents()

    def exposure_time(self, value):
        value /= 10
        self.camera.write_exposure(value)
        print(self.camera.read_exposure())

    def bye(self):
        self.camera.shutdown()
        # to finish

if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('Fusion')
    win = StartWindow()
    win.show()
    app.exit(app.exec_())
