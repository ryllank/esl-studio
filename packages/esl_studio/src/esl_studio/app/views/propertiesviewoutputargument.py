#! /usr/bin/python

from .propertiesviewargumententity import PropertiesViewArgumentEntity

class PropertiesViewOutputArgument(PropertiesViewArgumentEntity):

    def __init__(self, propertiesViewEntityPage):
        PropertiesViewArgumentEntity.__init__(self, propertiesViewEntityPage)
