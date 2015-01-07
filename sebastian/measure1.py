import numpy as np
import matplotlib.pyplot as plt
import random, model

def measure_k(Nmax, T, K, death_rate, growth_rate):
	states = []

	pool = mp.Pool(processes=8)
	manager = mp.Manager()

	print(growth_rate, death_rate)

	for k in range(K):
		params = dict(
			terrain = dict(
				land = 16 * 16,
				boxes = 1,
				distance = 0
			),

			migration_rate = 0.0,
			growth_rate = growth_rate,
			death_rate = death_rate,

			initial_prey = 0.05,
			initial_predator = 0.05
		)

		state = manager.dict(
			running = True,
			stop_t = T,
			stop_n = Nmax,
			output = 'data/d%f_g%f_k%d.dat' % (death_rate, growth_rate, k),
			extinct = False,
			abort = False
		)

		states.append(state)
		pool.apply_async(model.track, args=(state,params))

		#process = mp.Process(target=model.track, args=(state,params))
		#process.start()
		#process.join()

	pool.close()
	pool.join()

	extinct = 0
	abort = 0

	for state in states:
		if state['extinct']: extinct += 1
		if state['abort']: abort += 1

	print(extinct, abort)
	print('')

	return extinct, abort

def measure_death(Nmax, T, K, growth_rate):
	death_rate = 0.01
	abort = 0
	n = 0

	while True:
		extinct, _abort = measure_k(Nmax, T, K, death_rate, growth_rate)
		death_rate += 0.01

		n += 1
		if _abort != 0: abort += 1
		if extinct >= K:
			break

	return abort

def measure_growth(Nmax, T, K):
	growth_rate = 0.01

	while True:
		abort = measure_death(Nmax, T, K, growth_rate)
		growth_rate += 0.01

		if abort:
			break

if __name__ == '__main__':
	import multiprocessing as mp
	manager = mp.Manager()

	K = 10
	T = 1000
	Nmax = 1200

	measure_growth(Nmax, T, K)	
