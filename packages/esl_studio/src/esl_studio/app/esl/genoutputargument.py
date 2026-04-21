#! /usr/bin/python

from .gensimulationentity import GenSimulationEntity
from .generate import eslDatatype

class GenOutputArgument(GenSimulationEntity):

    def __init__(self, genDiagramInfo, objectId, appSimEntity):
        GenSimulationEntity.__init__(self, genDiagramInfo, objectId, appSimEntity)

    def generateOutputArgument(self, index):
        result = ""
        argName = self.appSimEntity().getArgName()
        for genPort in list(self.ports().values()):
            if genPort.direction() == "input":
                result += eslDatatype(genPort.datatype()) + ': ' + argName
                if genPort.dimensions():
                    result += "(" + genPort.dimensions() + ")"
                break
        return result

    def generateSpecialOutputArgumentEsl(self, coderegion):
        result = ""
        if coderegion == "declarations":
            for tag, attribute in self.appSimEntity().attributes().items():
                if tag != "INIT":
                    result += self.generateAttributeEsl(coderegion, attribute)
        else:
            result += self.generateAttributesEsl(coderegion)
        return result

    def generateEsl(self, coderegion):
        result = ""
        result += self.generateSpecialOutputArgumentEsl(coderegion)

        if self._entityModelXmlElement:
            result += self.generateDefinitionModelTemplate(coderegion)

        if result:
            result = self.substitute(result)
        return result

    def substitute(self, eslStr):
        if (eslStr.find("{N}") != -1): # {N} is the eslname of an output argument
            argName = self.appSimEntity().getArgName()
            subst = "{N}"
            value = argName
            eslStr = eslStr.replace(subst, value)

        eslStr = super(GenOutputArgument, self).substitute(eslStr)
        return eslStr
