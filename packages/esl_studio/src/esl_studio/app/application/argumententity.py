#! /usr/bin/python

from ..esl.parseesl import ParseEsl, DimensionalityParseObject
from .simulationentity import SimulationEntity
from .applicationtypes import CALLABLEMODULETYPES
from .attribute import Attribute
from .port import PortConnectorSeparator
from ..esl import esl
from .diagraminfo import DiagramInfo
from . import diagramactions as dgAction

class ArgumentEntity(SimulationEntity):

    # Note: Makes use of the following defined attributes
    SpecialAttributeTags = [
        "ARG",      # Arg Name: An ESL identifier for the argument in the generated ESL subprogram.
        "ARGDESC",  # Arg Description: Description for this subprogram argument.
        "ARGDIMS",  # Dimensions: For ESL Array or Matrix
        "ATTR",     # Attribute: If Attribute is set the argument will be an attribute of the subprogram call, otherwise it will be an input port. [for input argument]
        "INIT"      # Initial Value: Initial value for the variable for the segment call corresponding to this output argument [for output argument in a segment submodel]
    ]

    def __init__(self, parent, type="", objectId=""):
        SimulationEntity.__init__(self, parent, type, objectId)

        self._lastArgName = ""
        self._parseEsl = ParseEsl()

    def argName(self):
        argName = self._attributes["ARG"].valueStr()
        return argName
    def set_argName(self, argName):
        self._attributes["ARG"].set_valueStr(argName)
    def argDescription(self):
        argDescription = self._attributes["ARGDESC"].valueStr()
        return argDescription
    def set_argDescription(self, argDescription):
        self._attributes["ARGDESC"].set_valueStr(argDescription)
    def argDimensions(self):
        argDimensions = self._attributes["ARGDIMS"].valueStr()
        return argDimensions
    def set_argDimensions(self, argDimensions):
        self._attributes["ARGDIMS"].set_valueStr(argDimensions)
    def isAttribute(self):
        isAttribute = False
        attribute = self._attributes.get("ATTR")
        if attribute:
            attributeValue = attribute.valueStr()
            isAttribute = attributeValue.lower() == "true"
        return isAttribute
    def set_isAttribute(self, isAttribute):
        attribute = self._attributes.get("ATTR")
        if attribute:
            attributeValue = "true" if isAttribute else "false"
            attribute.set_valueStr(attributeValue)
    def initialValueESLValue(self):
        eslValue = None
        attribute = self._attributes.get("INIT")
        if attribute:
            eslValue = attribute.eslValue()
        return eslValue
    def getInitialisationValue(self):
        initialValue = ""
        attribute = self._attributes.get("INIT")
        if attribute:
            initialValue = attribute.getInitialisationValue()
        return initialValue

    def defaultArgName(self):
        argName = self.makeEslName("")
        return argName

    def getArgName(self):
        argName = self.argName()
        if not argName:
            argName = self.defaultArgName()
        return argName

    def getLastArgName(self):
        return self._lastArgName

    def getArgPort(self):   # Is overridden in Input/OutputArgument
        argPort = None
        return argPort

    def getPortInfoData(self, allowBlankTag=False):  # [datatype, description, tag, dimensions]
        portInfo = None
        argPort = self.getArgPort()
        if argPort is not None:
            datatype = argPort.datatype()
            description = ''
            attribute = self.attributes().get('ARGDESC')
            if attribute: description = attribute.valueStr()
            if allowBlankTag:
                tag = self.argName()
            else:
                tag = self.getArgName()  # returns the default value if argName not specified
            dimensions = ""
            attribute = self.attributes().get('ARGDIMS')
            if attribute: dimensions = attribute.valueStr()
            portInfo = [datatype, description, tag, dimensions]
        return portInfo

    def getDatatypeAndDimensions(self):
        datatype = None
        dimensions = ""
        argPort = self.getArgPort()
        if argPort is not None:
            datatype = argPort.datatype()
            if datatype:
                attribute = self.attributes().get('ARGDIMS')
                if attribute:
                    dimensions = attribute.valueStr()
                    if dimensions:
                        dimensions = "(" + dimensions + ")"
        return datatype, dimensions

    def loadAttributes(self, entityDescrXmlElement, suppressAddName=False):  # Special attributes created when the argument is created.
        attXmlList = entityDescrXmlElement.getXmlElementListByName("attribute", False)
        for attXmlElement in attXmlList:
            tempatt = Attribute(self)
            tempatt.clearAssignables()
            tempatt.load(attXmlElement, suppressAddName=suppressAddName, suppressSetDefaultsForDatatype=True)
            atttag = tempatt.tag()
            if self._application.compatibility() == 1: # Old-style attribute tags (TAG & DESCRIPTION) changed.
                if atttag == "TAG":
                    atttag = ArgumentEntity.SpecialAttributeTags[0] # ARG
                elif atttag == "DESCRIPTION":
                    atttag = ArgumentEntity.SpecialAttributeTags[1] # ARGDESC
            if atttag and atttag in self._attributes:
                att = self._attributes[atttag]
                att.copyAssignables(tempatt)

    def load(self, entityDescrXmlElement, suppressAddName=False):
        super(ArgumentEntity, self).load(entityDescrXmlElement, suppressAddName)
        # Add Arg Name (including if default) to this argument's module's block-names (i.e. scope).
        argName = self.getArgName()
        if argName:
            module = self.parent().parent()
            if module:
                module.blockNames().add(argName, self)
        # If has INIT attribute its ESLValue dimensions according to as specified in ARGDIMS.
        initAttribute = self._attributes.get("INIT")
        if initAttribute:
            dimensions = self.argDimensions()
            initAttribute.set_dimensions(dimensions)
        # Arg port should have been set by now from original definition (without dimensions) - see if should be updated.
        portsXmlElement = entityDescrXmlElement.getXmlElementByName("port")
        if portsXmlElement:
            argPort = self.getArgPort()
            if argPort is not None:
                dimensions = portsXmlElement.getAttribute("dimensions")
                if dimensions:
                    argPort.set_dimensions(dimensions)
                    # Update the diagram entity port datatype
                    newEntityObjectId = ""
                    if self._parent.oldToNewObjectIds():
                        newEntityObjectId = self._parent.oldToNewObjectIds().get(self.objectId())
                    actionStr = dgAction.makeUpdateEntityPortActionStr(self, argPort, newEntityObjectId)
                    dgAction.sendDiagramUpdate(self._parent, actionStr, applicationDataType="",
                                               applicationDataContents="", secondary=False, raiseEvent=False)
                    self._parent.canvas().Refresh()

    # def specialSaveXmlAttributes(self, indent=None, level=0, saveDefaults=False):

    # def specialSaveXmlContents(self, indent=None, level=0, saveDefaults=False):

    # def updateEntity(self, updateXmlElement): # No property update (at this level)

    # def validateEntityPropertyChange(self, propertyTag, newValue, val_type, val_item):

    # def updateEntityProperty(self, propertyTag, newValue, suppress_action=False):

    def validateEntityAttributePropertyChange(self, propertyTag, newValue, attribute, val_type, val_item, val_oldValue, val_newValue
        ) -> (bool, str, str, str, str, str, str):         # Override this in any special types of simulation entity that have entity properties that need validating.
        """ returns: valid:bool, rejection:str, val_type:str, val_item:str, val_oldValue:str, val_newValue:str, updatedPropertyValue:str """
        valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue = super(ArgumentEntity, self).validateEntityAttributePropertyChange(
            propertyTag, newValue, attribute, val_type, val_item, val_oldValue, val_newValue)
        if valid:
            dummyAttribute = attribute.detachedCopy(attribute.parent())
            dummyAttribute.loadData(newValue, suppressAddName=True)
            newValueStr = dummyAttribute.valueStr()
            oldValueStr = attribute.valueStr()
            module = None
            isForSegment = False
            if isinstance(self.parent(), DiagramInfo):
                module = self.parent().parent()
                isForSegment = module.moduleType() in CALLABLEMODULETYPES and module.callableType() == 'segment'
            if propertyTag == 'ARG':
                val_item = "Arg Name"
                if newValueStr != oldValueStr and newValueStr != "":
                    errTxt = esl.ValidateName(newValueStr, silent=True)
                    if errTxt:
                        rejection = 'not a valid ESL name - ' + errTxt
                        valid = False
                    elif module.eslnameIsInModule(newValueStr):
                        rejection = 'name is already in use in ' + module.identification()
                        valid = False
                    # Validate that is unique in module to 18 chars.
                    elif not module.blockNames().isUniqueToLength(newValueStr, 18):
                        rejection = "name is not unique in 18 characters in " + module.identification()
                        valid = False
            # elif propertyTag == 'ARGDESC': always valid
            elif propertyTag == 'ARGDIMS':
                val_item = "Dimensions"
                if newValueStr != oldValueStr:
                    diagramInfo = self._parent
                    dimensionality = None
                    argPort = self.getArgPort()
                    if argPort is not None:
                        portsConnections = diagramInfo.canvas().EstablishPortsConnections(self.objectId())
                        argPortConnected = False
                        portId = str(self.objectId())+PortConnectorSeparator+str(argPort.id())
                        for pair in portsConnections:
                            if pair[0] == portId:
                                argPortConnected = True if len(pair[1]) else False
                                break
                        if argPortConnected:
                            rejection = "cannot change the dimensions of an argument while it is connected to something in its diagram ("+module.identification()+")"
                            valid = False
                    else:
                        raise Exception("Cannot find argument port for argument entity "+self.identification())
                    if valid:
                        # Validate dimensions via parseDimensions
                        dimensionsText = newValueStr.strip()
                        if dimensionsText and dimensionsText[0] == "(":
                            if dimensionsText[-1] == ")":
                                dimensionsText = dimensionsText[1:-1].strip()
                            else:
                                rejection = "dimensions should not be in mis-matched brackets"
                                valid = False
                        if valid:
                            allowStar = True if module.moduleType() in CALLABLEMODULETYPES and module.callableType() == 'submodel' else False
                            pos, dimensionality = self._parseEsl.parseDimensions(dimensionsText, 0, None, checkNothingLeft=True, allowStar=allowStar)
                            if dimensionality is not None:
                                for parseMessage in dimensionality.messages:
                                    dimMsg = parseMessage.message + " "
                                    if dimMsg:
                                        rejection += dimMsg
                                        valid = False
                        if valid and dimensionality is not None:
                            updatedValueStr = dimensionality.dimensions() # standard form for dimensions
                            if updatedValueStr != dummyAttribute.valueStr():
                                dummyAttribute.set_valueStr(updatedValueStr)
                            updatedPropertyValue = dummyAttribute.save(saveDefaults=True)

            # elif propertyTag == 'ATTR': always valid
            elif propertyTag == 'INIT':   # If for Segment, validate Output Argument's Initial Value (given datatype & dimensions)
                if isForSegment:
                    val_item = "Initial Value"
                    newValueSaveStr = dummyAttribute.eslValue().saveStr()
                    oldValueSaveStr = attribute.eslValue().saveStr()
                    if newValueSaveStr != oldValueSaveStr:
                        initAttribute = self._attributes.get("INIT")
                        if initAttribute:
                            dummyESLValue = initAttribute.eslValue().detachedCopy(None)
                            dummyESLValue.loadStr(newValueSaveStr, checkValidity=False)
                            valid, rejection, val_type, val_item, updatedESLValue = initAttribute.eslValue().validateESLValuePropertyChange(
                                dummyESLValue, val_type, val_item)
                            if valid:
                                if updatedESLValue is not None:
                                    updatedValue = updatedESLValue.saveStr()
                                    if updatedValue != dummyAttribute.eslValue().saveStr():
                                        dummyAttribute.eslValue().loadStr(updatedValue, checkValidity=False)
                                    updatedPropertyValue = dummyAttribute.save(saveDefaults=True)
                    pass
            if rejection:
                val_oldValue = attribute.shortAttributeValueText(showName=True, showValue=True)
                val_newValue = dummyAttribute.shortAttributeValueText(showName=True, showValue=True)

        return valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue

    def updateEntityAttributeProperty(self, propertyTag, newValue, attribute, tempOldAttribute, suppress_action=False) -> bool: # Override this (and incorporate it) in any special types of simulation entity that have attribute properties.
        updateEntityPropertiesView = super(ArgumentEntity, self).updateEntityAttributeProperty(propertyTag, newValue, attribute, tempOldAttribute, suppress_action)
        newValueStr = attribute.valueStr()
        oldValueStr = tempOldAttribute.valueStr()
        module = None
        isForSegment = False
        if isinstance(self.parent(), DiagramInfo):
            module = self.parent().parent()
            isForSegment = module.moduleType() in CALLABLEMODULETYPES and module.callableType() == 'segment'
        if propertyTag == 'ARG':
            deleteArgName = oldValueStr
            if not oldValueStr:
                deleteArgName = self.defaultArgName()
            addArgName = newValueStr
            if newValueStr == self.defaultArgName():
                newValueStr = ""
            if not newValueStr:
                addArgName = self.defaultArgName()
            if module and newValueStr != oldValueStr:
                if deleteArgName:
                    module.blockNames().delete(deleteArgName)
                if addArgName:
                    module.blockNames().add(addArgName, self)
                self._lastArgName = oldValueStr # Record old (replaced) ArgName
            if newValueStr == "":
                updateEntityPropertiesView = True
        elif propertyTag == 'ARGDIMS':
            argPort = self.getArgPort()
            if argPort is not None:
                # Dimensions newValue is now standard form
                argPort.set_dimensions(newValueStr)
                # If has INIT property (for Output Argument) - if for Segment, set its dimensions too - check if INIT's value still valid if not mark it invalid.
                if isForSegment:
                    initAttribute = self._attributes.get("INIT")
                    if initAttribute:
                        initAttribute.set_dimensions(newValueStr)
                        initAttribute.eslValue().checkValidity()
                        updateEntityPropertiesView = True

                # Update the diagram entity port datatype
                actionStr = dgAction.makeUpdateEntityPortActionStr(self, argPort)
                dgAction.sendDiagramUpdate(self._parent, actionStr, applicationDataType="",
                                           applicationDataContents="", secondary=False, raiseEvent=False)
                self._parent.canvas().Refresh()

        if propertyTag in ["ARG", "ARGDIMS", "ATTR"]:
            moduleId = module.moduleId()
            self._application.onArgumentsChanged(moduleId, suppress_action=suppress_action)

        return updateEntityPropertiesView

    def makeUpdateEntityPropertyAnnotationsActionStr(self):
        updateActionStr = ""
        for tag, attribute in self._attributes.items():
            annotationId, annotationTxt, annotationVisible = dgAction.setEntityAttributeAnnotations(attribute)
            replaceId = ""
            if self._application.compatibility() == 1:
                if tag == "ARG":
                    replaceId = "attribute-TAG"
                elif tag == "ARGDESC":
                    replaceId = "attribute-DESCRIPTION"
            updateActionStr += dgAction.makeUpdateAnnotationActionStr("attribute-"+tag, annotationTxt, annotationVisible, replaceId)
        return updateActionStr
