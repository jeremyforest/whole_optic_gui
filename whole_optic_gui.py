# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'whole_optic_gui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1621, 922)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.camera = QtWidgets.QFrame(self.centralwidget)
        self.camera.setGeometry(QtCore.QRect(10, 80, 1091, 781))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.camera.setFont(font)
        self.camera.setFrameShape(QtWidgets.QFrame.Box)
        self.camera.setObjectName("camera")
        self.graphicsView = Custom_pyqtgraph_widget(self.camera)
        self.graphicsView.setGeometry(QtCore.QRect(20, 40, 1041, 651))
        self.graphicsView.setObjectName("graphicsView")
        self.replay_button = QtWidgets.QPushButton(self.camera)
        self.replay_button.setGeometry(QtCore.QRect(140, 10, 80, 21))
        self.replay_button.setObjectName("replay_button")
        self.stream_button = QtWidgets.QPushButton(self.camera)
        self.stream_button.setGeometry(QtCore.QRect(270, 10, 80, 21))
        self.stream_button.setObjectName("stream_button")
        self.exposure_time_label = QtWidgets.QLabel(self.camera)
        self.exposure_time_label.setGeometry(QtCore.QRect(50, 710, 81, 16))
        self.exposure_time_label.setObjectName("exposure_time_label")
        self.main_xamera_label = QtWidgets.QLabel(self.camera)
        self.main_xamera_label.setGeometry(QtCore.QRect(10, 10, 81, 16))
        self.main_xamera_label.setObjectName("main_xamera_label")
        self.exposure_time_bar = QtWidgets.QScrollBar(self.camera)
        self.exposure_time_bar.setGeometry(QtCore.QRect(220, 710, 261, 20))
        self.exposure_time_bar.setAutoFillBackground(False)
        self.exposure_time_bar.setMaximum(100)
        self.exposure_time_bar.setProperty("value", 0)
        self.exposure_time_bar.setTracking(True)
        self.exposure_time_bar.setOrientation(QtCore.Qt.Horizontal)
        self.exposure_time_bar.setInvertedAppearance(False)
        self.exposure_time_bar.setObjectName("exposure_time_bar")
        self.saving_check = QtWidgets.QCheckBox(self.camera)
        self.saving_check.setGeometry(QtCore.QRect(360, 10, 77, 20))
        self.saving_check.setChecked(False)
        self.saving_check.setTristate(False)
        self.saving_check.setObjectName("saving_check")
        self.progress_bar = QtWidgets.QProgressBar(self.camera)
        self.progress_bar.setGeometry(QtCore.QRect(730, 740, 291, 16))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progress_bar.sizePolicy().hasHeightForWidth())
        self.progress_bar.setSizePolicy(sizePolicy)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setObjectName("progress_bar")
        self.loading_saving_label = QtWidgets.QLabel(self.camera)
        self.loading_saving_label.setGeometry(QtCore.QRect(590, 740, 131, 20))
        self.loading_saving_label.setObjectName("loading_saving_label")
        self.exposure_time_value = QtWidgets.QLCDNumber(self.camera)
        self.exposure_time_value.setGeometry(QtCore.QRect(150, 710, 64, 23))
        self.exposure_time_value.setFrameShadow(QtWidgets.QFrame.Plain)
        self.exposure_time_value.setSmallDecimalPoint(True)
        self.exposure_time_value.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.exposure_time_value.setObjectName("exposure_time_value")
        self.binning_combo_box = QtWidgets.QComboBox(self.camera)
        self.binning_combo_box.setGeometry(QtCore.QRect(140, 750, 77, 22))
        self.binning_combo_box.setEditable(False)
        self.binning_combo_box.setCurrentText("")
        self.binning_combo_box.setFrame(True)
        self.binning_combo_box.setObjectName("binning_combo_box")
        self.binning_label = QtWidgets.QLabel(self.camera)
        self.binning_label.setGeometry(QtCore.QRect(70, 760, 52, 14))
        self.binning_label.setObjectName("binning_label")
        self.radioButton = QtWidgets.QRadioButton(self.camera)
        self.radioButton.setGeometry(QtCore.QRect(630, 760, 121, 20))
        self.radioButton.setObjectName("radioButton")
        self.subarray_label = QtWidgets.QLabel(self.camera)
        self.subarray_label.setGeometry(QtCore.QRect(750, 760, 291, 16))
        self.subarray_label.setObjectName("subarray_label")
        self.current_binning_size_label = QtWidgets.QLabel(self.camera)
        self.current_binning_size_label.setGeometry(QtCore.QRect(230, 750, 121, 16))
        self.current_binning_size_label.setObjectName("current_binning_size_label")
        self.current_binning_size_label_2 = QtWidgets.QLabel(self.camera)
        self.current_binning_size_label_2.setGeometry(QtCore.QRect(340, 750, 121, 16))
        self.current_binning_size_label_2.setObjectName("current_binning_size_label_2")
        self.controls = QtWidgets.QFrame(self.centralwidget)
        self.controls.setGeometry(QtCore.QRect(1240, 10, 311, 411))
        self.controls.setFrameShape(QtWidgets.QFrame.Box)
        self.controls.setObjectName("controls")
        self.gridLayoutWidget = QtWidgets.QWidget(self.controls)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 150, 191, 241))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.y_axis_backward_button = QtWidgets.QPushButton(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.y_axis_backward_button.sizePolicy().hasHeightForWidth())
        self.y_axis_backward_button.setSizePolicy(sizePolicy)
        self.y_axis_backward_button.setMinimumSize(QtCore.QSize(0, 21))
        self.y_axis_backward_button.setCheckable(False)
        self.y_axis_backward_button.setObjectName("y_axis_backward_button")
        self.gridLayout.addWidget(self.y_axis_backward_button, 2, 0, 1, 2)
        self.y_axis_forward_button = QtWidgets.QPushButton(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.y_axis_forward_button.sizePolicy().hasHeightForWidth())
        self.y_axis_forward_button.setSizePolicy(sizePolicy)
        self.y_axis_forward_button.setObjectName("y_axis_forward_button")
        self.gridLayout.addWidget(self.y_axis_forward_button, 0, 0, 1, 2)
        self.x_axis_right_button = QtWidgets.QPushButton(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.x_axis_right_button.sizePolicy().hasHeightForWidth())
        self.x_axis_right_button.setSizePolicy(sizePolicy)
        self.x_axis_right_button.setObjectName("x_axis_right_button")
        self.gridLayout.addWidget(self.x_axis_right_button, 1, 1, 1, 1)
        self.x_axisleft_button = QtWidgets.QPushButton(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.x_axisleft_button.sizePolicy().hasHeightForWidth())
        self.x_axisleft_button.setSizePolicy(sizePolicy)
        self.x_axisleft_button.setObjectName("x_axisleft_button")
        self.gridLayout.addWidget(self.x_axisleft_button, 1, 0, 1, 1)
        self.microscope_control_label = QtWidgets.QLabel(self.controls)
        self.microscope_control_label.setGeometry(QtCore.QRect(10, 10, 111, 16))
        self.microscope_control_label.setObjectName("microscope_control_label")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.controls)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(211, 150, 91, 241))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.z_axis_up = QtWidgets.QPushButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.z_axis_up.sizePolicy().hasHeightForWidth())
        self.z_axis_up.setSizePolicy(sizePolicy)
        self.z_axis_up.setObjectName("z_axis_up")
        self.verticalLayout.addWidget(self.z_axis_up)
        self.z_axis_down = QtWidgets.QPushButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.z_axis_down.sizePolicy().hasHeightForWidth())
        self.z_axis_down.setSizePolicy(sizePolicy)
        self.z_axis_down.setObjectName("z_axis_down")
        self.verticalLayout.addWidget(self.z_axis_down)
        self.stop_mouvment_button = QtWidgets.QPushButton(self.controls)
        self.stop_mouvment_button.setGeometry(QtCore.QRect(180, 30, 80, 21))
        self.stop_mouvment_button.setObjectName("stop_mouvment_button")
        self.laser = QtWidgets.QFrame(self.centralwidget)
        self.laser.setGeometry(QtCore.QRect(1310, 430, 231, 141))
        self.laser.setFrameShape(QtWidgets.QFrame.Box)
        self.laser.setObjectName("laser")
        self.laser_label = QtWidgets.QLabel(self.laser)
        self.laser_label.setGeometry(QtCore.QRect(10, 10, 81, 16))
        self.laser_label.setObjectName("laser_label")
        self.laser_on_button = QtWidgets.QPushButton(self.laser)
        self.laser_on_button.setGeometry(QtCore.QRect(60, 50, 80, 21))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(73, 239, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(162, 255, 141))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(117, 247, 88))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(36, 119, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(48, 159, 23))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(73, 239, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(164, 247, 145))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(73, 239, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(162, 255, 141))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(117, 247, 88))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(36, 119, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(48, 159, 23))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(73, 239, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(164, 247, 145))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(36, 119, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(73, 239, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(162, 255, 141))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(117, 247, 88))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(36, 119, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(48, 159, 23))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(36, 119, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(36, 119, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(73, 239, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(73, 239, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(73, 239, 35))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        self.laser_on_button.setPalette(palette)
        self.laser_on_button.setCheckable(True)
        self.laser_on_button.setChecked(False)
        self.laser_on_button.setFlat(False)
        self.laser_on_button.setObjectName("laser_on_button")
        self.dlp = QtWidgets.QFrame(self.centralwidget)
        self.dlp.setGeometry(QtCore.QRect(1110, 620, 471, 141))
        self.dlp.setFrameShape(QtWidgets.QFrame.Box)
        self.dlp.setObjectName("dlp")
        self.dlp_label = QtWidgets.QLabel(self.dlp)
        self.dlp_label.setGeometry(QtCore.QRect(10, 10, 31, 16))
        self.dlp_label.setObjectName("dlp_label")
        self.save_ROI_button = QtWidgets.QPushButton(self.dlp)
        self.save_ROI_button.setGeometry(QtCore.QRect(190, 60, 80, 21))
        self.save_ROI_button.setObjectName("save_ROI_button")
        self.saved_ROI_image = QtWidgets.QGraphicsView(self.dlp)
        self.saved_ROI_image.setGeometry(QtCore.QRect(280, 20, 171, 111))
        self.saved_ROI_image.setObjectName("saved_ROI_image")
        self.display_internal_pattern_combobox = QtWidgets.QComboBox(self.dlp)
        self.display_internal_pattern_combobox.setGeometry(QtCore.QRect(20, 60, 77, 22))
        self.display_internal_pattern_combobox.setObjectName("display_internal_pattern_combobox")
        self.internal_patterns_label = QtWidgets.QLabel(self.dlp)
        self.internal_patterns_label.setGeometry(QtCore.QRect(10, 40, 101, 16))
        self.internal_patterns_label.setObjectName("internal_patterns_label")
        self.folder = QtWidgets.QFrame(self.centralwidget)
        self.folder.setGeometry(QtCore.QRect(10, 20, 771, 41))
        self.folder.setFrameShape(QtWidgets.QFrame.Box)
        self.folder.setObjectName("folder")
        self.change_folder_button = QtWidgets.QPushButton(self.folder)
        self.change_folder_button.setGeometry(QtCore.QRect(190, 10, 101, 21))
        self.change_folder_button.setObjectName("change_folder_button")
        self.initialize_experiment_button = QtWidgets.QPushButton(self.folder)
        self.initialize_experiment_button.setGeometry(QtCore.QRect(30, 10, 131, 21))
        self.initialize_experiment_button.setObjectName("initialize_experiment_button")
        self.current_folder_label = QtWidgets.QLabel(self.folder)
        self.current_folder_label.setGeometry(QtCore.QRect(360, 10, 91, 16))
        self.current_folder_label.setObjectName("current_folder_label")
        self.current_folder_label_2 = QtWidgets.QLabel(self.folder)
        self.current_folder_label_2.setGeometry(QtCore.QRect(460, 5, 301, 31))
        self.current_folder_label_2.setScaledContents(True)
        self.current_folder_label_2.setObjectName("current_folder_label_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1621, 19))
        self.menubar.setObjectName("menubar")
        self.menuMenu = QtWidgets.QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.menuMenu.addAction(self.actionQuit)
        self.menubar.addAction(self.menuMenu.menuAction())

        self.retranslateUi(MainWindow)
        self.binning_combo_box.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.replay_button.setText(_translate("MainWindow", "Replay"))
        self.stream_button.setText(_translate("MainWindow", "Stream"))
        self.exposure_time_label.setText(_translate("MainWindow", "Exposure time"))
        self.main_xamera_label.setText(_translate("MainWindow", "Main Camera"))
        self.saving_check.setText(_translate("MainWindow", "Saving ?"))
        self.loading_saving_label.setText(_translate("MainWindow", "Loading / Saving video"))
        self.binning_label.setText(_translate("MainWindow", "Binning"))
        self.radioButton.setText(_translate("MainWindow", "SubArray mode ?"))
        self.subarray_label.setText(_translate("MainWindow", "subarray size and origin"))
        self.current_binning_size_label.setText(_translate("MainWindow", "Current binning size"))
        self.current_binning_size_label_2.setText(_translate("MainWindow", "None"))
        self.y_axis_backward_button.setText(_translate("MainWindow", "Y Axis BACKWARD"))
        self.y_axis_forward_button.setText(_translate("MainWindow", "Y axis FORWARD"))
        self.x_axis_right_button.setText(_translate("MainWindow", "X axis RIGHT"))
        self.x_axisleft_button.setText(_translate("MainWindow", "X axis LEFT"))
        self.microscope_control_label.setText(_translate("MainWindow", "Microscope control"))
        self.z_axis_up.setText(_translate("MainWindow", "Z axis UP"))
        self.z_axis_down.setText(_translate("MainWindow", "Z axis DOWN"))
        self.stop_mouvment_button.setText(_translate("MainWindow", "STOP"))
        self.laser_label.setText(_translate("MainWindow", "Laser"))
        self.laser_on_button.setText(_translate("MainWindow", "Laser"))
        self.dlp_label.setText(_translate("MainWindow", "DLP"))
        self.save_ROI_button.setText(_translate("MainWindow", "Save ROI"))
        self.internal_patterns_label.setText(_translate("MainWindow", "Internal patterns"))
        self.change_folder_button.setText(_translate("MainWindow", "Change Folder"))
        self.initialize_experiment_button.setText(_translate("MainWindow", "Initialize Experiment"))
        self.current_folder_label.setText(_translate("MainWindow", "Current Folder:"))
        self.current_folder_label_2.setText(_translate("MainWindow", "None"))
        self.menuMenu.setTitle(_translate("MainWindow", "Menu"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))

from custom_pyqtgraph_widget import Custom_pyqtgraph_widget
