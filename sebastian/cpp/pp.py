import numpy as np
import matplotlib.pyplot as plt

prey = []
pred = []

with open('build/pp.txt') as f:
	for line in f:
		p1, p2 = line.split(' ')
		prey.append(p1)
		pred.append(p2)

plt.figure()
plt.grid(True)
plt.plot(prey, 'b')
plt.plot(pred, 'r')
plt.xlim([0, 2500])
plt.show()

