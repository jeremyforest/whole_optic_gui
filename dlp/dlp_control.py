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

	def get_display_mode(self):
		self.dlp.getDisplayMode()

	def set_display_mode(self, mode):
		if mode == 'static':
			self.dlp.setModeToStaticImage()
		elif mode == 'internal':
			self.dlp.setModeToInternalTestPattern()
		elif mode == 'pattern':
			self.dlp.setModeToPatternSequenceDisplay()

	## internal patterns that are usefull
	def turn_on_blue(self):
		self.dlp.displayInternalTestPattern(4)

	def turn_off_light(self):
		self.dlp.displayInternalTestPattern(1)

	def checkerboard(self):
		self.dlp.displayInternalTestPattern(13)


	## static images
	def display_static_image(self, file_path):
		self.dlp.displayStaticImage(file_path)



	def disconnect(self):
		self.dlp.close()



if __name__ == "__main__":
	dlp = Dlp()
	dlp.connect()
	dlp.turn_on_blue()
	dlp.turn_off_light()
	dlp.disconnect()
