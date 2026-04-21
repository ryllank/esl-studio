#! /usr/bin/python

# Strictly speaking we don't need this, as the generation of ESL is handled in the standard Simulation Entity way.
# But this is here for consistency with other special entities, and in case this should change.

from .gensimulationentity import GenSimulationEntity

class GenConstantInput(GenSimulationEntity):

    def __init__(self, genDiagramInfo, objectId, appSimEntity):
        GenSimulationEntity.__init__(self, genDiagramInfo, objectId, appSimEntity)
