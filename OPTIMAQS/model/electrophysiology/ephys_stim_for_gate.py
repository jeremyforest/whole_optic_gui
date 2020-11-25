# -*- coding: utf-8 -*-
import time
import PyDAQmx
from PyDAQmx import Task
import numpy as np



#value = 1.3
#
#task = Task()
#task.CreateAOVoltageChan("/Dev1/ao0","",-10.0,10.0,PyDAQmx.DAQmx_Val_Volts,None)
#task.StartTask()
#task.WriteAnalogScalarF64(1,10.0,value,None)
#time.sleep(5)
#task.StopTask()
#
#





class Stim():
	def __init__(self):
		self.pulse = np.zeros(1, dtype=np.uint8)
		self.task = Task()

	def connect(self):
		self.task.CreateDOChan("/Dev1/port0/line3","",PyDAQmx.DAQmx_Val_ChanForAllLines)
		self.task.StartTask()

	def disconnect(self):
		self.task.StopTask()

	def stim_on(self):
	 	self.pulse[0]=1
	 	self.task.WriteDigitalLines(1, 1, 5.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse, None, None)

	def stim_off(self):
	 	self.pulse[0]=0
	 	self.task.WriteDigitalLines(1, 1, 5.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse , None, None)

#	def freq(self):
#	 	ctr_ini_delay = 0 # sec
#	 	ctr_period = 0.1 # sec
#	 	ctr_duty_cycle = 0.01
#	 	self.task.CreateCOPulseChanFreq("/Dev1/port0/line3", "",  PyDAQmx.DAQmx_Val_Hz,  PyDAQmx.DAQmx_Val_Low, ctr_ini_delay,  1/float(ctr_period), ctr_duty_cycle)
#	 	self.task.CfgImplicitTiming(PyDAQmx.DAQmx_Val_ContSamps,  1000)






if __name__ == "__main__":
	laser = Stim()
	laser.connect()
#	laser.freq()
	laser.stim_on()
	time.sleep(0.5)
	laser.stim_off()
	laser.disconnect()
#
#
#ctr_ini_delay = 0 # sec
#ctr_period = 0.1 # sec
#ctr_duty_cycle = 0.01
#task = PyDAQmx.Task()
#task.CreateCOPulseChanFreq("Dev1/ao0", "",  PyDAQmx.DAQmx_Val_Hz,  PyDAQmx.DAQmx_Val_Low, ctr_ini_delay,  1/float(ctr_period), ctr_duty_cycle)
#task.CfgImplicitTiming(PyDAQmx.DAQmx_Val_ContSamps,  1000)
#task.StartTask()
#sleep(5)
#task.StopTask()
#task.ClearTask()



