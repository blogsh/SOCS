import matplotlib.pyplot as plt
import numpy as np

# Extinction line for the reference

growth1 = [0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.06, 0.07, 0.1, 0.15, 0.2, 0.4]
death1 = [0.02, 0.05, 0.09, 0.12, 0.15, 0.16, 0.21, 0.24, 0.265, 0.28, 0.33, 0.36]

growth4 = [0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.06, 0.07, 0.1, 0.15, 0.2, 0.4]
death4 = [0.01, 0.035, 0.056, 0.085, 0.11, 0.15, 0.17, 0.178, 0.217, 0.27, 0.29, 0.36]

growth9 = [0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.06, 0.07, 0.1, 0.15, 0.2, 0.4]
death9 = [0.0088, 0.026, 0.046, 0.067, 0.087, 0.126, 0.137, 0.155, 0.169, 0.219, 0.247, 0.344]

#plt.plot(np.log10(growth), np.log10(death), 'x')
plt.plot(growth1, death1, 'bx-')
plt.plot(growth4, death4, 'rx-')
plt.plot(growth9, death9, 'kx-')
plt.grid(True)
plt.xlabel('Growth')
plt.ylabel('Death')
plt.legend(['1 sqare', '4 squares', '9 squares'], 'lower right')
plt.show()
