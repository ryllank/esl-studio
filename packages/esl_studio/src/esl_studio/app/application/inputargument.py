#! /usr/bin/python

from .argumententity import ArgumentEntity

class InputArgument(ArgumentEntity):

    def __init__(self, parent, type="", objectId=""):
        ArgumentEntity.__init__(self, parent, type, objectId)

    def getArgPort(self):
        argPort = None
        for port in list(self.ports().values()):
            if port.direction() == "output":
                argPort = port
                break
        return argPort

    #def load(self, entityDescrXmlElement, suppressAddName=False):

    # def specialSaveXmlAttributes(self, indent=None, level=0, saveDefaults=False):

    # def specialSaveXmlContents(self, indent=None, level=0, saveDefaults=False):

    def getPortInfoData(self, allowBlankTag=False): # [datatype, description, tag, dimensions]
        portInfo = None
        attribute = self.attributes().get('ATTR')
        isAttr = 'False'
        if attribute:
            isAttr = attribute.valueStr()
        if isAttr != 'True':
            portInfo = super(InputArgument, self).getPortInfoData(allowBlankTag)
        return portInfo

    def getAttributeInfoData(self): # [datatype, description, tag, dimensions, defaultValue]
        attributeInfo = None
        attribute = self.attributes().get('ATTR')
        isAttr = 'False'
        if attribute:
            isAttr = attribute.valueStr()
        if isAttr == 'True':
            argPort = self.getArgPort()
            if argPort is not None:
                datatype = argPort.datatype()
                tag = self.getArgName() # returns default arg name if not specified
                description = ''
                attribute = self.attributes().get('ARGDESC')
                if attribute:
                    description = attribute.valueStr()
                if not description:
                    description = tag  # description same as tag
                dimensions = ""
                attribute = self.attributes().get('ARGDIMS')
                if attribute: dimensions = attribute.valueStr()
                defaultValue = ""
                # Input Arguments do not have an INIT property - not even for Attributes so defaultValue will be the appropriate zero
                if not defaultValue:
                    defaultValue = '0.0'
                    if datatype == 'Integer':
                        defaultValue = '0'
                    elif datatype == 'Logical':
                        defaultValue = 'FALSE'
                    if dimensions:
                        pos, dimensionality = self._parseEsl.parseDimensions(dimensions, 0, None, checkNothingLeft=True, allowStar=False)
                        defaultValue = str(dimensionality.size()) + "*" + defaultValue
                attributeInfo = [ datatype, description, tag, dimensions, defaultValue ]
        return attributeInfo

    # def updateEntity(self, updateXmlElement):

    # def validateEntityPropertyChange(self, propertyTag, newValue, val_type, val_item):

    # def updateEntityProperty(self, propertyTag, newValue, suppress_action=False):

    # def validateEntityAttributePropertyChange(self, propertyTag, newValue, attribute, tempNewAttribute, val_type, val_item, val_oldValue, val_newValue):

    # def updateEntityAttributeProperty(self, propertyTag, newValue, attribute, tempOldAttribute, suppress_action=False):
