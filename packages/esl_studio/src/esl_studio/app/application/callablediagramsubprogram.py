#! /usr/bin/python

from collections import OrderedDict

from .. import utils as Utils
from .callablesubprogram import CallableSubprogram
from .port import Port
from .attribute import Attribute

class CallableDiagramSubprogram(CallableSubprogram): # mixin class for Submodel and Segment (which primarily inherit from ModelBase/Module)

    def __init__(self):
        CallableSubprogram.__init__(self, 'diagram') # has self._subprogramCalls
        # get self methods diagramInfo application moduleType from primary class of this - Submodel or Segment

    def set_diagramInfo(self, diagramInfo):
        if self._subprogramBaseType == 'diagram':
            self._diagramInfo = diagramInfo

    def getPorts(self, allowBlankTag=False):
        ports = OrderedDict()
        if self.diagramInfo():
            inputs = []
            outputs = []
            inputArgs = []
            outputArgs = []
            for entity in list(self.diagramInfo().simulationEntities().values()):
                entitytype = entity.type()
                argtype = None
                if entity.isInputArgument():
                    argtype = 'input'
                elif entity.isOutputArgument():
                    argtype = 'output'
                if argtype:
                    portInfoData = entity.getPortInfoData(allowBlankTag) # [datatype, description, tag, dimensions]
                    if portInfoData:
                        if argtype == 'input':
                            inputs.append(portInfoData)
                            inputArgs.append(entity)
                        else: #'output'
                            outputs.append(portInfoData)
                            outputArgs.append(entity)
            count = 1
            ix = 0
            for portinfo in inputs:
                id = str(count)
                datatype = portinfo[0]
                port = Port(None, id, datatype, 'input', description=portinfo[1], tag=portinfo[2], dimensions=portinfo[3])
                port.set_argument(inputArgs[ix])
                ix += 1
                ports[str(count)] = port
                count += 1
            ix = 0
            for portinfo in outputs:
                id = str(count)
                datatype = portinfo[0]
                port = Port(None, id, datatype, 'output', description=portinfo[1], tag=portinfo[2], dimensions=portinfo[3])
                port.set_argument(outputArgs[ix])
                ix += 1
                ports[str(count)] = port
                count += 1
        return ports

    def getAttributes(self):
        atts = OrderedDict()
        if self.diagramInfo():
            for entity in list(self.diagramInfo().simulationEntities().values()):
                if entity.isInputArgument():
                    attributeInfoData = entity.getAttributeInfoData()  # [datatype, description, tag, dimensions, defaultValue]
                    if attributeInfoData:
                        datatype = attributeInfoData[0]
                        description = attributeInfoData[1]
                        tag = attributeInfoData[2]
                        dimensions = attributeInfoData[3]
                        defaultvalue = attributeInfoData[4]
                        attribute = Attribute(None, tag, description, datatype=datatype, dimensions=dimensions, valueStr=defaultvalue)
                        atts[tag] = attribute
                        attribute.set_argument(entity)
        return atts

    def argumentsTemplate(self):
        result = ""
        callableType = self.callableType()
        if callableType == "submodel":
            result += "{O* := }{S}({I*}{A*});\n"
        elif callableType == "segment":  # segment invoked differently
            hasInputs = False
            for entity in list(self._diagramInfo.simulationEntities().values()):
                if entity.isInputArgument():
                    hasInputs = True
                    break
            result += "{S}({O*}"
            if hasInputs:
                result += " := "
            result += "{I*}{A*});\n"
        return result
