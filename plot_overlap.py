import numpy as np
import pylab as pl
from matplotlib.pylab import *

sp10 = np.load("sp10.0.npy")
xf10 = np.load("xf10.0.npy")

sp1 = np.load("sp1.0.npy")
xf1 = np.load("xf1.0.npy")

sp6 = np.load("sp6.0.npy")
xf6 = np.load("xf6.0.npy")

N = len(xf6)
P = N//3

line10, = pl.plot(xf10[:P],sp10[:P],label="p_rate: 10Hz")
pl.hold(True)
line1, = pl.plot(xf1[:P],sp1[:P],label="p_rate: 1Hz")
pl.hold(True)
line6, = pl.plot(xf6[:P],sp6[:P],label="p_rate: 6Hz")

pl.xlabel("Frequencies")
pl.ylabel("Amplitude")

pl.legend()

pl.show()


