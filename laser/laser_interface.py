# -*- coding: utf-8 -*-

import PyDAQmx
from PyDAQmx import Task
import numpy as np

class Laser():
	def __init__(self):
		self.pulse = np.zeros(1, dtype=np.uint8)

	def connect(self):
		self.task = Task()
		self.task.CreateDOChan("/Dev1/port0/line2","",PyDAQmx.DAQmx_Val_ChanForAllLines)
		self.task.StartTask()

	def disconnect(self):
		self.task.StopTask()

	# def turn_on(self):
	# 	self.pulse[0]=1
	# 	self.task.WriteDigitalLines(1, 1, 5.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse, None, None)
	#
	# def turn_off(self):
	# 	self.pulse[0]=0
	# 	self.task.WriteDigitalLines(1, 1, 5.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse , None, None)


if __name__ == "__main__":
	laser = Laser()
	laser.connect()
	laser.turn_on()
	laser.turn_off()
#	laser.disconnect()
