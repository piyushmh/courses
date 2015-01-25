import math as m
import matplotlib.pyplot as plt
import numpy as np






fig, ax = plt.subplots()
x = np.linspace(0,25,100)
y = (27 - 2*x)/3
plt.axis([0,25,0,20]);
ax.plot(1,5,'ro')
ax.plot(3,5,'ro')
ax.plot(3,1,'ro')
ax.plot(4,7,'b*')
ax.plot(4,9,'b*')
ax.plot(6,7,'b*')

ax.plot(x, y, 'm')
plt.show()