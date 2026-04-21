#! /usr/bin/python

import re

import wx

from ..esl import esl
from ..esl.parseesl import ParseEsl, DimensionalityParseObject

realPattern = re.compile(r"([+-])?\d+(\.\d+)?([EeDd][+-]?\d+)?$")
integerPattern = re.compile(r"[+-]?\d+$")
multipleComponentPattern = re.compile(r"(\d+)\s*\*\s*")
def isRealValue(valueStr:str) -> bool:
    result = False
    if realPattern.match(valueStr):
        result = True
    return result
def getRealValue(valueStr:str) -> str:
    """valueStr is assumed to be a valid real number (isRealValue)"""
    """ returns result:str with any 0(s) after/before . if required, else as given"""
    result = valueStr
    dot = valueStr.find('.')
    hasExp = valueStr.lower().find('e') != -1 or valueStr.lower().find('d') != -1
    if dot == len(valueStr) - 1: result += '0'  # dot at end
    if dot < 0 and not hasExp:
        result += '.0'
    return result
def isIntegerValue(valueStr:str) -> bool:
    result = False
    if integerPattern.match(valueStr):
        result = True
    return result
def getLogicalValue(valueStr:str) -> str:
    """ returns result:str - empty string or a valid ESL LOGICAL value (TRUE or FALSE) """
    result = ""
    upperValue = valueStr.upper()
    if upperValue == esl.EslLogicalValues[0] or \
        upperValue == esl.EslLogicalValues[0][0] or \
        upperValue == "1":
        result = esl.EslLogicalValues[0]
    elif upperValue == esl.EslLogicalValues[1] or \
        upperValue == esl.EslLogicalValues[1][0] or \
        upperValue == "0":
        result = esl.EslLogicalValues[1]
    return result

class ESLValue:
    DefaultEslValueSaveStr = "{unchecked|check|}"

    def __init__(self, parent, datatype:str="", dimensions:str="", valueStr:str="", defaultValueStr="") -> None:
        self._parent = parent
        self._parseEsl = None
        self._datatype = datatype
        self._dimensions = dimensions
        self._valueStr = valueStr # raw text of value without any braces/encoding for other features
        self._defaultValueStr = defaultValueStr
        # Features
        self._validity = 'unchecked' # one of: unchecked, valid, invalid - results of validation (if any)
        self._validityMsg = ""
        self._mode = 'check' # one of: 'check' 'raw' - whether perform validation on property change
        if self._datatype == "String" or self._datatype == "Character":
            self._mode = 'raw'

    def __str__(self) -> str:
        strng = "<" + self._datatype
        if self._dimensions:
            strng += "(" + self._dimensions + ")"
        strng += ":" + self.saveStr() +">"
        return strng

    def parent(self):
        return self._parent
    def parseEsl(self):
        if self._parseEsl is None:
            self._parseEsl = ParseEsl()
        return self._parseEsl

    def detachedCopy(self, parent):
        """ Copies from self to make a new ESLValue with a new parent (may be None) """
        newESLVal = ESLValue(parent)
        newESLVal.copyFrom(self, parent)
        return newESLVal

    def copyFrom(self, otherESLValue, parent):
        """ Copies from otherESLValue into the self except for parent which it updates (may set it None) """
        self._parent = parent
        self._datatype = otherESLValue._datatype
        self._dimensions = otherESLValue._dimensions
        self._valueStr = otherESLValue._valueStr
        self._defaultValueStr = otherESLValue._defaultValueStr
        self._validity = otherESLValue._validity
        self._validityMsg = otherESLValue._validityMsg
        self._mode = otherESLValue._mode

    def equals(self, otherESLValue):
        """ Tests for equal content other than parent """
        result = self._datatype == otherESLValue._datatype and \
                 self._dimensions == otherESLValue._dimensions and \
                 self._valueStr == otherESLValue._valueStr and \
                 self._defaultValueStr == otherESLValue._defaultValueStr and \
                 self._validity == otherESLValue._validity and \
                 self._mode == otherESLValue._mode
        return result

    def datatype(self):
        return self._datatype
    def set_datatype(self, datatype):
        self._datatype = datatype
        if self._datatype == "String" or self._datatype == "Character":
            self._validity = 'unchecked'
            self._validityMsg = ""
            self._mode = 'raw'

    def dimensions(self):
        return self._dimensions
    def set_dimensions(self, dimensions):
        self._dimensions = dimensions
    def valueStr(self):
        return self._valueStr
    def set_valueStr(self, valueStr):
        self._valueStr = valueStr

    def defaultValueStr(self):
        return self._defaultValueStr
    def set_defaultValueStr(self, defaultValueStr):
        self._defaultValueStr = defaultValueStr

    def validity(self):
        return self._validity
    def validityMsg(self):
        return self._validityMsg
    def set_validity(self, validity, msgs=""):
        self._validity = validity
        self._validityMsg = msgs
    def mode(self):
        return self._mode
    def set_mode(self, mode):
        self._mode = mode

    def saveStr(self, indent=None, level=0, saveDefaults=False) -> str:
        # Saves as single line with - features encoded (always in full) except for String/Character types
        # Note: The defaultValueStr (if any) never saved, as should be set in context of other application objects programmatically (or when this one created initially once and for all).
        result = "{" + self._validity + "|" + self._mode + "|" + self._valueStr + "}"
        return result

    def loadStr(self, valueXMLstr:str, checkValidity:bool=True) -> None:
        valueXMLstrStripped = valueXMLstr.strip()
        self._validity = 'unchecked'
        self._validityMsg = ""
        self._mode = 'check'
        if valueXMLstrStripped and valueXMLstrStripped[0] == "{":
            if valueXMLstrStripped[-1] == "}":
                parts = valueXMLstrStripped[1:-1].strip().split("|", 2)
                if len(parts) == 3:
                    self._validity = parts[0].strip()
                    self._mode = parts[1].strip()
                    self._valueStr = parts[2] # un-stripped
                else:
                    raise Exception("ESLValue.loadStr - not 3 parts in \""+valueXMLstr+"\"")
            else:
                raise Exception("ESLValue.loadStr - unterminated braces in \"" + valueXMLstr + "\"")
        else: # old style value string
            self._valueStr = valueXMLstr
        if checkValidity and self._datatype != "" and valueXMLstr != ESLValue.DefaultEslValueSaveStr:
            showMessages = False
            self.checkValidity(showMessages=showMessages)

    def checkValidity(self, showMessages:bool=False) -> None:
        msgs = ""
        if self._mode == "check":
            validity = "valid"
            valid, msg, standardisedDatatype = self.validateESLValueDatatype()
            if not valid:
                msgs += msg
                validity = "invalid"
            valid, msgs, standardisedDimensions = self.validateESLValueDimensions()
            if not valid:
                msgs += msg
                validity = "invalid"
            valid, msgs, standardisedValueStr = self.validateESLValueValueStr(standardise=False)
            if not valid:
                msgs += msg
                validity = "invalid"
            self.set_validity(validity, msgs)
            if showMessages and msgs:
                msg = "ESL value "
                parent = self.parent()
                if parent and hasattr(parent, "eslname"):
                    msg += "for \""+parent.eslname()+"\" "
                while parent:
                    if hasattr(parent, "identification"):
                        msg += "in "+parent.identification()+" "
                    else:
                        if hasattr(parent, "parent"):
                            parent = parent.parent()
                        else:
                            parent = None
                msg += msgs
                wx.GetApp().frame().control().appendMessage(msg)

    def validateESLValueDatatype(self, datatype:str=None) -> (bool,str,str):
        """ returns: validDatatype:bool, msgs:str, standardisedDatatype:str"""
        validDatatype = True
        msgs = ""
        standardisedDatatype = None
        if datatype is None:
            datatype = self._datatype
        if datatype and datatype.upper() in esl.EslTypeNames:
            standardisedDatatype = datatype.title()
        else:
            msgs += "not a valid ESL Datatype \"" + datatype + "\"\n"
            validDatatype = False
        return validDatatype, msgs, standardisedDatatype

    def validateESLValueDimensions(self, dimensions: str=None) -> (bool, str, str):
        """ returns: validDimensions:bool, msgs:str, standardisedDimensions:str"""
        validDimensions = True
        msgs = ""
        if dimensions is None:
            dimensions = self._dimensions
        standardisedDimensions = dimensions.strip()
        allowStar = False  #### TODO - Check under what circumstances can we allow * for dimensions when validate (?never) - what does it affect
        pos, dimensionality = self.parseEsl().parseDimensions(dimensions, 0, None, checkNothingLeft=True, allowStar=allowStar)
        if dimensionality is not None:
            for parseMessage in dimensionality.messages:
                dimMsg = parseMessage.message + " "
                if dimMsg:
                    msgs += dimMsg
                    validDimensions = False
            if validDimensions:
                standardisedDimensions = dimensionality.dimensions()
        return validDimensions, msgs, standardisedDimensions

    def _validateESLValueScalarValueStr(self, valueStr:str, upperDatatype:str, standardise:bool) -> (bool, str, str):
        """ returns: validValueStr:bool, msg:str, standardValueStr:str"""
        validValueStr = True
        msg = ""
        standardValueStr = None
        if upperDatatype == esl.EslBaseTypeNames[0]:  # REAL
            if isRealValue(valueStr):
                if standardise:
                    standardValueStr = valueStr
                    match = realPattern.match(valueStr)
                    if match:
                        standardValueStr = getRealValue(valueStr)
            else:
                msg += "invalid REAL literal \"" + valueStr + "\"\n"
                validValueStr = False
        elif upperDatatype == esl.EslBaseTypeNames[1]:  # INTEGER
            if not isIntegerValue(valueStr):
                msg += "invalid INTEGER literal \"" + valueStr + "\"\n"
                validValueStr = False
            else:
                if standardise:
                    standardValueStr = valueStr
        elif upperDatatype == esl.EslBaseTypeNames[2]:  # LOGICAL
            isItLogical = getLogicalValue(valueStr)
            if isItLogical == "":
                msg += "invalid LOGICAL literal \"" + valueStr + "\"\n"
                validValueStr = False
            else:
                if standardise:
                    standardValueStr = valueStr
                    if isItLogical != valueStr:
                        standardValueStr = isItLogical
        # else other datatype leave as valid (no standard)
        return validValueStr, msg, standardValueStr

    def _validateESLValueArrayValueStr(self, valueStr:str, upperDatatype:str, dimensionality:DimensionalityParseObject, standardise:bool, requireFullSize:bool) -> (bool, str, str):
        """ returns: validValueStr:bool, msgs:str, standardValueStr:str"""
        validValueStr = True
        msgs = ""
        standardisedValueStr = None

        # Match something like: (<int> *)?<value> (, (<int> *)?<value> )*
        if standardise:
            standardisedValueStr = ""
        components = list(map(lambda item: item.strip(), valueStr.split(",")))
        count = 0
        for component in components:
            scalar = ""
            match = multipleComponentPattern.match(component)
            if match:
                multiple = int(match[1])
                scalar = component[match.end():]
            else:
                multiple = 1
                scalar = component
            valid, msg, standardValueStr = self._validateESLValueScalarValueStr(scalar, upperDatatype, standardise=standardise)
            if msg:
                msgs += msg
            if valid:
                count += multiple
                if standardise:
                    if standardisedValueStr:
                        standardisedValueStr += ","
                    if multiple > 1:
                        standardisedValueStr += str(multiple) + "*" + standardValueStr
                    else:
                        standardisedValueStr += standardValueStr
            else:   # dont go on to next component
                validValueStr = False
        pass
        if validValueStr:
            # parser and dimensionality already set in validateESLValueValueStr
            size = dimensionality.size()
            if count != size:
                if count < size and requireFullSize:
                    msgs += "need to specify full size ("+str(size)+ " elements) "+str(count)+" given\n"
                    validValueStr = False
                elif count > size:
                    msgs += "have specified over full size ("+str(size)+ " elements) "+str(count)+" given\n"
                    validValueStr = False
        return validValueStr, msgs, standardisedValueStr

    def validateESLValueValueStr(self, valueStr:str=None, standardise:bool=True, requireFullSize:bool=True) -> (bool, str, str):
        """ returns: validValueStr:bool, msgs:str, standardisedValueStr:str"""
        validValueStr = True
        msgs = ""
        standardisedValueStr = None
        if valueStr is None:
            valueStr = self._valueStr
        dimensionality = None
        if self._dimensions:
            allowStar = False  #### TODO - Check under what circumstances can we allow * for dimensions when validate (?never) - what does it affect
            pos, dimensionality = self.parseEsl().parseDimensions(self._dimensions, 0, None, checkNothingLeft=True, allowStar=allowStar)
        outerValueStr = valueStr.strip()
        innerValueStr = outerValueStr
        if standardise:
            standardisedValueStr = outerValueStr
        upperDatatype = self._datatype.upper()
        if outerValueStr:
            if outerValueStr[0] == "/":
                if outerValueStr[-1] != "/":
                    outerValueStr += "/"
            elif outerValueStr[0] == "[":
                if outerValueStr[-1] != "]":
                    outerValueStr += "]"
            if outerValueStr[0] == "/" or outerValueStr[0] == "[":
                innerValueStr = outerValueStr[1:-1].strip()
            if dimensionality is None or dimensionality.number() == 0:  # scalar
                validValueStr, msg, standardValueStr = self._validateESLValueScalarValueStr(innerValueStr, upperDatatype, standardise=standardise)
            else: # an array
                validValueStr, msg, standardValueStr = self._validateESLValueArrayValueStr(innerValueStr, upperDatatype, dimensionality, standardise=standardise, requireFullSize=requireFullSize)

            if msg:
                msgs += msg
            if standardise and standardValueStr:
                if outerValueStr[0] == "/" or outerValueStr[0] == "[":
                    standardisedValueStr = outerValueStr[0] + standardValueStr + outerValueStr[-1]
                else:
                    standardisedValueStr = standardValueStr

            #if standardisedValueStr == valueStr:
            #    standardisedValueStr = None
        return validValueStr, msgs, standardisedValueStr

    def validateESLValuePropertyChange(self, newESLValue:'ESLValue', val_type:str, val_item:str) -> (bool,str,str,str,'ESLValue'):
        """ returns: valid:bool, rejection:str, val_type:str, val_item:str, updatedESLValue """
        valid = True
        rejection = ""
        updatedESLValue = None
        dimensionality = None
        oldValidity = self._validity
        if newESLValue._mode == 'check':
            newDatatype = newESLValue._datatype
            newDimensions = newESLValue._dimensions
            newValueStr = newESLValue._valueStr
            changedDatatype = newDatatype != self._datatype
            changedDimensions = newDimensions != self._dimensions
            changedESLValue = not changedDatatype and not changedDimensions # change event may be due to a mode change or valueStr change
            if changedDatatype: # datatype was changed
                validDatatype, msgs, standardisedDatatype = self.validateESLValueDatatype(newDatatype)
                if not validDatatype:
                    rejection += msgs
                    if not changedDimensions and not changedESLValue: # others not changed
                        valid = validDatatype
                    else:
                        self.checkValidity()
                else:
                    if newDatatype != standardisedDatatype:
                        if updatedESLValue is None:
                            updatedESLValue = newESLValue.detachedCopy(newESLValue._parent)
                        updatedESLValue.set_datatype(standardisedDatatype)
            if changedDimensions: # dimensions was changed
                validDimensions, msgs, standardisedDimensions = self.validateESLValueDimensions(newDimensions)
                if not validDimensions:
                    rejection += msgs
                    if not changedESLValue: # ESLValue not changed
                        valid = validDimensions
                    else:
                        self.checkValidity()
                else:
                    if newDimensions != standardisedDimensions:
                        if updatedESLValue is None:
                            updatedESLValue = newESLValue.detachedCopy(newESLValue._parent)
                        updatedESLValue.set_dimensions(standardisedDimensions)

            if changedESLValue:  # ESLValue was changed
                validValueStr, msgs, standardisedValueStr = self.validateESLValueValueStr(newValueStr)
                if not validValueStr:
                    rejection += msgs
                    valid = validValueStr
                else:
                    if newValueStr != standardisedValueStr:
                        if updatedESLValue is None:
                            updatedESLValue = newESLValue.detachedCopy(newESLValue._parent)
                        updatedESLValue.set_valueStr(standardisedValueStr)
                        updatedESLValue.set_validity("valid")

                pass

            #else don't validate

        else: # Not checked
            newESLValue._validityMsg = ""

        if valid and oldValidity != newESLValue._validity:
            if updatedESLValue is None:
                updatedESLValue = newESLValue.detachedCopy(newESLValue._parent)
            updatedESLValue.set_validity(newESLValue._validity, newESLValue._validityMsg)

        return valid, rejection, val_type, val_item, updatedESLValue

    def getInitialisationValue(self, useDefaultValue:bool=True, generateDefaultValue:bool=False) -> str:
        """ Returns the initial value - with generated /../ or [..] delimeters if not specified.
            Uses specified valueStr, if not set and useDefaultValue[defaults:True] uses the specified defaultValueStr,
            and if not set and generateDefaultValue[defaults:False] generates an initialValue for the datatype and dimensionality."""
        initialValue = self._valueStr.strip()
        if not initialValue and useDefaultValue:
            initialValue = self._defaultValueStr.strip()
        if not initialValue and generateDefaultValue:
            initialValue = self.generateDefaultValue()
        if initialValue:
            if initialValue[0] == "/" and initialValue[-1] != "/":
                initialValue = "/" + initialValue[1:].strip() + "/"
            if initialValue[0] == "[" and initialValue[-1] != "]":
                initialValue = "[" + initialValue[1:].strip() + "]"
            dimensionality = None
            if self._dimensions:
                pos, dimensionality = self.parseEsl().parseDimensions(self._dimensions, 0, None, checkNothingLeft=True, allowStar=False)
            if self._validity != 'invalid' and self._mode == 'check' and self._datatype == 'Real' and (not dimensionality or dimensionality.number() == 0):
                realisedValue = initialValue
                if initialValue[0] == "/" or initialValue[0] == "[":
                    realisedValue = initialValue[1:-1].strip()
                if realisedValue and (realisedValue.find('.') == -1 and realisedValue.lower().find('e') == -1):
                    realisedValue = getRealValue(realisedValue)
                if initialValue[0] == "/":
                    initialValue = "/" + realisedValue + "/"
                elif initialValue[0] == "[":
                    initialValue = "[" + realisedValue + "]"
                else:
                    initialValue = realisedValue
            if initialValue and initialValue[0] != "/" and initialValue[0] != "[":  # delimiter not included (when specified)
                if not dimensionality or dimensionality.number() <= 1:  # scalars and vectors
                    # Order is "column-major"  # i.e. use //
                    initialValue = "/" + initialValue + "/"
                else:
                    # Order is "row-major"  # i.e. use []
                    initialValue = "[" + initialValue + "]"
        return initialValue

    def generateDefaultValue(self):
        """ Returns a generated value for the datatype and dimensionality. """
        generatedValue = ""
        upperDatatype = self._datatype.upper()
        if upperDatatype in esl.EslBaseTypeNames:
            if upperDatatype == esl.EslBaseTypeNames[0]:  # REAL
                generatedValue = "0.0"
            elif upperDatatype == esl.EslBaseTypeNames[1]:  # INTEGER
                generatedValue = "0"
            elif upperDatatype == esl.EslBaseTypeNames[2]:  # LOGICAL
                generatedValue = "FALSE"
        if self._dimensions:
            pos, dimensionality = self.parseEsl().parseDimensions(self._dimensions, 0, None, checkNothingLeft=True, allowStar=False)
            generatedValue = str(dimensionality.size()) + "*" + generatedValue
        return generatedValue
