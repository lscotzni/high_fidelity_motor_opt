import numpy as np
import matplotlib.pyplot as plt 

x = np.linspace(0,1,10)
y = x**2

plt.figure(1)
plt.plot(x,y)
plt.show()