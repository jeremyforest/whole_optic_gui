# -*- coding: utf-8 -*-

from luigsneumann_SM5_modified import LuigsNeumann_SM5

class Manipulator():
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




if __name__ == '__main__':
	manip = Manipulator()
	manip.move_left()