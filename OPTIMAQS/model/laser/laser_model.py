from OPTIMAQS.controller.laser.laser_interface import Laser

class CrystalLaser():
	"""
	Laser model interface.
	Higher order control of the Laser.
	"""
	def __init__(self):
		super().__init__()
		self.laser = Laser()

	def connect(self):
		"""
		Connect to the laser
		"""
		self.laser.connect()

	def disconnect(self):
		"""
		Disconnect from laser
		"""
		self.laser.disconnect()

	def turn_on(self):
		"""
		Turn laser on
		"""
		self.laser.turn_on()

	def turn_off(self):
		"""
		Turn laser off
		"""
		self.laser.turn_off()




if __name__ == "__main__":
	laser = CrystalLaser()
	laser.connect()
	laser.turn_on()
	laser.turn_off()
