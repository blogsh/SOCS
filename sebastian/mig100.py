import matplotlib.pyplot as plt
import numpy as np

# Extinction line for the reference

growth1 = [0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.06, 0.07, 0.1, 0.15, 0.2, 0.4]
death1 = [0.02, 0.05, 0.09, 0.12, 0.15, 0.16, 0.21, 0.24, 0.265, 0.28, 0.33, 0.36]

growth4 = [0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.06, 0.07, 0.1, 0.15, 0.2, 0.4]
death4 = [0.018, 0.054, 0.07, 0.1, 0.14, 0.18, 0.19, 0.16, 0.21, 0.27, 0.27, 0.31]


#plt.plot(np.log10(growth), np.log10(death), 'x')
plt.plot(growth1, death1, 'bx-')
plt.plot(growth4, death4, 'rx-')
plt.grid(True)
plt.xlabel('Growth')
plt.ylabel('Death')
plt.legend(['1 sqare', '4 squares'], 'lower right')
plt.show()
