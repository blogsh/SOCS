import numpy as np
import matplotlib.pyplot as plt
import random, model3
import multiprocessing as mp
import scipy.optimize as opt
import pickle

area = np.ones((5, 5))
terrain = np.hstack([
	area * 1.0, 
	area * 2.0, 
	area * 3.0, 
	area * 4.0,
	area * 5.0,
	area * 6.0,
	area * 7.0,
	area * 8.0,
	area * 9.0,
	area * 10.0
])
#terrain = np.hstack([area * 1.0, area * 2.0])


params = dict(
	terrain = terrain,

	migration_rate = 0.0,
	growth_rate = 0.01,
	death_rate = 0.04,

	initial_prey = 0.05,
	initial_predator = 0.05
)

K = 20
T = 10000

nsum = np.zeros((T))

if True:
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

	with open('dump.dat', 'w+') as f:
		pickle.dump(nsum, f)

#with open('dump.dat') as f:
#	nsum = pickle.load(f)

Tv = np.array(range(T))
p = nsum / float(K)
mask = np.where(p > 0.0)

def fitl(l):
	return np.sum((-l * Tv[mask] - np.log(p[mask]))**2)


res = opt.minimize(fitl, 0.0)
l = res.x
print('lambda', l)

#def fitq(q):
#	return np.sum((1.0 - (1.0 - np.exp(-l * Tv))**4 - np.exp(-q * Tv))**2)
#
#res = opt.minimize(fitq, 0.0)
#q = res.x
#print('lambda2', q)

plt.figure()
plt.plot(Tv, p, 'rx')
plt.plot(Tv, np.exp(-l * Tv), 'k')
#plt.plot(Tv, np.exp(-0.000124 * Tv), 'k--')
#plt.plot(Tv, np.exp(-q * Tv), 'k--')
plt.grid(True)
plt.ylim([0, 1.0])
plt.xlim([0, T])
plt.show()
