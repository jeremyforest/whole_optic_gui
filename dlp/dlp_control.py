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
		self.dlp.setModeToPatternSequenceDisplay()
		images_path = os.listdir(image_folder)
		numOfPatters = len(images_path)
		self.dlp.setPatternSeqSetting(bitDepth = 8, numOfPatters = numOfPatters, Mode = 0, InputTriggerType = 1,
										InputTriggerDelay = InputTriggerDelay, AutoTriggerPeriod = AutoTriggerPeriod,
										ExposureTime = ExposureTime, LEDSelect =1)
		for image in images:
			image_path = os.path.join(image_path, 'f"{image}".bmp')
			self.dlp.PatternDefinition(image, image_path)
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
	dlp.disconnect()
