import matplotlib.pyplot as plt
import numpy as np

# Extinction line for the reference

growth16 = [0.01, 0.02, 0.03, 0.05, 0.07, 0.1, 0.15, 0.2, 0.4, 0.06, 0.005, 0.001]
death16 = [0.09, 0.12, 0.15, 0.16, 0.24, 0.265, 0.28, 0.33, 0.36, 0.21, 0.05, 0.02]

growth8 = [0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.06, 0.07, 0.1, 0.15, 0.2, 0.4]
death8 = [0.0081, 0.03, 0.04, 0.064, 0.053, 0.068, 0.084, 0.1, 0.12, 0.14, 0.164, 0.19]


#plt.plot(np.log10(growth), np.log10(death), 'x')
plt.plot(growth16, death16, 'xb')
plt.plot(growth8, death8, 'xr')
plt.grid(True)
plt.xlabel('Growth')
plt.ylabel('Death')
plt.legend(['16x16', '8x8'], 'lower right')
plt.show()
