import random
from math import sqrt
import numpy as np

# This is an example world that does the following:
#
# Generate agents for one specy, which walk around in the world.
# In the middle of the world is a lake, where no agent is allowed
# to enter. 
# Finally a renderer is written, which displays the world.
#
# There are some base classes that define the interface for the
# World and the Renderer:

from environment import World as BaseWorld
from environment import WorldRenderer as BaseWorldRenderer

# The agent class... only holding a position
class ExampleAgent:
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y

# The world class is the main part, that does most of the work.
# There is a static list called SETTINGS
# Whenever a simulation is started, it will be checked if all settings
# are provided. This will either happen through the GUI if it is used
# or manually through a dictionary or through a configuration file.

class ExampleWorld(BaseWorld):
	SETTINGS =  [
		("Number of Agents", 	"numberOfAgents",		int, 	'100'),
		("World Size", 			"size", 				int, 	'200'),
		("Lake Radius", 		"radius", 				int,	'50'),
		("Movement Rate",		"movementRate",			float, 	'0.3')
	]

	# Just validate the position (within the world boundaries? not within the lake?)
	def is_valid_position(self, x, y):
		""" Checks if a position is outside of the lake """
		size = self.settings['size']
		center = size / 2
		radius = self.settings['radius']

		if x < 0 or y < 0: return False
		if x > size or y > size: return False

		return (x - center)**2 + (y - center)**2 >= radius**2

	# Generate an agent with a reasonable starting positions outside of the lake
	def generate_agent(self):
		""" Generates a random position around the central lake """
		size = self.settings['size']
		center = size / 2
		radius = self.settings['radius']

		x = round(random.random() * size)

		if x < center - radius or x > center + radius:
			y = random.random() * size
		else:
			if random.random() > 0.5: 
				# left side of the lake
				y_max = center - sqrt(radius**2 - (x - center)**2)
				y = random.random() * y_max
			else: 
				# right side of the lake
				y_min = center + sqrt(radius**2 - (x - center)**2)
				y = y_min + (size - y_min) * random.random()

		return ExampleAgent(x, y)

	# Generate all the agents
	def __init__(self, settings):
		""" Inits the agents """
		BaseWorld.__init__(self, settings)
		self.agents = [self.generate_agent() for i in range(settings['numberOfAgents'])]

	# The movement happens with a certain probability and 
	# it should not end outside of the world or in the lake...
	def move(self, agent):
		if random.random() < self.settings['movementRate']:
			(x, y) = (agent.x, agent.y)

			x += round((random.random() - 0.5) * 2.0)
			y += round((random.random() - 0.5) * 2.0)

			if self.is_valid_position(x, y):
				(agent.x, agent.y) = (x, y)

	# Not much happening here, because the agents should 
	# only move. No predator-prey behavior yet or anything yet!
	def step(self):
		""" Performs one step of the lake world """
		for agent in self.agents: self.move(agent)

# While the World defines the simulation itself, the WorldRenderer
# defines how to display the world. The basic renderer defines
# some convenient methods, that can be used, i.e.:
#
#    - render_field(field, color)
#
#    It takes a numpy 2D-array with values between 0 and 1
# 	 and displays it on a grid. A value of 0 means "white"
#    and a value of one means "full color"
#
#    - render_agent(position, color)
#
#	 This methods renders a single agent with a certain color
#    at a certain grid position.
#
#    As for the world, some settings can be defined for the 
#    renderer with the static SETTINGS variable.
#

class ExampleWorldRenderer(BaseWorldRenderer):
	SETTINGS = [
		("Show Lake",	"showLake",		bool,	'True')
	]

	# No fancy initialization things
	def __init__(self, world, settings):
		BaseWorldRenderer.__init__(self, world, settings)
		self.update_field()

		world.settings.listeners.append(self.on_change_settings)

	def on_change_settings(self, key, value):
		if key == "radius": self.update_field()

	def update_field(self):
		size = self.world.settings['size']
		self.field = np.zeros((size, size))

		for x in range(size):
			for y in range(size):
				self.field[x, y] = self.world.is_valid_position(x, y) * 1.0

	def render(self, render):
		# Render the field (the lake) if the settings is True
		# In the GUI it can be changed on the fly during the simulation

		size = self.world.settings['size']
		render.set_size((size, size))

		if self.settings['showLake']:
			render.field(self.field, (0.0, 0.0, 1.0))

		# Render the agents with a different color for the two types
		for agent in self.world.agents:
			render.agent((agent.x, agent.y), (0.0, 0.0, 0.0))

# If the script is executed as the main script
if __name__ == '__main__':
	from gui import Environment
	#from text import Environment
	
	# Create a GUI environment, pass the world and the renderer
	# and let it run!

	env = Environment(ExampleWorld, ExampleWorldRenderer)
	env.run()
