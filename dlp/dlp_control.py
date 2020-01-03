"""
Created on Mon Jun 17 21:46:50 2019

@author: Jeremy
"""
from dlp.dm365 import dm365
import os
import time
import pdb


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

	## internal patterns
	def checkboard_small(self):
		self.dlp.displayInternalTestPattern(0)
	def black(self):
		self.dlp.displayInternalTestPattern(1)
	def white(self):
		self.dlp.displayInternalTestPattern(2)
	def green(self):
		self.dlp.displayInternalTestPattern(3)
	def blue(self):
		self.dlp.displayInternalTestPattern(4)
	def red(self):
		self.dlp.displayInternalTestPattern(5)
	def vertical_lines_1(self):
		self.dlp.displayInternalTestPattern(6)
	def horizontal_lines_1(self):
		self.dlp.displayInternalTestPattern(7)
	def vertical_lines_2(self):
		self.dlp.displayInternalTestPattern(8)
	def horizontal_lines_2(self):
		self.dlp.displayInternalTestPattern(9)
	def diagonal_lines(self):
		self.dlp.displayInternalTestPattern(10)
	def grey_ramp_vertical(self):
		self.dlp.displayInternalTestPattern(11)
	def grey_ramp_horizontal(self):
		self.dlp.displayInternalTestPattern(12)
	def checkerboard_big(self):
		self.dlp.displayInternalTestPattern(13)

	## static images
	def display_static_image(self, file_path):
		self.dlp.displayStaticImage(file_path)

	## pattern of images
	def display_image_sequence(self, image_folder, InputTriggerDelay, AutoTriggerPeriod, ExposureTime):
		pdb.set_trace()
		
		images = os.listdir(image_folder)
#		numOfPatters = len(images)
#		self.dlp.setPatternSeqSetting()
#		self.dlp.setPatternSeqSetting(bitDepth = 8, numOfPatters = numOfPatters, Mode = 0, InputTriggerType = 1,
#										InputTriggerDelay = InputTriggerDelay, AutoTriggerPeriod = AutoTriggerPeriod,
#										ExposureTime = ExposureTime, LEDSelect =1)
#		self.dlp.setModeToPatternSequenceDisplay()

		self.dlp.PatternDefinition(0, image_folder + images[0])
		time.sleep(5)
		self.dlp.PatternDefinition(1, image_folder + images[1])
		time.sleep(5)
		self.dlp.PatternDefinition(2, image_folder + images[2])
		time.sleep(5)
		self.dlp.PatternDefinition(3, image_folder + images[3])
		time.sleep(5)
		self.dlp.PatternDefinition(4, image_folder + images[4])

#		i=0
#		for image in images:
#			print(image)
#			print(i)
#			self.dlp.PatternDefinition(i, image_folder + image)
#			i+=1
		self.dlp.startPatternSequence()
		time.sleep(30)
		self.dlp.stoptPatternSequence()

	## disconnect
	def disconnect(self):
		self.dlp.close()



if __name__ == "__main__":
	dlp = Dlp()
	dlp.connect()
	dlp.blue()
	dlp.black()
#	dlp.disconnect()

#	dlp.set_display_mode('static')
#	dlp.display_static_image('C:/Users/barral/Desktop/2019_11_12/experiment_10/dlp_images/ROI_warped_0.bmp')
	
	
#
	InputTriggerDelay = 0
	AutoTriggerPeriod = 3333334
	ExposureTime = 3333334

	dlp.display_image_sequence('C:/Users/barral/Desktop/2019_11_12/experiment_10/dlp_images/', InputTriggerDelay, AutoTriggerPeriod, ExposureTime)




