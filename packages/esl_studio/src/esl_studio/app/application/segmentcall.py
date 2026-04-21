#! /usr/bin/python

from collections import OrderedDict

from .callentity import CallEntity
from .eslvalue import ESLValue
from .segment import Segment
from .codesubprogram import CodeSubprogram
from .attribute import Attribute
from . import diagramactions as dgAction

class SegmentCall(CallEntity):

    # Note: Makes use of special attributes (overriding any that may be set in the entity definitions)
    SpecialAttributeTags = [
        "frequency",    # Frequency of calls.
        "delay"         # Time delay for first call.
    ]
    SpecialAttributeDescriptions = ["Frequency of calls", "Time delay"]
    SpecialAttributeDatatypes = ["Integer", "Real"]

    Frequency_default = '1'
    Delay_default = '0.0'

    def __init__(self, parent, type="", objectId=""):
        CallEntity.__init__(self, parent, type, objectId)

        # Special properties (these are special Attributes)
        definedAttributesDict = {}
        if self._application:
            definedAttributesDict = self._application.frame().control().entities().getAttributesDict(type)

        tag = SegmentCall.SpecialAttributeTags[0] # Frequency
        description = SegmentCall.SpecialAttributeDescriptions[0]
        definedAttribute = definedAttributesDict.get(tag)
        if definedAttribute and definedAttribute.description():
            description = definedAttribute.description()
        datatype = SegmentCall.SpecialAttributeDatatypes[0]
        self._frequencyAttribute = Attribute(self, tag, description, datatype=datatype)
        self._frequencyAttribute.set_is_special("true")
        self._frequencyAttribute.set_default_value(SegmentCall.Frequency_default)
        self._attributes[tag] = self._frequencyAttribute

        tag = SegmentCall.SpecialAttributeTags[1] # Delay
        description = SegmentCall.SpecialAttributeDescriptions[1]
        definedAttribute = definedAttributesDict.get(tag)
        if definedAttribute and definedAttribute.description():
            description = definedAttribute.description()
        datatype = SegmentCall.SpecialAttributeDatatypes[1]
        self._delayAttribute = Attribute(self, tag, description, datatype=datatype)
        self._delayAttribute.set_is_special("true")
        self._delayAttribute.set_default_value(SegmentCall.Delay_default)

        self._frequencyAttribute.set_show_valueOnTop("true")
        self._frequencyAttribute.set_has_eslname("false")
        self._frequencyAttribute.set_has_sources("")
        self._frequencyAttribute.set_has_annotations("true")
        self._frequencyAttribute.set_hide_datatype("false")
        self._delayAttribute.set_show_valueOnTop("true")
        self._delayAttribute.set_has_eslname("false")
        self._delayAttribute.set_has_sources("")
        self._delayAttribute.set_has_annotations("true")
        self._delayAttribute.set_hide_datatype("false")

        self._attributes[SegmentCall.SpecialAttributeTags[0]] = self._frequencyAttribute
        self._attributes[SegmentCall.SpecialAttributeTags[1]] = self._delayAttribute

    def frequencyAttribute(self):
        return self._frequencyAttribute
    def set_frequencyAttribute(self, frequencyXmlStr):
        frequencyAttribute = self.frequencyAttribute()
        frequencyAttribute.loadData(frequencyXmlStr, suppressAddName=True)
    def set_frequency_value(self, val, source):
        if source is None or source == "":
            source = Attribute.SourceValue
        if source == Attribute.SourceValue and (val is None or val == ""):
            val = ESLValue.DefaultEslValueSaveStr
        frequencyAttribute = self.frequencyAttribute()
        frequencyAttribute.eslValue().loadStr(val, checkValidity=False)
        frequencyAttribute.set_source(source)

    def delayAttribute(self):
        return self._delayAttribute
    def set_delayAttribute(self, delayXmlStr):
        delayAttribute = self.delayAttribute()
        delayAttribute.loadData(delayXmlStr, suppressAddName=True)
    def set_delay_value(self, val, source):
        if source is None or source == "":
            source = Attribute.SourceValue
        if source == Attribute.SourceValue and (val is None or val == ""):
            val = ESLValue.DefaultEslValueSaveStr
        delayAttribute = self.delayAttribute()
        delayAttribute.eslValue().loadStr(val, checkValidity=False)
        delayAttribute.set_source(source)

    def copyFrom(self, anotherSegmentCall, parent):
        super(SegmentCall, self).copyFrom(anotherSegmentCall, parent)

    def load(self, entityDescrXmlElement, suppressAddName=False):
        super(SegmentCall, self).load(entityDescrXmlElement, suppressAddName)
        val = entityDescrXmlElement.getAttribute("segment")
        if val is not None:
            self._subprogramName = val
        val = entityDescrXmlElement.getAttribute("frequency")
        source = entityDescrXmlElement.getAttribute("frequency-source")
        self.set_frequency_value(val, source)
        annotationState = entityDescrXmlElement.getAttribute("frequency-annotations")
        self.loadAnnotationState(self.frequencyAttribute(), annotationState)
        val = entityDescrXmlElement.getAttribute("delay")
        source = entityDescrXmlElement.getAttribute("delay-source")
        self.set_delay_value(val, source)
        annotationState = entityDescrXmlElement.getAttribute("delay-annotations")
        self.loadAnnotationState(self.delayAttribute(), annotationState)

    def loadAnnotationState(self, attribute, annotationState):
        annotationStateSplit = []
        if annotationState: annotationStateSplit = annotationState.split("|")
        attribute.set_show_description("true" if "name" in annotationStateSplit else "false")
        attribute.set_show_tag("true" if "tag" in annotationStateSplit else "false")
        attribute.set_show_eslname("true" if "eslname" in annotationStateSplit else "false") # for completeness though currently wont happen
        attribute.set_show_source("true" if "source" in annotationStateSplit else "false")
        attribute.set_show_value("true" if "value" in annotationStateSplit else "false")

    def specialSaveXmlAttributes(self, indent=None, level=0, saveDefaults=False):
        xmlAttributeText = super(SegmentCall, self).specialSaveXmlAttributes(indent, level, saveDefaults)
        subprogram = self.subprogram()
        if subprogram or saveDefaults:
            subprogramName = ''
            if subprogram:
                subprogramName = subprogram.eslname()
            xmlAttributeText += ' segment="' + subprogramName + '"'
        frequencyAttribute = self.frequencyAttribute()
        val = str(frequencyAttribute.eslValue().saveStr())
        source = frequencyAttribute.source()
        if saveDefaults or source != Attribute.SourceValue or (val != "" and val != str(SegmentCall.Frequency_default)):
            xmlAttributeText += ' frequency="' + str(val) + '"'
        if source != Attribute.SourceValue or saveDefaults:
            xmlAttributeText += ' frequency-source="' + source + '"'
        annotationText = self.saveAnnotationStateText(frequencyAttribute)
        if saveDefaults or annotationText:
            xmlAttributeText += ' frequency-annotations="'+ annotationText + '"'
        delayAttribute = self.delayAttribute()
        val = str(delayAttribute.eslValue().saveStr())
        source = delayAttribute.source()
        if saveDefaults or source != Attribute.SourceValue or (val != "" and val != str(SegmentCall.Delay_default)):
            xmlAttributeText += ' delay="' + str(val) + '"'
        if source != Attribute.SourceValue or saveDefaults:
            xmlAttributeText += ' delay-source="' + source + '"'
        annotationText = self.saveAnnotationStateText(delayAttribute)
        if saveDefaults or annotationText:
            xmlAttributeText += ' delay-annotations="'+ annotationText + '"'
        return xmlAttributeText

    def saveAnnotationStateText(self, attribute):
        annotationStateList = []
        if attribute.show_description() == "true": annotationStateList.append("name")
        if attribute.show_tag() == "true": annotationStateList.append("tag")
        if attribute.show_eslname() == "true": annotationStateList.append("eslname")
        if attribute.show_source() == "true": annotationStateList.append("source")
        if attribute.show_value() == "true": annotationStateList.append("value")
        annotationState = "|".join(annotationStateList)
        return annotationState

    #def specialSaveXmlContents(self, indent=None, level=0, saveDefaults=False):  : # Has no contents.

    def checkValidToLoad(self): #valid, msg
        valid = True
        msg = ""
        subprogram = self._subprogram
        if subprogram:
            isPreloaded = subprogram.application() is None
            if not subprogram.valid():
                msg = 'Cannot create segment call as '
                if isPreloaded: msg += 'preloaded '
                msg += 'segment is not valid\n'
                self.unlinkSubprogramCallWithSubprogram()
                valid = False

            if isPreloaded and subprogram.hasSubprogramCalls():
                if self._parent.application().blockNames().isin(subprogram.eslname()):
                    msg = 'Cannot create segment call for preloaded segment as segment name "'+\
                        subprogram.eslname()+'" is already being used\n'
                    self.unlinkSubprogramCallWithSubprogram()
                    valid = False
        return valid, msg

    def setupSubprogramCallPortsNAtts(self, matchPortsById=False):
        # Preserve special attributes.
        removedSpecials = False
        for tag in SegmentCall.SpecialAttributeTags:    # Remove them from setupSubprogramCall consideration
            if tag in self._attributes:
                removedSpecials = True
                del self._attributes[tag]
        commonPortIdAnnotationPairDict, obsoletePortIdToAnnotationIdDict, commonAttributeTagAnnotationPairDict, obsoleteAttributeTagToAnnotationIdDict = \
            super(SegmentCall, self).setupSubprogramCallPortsNAtts(matchPortsById)
        # Restore special attributes
        if removedSpecials:
            for tag in SegmentCall.SpecialAttributeTags:
                if tag == "frequency":
                    self._attributes[tag] = self.frequencyAttribute()
                elif tag == "delay":
                    self._attributes[tag] = self.delayAttribute()
        return commonPortIdAnnotationPairDict, obsoletePortIdToAnnotationIdDict, commonAttributeTagAnnotationPairDict, obsoleteAttributeTagToAnnotationIdDict

    def updateEntity(self, updateXmlElement):
        val = updateXmlElement.getAttribute("segment")
        if val:
            subprogram = self._application.getSegmentByName(val) # Should be valid (comes after paste or redo)
            currentSubprogram = self.subprogram()
            if subprogram is not None and subprogram != currentSubprogram:
                self.linkSubprogramCallWithSubprogram(subprogram)
                self._ports = subprogram.getPorts()
                for port in list(self._ports.values()): port.set_parent(self)
                self._attributes = self._subprogram.getAttributes()
                for attribute in list(self._attributes.values()): attribute.set_parent(self)
        val = updateXmlElement.getAttribute("show-subprogram")
        if val is not None:
            self._show_subprogram = val
        val = updateXmlElement.getAttribute("frequency")
        source = updateXmlElement.getAttribute("frequency-source")
        self.set_frequency_value(val, source)
        val = updateXmlElement.getAttribute("delay")
        source = updateXmlElement.getAttribute("delay-source")
        self.set_delay_value(val, source)
        super(SegmentCall, self).updateEntity(updateXmlElement)

    def validateEntityPropertyChange(self, propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue):
        valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue = \
            super(SegmentCall, self).validateEntityPropertyChange(propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue)
        if valid:
            if propertyTag == 'segment':
                val_item = "Segment"
                if newValue != '':
                    subName = newValue
                    if newValue[-1] == "*":
                        subName = subName[:-1]
                    subprogram = self._application.blockNames().get(subName)
                    if subprogram is None:
                        valid = False
                        rejection = 'no subprogram of that name in the application'
                    elif subprogram.subprogramBaseType() == "code" and subprogram.callableType() != "segment":
                        valid = False
                        rejection = 'application subprogram of that name is not a segment'
                    elif subprogram.subprogramBaseType() == "diagram" and subprogram.moduleType() != "segment":
                        valid = False
                        rejection = 'application subprogram with that name is not a segment'
                    elif not subprogram.valid():
                        valid = False
                        rejection = 'segment is invalid'
                    elif newValue[-1] == "*":
                        valid = False
                        rejection = 'segment is marked invalid'
        if valid:
            attribute = None
            if propertyTag == 'frequency' or propertyTag == 'frequency'+Attribute.ValueEnumRefExtn:
                attribute = self.frequencyAttribute()
            elif propertyTag == 'delay' or propertyTag == 'delay'+Attribute.ValueEnumRefExtn:
                attribute = self.delayAttribute()
            if attribute:
                val_item = propertyTag.title()
                dummyAttribute = attribute.detachedCopy(attribute.parent())
                dummyAttribute.loadData(newValue, suppressAddName=True)
                # Note: Source change is always valid (ESLValue may be holding a string for a variable)
                if attribute.source() != dummyAttribute.source():
                    if dummyAttribute.source() == Attribute.SourceValue:
                        pass
                else:
                    if dummyAttribute.source() == Attribute.SourceValue and attribute.eslValue().saveStr() != dummyAttribute.eslValue().saveStr():
                        val_item += ".Value"
                        valid, rejection, val_type, val_item, updatedESLValue = attribute.eslValue().validateESLValuePropertyChange(
                            dummyAttribute.eslValue(), val_type, val_item)
                        if valid:
                            if updatedESLValue is not None:
                                updatedValue = updatedESLValue.saveStr()
                                if updatedValue != dummyAttribute.eslValue().saveStr():
                                    dummyAttribute.eslValue().loadStr(updatedValue, checkValidity=False)
                                updatedPropertyValue = dummyAttribute.save(saveDefaults=True)
                        if rejection:
                            val_oldValue = attribute.shortAttributeValueText(showName=True, showValue=True)
                            val_newValue = dummyAttribute.shortAttributeValueText(showName=True, showValue=True)
        return valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue

    def updateEntityProperty(self, propertyTag, newValue, suppress_action=False):
        refreshProperty = super(SegmentCall, self).updateEntityProperty(propertyTag, newValue, suppress_action=suppress_action)
        if propertyTag == 'segment':
            self.doSubprogramCallSubprogramPropertyChange(newValue, suppress_action=suppress_action)
            refreshProperty = True
        elif propertyTag == 'annotations':
            if 'Segment' in newValue:
                self.set_show_subprogram("true")
            else:
                self.set_show_subprogram("false")
        else:
            attribute = None
            if propertyTag == 'frequency' or propertyTag == 'frequency'+Attribute.ValueEnumRefExtn:
                self.set_frequencyAttribute(newValue)
                attribute = self.frequencyAttribute()
            elif propertyTag == 'delay' or propertyTag == 'delay'+Attribute.ValueEnumRefExtn:
                self.set_delayAttribute(newValue)
                attribute = self.delayAttribute()
            if attribute is not None:
                annotationId, annotationTxt, annotationVisible = dgAction.setEntityAttributeAnnotations(attribute)
                dgAction.sendAnnotationUpdate(self, annotationId, annotationTxt, annotationVisible)
                refreshProperty = True
        return refreshProperty

    # def validateEntityAttributePropertyChange(self, propertyTag, newValue, attribute, tempNewAttribute, val_type, val_item, val_oldValue, val_newValue): # No attribute property validation

    # def updateEntityAttributeProperty(self, propertyTag, newValue, attribute, tempOldAttribute, suppress_action=False): # No attribute property update

    def getAttribute(self, attributeTag):
        if attributeTag == 'frequency':
            attribute = self.frequencyAttribute()
        elif attributeTag == 'delay':
            attribute = self.delayAttribute()
        else:
            attribute = super(SegmentCall, self).getAttribute(attributeTag)
        return attribute
