#! /usr/bin/python

import esl_diagram.xmlutil as xut

from .. import utils as Utils
from .variable import Variable
from ..esl.esl import EslTypeNames
from ..esl.parseesl import ParseEsl, DimensionalityParseObject
from .module import Module
from .eslvalue import ESLValue

class Attribute(Variable):

    RESERVED_REAL = ['T', 'TSTART', 'TFIN', 'CINT', 'DISERR', 'INTERR']
    RESERVED_INT = ['NSTEP', 'ALGO']

    AttributeDefaults = None
    SourceValue = "Value"
    ValueEnumRefExtn = '+valueEnum'
    EnumValuesSplitCharacters = ["|", "/"]  # permitted characters to split a set of enum values joined in a string

    def __init__(self, parent, tag="", description="", constant="false", parameter="false",
                 datatype="", dimensions="", valueStr=""):
        Variable.__init__(self, parent, "", description, constant, parameter, datatype, dimensions, valueStr)
        self._hint = ""
        self._tag = tag
        self._is_special = "false"
        self._source  = Attribute.SourceValue # Parameter|<package-name>|Reserved|Output or Value (== to unset)
        self._enums = ""
        self._variableOrPort = None
        self._show_valueOnTop = "true" # Default "true" so attribute's property has its Value in the Top cell of the property (if "false" Value is a child property and the Top cell is a value display).
        self._show_tag = "false"
        self._show_eslname = "false"
        self._show_description = "false"
        self._show_source = "false"
        self._show_value = "false"
        self.set_defaults_for_datatype(self.datatype())
        self._argument = None  # Holds ArgumentEntity for a diagram subprogram (not saved/loaded nor copied).

    def set_defaults_for_datatype(self, datatype):
        if datatype and datatype.upper() in EslTypeNames:
            self._has_eslname = "true"
            self._has_sources = ""  # "|" separated list of "Value|Reserved|Parameter|Package|Output" (Package means any package), blank means all allowed (None means same as just Value)
            self._has_annotations = "true"
            self._hide_datatype = "false"
        else:
            self._has_eslname = "false"
            self._has_sources = "None"
            self._has_annotations = "false"
            self._hide_datatype = "true"

    def hint(self): return self._hint
    def tag(self): return self._tag
    def is_special(self): return self._is_special
    def source(self): return self._source
    def enums(self): return self._enums
    def variableOrPort(self): return self._variableOrPort
    def default_value(self):
        return self._eslValue.defaultValueStr()
    def show_valueOnTop(self): return self._show_valueOnTop
    def show_tag(self): return self._show_tag
    def show_eslname(self): return self._show_eslname
    def show_description(self): return self._show_description
    def show_source(self): return self._show_source
    def show_value(self): return self._show_value
    def has_eslname(self): return self._has_eslname
    def has_sources(self): return self._has_sources
    def has_annotations(self): return self._has_annotations
    def hide_datatype(self): return self._hide_datatype
    def argument(self): return self._argument
    def set_tag(self, value): self._tag = value
    def set_is_special(self, value): self._is_special = value
    def set_source(self, value): self._source = value
    def set_enums(self, value): self._enums = value
    def set_variableOrPort(self, value): self._variableOrPort = value
    def set_default_value(self, value):
        self._eslValue.set_defaultValueStr(value)
    def set_show_valueOnTop(self, value): self._show_valueOnTop = value
    def set_show_tag(self, value): self._show_tag = value
    def set_show_eslname(self, value): self._show_eslname = value
    def set_show_description(self, value): self._show_description = value
    def set_show_source(self, value): self._show_source = value
    def set_show_value(self, value): self._show_value = value
    def set_has_eslname(self, value): self._has_eslname = value
    def set_has_sources(self, value): self._has_sources = value
    def set_has_annotations(self, value): self._has_annotations = value
    def set_hide_datatype(self, value): self._hide_datatype = value
    def set_argument(self, value): self._argument = value
    def getInitialisationValue(self, useDefaultValue:bool=True, generateDefaultValue:bool=True) -> str: # Generate if not otherwise specified
        return super(Attribute, self).getInitialisationValue(useDefaultValue, generateDefaultValue)

    def detachedCopy(self, parent):
        """ Copies from self to make a new Attribute with a new parent (may be None) """
        newAtt = Attribute(parent)
        newAtt.copyFrom(self, parent)
        return newAtt

    def copyFrom(self, otherAttribute, parent):
        """ Copies from otherAttribute into the self except for parent which it updates (may set it None) """
        self._parent = parent
        Variable.copyFrom(self, otherAttribute, parent)
        self.set_default_value(otherAttribute.default_value())
        self._hint = otherAttribute._hint
        self._tag = otherAttribute._tag
        self._is_special = otherAttribute._is_special
        self._source = otherAttribute._source
        self._enums = otherAttribute._enums
        self._variableOrPort = otherAttribute._variableOrPort
        self._show_valueOnTop = otherAttribute._show_valueOnTop
        self._show_tag = otherAttribute._show_tag
        self._show_eslname = otherAttribute._show_eslname
        self._show_description = otherAttribute._show_description
        self._show_source = otherAttribute._show_source
        self._show_value = otherAttribute._show_value
        self._has_eslname = otherAttribute._has_eslname
        self._has_sources = otherAttribute._has_sources
        self._has_annotations = otherAttribute._has_annotations
        self._hide_datatype = otherAttribute._hide_datatype
        self._argument = otherAttribute._argument

    def copyAssignables(self, otheratt):
        if otheratt.datatype(): self.set_datatype(otheratt.datatype())
        if otheratt.dimensions(): self.set_dimensions(otheratt.dimensions())
        otherEslValueSaveStr = otheratt._eslValue.saveStr()
        if otherEslValueSaveStr != ESLValue.DefaultEslValueSaveStr:
            self._eslValue.loadStr(otherEslValueSaveStr, checkValidity=False)
        if otheratt._source: self._source = otheratt._source
        if otheratt._enums: self._enums = otheratt._enums
        if otheratt._eslname: self._eslname = otheratt._eslname
        if otheratt._show_valueOnTop: self._show_valueOnTop = otheratt._show_valueOnTop
        if otheratt._show_tag: self._show_tag = otheratt._show_tag
        if otheratt._show_eslname: self._show_eslname = otheratt._show_eslname
        if otheratt._show_description: self._show_description = otheratt._show_description
        if otheratt._show_source: self._show_source = otheratt._show_source
        if otheratt._show_value: self._show_value = otheratt._show_value
        if otheratt._has_eslname: self._has_eslname = otheratt._has_eslname
        if otheratt._has_sources: self._has_sources = otheratt._has_sources
        if otheratt._has_annotations: self._has_annotations = otheratt._has_annotations
        if otheratt._hide_datatype: self._hide_datatype = otheratt._hide_datatype

    def clearAssignables(self):
        self.set_valueStr("")
        self._source = ""
        self._enums = ""
        self._eslname = ""
        self._show_valueOnTop = ""
        self._show_tag = ""
        self._show_eslname = ""
        self._show_description = ""
        self._show_source = ""
        self._show_value = ""
        self._has_eslname = ""
        self._has_sources = ""
        self._has_annotations = ""
        self._hide_datatype = ""

    def set_parent(self, parent):
        self._parent = parent

    def set_valueData(self, valueData, suppressAddName=False):
        self.loadData(valueData, suppressAddName)
        variableOrPort = self.getVariableFromSource()
        self.linkAttributeWithVariableOrPort(variableOrPort)

    def unlinkAttributeWithVariableOrPort(self):
        currentVariableOrPort = self.variableOrPort()
        if currentVariableOrPort is not None:
            currentVariableOrPort.assignedAttributes().remove(self)

    def linkAttributeWithVariableOrPort(self, variableOrPort):
        self.unlinkAttributeWithVariableOrPort()
        if variableOrPort is not None:
            variableOrPort.assignedAttributes().append(self)
        self.set_variableOrPort(variableOrPort)

    def load(self, attXmlElement, suppressAddName=False, suppressSetDefaultsForDatatype=False):
        Variable.load(self, attXmlElement, suppressAddName=suppressAddName)
        valueStr = self.valueStr()
        if self._eslname:
            module = self._parent
            if not suppressAddName:
                while module and not isinstance(module, Module):
                    module = module.parent()
                if module:
                    module.blockNames().add(self._eslname, self)
        val = attXmlElement.getAttribute("hint")
        if val is not None:
            self._hint = val
        val = attXmlElement.getAttribute("tag")
        if val is not None: self._tag = val
        val = attXmlElement.getAttribute("is-special")
        if val is not None: self._is_special = val
        val = attXmlElement.getAttribute("source")
        if val is not None:
            if val == "": val = Attribute.SourceValue
            elif val == "Reserved": val = "RESERVED"    # legacy fix up
            self._source = val
        val = attXmlElement.getAttribute("enums")
        if val is not None: self._enums = val
        val = attXmlElement.getAttribute("show-value-on-top")
        if val is not None: self._show_valueOnTop = val
        val = attXmlElement.getAttribute("show-tag")
        if val is not None: self._show_tag = val
        val = attXmlElement.getAttribute("show-eslname")
        if val is not None: self._show_eslname = val
        val = attXmlElement.getAttribute("show-description")
        if val is not None: self._show_description = val
        val = attXmlElement.getAttribute("show-source")
        if val is not None: self._show_source = val
        val = attXmlElement.getAttribute("show-value")
        if val is not None: self._show_value = val
        if not suppressSetDefaultsForDatatype:
            self.set_defaults_for_datatype(self.datatype())
        val = attXmlElement.getAttribute("has-eslname")
        if val is not None: self._has_eslname = val
        val = attXmlElement.getAttribute("has-sources")
        if val is not None: self._has_sources = val
        val = attXmlElement.getAttribute("has-annotations")
        if val is not None: self._has_annotations = val
        val = attXmlElement.getAttribute("hide-datatype")
        if val is not None: self._hide_datatype = val

    def getVariableFromSource(self):
        variableOrPort = None
        if self._source != Attribute.SourceValue and self._source.upper() != 'RESERVED':
            varName = ""
            if self.valueStr():
                oldSource = self._source
                sources, sourceEnumValues = self.get_valid_sources_and_sourceEnumValues()
                source = self.check_valid_source_and_enumValue(sources, sourceEnumValues)
                if source != oldSource:
                    self._source = source
                else:
                    valueStr = self.valueStr()
                    if valueStr.endswith(")"): # an array with reference
                        pos = valueStr.rfind("(")
                        baseValueStr = valueStr[:pos]
                    else:
                        baseValueStr = valueStr
                    if baseValueStr == valueStr:
                        if valueStr in sourceEnumValues[source]:
                            varName = valueStr
                    else:
                        for enumValue in sourceEnumValues[source]:
                            attrValueEnum, baseEnumValue, reference = Attribute.check_enumValue_reference(enumValue)
                            if baseEnumValue == baseValueStr:
                                varName = baseValueStr
                                break
            if varName:
                entity = self._parent
                diagInfo = entity.parent()
                module = diagInfo.parent()
                application = module.application()
                if self._source == 'Parameter':
                    variableOrPort = module.blockNames().get(varName)
                elif self._source == 'RESERVED' or self._source == 'Reserved':
                    variableOrPort = None # We don't want to link attribute with a simulation parameter
                elif self._source == 'Output':
                    for simEntity in list(diagInfo.simulationEntities().values()):
                        if simEntity != entity:
                            for port in list(simEntity.ports().values()):
                                if port.eslname() == varName:
                                    variableOrPort = port
                                    break
                            if variableOrPort: break
                elif self._source != Attribute.SourceValue: #<package-name>
                    package = application.getPackageByName(self._source)
                    if package:
                        variableOrPort = package.blockNames().get(varName)
        return variableOrPort

    def save(self, indent=None, level=0, saveDefaults=False, exemplarAttribute=None):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ""
        properties = ""
        exemplar = exemplarAttribute
        if exemplar is None:
            if Attribute.AttributeDefaults is None:
                Attribute.AttributeDefaults = Attribute(None)
            exemplar = Attribute.AttributeDefaults
            exemplar.set_defaults_for_datatype(self.datatype())
        if saveDefaults or self._is_special != exemplar._is_special:
            properties += ' is-special="' + self._is_special + '"'
        eslValueSaveStr = self._eslValue.saveStr()
        if saveDefaults or self._source != Attribute.SourceValue:
            properties += ' source="' + self._source + '"'
        if saveDefaults or self._enums != exemplar._enums:
            properties += ' enums="' + self._enums + '"'
        if saveDefaults or eslValueSaveStr != exemplar._eslValue.saveStr():
            properties += ' value="' + xut.entitise(eslValueSaveStr) + '"'
        if saveDefaults or (self.datatype() != exemplar.datatype() or self.dimensions() != exemplar.dimensions()):
            properties += ' type="' + self.datatype() + '"'
            properties += ' dimensions="' + self.dimensions() + '"'
        if saveDefaults or self._eslname:
            properties += ' eslname="' + self._eslname + '"'
        if saveDefaults or self._show_valueOnTop != exemplar._show_valueOnTop:
            properties += ' show-tag-value-on-top="' + self._show_valueOnTop + '"'
        if saveDefaults or self._show_tag != exemplar._show_tag:
            properties += ' show-tag="' + self._show_tag + '"'
        if saveDefaults or self._show_eslname != exemplar._show_eslname:
            properties += ' show-eslname="' + self._show_eslname + '"'
        if saveDefaults or self._show_description != exemplar._show_description:
            properties += ' show-description="' + self._show_description + '"'
        if saveDefaults or self._show_source != exemplar._show_source:
            properties += ' show-source="' + self._show_source + '"'
        if saveDefaults or self._show_value != exemplar._show_value:
            properties += ' show-value="' + self._show_value + '"'
        if saveDefaults or self._has_eslname != exemplar._has_eslname:
            properties += ' has-eslname="' + self._has_eslname + '"'
        if saveDefaults or self._has_sources != exemplar._has_sources:
            properties += ' has-sources="' + self._has_sources + '"'
        if saveDefaults or self._has_annotations != exemplar._has_annotations:
            properties += ' has-annotations="' + self._has_annotations + '"'
        if saveDefaults or self._hide_datatype != exemplar._hide_datatype:
            properties += ' hide-datatype="' + self._hide_datatype + '"'
        if properties:
            result = ind + '<attribute tag="' + self._tag + '"'
            result += properties
            result += '/>' + nl
        return result

    def shortAttributeValueText(self, showName=True, showValue=False):
        val_text = '<attribute tag="' + self._tag + '"'
        if showName and self._eslname:
            val_text += " name=\""+self._eslname+"\""
        if showValue and self._eslValue.saveStr() != ESLValue.DefaultEslValueSaveStr:
            val_text += " value("+self._eslValue.mode()+")=\""+self._eslValue.valueStr()+"\""
        val_text += ">"
        return val_text

    @staticmethod
    def splitEnums(enums):
        enumValues = []
        splitCh = "|"
        if enums:
            if enums[0] in Attribute.EnumValuesSplitCharacters:
                if enums[-1] == enums[0]:
                    splitCh = enums[0]
                    enums = enums[1:-1]
            enumValues = list(map(lambda item: item.strip(), enums.split(splitCh)))
        return enumValues

    def setESLValueForEnumValue(self, enumValue, is_valid=True):
        validity = 'valid'
        if not is_valid:
            validity = 'invalid'
        loadvalueEnumStr = "{" + validity + "|raw|" + enumValue + "}"
        self._eslValue.loadStr(loadvalueEnumStr, checkValidity=False)

    def check_valid_source_and_enumValue(self, sources, sourceEnumValues) -> str:
        source = self.source()
        if not source:
            source = Attribute.SourceValue
        msgSource = source
        if source not in ['Parameter', 'Output', 'RESERVED']:
            msgSource = "Package " + msgSource
        if source not in sources:
            msg = "source " + msgSource + " is not available for this attribute"
            entityAttribute = self._parent.attributes().get(self._tag)
            entityAttribute.eslValue().set_validity('invalid', msg)
            source = sources[0]
            entityAttribute.set_source(source)
        elif source != Attribute.SourceValue:
            attrValueEnum = self._eslValue.valueStr()
            attrValueEnum, baseEnumValue, reference = Attribute.check_enumValue_reference(attrValueEnum)
            enumValues = self.get_initial_enumValues(source, sources, sourceEnumValues)
            valid = False
            if not reference:
                if attrValueEnum in enumValues:
                    valid = True
            else:
                idx = Attribute.get_enumValue_index(baseEnumValue, enumValues)
                if idx >= 0:
                    valid = True
            if not valid:
                msg = "value " + attrValueEnum + " is not available in source " + msgSource
                entityAttribute = self._parent.attributes().get(self._tag)
                entityAttribute.eslValue().set_validity('invalid', msg)
                source = sources[0]
                entityAttribute.set_source(source)
            else:
                self.setESLValueForEnumValue(attrValueEnum)
        return source

    def check_valid_variable(self, variable):
        variableName = ""
        if variable.datatype() == self.datatype():
            # Check parameter dimensions match (same number and sizes) or can subsume this attribute's dimensions.
            ownDimensionality = ParseEsl.get_dimensionality(self.dimensions())
            varDimensionality = ParseEsl.get_dimensionality(variable.dimensions())
            compatibility = ownDimensionality.compatibility(varDimensionality)
            if compatibility == 'same' or compatibility == 'compatible':
                variableName = variable.eslname()
            elif compatibility == 'minimal-form-compatible': # also
                variableName = variable.eslname()
            elif compatibility == 'sliceable':
                # attribute can be set with a variable reference - a slice of the variable
                reference = self.get_first_variable_reference(variable)
                variableName = variable.eslname() + "(" + reference + ")..."
        return variableName

    def get_valid_parameters(self):
        parameterNames = []
        module = self._parent.parent().parent()
        for parameter in list(module.variables().values()):
            variableName = self.check_valid_variable(parameter)
            if variableName:
                parameterNames.append(variableName)
        return parameterNames

    def get_valid_package_varNames(self, module, packageName):
        varNames = []
        package = module.application().getPackageByName(packageName)
        if package:
            for var in list(package.variables().values()):
                variableName = self.check_valid_variable(var)
                if variableName:
                    varNames.append(variableName)
        return varNames

    def get_valid_packages(self):
        packageNames = []
        packageVarNames = {}
        module = self._parent.parent().parent()
        for packageName in module.diagramInfo().importedPackageNames():
            varNames = self.get_valid_package_varNames(module, packageName)
            if len(varNames) > 0:
                packageNames.append(packageName)
                packageVarNames[packageName] = varNames
        return packageNames, packageVarNames

    def get_valid_outputs(self):
        outputVarNames = []
        module = self._parent.parent().parent()
        for entity in list(module.diagramInfo().simulationEntities().values()):
            if entity != self._parent:
                for port in list(entity.ports().values()):
                    if port.direction() == "output" and port.datatype() == self.datatype():
                        if port.eslname():
                            # Check port dimensions match (same number and sizes) - don't permit reference.
                            ownDimensionality = ParseEsl.get_dimensionality(self.dimensions())
                            portDimensionality = ParseEsl.get_dimensionality(port.dimensions())
                            compatibility = ownDimensionality.compatibility(portDimensionality)
                            if compatibility == 'same' or compatibility == 'compatible':
                                outputVarNames.append(port.eslname())
        return outputVarNames

    def get_initial_enumValues(self, source, sources, sourceEnumValues):
        # Called when source has changed.
        # After this enumValues for arrays have the first variable reference (eg. ending "(1,1,1)..."
        enumValues = []
        if source != Attribute.SourceValue:
            enumValues = []
            if source == 'Parameter':
                enumValues = sourceEnumValues[source].copy()
            elif source == 'RESERVED':
                if self.datatype() == 'Real':
                    enumValues = Attribute.RESERVED_REAL.copy()
                elif self.datatype() == 'Integer':
                    enumValues = Attribute.RESERVED_INT.copy()
            elif source == 'Output':
                enumValues = sourceEnumValues[source].copy()
            else:
                if source in sources:
                    enumValues = sourceEnumValues[source].copy()
        return enumValues

    @staticmethod
    def check_enumValue_reference(enumValueOrAttrValueEnum:str) -> (str, str, str):
        # returns attrValueEnum, baseEnumValue, reference
        attrValueEnum = enumValueOrAttrValueEnum
        baseEnumValue = ""
        reference = ""
        if enumValueOrAttrValueEnum.endswith(")..."):
            attrValueEnum = enumValueOrAttrValueEnum[:-3]
        if attrValueEnum.endswith(")"):
            pos = attrValueEnum.rfind("(")
            baseEnumValue = attrValueEnum[:pos]	# stem-name of array variable
            reference = attrValueEnum[pos+1:-1] # without enclosing brackets
        return attrValueEnum, baseEnumValue, reference

    @staticmethod
    def get_enumValue_index(baseEnumValue, enumValues):
        idx = -1
        for i in range(len(enumValues)):
            if enumValues[i].endswith(")..."):
                pos = enumValues[i].rfind("(")
                if pos >= 0:
                    if enumValues[i][:pos] == baseEnumValue:
                        idx = i
                        break
        return idx

    def get_first_variable_reference(self, variable):
        ownDimensionality = ParseEsl.get_dimensionality(self.dimensions())
        varDimensionality = ParseEsl.get_dimensionality(variable.dimensions())
        varNumber = varDimensionality.number()
        varBounds = varDimensionality.bounds()
        varSizes = varDimensionality.sizes()
        ownNumber = ownDimensionality.number()
        ownSizes = ownDimensionality.sizes()
        reference = str(varBounds[0][0]) # low-bound-dim1
        if ownNumber >= 1 and ownSizes[0] > 1:
            reference += ".."
            reference += str(varBounds[0][0] + ownSizes[0] - 1)
        if varNumber >= 2:
            reference += "," +   str(varBounds[1][0])
            if ownNumber >= 2 and ownSizes[1] > 1:
                reference += ".."
                reference += str(varBounds[1][0] + ownSizes[1] - 1)
            if varNumber == 3:
                reference += "," + str(varBounds[2][0])
                if ownNumber == 3 and ownSizes[2] > 1:
                    reference += ".."
                    reference += str(varBounds[2][0] + ownSizes[2] - 1)
        return reference

    def check_valid_variable_reference(self, reference:str, variable) -> str:
        rejectMsg = ""
        ownDimensionality = ParseEsl.get_dimensionality(self.dimensions())
        ownNumber = ownDimensionality.number()
        elementOrSlice = "element" if ownNumber == 0 else "slice"
        refDimensionality = ParseEsl.get_dimensionality(reference, parseReference=True)  # Can parse a reference like dimensions (slice looks like a dimension's bounds).
        if refDimensionality is None:
            rejectMsg = "reference has no dimensionality"
        rejectMsgStart = "invalid reference \"" + reference + "\":"
        if not rejectMsg:   # check reference was well formed
            if len(refDimensionality.messages) > 0:
                rejectMsg = rejectMsgStart
                for parseMessage in refDimensionality.messages:
                    rejectMsg += "\n" + parseMessage.message
        if not rejectMsg:   # Check for additional slice syntax restriction (Dev Guide 6.3 Array Slicing).
            # If the first subscript is not sliced, then subsequent subscripts must not be sliced; the following is illegal: AAA(2,3..4,4) --ILLEGAL
            if ownDimensionality.size() > 1:
                refComponents = reference.split(",")
                if refComponents[0].find("..") < 0:
                    rejectMsg = rejectMsgStart + "\nreference for slice requires slice notation (..) in first component"
        if not rejectMsg:   # check reference suits variable's dimensionality
            varDimensionality = ParseEsl.get_dimensionality(variable.dimensions())
            varNumber = varDimensionality.number()
            if refDimensionality.number() != varNumber:
                rejectMsg = rejectMsgStart + "\nreference to variable " + elementOrSlice + " needs " + str(varNumber)
                rejectMsg += " dimension" if varNumber == 1 else " dimensions"
            else:
                varBounds = varDimensionality.bounds()
                refBounds = refDimensionality.bounds()
                for dim in range(varNumber):
                    if ((refBounds[dim][0] != DimensionalityParseObject.ReferenceUnsliced and refBounds[dim][0] < varBounds[dim][0])
                        or refBounds[dim][1] > varBounds[dim][1]):
                        rejectMsg = rejectMsgStart + "\nout of range bounds for variable"
                        if dim == 0 and varNumber > 1:
                            rejectMsg += " (first dimension)"
                        elif dim == 1:
                            rejectMsg += " (second dimension)"
                        elif dim == 2:
                            rejectMsg += " (third dimension)"
                        break
        if not rejectMsg:   # check reference sizes suit attribute's dimensionality
            ownSize = ownDimensionality.size()
            refSize = refDimensionality.size()
            if refSize != ownSize:
                rejectMsg = rejectMsgStart + "\nreference (size "+str(refSize)+") must have same number of elements as the attribute needs ("+str(ownSize)+")"
            else:
                # ESL requires each 'minimal form's of dimensions (sizes) to match (Dev Guide 6.4.1 Array assignment).
                ownMinFormSizes = ownDimensionality.minimalFormSizes()
                refMinFormSizes = refDimensionality.minimalFormSizes()
                if ownMinFormSizes != refMinFormSizes:
                    ownMinsStr = ",".join(map(lambda it: str(it), ownMinFormSizes))
                    refMinsStr = ",".join(map(lambda it: str(it), refMinFormSizes))
                    rejectMsg = rejectMsgStart + "\nreference minimal form dimension (" + ownMinsStr + \
                                ") must match that for attribute (" + refMinsStr + ")"
        return rejectMsg

    def get_sourceEnumValues(self, source) -> dict:
        sourceEnumValues = {}
        if source == 'Parameter':
            parameterNames = self.get_valid_parameters()
            if len(parameterNames) > 0:
                sourceEnumValues['Parameter'] = parameterNames
        elif source == 'Output':
            outputVarNames = self.get_valid_outputs()
            if len(outputVarNames):
                sourceEnumValues['Output'] = outputVarNames
        elif source != Attribute.SourceValue and source != 'RESERVED':
            varNames = self.get_valid_package_varNames(self._parent, source)
            sourceEnumValues[source] = varNames
        return sourceEnumValues

    def get_valid_sources_and_sourceEnumValues(self) -> (list, dict):
        sources = []
        sourceEnumValues = {}
        has_sources = self.has_sources()
        has_sources_list = has_sources.split('|')
        if not has_sources or has_sources == "None" or Attribute.SourceValue in has_sources_list:
            sources = [Attribute.SourceValue]
            sourceEnumValues[Attribute.SourceValue] = None
        if not has_sources or 'Parameter' in has_sources_list:
            parameterNames = self.get_valid_parameters()
            if len(parameterNames) > 0:
                sources.append('Parameter')
                sourceEnumValues['Parameter'] = parameterNames
        if not has_sources or 'Package' in has_sources_list:
            packageNames, packageVarNames = self.get_valid_packages()
            if len(packageNames) > 0:
                Utils.extendNew(sources, packageNames)
                for packageName in packageNames:
                    if packageName in sourceEnumValues:
                        Utils.extendNew(sourceEnumValues[packageName], packageVarNames[packageName])
                    else:
                        sourceEnumValues[packageName] = packageVarNames[packageName]
        if not has_sources or 'RESERVED' in has_sources_list or 'Reserved' in has_sources_list:
            if not self.dimensions() and (self.datatype() == 'Real' or self.datatype() == 'Integer'):
                sources.append('RESERVED')
                sourceEnumValues['RESERVED'] = None
        if not has_sources or 'Output' in has_sources_list:
            outputVarNames = self.get_valid_outputs()
            if len(outputVarNames):
                sources.append('Output')
                sourceEnumValues['Output'] = outputVarNames
        return sources, sourceEnumValues
