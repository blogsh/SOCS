import numpy as np
import matplotlib.pyplot as plt

X = np.loadtxt("pred0s.tsv")
Y = np.loadtxt("water_levels.tsv")
Z = np.loadtxt("extinction_time.tsv")

plt.figure()
contours = plt.contour(Y, X, Z)
plt.clabel(contours, inline=1)
plt.ylabel(r"Initial fraction of predators")
plt.xlabel(r"Water level")
plt.colorbar()
plt.show()
