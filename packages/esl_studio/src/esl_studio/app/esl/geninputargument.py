#! /usr/bin/python

from .gensimulationentity import GenSimulationEntity
from .generate import eslDatatype

class GenInputArgument(GenSimulationEntity):

    def __init__(self, genDiagramInfo, objectId, appSimEntity):
        GenSimulationEntity.__init__(self, genDiagramInfo, objectId, appSimEntity)

    def generateInputArgument(self, index, constant):
        result = ""
        const = 'false'
        attrtag = self.appSimEntity().attributes().get('ATTR') # A boolean attribute ATTR says whether this is for a CONSTANT input or not
        if attrtag: const = attrtag.valueStr().lower()
        if (constant and const == 'true') or (not constant and const != 'true'):
            if constant:
                result += "CONSTANT "
            argName = self.appSimEntity().getArgName()
            for genPort in list(self.ports().values()):
                if genPort.direction() == "output":
                    result += eslDatatype(genPort.datatype()) + ': ' + argName
                    if genPort.dimensions():
                        result += "("+genPort.dimensions()+")"
                    break
        return result

    def generateSpecialInputArgumentEsl(self, coderegion):
        result = ""
        # For coderegion "include" uses normal port variable declaration (generateESLDeclaration).
        if coderegion == "dynamic":
            inputPortName = ""                  # This is equivalent to {O:y} in template.
            for genPort in list(self.ports().values()):
                if genPort.direction() == "output":
                    inputPortName = genPort.eslname()
                    break
            if inputPortName:
                inputArgName = self.appSimEntity().getArgName()
                if inputArgName:
                    result = inputPortName+" := "+inputArgName+";\n"
        return result

    def generateEsl(self, coderegion):
        result = ""
        result += self.generateSpecialInputArgumentEsl(coderegion)

        if self._entityModelXmlElement:
            result += self.generateDefinitionModelTemplate(coderegion)

        if result:
            result = self.substitute(result)
        return result
