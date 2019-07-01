# -*- coding: utf-8 -*-
import time
import PyDAQmx
from PyDAQmx import Task
import numpy as np

class Laser():
	def __init__(self):
		self.pulse = np.zeros(1, dtype=np.uint8)
		self.task = Task()

	def connect(self):
		self.task.CreateDOChan("/Dev1/port0/line2","",PyDAQmx.DAQmx_Val_ChanForAllLines)
		self.task.StartTask()

	def disconnect(self):
		self.task.StopTask()

	def turn_on(self):
	 	self.pulse[0]=1
	 	self.task.WriteDigitalLines(1, 1, 5.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse, None, None)
	
	def turn_off(self):
	 	self.pulse[0]=0
	 	self.task.WriteDigitalLines(1, 1, 5.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse , None, None)


	# a finir
	def frequency(self):
		start_time=time.time()
		while ((time.time()-start_time) < 5.0):
			self.task.WriteDigitalLines(1, 1, 5.0, self.PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse, None, None)
			time.sleep(0.5)
			self.pulse[0]=abs(self.pulse[0]-1)


if __name__ == "__main__":
	laser = Laser()
	laser.connect()
	laser.turn_on()
	laser.turn_off()
#	laser.disconnect()
