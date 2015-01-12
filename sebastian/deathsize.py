import matplotlib.pyplot as plt
import numpy as np

# sizes growth 1.0
size = np.array([5, 6, 7, 8, 10, 12, 15, 20, 32]) ** 2
death = [0.065, 0.088, 0.196, 0.273, 0.37, 0.39, 0.414, 0.436, 0.45]


#sizes growth 0.25
size25 = np.array([10])**2
death25 = [0.305]

#sizes growth 0.5
size50 = np.array([])**2
death50 = []

#sizes growth 0.75
size75 = np.array([])**2
death75 = []

plt.figure()
plt.plot(size, death, 'kx-')
plt.plot(size25, death25, 'rx-')
plt.plot(size50, death50, 'gx-')
plt.plot(size75, death75, 'bx-')
plt.grid(True)
plt.xlabel('Map Size')
plt.ylabel('Critical Death Rate')
plt.legend(['1.0', '0.25', '0.5', '0.75'])
plt.show()
