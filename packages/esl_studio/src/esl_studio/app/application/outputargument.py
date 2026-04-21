#! /usr/bin/python

from .argumententity import ArgumentEntity

class OutputArgument(ArgumentEntity): # or possibly InputArgumwnt

    def __init__(self, parent, type="", objectId=""):
        ArgumentEntity.__init__(self, parent, type, objectId)

    def getArgPort(self):
        argPort = None
        for port in list(self.ports().values()):
            if port.direction() == "input":
                argPort = port
                break
        return argPort

    # def load(self, entityDescrXmlElement, suppressAddName=False):

    # def specialSaveXmlAttributes(self, indent=None, level=0, saveDefaults=False):

    # def specialSaveXmlContents(self, indent=None, level=0, saveDefaults=False):

    def getPortInfoData(self, allowBlankTag=False): # [datatype, description, tag, dimensions]
        portInfo = super(OutputArgument, self).getPortInfoData(allowBlankTag)
        return portInfo

    # def validateEntityPropertyChange(self, propertyTag, newValue, val_type, val_item):

    # def updateEntityProperty(self, propertyTag, newValue, suppress_action=False):

    # def validateEntityAttributePropertyChange(self, propertyTag, newValue, attribute, tempNewAttribute, val_type, val_item, val_oldValue, val_newValue):

    # def updateEntityAttributeProperty(self, propertyTag, newValue, attribute, tempOldAttribute, suppress_action=False):
