
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage
import pyqtgraph as pg
from threading import Thread
import numpy as np
import matplotlib.pyplot as plt
import os
import time

from camera.camera_control import MainCamera


def debug_trace():
  '''Set a tracepoint in the Python debugger that works with Qt'''
  from PyQt5.QtCore import pyqtRemoveInputHook

  # Or for Qt5
  #from PyQt5.QtCore import pyqtRemoveInputHook

  from pdb import set_trace
  pyqtRemoveInputHook()
  set_trace()


class StartWindow(QMainWindow):
    def __init__(self, camera=None):
        super().__init__()
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self.stream_button = QPushButton('Stream', self.central_widget)
        self.layout.addWidget(self.stream_button)
        self.stream_button.clicked.connect(self.stream)

        self.replay_button = QPushButton('Replay', self.central_widget)
        self.layout.addWidget(self.replay_button)
        self.replay_button.clicked.connect(self.replay)

        # self.display_image_widget = pg.ImageView()
        # self.layout.addWidget(self.display_image_widget)

        self.canvas = pg.GraphicsLayoutWidget()
        self.central_widget.layout().addWidget(self.canvas)
        self.view = self.canvas.addViewBox()
        self.img = pg.ImageItem(border='w')
        self.view.addItem(self.img)



    def stream(self):
        # self.camera = MainCamera()
        # self.camera.start_acquisition()
#        image = np.random.normal(size=(15, 600, 600), loc=1024, scale=64).astype(np.uint16)
#        start_time = time.time()
        for _ in range(100):
            self.image = np.random.rand(256, 256)
            print(self.image)
#            image = self.camera.stream_images()
            self.img.setImage(self.image)
            # self.img.setImage(self.image)
            pg.QtGui.QApplication.processEvents()

        #     plt.imshow(image, interpolation=None, cmap='gray')
        #     plt.draw()
        #     plt.pause(0.0001)
        #     plt.clf()
        # plt.close()

#            self.display_image_widget.imageItem(image)
#            pg.ImageView.setImage(self, img = image.T)
#            self.display_image_widget.getView()
#            pg.ImageItem(self.camera.stream_images().T)
        # self.camera.end_acquisition()

    def open_saved(self, path):
        path_files = path
        images_nb = len(os.listdir(path))
        images = []
        for i in range(images_nb):
            image = np.load(str(path_files) + 'image{}.npy'.format(str(i)))
#            Thread(target=self.stream_images(image))
            image_reshaped = image.reshape(2048, 2048)
            images.append(image_reshaped)
#        plt.close()
        return images

    def replay(self):
        images = self.open_saved(path='/media/jeremy/Data/CloudStation/Postdoc/Project/Memory project/optopatch/equipment/camera/Images/')
        nb_frame = len(images)
        # images = self.camera.open_saved('C:\\Users\\barral\\Desktop\\camera\\data\\')
        start = time.time()
        for img in images:
            print(img)
            img = img.reshape(2048, 2048)
            self.display_image_widget.setImage(img.T)
        #     plt.imshow(img, interpolation=None, cmap='gray')
        #     plt.draw()
        #     plt.pause(0.0001)
        #     plt.clf()
        # plt.close()
        print (nb_frame/(time.time()-start))


if __name__ == '__main__':
#    app = pg.mkQApp()
    app = QApplication([])
    win = StartWindow()
    win.setGeometry(100, 100, 800, 800)
    win.show()
    app.exit(app.exec_())







#
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtCore, QtGui
#
# os.chdir(os.getcwd() + '/Images/')
# images_nb = len(os.listdir())
# for i in range(images_nb):
#     # i=i+1 i=1
#     image = np.load('image{}.npy'.format(str(i)))
#     pg.image(image.reshape(2048, 2048))
#
# image
# image.reshape(2048,2048).shape
# pg.image(image.reshape(2048,2048))
#
# pg.ImageView(image.reshape(2048, 2048))
#
#
#
# app = QtGui.QApplication([])
# win = QtGui.QMainWindow()
