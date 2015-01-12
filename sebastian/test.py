import numpy as np
import matplotlib.pyplot as plt
import random, model3
import multiprocessing as mp
import scipy.optimize as opt
import pickle
import time

K = 20
T = 2000
size = 5

terrain = np.ones((size, size))

terrain = np.hstack([
	np.ones((size, size)) * 1.0,
	np.ones((size, size)) * 2.0,
	np.ones((size, size)) * 3.0,
	np.ones((size, size)) * 4.0
])

params = dict(
	terrain = terrain,

	migration_rate = 10.0 ** (-2),
	growth_rate = 0.04,
	death_rate = 0.09,

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
		print(k, t)

	nsum += (n > 0) * 1.0

nsum = nsum.astype(np.float)
p = nsum / nsum[0]
print(p[-1])

plt.figure()
plt.plot(range(T), p)
plt.xlim([0, T])
plt.ylim([0, 1])
plt.grid(True)
plt.show()
