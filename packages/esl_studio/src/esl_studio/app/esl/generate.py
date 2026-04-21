#! /usr/bin/python

import time

from .. import utils as Utils
from ..general import APP_NAME, APPLICATION_VERSION_STRING
from ..esl import parseesl, esl

from .genprogram import GenProgram
from .genorder import GenOrder

nl = '\n'
indent = '  '

MAX_LINE_LEN = 132

def indentate(indentation, multiline):
    ends_with_nl = False
    if len(multiline) > 1 and multiline[-1] == nl and multiline[-2] != nl:
        ends_with_nl = True
    result = ""
    lines = multiline.split(nl)
    if ends_with_nl:
        lines = lines[:-1]
    for line in lines:
        if line:
            result += indentation + line + nl
        else: # blank line
            result += nl
    return result

def eslDatatype(datatype):
    result = ''
    datatypeUpper = datatype.upper()
    if datatypeUpper in esl.EslTypeNames:
        result = datatypeUpper
    return result

from .genmodule import GenModule

def breakLongLines(text, limit = MAX_LINE_LEN):
    newlines = []
    lines = text.splitlines()
    for line in lines:
        if len(line) <= limit:
            newlines.append(line)
        else:
            part = line[:]
            while len(part) > limit:
                poscomment = part.find('--')
                if poscomment == -1 or poscomment > limit:
                    poscomma = part.rfind(',', 0, limit)
                    posblank = part.rfind(' ', 0, limit)
                    if poscomma > posblank:
                        newlines.append(part[0:poscomma + 1])
                        part = part[poscomma + 1:]
                    elif posblank > poscomma:
                        newlines.append(part[0:posblank + 1])
                        part = part[posblank + 1:]
                else:
                    break
            if len(part) > 0:
                newlines.append(part)
    result = '\n'.join(newlines)
    return result

class Generate(object):

    def __init__(self, control):
        self._parseEsl = parseesl.ParseEsl()
        self._control = control
        self._genOrder = GenOrder(self)
        self._appProgram = None
        self._genModules = {}
        self._genModel = None
        self._genPackages = []
        self._genSubmodels = []
        self._genSegments = []
        self._genCodes = []
        self.debugging = True #False # Set True for print output

    def control(self):
        return self._control
    def appProgram(self):
        return self._appProgram
    def genModules(self):
        return self._genModules
    def genModels(self):
        return self._genModels
    def genPackages(self):
        return self._genPackages
    def genSubmodels(self):
        return self._genSubmodels
    def genSegments(self):
        return self._genSegments
    def genCodes(self):
        return self._genCodes

    def entities(self):
        return self._control.entities()
    def application(self):
        return self._control.frame().application()
    def parseEsl(self):
        return self._parseEsl

    def setup(self):
        pass

    def refresh(self):
        self._appProgram = self.application().program()
        self._genProgram = GenProgram(self, self._appProgram)
        self._genModules = {}
        self._genModels = []
        self._genPackages = []
        self._genSubmodels = []
        self._genSegments = []
        self._genCodes = []
        for appModel in list(self.application().models().values()):
            genModel = GenModule(self, appModel, 'model')
            self._genModels.append(genModel)
        for appPackage in list(self.application().packages().values()):
            genPackage = GenModule(self, appPackage, 'package')
            self._genPackages.append(genPackage)
        for appSubmodel in list(self.application().submodels().values()):
            genSubmodel = GenModule(self, appSubmodel, 'submodel')
            self._genSubmodels.append(genSubmodel)
        for appSegment in list(self.application().segments().values()):
            genSegment = GenModule(self, appSegment, 'segment')
            self._genSegments.append(genSegment)
        for appCode in list(self.application().codes().values()):
            genCode = GenModule(self, appCode, 'code')
            self._genCodes.append(genCode)

        self._genProgram.setupProgram()
        for genModel in self._genModels:
            genModel.setupGenModule()
        for genPackage in self._genPackages:
            genPackage.setupGenModule()
        for genSubmodel in self._genSubmodels:
            genSubmodel.setupGenModule()
        for genSegment in self._genSegments:
            genSegment.setupGenModule()
        for genCode in self._genCodes:
            genCode.setupGenModule()

    def GenerateESL(self, runDirect):
        result = ""
        now = time.localtime()

        self.refresh()

        errMsg = self._genOrder.establishOrder()

        if not errMsg:

            if len(self._genOrder.unusedApplicationModules()):
                msg = "The following application subprograms are not called (code not generated):\n"
                for m in self._genOrder.unusedApplicationModules():
                    msg += "  " + str(m.identification()) + "\n"
                msg += "\n"
                self._control.appendMessage(msg)

            nowstr = time.strftime("%Y-%m-%d %H:%M:%S", now)
            result = '-- Created by ' + APP_NAME + ' v'+APPLICATION_VERSION_STRING + ' on ' + nowstr + '\n'

            result += self.generateProgram(runDirect)

            result = breakLongLines(result)
        return result, errMsg

    def generateProgram(self, runDirect):
        eslStr = ''
        programType = self._appProgram.programType()
        if programType == 'study':
            eslStr += "STUDY" + nl
        elif programType == 'embedded-segment':
            eslStr += "EMBEDDED" + nl
        elif programType == 'remote-segment':
            eslStr += "REMOTE" + nl
        if self._appProgram.name():
            eslStr += "-- Name: " + self._appProgram.name() + nl
        if self._appProgram.description():
            eslStr += "-- Description: " + self._appProgram.description() + nl
        eslStr += nl

        # Generate ESL for packages (Reserved wont).
        if len(self._genPackages) > 0:
            eslStr += "-- Packages\n"
            for genPackage in self._genPackages:
                eslStr += genPackage.generateCodeInsert(runDirect)
                eslStr += nl

        # Library lib in used subs (assumed independent of application subs).
        valid = True
        libraryList = []
        genMainModel = self._genProgram.genModel()
        if genMainModel:
            Utils.extendNew(libraryList, genMainModel.libraryList())
        for genModel in self._genModels:
            if genModel != genMainModel:
                Utils.extendNew(libraryList, genModel.libraryList())
        for genSubprogram in self._genOrder.orderedUsedApplicationModules():
            Utils.extendNew(libraryList, genSubprogram.libraryList())
        if len(libraryList) > 0:
            # Remove any application submodels
            newLibList = []
            for lib in libraryList:
                libName = Utils.libraryBaseName(lib)
                application = self.application()
                #### TODO we now assume only if not in application scope is it deemed a lib (other things in scope are considered application or preloaded)
                if not application.blockNames().isin(libName):
                    newLibList.append(lib)
            libraryList = newLibList
        if len(libraryList) > 0:
            eslStr += "-- LIBRARY submodels\n"
            for lib in libraryList:
                lib = Utils.disEnvVarPath(lib)
                if not lib[0] == '"':
                    lib = '"' + lib + '"'
                eslStr += "INCLUDE " + lib + ";" + nl
            eslStr += nl

        # Preloaded subs (assumed independent of application subs).
        preloadedSubprograms = []                                   #### TODO reconsider preloaded subprograms
        for genSubprogram in self._genModels + self._genSubmodels + self._genSegments:
            for preloadedSubprogram in genSubprogram.preloadedSubprograms():
                if preloadedSubprogram not in preloadedSubprograms:
                    preloadedSubprograms.append(preloadedSubprogram)
        if len(preloadedSubprograms) > 0:
            eslStr += "-- Preloaded subprograms\n"
            for appSubprogram in preloadedSubprograms:
                genSubprogram = GenModule(self, appSubprogram)
                eslStr += genSubprogram.generateCodeInsert(runDirect)
                eslStr += nl

        # Application subprograms (ordered).
        if len(self._genOrder.orderedUsedApplicationModules()) > 0:
            eslStr += "-- Application subprograms\n"
            for genSubprogram in self._genOrder.orderedUsedApplicationModules():
                eslStr += genSubprogram.generateCodeInsert(runDirect)
                eslStr += nl

        if genMainModel:
            eslStr += "-- Main module\n"
            eslStr += genMainModel.generateCodeInsert(runDirect)
            eslStr += nl
        nr = 2
        for genModel in self._genModels:
            if genModel != genMainModel:
                eslStr += "-- Model "+str(nr) + nl
                eslStr += genModel.generateCodeInsert(runDirect)
                eslStr += nl
                nr += 1

        if programType == "study":
            eslStr += "-- Experiment" + nl
            xpt = self._appProgram.experiment()
            if xpt:
                eslStr += xpt
            else:
                eslStr += self.generateESLExperiment()
            eslStr += "END_STUDY" + nl
        eslStr += nl
        return eslStr

    def generateESLExperiment(self):
        result = ""
        # declare IO variables
        applicationScope = self.application().blockNames()
        genMainModel = self._genProgram.genModel()
        orderedModels = []
        if genMainModel:
            orderedModels.append(genMainModel)
        for genModel in self._genModels:
            if genModel != genMainModel:
                orderedModels.append(genModel)
        model_inputs = []
        model_outputs = []
        experimentAddedNames = []
        for genModel in orderedModels:
            inputs = []
            outputs = []
            # First do all declarations for the experiment (all models)
            for genSimEntity in list(genModel.genDiagramInfo().simulationEntities().values()):
                if genSimEntity.isInputArgument():
                    eslname = genSimEntity.appSimEntity().getArgName()
                    if applicationScope.isin(eslname):
                        eslname = applicationScope.getUnusedName(eslname)
                    applicationScope.add(eslname, "FAUX-BLOCK")
                    experimentAddedNames.append(eslname)
                    datatype,dimensions = genSimEntity.appSimEntity().getDatatypeAndDimensions()
                    inputs.append(eslname)
                    result += eslDatatype(datatype) + ': ' + eslname+dimensions + ';' + nl
                if genSimEntity.isOutputArgument():
                    eslname = genSimEntity.appSimEntity().getArgName()
                    if applicationScope.isin(eslname):
                        eslname = applicationScope.getUnusedName(eslname)
                    applicationScope.add(eslname, "FAUX-BLOCK")
                    experimentAddedNames.append(eslname)
                    datatype, dimensions = genSimEntity.appSimEntity().getDatatypeAndDimensions()
                    outputs.append(eslname)
                    result += eslDatatype(datatype) + ': ' + eslname+dimensions + ';' + nl

            model_inputs.append(inputs)
            model_outputs.append(outputs)
            if len(inputs) > 0 or len(outputs) > 0:
                result += nl

        for exptAddedName in experimentAddedNames:
            applicationScope.delete(exptAddedName)

        # Now do the models' experiment procedural code
        for i in range(len(model_inputs)):
            inputs = model_inputs[i]
            outputs = model_outputs[i]
            # input inputs
            if len(inputs) > 0:
                for i in range(len(inputs)):
                    result +=  'READ '+inputs[i]+';'+nl
                result += nl
            #  provide model call
            genModel = orderedModels[i]
            result += genModel.eslname()
            if len(inputs) > 0 or len(outputs) > 0:
                result += '('
                if len(outputs) > 0:
                    for i in range(len(outputs)):
                        n = i+1
                        result += outputs[i]
                        if n < len(outputs): result += ', '
                if len(inputs) > 0:
                    result += ' := '
                    for i in range(len(inputs)):
                        n = i+1
                        result += inputs[i]
                        if n < len(inputs): result += ', '
                result += ')'
            result += ";" + nl + nl
            # print outputs
            if len(outputs) > 0:
                for i in range(len(outputs)):
                    result +=  'PRINT "'+outputs[i]+'=", '+outputs[i]+';'+nl
            if len(inputs) > 0 or len(outputs) > 0:
                result += nl
        return result

    def generateVariableDeclaration(self, appVariable, doDescription=True): # Note: does not end with newline (so can be used in VariableProperty).
        result = ''
        if doDescription:
            if appVariable.description():
                result += '-- ' + appVariable.description() + nl
        if appVariable.parameter() == 'true':
            result += 'PARAMETER '
        if appVariable.constant() == 'true':
            result += 'CONSTANT '
        datatype = appVariable.datatype()
        if not datatype: datatype = 'Real'
        result += eslDatatype(datatype)
        result += ': '
        result += appVariable.eslname()
        dimensions = appVariable.dimensions()
        pos, dimensionality = self._parseEsl.parseDimensions(dimensions)
        if dimensions:
            result += '(' + dimensions + ')'
        value = appVariable.getInitialisationValue()
        result += value
        result += ';'
        return result
