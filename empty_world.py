from environment import World as BaseWorld
from environment import WorldRenderer as BaseWorldRenderer

class EmptyWorld(BaseWorld):
	SETTINGS =  []

	def __init__(self, settings):
		World.__init__(self, settings)
		# Implement initialization here

	def step(self):
		# Implement time step here
		pass

class EmptyWorldRenderer(BaseWorldRenderer):
	SETTINGS = []

	def __init__(self, world, settings):
		BaseRenderer.__init__(self, world, settings)
		# Implement initialization here

	def render(self):
		# Implement rendering here
		pass

if __name__ == '__init__':
	from environment import GUIEnvironment
	env = GUIEnvironment(EmptyWorld, EmptyWorldRenderer)
	env.run()
