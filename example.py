import auxiliary_functions as aux
import nest
import nest.voltage_trace
import nest.raster_plot
import pylab as pl
import numpy as np
from matplotlib.pylab import *
 
 
g = 7.1
eta = 45.0
delay = 1.5
V_th = 30.0     # [mV]
N_E = 4000      # [Sahasranamam et al, NatSciRep, 2016]; all RS
N_I = 1000     
F = 0.8     # Fraction of BS in the inhibitory population
N_neurons = N_E+N_I
C_E = N_E/20        # Number of synapses per neuron
C_I = N_I/20
J_E = 0.1       # Peak of alpha function for synapses
J_I = -g*J_E
nu_ex = eta*V_th/(J_E*C_E)
#p_rate = 1000.0*nu_ex*C_E      # From spk/ms to spk/s
p_rate = 1000.0*eta
 
 
nest.SetKernelStatus({'print_time': True})
nest.SetKernelStatus({"overwrite_files": True,              # Parameters for writing on files
                      "data_path": "/home/realnet/workspace/nest-simulator",
                      "data_prefix": "reteGranular_"})
 
# Neuroni rete
neu = nest.Create('izhikevich', N_neurons)
neuE = neu[:N_E]
neuI = neu[N_E:]
neuFS = neuI[:int(N_I*(1-F))]
neuBS = neuI[int(N_I*(1-F)):]
 
nest.SetStatus(neuE, {'a': 0.02,'b': 0.2,'c': -65.0, 'd': 8.0,'V_th': V_th})
nest.SetStatus(neuFS, {'a': 0.1,'b': 0.2,'c': -65.0, 'd': 2.0,'V_th': V_th})
 
 
nest.SetStatus(neuBS, {'a': 0.02,'b': 0.2,'c': -50.0, 'd': 2.0,'V_th': V_th})
 
# Neuroni esterni
noise = nest.Create('poisson_generator',1,{'rate': p_rate})
 
 
 
#Spike detector
spk = nest.Create('spike_detector', params = {"to_file": True,
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
