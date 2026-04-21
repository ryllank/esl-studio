#! /usr/bin/python

from collections import OrderedDict

from .. import utils as Utils
from .eslvalue import ESLValue

ApplicationDefaultSimulationParameters = OrderedDict(
    [
        ("TSTART", [ "Real", "0.0", 'Initial value of T at start of run' ]),
        ("TFIN", [ "Real", "10.0", 'Final value of T at end of run' ]),
        ("CINT", [ "Real", "1.0", 'Communication interval' ]),
        ("DISERR", [ "Real", "0.0001", 'Discontinuity detection error tolerance' ]),
        ("INTERR", [ "Real", "0.001", 'Integration error tolerance' ]),
        ("ALGO", [ "Integer", "1", 'Integration algorithm' ]),
        ("NSTEP", [ "Integer", "1", 'Number of integration steps in CINT' ])
    ])

ApplicationAlgoValues = OrderedDict(
    [
        ("8", "RK1" ),
        ("3", "RK2"),
        ("2", "RK4"),
        ("1", "RK5"),
        ("5", "GEAR1"),
        ("6", "GEAR2"),
        ("4", "STIFF2"),
        ("7", "ADAMS"),
        ("21", "LIN1"),
        ("22", "LIN2")
    ])

ApplicationAlgoOptionTexts = OrderedDict(
    [
        ("RK1 (Euler 1st order)", "8"),
        ("RK2 (Runge-Kutta 2nd order)", "3"),
        ("RK4 (Runge-Kutta 4th order)", "2"),
        ("RK5 (variable-step 5th order)", "1"),
        ("GEAR1 (Gear variable-step)", "5"),
        ("GEAR2 (Gear diagonal Jacobean)", "6"),
        ("STIFF2 (stiff 2nd order)", "4"),
        ("ADAMS (Adams predictor-corrector)", "7"),
        ("LIN1 (Newton-Raphson trim)", "21"),
        ("LIN2 (Simplex trim)", "22")
    ])

class SimulationParameter():
    def __init__(self, parent, eslname="", description="", datatype="", valueStr=""):
        self._parent = parent
        self._eslname = eslname
        self._description = description
        self._eslValue = ESLValue(self, datatype, "", valueStr)
        #self._variableId = 0
    def parent(self): return self._parent
    def eslname(self): return self._eslname
    def description(self): return self._description
    def datatype(self):
        return self._eslValue.datatype()
    def valueStr(self):
        return self._eslValue.valueStr()
    def eslValue(self):
        return self._eslValue
    def set_eslname(self, eslname):
        self._eslname = eslname
    def set_valueStr(self, valueStr):
        self._eslValue.set_valueStr(valueStr)

    def validateSimulationParameterPropertyChange(self, module, propertyTag, newValue, val_type, val_item) -> (bool, str, str, str, str):
        """ returns: valid:bool, rejection:str, val_type:str, val_item:str, updatedPropertyValue:str """
        #dummySimPar = SimulationParameter(None)
        #dummySimPar.loadData(newValue)
        dummyESLValue = self.eslValue().detachedCopy(None)
        dummyESLValue.loadStr(newValue, checkValidity=False)
        updatedPropertyValue = None
        valid, rejection, val_type, val_item, updatedESLValue = self._eslValue.validateESLValuePropertyChange(dummyESLValue, val_type, val_item)
        if valid:
            if updatedESLValue is not None:
                updatedPropertyValue = updatedESLValue.saveStr()
                self._eslValue.loadStr(updatedPropertyValue)
                ###self._parent.updateProperty(self)
        return valid, rejection, val_type, val_item, updatedPropertyValue

class SimulationParameters():
    def __init__(self, parent):
        self._parent = parent # model or segment
        self._application = parent.application()
        self._parameters = OrderedDict()
        for parESLName in ApplicationDefaultSimulationParameters:
            parInfo = ApplicationDefaultSimulationParameters[parESLName]
            simPar = SimulationParameter(self, parESLName, description=parInfo[2], datatype=parInfo[0], valueStr="")
            self._parameters[parESLName] = simPar
            simPar.eslValue().set_defaultValueStr(parInfo[1])

    def parameters(self):
        return self._parameters

    def defaultValue(self, simpartag):
        result = None
        if simpartag in ApplicationDefaultSimulationParameters:
            result = ApplicationDefaultSimulationParameters[simpartag][1]
        return result

    def load(self, modelXmlElement):
        simParView = self._application.frame().viewManager().simulationParametersView()
        simParsXmlElement = modelXmlElement.getXmlElementByName("simulation-parameters", False)
        if simParsXmlElement:
            simParXmlList = simParsXmlElement.getXmlElementListByName("parameter", False)
            for simParXmlElement in simParXmlList:
                simParEslname = simParXmlElement.getAttribute("eslname")
                simParESLValue = simParXmlElement.getAttribute("value")
                if simParEslname:
                    simPar = self._parameters[simParEslname]
                    simPar.eslValue().loadStr(simParESLValue)
        if self._parent == self._application.program().model():
            xpt = self._application.program().experiment()
            simParView.hideExperimentWarning(xpt == "")

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ''
        for simPar in list(self._parameters.values()):
            valueStr = simPar.valueStr()
            if valueStr or saveDefaults:
                result += ind2 + '<parameter eslname="'+simPar.eslname()+'" value="'+simPar.eslValue().saveStr()+'"/>' + nl
        if result or saveDefaults:
            result = ind + '<simulation-parameters>' + nl + result
            result += ind + '</simulation-parameters>' + nl
        return result
