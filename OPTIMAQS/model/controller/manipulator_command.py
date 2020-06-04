# -*- coding: utf-8 -*-

from OPTIMAQS.controller.controller.luigsneumann_SM5_modified import LuigsNeumann_SM5

class Controller():
	def __init__(self):
		self.controler = LuigsNeumann_SM5('COM3')
		self.axis = [1,2,3]  ## for x,y,z

	def move_left(self):
		self.controler.relative_move(10.,1)

	def move_right(self):
		self.controler.relative_move(-10.,1)

	def move_forward(self):
		self.controler.relative_move(-10.,2)

	def move_backward(self):
		self.controler.relative_move(10.,2)

	def up(self):
		self.controler.relative_move(5.,3)

	def down(self):
		self.controler.relative_move(-5.,3)

	def stop_mouvment(self):
		self.controler.stop()

	def set_origin(self):
		self.controler.set_to_zeros(self.axis)

	def go_to_origin(self):
		self.controler.go_to_zero(self.axis)

	def get_coordinates(self):
		x, y, z = [sm5.position(axis) for axis in self.axis]
		coordinates = (f"x:{x}, y:{y}, z:{z}")
		return coordinates

	def go_to_coordinates(self, x, y, z):
		self.controler.relative_move(x, 1)
		self.controler.relative_move(y, 2)
		self.controler.relative_move(z, 3)


if __name__ == '__main__':
	manip = Controller()
	manip.move_left()
