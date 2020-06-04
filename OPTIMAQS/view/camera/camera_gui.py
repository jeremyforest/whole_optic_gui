## PyQT5
from PyQt5 import uic
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, pyqtSignal, QThreadPool, QObject, QTimer, QEventLoop
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, \
                            QMessageBox, QProgressBar, QGraphicsScene, QInputDialog, QDialog
from PyQt5.QtGui import QImage, QPixmap, QPen, QPainter
from PyQt5.QtTest import QTest
import pyqtgraph as pg
import sys


## Custom imports
from OPTIMAQS.utils.signals import Signals

# import sys
# sys.path.append('../../')

class CameraGui(QWidget):
    """
    GUI for the camera
    """
    def __init__(self):
        """
        Initialize the ui and load the camera functions
        """
        super(CameraGui, self).__init__()
        uic.loadUi('OPTIMAQS/view/camera/camera.ui', self)
        self.show()
        self.import_camera_model()
        self.actions()

        self.save_images = False
        self.simulated = False
        self.images = []
        self.image_list = []
        self.image_reshaped = []
        self.roi_list = []




    def import_camera_model(self):
        """
        import camera model-type script
        """
        from model.camera.camera_model import MainCamera
        self.cam = MainCamera()

    def initialize_camera_parameters(self):
        """
        Initialize all the camera variables
        """
        ## initialize camera parameters
        ## fov
        self.x_dim = self.cam.get_subarray_size()[1]
        self.x_init = self.cam.get_subarray_size()[0]
        self.y_dim = self.cam.get_subarray_size()[3]
        self.y_init = self.cam.get_subarray_size()[2]
        self.subarray_label.setText(str(self.cam.get_subarray_size()))
        ## binning
        self.bin_size = self.cam.read_binning()
        self.current_binning_size_label_2.setText(str(self.cam.read_binning()))
        ## counters initialization (exposure time and fps)
        self.exposure_time_value.display(self.cam.read_exposure())
        self.internal_frame_rate = self.cam.get_internal_frame_rate()
        self.internal_frame_rate_label.setText(str(self.internal_frame_rate))
        ## set property as wanted
        self.cam.hcam.setPropertyValue('defect_correct_mode', 1)  ## necessary ?
        print(self.cam.hcam.getPropertyValue('defect_correct_mode'))
        self.cam.hcam.setPropertyValue('hot_pixel_correct_level', 2)   ## necessary ?
        print(self.cam.hcam.getPropertyValue('hot_pixel_correct_level'))
        ## custom signals
        self.camera_signal = Signals()
        self.camera_signal.start.connect(self.stream)
        self.camera_signal.finished.connect(self.stop_stream)

    def actions(self):
        """
        Define actions for buttons and items.
        """
        self.snap_image_button.clicked.connect(self.snap_image)
        self.stream_button.clicked.connect(self.stream)
        self.replay_button.clicked.connect(self.replay)
        self.exposure_time_bar.valueChanged.connect(self.exposure_time)
        self.binning_combo_box.activated.connect(self.binning)
        self.subArray_mode_radioButton.toggled.connect(self.subarray)
        self.update_internal_frame_rate_button.clicked.connect(self.update_internal_frame_rate)
        self.stop_stream_button.clicked.connect(self.stop_stream)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)

    def save_as_png(self, array, image_name):
        plt.imsave('{}{}.png'.format(self.path, image_name), array, cmap='gray')

    def snap_image(self): ## only takes an image and saves it
        self.cam.start_acquisition()
        for i in range(1):
            self.images, self.times = self.cam.get_images()
            while self.images == []:
                self.images, self.times = self.cam.get_images() ## break the function if no image (due to the lauching time of the camera)
            self.cam.end_acquisition()
            self.image = self.images[0]
            self.image_reshaped = self.image.reshape(int(self.y_dim/self.bin_size),
                                                    int(self.x_dim/self.bin_size))
            self.graphicsView.setImage(self.image_reshaped)
            image_name = QInputDialog.getText(self, 'Input Dialog', 'File name:')
            self.save_as_png(self.image_reshaped, image_name)

    def stream(self):
         self.timings_logfile_dict['camera'] = []
         self.timings_logfile_dict['camera_bis'] = []
         image_processing_worker = Worker(self.processing_images)
         image_processing_worker.signals.result.connect(self.print_output)
         image_processing_worker.signals.finished.connect(self.thread_complete)
         self.threadpool.start(image_processing_worker)
         self.timer.start(10)

    def stop_stream(self):
        print('camera end signal received')
        self.acquire_images = False

    def processing_images(self):
        self.acquire_images = True
        self.cam.start_acquisition()
        image_acquired = 0
        self.timings_logfile_dict['camera_bis'].append(datetime.now().timestamp())
        self.timings_logfile_dict['camera_bis'].append((time.perf_counter() - self.perf_counter_init)*1000)
#        self.timings_logfile_dict['camera_bis'].append(self.times_bis)
        while self.acquire_images:
            if self.acquire_images == False:
                break
            # if image_acquired == 800:
            #     break
            else:
                self.images, self.times = self.cam.get_images()  ## getting the images, getting 0, 1 or >1 images
                while self.images == []:
                    self.images, self.times = self.cam.get_images() ## break the function if no image (due to the lauching time of the camera)
                self.image = self.images[0]  ## keeping only the 1st image for GUI display
                self.image_reshaped = self.image.reshape(int((self.y_dim/self.bin_size)),
                                                        int(self.x_dim/self.bin_size))  ## image needs reshaping for show
                print(f"Acquired {image_acquired} images")
                image_acquired += 1
                if self.saving_check.isChecked(): ## for saving data after end of acquisition, uses less memory if no saving
                    for j in range(len(self.images)):
                        self.image_list.append(self.images[j])
                    self.timings_logfile_dict['camera'].append(self.times)
#        self.timings_logfile_dict['camera_bis'].append(self.times_bis)
        self.cam.end_acquisition()
        self.saving_images(self.images, self.times)
#        self.camera_signal.finished.emit()  ## not sure this is needed

    def update_plot(self):
        if self.image_reshaped == []:
            pass
        else:
            self.graphicsView.setImage(self.image_reshaped)

    def saving_images(self, images, times):
        if self.saving_check.isChecked():
            ## saving images
            save_images_worker = Worker(self.save, self.image_list, self.path_raw_data)
            save_images_worker.signals.result.connect(self.print_output)
            save_images_worker.signals.finished.connect(self.thread_complete)
            #save_images_worker.signals.progress.connect(self.progress_fn)
            self.threadpool.start(save_images_worker)
            ## saving images times
            with open(self.timings_logfile_path, "w") as file:
                file.write(json.dumps(self.timings_logfile_dict, default=lambda x:list(x), indent=4, sort_keys=True))
            ## saving experiment info
            self.info_logfile_dict['roi'].append(self.roi_list)
            self.info_logfile_dict['exposure time'].append(self.exposure_time_value.value())
            self.info_logfile_dict['binning'].append(self.bin_size)
            self.info_logfile_dict['fps'].append(self.internal_frame_rate)
            self.info_logfile_dict['fov'].append((self.x_init, self.x_dim, self.y_init, self.y_dim))
            with open(self.info_logfile_path, "w") as file:
                file.write(json.dumps(self.info_logfile_dict, default=lambda x:list(x), indent=4, sort_keys=True))

    def roi(self):
        axes = (0, 1)
        self.saved_ROI_image.setImage(self.image_reshaped) ## get the image into the ROI graphic interface
        # data, coords = self.graphicsView.roi.getArrayRegion(self.image_reshaped.view(), self.graphicsView.imageItem, axes, returnMappedCoords=True) ## get the roi data and coords
        # self.roi_list.append(coords)
        roi_state = self.graphicsView.roi.getState()
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
            file.write(json.dumps(self.info_logfile_dict, default=lambda x:list(x), indent=4, sort_keys=True))

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
        self.bin_size = self.cam.read_binning()

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



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CameraGui()
    win.showMaximized()
    app.exit(app.exec_())
