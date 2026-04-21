#! /usr/bin/python

from .propertiesviewcallentity import PropertiesViewCallEntity

class PropertiesViewFunctionCall(PropertiesViewCallEntity):

    def __init__(self, propertiesViewEntityPage):
        PropertiesViewCallEntity.__init__(self, propertiesViewEntityPage)
