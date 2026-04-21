#! /usr/bin/python

from . import utils as Utils
from .moduleschangeevent import ModulesChangeEvent, EVT_MODULES_CHANGE
from .alterations import ModuleAlteration
from .application.variable import Variable

_categoryStrings = {
    'add-model': 'add model',
    'add-submodel': 'add submodel',
    'add-segment': 'add segment',
    'add-package': 'add package',
    'add-code': 'add code',
    'remove-model': 'remove model',
    'remove-submodel': 'remove submodel',
    'remove-segment': 'remove segment',
    'remove-package': 'remove package',
    'remove-code': 'remove code',
    'add-package-variable': 'add package variable',
    'remove-package-variable': 'remove package variable',
    'add-parameter': 'add parameter',
    'remove-parameter': 'remove parameter'
}
class ModulesControl(object):
    def __init__(self, control):
        self._control = control

    def setup(self):
        self._frame = self._control.frame()
        self.registerEvents()

    def registerEvents(self):
        self._frame.Bind(EVT_MODULES_CHANGE, self.onModulesChange)

    def onModulesChange(self, moduleschange_event):
        valid = self.validateModuleChange(moduleschange_event.category,
                                          moduleschange_event.moduleId,
                                          moduleschange_event.subType,
                                          moduleschange_event.variableId,
                                          moduleschange_event.data)
        if not valid:
            moduleschange_event.Veto()
        else:
            done, newModuleId, newVariableId = self.doModuleChange(
                                    moduleschange_event.category,
                                    moduleschange_event.moduleId,
                                    moduleschange_event.subType,
                                    moduleschange_event.variableId,
                                    moduleschange_event.data)
            if done:
                moduleId = moduleschange_event.moduleId
                if newModuleId != 0:
                    if newModuleId != moduleId:
                        moduleId = newModuleId
                variableId = moduleschange_event.variableId
                if newVariableId != 0:
                    if newVariableId != variableId:
                        variableId = newVariableId
                self._control.alterationStack().add(
                    ModuleAlteration(moduleId, moduleschange_event.category,
                                     moduleschange_event.subType,
                                     variableId, moduleschange_event.data))

    def addModel(self, modelType):
        # raise the moduleschange_event
        moduleschange_event = ModulesChangeEvent('add-model', 0, modelType)
        self._control.frame().GetEventHandler().ProcessEvent(moduleschange_event)
        valid = moduleschange_event.IsAllowed()
        return valid

    def addSubmodel(self, subType):
        # raise the moduleschange_event
        moduleschange_event = ModulesChangeEvent('add-submodel', 0, subType)
        self._control.frame().GetEventHandler().ProcessEvent(moduleschange_event)
        valid = moduleschange_event.IsAllowed()
        return valid

    def addSegment(self, segmentType):
        # raise the moduleschange_event
        moduleschange_event = ModulesChangeEvent('add-segment', 0, segmentType)
        self._control.frame().GetEventHandler().ProcessEvent(moduleschange_event)
        valid = moduleschange_event.IsAllowed()
        return valid

    def addPackage(self):
        # raise the moduleschange_event
        moduleschange_event = ModulesChangeEvent('add-package', moduleId=0)
        self._control.frame().GetEventHandler().ProcessEvent(moduleschange_event)
        valid = moduleschange_event.IsAllowed()
        return valid

    def addCode(self, codeType):
        # raise the moduleschange_event
        moduleschange_event = ModulesChangeEvent('add-code', 0, codeType)
        self._control.frame().GetEventHandler().ProcessEvent(moduleschange_event)
        valid = moduleschange_event.IsAllowed()
        return valid

    def removeSubprogram(self, moduleId):
        valid = False
        frame = self._control.frame()
        application = frame.application()
        subprogram = application.getModuleById(moduleId)
        if subprogram:
            data = subprogram.save(None, 0, True)
            eventType = "remove-"+subprogram.moduleType()
            subType = ""
            if subprogram.moduleType() == "model":
                subType = subprogram.modelType()
            elif subprogram.moduleType() == "segment":
                subType = subprogram.segmentType()
            moduleschange_event = ModulesChangeEvent(eventType,
                                                     moduleId, subType, 0,
                                                     data)
            self._control.frame().GetEventHandler().ProcessEvent(moduleschange_event)
            valid = moduleschange_event.IsAllowed()
        return valid

    def removePackage(self, moduleId):
        valid = False
        frame = self._control.frame()
        application = frame.application()
        package = application.getPackageById(moduleId)
        if package:
            data = package.save(None, 0, True)
            moduleschange_event = ModulesChangeEvent('remove-package',
                                                     moduleId, '', 0,
                                                     data)
            self._control.frame().GetEventHandler().ProcessEvent(moduleschange_event)
            valid = moduleschange_event.IsAllowed()
        return valid

    def removeCode(self, moduleId):
        valid = False
        frame = self._control.frame()
        application = frame.application()
        code = application.getModuleById(moduleId)
        if code:
            data = code.save(None, 0, True)
            moduleschange_event = ModulesChangeEvent('remove-code',
                                                     moduleId, code.codeType(), 0,
                                                     data)
            self._control.frame().GetEventHandler().ProcessEvent(moduleschange_event)
            valid = moduleschange_event.IsAllowed()
        return valid

    def validateModuleChange(self, category, moduleId, subType, variableId, data):
        valid = False
        rejection = '?'
        frame = self._control.frame()
        application = frame.application()
        if category in ['add-model', 'add-submodel', 'add-segment', 'add-code']:
            valid = True
        elif category == 'remove-model':
            subprogram = application.getModuleById(moduleId)
            if not subprogram == application.program().model():
                valid = True
            else:
                rejection = subprogram.moduleType() + ' ' + subprogram.eslname() + ' in use as the Program\'s Model cannot be removed'
        elif category in ['remove-submodel', 'remove-segment', 'remove-code']:
            subprogram = application.getModuleById(moduleId)
            if not subprogram.hasSubprogramCalls():
                valid = True
            else:
                rejection = subprogram.moduleType()+' '+subprogram.eslname()+' in use cannot be removed'
        elif category == 'add-package':
            valid = True
        elif category == 'remove-package':
            package = application.getPackageById(moduleId)
            if not application.packageVariableInUse(moduleId):
                valid = True
            else:
                rejection = 'package '+package.eslname()+' in use cannot be removed'
        elif category == 'add-package-variable':
            valid = True
        elif category == 'remove-package-variable':
            package = application.getPackageById(moduleId)
            if not application.packageVariableInUse(moduleId, variableId):
                valid = True
            else:
                variable = package.getVariableById(variableId)
                rejection = 'package-variable '+variable.eslname()+' in use cannot be removed'
        elif category == 'add-parameter':
            # No need to check if program's model
            valid = True
        elif category == 'remove-parameter':
            module = application.getModuleById(moduleId)
            if module == application.program():
                module = application.program().model()
            variable = module.getVariableById(variableId)
            if len(variable.assignedAttributes()) == 0: # not in use
                valid = True
            else:
                rejection = 'parameter '+variable.eslname()+' in use cannot be removed'
        diagnosticVerbosity = 1
        msg = "Module change " + self.categoryStr(category) + " module " + self.moduleStr(moduleId)
        if not valid:
            msg += " rejected - " + rejection
            diagnosticVerbosity = 0
        msg += '\n'
        self._control.appendMessage(msg, diagnosticVerbosity)
        if not valid:
            Utils.bleep()
        return valid

    def doModuleChange(self, category, moduleId, subType, variableId, data, alterationReason=None):
        done = False
        newModuleId = 0
        newVariableId = 0
        frame = self._control.frame()
        application = frame.application()
        programsModelId = 0
        if moduleId and moduleId == application.program().moduleId():
            if application.program().model():
                programsModelId = application.program().model().moduleId()
        if category == 'add-model' or category == 'add-submodel' or category == 'add-segment':
            subprogram = None
            if not data:
                eslname = ""
                tabname = ""
                if category == 'add-model':
                    eslname = 'Mod'
                    tabname = "Model "
                elif category == 'add-submodel':
                    eslname = 'Sub'
                    tabname = "Submodel "
                elif category == 'add-segment':
                    eslname = 'Seg'
                    tabname = "Segment "
                name = application.blockNames().getUnusedName(eslname)
                tabname += name
                page = None
                if category == 'add-model':
                    if not application.program().model():
                        page = frame.viewManager().mainView().programPage()
                        #### TODO consider changing page's tabname
                    else:
                        page = frame.viewManager().mainView().addModelPage("")
                    if page:
                        subprogram = application.addModel(moduleId, subType, name, page)
                elif category == 'add-submodel' or category == 'add-segment':
                    page = frame.viewManager().mainView().addSubprogramPage(tabname)
                    if page:
                        if category == 'add-submodel':
                            subprogram = application.addSubmodel(moduleId, subType, name, page)
                        else: # segment
                            subprogram = application.addSegment(moduleId, subType, name, page)
                if subprogram:
                    tabname = application.moduleViewTabname(subprogram)
                    page.set_caption(tabname)
            else:
                subprogram = application.loadSubprogramData(moduleId, category, subType, data) # creates the page
                page = frame.viewManager().mainView().getCanvasByModuleId(subprogram.moduleId())
            if subprogram:
                newModuleId = subprogram.moduleId()
                pageindex = frame.viewManager().mainView().GetPageIndex(page)
                frame.viewManager().mainView().SetSelection(pageindex)
                self._control.propertiesControl().setCanvasPropertyPage(page)
                select = ""
                if category == 'add-model':
                    select = "model"
                elif category == 'add-submodel':
                    select = "submodel"
                elif category == 'add-segment':
                    select = "segment"
                frame.viewManager().applicationView().selectItem(select, subprogram.moduleId())
                done = True
        elif category == 'add-code':
            subprogram = None
            if not data:
                tabname = ""
                if subType == 'ESL':
                    tabname = "Code (ESL)"
                elif subType == 'file':
                    tabname = "Code (File)"
                page = frame.viewManager().mainView().addCodePage(tabname)
                if page and subType == 'ESL':
                    page.setReadOnly(False)
                    page.setAllowCommitESL(True)
                if page:
                    subprogram = application.addCode(moduleId, subType, page)
            else:
                subprogram = application.loadSubprogramData(moduleId, category, subType, data) # creates the page
                page = frame.viewManager().mainView().getCanvasByModuleId(subprogram.moduleId())
            if subprogram:
                newModuleId = subprogram.moduleId()
                pageindex = frame.viewManager().mainView().GetPageIndex(page)
                frame.viewManager().mainView().SetSelection(pageindex)
                self._control.propertiesControl().setCodePropertyPage(subprogram.moduleId())
                done = True
        elif category == 'remove-model' or category == 'remove-submodel' or category == 'remove-segment':
            if programsModelId:
                application.removeSubprogram(programsModelId)
            else:
                application.removeSubprogram(moduleId)
                frame.viewManager().mainView().deleteModuleViewByModuleId(moduleId)
            done = True
        elif category == 'remove-code':
            application.removeCode(moduleId)
            frame.viewManager().mainView().deleteModuleViewByModuleId(moduleId)
            done = True
        if category == 'add-package':
            package = None
            if not data:
                eslname = 'Pack'
                name = application.blockNames().getUnusedName(eslname)
                tabname = "Package " + name
                page = frame.viewManager().mainView().addPackagePage(tabname)
                if page:
                    package = application.addPackage(moduleId, name, page)
            else:
                package = application.loadPackageData(moduleId, data) # creates the page
                page = frame.viewManager().mainView().getPackageViewByModuleId(package.moduleId())
            if package:
                newModuleId = package.moduleId()
                pageindex = frame.viewManager().mainView().GetPageIndex(page)
                frame.viewManager().mainView().SetSelection(pageindex)
                frame.viewManager().applicationView().selectItem('package', package.moduleId())
                done = True
        elif category == 'remove-package':
            application.removePackage(moduleId)
            frame.viewManager().mainView().deleteModuleViewByModuleId(moduleId)
            done = True
        elif category == 'add-package-variable':
            package = application.getPackageById(moduleId)
            eslname = 'Var'
            if not data:
                eslname = package.getUnusedName(eslname)
            variable = Variable(package, eslname, parameter="true", datatype='Real', valueStr="0")
            variable.set_variableId(variableId)
            if data:
                variable.loadData(data)
            package.addVariable(variable)
            newVariableId = variable.variableId()
            view = frame.viewManager().mainView().getPackageViewByModuleId(moduleId)
            view.addVariableProperty(variable)
            #frame.viewManager().applicationView().selectItem('package', moduleId)
            frame.viewManager().mainView().setPage(view)
            done = True
        elif category == 'remove-package-variable':
            package = application.getPackageById(moduleId)
            variable = package.getVariableById(variableId)
            package.removeVariable(variable)
            view = frame.viewManager().mainView().getPackageViewByModuleId(moduleId)
            view.removeVariableProperty(moduleId, variableId)
            #frame.viewManager().applicationView().selectItem('package', moduleId)
            frame.viewManager().mainView().setPage(view)
            done = True
        elif category == 'add-parameter':
            actualModuleId = moduleId
            if programsModelId:
                module = application.getModuleById(programsModelId)
                actualModuleId = module.moduleId()
            else:
                module = application.getModuleById(moduleId)
            eslname = 'Par'
            if not data:
                eslname = module.getUnusedName(eslname)
            variable = Variable(module, eslname, parameter="true", datatype='Real', valueStr="0")
            variable.set_variableId(variableId)
            if data:
                variable.loadData(data)
            module.addVariable(variable)
            newVariableId = variable.variableId()
            canvas = frame.viewManager().mainView().getCanvasByModuleId(moduleId)
            if frame.viewManager().propertiesView().moduleId() == moduleId:
                frame.viewManager().propertiesView().addVariableProperty(variable)
            else:
                self._control.propertiesControl().setCanvasPropertyPage(canvas)
            frame.viewManager().applicationView().selectItem(module.moduleType(), actualModuleId)
            self._control.selectObjects(canvas, [], raiseSelectionEvent=False)
            frame.viewManager().mainView().setPage(canvas)
            done = True
        elif category == 'remove-parameter':
            actualModuleId = moduleId
            if programsModelId:
                module = application.getModuleById(programsModelId)
                actualModuleId = module.moduleId()
            else:
                module = application.getModuleById(moduleId)
            variable = module.getVariableById(variableId)
            module.removeVariable(variable)
            canvas = frame.viewManager().mainView().getCanvasByModuleId(moduleId)
            if frame.viewManager().propertiesView().moduleId() == moduleId:
                frame.viewManager().propertiesView().removeVariableProperty(actualModuleId, variableId)
            else:
                self._control.propertiesControl().setCanvasPropertyPage(canvas)
            frame.viewManager().applicationView().selectItem(module.moduleType(), actualModuleId)
            self._control.selectObjects(canvas, [], raiseSelectionEvent=False)
            frame.viewManager().mainView().setPage(canvas)
            done = True
        return done, newModuleId, newVariableId

    def categoryStr(self, category):
        return _categoryStrings[category]

    def moduleStr(self, moduleId):
        result = ''
        module = self._control.frame().application().getModuleById(moduleId)
        if module:
            result = module.moduleType() + ' ' + module.eslname()
        return result
