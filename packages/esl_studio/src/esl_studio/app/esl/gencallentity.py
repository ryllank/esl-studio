#! /usr/bin/python

from .. import utils as Utils
from .gensimulationentity import GenSimulationEntity

class GenCallEntity(GenSimulationEntity):

    def __init__(self, genDiagramInfo, objectId, appSimEntity):
        GenSimulationEntity.__init__(self, genDiagramInfo, objectId, appSimEntity)
        self._submodel = None

    def subprogram(self):
        return self._subprogram

    def setupCallSubprogram(self):
        isPreloaded = None
        self._subprogram = None
        entityModelType = self._appSimEntity.entityModelType()      #### TODO this refers to the entity definition <module type - reconsider with preloaded subprograms
        if entityModelType == "ESL-submodel" or entityModelType == "file-submodel":
            subprogramName = self._entityModelXmlElement.getAttribute("submodel") ####TODO preloaded ??subprogram
            self._subprogram = self._genDiagramInfo.generate().entities().getPreloadedSubprogram(subprogramName)
            isPreloaded = True
        else: #### was if modelType == "submodel":
            self._subprogram = self._appSimEntity.subprogram()
            isPreloaded = False
        return isPreloaded

    def generateSpecialCallEntityEsl(self, coderegion):
        result = ""
        if self._subprogram:
            if coderegion == "include":
                liblst = []
                if self._subprogram.subprogramBaseType() == 'code':
                    Utils.extendNew(liblst, self._subprogram.libraryList())
                if len(liblst) > 0:
                    result = ", ".join(liblst)
        return result

    def substitute(self, eslStr):
        if (eslStr.find("{S}") != -1): # {S} is the eslname of the subprogram of the subprogram call
            if self.subprogram():
                subprogramName = self.subprogram().eslname()
                subst = "{S}"
                value = subprogramName
                eslStr = eslStr.replace(subst, value)

        eslStr = super(GenCallEntity, self).substitute(eslStr)
        return eslStr
