"""
Created on Mon Jun 17 21:46:50 2019

@author: Jeremy
"""
from dlp.dm365 import dm365


class Dlp():
	def __init__(self):
		self.dlp = dm365()

	def connect(self):
		self.dlp.connect()

	def turn_on_blue(self):
		self.dlp.displayInternalTestPattern(4)

	def turn_off_light(self):
		self.dlp.displayInternalTestPattern(1)

	def disconnect(self):
		self.dlp.close()



if __name__ == "__main__":
	dlp = Dlp()
	dlp.connect()
	dlp.turn_on_blue()
	dlp.turn_off_light()
	dlp.disconnect()