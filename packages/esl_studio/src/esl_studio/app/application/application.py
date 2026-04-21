#! /usr/bin/python

import os
import time

from collections import OrderedDict

import esl_diagram.xmlutil as xut

from ..general import APP_NAME, APPLICATION_VERSION_STRING, COMPATIBILITY_1_VERSION_STRING
from ..config import Config
from .. import utils as Utils
from . import diagramactions as dgAction
from .applicationtypes import CALLABLEMODULETYPES
from .setupinfo import SetupInfo
from .eslblocknames import EslBlockNames
from .program import Program
from .model import Model
from .package import Package
from .submodel import Submodel
from .callablesubprogram import CallableSubprogram
from .segment import Segment
from .code import Code
from .diagraminfo import DiagramInfo
from .displaydefinition import DisplayNames
from .simulationentity import SimulationEntity
from .transferfunction import TransferFunction
from .submodelcall import SubmodelCall
from .segmentcall import SegmentCall
from .functioncall import FunctionCall
from .inputargument import InputArgument
from .outputargument import OutputArgument
from .codeinsert import CodeInsert
from .constantinput import ConstantInput
from .arrayoperatorentity import ArrayOperatorEntity

class Application(object):

    _allocatedModuleNr = 0

    def __init__(self, frame):
        self._frame = frame
        self._filepath = ""
        self._xmlapplication = None
        self._version = ""
        self._compatibility = 0

    def frame(self): return self._frame

    def filepath(self): return self._filepath
    def xml(self): return self._xmlapplication
    def version(self): return self._version
    def compatibility(self): return self._compatibility

    def clearApplication(self):
        Application._allocatedModuleNr = 100
        self._modules = OrderedDict()
        self._blockNames = EslBlockNames() # for Models Packages Submodels Segments and CodeSubprograms
        self._displayNames = DisplayNames()
        self._program = None
        self._setupInfo = SetupInfo(self, moduleId=0)
        self._models = OrderedDict()
        self._packages = OrderedDict()
        self._submodels = OrderedDict()
        self._segments = OrderedDict()
        self._codes = OrderedDict()

    def blockNames(self): return self._blockNames
    def displayNames(self): return self._displayNames

    def program(self): return self._program
    def setupInfo(self): return self._setupInfo
    def models(self): return self._models
    def packages(self): return self._packages
    def submodels(self): return self._submodels
    def segments(self): return self._segments
    def codes(self): return self._codes

    def changed(self):
        state = self._frame.control().alterationStack().state()
        changed = state != 'empty' and state != 'beginning'
        return changed
    
    def addModule(self, module):
        moduleId = module.moduleId()
        if moduleId > 0 and moduleId in self._modules:
            raise Exception('Module being added has an allocated moduleId')
        if moduleId == 0:
            Application._allocatedModuleNr += 1
            moduleId = Application._allocatedModuleNr
        module.set_moduleId(moduleId)
        self._modules[moduleId] = module

    def removeModule(self, module):
        del self._modules[module.moduleId()]
        module.set_moduleId(0)

    def getModuleById(self, moduleId):
        module = None
        for item in list(self._modules.values()):
            if item.moduleId() == moduleId:
                module = item
                break
        return module

    def getModuleByName(self, eslname):
        module = None
        for item in list(self._modules.values()):
            if item.eslname().upper() == eslname.upper():
                module = item
                break
        return module

    def assignBlock(self, item):
        eslname = item.eslname()
        block = self._blockNames.get(eslname)
        if block is None:
            self._blockNames.add(eslname, item)
        else:
            raise Exception('Duplicate name "'+eslname+'" in application')

    def addModel(self, moduleId, subType, eslname, pageview):
        subprogram = Model(self, moduleId)
        subprogram.set_eslname(eslname)
        subprogram.diagramInfo().set_canvas(pageview)
        self.assignBlock(subprogram)
        self._models[subprogram.moduleId()] = subprogram
        if not self._program.model():
            self._program.set_model(subprogram)
        else:
            pageview.set_moduleId(subprogram.moduleId())
        self._frame.viewManager().applicationView().addInModule(subprogram)
        return subprogram

    def addSubmodel(self, moduleId, subType, eslname, pageview):
        subprogram = Submodel(self, moduleId)
        pageview.set_moduleId(subprogram.moduleId())
        subprogram.set_eslname(eslname)
        subprogram.set_diagramInfo(DiagramInfo(subprogram))
        subprogram.diagramInfo().set_canvas(pageview)
        self.assignBlock(subprogram)
        self._submodels[subprogram.moduleId()] = subprogram
        self._frame.viewManager().applicationView().addInModule(subprogram)
        return subprogram

    def addSegment(self, moduleId, subType, eslname, pageview):
        subprogram = Segment(self, moduleId)
        pageview.set_moduleId(subprogram.moduleId())
        if subType:
            subprogram.set_segmentType(subType)
        subprogram.set_eslname(eslname)
        subprogram.set_diagramInfo(DiagramInfo(subprogram))
        subprogram.diagramInfo().set_canvas(pageview)
        self.assignBlock(subprogram)
        self._segments[subprogram.moduleId()] = subprogram
        self._frame.viewManager().applicationView().addInModule(subprogram)
        return subprogram

    def addCode(self, moduleId, subType, pageview):
        subprogram = Code(self, moduleId)
        pageview.set_moduleId(subprogram.moduleId())
        subprogram.set_codeType(subType)
        self._codes[subprogram.moduleId()] = subprogram
        self._frame.viewManager().applicationView().addInModule(subprogram)
        return subprogram

    def setEslnameIntoNullFile(self, eslname):
        return '[:' + eslname + ':]'

    def removeSubprogram(self, moduleId):
        subprogram = self.getModuleById(moduleId)
        moduleType = subprogram.moduleType()
        moduleId = subprogram.moduleId()
        if moduleType == "model":
            if self._program.model():
                if self._program.model().moduleId() == moduleId:
                    self.program().set_model(None)
            del self._models[moduleId]
        elif moduleType == "submodel":
            del self._submodels[moduleId]
        elif moduleType == "segment":
            del self._segments[moduleId]
        else:
            subprogram = None
        if subprogram:
            self._blockNames.delete(subprogram.eslname())
            self.removeModule(subprogram)
            self._frame.viewManager().applicationView().removeModule(moduleType, moduleId)

    def removeCode(self, moduleId):
        module = self.getModuleById(moduleId)
        if module.moduleType() == "code":
            subprograms = list(module.codeSubprograms().values())
            for sub in subprograms:
                self._blockNames.delete(sub.eslname())
            del self._codes[moduleId]
            self.removeModule(module)
            self._frame.viewManager().applicationView().removeModule(module.moduleType(), moduleId)

    def loadSubprogramData(self, moduleId, category, subType, data):
        subprogram = None
        xmlElement = xut.xmlElement(data)
        if xmlElement:
            if category == "add-submodel":
                subprogram = Submodel(self, moduleId)
            elif category == "add-segment":
                subprogram = Segment(self, moduleId)
            elif category == "add-code":
                subprogram = Code(self, moduleId)
            subprogram.load(xmlElement)
            if category != "add-code":
                if subprogram.eslname():
                    self.assignBlock(subprogram)
            if category == "add-submodel":
                self._submodels[subprogram.moduleId()] = subprogram
            elif category == "add-segment":
                self._segments[subprogram.moduleId()] = subprogram
            elif category == "add-code":
                self._codes[subprogram.moduleId()] = subprogram
                subprogram.set_codeType(subType)
            self._frame.viewManager().applicationView().addInModule(subprogram)
            self.setupSubprogramCalls()
        return subprogram

    def getSubmodelByName(self, eslname, includeCodePackages=True, validOnly=True):
        submodel = None
        for sub in list(self._submodels.values()):
            if not validOnly or sub.valid():
                if sub.eslname().upper() == eslname.upper():
                    submodel = sub
                    break
        if not submodel and includeCodePackages:
            for code in list(self._codes.values()):
                if not validOnly or code.valid():
                    sub = code.getSubmodelByName(eslname)
                    if sub:
                        submodel = sub
                        break
        return submodel

    def getSegmentByName(self, eslname, includeCodePackages=True, validOnly=True):
        segment = None
        for sub in list(self._segments.values()):
            if not validOnly or sub.valid():
                if sub.eslname().upper() == eslname.upper():
                    segment = sub
                    break
        if not segment and includeCodePackages:
            for code in list(self._codes.values()):
                if not validOnly or code.valid():
                    sub = code.getSegmentByName(eslname)
                    if sub:
                        segment = sub
                        break
        return segment

    def getFunctionByName(self, eslname, includeCodePackages=True, validOnly=True):
        function = None
        if not function and includeCodePackages:
            for code in list(self._codes.values()):
                if not validOnly or code.valid():
                    sub = code.getFunctionByName(eslname)
                    if sub:
                        function = sub
                        break
        return function

    def getModelForCanvas(self, canvas):
        model = None
        for mod in list(self._models.values()):
            if mod.diagramInfo() and mod.diagramInfo().canvas() == canvas:
                model = mod
                break
        return model

    def getSubmodelForCanvas(self, canvas):
        submodel = None
        for sub in list(self._submodels.values()):
            if sub.diagramInfo() and sub.diagramInfo().canvas() == canvas:
                submodel = sub
                break
        return submodel

    def getSegmentForCanvas(self, canvas):
        segment = None
        for seg in list(self._segments.values()):
            if seg.diagramInfo() and seg.diagramInfo().canvas() == canvas:
                segment = seg
                break
        return segment

    def addPackage(self, moduleId, eslname, packageview):
        package = Package(self, moduleId)
        package.set_eslname(eslname)
        if packageview:
            packageview.loadPackage(package)
        self.assignBlock(package)
        self._packages[package.moduleId()] = package
        self._frame.viewManager().applicationView().addInModule(package)
        return package

    def removePackage(self,  moduleId):
        package = self.getPackageById(moduleId)
        if package:
            self._blockNames.delete(package.eslname())
            del self._packages[moduleId]
            self.removeModule(package)
            self._frame.viewManager().applicationView().removeModule(package.moduleType(), moduleId)

    def loadPackageData(self, moduleId, data):
        package = Package(self, moduleId)
        xmlElement = xut.xmlElement(data)
        if xmlElement:
            package.load(xmlElement)
            if package.eslname():
                self.assignBlock(package)
                self._packages[moduleId] = package
                self._frame.viewManager().applicationView().addInModule(package)
        return package

    def getPackageById(self, moduleId):
        package = None
        for pack in list(self._packages.values()):
            if pack.moduleId() == moduleId:
                package = pack
                break
        return package

    def getPackageByName(self, eslname, includeCodePackages=True, validOnly=True):
        package = None
        for pack in list(self._packages.values()):
            if not validOnly or pack.valid():
                if pack.eslname().upper() == eslname.upper():
                    package = pack
                    break
        if not package and includeCodePackages:
           for code in list(self.codes().values()):
               if not validOnly or code.valid():
                   for sub in list(code.codeSubprograms().values()):
                        if sub.subprogramType() == "package":
                            if sub.eslname().upper() == eslname.upper():
                                package = sub
                                break
        return package

    def makeSimulationEntity(self, parent, type="", objectId=""):
        entity = None
        specialType = ""
        entities = self._frame.control().entities()
        entityDefnXmlElement = entities.getEntityDefnXmlElement(type)
        if entityDefnXmlElement:
            specialType = entityDefnXmlElement.getAttribute('special-type')

        if specialType == "Transfer Function":
            entity = TransferFunction(parent, type, objectId)
        elif specialType == "Submodel Call":
            entity = SubmodelCall(parent, type, objectId)
        elif specialType == "Segment Call":
            entity = SegmentCall(parent, type, objectId)
        elif specialType == "Function Call":
            entity = FunctionCall(parent, type, objectId)
        elif specialType == "Input Argument":
            entity = InputArgument(parent, type, objectId)
        elif specialType == "Output Argument":
            entity = OutputArgument(parent, type, objectId)
        elif specialType == "Code Insert":
            entity = CodeInsert(parent, type, objectId)
        elif specialType == "Constant Input":
            entity = ConstantInput(parent, type, objectId)
        elif specialType in ArrayOperatorEntity.SpecialTypes: # One of several array operators all handled by ArrayOperatorEntity
            entity = ArrayOperatorEntity(parent, type, objectId)
        else:
            entity = SimulationEntity(parent, type, objectId)
        if entity:
            entity.setSpecialType(specialType)
        if entity:
            entity.setExemplar()
        return entity

    def newApplication(self):
        self.clearApplication()
        self._frame.viewManager().clearViews()
        self._program = Program(self)
        self._frame.viewManager().mainView().programPage().set_moduleId(self._program.moduleId())
        mainModel = Model(self, 0)
        mainModel.diagramInfo().set_canvas(self._frame.viewManager().mainView().programPage())
        mainModel.set_eslname("Main")
        self._models[mainModel.moduleId()] = mainModel
        self._program.set_model(mainModel)
        self._filepath = ""
        self._xmlapplication = None
        self._version = APPLICATION_VERSION_STRING
        self._compatibility = 0 # compatibility level of loaded application with current ESL-Studio
        self._frame.control().propertiesControl().resetPropertiesForNewApplication()
        self._frame.viewManager().simulationParametersView().hideExperimentWarning(True)
        canvas = self._frame.viewManager().mainView().programPage()
        self._frame.control().propertiesControl().setCanvasPropertyPage(canvas)
        self._frame.SetTitle(self._frame._title)
        tabname = self.moduleViewTabname(self._program)
        self._frame.viewManager().mainView().programPage().set_caption(tabname)
        self._frame.viewManager().applicationView().loadFromApplication()
        self._frame.viewManager().setupView().resetSetupView()
        if Config.getBool('Application/Open Simulation Parameters'):
            self._frame.viewManager().showView("SimulationParametersView")
        if Config.getBool('Application/Open Setup View'):
            self._frame.viewManager().showView("SetupView")

    def loadFromFile(self, filepath, reloadingProfile=False):
        valid = False
        if os.path.exists(filepath):
            xmlElement, error = xut.xmlElementFromFile(filepath)
            if xmlElement:
                dir = os.path.dirname(filepath)
                if dir:
                    os.chdir(dir)
                self._frame.control().propertiesControl().resetPropertiesForNewApplication()
                self._xmlapplication = xmlElement
                self._filepath = os.path.abspath(filepath)
                valid = self.load()
                if valid:
                    canvas = self._frame.viewManager().mainView().programPage()
                    self._frame.control().propertiesControl().setCanvasPropertyPage(canvas)
                    applicationTitle = filepath
                    if not Config.getBool('General/Show Full Application Path'):
                        applicationTitle = os.path.basename(applicationTitle)
                    self._frame.SetTitle(self._frame._title + ' ' + applicationTitle)
                    self._frame.viewManager().applicationView().loadFromApplication()
                    if not reloadingProfile:
                        self._frame.applicationHistory().addToHistory(self._filepath)
            else:
                msg = 'File "'+filepath+'" cannot be loaded as an '+APP_NAME+' application\n'
                if error: msg += error + "\n"
                self._frame.control().appendMessage(msg)
        else:
            msg = 'File "'+filepath+'" not found\n'
            self._frame.control().appendMessage(msg)
        return valid

    def load(self):
        msg = ""
        valid = False
        xmlelementname = self._xmlapplication.name()
        if xmlelementname == "esl-studio-application" or xmlelementname == "ise-application":
            self._compatibility = 0
            applicationWithFile = "Application"
            if self._filepath:
                applicationWithFile += " \"" + self._filepath+"\""
            if xmlelementname == "ise-application":
                msg = applicationWithFile + " is an imported ESL-ISE application\n"
                self._compatibility = 1 # same as for version 1.2.0.30 (ESL v8.3.0.1)
                valid = True
            else:
                version = self._xmlapplication.getAttribute("version")
                if version is None: version = ""
                versionComparison = Utils.compareVersions(version, APPLICATION_VERSION_STRING)
                if versionComparison != "invalid":
                    valid = True
                    self._version = version
                    if versionComparison != "same":
                        msg = applicationWithFile + " version " + self._version + " is " + versionComparison + " than this version of ESL-Studio (" + APPLICATION_VERSION_STRING + ")\n"
                    else:
                        msg = applicationWithFile + "\n"
                    compatibilityComparison = Utils.compareVersions(self._version, COMPATIBILITY_1_VERSION_STRING)
                    if compatibilityComparison != "invalid" and compatibilityComparison != "later":
                        self._compatibility = 1
                else:
                    msg = applicationWithFile + " version" + version + " is invalid\n"
        if msg:
            self._frame.control().appendMessage(msg) # show msg right away
            msg = ""
        if valid:
            self.clearApplication()
            self._frame.viewManager().clearViews()
            self._program = Program(self)
            self._frame.viewManager().mainView().programPage().set_moduleId(self._program.moduleId())
            xmlElement = self._xmlapplication.getXmlElementByName("program", False)
            if xmlElement:
                self._program.load(xmlElement)
            xmlElementList = self._xmlapplication.getXmlElementListByName("model", False)
            model = None
            for xmlElement in xmlElementList:
                model = Model(self, moduleId=0)
                model.load(xmlElement)
                if model.eslname():
                    self.assignBlock(model)
                    self._models[model.moduleId()] = model
            if self._compatibility == 1: # load old top-level simulation-parameters into (one and only) model
                model.simulationParameters().load(self._xmlapplication)
            # Set first (diagram) model as program's model
            if len(self._models) > 0:
                self._program.set_model(list(self._models.values())[0])
                if Config.getBool('Application/Open Simulation Parameters'):
                    self._frame.viewManager().showView("SimulationParametersView")
            tabname = self.moduleViewTabname(self._program)
            self._frame.viewManager().mainView().programPage().set_caption(tabname)
            xmlElementList = self._xmlapplication.getXmlElementListByName("package", False)
            for xmlElement in xmlElementList:
                package = Package(self, moduleId=0)
                package.load(xmlElement)
                if package.eslname():
                    self.assignBlock(package)
                    self._packages[package.moduleId()] = package
            xmlElementList = self._xmlapplication.getXmlElementListByName("submodel", False)
            for xmlElement in xmlElementList:
                submodel = None
                if self._compatibility == 1:  # old submodel may be a segment or code (ESL|file)
                    codeType = xmlElement.getAttribute("type")  # old submodel's code-type was given by type
                    if codeType == "ESL" or codeType == "file":
                        code = Code(self, moduleId=0)
                        code.load(xmlElement)
                        self._codes[code.moduleId()] = code
                    else:
                        eslType = xmlElement.getAttribute("esl-type")   # old segment's [segment] type was given by esl-type
                        if eslType == "segment" or eslType == "external-segment":
                            segment = Segment(self, moduleId=0)
                            segment.load(xmlElement)
                            if segment.eslname():
                                self.assignBlock(segment)
                                self._segments[segment.moduleId()] = segment
                        else: # old submodel is still a submodel
                            submodel = Submodel(self, moduleId=0)
                else:
                    submodel = Submodel(self, moduleId=0)
                if submodel:
                    submodel.load(xmlElement)
                    if submodel.eslname():
                        self.assignBlock(submodel)
                        self._submodels[submodel.moduleId()] = submodel
            xmlElementList = self._xmlapplication.getXmlElementListByName("segment", False)
            for xmlElement in xmlElementList:
                segment = Segment(self, moduleId=0)
                segment.load(xmlElement)
                if segment.eslname():
                    self.assignBlock(segment)
                    self._segments[segment.moduleId()] = segment
            xmlElementList = self._xmlapplication.getXmlElementListByName("code", False)
            for xmlElement in xmlElementList:
                code = Code(self, moduleId=0)
                loadedCode = code.load(xmlElement)
                if loadedCode:
                    self._codes[code.moduleId()] = code
            self._setupInfo.load()
            self.setupImportedPackages()
            self.setupSubprogramCalls()
            self.setupLinkedAttributes()
            self.setupAnnotationTexts()
            if Config.getBool('Application/Open Setup View'):
                self._frame.viewManager().showView("SetupView")
        else:
            msg = "Not recognised as an ESL-Studio application file\n"
        if msg:
            self._frame.control().appendMessage(msg)
        self._compatibility = 0
        return valid

    def setupImportedPackages(self):
        for model in list(self._models.values()):
            model.setupImportedPackages()
        for submodel in list(self._submodels.values()):
            submodel.setupImportedPackages()
        for segment in list(self._segments.values()):
            segment.setupImportedPackages()

    def setupSubprogramCalls(self):
        for model in list(self._models.values()):
            model.setupSubprogramCalls()
        for submodel in list(self._submodels.values()):
            submodel.setupSubprogramCalls()
        for segment in list(self._segments.values()):
            segment.setupSubprogramCalls()

    def setupLinkedAttributes(self):
        for model in list(self._models.values()):
            model.setupLinkedAttributes()
        for submodel in list(self._submodels.values()):
            submodel.setupLinkedAttributes()
        for segment in list(self._segments.values()):
            segment.setupLinkedAttributes()

    def setupAnnotationTexts(self):
        for model in list(self._models.values()):
            model.setupAnnotationTexts()
        for submodel in list(self._submodels.values()):
            submodel.setupAnnotationTexts()
        for segment in list(self._segments.values()):
            segment.setupAnnotationTexts()

    def saveApplication(self):
        self.saveToFile(self._filepath)

    def saveToFile(self, filepath):
        xmlString = self.save('\t', 0, False)
        if xmlString:
            f = None
            try:
                f = open(filepath, 'w')
            except Exception:
                msg = 'Cannot write to file "' + filepath +'"\n'
                self._frame.control().appendMessage(msg)
            if f and not f.closed:
                f.write(xmlString)
                f.close()
                applicationTitle = filepath
                if not Config.getBool('General/Show Full Application Path'):
                    applicationTitle = os.path.basename(applicationTitle)
                self._frame.SetTitle(self._frame._title + ' ' + applicationTitle)
                self._filepath = filepath

    def updateModuleProperty(self, module, propertyTag, value, suppress_action=False, alterationReason=None):
        page = self._frame.viewManager().mainView().getModuleViewByModuleId(module.moduleId())
        updateApplicationView = False
        if page:
            oldeslname = ""
            program = None
            if module.moduleType() == "program":
                program = module
                if program.model():
                    module = program.model()
                else:
                    module = None
            else:
                if module == self._program.model():
                    program = self._program
            if module:
                oldeslname = module.eslname()
            if propertyTag == 'programType':
                program.set_programType(value)
                if program.model():
                    modelType = "model"
                    if value == "remote-program":
                        modelType = "remote-segment"
                    elif value == "embedded-program":
                        modelType = "embedded-segment"
                    program.model().set_modelType(modelType)
                program.checkProgramAnnotations(propertyTag, suppress_action=suppress_action)
                updateApplicationView = True
            elif propertyTag == 'programName':
                program.set_name(value)
                program.checkProgramAnnotations(propertyTag, suppress_action=suppress_action)
                updateApplicationView = True
            elif propertyTag == 'programDescription':
                program.set_description(value)
                program.checkProgramAnnotations(propertyTag, suppress_action=suppress_action)
            elif propertyTag == 'experiment':
                program.set_experiment(value)
            elif propertyTag == 'eslname':
                eslname = self._blockNames.getUnusedName(value)
                module.set_eslname(eslname)
                module.checkModuleAnnotations(propertyTag, suppress_action=suppress_action)
                updateApplicationView = True
            elif propertyTag == 'description':
                module.set_description(value)
                module.checkModuleAnnotations(propertyTag, suppress_action=suppress_action)
            elif propertyTag == 'modelType':
                module.set_modelType(value)
                updateApplicationView = True
            elif propertyTag == 'segmentType':
                module.set_segmentType(value)
                updateApplicationView = True
            elif propertyTag == 'ESL':
                updated = module.updateCodeSubprograms(propertyTag, value, suppress_action=suppress_action, alterationReason=alterationReason)
                if updated:
                    page.setText(module.eslText())
                    if hasattr(page, "doShowCodeChecks"):
                        page.doShowCodeChecks(conditionalPaneAlreadyShowing=True)
                        page.hideESLCompilerResultsText()
            elif propertyTag == 'file':
                updated = module.updateCodeSubprograms(propertyTag, value, suppress_action=suppress_action, alterationReason=alterationReason)
                if updated:
                    page.LoadFile(module.file())
                    if hasattr(page, "doShowCodeChecks"):
                        page.doShowCodeChecks(conditionalPaneAlreadyShowing=True)
                        page.hideESLCompilerResultsText()
            elif propertyTag == 'packages':
                module.updateImportedPackages(value)
            elif propertyTag == 'annotations': # for Module Annotation
                if 'ESL Name' in value:
                    module.set_show_eslname("true")
                else:
                    module.set_show_eslname("false")
                if 'Description' in value:
                    module.set_show_description("true")
                else:
                    module.set_show_description("false")
                module.checkModuleAnnotations(propertyTag, suppress_action=suppress_action)
            elif propertyTag == 'programAnnotations':  # for Program Annotation
                if 'Program Type' in value:
                    program.set_show_type("true")
                else:
                    self._program.set_show_type("false")
                if 'Program Name' in value:
                    program.set_show_name("true")
                else:
                    program.set_show_name("false")
                if 'Program Description' in value:
                    program.set_show_description("true")
                else:
                    program.set_show_description("false")
                program.checkProgramAnnotations(propertyTag, suppress_action=suppress_action)

            mainview = self._frame.viewManager().mainView()
            pageindex = mainview.GetPageIndex(page)

            if module:
                eslname = module.eslname()
                if eslname != oldeslname:
                    self._blockNames.delete(oldeslname)
                    module.blockNames().delete(oldeslname)
                    self._blockNames.add(eslname, module)
                    module.blockNames().add(eslname, module)
                    updateApplicationView = True
                    self.renameSubprogramCallsForSubprogram(module, oldeslname, eslname)

            if module:
                tabname = self.moduleViewTabname(module)
                updateApplicationView = True
            else:
                tabname = self.moduleViewTabname(program)
            if tabname:
                mainview.GetPage(pageindex).set_caption(tabname)
            if updateApplicationView:
                self._frame.viewManager().applicationView().updateModuleItem(module)

    def updatePackageName(self, package, eslname):
        oldName = package.eslname()
        package.set_eslname(eslname)
        self._blockNames.delete(oldName)
        package.blockNames().delete(oldName)
        self._blockNames.add(eslname, package)
        package.blockNames().add(eslname, package)
        for module in package.usingModules():
            module.renameImportedPackageName(oldName, eslname)
        mainview = self._frame.viewManager().mainView()
        packageview = mainview.getPackageViewByModuleId(package.moduleId())
        if packageview:
            pageindex = mainview.GetPageIndex(packageview)
            tabname = self.moduleViewTabname(package)
            self._frame.viewManager().mainView().GetPage(pageindex).set_caption(tabname)
            self._frame.viewManager().applicationView().updateModuleItem(package)

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = '<?xml version="1.0"?>' + nl
        now = time.localtime()
        nowstr = time.strftime("%Y-%m-%d %H:%M:%S", now)
        result += '<!-- Created by ' + APP_NAME + ' v'+APPLICATION_VERSION_STRING + ' on ' + nowstr + ' -->' + nl
        result += '<esl-studio-application version="' + APPLICATION_VERSION_STRING + '">' + nl # not the self._version as loaded
        result += self._program.save(indent, level + 1, saveDefaults)
        for model in list(self._models.values()):
            result += model.save(indent, level + 1, saveDefaults)
        for package in list(self._packages.values()):
            result += package.save(indent, level + 1, saveDefaults)
        for submodel in list(self._submodels.values()):
            result += submodel.save(indent, level + 1, saveDefaults)
        for segment in list(self._segments.values()):
            result += segment.save(indent, level + 1, saveDefaults)
        for code in list(self._codes.values()):
            result += code.save(indent, level + 1, saveDefaults)
        result += self._setupInfo.save(indent, level + 1, saveDefaults)
        result += '</esl-studio-application>' + nl
        return result

    def checkValidToInsert(self, diagramInfo, entityElementsToInsertList):
        valid = True
        for entityElement in entityElementsToInsertList:
            thisValid = diagramInfo.checkValidToInsert(entityElement)
            if not thisValid: valid = False
        return valid

    def checkValidNewLinks(self, diagramInfo, newLinksInsertedList):
        valid = True
        for linkElement in newLinksInsertedList:
            thisValid = diagramInfo.checkValidNewLink(linkElement)
            if not thisValid: valid = False
        return valid

    def checkValidToRemove(self, diagramInfo, entityList):
        valid = True
        for entity in entityList:
            thisValid = diagramInfo.checkValidToRemove(entity)
            if not thisValid: valid = False
        return valid

    def setupUndoChangeApplicationData(self, diagramInfo, entityList):
        undoChangeApplicationData = xut.XmlElement('<simulation-entities/>')
        for entity in entityList:
            entityXmlElement = xut.XmlElement(entity.save(None, 0, True))
            undoChangeApplicationData.appendChild(entityXmlElement)
        return undoChangeApplicationData

    def onArgumentsChanged(self, moduleId, suppress_action):
        subprogram = self._modules[moduleId]
        if subprogram.moduleType() in CALLABLEMODULETYPES:
            self.onCallableSubprogramArgumentsChanged(subprogram, suppress_action)

    def onCallableSubprogramArgumentsChanged(self, subprogram, suppress_action):
        subprogramName = subprogram.eslname()
        ports = subprogram.getPorts(allowBlankTag=True)
        portsActionStr = dgAction.makeSubprogramPortsActionStr(ports)

        ###
        self._frame.control().appendMessage('onCallableSubprogramArgumentsChanged name=' + subprogramName + ' ports=' + portsActionStr, 2)
        ###
        for mod in list(self._models.values()):
            mod.diagramInfo().updateSubprogramCalls(subprogram, portsActionStr, suppress_action)
        for sub in list(self._submodels.values()):
            if sub != subprogram: # no recursive subprograms
                if sub.diagramInfo():
                    sub.diagramInfo().updateSubprogramCalls(subprogram, portsActionStr, suppress_action)
        for seg in list(self._segments.values()):
            if seg != subprogram:
                if seg.diagramInfo():
                    seg.diagramInfo().updateSubprogramCalls(subprogram, portsActionStr, suppress_action)

    def getCanvasDiagramInfo(self, canvas):
        diagramInfo = None
        subprogram = None
        subprogram = self.getModelForCanvas(canvas)
        if not subprogram:
            subprogram = self.getSubmodelForCanvas(canvas)
        if not subprogram:
            subprogram = self.getSegmentForCanvas(canvas)
        if subprogram:
            diagramInfo = subprogram.diagramInfo()
        return diagramInfo

    def getCanvasInfo(self, canvas): #[canvasId, model/submodel, name]
        info = None
        subprogram = None
        subprogram = self.getModelForCanvas(canvas)
        if not subprogram:
            subprogram = self.getSubmodelForCanvas(canvas)
        if not subprogram:
            subprogram = self.getSegmentForCanvas(canvas)
        if subprogram:
           info = [canvas.canvasId(), subprogram.moduleType(), subprogram.eslname()]
        return info

    def getSubprogramForCanvasId(self, canvasId):
        subprogram = None
        for mod in list(self._models.values()):
            if mod.diagramInfo() and mod.diagramInfo().canvas().canvasId() == canvasId:
                subprogram = mod
                break
        if not subprogram:
            for sub in list(self._submodels.values()):
                if sub.diagramInfo() and sub.diagramInfo().canvas().canvasId() == canvasId:
                    subprogram = sub
                    break
        if not subprogram:
            for seg in list(self._segments.values()):
                if seg.diagramInfo() and seg.diagramInfo().canvas().canvasId() == canvasId:
                    subprogram = seg
                    break
        return subprogram

    def getCanvasForCanvasId(self, canvasId):
        canvas = None
        subprogram = self.getSubprogramForCanvasId(canvasId)
        if subprogram and subprogram.diagramInfo():
            canvas = subprogram.diagramInfo().canvas()
        return canvas

    def getEntityForCanvasObjectIds(self, canvasId, objectId):
        entity = None
        diagramInfo = None
        subprogram = self.getSubprogramForCanvasId(canvasId)
        if subprogram and subprogram.diagramInfo():
            diagramInfo = subprogram.diagramInfo()
        if diagramInfo:
            entity = diagramInfo.simulationEntities().get(objectId)
        return entity

    def getDisplayForCanvasObjectIds(self, canvasId, objectId):
        display = None
        diagramInfo = None
        subprogram = self.getSubprogramForCanvasId(canvasId)
        if subprogram and subprogram.diagramInfo():
            diagramInfo = subprogram.diagramInfo()
        if diagramInfo:
            display = diagramInfo.displayDefinitions().get(objectId)
        return display

    def getEntityAttributesDict(self, canvasId, objectId):
        attDict = OrderedDict()
        entity = self.getEntityForCanvasObjectIds(canvasId, objectId)
        if entity:
            for atttag in entity.attributes():
                att = entity.attributes()[atttag]
                attDict[atttag] = [ att.valueStr(), att.datatype() ]
        return attDict

    def renameSubprogramCallsForSubprogram(self, module, oldsubmodelname, newsubmodelname):
        if isinstance(module, CallableSubprogram):
            for call in module.subprogramCalls():
                call.subprogramRename(module, oldsubmodelname, newsubmodelname)

    def packageVariableInUse(self, packageModuleId, variableId=0):
        result = False
        package = self.getModuleById(packageModuleId)
        if variableId != 0:
            variable = package.getVariableById(variableId)
            result = len(variable.assignedAttributes()) > 0
        else:
            for variable in list(package.variables().values()):
                if len(variable.assignedAttributes()) > 0:
                    result = True
                    break
        return result

    def getFullLibraryList(self):
        fullLibraryList = []
        for sub in self._models.values():
            if sub.diagramInfo():
                libList = sub.diagramInfo().getLibraryList()
                Utils.extendNew(fullLibraryList, libList)
        for sub in self._submodels.values():
            if sub.diagramInfo():
                libList = sub.diagramInfo().getLibraryList()
                Utils.extendNew(fullLibraryList, libList)
        for sub in self._segments.values():
            if sub.diagramInfo():
                libList = sub.diagramInfo().getLibraryList()
                Utils.extendNew(fullLibraryList, libList)
        for code in self._codes.values():
            libList = code.libraryList()
            Utils.extendNew(fullLibraryList, libList)
        return fullLibraryList

    def checkIsinFullLibraryList(self, eslname):
        result = False
        fullLibraryList = self.getFullLibraryList()
        if fullLibraryList and len(fullLibraryList) > 0:
            fullLibraryBaseNameUpperisedList = list(map(Utils.libraryBaseName, fullLibraryList))
            result = eslname.upper() in fullLibraryBaseNameUpperisedList
        return result

    def getCodeSubprograms(self, subprogramType=None):
        result = []
        for code in self._codes.values():
            subprograms = list(code.codeSubprograms().values())
            if subprogramType:
                subprograms = list(filter(lambda item: item.subprogramType() == subprogramType, subprograms))
            if len(subprograms) > 0:
                result += subprograms
        return result

    def moduleViewTabname(self, module):
        tabname = ""
        if module.moduleType() == 'program':
            if module.model():
                tabname = "Program/" + module.model().identification()
            else:
                tabname = self._program.identification()
        elif module.moduleType() == 'model':
            if self._program.model() and module == self._program.model():
                tabname = "Program/" + module.identification()
            else:
                tabname = module.identification()
        elif module.moduleType() == 'code':
            tabname = module.identification(showSubType=True)
            if not module.valid():
                tabname = "! "+tabname
        elif module.moduleType() == 'setup-info':
            tabname = "Setup"
        else: # submodel segment package code
            tabname = module.identification()
        return tabname

    # TODO this and use when try to delete sim entity with port in use or blank its eslname
    def portInUse(self, simEntity):
        result = False
        return result
