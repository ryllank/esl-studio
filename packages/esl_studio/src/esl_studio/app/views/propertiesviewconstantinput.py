#! /usr/bin/python

# Strictly speaking we don't need this, as properties are handled in the standard Simulation Entity way.
# But this is here for consistency with other special entities, and in case this should change.

from .propertiesviewsimulationentity import PropertiesViewSimulationEntity

class PropertiesViewConstantInput(PropertiesViewSimulationEntity):

    def __init__(self, propertiesViewEntityPage):
        PropertiesViewSimulationEntity.__init__(self, propertiesViewEntityPage)
