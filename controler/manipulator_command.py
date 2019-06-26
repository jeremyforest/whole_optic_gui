# -*- coding: utf-8 -*-

from controler.luigsneumann_SM5_modified import LuigsNeumann_SM5

class Scope():
	def __init__(self):
		self.scope = LuigsNeumann_SM5('COM3')

	def move_left(self):
		self.scope.relative_move(10.,2)

	def move_right(self):
		self.scope.relative_move(-10.,2)

	def move_forward(self):
		self.scope.relative_move(-10.,2)

	def move_backward(self):
		self.scope.relative_move(10.,2)

	def up(self):
		self.scope.relative_move(5.,2)

	def down(self):
		self.scope.relative_move(-5.,2)

	def stop_mouvment(self):
		self.scope.stop()


if __name__ == '__main__':
	manip = Scope()
	manip.move_left()
