import numpy as np
import matplotlib.pyplot as plt
import random, pickle

class Agent:
	PREY = 1
	PREDATOR = 2

	def __init__(self, type, pos):
		self.pos = pos
		self.type = type

class Model:
	DIRECTIONS = ((0,0), (1,0), (-1,0), (0,1), (0,-1))

	def __init__(self, params):
		self.params = params

		self.terrain = params['terrain']
		self.sizex = self.terrain.shape[0]
		self.sizey = self.terrain.shape[1]

		self.lattice = [set() for _ in range(self.sizex * self.sizey)]
		self.preys = np.zeros((self.sizex, self.sizey))
		self.predators = np.zeros((self.sizex, self.sizey))

		self.agents = set()

		self.initialize()

	def pi(self, pos):
		return pos[0] + pos[1] * self.sizex

	def px(self, index):
		return index % self.sizex

	def py(self, index):
		return index / self.sizex

	def normalize(self, pos):
		x, y = pos

		if x < self.sizex: x += self.sizex
		if x >= self.sizex: x -= self.sizex

		if y < self.sizey: y += self.sizey
		if y >= self.sizey: y -= self.sizey

		return x, y

	def neighbors(self, pos):
		return map(
			self.normalize, 
			[(pos[0] + dx, pos[1] + dy) for (dx, dy) in self.DIRECTIONS]
		)

	def all(self):
		positions = []
		for x in range(self.sizex):
			for y in range(self.sizey):
				positions.append((x, y))
		return positions

	def is_safe(self, pos):
		return self.terrain[pos] != 0

	def is_within(self, area):
		return lambda pos: self.terrain[pos] == area

	def is_empty(self, pos):
		return self.lattice[self.pi(pos)]

	def is_not_prey(self, pos):
		return self.preys[pos] == 0

	def move(self, agent, pos):
		if agent.type == Agent.PREDATOR:
			self.predators[agent.pos] -= 1
			self.predators[pos] += 1
		if agent.type == Agent.PREY:
			self.preys[agent.pos] -= 1
			self.preys[pos] += 1

		self.lattice[self.pi(agent.pos)].remove(agent)
		self.lattice[self.pi(pos)].add(agent)
		agent.pos = pos

	def create(self, type, pos):
		agent = Agent(type, pos)
		self.agents.add(agent)

		if type == Agent.PREDATOR:
			self.predators[pos] += 1
		if type == Agent.PREY:
			self.preys[pos] += 1

		self.lattice[self.pi(pos)].add(agent)

	def remove(self, agent):
		if agent.type == Agent.PREDATOR:
			self.predators[agent.pos] -= 1
		if agent.type == Agent.PREY:
			self.preys[agent.pos] -= 1

		self.lattice[self.pi(agent.pos)].remove(agent)
		self.agents.remove(agent)

	def step(self):
		# Movement
		for agent in self.agents:
			options = self.neighbors(agent.pos)
			options = list(filter(self.is_safe, options))

			if agent.type == Agent.PREY or not random.random() < self.params['migration_rate']:
				filtered_options = list(filter(self.is_within(self.terrain[agent.pos]), options))
				if len(filtered_options) == 0:
					filtered_options = options
			else:
				filtered_options = options

			if agent.type == Agent.PREY:
				filtered_options = list(filter(self.is_not_prey, filtered_options))

			if len(filtered_options) > 0:
				pos = random.choice(filtered_options)
				self.move(agent, pos)

		# Predators eat preys
		eat = np.where(((self.preys > 0) * 1.0 * (self.predators > 0) * 1.0) > 0.0)
		for i in range(len(eat[0])):
			pos = eat[0][i], eat[1][i]

			for agent in self.lattice[self.pi(pos)]:
				if agent.type == Agent.PREY:
					self.remove(agent)
					self.create(Agent.PREDATOR, agent.pos)

		# Prey is born
		growth = (self.terrain > 0.5) * (self.preys == 0)
		growth = np.where(growth)
		
		for i in range(len(growth[0])):
			pos = growth[0][i], growth[1][i]
			if random.random() < self.params['growth_rate']:
				self.create(Agent.PREY, pos)

		# Predators die
		deaths = np.where(self.predators > 0)
		for i in range(len(deaths[0])):
			pos = deaths[0][i], deaths[1][i]

			removes = []

			for agent in self.lattice[self.pi(pos)]:
				if agent.type == Agent.PREDATOR and random.random() < self.params['death_rate']:
					removes.append(agent)

			for agent in removes:
				self.remove(agent)

	def initialize(self):
		safe = list(filter(self.is_safe, self.all()))

		occupy = random.sample(safe, int(len(safe) * self.params['initial_prey']))
		for pos in occupy:
			self.create(Agent.PREY, pos)

		occupy = random.sample(safe, int(len(safe) * self.params['initial_predator']))
		for pos in occupy:
			self.create(Agent.PREDATOR, pos)

class Plotter:
	def __init__(self, model):
		self.model = model

		plt.figure(1)
		plt.imshow(self.model.terrain, cmap='gray', interpolation='none')
		plt.axis('tight')
		plt.gca().get_xaxis().set_visible(False)
		plt.gca().get_yaxis().set_visible(False)

		self.predator, = plt.plot([], [], 'r.')
		self.prey, = plt.plot([], [], 'b.')

		self.npred = []
		self.nprey = []

	def track(self):
		self.npred.append(np.sum(self.model.predators))
		self.nprey.append(np.sum(self.model.preys))

	def plotn(self):
		plt.figure(2)
		plt.plot(self.npred, 'r')
		plt.plot(self.nprey, 'b')
		plt.draw()
		plt.pause(0.0001)

	def plot(self):
		plt.figure(1)

		preds = np.where(self.model.predators.T > 0)
		preys = np.where(self.model.preys.T > 0)

		self.predator.set_data(preds)
		self.prey.set_data(preys)

		plt.draw()
		plt.pause(0.0001)

def dieout(state, params):
	t = 0

	model = Model(params)
	while state['running']:
		model.step()
		t += 1

		if np.sum(model.predators) == 0 or t > state['stop_t']:
			state['extinct'] = np.sum(model.predators) == 0
			state['endval'] = np.sum(model.predators)
			state['endtime'] = t
			break

def track(state, params):
	t = 0

	prey = 0
	pred = 0

	model = Model(params)
	while state['running'] and t < state['stop_t']:
		model.step()
		prey = np.sum(model.preys)
		pred = np.sum(model.predators)
		t += 1

		if pred + prey >= state['stop_n'] and t > 1000:
			state['abort'] = True
			break

		if pred == 0: 
			state['extinct'] = True
			break

def simulate(state, params):
	model = Model(params)
	plotter = Plotter(model)

	t = 0

	while state['running']:
		t += 1

		model.step()
		plotter.track()

		if t % 100 == 0:
			plotter.plot()
			plotter.plotn()

		nprey = np.sum(model.preys)
		npred = np.sum(model.predators)

		print(nprey, npred, nprey + npred)
		print(t)

if __name__ == '__main__':
	import multiprocessing as mp
	manager = mp.Manager()

	state = manager.dict()
	state['running'] = True

	terrain = np.zeros((8, 8))
	terrain[0:4, 0:4] = 1
	terrain[0:4, 4:8] = 2
	terrain[4:8, 0:4] = 3
	terrain[4:8, 4:8] = 4

	params = dict(
		terrain = terrain,

		migration_rate = 0.0,
		growth_rate = 0.2,
		death_rate = 0.25,

		initial_prey = 0.05,
		initial_predator = 0.05
	)

	process = mp.Process(target=simulate, args=(state,params))
	process.start()

	raw_input()
	state['running'] = False

	process.join()

	exit()

	state['stop_t'] = 2000
	dieout(state, params)
