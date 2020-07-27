import time
import PyDAQmx
from PyDAQmx import Task
import numpy as np

class Laser():
	"""
	Laser Controller interface.
 	This is a class for low level interface control of the laser which is controlled
	through a NI acquisition card.
	"""
	def __init__(self):
		self.pulse = np.zeros(1, dtype=np.uint8)

	def connect(self, line="/Dev1/port0/line2"):
		"""
		Connect the laser to the software through the NI card through
		digital lines interface.
		"""
		self.task = Task()
		self.task.CreateDOChan(line,"",PyDAQmx.DAQmx_Val_ChanForAllLines)
		self.task.StartTask()

	def disconnect(self):
		"""
		Disconnect the laser from the software through the NI card
		"""
		self.task.StopTask()

	def turn_on(self):
		"""
		Turn the laser ON
		"""
		self.pulse[0] = 1
		self.task.WriteDigitalLines(1, 1, 5.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse, None, None)

	def turn_off(self):
		"""
		Turn the laser OFF
		"""
		self.pulse[0] = 0
		self.task.WriteDigitalLines(1, 1, 5.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.pulse , None, None)


if __name__ == "__main__":
	laser = Laser()
	laser.connect()
	laser.turn_on()
	time.sleep(2)
	laser.turn_off()
	laser.disconnect()
