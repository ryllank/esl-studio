#! /usr/bin/python

from .gencallentity import GenCallEntity

class GenSubmodelCall(GenCallEntity):

    def __init__(self, genDiagramInfo, objectId, appSimEntity):
        GenCallEntity.__init__(self, genDiagramInfo, objectId, appSimEntity)

    def generateEsl(self, coderegion):
        result = ""
        result += self.generateSpecialCallEntityEsl(coderegion)

        result += self.generateAttributesEsl(coderegion)

        if coderegion == "dynamic" and self._subprogram:
            result += self._subprogram.argumentsTemplate()

        if result:
            result = self.substitute(result)
        return result
