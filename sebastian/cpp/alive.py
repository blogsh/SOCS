import numpy as np
import matplotlib.pyplot as plt

dist = []

with open('build/alive1x16x16.txt') as f:
	for line in f:
		dist.append(float(line))

plt.figure()
plt.grid(True)
plt.plot(dist, 'b')
plt.show()

