import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.mlab import griddata
import pickle
import numpy as np
import scipy.optimize as opt

with open('output.dat') as f:
	data = pickle.load(f)

x = []
y = []
z1 = []
z2 = []

for dataset in data:
	nsum = dataset['nsum']
	#p = float(nsum[-1]) / float(nsum[0])
	p = nsum / float(nsum[0])
	x.append(dataset['growth_rate'])
	y.append(dataset['death_rate'])

	#if p == 0.0: p = 0.0000001

	#l = - np.log(p) / 1000.0

	Tv = np.array(range(1000))
	#p = nsum / float(K)
	mask = np.where(p > 0.0)

	def fitl(l):
		return np.sum((-l * Tv[mask] - np.log(p[mask]))**2)

	res = opt.minimize(fitl, 0.0)
	l = res.x[0]

	z1.append(np.exp(-1000.0 * l))
	z2.append(p[-1])

xi = np.linspace(min(x), max(x))
yi = np.linspace(min(y), max(y))

X, Y = np.meshgrid(xi, yi)
Z1 = griddata(x, y, z1, xi, yi)
Z2 = griddata(x, y, z2, xi, yi)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_wireframe(X, Y, Z1, color='r')
ax.plot_wireframe(X, Y, Z2, color='b')
plt.xlabel('Growth')
plt.ylabel('Death')
#plt.zlabel('Size')
plt.show()
