#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

#---------------rapporti di convergenza----------------
C_mossy_Glo = 20
C_Glo_Gra = 4
C_Glo_Gol = 70
C_Gol_Gol = 400
C_Gol_Gra = 4
C_Gra_Parallel = 1000
#------------------------------------------------------

#---------------conduttanze----------------------------
J_E = 0.1       # Peak of alpha function for synapses
J_I = -g*J_E
nu_ex = eta*V_th/(J_E*C_E)
#p_rate = 1000.0*nu_ex*C_E      # From spk/ms to spk/s
p_rate = 6 #perchè la frequenza di stimolazione è 6Hz
#------------------------------------------------------
 
 
nest.SetKernelStatus({'print_time': True})
nest.SetKernelStatus({"overwrite_files": True,              # Parameters for writing on files
                      "data_path": my_path,
                      "data_prefix": "reteGranular_"})
 
# Neuroni rete
neu = nest.Create('izhikevich', (N_neurons-N_Glomeruli))
neu_Granular = neu[:N_Granular]
neu_Golgi = neu[(N_Granular:]

 
#nest.SetStatus(neu_Granular, {'a': 0.02,'b': 0.2,'c': -65.0, 'd': 8.0,'V_th': V_th_Granular,})
nest.SetStatus(neu_Granular, {'a': 0.1,'b': 0.2,'c': -65.0, 'd': 2.0,'V_th': V_th_Granular})
nest.SetStatus(neu_Golgi, {'a': 0.1,'b': 0.2,'c': -65.0, 'd': 2.0,'V_th': V_th_Golgi})
#da mettere a variare i diversi input, mentre rimane invariato il fatto di avere bursting o spike o altro.
#per i valori che possiamo recuperare da fisiologia li mettiamo fissi (con il valore pari al valore della grandezza con le stess eunità di misura)
 
 
neu_Glomeruli=nest.Create('parrot',N_Glomeruli)
 
# Neuroni esterni
mossy = nest.Create('poisson_generator',150,{'rate': p_rate}) #il p-rate va bene che sia 6, da controllare (da variare nel range)
#le mossy fibers le modellizziamo come un generatore di poisson (quindi le mossy sono poisson)
 
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
nest.CopyModel('static_synapse_hom_w',
        'inhibitory', {'weight': J_I, 'delay': delay})

nest.Connect(mossy,neu_Glomeruli)
nest.Connect(neu_Glomeruli,neu_Granular,{'rule':'fixed_indegree','indegree': C_Glo_Gra},'excitatory')
nest.Connect(neu_Golgi,neu_Granular,{'rule':'fixed_indegree','indegree': C_Gol_Gra},'inhibitory')
nest.Connect(neu_Golgi,neu_Golgi,{'rule':'fixed_indegree','indegree': C_Gol_Gol},'inhibitory')
nest.Connect(neu_Glomeruli,neu_Golgi,{'rule':'fixed_indegree','indegree': C_Glo_Gol},'excitatory')
nest.Connect(neu_Granular,spk)

#nest.Connect(spk,m)
 
nest.Simulate(1000.0)
nest.ruster_plot.from_device(spk, hist=True)

#rusterplot alla fine di ogni simulazione, come input poisson sia segnale che rumore. usiamo un poisson per tutti i neuroni a diverse frequenze.
#siamo felici quando dando un input a una frequenza tra 8-10 Hz le granular hanno andamento oscialltorio a 6 Hz di risonanza.
