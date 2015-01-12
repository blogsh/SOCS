import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.mlab import griddata
import pickle
import numpy as np
import scipy.optimize as opt

with open('output4x55.dat') as f:
	data1 = pickle.load(f)

with open('output_combined.dat') as f:
	data2 = pickle.load(f)

x1 = []
x2 = []

y1 = []
y2 = []

z1 = []
z2 = []

for dataset in data1:
	nsum = dataset['nsum']
	p = nsum / float(nsum[0])
	x1.append(dataset['growth_rate'])
	y1.append(dataset['death_rate'])

	Tv = np.array(range(1000))
	mask = np.where(p > 0.0)

	def fitl(l):
		return np.sum((-l * Tv[mask] - np.log(p[mask]))**2)

	res = opt.minimize(fitl, 0.0)
	l = res.x[0]

	z1.append(1000.0 * l)
	#z1.append(np.exp(-1000.0 * l))
	#z1.append(p[-1])

for dataset in data2:
	nsum = dataset['nsum']
	p = nsum / float(nsum[0])
	x2.append(dataset['growth_rate'])
	y2.append(dataset['death_rate'])

	Tv = np.array(range(1000))
	mask = np.where(p > 0.0)

	def fitl(l):
		return np.sum((-l * Tv[mask] - np.log(p[mask]))**2)

	res = opt.minimize(fitl, 0.0)
	l = res.x[0]

	z2.append(1000.0 * l)
	#z2.append(np.exp(-1000.0 * l))
	#z2.append(p[-1])

xi1 = np.linspace(min(x1), max(x1))
yi1 = np.linspace(min(y1), max(y1))
xi2 = np.linspace(min(x2), max(x2))
yi2 = np.linspace(min(y2), max(y2))

X1, Y1 = np.meshgrid(xi1, yi1)
X2, Y2 = np.meshgrid(xi2, yi2)

Z1 = griddata(x1, y1, z1, xi1, yi1)
Z2 = griddata(x2, y2, z2, xi2, yi2)

#Z1 *= 0.0

#mask = np.where((Z1 > 0.0) * (Z2 > 0.0))

#Z2 = Z1 / Z2
#Z = Z2[mask] / Z1[mask]
#print(Z)
#print(np.sum(Z) / float(Z.shape[0]))

#Z1 = np.exp(-Z1)
#Z2 = -np.log( 1.0 - (1.0 - np.exp(-Z2)) ** 4 )
#Z2 /= 1.266


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_wireframe(X1, Y1, Z1, color='r')
ax.plot_wireframe(X2, Y2, Z2, color='b')
plt.xlabel('Growth')
plt.ylabel('Death')
#plt.zlabel('Size')
plt.show()
