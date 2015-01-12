import matplotlib.pyplot as plt
import numpy as np

q = np.linspace(0.0, 1.0)
r = 1.0 - (1.0 - q)**4

plt.plot(q, r)
plt.grid(True)
plt.show()
