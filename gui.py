
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

import open_saved


class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.central_widget = QWidget()
        self.stream_button = QPushButton('Stream', self.central_widget)
        self.replay_button = QPushButton('Replay', self.central_widget)

        self.stream_button.clicked.connect(self.stream)
        self.replay_button.clicked.connect(self.replay)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.stream_button)
        self.layout.addWidget(self.replay_button)
        self.setCentralWidget(self.central_widget)

    def stream(self):
        print('not implemented yet')

    def replay(self):
        return open_saved.run()



if __name__ == '__main__':
    app = QApplication([])
    window = StartWindow()
    window.show()
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
