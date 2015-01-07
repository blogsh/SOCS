import numpy as np
import matplotlib.pyplot as plt
import random, pickle

class Agent:
	PREY = 1
	PREDATOR = 2

	def __init__(self, type, pos):
		self.pos = pos
		self.type = type

def check_terrain(size, squares, distance):
	if size % 2 > 0: return False
	if squares % 2 > 0: return False
	if squares > size: return False

	width = size / (squares / 2)  - distance
	if width < 1: return False

	return True

def generate_terrain(land, boxes, distance):
		#assert(check_terrain(size, squares, distance))
		boxes2 = int(np.ceil(np.sqrt(boxes)))

		box_size = np.ceil(np.sqrt(land / boxes2**2))
		#while box_size % 2 != 0: box_size + 1

		size = (box_size + distance) * boxes2

		terrain = np.zeros((size, size))

		for i in range(boxes2):
			for j in range(boxes2):
				fromx = (box_size + distance) * i
				fromy = (box_size + distance) * j
				tox = fromx + box_size
				toy = fromy + box_size

				terrain[fromx:tox, fromy:toy] = 1.0

		return terrain

class Model:
	DIRECTIONS = ((0,0), (1,0), (-1,0), (0,1), (0,-1))

	def __init__(self, params):
		self.params = params

		self.terrain = generate_terrain(**params['terrain'])
		#self.size = params['terrain']['size']
		self.size = self.terrain.shape[0]

		self.lattice = [set() for _ in range(self.size**2)]
		self.preys = np.zeros((self.size, self.size))
		self.predators = np.zeros((self.size, self.size))

		self.agents = set()

		self.initialize()

	def pi(self, pos):
		return pos[0] + pos[1] * self.size

	def px(self, index):
		return index % self.size

	def py(self, index):
		return index / self.size

	def normalize(self, pos):
		x, y = pos

		if x < self.size: x += self.size
		if x >= self.size: x -= self.size

		if y < self.size: y += self.size
		if y >= self.size: y -= self.size

		return x, y

	def neighbors(self, pos):
		return map(
			self.normalize, 
			[(pos[0] + dx, pos[1] + dy) for (dx, dy) in self.DIRECTIONS]
		)

	def all(self):
		positions = []
		for x in range(self.size):
			for y in range(self.size):
				positions.append((x, y))
		return positions

	def is_safe(self, pos):
		return self.terrain[pos] > 0.5

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

			if agent.type == Agent.PREY or not random.random() < self.params['migration_rate']:
				filtered_options = list(filter(self.is_safe, options))
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

		preds = np.where(self.model.predators > 0)
		preys = np.where(self.model.preys > 0)

		self.predator.set_data(preds)
		self.prey.set_data(preys)

		plt.draw()
		plt.pause(0.0001)

def track(state, params):
	t = 0

	prey = []
	pred = []

	model = Model(params)
	while state['running'] and t < state['stop_t']:
		model.step()
		prey.append(np.sum(model.preys))
		pred.append(np.sum(model.predators))
		t += 1

		#print(t, pred[-1] + prey[-1])

		if pred[-1] + prey[-1] >= state['stop_n']:
			state['abort'] = True
			break

	if pred[-1] == 0: state['extinct'] = True

	output = dict(
		prey = prey,
		pred = pred,
		params = params,
		state = state
	)

	with open(state['output'], 'w+') as f:
		pickle.dump(output, f)

def simulate(state, params):
	model = Model(params)
	plotter = Plotter(model)

	t = 0

	while state['running']:
		t += 1

		model.step()
		plotter.track()

		if t % 100 == 0:
		#	plotter.plot()
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

	params = dict(
		terrain = dict(
			land = 16*16,
			boxes = 1,
			distance = 1
		),

		migration_rate = 1.0,
		growth_rate = 0.3,
		death_rate = 0.01,

		initial_prey = 0.05,
		initial_predator = 0.05
	)

	process = mp.Process(target=simulate, args=(state,params))
	process.start()

	raw_input()
	state['running'] = False

	process.join()

	exit()

	state['stop_t'] = 1000
	state['stop_n'] = 1200
	state['output'] = 'none.dat'

	track(state, params)
