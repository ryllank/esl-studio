#! /usr/bin/python

from .. import utils as Utils
from ..application.simulationparameters import ApplicationAlgoValues
from .generate import nl, indentate, indent
from .gendiagraminfo import GenDiagramInfo
from .lexer import inclusionStartString, inclusionEndString

class GenModule(object):
    def __init__(self, generate, appModule, subType):
        self._generate = generate
        self._appModule = appModule
        self._subType = subType
        self._generate.genModules()[appModule] = self
        self._genDiagramInfo = None

    def setupGenModule(self):
        if self._subType != 'code' and self._subType != 'package':    # diagram modules need addition information gathered from the diagram-info
            self._genDiagramInfo = self.gatherDiagramInfo(self._appModule.diagramInfo())
        self._rank = 0 # used when do GenOrder establishOrder

    def generate(self):
        return self._generate
    def appModule(self):
        return self._appModule
    def subType(self):
        return self._subType
    def genDiagramInfo(self):
        return self._genDiagramInfo
    def eslname(self):
        return self._appModule.eslname()
    def identification(self):
        if self._subType == 'code':
            identification = self._appModule.identification(showSubType=True)
        else:
            identification = self._appModule.identification()
        return identification

    def calledModules(self):
        calledGenModules = []
        application = self._generate.application()
        if self._subType != 'code' and self._genDiagramInfo:
            calledAppSubprograms = self._genDiagramInfo.calledAppSubprograms()
            for appSubprogram in calledAppSubprograms:
                appModule = appSubprogram
                if appSubprogram.subprogramBaseType() == 'code':
                    appModule = appSubprogram.code()
                genModule = self._generate.genModules().get(appModule)
                if genModule and genModule not in calledGenModules:
                    calledGenModules.append(genModule)
            for importedPackageName in self._genDiagramInfo.importedPackageNames():
                appPackage = application.getPackageByName(importedPackageName)
                if appPackage.subprogramBaseType() == 'code': # can disregard "diagram" packages
                    appModule = appPackage.code()
                    genModule = self._generate.genModules().get(appModule)
                    if genModule and genModule not in calledGenModules:
                        calledGenModules.append(genModule)
        elif self._subType == 'code':
            calledAppSubprogramNames = self._appModule.libraryList() + self._appModule.calledSubprogramNames() + self._appModule.importedPackageNames()
            for entry in calledAppSubprogramNames:
                name = Utils.libraryBaseName(entry)
                appSubprogram = None
                if name:
                    appSubprogram = application.blockNames().get(name)
                if appSubprogram:  # subprogram entered in application scope
                    if appSubprogram.subprogramBaseType() == 'code' or appSubprogram.moduleType() != 'package': # can disregard "diagram" packages
                        appModule = appSubprogram
                        if appSubprogram.subprogramBaseType() == 'code':
                            appModule = appSubprogram.code()
                        if appModule != self._appModule: # prune any subprograms in this Code that may have been named in lib-list by mistake, or packages USEed by subprograms in same Code import.
                            genModule = self._generate.genModules().get(appModule)
                            if genModule and genModule not in calledGenModules:
                                calledGenModules.append(genModule)
        return calledGenModules
    def rank(self):
        return self._rank
    def set_rank(self, rank):
        self._rank = rank

    def gatherDiagramInfo(self, appDiagramInfo):
        result = GenDiagramInfo(self, appDiagramInfo)
        result.gather()
        result.setupArguments()
        result.gatherForPorts()
        result.setupCallSubprograms()
        result.setupLibraryList()
        result.gatherForResolvePortDimensions()
        return result

    def preloadedSubprograms(self):
        result = []
        if self._genDiagramInfo:
            result = self._genDiagramInfo.preloadedSubprograms()
        return result

    def libraryList(self):
        result = []
        if self._genDiagramInfo:
            result = self._genDiagramInfo.libraryList()
        else:
            result = self._appModule.libraryList()
        return result

    def generateCodeInsert(self, runDirect):
        eslStr = ''
        moduleType = self._appModule.moduleType()
        if moduleType in ['model', 'submodel', 'segment']:
            if self._genDiagramInfo:
                if moduleType == 'model':
                    modelType = self._appModule.modelType()
                    if modelType == "model":
                        eslStr += "MODEL "
                    else:
                        eslStr += "SEGMENT "
                elif moduleType == "segment":
                    eslStr += "SEGMENT "
                else:
                    eslStr += "SUBMODEL "
                eslStr += self._appModule.eslname()
                eslStr += self._genDiagramInfo.generateCodeInsertArguments()
                if self._appModule.moduleType() == 'segment' and self._appModule.segmentType() == "external-segment":
                    eslStr += " EXTERNAL"
                eslStr += ';'
                eslStr += nl
                if self._appModule.description():
                    eslStr += "-- Description: " + self._appModule.description() + nl

                # simulation parameters
                simParStr = ""
                if moduleType in ['model', 'segment']:
                    simParStr = self.generateSimulationParameterValues()
                eslStr += self._genDiagramInfo.generateCodeInsert(runDirect, simParStr)
        else:   # Code
            if self._appModule.moduleType() == 'code':
                codeType = self._appModule.codeType()
                if codeType == 'file':
                    filepath = self._appModule.file()
                    if not filepath:
                        eslStr += inclusionStartString+'Code('+codeType+') has no file specified'+inclusionEndString
                    else:
                        eslStr += "INCLUDE \"" + Utils.disEnvVarPath(self._appModule.file()) + "\";\n"
                elif not self._appModule.eslText():
                    eslStr += inclusionStartString+'Code('+codeType+') has no text set'+inclusionEndString
                else:
                    eslStr += self._appModule.eslText()
                if eslStr and eslStr[len(eslStr) - 1] != "\n":
                    eslStr += nl
            elif self._appModule.moduleType() == 'package':
                eslStr += 'PACKAGE '
                eslStr += self._appModule.eslname()
                eslStr += ';'
                eslStr += nl
                if self._appModule.description():
                    eslStr += "-- Description: " + self._appModule.description() + nl
                declarations = ""
                for appVariable in list(self._appModule.variables().values()):
                    declarations += self._generate.generateVariableDeclaration(appVariable) + nl
                eslStr += indentate(indent, declarations)
                eslStr += 'END ' + self._appModule.eslname() + ';' + nl
        return eslStr

    def generateSimulationParameterValues(self):
        result = ''
        for simPar in list(self._appModule.simulationParameters().parameters().values()):
            simParTag = simPar.eslname()
            valueStr = simPar.valueStr()
            if valueStr:
                if simParTag == "ALGO":
                    result += simParTag +' := ' + ApplicationAlgoValues[valueStr] + ';' + nl
                else:
                    result += simParTag +' := ' + valueStr + ';' + nl
        return result
