from environment import World as BaseWorld
from environment import WorldRenderer as BaseWorldRenderer

class EmptyWorld(BaseWorld):
	SETTINGS =  []

	def __init__(self, settings):
		BaseWorld.__init__(self, settings)
		# Implement initialization here

	def step(self):
		# Implement time step here
		pass

class EmptyWorldRenderer(BaseWorldRenderer):
	SETTINGS = []

	def __init__(self, world, settings):
		BaseWorldRenderer.__init__(self, world, settings)
		# Implement initialization here

	def render(self, render):
		# Implement rendering here
		pass

if __name__ == '__main__':
	from gui import Environment
	env = Environment(EmptyWorld, EmptyWorldRenderer)
	env.run()
