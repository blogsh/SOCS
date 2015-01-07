import numpy as np
import matplotlib.pyplot as plt
import random, model
import multiprocessing as mp

def measure(Tmax, Nmax, K, params):
	states = []

	pool = mp.Pool(processes=8)
	manager = mp.Manager()

	for k in range(K):
		state = manager.dict(
			running = True,
			stop_t = Tmax,
			stop_n = Nmax,
			output = 'data/d%f_g%f_k%d.dat' % (params['death_rate'], params['growth_rate'], k),
			extinct = False,
			abort = False
		)

		states.append(state)
		pool.apply_async(model.track, args=(state,params))

	pool.close()
	pool.join()

	extinct = 0
	abort = 0

	for state in states:
		if state['extinct']: extinct += 1
		if state['abort']: abort += 1

	return extinct, abort

def bisect_measure(K, death_rate, growth_rate):
	Tmax = 1000
	Nmax = 1200

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

	return measure(Tmax, Nmax, K, params)

if __name__ == '__main__':
	K = 10
	growth = 0.07

	adeath = 0.15
	bdeath = 0.3

	extinct, abort = bisect_measure(K, adeath, growth)
	assert(extinct == 0)
	print("Lower bound is OK: %d/%d" % (extinct,abort))

	extinct, abort = bisect_measure(K, bdeath, growth)
	assert(extinct > 0)
	print("Upper bound is OK: %d/%d" % (extinct,abort))

	while True:
		cdeath = adeath + (bdeath - adeath) * 0.5
		extinct, abort = bisect_measure(K, cdeath, growth)

		print("Value %f gives %d/%d" % (cdeath, extinct, abort))

		if extinct == 0:
			adeath = cdeath
		else:
			bdeath = cdeath

		print("New Bounds: %f / %f" % (adeath, bdeath))
