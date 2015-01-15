import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.mlab import griddata

migration = []
initial = []
avgtime = []

with open('data4.txt') as f:
	for line in f:
		m, i, a = line.split(' ')
		if float(i) > 0.0:
			migration.append(float(m))
			initial.append(float(i))
			avgtime.append(float(a))

xi = np.linspace(min(migration), max(migration))
yi = np.linspace(min(initial), max(initial))

X, Y = np.meshgrid(xi, yi)

Z = griddata(migration, initial, avgtime, xi, yi)

fig = plt.figure()
ax = fig.add_subplot(111)#, projection='3d')
#ax.plot_wireframe(X, Y, Z, color='b')
contours = plt.contour(X, Y, Z)
plt.xlabel('Migration')
plt.ylabel('Initial')
plt.clabel(contours, inline=1)
plt.colorbar()

plt.plot([0.4, 0.4], [0.5, 0.05], 'k--')
#plt.zlabel('Size')
plt.show()


