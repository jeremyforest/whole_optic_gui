# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 17:47:38 2019

@author: jeremy
"""

from PyDAQmx import *
from PyDAQmx.DAQmxTypes import *
from PyDAQmx import Task
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')

class StimVoltage():
    def __init__(self):
        task = Task()
        task.CreateAOVoltageChan("Dev1/ao1",
                                "",
                                -10.0,
                                10.0,
                                DAQmx_Val_Volts,
                                None)

    def start_stimulation(self, value):
        task.StartTask()
        task.WriteAnalogScalarF64(1,10.0,value,None)

    def end_stimulation(self):
        task.StopTask()


class ReadingVoltage():
    def __init__(self):
        self.analog_input = Task()
        self.read = int32()
        self.data = numpy.zeros((1000,), dtype=numpy.float64)
        self.analog_input.CreateAIVoltageChan("Dev1/ai16",
                                            "",
                                            DAQmx_Val_Cfg_Default,
                                            -10.0,
                                            10.0,
                                            DAQmx_Val_Volts,
                                            None)
        # DAQmx Configure Code
        self.analog_input.CfgSampClkTiming("",
                                        10000.0,
                                        DAQmx_Val_Rising,
                                        DAQmx_Val_FiniteSamps,
                                        1000)

    def recording(self):
        # DAQmx Start Code
        self.analog_input.StartTask()
        # DAQmx Read Code
        self.analog_input.ReadAnalogF64(1000,
                                    10.0,
                                    DAQmx_Val_GroupByChannel,
                                    self.data,
                                    1000,
                                    byref(self.read),None)
        print(f"Acquired {self.read.value} points")
        return self.data


    def live_plotter(self, x_vec, y1_data, line1, identifier='', pause_time = 0.1):
        if line1==[]:
            # this is the call to matplotlib that allows dynamic plotting
            plt.ion()
            fig = plt.figure(figsize=(13,6))
            ax = fig.add_subplot(111)
            # create a variable for the line so we can later update it
            line1, = ax.plot(x_vec, y1_data, '-o', alpha=0.8)
            #update plot label/title
            plt.ylabel('voltage')
            plt.title('Title: {}'.format(identifier))
            plt.show()

        # after the figure, axis, and line are created, we only need to update the y-data
        line1.set_ydata(y1_data)
        # adjust limits if new data goes beyond bounds
        if np.min(y1_data)<=line1.axes.get_ylim()[0] or np.max(y1_data)>=line1.axes.get_ylim()[1]:
            plt.ylim([np.min(y1_data)-np.std(y1_data),np.max(y1_data)+np.std(y1_data)])
        # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
        plt.pause(pause_time)

        # return line so we can update it again in the next iteration
        return line1

    def updating_plot(self):
        y1_data = self.read

        size = 100
        x_vec = np.linspace(0,1,size+1)[0:-1]
        y_vec = np.zeros(len(x_vec))
        line1 = []
        while True:
            y_vec[-1] = rand_val
            line1 = live_plotter(x_vec,y_vec,line1)
            y_vec = np.append(y_vec[1:],0.0)



if __name__ == "__main__":
    stim = StimVoltage()
    read = ReadingVoltage()

    data = read.recording()
    stim.stimulation(1.3)
    print(data)
