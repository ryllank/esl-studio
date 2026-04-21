#! /usr/bin/python

from collections import OrderedDict

from .callablecodesubprogram import CallableCodeSubprogram
from .eslblocknames import EslBlockNames
from .variable import Variable

class CodeSubprogram(CallableCodeSubprogram):

    def __init__(self, code, subprogramParseObject):
        CallableCodeSubprogram.__init__(self)
        self._code = code
        self._subprogramParseObject = subprogramParseObject

        self._errors = []       #### any that are found *after* parsing
        # To support code package
        self._blockNames = EslBlockNames() # for module name, parameters of submodels(diagram) and variables of packages, port attribute names, etc
        self._variables = OrderedDict()
        self._usingModules = [] # model or submodels that import/use this package
        if self._subprogramParseObject.subprogramType() == "package":
            self.setupPackageVariables()

    def code(self):
        return self._code

    def errors(self):
        return self._errors
    def subprogramType(self):
        return self._subprogramParseObject.subprogramType()
    def eslname(self):
        return self._subprogramParseObject.name
    def position(self):
        return self._subprogramParseObject.startPos
    def argumentParseObjects(self):
        return self._subprogramParseObject.signatureParseObject.argumentParseObjects
    def returnType(self):
        result = ""
        if self._subprogramParseObject.signatureParseObject:
            result = self._subprogramParseObject.signatureParseObject.returnType
        return result
    def libraryList(self):
        return self._code.libraryList()
    def valid(self):
        valid = self._valid and len(self._subprogramParseObject.messages) == 0 and len(self._errors) == 0
        return valid

    # To support CodeSubProgram "package"
    def setupPackageVariables(self):
        for variableParseObject in self._subprogramParseObject.packageVariables:
            eslname = variableParseObject.name
            datatype = variableParseObject.datatype.title()
            description = "" # always
            initialValue = ""
            if variableParseObject.initialValue is not None:
                initialValue = variableParseObject.initialValue
            constant = "true" if variableParseObject.isConstant else "false"
            parameter = "true" if variableParseObject.isParameter else "false"
            dimensions = ""
            if variableParseObject.dimensionality:
                dimensions = variableParseObject.dimensionality.dimensions()
            variable = Variable(self, eslname, description, constant, parameter, datatype, dimensions, initialValue)
            self._variables[eslname] = variable
            self._blockNames.add(eslname, variable)

    def variables(self):
        return self._variables

    def blockNames(self):
        return self._blockNames

    def usingModules(self):
        return self._usingModules

    def hasVariableInUse(self):
        inUse = False
        for var in list(self._variables.values()):
            if len(var.assignedAttributes()) > 0:
                inUse = True
                break
        return inUse
