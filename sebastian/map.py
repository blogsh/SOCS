import numpy as np
import matplotlib.pyplot as plt
import random, model3
import multiprocessing as mp
import scipy.optimize as opt
import pickle
import time

def measure_combination(growth_rate, death_rate):
	K = 20
	T = 1000
	size = 5

	terrain = np.ones((size, size))

	___terrain = np.hstack([
		np.ones((size, size)) * 1.0,
		np.ones((size, size)) * 2.0,
		np.ones((size, size)) * 3.0,
		np.ones((size, size)) * 4.0
	])

	params = dict(
		terrain = terrain,

		migration_rate = 0.0,
		growth_rate = growth_rate,
		death_rate = death_rate,

		initial_prey = 0.05,
		initial_predator = 0.05
	)

	nsum = np.zeros((T))

	for k in range(K):
		model = model3.Model(params)
		n = np.zeros((T))

		for t in range(T):
			p = np.sum(model.predators)
			n[t] = p
			if p == 0: break
			model.step()

		nsum += (n > 0) * 1.0

	return dict(
		nsum = nsum,
		growth_rate = growth_rate,
		death_rate = death_rate,
		size = size
	)

growths = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07]
deaths = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.1, 0.2]

pool = mp.Pool(8)
manager = mp.Manager()
tasks = []

for g in growths:
	for d in deaths:
		tasks.append(pool.apply_async(measure_combination, (g, d)))

pool.close()

while True:
	ready = filter(lambda x: x.ready(), tasks)
	print("%d / %d" % (len(ready), len(tasks)))

	if len(ready) == len(tasks):
		pool.join()
		break

	time.sleep(0.1)

data = []

for task in tasks:
	res = task.get()
	data.append(res)

with open('output.dat', 'w+') as f:
	pickle.dump(data, f)
