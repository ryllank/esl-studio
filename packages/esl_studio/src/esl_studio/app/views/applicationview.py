#! /usr/bin/python

import wx

from .. import auihandler as aui
from .view import View

class ApplicationItemId():
    def __init__(self, itemNr):
        self._itemNr = itemNr

    def GetItemNr(self):
        return self._itemNr

class ApplicationItem(object):
    def __init__(self, itemNr, treeItem, type, moduleId, componentId):
        self.itemNr = itemNr
        self.treeItem = treeItem
        self.type = type
        self.moduleId = moduleId
        self.componentId = componentId


class ApplicationView(View, wx.TreeCtrl):
    def __init__(self, parent, viewtype):
        treeStyles = wx.TR_DEFAULT_STYLE | wx.NO_BORDER | wx.TR_HIDE_ROOT
        tree = wx.TreeCtrl.__init__(self, parent, -1, wx.Point(0, 0), wx.Size(160, 250), treeStyles)
        View.__init__(self, parent, viewtype)
        self.clear()

        #self.Expand(root) - this caused a crash in MSW
        self.Bind(wx.EVT_CLOSE, self.OnCloseView, self)
 #       self.Bind(wx.EVT_CANCEL, self.OnCancelView, self)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onActivated, self)
        ####self.Bind(wx.EVT_TREE_SEL_CHANGING, self.onSelChange, self) - not used
        self._propagateSelChange = True

        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16, 16)))
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16)))
        self.AssignImageList(imglist)

        self._root = None
        self._allocatedItemNr = 0

    def propagateSelChange(self):
        return self._propagateSelChange
    def set_propagateSelChange(self, propagateSelChange):
        self._propagateSelChange = propagateSelChange

    def defaultPaneInfo(self):
        info = aui.AuiPaneInfo()
        info.Name("applicationView")
        info.Caption("Application")
        info.CaptionVisible(True)
        info.Dockable(True)
        info.Floatable(True)
        #info.Float()
        info.Left()
        info.Layer(1)
        info.FloatingPosition(wx.Point(100, 100))
        info.FloatingSize(wx.Size(150, 300))
        info.MinimizeButton(True)
        info.MaximizeButton(True)
        info.CloseButton(True)
        info.PaneBorder(True)
        info.Resizable(True)
        #info.Gripper(True)
#        info.DestroyOnClose(True)
        return info

    def clear(self):
        self._applicationItems = {}
        self._allocatedItemNr = 0
        self.DeleteAllItems()

    def loadFromApplication(self):
        application = self._parent.application()
        self.clear()
        self._root = self.AddRoot("ROOT", 0)
        program = application.program()
        type = program.programType()
        text = self.moduleItemText(program)
        treeItem = self.addApplicationItem(self._root, text, "program", program.moduleId(), None)
        for model in list(application.models().values()):
            type = model.modelType()
            text = self.moduleItemText(model)
            treeItem = self.addApplicationItem(self._root, text, model.moduleType(), model.moduleId(), None)
            diagramInfo = model.diagramInfo()
            if diagramInfo:
                self.addCanvas(treeItem, model.moduleId(), diagramInfo)
        for package in list(application.packages().values()):
            text = self.moduleItemText(package)
            treeItem = self.addApplicationItem(self._root, text, package.moduleType(), package.moduleId(), None)
        for submodel in list(application.submodels().values()):
            text = self.moduleItemText(submodel)
            treeItem = self.addApplicationItem(self._root, text, submodel.moduleType(), submodel.moduleId(), None)
            diagramInfo = submodel.diagramInfo()
            if diagramInfo:
                self.addCanvas(treeItem, submodel.moduleId(), diagramInfo)
        for segment in list(application.segments().values()):
            text = self.moduleItemText(segment)
            treeItem = self.addApplicationItem(self._root, text, segment.moduleType(), segment.moduleId(), None)
            diagramInfo = segment.diagramInfo()
            if diagramInfo:
                self.addCanvas(treeItem, segment.moduleId(), diagramInfo)
        for code in list(application.codes().values()):
            text = self.moduleItemText(code)
            treeItem = self.addApplicationItem(self._root, text, code.moduleType(), code.moduleId(), None)
            self.addCodeSubprograms(treeItem, code.moduleId(), code)

    def addCanvas(self, baseTreeItem, moduleId, diagramInfo):
        if diagramInfo:
            simulationEntities = diagramInfo.simulationEntities()
            for entityObjectId in simulationEntities:
                entity = simulationEntities[entityObjectId]
                text = entity.identification()
                treeItem = self.addApplicationItem(baseTreeItem, text, 'entity', moduleId, entityObjectId)

    def addCodeSubprograms(self, baseTreeItem, moduleId, code):
        if not baseTreeItem:
            codeApplicationItem = self.findApplicationItem("code", moduleId, None)
            if codeApplicationItem:
                baseTreeItem = codeApplicationItem.treeItem
        if baseTreeItem:
            self.removeAllModuleSubItems(baseTreeItem, moduleId)
            for sub in list(code.codeSubprograms().values()):
                text = self.codeItemText(sub)
                treeItem = self.addApplicationItem(baseTreeItem, text, 'code-subprogram', moduleId, sub.eslname())

    def addApplicationItem(self, baseTreeItem, text, type, moduleId, componentId, afterTreeItem=None, prependItem=False): # Note: we insert afterItem (which comes prior to it)
        self._allocatedItemNr += 1
        itemNr = self._allocatedItemNr
        itemId = ApplicationItemId(itemNr)
        image = 0
        if type == 'entity': image = 1
        if prependItem:
            treeItem = self.PrependItem(baseTreeItem, text, image)
        else:
            if afterTreeItem is None:
                treeItem = self.AppendItem(baseTreeItem, text, image)
            else:
                treeItem = self.InsertItem(baseTreeItem, afterTreeItem, text, image)
        self.SetItemData(treeItem, itemId)
        self._applicationItems[itemNr] = ApplicationItem(itemNr, treeItem, type, moduleId, componentId)
        return treeItem

    def getApplicationItem(self, tree_event):
        applicationItem = None
        treeItem = tree_event.GetItem()
        applicationItemId = None
        try:
            applicationItemId = self.GetItemData(treeItem)
        except Exception:
            pass
        if applicationItemId:
            itemNr = applicationItemId.GetItemNr()
            if itemNr:
                applicationItem = self._applicationItems.get(itemNr)
        return applicationItem

    def findApplicationItem(self, type, moduleId, componentId):
        applicationItem = None
        for appItem in self._applicationItems.values():
            if (appItem.type == type and
                appItem.moduleId == moduleId and
                appItem.componentId == componentId):
                applicationItem = appItem
                break
        return applicationItem

    def addInModule(self, module):
        moduleId = module.moduleId()
        applicationItem = self.findApplicationItem(module.moduleType(), moduleId, None)
        if not applicationItem:
            moduleType = module.moduleType()
            # look for a module, of the same module-type, prior to this in module-id order - to insert this after
            priorTreeItem = None
            someAppItems = list(filter(lambda item: item.type == moduleType, list(self._applicationItems.values())))
            if len(someAppItems) > 0:
                someAppItems = sorted(someAppItems, key=lambda item: int(item.moduleId))
                for it in someAppItems:
                    if int(it.moduleId) > int(moduleId):
                        break
                    priorTreeItem = it.treeItem
            typeOrder = ["program", "model", "package", "submodel", "segment", "code"]
            if priorTreeItem is None:
                priorType = moduleType
                while priorTreeItem is None:
                    for i in range(len(typeOrder)-1, 0, -1):
                        if priorType == typeOrder[i]:
                            priorType = typeOrder[i-1]
                            break #for
                    #end for
                    if priorType == "program":
                        break #while
                    else:
                        someAppItems = list(filter(lambda item: item.type == priorType, list(self._applicationItems.values())))
                        if len(someAppItems) > 0:
                            someAppItems = sorted(someAppItems, key=lambda item: int(item.moduleId), reverse=True)
                            priorTreeItem = someAppItems[0].treeItem
                #end while
            #end if
            text = self.moduleItemText(module)
            treeItem = self.addApplicationItem(self._root, text, moduleType, moduleId, None, priorTreeItem)
            if moduleType == "code" and len(module.codeSubprograms()) > 0:
                self.addCodeSubprograms(treeItem, moduleId, module)
            if moduleType in ["model", "submodel", "segment"]:
                diagramInfo = module.diagramInfo()
                if diagramInfo:
                    self.addCanvas(treeItem, moduleId, diagramInfo)
        else:
            raise Exception('addInModule: module to add in already in application view')
        pass

    def removeModule(self, moduleType, moduleId):
        applicationItem = self.findApplicationItem(moduleType, moduleId, None)
        if applicationItem:
            self.removeAllModuleSubItems(applicationItem.treeItem, moduleId)
            self.Delete(applicationItem.treeItem)
            del self._applicationItems[applicationItem.itemNr]
        else:
            raise Exception('removeModule: module to remove not in application view')
        pass

    def removeAllModuleSubItems(self, baseTreeItem, moduleId):
        moduleAppItems = filter(lambda item: item.moduleId == moduleId, list(self._applicationItems.values()))
        for appItem in moduleAppItems:
            if appItem.treeItem != baseTreeItem:
                del self._applicationItems[appItem.itemNr]
                self.Delete(appItem.treeItem)

    def addInEntity(self, module, entity):
        moduleId = module.moduleId()
        applicationItem = self.findApplicationItem('entity', moduleId, entity.objectId())
        if not applicationItem:
            moduleItem = self.findApplicationItem(module.moduleType(), moduleId, None)
            if moduleItem:
                entityAppItems = list(filter(lambda item: item.type == 'entity' and item.moduleId == moduleId, list(self._applicationItems.values())))
                # look for entity in this module prior to this in module-id order - to insert this after
                priorTreeItem = None
                prependItem = False
                entityObjectId = entity.objectId()
                if len(entityAppItems) > 0:
                    entityAppItems = sorted(entityAppItems, key=lambda item: int(item.componentId))
                    for appItem in entityAppItems:
                        if int(appItem.componentId) > int(entityObjectId):
                            break
                        priorTreeItem = appItem.treeItem
                if priorTreeItem is None: # no prior entity item in this module - so entity will be prepended to model item
                    prependItem = True
                text = entity.identification()
                treeItem = self.addApplicationItem(moduleItem.treeItem, text, 'entity', moduleId, entityObjectId, priorTreeItem, prependItem)
            else:
                raise Exception('addInEntity: module for entity to add in not in application view')
        else:
            raise Exception('addInEntity: entity to add in already in application view')
        pass

    def removeEntity(self, moduleId, componentId):
        applicationItem = self.findApplicationItem('entity', moduleId, componentId)
        if applicationItem:
            itemNr = applicationItem.itemNr
            del self._applicationItems[itemNr]
            self.Delete(applicationItem.treeItem)
        else:
            raise Exception('removeEntity: entity to remove not in application view')
        pass

    def updateModuleItem(self, module):
        text = '????'
        applicationItem = self.findApplicationItem(module.moduleType(), module.moduleId(), None)
        if applicationItem:
            text = self.moduleItemText(module)
            self.SetItemText(applicationItem.treeItem, text)
        if module.moduleType() == "model":
            program = self._parent.application().program()
            if module == program.model():
                applicationItem = self.findApplicationItem(program.moduleType(), program.moduleId(), None)
                if applicationItem:
                    text = self.moduleItemText(program)
                    self.SetItemText(applicationItem.treeItem, text)

    def moduleItemText(self, module):
        text = module.identification(showSubType=True)
        valid = True
        if module.moduleType() == "code":
            valid = module.valid()
        if not valid:
            text = "! " + text
        return text

    def codeItemText(self, codeSubprogram):
        subprogramType = codeSubprogram.subprogramType()
        eslname = codeSubprogram.eslname()
        text = subprogramType+" "+eslname
        valid = codeSubprogram.valid()
        if not valid:
            text = "! " + text
        return text

    #   def OnCancelView(self, event):
#       self._parent._elementsView = None
#       self.Destroy()

    def selectItem(self, type, moduleId=None, componentId=None, suppressPropagation=True): # type can be None or model submodel, entity, package
        alreadySelected = False
        applicationItem = self.findApplicationItem(type, moduleId, componentId)
        if applicationItem:
            if not self.IsSelected(applicationItem.treeItem):
                doSelection = True
                if type == "model":
                    program = self._parent.application().program()
                    if program.model() and moduleId == program.model().moduleId():
                        programApplicationItem = self.findApplicationItem("program", program.moduleId(), None)
                        if programApplicationItem and self.IsSelected(programApplicationItem.treeItem):
                            doSelection = False
                elif type == "code":
                    treeItem = self.GetSelection()
                    if treeItem.IsOk():
                        applicationItemId = self.GetItemData(treeItem)
                        if applicationItemId:
                            itemNr = applicationItemId.GetItemNr()
                            if itemNr:
                                appItem = self._applicationItems.get(itemNr)
                                if appItem and appItem.moduleId == moduleId: # it or a subprogram in it is currently selected
                                    doSelection = False
                if doSelection:
                    if suppressPropagation:
                        self._propagateSelChange = False
                    self.SelectItem(applicationItem.treeItem)
            else:
                alreadySelected = True
        else:
            self.UnselectAll()
        return alreadySelected

    def OnCloseView(self, event):
        self._parent._elementsView = None
        self.Destroy()

    def onActivated(self, tree_event):
        treeItem = tree_event.GetItem()
        if self.ItemHasChildren(treeItem):
            if self.IsExpanded(treeItem):
                self.Collapse(treeItem)
            else:
                self.Expand(treeItem)

    """def onSelChange(self, tree_event):  # not used (instead control's OnApplicationViewItemSelChange checks this view's propagateSelChange state.
        if not self._propagateSelChange:
            #####tree_event.Skip() # doesnt seem to work
            tree_event.Veto() # doesnt highlight the tree item
        #else:
        self._propagateSelChange = True"""
