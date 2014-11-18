import util
import numpy as np
import threading
import matplotlib
#matplotlib.use("qt4agg")
import matplotlib.pyplot as plt
import time

class Renderer:
	def __init__(self, worldRenderer):
		plt.figure()
		self.size = (100, 100)
		self.worldRenderer = worldRenderer
		self.i = 0
		plt.show(block=False)

	def agent(self, position, color):
		plt.plot(position[0], position[1], 'o', color=color)
		plt.hold(True)

	def field(self, field, color):
		plt.imshow(field)

	def set_size(self, size):
		self.size = size

	def render(self):
		plt.clf()
		plt.xlim([0, self.size[0]])
		plt.ylim([0, self.size[0]])
		self.worldRenderer.render(self)
		plt.draw()

class Environment:
	def __init__(self, World, WorldRenderer, settings = dict()):
		self.worldSettingsResolver = util.SettingsResolver(World.SETTINGS)
		self.rendererSettingsResolver = util.SettingsResolver(WorldRenderer.SETTINGS)

		self.worldSettingsResolver.resolve(settings)
		self.rendererSettingsResolver.resolve(settings)

		self.worldInstance = World(self.worldSettingsResolver.settings)
		self.worldRendererInstance = WorldRenderer(self.worldInstance, self.rendererSettingsResolver.settings)

		self.renderer = Renderer(self.worldRendererInstance)
		self.running = False

	def worker(self):
		i = 0
		while self.running:
			i += 1
			self.worldInstance.step()

			if i == 1:
				self.renderer.render()
				i = 0

	def run(self):
		self.running = True
		#worker = threading.Thread(target=self.worker)
		#worker.start()

		#raw_input()
		#worker.join()

		self.worker()
