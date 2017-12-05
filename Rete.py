import nest
import nest.voltage_trace
import nest.raster_plot
import pylab as pl
import numpy as np
import os
from matplotlib.pylab import *


#print the names of the models we need
print " ---------------- Models' names----------------------------------"
for s in nest.Models():
	if( (s.find("parrot") == 0) or (s.find("izhikevich") == 0)  ):
		print s
print "-----------------------------------------------------------------"

#Get path of the working directory
my_path = os.getcwd()

 
g = 7.1
eta = 45.0
delay = 1.5
V_th_Granular = -41.0
V_th_Golgi = -55.0     # [mV]
N_Granular = 40000     # [Sahasranamam et al, NatSciRep, 2016]; all RS
N_Golgi = 90 
N_Glomeruli= 3000  

N_neurons = N_Golgi+N_Granular+N_Glomeruli

# dati da scrivere
C_Granular = N_Granular/20        # Number of synapses per neuron
C_Golgi = N_Golgi/20
C_Glomeruli = N_Glomeruli/20

J_E = 0.1       # Peak of alpha function for synapses
J_I = -g*J_E
nu_ex = eta*V_th/(J_E*C_E)
#p_rate = 1000.0*nu_ex*C_E      # From spk/ms to spk/s
p_rate = 6 #perchè la frequenza di stimolazione è 6Hz
 
 
nest.SetKernelStatus({'print_time': True})
nest.SetKernelStatus({"overwrite_files": True,              # Parameters for writing on files
                      "data_path": my_path,
                      "data_prefix": "reteGranular_"})
 
# Neuroni rete
neu = nest.Create('izhikevich', (N_neurons-N_Glomeruli))
neu_Granular = neu[:N_Granular]
neu_Golgi = neu[(N_Granular:]

 
nest.SetStatus(neu_Granular, {'a': 0.02,'b': 0.2,'c': -65.0, 'd': 8.0,'V_th': V_th_Granular,})
nest.SetStatus(neu_Golgi, {'a': 0.1,'b': 0.2,'c': -65.0, 'd': 2.0,'V_th': V_th_Golgi})
 
 
neu_Glomeruli=nest.Create('parrot',N_Glomeruli)
 
# Neuroni esterni
noise = nest.Create('poisson_generator',150,{'rate': p_rate})
 
 
 
#Spike detector
spk = nest.Create('spike_detector', 101, params = {"to_file": True,
            "withgid": True,
            "label": "spikes"})
 
 
m = nest.Create("multimeter",
                params = {"interval": 0.1,
                         "record_from": ["V_m"],
                          "withgid": True,
                          "to_file": True,
                          "label": "multimeter"})
 
# Connections
nest.CopyModel('static_synapse_hom_w',
        'excitatory', {'weight': J_E, 'delay': delay})
nest.Connect(neuE,neu,{'rule':'fixed_indegree','indegree': C_E},'excitatory')
nest.CopyModel('static_synapse_hom_w',
        'inhibitory', {'weight': J_I, 'delay': delay})
nest.Connect(neuI,neu,{'rule':'fixed_indegree','indegree': C_I},'inhibitory')
 
nest.Connect(noise, neu, syn_spec = 'excitatory')
nest.Connect(neu,spk)
nest.Connect(m,neu)
 
 
nest.Simulate(600.0)
