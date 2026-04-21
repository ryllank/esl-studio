#! /usr/bin/python

import esl_diagram.xmlutil as xut

from .. import utils as Utils
from . import diagramactions as dgAction
from ..esl import esl
from ..esl.parseesl import ParseEsl, DimensionalityParseObject
from .eslvalue import ESLValue, multipleComponentPattern

class Variable(object):
    def __init__(self, parent, eslname="", description="", constant="false", parameter="false",
                 datatype="", dimensions="", valueStr=""):
        self._parent = parent
        self._eslname = eslname
        self._description = description
        self._constant = constant
        self._parameter = parameter
        self._eslValue = ESLValue(self, datatype, dimensions, valueStr)

        self._assignedAttributes = []
        self._variableId = 0

    def detachedCopy(self, parent):
        """ Copies from self to make a new Variable with a new parent (may be None) """
        newVar = Variable(parent)
        newVar.copyFrom(self, parent)
        return newVar

    def copyFrom(self, otherVariable, parent):
        """ Copies from otherVariable into the self except for parent which it updates (may set it None) """
        self._parent = parent
        self._eslname = otherVariable._eslname
        self._description = otherVariable._description
        self._constant = otherVariable._constant
        self._parameter = otherVariable._parameter
        self._eslValue.copyFrom(otherVariable._eslValue, self)

    def parent(self): return self._parent
    def eslname(self): return self._eslname
    def description(self): return self._description
    def constant(self): return self._constant
    def parameter(self): return self._parameter
    def datatype(self):
        return self._eslValue.datatype()
    def dimensions(self):
        return self._eslValue.dimensions()
    def valueStr(self):
        return self._eslValue.valueStr()
    def eslValue(self):
        return self._eslValue
    def defaultValueStr(self):
        return self._eslValue.defaultValueStr()
    def getInitialisationValue(self, useDefaultValue:bool=True, generateDefaultValue:bool=False) -> str:
        return self._eslValue.getInitialisationValue(useDefaultValue, generateDefaultValue)

    def assignedAttributes(self): return self._assignedAttributes

    def set_eslname(self, eslname): self._eslname = eslname
    def set_description(self, description): self._description = description
    def set_constant(self, constant): self._constant = constant
    def set_parameter(self, parameter): self._parameter = parameter
    def set_datatype(self, datatype): self._eslValue.set_datatype(datatype)
    def set_dimensions(self, dimensions): self._eslValue.set_dimensions(dimensions)
    def set_valueStr(self, valueStr):
        self._eslValue.set_valueStr(valueStr)

    def variableId(self): return  self._variableId
    def set_variableId(self, variableId):
        self._variableId = variableId

    def load(self, varXmlElement, suppressAddName=False):
        val = varXmlElement.getAttribute("type")
        if val is not None:
            self._eslValue.set_datatype(val)
        val = varXmlElement.getAttribute("eslname")
        if val is not None: self._eslname = val
        val = varXmlElement.getAttribute("description")
        if val is not None: self._description = val
        val = varXmlElement.getAttribute("constant")
        if val is not None: self._constant = val
        val = varXmlElement.getAttribute("parameter")
        if val is not None: self._parameter = val
        val = varXmlElement.getAttribute("dimensions")
        if val is not None:
            self._eslValue.set_dimensions(val)
        val = varXmlElement.getAttribute("value")
        if val is not None:
            self._eslValue.loadStr(val)

    def loadData(self, data, suppressAddName=False):
        xmlElement = xut.xmlElement(data)
        if xmlElement:
            self.load(xmlElement, suppressAddName)

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ind + '<variable eslname="' + self._eslname + '" type="' + str(self.datatype()) + '"'
        if self._description or saveDefaults:
            result += ' description="' + xut.entitise(self._description) + '"'
        if self._constant and self._constant == "true":
            result += ' constant="true"'
        elif saveDefaults:
            result += ' constant="false"'
        if self._parameter and self._parameter == "true":
            result += ' parameter="true"'
        elif saveDefaults:
            result += ' parameter="false"'
        if self.dimensions() or saveDefaults:
            result += ' dimensions="' + self.dimensions() + '"'
        eslValueSaveStr = self._eslValue.saveStr()
        if eslValueSaveStr != ESLValue.DefaultEslValueSaveStr or saveDefaults:
            result += ' value="' + xut.entitise(eslValueSaveStr) + '"'
        result += '/>' + nl
        return result

    def get_element_indices_for_reference(self, reference, ownDimensionality) -> list[int]:
        indices = []
        refDimensionality = ParseEsl.get_dimensionality(reference, parseReference=True)
        refBounds = refDimensionality.bounds()
        ownNumber = ownDimensionality.number()
        ownSizes = ownDimensionality.sizes()
        ownBounds = ownDimensionality.bounds()
        iCoords = []
        jCoords = []
        kCoords = []
        if ownNumber >= 1:
            dim = 0
            if refBounds[dim][0] == DimensionalityParseObject.ReferenceUnsliced:
                iCoord = refBounds[dim][1] - ownBounds[dim][0]
                iCoords.append(iCoord)
            else:
                for ixRef in range(refBounds[dim][0], refBounds[dim][1]+1):
                    iCoord = ixRef - ownBounds[dim][0]
                    iCoords.append(iCoord)
        if ownNumber >= 2:
            dim = 1
            if refBounds[dim][0] == DimensionalityParseObject.ReferenceUnsliced:
                jCoord = refBounds[dim][1] - ownBounds[dim][0]
                jCoords.append(jCoord)
            else:
                for ixRef in range(refBounds[dim][0], refBounds[dim][1]+1):
                    jCoord = ixRef - ownBounds[dim][0]
                    jCoords.append(jCoord)
        if ownNumber == 3:
            dim = 2
            if refBounds[dim][0] == DimensionalityParseObject.ReferenceUnsliced:
                kCoord = refBounds[dim][1] - ownBounds[dim][0]
                kCoords.append(kCoord)
            else:
                for ixRef in range(refBounds[dim][0], refBounds[dim][1]+1):
                    kCoord = ixRef - ownBounds[dim][0]
                    kCoords.append(kCoord)
        if ownNumber == 1:
            for iCoord in iCoords:
                index = iCoord
                indices.append(index)
        if ownNumber == 2:
            for iCoord in iCoords:
                for jCoord in jCoords:
                    index = jCoord + iCoord * ownSizes[0]
                    indices.append(index)
        if ownNumber == 3:
            for iCoord in iCoords:
                for jCoord in jCoords:
                    for kCoord in kCoords:
                        index = kCoord + (jCoord + iCoord * ownSizes[0]) * ownSizes[1]
                        indices.append(index)
        return indices

    def get_expanded_value(self, ownDimensionality) -> list[str]:
        expansion = []
        initialValueStr = self.valueStr().strip()
        if not initialValueStr:
            initialValueStr = self.defaultValueStr().strip()
        if initialValueStr:
            orderChar = ""
            if initialValueStr[0] == "/" and initialValueStr[-1] == "/":
                orderChar = "/" # column-major specified < will transpose to row-major default (if 2 or 3D)
            if initialValueStr[0] == "[" and initialValueStr[-1] == "]":
                orderChar = "[" # row-major specfied
            if orderChar:
                initialValueStr = initialValueStr[1:-1].strip()
            if initialValueStr:
                components = list(map(lambda it: it.strip(), initialValueStr.split(",")))
                for component in components:
                    match = multipleComponentPattern.match(component)
                    if match:
                        multiple = int(match[1])
                        element = component[match.end():]
                        expansion.extend([element]*multiple)
                    else:
                        expansion.append(component)
            if orderChar == "/": # column-major specified
                ownNumber = ownDimensionality.number()
                if ownNumber > 1: # 2D & 3D matrices have to be transposed (to put elements given into row-major sequence)
                    sizes = ownDimensionality.sizes()
                    count = 0
                    ix = 0
                    transposed = expansion.copy()
                    expansion = [0]*len(transposed)
                    if ownNumber == 3:
                        for k in range(sizes[2]):
                            for j in range(sizes[1]):
                                for i in range(sizes[0]):
                                    ix = (i * sizes[0] + j) * sizes[1] + k
                                    expansion[ix] = transposed[count]
                                    count += 1
                    elif ownNumber == 2:
                        for j in range(sizes[1]):
                            for i in range(sizes[0]):
                                ix = i * sizes[0] + j
                                expansion[ix] = transposed[count]
                                count += 1
        return expansion

    def extract_referenced_value(self, expandedVariableValue:list[str], referencedIndices:list[int]) -> list[str]:
        referencedValue = []
        for index in referencedIndices:
            referencedValue.append(expandedVariableValue[index])
        return referencedValue

    def condense_referenced_value(self, referencedValue:list[str]) -> list[str]:
        condensedReferenceValue = []
        lastValue = ""
        multiple = 1
        for ix in range(len(referencedValue)):
            value = referencedValue[ix]
            if lastValue:
                if value != lastValue:
                    if multiple > 1:
                        condensedReferenceValue.append(str(multiple)+"*"+lastValue)
                    else:
                        condensedReferenceValue.append(lastValue)
                    multiple = 1
                else:
                    multiple += 1
            lastValue = value
        if lastValue:
            if multiple > 1:
                condensedReferenceValue.append(str(multiple)+"*"+lastValue)
            else:
                condensedReferenceValue.append(lastValue)
        return condensedReferenceValue

    def get_reference_value(self, reference):
        ownDimensionality = ParseEsl.get_dimensionality(self.dimensions())
        referencedIndices = self.get_element_indices_for_reference(reference, ownDimensionality)
        expandedVariableValue = self.get_expanded_value(ownDimensionality)
        referencedValue = self.extract_referenced_value(expandedVariableValue, referencedIndices)
        if len(referencedValue) == 1:
            value = referencedValue[0]
        else:
            referencedValue = self.condense_referenced_value(referencedValue) # condense back to star-style when have multiple (repeated) values in the (flat) list
            value = "[" + ",".join(referencedValue) + "]"
        return value

    def shortVariableValueText(self, showValue=False):
        val_text = "<variable name=\""+self._eslname+"\""
        val_text += " type=\""+self.datatype()
        dimensions = self.dimensions()
        if dimensions:
            val_text += "("+dimensions+")"
        val_text += "\""
        if showValue and self._eslValue.saveStr() != ESLValue.DefaultEslValueSaveStr:
            val_text += " value("+self._eslValue.mode()+")=\""+self._eslValue.valueStr()+"\""
        val_text += ">"
        return val_text

    def validateVariablePropertyChange(self, module, propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue) -> (bool, str, str, str, str, str, str):
        """ returns: valid:bool, rejection:str, val_type:str, val_item:str, val_oldValue:str, val_newValue:str, updatedPropertyValue:str """
        dummyVar = Variable(None)
        dummyVar.loadData(newValue)
        valid = True
        rejection = ""
        updatedPropertyValue = None
        if self.eslname().upper() != dummyVar.eslname().upper():
            #oldName = self.eslname()
            newName = dummyVar.eslname()
            errTxt = esl.ValidateName(newName, silent=True)
            if errTxt:
                rejection = "not a valid ESL name - " + errTxt
                valid = False
            else:
                if module.moduleType() == "package":
                    if module.eslnameIsInUse(newName):
                        rejection = "name \""+newName+"\" is already in " + module.identification() + " or a module using it"
                        valid = False
                else:
                    if module.eslnameIsInModule(newName):
                        rejection = "name \""+newName+"\" is already in use in " + module.identification()
                        valid = False
            if rejection:
                val_item += ".ESL Name"
        if len(self.assignedAttributes()) > 0:
            if self.datatype() != dummyVar.datatype():
                rejection = 'cannot change datatype as this variable is being used for an attribute value'
                val_item += ".Data Type"
                valid = False
            if self.dimensions() != dummyVar.dimensions():
                rejection = 'cannot change dimensions as this variable is being used for an attribute value'
                val_item += ".Dimensions"
                valid = False
        if rejection:
            val_oldValue = self.shortVariableValueText(showValue=False)
            val_newValue = dummyVar.shortVariableValueText(showValue=False)
        if valid:
            valid, rejection, val_type, val_item, updatedESLValue = self._eslValue.validateESLValuePropertyChange(dummyVar._eslValue, val_type, val_item)
            if valid:
                if updatedESLValue is not None:
                    updatedValue = updatedESLValue.datatype()
                    if updatedValue != dummyVar.datatype():
                        dummyVar.set_datatype(updatedValue)
                    updatedValue = updatedESLValue.dimensions()
                    if updatedValue != dummyVar.dimensions():
                        dummyVar.set_dimensions(updatedValue)
                    updatedValue = updatedESLValue.valueStr()
                    if updatedValue != dummyVar.valueStr():
                        dummyVar.set_valueStr(updatedValue)
                    updatedPropertyValue = dummyVar.save(saveDefaults=True)
            if rejection:
                val_item += ".Value"
                val_oldValue = self.shortVariableValueText(showValue=True)
                val_newValue = dummyVar.shortVariableValueText(showValue=True)
                if dummyVar.eslValue().equals(self.eslValue()): # the variable's ESLValue property was not changed
                    rejection = "" # don't reject the full variable property change
                    valid = True
        return valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue

    def updateVariableProperty(self, module, propertyTag, newValue, suppress_action=False):
        oldEslname = self.eslname()
        oldDatatype = self.datatype()
        oldDimensions = self.dimensions()
        oldValueStr = self.valueStr()
        self.loadData(newValue)
        newEslname = self.eslname()
        newDatatype = self.datatype()
        newDimensions = self.dimensions()
        newValueStr = self.valueStr()
        if oldEslname != newEslname:
            module.blockNames().delete(oldEslname)
            module.blockNames().add(newEslname, self)
        if oldEslname != newEslname or oldDatatype != newDatatype or oldDimensions != newDimensions or oldValueStr != newValueStr:
            for attribute in self.assignedAttributes():
                if oldEslname != newEslname:
                    attrValueStr = attribute.valueStr()
                    attrValueStr = attrValueStr.replace(oldEslname, newEslname) # preserve any reference
                    attribute.set_valueStr(attrValueStr)
                entity = attribute.parent()
                annotationId, annotationTxt, annotationVisible = dgAction.setEntityAttributeAnnotations(attribute)
                dgAction.sendAnnotationUpdate(entity, annotationId, annotationTxt, annotationVisible)
