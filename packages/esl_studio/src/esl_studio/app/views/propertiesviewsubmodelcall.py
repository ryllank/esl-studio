#! /usr/bin/python

from .propertiesviewcallentity import PropertiesViewCallEntity

class PropertiesViewSubmodelCall(PropertiesViewCallEntity):

    def __init__(self, propertiesViewEntityPage):
        PropertiesViewCallEntity.__init__(self, propertiesViewEntityPage)
