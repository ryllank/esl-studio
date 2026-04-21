#! /usr/bin/python

from .. import utils as Utils
from .simulationentity import SimulationEntity
from ..esl.parsetf import ParseTF

class TransferFunction(SimulationEntity):

    def __init__(self, parent, type="", objectId=""):
        SimulationEntity.__init__(self, parent, type, objectId)
        # Note: Makes use of the following defined attributes:
        # - String attribute TF - transfer function in the ESL notation.
        # - String attribute ICS - One or more state variable initial conditions (not more than the number of states) - separated with commas.
        # - Boolean attribute TF-differential - checkbox to generate code for the Transfer Function as differential equations if "true", else generate as ESL TRANSFER statement.
        # Allow them to have annotations (including TF-differential).

    # def specialSaveXmlAttributes(self, indent=None, level=0, saveDefaults=False):

    #def specialSaveXmlContents(self, indent=None, level=0, saveDefaults=False):

    def checkTransferFunction(self, tfTxt):
        syntaxErrTxt = ""
        if self._specialType == "Transfer Function":
            ptf = ParseTF()
            syntaxErrTxt = ptf.setTF(tfTxt)
            if not syntaxErrTxt:
                syntaxErrTxt = ptf.parse()
        return syntaxErrTxt

    # def updateEntity(self, updateXmlElement):

    # def validateEntityPropertyChange(self, propertyTag, newValue, val_type, val_item):

    # def updateEntityProperty(self, propertyTag, newValue, suppress_action=False):

    def validateEntityAttributePropertyChange(self, propertyTag, newValue, attribute, val_type, val_item, val_oldValue, val_newValue):
        updatedPropertyValue = None
        valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue = super(TransferFunction, self).validateEntityAttributePropertyChange(
            propertyTag, newValue, attribute, val_type, val_item, val_oldValue, val_newValue)
        if valid:
            dummyAttribute = attribute.detachedCopy(attribute.parent())
            dummyAttribute.loadData(newValue)
            if propertyTag == "TF" and attribute.valueStr() != dummyAttribute.valueStr():
                syntaxErrTxt = self.checkTransferFunction(dummyAttribute.valueStr())
                if syntaxErrTxt:
                    # Treat as immediate message - not an error, so no rejection.
                    syntaxErrTxt = "TF syntax check (warning): " + syntaxErrTxt + "\n"
                    self._application.frame().control().appendMessage(syntaxErrTxt)
                    Utils.bleep()
        return valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue

    # def updateEntityAttributeProperty(self, propertyTag, newValue, attribute, tempOldAttribute, suppress_action=False):
