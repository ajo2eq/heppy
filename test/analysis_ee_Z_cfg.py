'''Example configuration file for an ee->ZH->mumubb analysis in heppy, with the FCC-ee

While studying this file, open it in ipython as well as in your editor to 
get more information: 

ipython
from analysis_ee_ZH_cfg import * 
'''

import os
import copy
import heppy.framework.config as cfg
import functools

from heppy.framework.event import Event
# Event.print_patterns=['*hadrons*', '*zeds*']

import logging
# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)
logging.basicConfig(level=logging.WARNING)

# setting the random seed for reproducible results
import random
random.seed(0xdeadbeef)

# input definition
ee_Z_ddbar = cfg.Component(
    'ee_Z_ddbar',
    files = [
        'ee_Z_ddbar.root'
    ]
)

ee_Z_bbbar = cfg.Component(
    'ee_Z_bbbar',
    files = [
        'ee_Z_bbbar.root',
    ]
)

selectedComponents = [ee_Z_bbbar, ee_Z_ddbar]

# read FCC EDM events from the input root file(s)
# do help(Reader) for more information
from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    mode = 'ee',
    gen_particles = 'GenParticle',
    gen_vertices = 'GenVertex'
)

# Use a Filter to select stable gen particles for simulation
# from the output of "source" 
# help(Filter) for more information

class Stable():
    def __call__(self, x):
        return x.status()==1 and abs(x.pdgid()) not in [12,14,16] and x.pt()>1e-5

def stable(x):
    return x.status()==1 and abs(x.pdgid()) not in [12,14,16] and x.pt()>1e-5
    
from heppy.analyzers.Filter import Filter
gen_particles_stable = cfg.Analyzer(
    Filter,
    output = 'gen_particles_stable',
    # output = 'particles',
    input_objects = 'gen_particles',
    # filter_func = lambda x : x.status()==1 and abs(x.pdgid()) not in [12,14,16] and x.pt()>1e-5
    # filter_func = Stable()
    filter_func = stable 
)

# class Wrapper(object):
#     def __init__(self, func):
#         self.func = func
#     def __call__(self, *args, **kwargs):
#         return self.func(*args, **kwargs)
# gen_particles_stable.filter_func = Wrapper(gen_particles_stable.filter_func)

# configure the papas fast simulation with the CMS detector
# help(Papas) for more information
from heppy.analyzers.Papas import Papas
from heppy.papas.detectors.CMS import CMS
papas = cfg.Analyzer(
    Papas,
    instance_label = 'papas',
    detector = CMS(),
    gen_particles = 'gen_particles_stable',
    sim_particles = 'sim_particles',
    rec_particles = 'particles',
    display_filter_func = lambda ptc: ptc.e()>1.,
    display = False,
    verbose = True
)

# Make jets from the particles not used to build the best zed.
# Here the event is forced into 2 jets to target ZH, H->b bbar)
# help(JetClusterizer) for more information
from heppy.analyzers.fcc.JetClusterizer import JetClusterizer
jets = cfg.Analyzer(
    JetClusterizer,
    output = 'jets',
    particles = 'particles',
    fastjet_args = dict( njets = 2)  
)

gen_jets = cfg.Analyzer(
    JetClusterizer,
    output = 'gen_jets',
    particles = 'gen_particles_stable',
    fastjet_args = dict( njets = 2)  
)

# Build Zed candidates from pairs of jets.
from heppy.analyzers.ResonanceBuilder import ResonanceBuilder
zeds = cfg.Analyzer(
    ResonanceBuilder,
    output = 'zeds',
    leg_collection = 'jets',
    pdgid = 23
)

gen_zeds = cfg.Analyzer(
    ResonanceBuilder,
    output = 'gen_zeds',
    leg_collection = 'gen_jets',
    pdgid = 23
)

# print particles to text file for Gael
from heppy.analyzers.EventTextOutput import EventTextOutput
print_ptcs = cfg.Analyzer(
    EventTextOutput,
    particles = 'gen_particles_stable',
    )

from heppy.analyzers.ChargedHadronsFromB import ChargedHadronsFromB
charged_hadrons_from_b = cfg.Analyzer(
    ChargedHadronsFromB
    )

from heppy.analyzers.ImpactParameter import ImpactParameter
impact_parameter = cfg.Analyzer(
    ImpactParameter,
    jets = 'jets'
    )

from heppy.analyzers.ParticleTreeProducer import ParticleTreeProducer
particle_tree = cfg.Analyzer(
    ParticleTreeProducer,
    particles = 'particles'
    )


# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence( [
    source,
    gen_particles_stable,
    # papas,
    # gen_jets,
    # gen_zeds,
    # jets,
    # zeds,
    # charged_hadrons_from_b,
    # impact_parameter,
    # particle_tree
    ] )

# Specifics to read FCC events 
from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events

config = cfg.Config(
    components = selectedComponents,
    sequence = sequence,
    services = [],
    events_class = Events
)

if __name__ == '__main__':
    import sys
    from heppy.framework.looper import Looper

    import random
    random.seed(0xdeadbeef)

    def process(iev=None):
        if iev is None:
            iev = loop.iEvent
        loop.process(iev)
        if display:
            display.draw()

    def next():
        loop.process(loop.iEvent+1)
        if display:
            display.draw()            

    iev = None
    usage = '''usage: python analysis_ee_ZH_cfg.py [ievent]
    
    Provide ievent as an integer, or loop on the first events.
    You can also use this configuration file in this way: 
    
    heppy_loop.py OutDir/ analysis_ee_ZH_cfg.py -f -N 100 
    '''
    if len(sys.argv)==2:
        papas.display = True
        try:
            iev = int(sys.argv[1])
        except ValueError:
            print usage
            sys.exit(1)
    elif len(sys.argv)>2: 
        print usage
        sys.exit(1)
            
        
    loop = Looper( 'looper', config,
                   nEvents=10,
                   nPrint=1,
                   timeReport=True)
    
    simulation = None
    for ana in loop.analyzers: 
        if hasattr(ana, 'display'):
            simulation = ana
    display = getattr(simulation, 'display', None)
    simulator = getattr(simulation, 'simulator', None)
    if simulator: 
        detector = simulator.detector
    if iev is not None:
        process(iev)
        process(iev)
        process(iev)
    else:
        loop.loop()
        loop.write()
