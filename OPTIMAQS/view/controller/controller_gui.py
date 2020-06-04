## PyQT5
from PyQt5 import uic
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, pyqtSignal, QThreadPool, QObject, QTimer, QEventLoop
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, \
                            QMessageBox, QProgressBar, QGraphicsScene, QInputDialog, QDialog
from PyQt5.QtGui import QImage, QPixmap, QPen, QPainter
from PyQt5.QtTest import QTest
import pyqtgraph as pg
import sys



class ControllerGui(QWidget):
    def __init__(self):
        super(ControllerGui, self).__init__()
        uic.loadUi('OPTIMAQS/view/controller/controller.ui', self)
        self.show()
        self.import_controller_model()
        self.initialize_controller_parameters()
        self.ations()


    def import_controller_model(self):
        """
        import controller model-type script
        """
        from model.controller.manipulator_command import Controller
        self.controler = Controler()


    def initialize_controller_parameters(self):
        """
        Initialize all the controller variables
        """
        pass


    def actions(self):
        """
        Define actions for buttons and items.
        """
        self.x_axis_left_button.clicked.connect(self.left)
        self.x_axis_right_button.clicked.connect(self.right)
        self.y_axis_backward_button.clicked.connect(self.backward)
        self.y_axis_forward_button.clicked.connect(self.forward)
        self.z_axis_up.clicked.connect(self.up)
        self.z_axis_down.clicked.connect(self.down)
        self.stop_mouvment_button.clicked.connect(self.stop_mouvment)

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




if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ControllerGui()
    win.showMaximized()
    app.exit(app.exec_())
