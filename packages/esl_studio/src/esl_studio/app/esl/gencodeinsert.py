#! /usr/bin/python

from .gensimulationentity import GenSimulationEntity

class GenCodeInsert(GenSimulationEntity):

    def __init__(self, genDiagramInfo, objectId, appSimEntity):
        GenSimulationEntity.__init__(self, genDiagramInfo, objectId, appSimEntity)
        self._insert_position = self._appSimEntity.insert_position()

    def generateEslPositioned(self, coderegion, position):  # override for simulation entities that support positioned code generation
        # coderegion : "declarations" "initial" "dynamic" "step" "communication" + "terminal" "analysis"
        # position: "beginning" "end"
        result = ""
        if position == self._insert_position and coderegion == self._appSimEntity.region():
            result += self._appSimEntity.esl()
            if not result.endswith("\n"):
                result += "\n"
        return result
