#! /usr/bin/python

from collections import OrderedDict

from ..esl import esl
from .eslblocknames import EslBlockNames

class Module(object):
    def __init__(self, application, moduleId, moduleType):
        self._moduleId = 0
        self._application = application
        self._moduleId = moduleId
        self._moduleType = moduleType                   # 'program' 'model' 'submodel' 'segment 'package' 'setup-info' 'code'
        if self._application:
            self._application.addModule(self)
        self._eslname = ''
        self._description = ''
        self._allocatedVariableNr = 0   # id of variables (as name may be changed)
        self._blockNames = EslBlockNames() # for module name, parameters of submodels(diagram) and variables of packages, port attribute names, etc
        self._variables = OrderedDict()

    def moduleId(self):
        return self._moduleId
    def set_moduleId(self, moduleId):
        self._moduleId = moduleId

    def moduleType(self):
        return self._moduleType

    def application(self):
        return self._application

    def eslname(self):
        return self._eslname
    def set_eslname(self, eslname):
        self._eslname = eslname

    def identification(self, showSubType=False): # override for nicer presentation
        result = self._moduleType.title()
        if self._eslname:
            result += " " + self._eslname
        return result

    def description(self):
        return self._description
    def set_description(self, description):
        self._description = description

    def variables(self):
        return self._variables

    def blockNames(self):
        return self._blockNames

    def addVariable(self, variable):
        variableId = variable.variableId()
        if variableId > 0 and variableId in self._variables:
            raise Exception('Variable being added has an allocated variableId')
        eslname = variable.eslname()
        nameAlreadyInModule = self._blockNames.isin(eslname)
        if nameAlreadyInModule:
            raise Exception('Duplicate name "'+eslname+'" in application')
        else:
            self._blockNames.add(eslname, variable)
            if variableId == 0:
                self._allocatedVariableNr += 1
                variableId = self._allocatedVariableNr
            variable.set_variableId(variableId)
            self._variables[variableId] = variable

    def removeVariable(self, variable):
        self._blockNames.delete(variable.eslname())
        del self._variables[variable.variableId()]
        variable.set_variableId(0)

    def getVariableById(self, variableId):
        variable = None
        for item in list(self._variables.values()):
            if item.variableId() == variableId:
                variable = item
                break
        return variable

    def validateModulePropertyChange(self, propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue):
        valid = True
        rejection = ""
        module = self
        if self._moduleType == 'program':
            module = self._model
        if propertyTag == 'eslname':
            val_item = module.eslname() + ".ESL Name"
            errTxt = esl.ValidateName(newValue, silent=True)
            if errTxt:
                rejection = "not a valid ESL name - " + errTxt
                valid = False
            elif self._application.blockNames().isin(newValue):
                rejection = "name \""+newValue+"\" is already in the application"
                valid = False
            elif self._application.checkIsinFullLibraryList(newValue):
                rejection = "name \""+newValue+"\" is in use as a library subprogram"
                valid = False
            elif module.blockNames().isin(newValue):
                rejection = "name \""+newValue+"\" is in use in the "+module.moduleType()
                valid = False

            if module.moduleType() == 'submodel' or  module.moduleType() == 'segment':
                if module.checkNameIsInCalledModule(newValue):
                    rejection = "name \""+newValue+"\" is in use in a module in which the "+module.moduleType()+" is called"
                    valid = False

            if module.moduleType() == 'package':
                if module.eslnameIsInUse(newValue):
                    rejection = "name \""+newValue+"\" is already in a module which is using the package"
                    valid = False

        elif propertyTag == 'packages':
            errTxt = module.okToImportPackages(newValue)
            if errTxt:
                rejection = errTxt
                valid = False

        elif propertyTag == 'experiment':
            program = None
            if self._moduleType != 'program':
                if self._application.program().model() == self:
                    program = self._application.program()
            else:
                program = self
            if program and program.programType() != 'study':
                rejection = "experiment is only valid for a STUDY Program"
                if val_oldValue == "":
                    val_oldValue = "<default experiment>"
                else:
                    items = val_oldValue.split("\n")
                    val_oldValue = ""
                    for item in items:
                        if item:
                            val_oldValue = item
                            break
                    if val_oldValue: val_oldValue += "..."
                if val_newValue == "":
                    val_newValue = "<default experiment>"
                else:
                    items = val_newValue.split("\n")
                    val_newValue = ""
                    for item in items:
                        if item:
                            val_newValue = item
                            break
                    if val_newValue: val_newValue += "..."
                valid = False

        # Note: For moduleType 'code' - validate code subprograms is handled directly in PropertiesControl.validatePropertyChange
        # (because it may give a warning msg, and also may explicitly require to restorePropertiesView after this)
        return valid, rejection, val_type, val_item, val_oldValue, val_newValue
