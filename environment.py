class World:
	""" 
	Abstract World class.

	A list of settings for the world can be defined,
	in order to make them accessible by the GUI or a
	configuration file:

	SETTINGS = [
		("World Name", "name", string, "default name"),
		("Lattice Width", "width", int, 200),
		("Lattice Height", "height", int, 200)
	]

	"""
	SETTINGS = []

	def __init__(self, settings):
		self.settings = settings

	def step(self):
		""" Performs a single time step """
		raise NotImplemented()

class WorldRenderer:
	""" 
	Abstract World renderer class.

	A list of settings for the world can be defined,
	in order to make them accessible by the GUI or a
	configuration file:

	SETTINGS = [
		("Render every N steps", "renderSteps", int, 10),
		("Agent Color", "agentColor", string, , "#ff0000")
	]

	"""
	SETTINGS = []

	def __init__(self, world, settings):
		self.world = world
		self.settings = settings

	def render(self):
		raise NotImplemented()
