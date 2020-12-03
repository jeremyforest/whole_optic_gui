"""
Created on Mon Jun 17 21:46:50 2019

@author: Jeremy
"""
from OPTIMAQS.controller.dlp.dm365 import dm365
import os
import time

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
		elif mode == 'hdmi':
			self.dlp.setModeToHDMIVideo()
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

	## hdmi
	def display_hdmi_video(self):
		self.dlp.setModeToHDMIVideo()

	## pattern of images
	def set_pattern_sequence_setting(self, bitDepth=8, numOfPatters=2, Mode =0, InputTriggerType = 1, InputTriggerDelay = 0, AutoTriggerPeriod = 3333334, ExposureTime = 3333334, LEDSelect =1):
		self.dlp.setPatternSeqSetting(bitDepth,
										numOfPatters,
										Mode,
										InputTriggerType,
										InputTriggerDelay,
										AutoTriggerPeriod,
										ExposureTime,
										LEDSelect)

	def display_image_sequence(self, image_folder): #, InputTriggerDelay, AutoTriggerPeriod, ExposureTime):
		patterns = os.listdir(image_folder)
		self.set_pattern_sequence_setting(numOfPatters = len(patterns))
#		self.dlp.setPatternSeqSetting(bitDepth = 8, numOfPatters = len(patterns), Mode = 0,
#									InputTriggerType = 1, InputTriggerDelay = InputTriggerDelay,
#									AutoTriggerPeriod = AutoTriggerPeriod,
#									ExposureTime = ExposureTime, LEDSelect =1)
#		self.dlp.setModeToPatternSequenceDisplay()

		for pattern in patterns:
			self.dlp.PatternDefinition(pattern, image_folder + pattern)
			time.sleep(10)
		# self.dlp.PatternDefinition(0, image_folder + images[0])
		# time.sleep(5)
		# self.dlp.PatternDefinition(1, image_folder + images[1])
		# time.sleep(5)
		# self.dlp.PatternDefinition(2, image_folder + images[2])
		# time.sleep(5)
		# self.dlp.PatternDefinition(3, image_folder + images[3])
		# time.sleep(5)
		# self.dlp.PatternDefinition(4, image_folder + images[4])

		self.dlp.startPatternSequence()
		time_for_patterns = 15 * len(pattern) ## time for loading and disp 1 pattern * nb of patterns
		time.sleep(time_for_patterns)
		self.dlp.stoptPatternSequence()

	## disconnect
	def disconnect(self):
		self.dlp.close()



if __name__ == "__main__":
	dlp = Dlp()
	dlp.connect()
#	dlp.blue()
#	dlp.black()
#	dlp.disconnect()

#	dlp.set_display_mode('static')
#	dlp.display_static_image('C:/Users/barral/Desktop/2019_11_12/experiment_10/dlp_images/ROI_warped_0.bmp')

#	dlp.display_image_sequence('C:/Users/barral/Desktop/2020_01_16/experiment_13/dlp_images/')
