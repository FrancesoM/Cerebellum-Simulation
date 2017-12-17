import numpy as np

#population_activity è un array con il tempo di spiking di ogni neurone

Bin = 5 #ms
N_pop = spikes.size()[0]
Max_time = spikes[-1]

t_start = 0;
t_end = t_start + Bin

pop = np.array()

for i in range(0,N_pop):
	if(spikes[i] <= t_end and spikes[i] >= t_start):
		#current time falls within the window
		
