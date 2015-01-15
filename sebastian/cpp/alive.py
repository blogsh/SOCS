import numpy as np
import matplotlib.pyplot as plt
import scipy.stats 
import scipy.optimize as opt

dist1 = []
dist2 = []
dist4 = []
dist32 = []

with open('build/alive1x16x16.txt') as f:
	for line in f:
		dist1.append(float(line))

with open('build/alive2x16x16.txt') as f:
	for line in f:
		dist2.append(float(line))

with open('build/alive4x16x16.txt') as f:
	for line in f:
		dist4.append(float(line))

with open('build/alive32x32.txt') as f:
	for line in f:
		dist32.append(float(line))

dist1 = np.array(dist1)
dist2 = np.array(dist2)
dist4 = np.array(dist4)
dist32 = np.array(dist32)

N1 = dist1[0]
N2 = dist2[0]
N4 = dist4[0]
N32 = dist32[0]

#dist1 = dist1[50:]
#dist2 = dist2[50:]
#dist4 = dist4[50:]

dist1 /= N1
dist2 /= N2
dist4 /= N4
dist32 /= N32

T = np.array(list(range(dist1.shape[0])))

def fitexp(dist):
	T = np.array(list(range(dist.shape[0])))

	def fitl(l):
		return np.sum((-l * T - np.log(dist))**2)

	return opt.minimize(fitl, 0.0).x

#res1 = scipy.stats.linregress(T, np.log(dist1))
#res2 = scipy.stats.linregress(T, np.log(dist2))
#res3 = scipy.stats.linregress(T, np.log(dist4))

#l1 = fitexp(dist1)
#l2 = fitexp(dist2)
#l4 = fitexp(dist4)

#print(l1, l2, l4)

plt.figure()
plt.grid(True)
plt.plot(T, dist1, 'b')

plt.plot(T, dist32, 'k')

plt.plot(T, dist2, 'g')

plt.plot(T, dist4, 'r')

plt.plot(T, 1.0 - (1.0 - dist2)**(1.0/2.0), 'g--')
plt.plot(T, 1.0 - (1.0 - dist4)**(1.0/4.0), 'r--')

plt.xlabel('Time')
plt.ylabel('Probability of Survival')

plt.legend(['1x16x16', '1x32x32', '2x16x16', '4x16x16'])

plt.show()

