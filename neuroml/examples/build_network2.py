"""

Example to build a full spiking IaF network
through libNeuroML, save it as XML and validate it

"""

from neuroml import NeuroMLDocument
from neuroml import IafCell
from neuroml import Network
from neuroml import ExpOneSynapse
from neuroml import Population

from neuroml import Input
from neuroml import InputList
from neuroml import ConnectionWD
from neuroml import Projection
from neuroml import Property
from neuroml import Instance
from neuroml import Location
from neuroml import PoissonFiringSynapse

import neuroml.writers as writers
from random import random

scale = 2

nml_doc = NeuroMLDocument(id="IafNet")

nml_doc.notes = "Root notes"

IafCell0 = IafCell(id="iaf0",
                   C="1.0 nF",
                   thresh = "-50mV",
                   reset="-65mV",
                   leak_conductance="10 nS",
                   leak_reversal="-65mV")

nml_doc.iaf_cells.append(IafCell0)

IafCell1 = IafCell(id="iaf1",
                   C="1.0 nF",
                   thresh = "-50mV",
                   reset="-65mV",
                   leak_conductance="20 nS",
                   leak_reversal="-65mV")

nml_doc.iaf_cells.append(IafCell1)

syn0 = ExpOneSynapse(id="syn0",
                     gbase="65nS",
                     erev="0mV",
                     tau_decay="3ms")

nml_doc.exp_one_synapses.append(syn0)


pfs = PoissonFiringSynapse(id='pfs',
                                   average_rate='50Hz',
                                   synapse=syn0.id, 
                                   spike_target="./%s"%syn0.id)

nml_doc.poisson_firing_synapses.append(pfs)

net = Network(id="IafNet")

net.notes = "Netw notes"

nml_doc.networks.append(net)

size0 = 5*scale
pop0 = Population(id="IafPop0",
                  component=IafCell0.id,
                  size=size0)

net.populations.append(pop0)

size1 = 5*scale
pop1 = Population(id="IafPop1",
                  component=IafCell0.id,
                  size=size1)

net.populations.append(pop1)



cell_num = 4*scale
pop = Population(id="Pop_x", component=IafCell0.id, type="populationList",size=cell_num)
net.populations.append(pop)
pop.properties.append(Property(tag="color", value="1 0 0"))

x_size = 500
y_size = 500
z_size = 500
    
for i in range(cell_num):
    inst = Instance(id=i)
    pop.instances.append(inst)

    inst.location = Location(x=str(x_size*random()), y=str(y_size*random()), z=str(z_size*random()))

prob_connection = 0.5
proj_count = 0


from_pop = "Pop_x"
to_pop = "Pop_x"
projection = Projection(id="Proj", presynaptic_population=from_pop, postsynaptic_population=to_pop, synapse=syn0.id)

net.projections.append(projection)


input_list = InputList(id='il',
                     component=pfs.id,
                     populations=from_pop)

net.input_lists.append(input_list)

for pre_index in range(0,cell_num):
    
    for post_index in range(0,cell_num):
        if pre_index != post_index and random() <= prob_connection:


            pre_seg_id = 0
            post_seg_id = 0

            connection = ConnectionWD(id=proj_count, \
                                    pre_cell_id="../%s/%i/%s"%(from_pop,pre_index,IafCell0.id), \
                                    pre_segment_id=pre_seg_id, \
                                    pre_fraction_along=random(),
                                    post_cell_id="../%s/%i/%s"%(to_pop,post_index,IafCell0.id), \
                                    post_segment_id=post_seg_id,
                                    post_fraction_along=random(),
                                    weight=random(),
                                    delay='%sms'%(random()*10))

            projection.connection_wds.append(connection)
            proj_count += 1
            
    input = Input(id=pre_index, 
              target="../%s/%i/%s"%(from_pop, pre_index, pop.component), 
              destination="synapses")  
    input_list.input.append(input)
        
    

nml_file = 'tmp/testh5.nml'
writers.NeuroMLWriter.write(nml_doc, nml_file)


print("Written network file to: "+nml_file)

nml_h5_file = 'tmp/testh5.nml.h5'
writers.NeuroMLHdf5Writer.write(nml_doc, nml_h5_file)


print("Written H5 network file to: "+nml_h5_file)

sum2 = nml_doc.summary()

from neuroml.loaders import NeuroMLHdf5Loader

nml_doc2 = NeuroMLHdf5Loader.load(nml_h5_file)

sum1 = nml_doc2.summary()

assert(sum1==sum2)


###### Validate the NeuroML ######    

from neuroml.utils import validate_neuroml2

validate_neuroml2(nml_file)

