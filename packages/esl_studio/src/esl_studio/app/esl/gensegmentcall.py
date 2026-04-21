#! /usr/bin/python

from .gencallentity import GenCallEntity
from .generate import nl, indent, indentate
from ..application.segmentcall import SegmentCall
from ..application.variable import Variable

class GenSegmentCall(GenCallEntity):

    def __init__(self, genDiagramInfo, objectId, appSimEntity):
        GenCallEntity.__init__(self, genDiagramInfo, objectId, appSimEntity)

    def generateSpecialSegmentCallAttributesEsl(self, coderegion):
        result = ""
        # Handle segment call output argument initial values
        for port in list(self._ports.values()):
            if port.direction() == "output":
                if coderegion == "declarations":  # segment call needs outputs initialisation variables declared and given initialisation
                    initVarName = port.eslname()+"_INIT"
                    datatype = port.datatype()
                    dimensions = port.dimensions()
                    value = ""
                    # First get any value from segment call's port's initial value property
                    if not value:
                        value = port.appPort().getInitialisationValue()     # Does not generate default value if not specified.
                    # Second get any value, for a call for a diagram Segment, from the Argument's initial value property
                    if not value and port.appPort().argument():
                        value = port.appPort().argument().getInitialisationValue() # Does generate default value if needed.
                    if not value:
                        value = port.appPort().getInitialisationValue(generateDefaultValue=True)
                    portDescription = ""
                    if port.appPort().description():
                        portDescription = " ("+port.appPort().description()+")"
                    description = "Initialisation for " + port.tag()+portDescription + " for " + self._appSimEntity.identification()

                    initVariable = Variable(None, initVarName, description, "false", "false", datatype, dimensions, value)
                    result += self._genDiagramInfo.generate().generateVariableDeclaration(initVariable) + "\n"
                    initVariable = None
                elif coderegion == "initial":
                    result += port.eslname() + " := " + port.eslname()+"_INIT" + ";\n"

        frequencyValue = self.appSimEntity().frequencyAttribute().valueStr()
        if coderegion == "declarations":
            if frequencyValue and frequencyValue != SegmentCall.Frequency_default:
                result += "-- Frequency counter for " + self._appSimEntity.identification() + "\n"
                result += "INTEGER: "+self.makeEslName("Frequency")+";\n"
                result += "INTEGER: "+self.makeEslName("Count")+";\n"
        if coderegion == "initial":
            if frequencyValue and frequencyValue != SegmentCall.Frequency_default:
                result += self.makeEslName("Frequency")+" := "+str(frequencyValue)+";\n"
                result += self.makeEslName("Count")+" := "+str(frequencyValue)+";\n"
        return result

    def generateSpecialSegmentCallInvocationEsl(self, coderegion):
        result = ""
        if coderegion == "communication":
            callStatement = ""
            if self._subprogram:
                callStatement = self._subprogram.argumentsTemplate()
            communicationCode = callStatement
            frequencyValue = self.appSimEntity().frequencyAttribute().valueStr()
            delayValue = self.appSimEntity().delayAttribute().valueStr()
            if frequencyValue and frequencyValue != SegmentCall.Frequency_default:
                frequencyCode = "IF "+self.makeEslName("Count")+" = "+self.makeEslName("Frequency")+" THEN\n"
                frequencyCode += indent + callStatement
                frequencyCode += indent + self.makeEslName("Count") + " := 0;\n"
                frequencyCode += "END_IF;\n"
                frequencyCode += self.makeEslName("Count") + " := " + self.makeEslName("Count") + " + 1;\n"
                communicationCode = frequencyCode
            if delayValue and delayValue != SegmentCall.Delay_default:
                delayCode = "IF T >= "+str(delayValue)+" THEN\n"
                delayCode += indentate(indent, communicationCode)
                delayCode += "END_IF;\n"
                communicationCode = delayCode
            result += communicationCode
        return result

    def generateEsl(self, coderegion):
        result = ""
        result += self.generateSpecialCallEntityEsl(coderegion)

        result += self.generateSpecialSegmentCallAttributesEsl(coderegion)

        result += self.generateAttributesEsl(coderegion)

        result += self.generateSpecialSegmentCallInvocationEsl(coderegion)

        if result:
            result = self.substitute(result)
        return result
