# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 04:18:45 2019

@author: Jeremie
"""

from laser.laser_interface import Laser

class CrystalLaser():
	def __init__(self):
		super().__init__()
		self.laser = Laser()

	def connect(self):
		self.laser.connect()

	def disconnect(self):
		self.laser.disconnect()

	def turn_on(self):
		self.laser.turn_on()
		
	def turn_off(self):
		self.laser.turn_off()




if __name__ == "__main__":
	laser = CrystalLaser()
	laser.connect()
	laser.turn_on()
	laser.turn_off()
