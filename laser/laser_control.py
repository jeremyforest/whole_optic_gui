# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 04:18:45 2019

@author: Jeremie
"""
import time
import numpy as np
from laser.laser_interface import Laser

class CrystalLaser():
	def __init__(self):
		super().__init__()
		self.laser = Laser()
		self.pulse = np.zeros(1, dtype=np.uint8)

	def connect(self):
		self.laser.connect()

	def disconnect(self):
		self.laser.disconnect()

	def turn_on(self):
		self.pulse[0]=1
		self.task.WriteDigitalLines(1, 1, 5.0, self.PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse, None, None)

	def turn_off(self):
		self.pulse[0]=0
		self.task.WriteDigitalLines(1, 1, 5.0, self.PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse , None, None)


	# a finir
	def frequency(self):
		start_time=time.time()
		while ((time.time()-start_time) < 5.0):
			self.task.WriteDigitalLines(1, 1, 5.0, self.PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse, None, None)
			time.sleep(0.5)
			self.pulse[0]=abs(self.pulse[0]-1)


if __name__ == "__main__":
	laser = CrystalLaser()
	laser.connect()
	laser.turn_on()
	laser.turn_off()
