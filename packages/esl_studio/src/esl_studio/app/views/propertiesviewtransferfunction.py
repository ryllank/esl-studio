#! /usr/bin/python

import sys
import wx.propgrid as wxpg

from .propertiesviewsimulationentity import PropertiesViewSimulationEntity

class PropertiesViewTransferFunction(PropertiesViewSimulationEntity):

    def __init__(self, propertiesViewEntityPage):
        PropertiesViewSimulationEntity.__init__(self, propertiesViewEntityPage)

    def setAttributeProperties(self, newItem, simulationEntity, ref, label="Transfer Function Attributes"):
        super(PropertiesViewTransferFunction, self).setAttributeProperties(newItem, simulationEntity, ref, label)
