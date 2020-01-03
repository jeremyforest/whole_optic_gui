# -*- coding: utf-8 -*-

from controler.luigsneumann_SM5_modified import LuigsNeumann_SM5

class Scope():
	def __init__(self):
		self.scope = LuigsNeumann_SM5('COM3')
		self.axis = [1,2,3]  ## for x,y,z

	def move_left(self):
		self.scope.relative_move(10.,1)

	def move_right(self):
		self.scope.relative_move(-10.,1)

	def move_forward(self):
		self.scope.relative_move(-10.,2)

	def move_backward(self):
		self.scope.relative_move(10.,2)

	def up(self):
		self.scope.relative_move(5.,3)

	def down(self):
		self.scope.relative_move(-5.,3)

	def stop_mouvment(self):
		self.scope.stop()

	def set_origin(self):
		self.scope.set_to_zeros(self.axis)

	def go_to_origin(self):
		self.scope.go_to_zero(self.axis)

	def get_coordinates(self):
		x, y, z = [sm5.position(axis) for axis in self.axis]
		coordinates = (f"x:{x}, y:{y}, z:{z}")
		return coordinates

	def go_to_coordinates(self, x, y, z):
		self.scope.relative_move(x, 1)
		self.scope.relative_move(y, 2)
		self.scope.relative_move(z, 3)


if __name__ == '__main__':
	manip = Scope()
	manip.move_left()
