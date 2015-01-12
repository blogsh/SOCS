import numpy as np
import matplotlib.pyplot as plt
import random, model3
import multiprocessing as mp

def measure(Tmax, K, params):
	states = []

	pool = mp.Pool(processes=8)
	manager = mp.Manager()

	for k in range(K):
		state = manager.dict(
			running = True,
			stop_t = Tmax,
			extinct = False,
			endval = 0
		)

		states.append(state)
		pool.apply_async(model3.dieout, args=(state,params))

	pool.close()
	pool.join()

	extinct = 0

	for state in states:
		if state['extinct']: extinct += 1

	return extinct

def bisect_measure(K, death_rate, growth_rate):
	Tmax = 1000

	terrain = np.zeros((8, 8))
	terrain[0:4, 0:4] = 1
	terrain[0:4, 4:8] = 2
	terrain[4:8, 0:4] = 3
	terrain[4:8, 4:8] = 4

	params = dict(
		terrain = terrain,

		migration_rate = growth_rate,
		growth_rate = 0.2,
		death_rate = death_rate,

		initial_prey = 0.05,
		initial_predator = 0.05
	)

	return measure(Tmax, K, params)

if __name__ == '__main__':
	K = 10
	#growths = [0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.06, 0.07, 0.1, 0.15, 0.2, 0.4]
	growths = [0.0, 0.25, 0.5, 0.75, 1.0]

	vals = []

	for growth in growths:
		#adeath = 0.001
		#death = 0.5 * growth
		#bdeath = 0.45
		adeath = 0.01
		bdeath = 0.4

		print("MIG: %f" % growth)

		extinct = bisect_measure(K, adeath, growth)
		assert(extinct == 0)
		print("    Lower bound is OK: %d" % (extinct))

		extinct = bisect_measure(K, bdeath, growth)
		assert(extinct > 0)
		print("    Upper bound is OK: %d" % (extinct))

		while True:
			cdeath = adeath + (bdeath - adeath) * 0.5
			extinct = bisect_measure(K, cdeath, growth)

			print("    Value %f gives %d" % (cdeath, extinct))

			if extinct == 0:
				adeath = cdeath
			else:
				bdeath = cdeath

			print("    New Bounds: %f / %f" % (adeath, bdeath))

			if round(adeath, 2) == round(bdeath, 2):
				break

		print("RESULT FOR %f: %f" % (growth, adeath))
		vals.append(adeath)

	print("AVERAGE", np.sum(vals) / 10.0)
