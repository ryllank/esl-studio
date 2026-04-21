#! /usr/bin/python

from collections import OrderedDict

from .callablesubprogram import CallableSubprogram
from .port import Port
from .attribute import Attribute

class CallableCodeSubprogram(CallableSubprogram): # mixin class for CodeSubprogram

    def __init__(self):
        CallableSubprogram.__init__(self, 'code') # has self._subprogramCalls

    def getPorts(self, allowBlankTag=False):
        ports = OrderedDict()
        count = 1
        for argumentParseObject in self.argumentParseObjects():
            if not argumentParseObject.isOutput and not argumentParseObject.isConstant:
                datatype = argumentParseObject.datatype.title()
                dimensions = ""
                if argumentParseObject.dimensionality:
                    if not argumentParseObject.dimensionality.usable:
                        datatype = ""
                    else:
                        dimensions = argumentParseObject.dimensionality.dimensions()
                if datatype:
                    port = Port(None, str(count), datatype, 'input', '', argumentParseObject.name)
                    if dimensions:
                        port.set_dimensions(dimensions)
                    ports[str(count)] = port
                    count += 1
        for argumentParseObject in self.argumentParseObjects():
            if argumentParseObject.isOutput:
                datatype = argumentParseObject.datatype.title()
                dimensions = ""
                if argumentParseObject.dimensionality:
                    if not argumentParseObject.dimensionality.usable:
                        datatype = ""
                    else:
                        dimensions = argumentParseObject.dimensionality.dimensions()
                if datatype:
                    port = Port(None, str(count), datatype, 'output', '', argumentParseObject.name)
                    if dimensions:
                        port.set_dimensions(dimensions)
                    ports[str(count)] = port
                    count += 1
        return ports

    def getAttributes(self):
        atts = OrderedDict()
        for argumentParseObject in self.argumentParseObjects():
            if argumentParseObject.isConstant:
                tag = argumentParseObject.name
                datatype = argumentParseObject.datatype.title()
                dimensions = ""
                defaultValue = '0.0'
                if datatype == 'Integer':
                    defaultValue = '0'
                elif datatype == 'Logical':
                    defaultValue = 'FALSE'
                if argumentParseObject.dimensionality:
                    if not argumentParseObject.dimensionality.usable:
                        datatype = ""
                    else:
                        dimensions = argumentParseObject.dimensionality.dimensions()
                        size = argumentParseObject.dimensionality.size()
                        if isinstance(size, int) and size > 0:
                            defaultValue = str(size) + "*" + defaultValue
                        else:
                            defaultValue = str(argumentParseObject.dimensionality.number()) + "*" + defaultValue
                if datatype:
                    attribute = Attribute(None, tag, tag, datatype=datatype, valueStr=defaultValue) # description same as tag
                    if dimensions:
                        attribute.set_dimensions(dimensions)
                    atts[tag] = attribute
        return atts

    def argumentsTemplate(self):
        result = ''
        outputInfos = []
        inpAttInfos = []
        for argumentParseObject in self.argumentParseObjects():
            if argumentParseObject.isOutput:
                outputInfos.append(argumentParseObject)
            else:
                inpAttInfos.append(argumentParseObject)
        n = len(outputInfos)
        outputsTemplate = ""
        if n > 0:
            for i in range(n):
                outputsTemplate += '{O:' + outputInfos[i].name +'}'
                if i < n - 1:
                    outputsTemplate += ', '
        inputsTemplate = ""
        n = len(inpAttInfos)
        if n > 0:
            for i in range(n):
                IorA = 'I'
                if inpAttInfos[i].isConstant:
                    IorA = 'A'
                inputsTemplate += '{' + IorA + ':' + inpAttInfos[i].name + '}'
                if i < n - 1:
                    inputsTemplate += ', '
        callableType = self.callableType()
        if callableType == 'submodel':
            if outputsTemplate:
                result += outputsTemplate
                result += ' := '
            result += "{S}("  # always have brackets
            result += inputsTemplate
        elif callableType == 'segment': # segment invoked differently
            result += "{S}("  # always have brackets
            result += outputsTemplate
            if inputsTemplate:
                result += ' := '
                result += inputsTemplate
        elif callableType == 'function': # Do generically as for submodel
            if outputsTemplate:
                result += outputsTemplate
                result += ' := '
            result += "{S}("  # always have brackets
            result += inputsTemplate
        result += ');\n'
        return result
