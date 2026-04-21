#! /usr/bin/python

from .gensimulationentity import GenSimulationEntity
from ..esl.parsetf import ParseTF

class GenTransferFunction(GenSimulationEntity):

    def __init__(self, genDiagramInfo, objectId, appSimEntity):
        GenSimulationEntity.__init__(self, genDiagramInfo, objectId, appSimEntity)
        self._parseTF = None
        self.err = ""

    def generateEsl(self, coderegion):
        result = ""
        tf_differentialAttribute = self.appSimEntity().getAttribute('TF-differential')
        if tf_differentialAttribute and tf_differentialAttribute.valueStr().lower() == "false":
            result = super(GenTransferFunction, self).generateEsl(coderegion)
        else:
            if not self._parseTF:
                self._parseTF = ParseTF()
                self._parseTF.reverseOrder = True
                tfTxt = ""
                attTF = self.appSimEntity().getAttribute('TF')
                if attTF:
                    tfTxt = attTF.valueStr()
                initialisations = ""
                attICS = self.appSimEntity().getAttribute('ICS')
                if attICS:
                    initialisations = attICS.valueStr()
                    if not initialisations: # Can use a single real zero
                        initialisations = attICS.defaultValueStr()
                self.err = self._parseTF.setTF(tfTxt)
                if self.err:
                    pass
                    #### TODO what
                else:
                    self.err = self._parseTF.parse()
                    if self.err:
                        pass
                        #### TODO what
                    else:
                        self.err = self._parseTF.derive()
                        if self.err:
                            pass
                            #### TODO what
                        else:
                            info = self._parseTF.setInitialisations(initialisations)  # do this after derive so can get info
                            if info:
                                pass
                if self.err:
                    msg = "Problem converting Transfer Function-"+str(self.objectId())+" in "+self._appSimEntity.parent().parent().identification()+" to differential equations: "+self.err + '\n'
                    self._genDiagramInfo.module().generate().control().appendMessage(msg)
            if not self.err:
                result = self._parseTF.generateEsl(self, coderegion)
                result = self.substitute(result)
        return result
