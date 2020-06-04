# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 17:47:38 2019

@author: jeremy
"""
import PyDAQmx
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import time

class StimVoltage():
    def __init__(self):
        self.analog_output = PyDAQmx.Task()
        self.analog_output.CreateAOVoltageChan("Dev1/ao0",
                                "",
                                -10.0,
                                10.0,   
                                PyDAQmx.DAQmx_Val_Volts,
                                None)

    def start_stimulation(self, set_voltage_value):
        self.analog_output.StartTask()
        self.analog_output.WriteAnalogScalarF64(1,10.0,set_voltage_value,None)

    def end_stimulation(self):
        self.analog_output.StopTask()


class ReadingVoltage():
    def __init__(self):
        self.analog_input = PyDAQmx.Task()
        self.read = PyDAQmx.int32()
        self.data = np.zeros((2,1000), dtype=np.float64)
        self.analog_input.CreateAIVoltageChan("Dev1/ai16", ## voltage is ai16
                                            "",
                                            PyDAQmx.DAQmx_Val_Cfg_Default,
                                            -10.0,
                                            10.0,
                                            PyDAQmx.DAQmx_Val_Volts,
                                            None)
        # DAQmx Configure Code
        self.analog_input.CfgSampClkTiming("",
                                        1000.0,  ## sampling rate
                                        PyDAQmx.DAQmx_Val_Rising,  ## active edge
                                        PyDAQmx.DAQmx_Val_FiniteSamps, ## sample mode
                                        1000) ## nb of sample to acquire
        self.analog_input.StartTask()
        
        ## timer for plot update        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)

    def recording(self):
        self.analog_input.ReadAnalogF64(1000,   ## number of sample per channel
                                    10.0,  ## timeout in s
                                    PyDAQmx.DAQmx_Val_GroupByChannel,  # fillMode (interleave data acqcuisition or not?)
                                    self.data,   #The array to store read data into
                                    2000,  ## length of the data array
                                    PyDAQmx.byref(self.read),None) ## total number of data points read per channel
        print(f"Acquired {self.read.value} points")
        self.analog_input.StopTask()
        print(self.data.shape)
        return self.data
    
    def graph_voltage(self):
        self.x = range(1000)
        self.voltage_plot = win.addPlot(title='Voltage')
        self.recording()
        self.curve0 = self.voltage_plot.plot(self.x, self.data[0])
        self.curve1 = self.voltage_plot.plot(self.x, self.data[1])

    def update_plot(self):
        self.recording()
#        self.voltage_plot.enableAutoRange('xy', False)
        self.curve0.setData(self.x, self.data[0])
        self.curve1.setData(self.x, self.data[1])




if __name__ == "__main__":
    app = QtGui.QApplication([])
    win = pg.GraphicsWindow(title="Electrophysiology")
    pg.setConfigOptions(antialias=False)
    reading_voltage = ReadingVoltage()
    stimulating_voltage = StimVoltage()
    reading_voltage.graph_voltage()
    pg.QtGui.QApplication.instance().exec_()