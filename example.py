import auxiliary_functions as aux
import nest
import nest.voltage_trace
import nest.raster_plot
import pylab as pl
import numpy as np
from matplotlib.pylab import *

"""

Prototype of common nest functions:

	nest.Create ( 	/model - literal naming the modeltype (entry in modeldict)
			/n - the desired number of nodes
			/params - parameters for the newly created node(s)
			/gid - gid of last created node

			Description

			Create generates n new network objects of the supplied model
			type. If n is not given a single node is created. The objects
			are added as children of the current working node. params is a
			dictsionary with parameters for the new nodes. 

			Returns
			
			Array of integeres which represents the neurons ID

	nest.CopyModel(	/model - literal naming an existing model
			/new_model - literal giving the name of the copy to create must not
				exist in modeldict or synapsedict before
			/param_dict - parameters to set in the new_model
			
			Description

			A copy of model is created and registered in modeldict or synapsedict
			under the name new_model. If a parameter dictionary is given the parameters
			are set in new_model.
			Warning: It is impossible to unload modules after use of CopyModel. 
			
	nest.Connect(	source integer - the GID of the source
			target integer - the GID of the target
			weight double - the weight of the connection
			delay double - the delay of the connection
			params dict - dictionary with synapse parameters

			sources array/intvector/gidcollection - the GIDs of the sources
			targets array/intvector/gidcollection - the GIDs of the targets
			syn_model literal - the name of the synapse model see synapsedict
			syn_spec dict - dictionary with synapse model specification (see Options)
			conn_rule literal - the name of the connection rule see connruledict
			conn_spec dict - dictionary with connectivity specification (see Options)


			Description

			Connects sources to targets according to the given connectivity
			specification conn_spec. Some connection rules impose requirements.
			E.g. /one_to_one requires that sources and targets have the same
			number of elements. Others may have additional parameters
			e.g. connection probability /p for /pairwise_binomial.

			The variants with two global ids as arguments implicitly connect
			the two neurons using the all_to_all rule. If given weight delay
			syn_model and params are used for the connection.

			The variants with only literal arguments /conn_rule or /syn_model
			are shorthand for the corresponding calls with a connectivity or
			synapse specification dictionaries as explained in the Options
			section. The literals are expanded to << /rule /conn_rule >> and
			<< /model /syn_model >> respectively.

			Parameters for connectivity rules must have fixed values.

			Parameters for synapses may be fixed single values and random deviate
			specifications. 


"""

 
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
