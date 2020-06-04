## PyQT5
from PyQt5 import uic
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, pyqtSignal, QThreadPool, QObject, QTimer, QEventLoop
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSlider, QFileDialog, \
                            QMessageBox, QProgressBar, QGraphicsScene, QInputDialog, QDialog
from PyQt5.QtGui import QImage, QPixmap, QPen, QPainter
from PyQt5.QtTest import QTest
import pyqtgraph as pg
import sys



class ElectrophysiologyGui(QWidget):
    def __init__(self):
        super(ElectrophysiologyGui, self).__init__()
        uic.loadUi('OPTIMAQS/view/electrophysiology/electrophysiology.ui', self)
        self.show()
        self.import_electrophysiology_model()
        self.initialize_electrophysiology_parameters()
        self.actions()


        self.ephy_data = []
        self.end_expe = False
        self.channel_number = [2,6,10,14,16,18,20,22]
        self.sampling_rate = 1000

    def import_electrophysiology_model(self):
        """
        import laser model-type script
        """
        import PyDAQmx
        from model.electrophysiology.electrophysiology import StimVoltage, ReadingVoltage

    def initialize_electrophysiology_parameters(self):
        """
        Initialize all the laser variables
            """
        ## custom signals
        self.ephy_signal = Signals()
        self.ephy_signal.start.connect(self.start_recording)
        self.ephy_signal.finished.connect(self.stop_recording)

        self.recording = False
        self.ephy_graph = False


    def actions(self):
        """
        Define actions for buttons and items.
        """
        self.record_trace_button.clicked.connect(self.init_voltage)
        self.display_trace_button.clicked.connect(self.graph_voltage)
        self.stimulation_button.clicked.connect(self.ephy_stim)
        self.close_graph_button.clicked.connect(self.close_graph_windows)



    def init_voltage(self):
        ## reading voltage
        self.analog_input = PyDAQmx.Task()
        self.read = PyDAQmx.int32()
        self.data_ephy = np.zeros((len(self.channel_number), self.sampling_rate), dtype=np.float64)
        for channel in self.channel_number:
            self.analog_input.CreateAIVoltageChan(f'Dev1/ai{channel}',
                                                        "",
                                                        PyDAQmx.DAQmx_Val_Cfg_Default,
                                                        -10.0,
                                                        10.0,
                                                        PyDAQmx.DAQmx_Val_Volts,
                                                        None)
        self.analog_input.CfgSampClkTiming("",
                            self.sampling_rate,  ## sampling rate
                            PyDAQmx.DAQmx_Val_Rising,  ## active edge
                            PyDAQmx.DAQmx_Val_FiniteSamps, ## sample mode
                            1000) ## nb of sample to acquire
        self.analog_input.StartTask()

        ## stimulating
        self.analog_output = PyDAQmx.Task()
        self.analog_output.CreateAOVoltageChan("Dev1/ao0",
                                "",
                                -10.0,
                                10.0,
                                PyDAQmx.DAQmx_Val_Volts,
                                None)
        self.analog_output.CfgSampClkTiming("",
                    self.sampling_rate,  ## sampling rate
                    PyDAQmx.DAQmx_Val_Rising,  ## active edge
                    PyDAQmx.DAQmx_Val_ContSamps, ## sample mode
                    1000) ## nb of sample to acquire
#        self.analog_output.StartTask()

#        self.pulse = np.zeros(1, dtype=np.uint8)
#        self.write_digital_lines = PyDAQmx.Task()
#        self.write_digital_lines.CreateDOChan("/Dev1/port0/line3","",PyDAQmx.DAQmx_Val_ChanForAllLines)
#        self.write_digital_lines.StartTask()

    def start_recording(self):
        self.analog_input.ReadAnalogF64(self.sampling_rate,   ## number of sample per channel
                                    10.0,  ## timeout in s
                                    PyDAQmx.DAQmx_Val_GroupByChannel,  ## fillMode (interleave data acqcuisition or not?)
                                    self.data_ephy,   #The array to store read data into
                                    self.data_ephy.shape[0]*self.data_ephy.shape[1],  ## length of the data array
                                    PyDAQmx.byref(self.read),None) ## total number of data points read per channel
        print(f"Acquired {self.read.value} points")
        self.analog_input.StopTask()
        print(self.data_ephy.shape)

        self.timings_logfile_dict['ephy']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)
        return self.data_ephy

    def graph_voltage(self):
        self.x = range(self.sampling_rate)
        self.start_recording()
#        colors = ['g', 'r', 'c', 'm', 'y', 'k', 'w']
#        self.voltage_plot = pg.plot(self.x, self.data_ephy[0], pen='b')
#        if self.data_ephy.shape[0] > 1:
#            for channel, color in zip(range(self.data_ephy.shape[0]-1), colors):
#                    self.voltage_plot.plot(self.x, self.data_ephy[channel]+1, pen = color)
        self.plot = pg.GraphicsWindow(title="Electrophysiology")
        self.voltage_plot = self.plot.addPlot(title='Voltage')

        self.curve0 = self.voltage_plot.plot(self.x, self.data_ephy[0], pen='b')
#        self.curve1 = self.voltage_plot.plot(self.x, self.data_ephy[1], pen='g')
#        self.curve2 = self.voltage_plot.plot(self.x, self.data_ephy[2], pen='r')
#        self.curve3 = self.voltage_plot.plot(self.x, self.data_ephy[3], pen='c')
#
#        self.curve4 = self.voltage_plot.plot(self.x, self.data_ephy[4], pen='m')
#        self.curve5 = self.voltage_plot.plot(self.x, self.data_ephy[5], pen='y')
#        self.curve6 = self.voltage_plot.plot(self.x, self.data_ephy[6], pen='k')
#        self.curve7 = self.voltage_plot.plot(self.x, self.data_ephy[7], pen='w')

        self.voltage_plot.addLegend()
        self.voltage_plot.showGrid(x=True, y=True)
        self.plot.setBackground('w')
        pg.setConfigOptions(antialias=True)
        self.ephy_graph = True

        self.timer_ephy = QTimer()
        self.timer_ephy.timeout.connect(self.update_plot_ephy)
        self.timer_ephy.start(1000)

    def update_plot_ephy(self):
        if self.ephy_graph==False:
            self.timer_ephy.stop()

        self.start_recording()
#        self.voltage_plot.enableAutoRange('xy', False)
#        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
#        debug_trace()
#        for channel, color in zip(range(self.data_ephy.shape[0]), colors):
#        for channel in range(self.data_ephy.shape[0]):
#            self.voltage_plot.setData(1000, self.data_ephy[channel])
#            self.voltage_plot.plot(self.x, self.data_ephy[channel], clear=True, pen=color)
        self.curve0.setData(self.x, self.data_ephy[0])
#        self.curve1.setData(self.x, self.data_ephy[1])
#        self.curve2.setData(self.x, self.data_ephy[2])
#        self.curve3.setData(self.x, self.data_ephy[3])
#
#        self.curve4.setData(self.x, self.data_ephy[4])
#        self.curve5.setData(self.x, self.data_ephy[5])
#        self.curve6.setData(self.x, self.data_ephy[6])
#        self.curve7.setData(self.x, self.data_ephy[7])


    def close_graph_windows(self):
        print('closing ephy plot and stopping recording')
        self.ephy_graph = False
        self.timer_ephy.stop()
        self.stop_recording()
        self.plot.close()

    def stop_recording(self):
        print('ephy end signal received')
        self.recording = False
        self.analog_input.StopTask()
        self.timings_logfile_dict['ephy']['off'].append((time.perf_counter() - self.perf_counter_init)*1000)

    def save_ephy_data(self, data):
#        np.save(file = f"{self.path}/voltage.npy", arr = data)
        np.savetxt(f"{self.path}/voltage.txt", self.data_ephy)

    def ephy_recording_thread(self):
        if self.record_electrophysiological_trace_radioButton.isChecked():
            while self.recording:
                data = self.start_recording()
                self.graph_voltage()
                self.ephy_data.append(data)
            self.save_ephy_data(self.ephy_data)

    def start_stimulation(self):
        print('stimulation start')
#        set_voltage_value = 5.
        self.stim_data = np.array([5]*1000)
        self.stim_data[1:100] = 0
        self.stim_data[900:1000] = 0
#        self.stim_data = np.array([5])
        n=1000
        sampsPerChanWritten=PyDAQmx.int32()

#        self.analog_output.WriteAnalogScalarF64(1, 10.0, set_voltage_value, None)
#        self.analog_output.WriteAnalogF64(1000, 0, 10.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.stim_data, PyDAQmx.byref(sampsPerChanWritten), None)
        self.analog_output.WriteAnalogF64(n, 0, 10.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.stim_data, PyDAQmx.byref(sampsPerChanWritten), None)
        self.analog_output.StartTask()

        self.timings_logfile_dict['ephy_stim']['on'].append((time.perf_counter() - self.perf_counter_init)*1000)


#        self.pulse[0]=1
#        self.write_digital_lines.WriteDigitalLines(1, 1, 5.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse, None, None)

    def end_stimulation(self):
        self.analog_output.StopTask()
        self.timings_logfile_dict['ephy_stim']['off'].append((time.perf_counter() - self.perf_counter_init)*1000)
        print('stimulation end')

#        self.pulse[0]=0
#        self.write_digital_lines.WriteDigitalLines(1, 1, 5.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse , None, None)

    def ephy_stim(self):
        self.start_stimulation()
        custom_sleep_function(2500)
        self.end_stimulation()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ElectrophysiologyGui()
    win.showMaximized()
    app.exit(app.exec_())
