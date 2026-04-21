#! /usr/bin/python

import wx

from .. import xmlutil as xut

from .object import toplevelise, Orientation
from .objectxml import getXmlOrientation
from .node import Node

class ActionDefn(object):

    def __init__(self, name, procedure, actionElement):
        self.name = name # used to identify the action
        self.procedure = procedure # identifies procedure - name of method in this class
        self.actionElement = actionElement
    def __str__(self):
        return "<ActionDefn " + str(self.name) + " :" + str(self.procedure) + ">"

class ActionContext(object):
    def __init__(self):
        self.type = None # 'direct', 'interaction', 'context-menu-item', 'keyshortcut'
        self.dc = None # the canvas DC (for drawing on)
        self.ptr = None # location where on the diagram we are interested in (e.g. where mouse was when a click happened, or centre canvas)
        self.targets = [] # list of objects (eg selection, or what hit or a component)
        self.initTargetsSaved = '' # set by interactions - currently only at start of 'dragging' operation (which may be converted to 'linking')
        self.initSelectionSaved = '' # set by interactions
        self.raiseEvent = True # set False if want to perform action but not notify application
        self.suppressAction = False # set True if want to notify application but not perform action (as when done as part of an operation)
    def __str__(self):
        return "<ActionContext "+str(self.type)+" @"+str(self.ptr)+" :"+str(self.targets)+"|"+self.initTargetsSaved+"*"+self.initSelectionSaved+">"

class Actions(object):

    def __init__(self, canvas):
        self._canvas = canvas
        self.actionDefnByName = {}

    def clearActionsDefinitions(self):
        self.actionDefnByName = {}

    def setActionDefinitions(self, canvasDefinitions):
        self.loadFromXml(canvasDefinitions)

    def loadFromXml(self, xmlElement):
        if xmlElement:
            if xmlElement.name() == "actions": actionsElements = [xmlElement]
            else: actionsElements = xmlElement.getXmlElementListByName("actions", True)
            if actionsElements:
                for actionsElement in actionsElements:
                    actionElements = actionsElement.getXmlElementListByName("action", False)
                    if actionElements:
                        for actionElement in actionElements:
                            name = actionElement.getAttribute("name")
                            procedure = actionElement.getAttribute("procedure")
                            if (name and procedure and
                                procedure in self.__class__.__dict__):
                                actionDefn = ActionDefn(name, procedure, actionElement)
                                self.actionDefnByName[name] = actionDefn

    def getObjectsFromXmlElementByIds(self, xmlElement):
        objectList = []
        objectsXmlElement = xmlElement
        if objectsXmlElement:
            objectsXmlElement = objectsXmlElement.getXmlElementByName('objects')
        if objectsXmlElement:
            objectIdList = []
            for objectXmlElement in objectsXmlElement.getChildren():
                objectIdList.append(objectXmlElement.getAttribute('id'))
            for objectId in objectIdList:
                obj = self._canvas.diagram().findObject(objectId)
                if obj: objectList.append(obj)
        return objectList

    def checkForObjectsXmlElementsIncludeZOrder(self, xmlElement):
        includeZOrder = False
        objectsXmlElement = xmlElement
        if objectsXmlElement:
            objectsXmlElement = objectsXmlElement.getXmlElementByName('objects')
        if objectsXmlElement:
            for objectXmlElement in objectsXmlElement.getChildren():
                zOrder = objectXmlElement.getAttribute("z-order")
                if zOrder is not None:
                    includeZOrder = True
                    break
        return includeZOrder

    def ContextMenuAction(self, commandevent): # does not return the resultStr (as is invoked from context menu)
        resultStr = ''
        msg = ''
        actionContext = self._canvas.interactions().ContextMenuActionContext()
        if actionContext is not None:
            menuItemId = commandevent.GetId()
            menuItemElement = self._canvas.interactions().contextmenus().getMenuItemById(menuItemId)
            if menuItemElement:
                action = menuItemElement.getAttribute("action")
                if action:
                    actionDefn = self._canvas.actions().actionDefnByName.get(action)
                    if actionDefn:
                        modeOk = False
                        if self._canvas.mode() == "editing":
                            modeOk = True
                        elif self._canvas.mode() == "browsing":
                            browsable = actionDefn.actionElement.getAttribute("browse")
                            if browsable and browsable == "true":
                                modeOk = True
                        if modeOk:
                            actionXmlElement = menuItemElement.getXmlElementByName("action")
                            procedure = actionDefn.procedure
                            if procedure and isinstance(procedure, str):
                                proc = self.__class__.__dict__.get(procedure)
                                if proc:
                                    resultStr = proc(self, actionDefn, actionContext, actionXmlElement)
                                    if resultStr:
                                        text = menuItemElement.getAttribute("text")
                                        if not text:
                                            text = menuItemElement.getAttribute("action")
                                        msg = 'Action procedure '+procedure+' for context-menu-item '+text+': '+resultStr
                                else:
                                    msg = 'Action procedure '+procedure+' not found for context-menu-item '+str(menuItemElement)
                            else:
                                msg = 'Action '+action+' for context-menu-item '+str(menuItemId)+' has no procedure'
                        else:
                            msg = 'Action ' + action + ' not available in ' + self._canvas.mode() + ' mode'
                    else:
                        msg = 'Action '+action+' not found for context-menu-item '+str(menuItemElement)
                else:
                    msg = 'Action for context-menu-item '+str(menuItemElement)+' has no action'
            else:
                msg = 'Action for context-menu-item for id'+str(menuItemElement)+' has no context-menu-item'
            #delete actionContext
        else:
            msg = 'Action for a context-menu-item has no action-context'
        if msg:
            application_data = '' # cant happen
            self._canvas.raiseCanvasApplicationNotifyEvent(application_data, "display", msg)
        #return resultStr

    def InvokeAction(self, action, actionContext, actionXmlElement=None):
        resultStr = ''
        msg = ''
        actionDefn = self.actionDefnByName.get(action)
        if actionDefn:
            modeOk = False
            if self._canvas.mode() == "editing":
                modeOk = True
            elif self._canvas.mode() == "browsing":
                browsable = actionDefn.actionElement.getAttribute("browse")
                if browsable and browsable == "true":
                    modeOk = True
            if modeOk:
                if actionContext:
                    procedure = actionDefn.procedure
                    if procedure and isinstance(procedure, str):
                        proc = self.__class__.__dict__.get(procedure)
                        if proc:
                            resultStr = proc(self, actionDefn, actionContext, actionXmlElement)
                            if resultStr:
                                msg = 'Action '+action+': '+resultStr
                        else:
                            msg = 'Action procedure '+procedure+' not found when invoking an action'
                    else:
                        msg = 'Action '+action+' when invoking an action has no procedure'
                else:
                    msg = 'Action '+action+' has no action-context when invoking an action'
            else:
                msg = 'Action ' + action + ' not available in '+self._canvas.mode()+' mode'
        else:
            msg = 'Action '+action+' not found when invoking an action'
        if msg:
            application_data = self.getApplicationData(actionXmlElement)
            self._canvas.raiseCanvasApplicationNotifyEvent(application_data, "display", msg)
        #delete actionContext
        return resultStr

    def getApplicationData(self, actionXmlElement):
        application_data = ''
        if actionXmlElement:
            applicationDataXmlElement = actionXmlElement.getXmlElementByName("application-data")
            if applicationDataXmlElement:
                application_data = applicationDataXmlElement.xml()
        return application_data

    def DirectAction(self, actionStr, dc, pos):
        resultStr = ''
        msg = ''
        action = ''
        actionDefn = self.actionDefnByName.get(actionStr)
        actionXmlElement = None
        if not actionDefn:
            actionXmlElement = xut.xmlElement(actionStr)
            if actionXmlElement:
                action = actionXmlElement.getAttribute("name")
                if action:
                    actionDefn = self.actionDefnByName.get(action)
        if actionDefn:
            actionContext = ActionContext()
            actionContext.type = 'direct'
            actionContext.dc = dc
            actionContext.ptr = pos
            actionContext.targets = self._canvas.interactions().selection().selection()
            if actionXmlElement:
                raiseEvent = actionXmlElement.getAttribute("raise-event")
                if raiseEvent == "false":
                    actionContext.raiseEvent = False
            procedure = actionDefn.procedure
            if procedure and isinstance(procedure, str):
                proc = self.__class__.__dict__.get(procedure)
                if proc:
                    resultStr = proc(self, actionDefn, actionContext, actionXmlElement)
                    if resultStr:
                        msg = 'Action '+str(actionStr)+': '+resultStr
                else:
                    msg = 'Action procedure '+procedure+' not found for direct action '+str(actionStr)
            else:
                msg = 'Action '+action+' for direct action '+str(actionStr)+' has no procedure'
            #delete actionContext
        else:
            msg = 'Action'
            if action: msg += ' ' + action
            msg += ' not found for direct action '+str(actionStr)
        if msg:
            application_data = self.getApplicationData(actionXmlElement)
            self._canvas.raiseCanvasApplicationNotifyEvent(application_data, "display", msg)
        return resultStr


    ######## COMMAND PROCEDURES #########

    def NotImplemented(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        text = "NotImplemented invoked for actionDefn '" + str(actionDefn)
        wx.MessageBox(text)
        return resultStr

    def ActivateAction(self, actionDefn, actionContext, actionXmlElement):
        resultStr = '' #'No activate action' no need to keep saying that
        action = ''
        if len(actionContext.targets) == 0:
            pass
        elif len(actionContext.targets) == 1:
            action = actionContext.targets[0].activate()
        else:
            pass
        if action:
            resultStr = self.InvokeAction(action, actionContext)
        return resultStr

    def ShowContextMenu(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        contextmenus = self._canvas.interactions().contextmenus()
        if len(actionContext.targets) == 0:
            contextmenus.showBackgroundContextMenu()
        elif len(actionContext.targets) == 1:
            contextmenus.showObjectContextMenu(actionContext.targets[0])
        else:
            contextmenus.showSelectionContextMenu()
        return resultStr

    def RefreshCanvas(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        self._canvas.Refresh()
        return resultStr

    def SelectAll(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        raiseSelectionEvent = actionContext.raiseEvent
        self._canvas.diagram().selectAllObjectsAndNodes(raiseSelectionEvent)
        return resultStr

    def SetScale(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        toStr = ''
        byStr = ''
        infoElement = actionDefn.actionElement.getXmlElementByName("info")
        if infoElement:
            toStr = infoElement.getAttribute('to')
            byStr = infoElement.getAttribute('by')
        if actionXmlElement:
            infoElement = actionXmlElement.getXmlElementByName("info")
            if infoElement:
                # this overwrites both parameters even if not given in infoElement
                toStr = infoElement.getAttribute('to')
                byStr = infoElement.getAttribute('by')
        # if both to & by given favour by
        if byStr:
            byPct = float(byStr)
            scale = self._canvas.GetScale()
            scale = scale * (1 + byPct / 100.0)
            self._canvas.SetScale(scale)
        elif toStr:
            if toStr == 'all':
                self._canvas.ZoomAll()
            elif toStr == 'selected':
                self._canvas.ZoomSelected()
            else:
                toPct = float(toStr)
                scale = toPct / 100.0
                self._canvas.SetScale(scale)
        else:
            resultStr = 'no "to" or "by" info given'
        return resultStr

    def UndoRequest(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        objlist = actionContext.targets
        application_data = self.getApplicationData(actionXmlElement)
        objectsStr = self._canvas.diagram().saveObjectList(objlist, indent = None, level = 0, saveDefaults = True)
        self._canvas.raiseCanvasApplicationRequestEvent(application_data, "Undo", '', objectsStr)
        return resultStr

    def RedoRequest(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        objlist = actionContext.targets
        application_data = self.getApplicationData(actionXmlElement)
        objectsStr = self._canvas.diagram().saveObjectList(objlist, indent = None, level = 0, saveDefaults = True)
        self._canvas.raiseCanvasApplicationRequestEvent(application_data, "Redo", '', objectsStr)
        return resultStr

    def SelectObjects(self, actionDefn, actionContext, actionXmlElement):
        #objlist = actionContext.targets # this would be the current selection
        #if len(objlist) == 0:
        objlist = self.getObjectsFromXmlElementByIds(actionXmlElement)
        self._canvas.interactions().resetSelection()
        for obj in objlist:
            self._canvas.interactions().selectObject(obj)
        pan = True
        nrObjs = len(objlist)
        if nrObjs > 0 and pan:
            objExtent = self._canvas.diagram().getSelectedExtent()
            if objExtent is not None:
                clientExtent = self._canvas.GetClientRect()
                diagramExtent = self._canvas.screenRectToDiagramRect(clientExtent)
                panLeft = 0
                panUp = 0
                if objExtent.x < diagramExtent.x:
                    panLeft = diagramExtent.x - objExtent.x
                elif objExtent.x + objExtent.width > diagramExtent.x + diagramExtent.width:
                    panLeft = diagramExtent.x + diagramExtent.width - objExtent.x - objExtent.width
                if objExtent.y < diagramExtent.y:
                    panUp = diagramExtent.y - objExtent.y
                elif objExtent.y + objExtent.height > diagramExtent.y + diagramExtent.height:
                    panUp = diagramExtent.y + diagramExtent.height - objExtent.y - objExtent.height
                self._canvas.panDiagram(panLeft, panUp)
        if actionContext.raiseEvent:
            self._canvas.interactions().raiseCanvasSelectedObjects()

    def InsertObjects(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        stagger = False
        infoElement = actionXmlElement.getXmlElementByName("info")
        if infoElement:
            attr = infoElement.getAttribute("stagger")
            if attr and attr == "true":
                stagger = True
        objectsElement = actionDefn.actionElement.getXmlElementByName("objects")
        if actionXmlElement:
            obsElement = actionXmlElement.getXmlElementByName("objects")
            if obsElement: objectsElement = obsElement
        if not objectsElement:
            if actionXmlElement.hasChildren(): #?
                objectsElement = actionXmlElement.getChildren()[0]
            else:
                objectsElement = xut.xmlElement("<objects>"+actionXmlElement.xml()+"</objects>")
        if objectsElement:
            initSelectionSaved = self.getInitSelectionSaved(actionContext)
            application_data = self.getApplicationData(actionXmlElement)
            pos = actionContext.ptr
            if pos and stagger:
                pos = self._canvas.diagram().snapPoint(pos)
                pos = self.staggerPosition(pos)
            objects, oldToNewObjectIds = self._canvas.diagram().insertObjects(objectsElement, pos, selectObjects=True)
            if actionContext.raiseEvent:
                insertedObjectsStr = self._canvas.diagram().saveObjectList(objects, indent = None, level = 0, saveDefaults = True)
                self._canvas.raiseCanvasChangedObjects(application_data,
                                                       '',
                                                       initSelectionSaved,
                                                       '',
                                                       '',
                                                       '',
                                                       insertedObjectsStr)
            secondary = True if actionXmlElement and actionXmlElement.findXmlElementWithAttribute("application-data", "secondary", "true") else False
            if not secondary:
                self._canvas.interactions().raiseCanvasSelectedObjects()
            #self._canvas.Refresh()
        return resultStr

    def staggerPosition(self, pos, matchObjXml=None):
        staggerPos = wx.Point(pos)
        staggerPxl = self._canvas.diagram().gridSnap()
        if not staggerPxl or staggerPxl == 0:
            staggerPxl = 5
        underObjects = self._canvas.diagram().getLayeredObjects(pos)
        while len(underObjects) != 0:
            somethingExactlyUnder = False
            for underObj in underObjects:
                anotherPos = underObj.position()
                if anotherPos.x == staggerPos.x and anotherPos.y == staggerPos.y:
                    # the other object is positioned exactly where we want to be - so cant go ahead
                    if matchObjXml is None:
                        somethingExactlyUnder = True
                        break
                    else: # the under object has to also match the matchObjXml
                        category = matchObjXml.name()
                        type = matchObjXml.getAttribute("type")
                        if underObj.category() == category and underObj.type() == type:
                            somethingExactlyUnder = True
                            break
            pass
            if somethingExactlyUnder:
                staggerPos.x += staggerPxl
                staggerPos.y += staggerPxl
                underObjects = self._canvas.diagram().getLayeredObjects(staggerPos)
            else:
                break  # we can go ahead
        pass
        return staggerPos

    def getInitSelectionSaved(self, actionContext):
        initSelectionSaved = ''
        if actionContext.raiseEvent:
            if actionContext.initSelectionSaved:
                initSelectionSaved = actionContext.initSelectionSaved
            else:
                initSelectionSaved = self._canvas.diagram().saveObjectList(
                    self._canvas.interactions().selection().selection(),
                    indent=None, level=0, saveDefaults=True)
        return initSelectionSaved

    def loadObjectsFromXml(self, xmlnode, raiseEvent, selectObjects, pasting):
        initSelectionSaved = self._canvas.diagram().saveObjectList(
            self._canvas.interactions().selection().selection(),
            indent=None, level=0, saveDefaults=True)
        if pasting:
            objectsElement = xmlnode.getXmlElementByName("objects", True)
            if objectsElement:
                objectElements = objectsElement.getChildren()
                if len(objectElements) > 0:
                    x = int(objectElements[0].getAttribute("x"))
                    y = int(objectElements[0].getAttribute("y"))
                    pos = wx.Point(x, y)
                    staggerPos = self.staggerPosition(pos, None) #stagger for any object - wos #objectElements[0]) stagger for a match object
                    deltaX = staggerPos.x - pos.x
                    deltaY = staggerPos.y - pos.y
                    if deltaX != 0 or deltaY != 0:
                        for objectElement in objectElements:
                            x = objectElement.getAttribute("x")
                            if x is not None: # as for a link
                                x = int(x) + deltaX
                                y = objectElement.getAttribute("y")
                                y = int(y) + deltaY
                                objectElement.setAttribute("x", str(x))
                                objectElement.setAttribute("y", str(y))
        objects, oldToNewObjectIds = self._canvas.diagram().insertObjects(xmlnode, None, selectObjects=selectObjects)
        if raiseEvent:
            redo_inserted = ""
            redoInsertApplicationData = xmlnode.getXmlElementByName("simulation-entities")
            if redoInsertApplicationData:
                redoInsertApplicationData = redoInsertApplicationData.copy()
                for entityElement in redoInsertApplicationData.getChildren():
                    oldId = entityElement.getAttribute("id")
                    if oldId:
                        newId = oldToNewObjectIds.get(oldId)
                        entityElement.setAttribute("id", newId)
                redo_inserted = redoInsertApplicationData.xml()
            application_data = "<application-data type=\"load\"><redo-inserted>"+redo_inserted+"</redo-inserted></application-data>"
            insertedObjectsStr = self._canvas.diagram().saveObjectList(objects, indent=None, level=0, saveDefaults=True)
            self._canvas.raiseCanvasChangedObjects(application_data,
                                                   '',
                                                   initSelectionSaved,
                                                   '',
                                                   '',
                                                   '',
                                                   insertedObjectsStr)
        if selectObjects:
            self._canvas.interactions().raiseCanvasSelectedObjects()
        return oldToNewObjectIds

    def DeleteObjects(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        deleteList = self.getObjectsFromXmlElementByIds(actionXmlElement)
        if len(deleteList) == 0:
            for obj in actionContext.targets:
                obj.gatherDeleteList(deleteList)
        if len(deleteList) > 0:
            initSelectionSaved = self.getInitSelectionSaved(actionContext)
            application_data = self.getApplicationData(actionXmlElement)
            deletedObjectsStr = ''
            if actionContext.raiseEvent:
                deletedObjectsStr = self._canvas.diagram().saveObjectList(deleteList, indent = None, level = 0, saveDefaults = True)
            self._canvas.interactions().removeFromSelection(deleteList)
            self._canvas.diagram().deleteObjects(deleteList)
            if actionContext.raiseEvent:
                self._canvas.raiseCanvasChangedObjects(application_data,
                                                       '',
                                                       initSelectionSaved,
                                                       deletedObjectsStr,
                                                       '',
                                                       '',
                                                       '')
            secondary = True if actionXmlElement and actionXmlElement.findXmlElementWithAttribute("application-data", "secondary", "true") else False
            if not secondary:
                self._canvas.interactions().raiseCanvasSelectedObjects()
        return resultStr

    def UndeleteObjects(self, actionDefn, actionContext, actionXmlElement):
        wx.MessageBox("DEPRECATED: UndeleteObjects")
        resultStr = ''
        category = ''
        type = ''
        infoElement = actionDefn.actionElement.getXmlElementByName("info")
        if infoElement:
            category = infoElement.getAttribute('category')
            type = infoElement.getAttribute('type')
        descr = None
        if category and type:
            if category == 'element':
                descr = '<' + type + '/>'
            else:
                descr = '<' + category + ' type="' + type + '"/>'
        if not descr and actionXmlElement:
            xmlList = actionXmlElement.getChildren()
            if xmlList and len(xmlList) > 0: descr = xmlList[0]
            #self._canvas.InsertObject(descr, actionContext.ptr)
        initSelectionSaved = self.getInitSelectionSaved(actionContext)
        application_data = self.getApplicationData(actionXmlElement)
        pos = actionContext.ptr
        obj = self._canvas.diagram().undeleteObjects(descr, pos, actionContext.raiseEvent,
                                                   application_data=application_data)
        return resultStr

    def UpdateObjects(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        objlist = actionContext.targets
        if len(objlist) == 0:
            objlist = self.getObjectsFromXmlElementByIds(actionXmlElement)
        if len(objlist) > 0:
            topObjlist = list(map(toplevelise, objlist))
            initObjectsSaved = ''
            if actionContext.raiseEvent:
                if actionContext.initTargetsSaved:
                    initObjectsSaved = actionContext.initTargetsSaved
                else:
                    initObjectsSaved = self._canvas.diagram().saveObjectList(topObjlist, indent = None, level = 0, saveDefaults = True)
            initSelectionSaved = self.getInitSelectionSaved(actionContext)
            deleteList = []
            deletedObjectsStr = ''
            if not actionContext.suppressAction:
                self._canvas.diagram().updateObjects(actionXmlElement, deleteList)
                if len(deleteList):
                    if actionContext.raiseEvent:
                        deletedObjectsStr = self._canvas.diagram().saveObjectList(deleteList, indent = None, level = 0, saveDefaults = True)
                    self._canvas.diagram().deleteObjects(deleteList)
            application_data = self.getApplicationData(actionXmlElement)
            if actionContext.raiseEvent:
                objlist = list(map(toplevelise, objlist))
                updatedObjectsStr = self._canvas.diagram().saveObjectList(topObjlist, indent = None, level = 0, saveDefaults = True)
                self._canvas.raiseCanvasChangedObjects(application_data,
                                                       '',
                                                       initSelectionSaved,
                                                       deletedObjectsStr,
                                                       initObjectsSaved,
                                                       updatedObjectsStr,
                                                       '')
            secondary = True if actionXmlElement and actionXmlElement.findXmlElementWithAttribute("application-data", "secondary", "true") else False
            if not secondary and actionContext.raiseEvent:
                self._canvas.interactions().raiseCanvasSelectedObjects()
            # overkill - redraw everything
            self._canvas.Refresh()
        return resultStr

    def AlterationObjects(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        deleteElement = actionXmlElement.getXmlElementByName("delete")
        insertElement = actionXmlElement.getXmlElementByName("insert")
        updateElement = actionXmlElement.getXmlElementByName("update")
        selectElement = actionXmlElement.getXmlElementByName("select")

        initSelectionSaved = self._canvas.diagram().saveObjectList(
            self._canvas.interactions().selection().selection(),
            indent=None, level=0, saveDefaults=True)

        if deleteElement:
            deleteList = self.getObjectsFromXmlElementByIds(deleteElement)
            self._canvas.diagram().deleteObjects(deleteList)

        if insertElement: # not links:
            objects, oldToNewObjectIds = self._canvas.diagram().insertObjects(insertElement, None, selectObjects=False, keepObjectIds=True, linksOnlyOrNotLinks="notLinks")

        initObjectsSaved = ''
        includeZOrder = False
        if updateElement: # not links
            includeZOrder = self.checkForObjectsXmlElementsIncludeZOrder(updateElement)
            updateList = self.getObjectsFromXmlElementByIds(updateElement)
            initObjectsSaved = self._canvas.diagram().saveObjectList(updateList, indent=None, level=0, saveDefaults=True, includeZOrder=includeZOrder)
            self._canvas.diagram().updateObjects(updateElement, [], linksOnlyOrNotLinks="notLinks", includeZOrder=includeZOrder)

        if insertElement: # links only
            objects, oldToNewObjectIds = self._canvas.diagram().insertObjects(insertElement, None, selectObjects=False, keepObjectIds=True, linksOnlyOrNotLinks="linksOnly")

        if updateElement: # links only
            self._canvas.diagram().updateObjects(updateElement, [], linksOnlyOrNotLinks="linksOnly")

        if selectElement:
            selectList = self.getObjectsFromXmlElementByIds(selectElement)
            self._canvas.interactions().resetSelection(selectList)

        application_data = self.getApplicationData(actionXmlElement)
        if actionContext.raiseEvent:
            deleteElementStr = deleteElement.getChildren()[0].xml() if deleteElement else ''
            updateElementStr = updateElement.getChildren()[0].xml() if updateElement else ''
            insertElementStr = insertElement.getChildren()[0].xml() if insertElement else ''
            self._canvas.raiseCanvasChangedObjects(application_data,
                                                   '',
                                                   initSelectionSaved,
                                                   deleteElementStr,
                                                   initObjectsSaved,
                                                   updateElementStr,
                                                   insertElementStr)

        secondary = True if actionXmlElement and actionXmlElement.findXmlElementWithAttribute("application-data", "secondary", "true") else False
        if not secondary:
            self._canvas.interactions().raiseCanvasSelectedObjects()
        # overkill - redraw everything
        self._canvas.Refresh()
        return resultStr

    def CutObjects(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        deleteList = []
        for obj in actionContext.targets:
            obj.gatherDeleteList(deleteList)
        if len(deleteList) > 0:
            #self._canvas.clipboard().copyObjects(deleteList)
            application_data = self.getApplicationData(actionXmlElement)
            objectsStr = self._canvas.diagram().saveObjectList(deleteList, indent = None, level = 0, saveDefaults = True)
            self._canvas.raiseCanvasApplicationRequestEvent(application_data, "Clip Save Objects", '', objectsStr)
            initSelectionSaved = self.getInitSelectionSaved(actionContext)
            self._canvas.interactions().removeFromSelection(deleteList)
            self._canvas.diagram().deleteObjects(deleteList)
            if actionContext.raiseEvent:
                self._canvas.raiseCanvasChangedObjects(application_data,
                                                       '',
                                                       initSelectionSaved,
                                                       objectsStr,
                                                       '',
                                                       '',
                                                       '')
            self._canvas.interactions().resetSelection()
            self._canvas.interactions().raiseCanvasSelectedObjects()
        return resultStr

    def CopyObjects(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        copyList = []
        copyList = actionContext.targets
        copyList = list(filter(lambda obj: obj.copyable(), copyList))
        for obj in actionContext.targets:
            obj.gatherCopyList(copyList)
        if len(copyList) > 0:
            application_data = self.getApplicationData(actionXmlElement)
            objectsStr = self._canvas.diagram().saveObjectList(copyList, indent = None, level = 0, saveDefaults=False)
            self._canvas.raiseCanvasApplicationRequestEvent(application_data, "Clip Save Objects", '', objectsStr)
        return resultStr

    def PasteObjects(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        application_data = self.getApplicationData(actionXmlElement)
        self._canvas.raiseCanvasApplicationRequestEvent(application_data, "Clip Paste Objects", '', '')
        return resultStr

    def TogglePortSign(self, actionDefn, actionContext, actionXmlElement):
        resultStr = 'No port'
        obj = None
        if len(actionContext.targets) == 1:
            obj = actionContext.targets[0]
        if obj is not None and obj.category() == "port":
            resultStr = ''
            initSelectionSaved = self.getInitSelectionSaved(actionContext)
            initObjectsSaved = ''
            # Save the whole entity (top-level object) the port belongs to.
            entity = obj.entity()
            if actionContext.raiseEvent:
                initObjectsSaved = self._canvas.diagram().saveObjectList([entity], indent = None, level = 0, saveDefaults = True)
            obj.togglesign()
            #obj.refreshOverlayExtent(None)
            obj.parent().refreshOverlayExtent(None)
            if actionContext.raiseEvent:
                #data = '<data>'
                #data += '<initial>' + initObjectsSaved + '</initial>'
                #data += '</data>'
                application_data = self.getApplicationData(actionXmlElement)
                updatedObjectsStr = self._canvas.diagram().saveObjectList([entity], indent = None, level = 0, saveDefaults = True)
                self._canvas.raiseCanvasChangedObjects(application_data,
                                                       '',
                                                       initSelectionSaved,
                                                       '',
                                                       initObjectsSaved,
                                                       updatedObjectsStr,
                                                       '')
            self._canvas.interactions().raiseCanvasSelectedObjects()
        # overkill - redraw everything
        self._canvas.Refresh()
        return resultStr

    def SetOrientation(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        orientation = Orientation.normal
        infoElement = actionDefn.actionElement.getXmlElementByName("info")
        if infoElement:
            orient = getXmlOrientation(infoElement)
            if orient: orientation = orient
        if actionXmlElement:
            infoElement = actionXmlElement.getXmlElementByName("info")
            if infoElement:
                orient = getXmlOrientation(infoElement)
                if orient: orientation = orient
        objlist = actionContext.targets
        if len(objlist) == 0:
            objlist = self.getObjectsFromXmlElementByIds(actionXmlElement)
        if len(objlist) > 0:
            initSelectionSaved = self.getInitSelectionSaved(actionContext)
            initObjectsSaved = ''
            if actionContext.raiseEvent:
                if actionContext.initTargetsSaved:
                    initObjectsSaved = actionContext.initTargetsSaved
                else:
                    initObjectsSaved = self._canvas.diagram().saveObjectList(objlist, indent = None, level = 0, saveDefaults = True)
            applied = False
            for obj in objlist:
                if (obj.isOrientable()              # Don't raise event if no objects were applied
                    and obj.category() != "port"):  # Prevent re-orientating ports via command
                    obj.applyOrientation(actionContext.dc, orientation)
                    applied = True
            if applied:
                if actionContext.raiseEvent:
                    #data = '<data orientation="' + str(orientation)
                    #data += '">'
                    #data += '<initial>' + initObjectsSaved + '</initial>'
                    #data += '</data>'
                    application_data = self.getApplicationData(actionXmlElement)
                    updatedObjectsStr = self._canvas.diagram().saveObjectList(objlist, indent = None, level = 0, saveDefaults = True)
                    self._canvas.raiseCanvasChangedObjects(application_data,
                                                           '',
                                                           initSelectionSaved,
                                                           '',
                                                           initObjectsSaved,
                                                           updatedObjectsStr,
                                                           '')
                    self._canvas.interactions().raiseCanvasSelectedObjects()
                # overkill - redraw everything
                self._canvas.Refresh()
        return resultStr

    def MoveObjects(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        xStr = ''
        yStr = ''
        infoElement = actionDefn.actionElement.getXmlElementByName("info")
        x = 0
        y = 0
        if infoElement:
            xStr = infoElement.getAttribute('x')
            yStr = infoElement.getAttribute('y')
            if xStr: x = int(xStr)
            if yStr: y = int(yStr)
        if actionXmlElement:
            infoElement = actionXmlElement.getXmlElementByName("info")
            if infoElement:
                xStr = infoElement.getAttribute('x')
                yStr = infoElement.getAttribute('y')
                if xStr: x = int(xStr)
                if yStr: y = int(yStr)
        objlist = actionContext.targets
        if len(objlist) == 0:
            objlist = self.getObjectsFromXmlElementByIds(actionXmlElement)
        if len(objlist) > 0:
            objlist = list(map(toplevelise, objlist))
            initSelectionSaved = self.getInitSelectionSaved(actionContext)
            initObjectsSaved = ''
            if actionContext.raiseEvent:
                if actionContext.initTargetsSaved:
                    initObjectsSaved = actionContext.initTargetsSaved
                else:
                    initObjectsSaved = self._canvas.diagram().saveObjectList(objlist, indent = None, level = 0, saveDefaults = True)
            if not actionContext.suppressAction:
                refreshCache = wx.Rect()
                displacement = wx.Point(x, y)
                for obj in objlist:
                    obj.startDragging()
                    obj.dragBy(actionContext.dc, displacement, refreshCache)
                    obj.stopDragging()
                #if refreshCache.width != 0 and refreshCache.height != 0: # dont need this if Refresh (everything) later
                #    self._canvas.refreshExtent(refreshCache)
            if actionContext.raiseEvent:
                #data = '<data displacement="' + str(x) + ',' + str(y)
                #data += '">'
                #data += '<initial>' + initObjectsSaved + '</initial>'
                #data += '</data>'
                application_data = self.getApplicationData(actionXmlElement)
                #infoStr = '<info dragged-by="' + str(x) + ',' + str(y) + '"/>'
                objlist = list(map(toplevelise, objlist))
                updatedObjectsStr = self._canvas.diagram().saveObjectList(objlist, indent = None, level = 0, saveDefaults = True)
                self._canvas.raiseCanvasChangedObjects(application_data,
                                                       '',
                                                       initSelectionSaved,
                                                       '',
                                                       initObjectsSaved,
                                                       updatedObjectsStr,
                                                       '')
            # overkill - redraw everything
            self._canvas.Refresh()
        return resultStr

    def JoinLink(self, actionDefn, actionContext, actionXmlElement):
        resultStr = 'No link and/or connectable'
        objlist = actionContext.targets
        if len(objlist) == 0:
            objlist = self.getObjectsFromXmlElementByIds(actionXmlElement)
        if len(objlist) >= 2:
            initSelectionSaved = self.getInitSelectionSaved(actionContext)
            link = objlist[0]
            if link.category() == 'link':
                connectable = objlist[1]
                joined = False
                resultStr = 'Could not join link ({type}) to {dst-category} ({dst-type})'
                if connectable is not link.startObject():
                    if connectable.category() == "port":
                        joined, errorMsg = connectable.endLink(link)
                    elif connectable.category() == "node":
                        joined, errorMsg = connectable.joinLink(link)
                if not joined:
                    if errorMsg:
                        resultStr = errorMsg
                    # helpful substitutions
                    resultStr = resultStr.replace("{dst-category}", connectable.category())
                    resultStr = resultStr.replace("{type}", link.type())
                    resultStr = resultStr.replace("{dst-type}", connectable.type())
                else:
                    resultStr = ''
                    if actionContext.raiseEvent:
                        application_data = self.getApplicationData(actionXmlElement)
                        insertedObjectsStr = self._canvas.diagram().saveObjectList([link], indent = None, level = 0, saveDefaults = True)
                        self._canvas.raiseCanvasChangedObjects(application_data,
                                                               '',
                                                               initSelectionSaved,
                                                               '',
                                                               '',
                                                               '',
                                                               insertedObjectsStr)
        # overkill - redraw everything
        self._canvas.Refresh()
        return resultStr

    def CreateNodeEndLink(self, actionDefn, actionContext, actionXmlElement):
        resultStr = 'No link'
        objlist = actionContext.targets
        if len(objlist) == 0:
            objlist = self.getObjectsFromXmlElementByIds(actionXmlElement)
        if len(objlist) >= 1:
            initSelectionSaved = self.getInitSelectionSaved(actionContext)
            link = objlist[0]
            if link.category() == 'link':
                resultStr = 'Could not end link with node'
                pos = actionContext.ptr
                node, errorMsg = link.endWithNode(pos)
                if node:
                    resultStr = ''
                    if actionContext.raiseEvent:
                        application_data = self.getApplicationData(actionXmlElement)
                        insertedObjectsStr = self._canvas.diagram().saveObjectList([link, node], indent = None, level = 0, saveDefaults = True)
                        self._canvas.raiseCanvasChangedObjects(application_data,
                                                               '',
                                                               initSelectionSaved,
                                                               '',
                                                               '',
                                                               '',
                                                               insertedObjectsStr)
                elif errorMsg:
                    resultStr = errorMsg
        # overkill - redraw everything
        self._canvas.Refresh()
        return resultStr

    def InsertNodeInLink(self, actionDefn, actionContext, actionXmlElement):
        resultStr = 'No link'
        objlist = actionContext.targets
        if len(objlist) == 0:
            objlist = self.getObjectsFromXmlElementByIds(actionXmlElement)
        if len(objlist) >= 1:
            old_link = objlist[0]
            if old_link.category() == 'link':
                resultStr = ""
                old_connectable = old_link.endObject()
                old_node = None
                if isinstance(old_connectable, Node):
                    old_node = old_connectable
                    old_entity = old_node
                else:
                    old_entity = old_connectable.parent()
                initSelectionSaved = self.getInitSelectionSaved(actionContext)
                initObjectsSaved = ''
                if actionContext.raiseEvent:
                    initObjectsSaved = self._canvas.diagram().saveObjectList([old_link, old_entity], indent=None, level=0,
                                                                             saveDefaults=True)
                linkConnectsAtEnd = old_connectable.linkConnectsAtEnd(old_link)
                old_connectable.detachLink(old_link)
                pos = old_link.getClosestPtOnLine(actionContext.ptr)
                new_node, errorMsg = old_link.endWithNode(pos)
                if new_node:
                    new_link, errorMsg = new_node.startLink()
                    joined = False
                    if old_node:
                        joined, errorMsg = old_node.joinLink(new_link, alertNode=False)
                    else:
                        joined, errorMsg = old_connectable.endLink(new_link)
                    if joined:
                        resultStr = ''
                        if actionContext.raiseEvent:
                            application_data = self.getApplicationData(actionXmlElement)
                            updatedObjectsStr = self._canvas.diagram().saveObjectList([old_entity, old_link, new_node, new_link], indent = None, level = 0, saveDefaults = True)
                            insertedObjectsStr = self._canvas.diagram().saveObjectList(
                                [new_node, new_link], indent=None, level=0, saveDefaults=True)
                            self._canvas.raiseCanvasChangedObjects(application_data,
                                                                   '',
                                                                   initSelectionSaved,
                                                                   '',
                                                                   initObjectsSaved,
                                                                   updatedObjectsStr,
                                                                   insertedObjectsStr)
                        new_node.alertObject(self._canvas.diagram().themeProperties().AlertConnectionTime)
                    else:
                        if new_link:
                            self._canvas.diagram().removeLink(new_link)
                        self._canvas.diagram().removeNode(new_node)
                        old_connectable.addLink(old_link, linkConnectsAtEnd)
                        if linkConnectsAtEnd:
                            old_link.endOnConnectable(old_connectable)
                        else:
                            old_link.startOnConnectable(old_connectable)
                        if errorMsg:
                            resultStr = errorMsg
        # overkill - redraw everything
        self._canvas.Refresh()
        return resultStr

    def RemoveNode(self, actionDefn, actionContext, actionXmlElement):
        resultStr = 'No node'
        objlist = actionContext.targets
        if len(objlist) == 0:
            objlist = self.getObjectsFromXmlElementByIds(actionXmlElement)
        if len(objlist) >= 1:
            initSelectionSaved = self.getInitSelectionSaved(actionContext)
            old_node = objlist[0]
            if old_node.category() == 'node':
                old_link = None # to be eliminated
                for link in old_node.links(): # get last one of the type
                    if link.type() == old_node.type():
                        old_link = link
                if old_link:
                    other_links = old_node.links()[:]
                    other_links.remove(old_link)
                    initObjectsSaved = ""
                    deletedObjectsSaved = ""
                    if actionContext.raiseEvent:
                        init_objs = [old_node, old_link]
                        init_objs.extend(other_links)
                        initObjectsSaved = self._canvas.diagram().saveObjectList(
                            init_objs, indent=None, level=0, saveDefaults=True)
                        deletedObjectsSaved = self._canvas.diagram().saveObjectList(
                            [old_node, old_link], indent=None, level=0, saveDefaults=True)
                    root_connectable = old_link.startObject()
                    if root_connectable == old_node: root_connectable = old_link.endObject()
                    old_node.detachLink(old_link)
                    for link in other_links:
                        if link.endObject() == old_node:
                            link.endOnConnectable(root_connectable)
                            added, errorMsg = root_connectable.addLink(link, True)
                            link.refreshOverlayExtent(None)
                        elif link.startObject() == old_node:
                            link.startOnConnectable(root_connectable)
                            added, errorMsg = root_connectable.addLink(link, False)
                            link.refreshOverlayExtent(None)
                    self._canvas.diagram().removeLink(old_link)
                    self._canvas.diagram().removeNode(old_node)
                    resultStr = ''
                    if actionContext.raiseEvent:
                        application_data = self.getApplicationData(actionXmlElement)
                        updatedObjectsStr = self._canvas.diagram().saveObjectList(other_links, indent = None, level = 0, saveDefaults = True)
                        self._canvas.raiseCanvasChangedObjects(application_data,
                                                               '',
                                                               initSelectionSaved,
                                                               deletedObjectsSaved,
                                                               initObjectsSaved,
                                                               updatedObjectsStr,
                                                               '')
        # overkill - redraw everything
        self._canvas.Refresh()
        return resultStr

    def SetLineDraw(self, actionDefn, actionContext, actionXmlElement):
        resultStr = 'No line or link'
        line_draw = "straight"
        infoElement = actionDefn.actionElement.getXmlElementByName("info")
        if infoElement:
            line_dr = infoElement.getAttribute("line-draw")
            if line_dr: line_draw = line_dr
        if actionXmlElement:
            infoElement = actionXmlElement.getXmlElementByName("info")
            if infoElement:
                line_dr = infoElement.getAttribute("line-draw")
                if line_dr: line_draw = line_dr
        objlist = actionContext.targets
        if len(objlist) == 0:
            objlist = self.getObjectsFromXmlElementByIds(actionXmlElement)
        if len(objlist) >= 1:
            line_or_link = objlist[0]
            resultStr = ""
            if (line_or_link.category() == "element" and line_or_link.type() == "line")\
                or line_or_link.category() == "link":
                initSelectionSaved = self.getInitSelectionSaved(actionContext)
                initObjectsSaved = ''
                if actionContext.raiseEvent:
                     initObjectsSaved = self._canvas.diagram().saveObjectList([line_or_link], indent = None, level = 0, saveDefaults = True)
                line_or_link.setLineDraw(line_draw)
                if actionContext.raiseEvent:
                    #data = '<data orientation="' + str(orientation)
                    #data += '">'
                    #data += '<initial>' + initObjectsSaved + '</initial>'
                    #data += '</data>'
                    application_data = self.getApplicationData(actionXmlElement)
                    updatedObjectsStr = self._canvas.diagram().saveObjectList([line_or_link], indent = None, level = 0, saveDefaults = True)
                    self._canvas.raiseCanvasChangedObjects(application_data,
                                                           '',
                                                           initSelectionSaved,
                                                           '',
                                                           initObjectsSaved,
                                                           updatedObjectsStr,
                                                           '')
                # overkill - redraw everything
                self._canvas.Refresh()
                self._canvas.interactions().raiseCanvasSelectedObjects() #force property refresh
        return resultStr

    def AppendPoint(self, actionDefn, actionContext, actionXmlElement):
        resultStr = 'No polyline, polygon or spline'
        obj = None
        if len(actionContext.targets) == 1:
            obj = actionContext.targets[0]
        if obj is not None and obj.category() == "element" and obj.type() in ["polyline", "polygon", "spline"]:
            resultStr = 'Need at least 3 points/segments'
            pts = obj.getPoints()
            nr = len(pts)
            if nr >= 3:
                resultStr = ''
                initSelectionSaved = self.getInitSelectionSaved(actionContext)
                initObjectsSaved = ''
                # Save the (top-level) object.
                if actionContext.raiseEvent:
                    initObjectsSaved = self._canvas.diagram().saveObjectList([obj], indent = None, level = 0, saveDefaults = True)
                # repeat last segment
                lastPt = pts[len(pts) - 1]
                penultPt = pts[len(pts) - 2]
                newPt = lastPt + (lastPt - penultPt)
                pts.append(newPt)
                obj.setPoints(pts)
                obj.clearGrabs() # to force them to be recalc if selected
                obj.handleGrabs()
                obj.refreshOverlayExtent(None)
                if actionContext.raiseEvent:
                    application_data = self.getApplicationData(actionXmlElement)
                    updatedObjectsStr = self._canvas.diagram().saveObjectList([obj], indent = None, level = 0, saveDefaults = True)
                    self._canvas.raiseCanvasChangedObjects(application_data,
                                                           '',
                                                           initSelectionSaved,
                                                           '',
                                                           initObjectsSaved,
                                                           updatedObjectsStr,
                                                           '')
        # overkill - redraw everything
        self._canvas.Refresh()
        return resultStr

    def RemovePoint(self, actionDefn, actionContext, actionXmlElement):
        resultStr = 'No polyline, polygon or spline'
        obj = None
        if len(actionContext.targets) == 1:
            obj = actionContext.targets[0]
        if obj is not None and obj.category() == "element" and obj.type() in ["polyline", "polygon", "spline"]:
            resultStr = 'Need at least 4 points/segments'
            pts = obj.getPoints()
            nr = len(pts)
            if nr >= 4:
                resultStr = ''
                initSelectionSaved = self.getInitSelectionSaved(actionContext)
                initObjectsSaved = ''
                # Save the (top-level) object.
                if actionContext.raiseEvent:
                    initObjectsSaved = self._canvas.diagram().saveObjectList([obj], indent = None, level = 0, saveDefaults = True)
                origExt = obj.getGrabOverlayExtent(None)
                # lose the last segment
                del pts[-1:]
                obj.setPoints(pts)
                obj.clearGrabs() # to force them to be recalc if selected
                obj.handleGrabs()
                obj.diagram().canvas().refreshExtent(origExt)
                obj.refreshOverlayExtent(None)
                if actionContext.raiseEvent:
                    application_data = self.getApplicationData(actionXmlElement)
                    updatedObjectsStr = self._canvas.diagram().saveObjectList([obj], indent = None, level = 0, saveDefaults = True)
                    self._canvas.raiseCanvasChangedObjects(application_data,
                                                           '',
                                                           initSelectionSaved,
                                                           '',
                                                           initObjectsSaved,
                                                           updatedObjectsStr,
                                                           '')
        # overkill - redraw everything
        self._canvas.Refresh()
        return resultStr

    #def UpdateEntityPorts(self, actionDefn, actionContext, actionXmlElement):
    #    print "UpdateEntityPorts " + str(actionContext) + " " + str(actionDefn) + " " + str(actionXmlElement)
    #    resultStr = 'No entity'
    #    objlist = actionContext.targets
    #    if len(objlist) == 0:
    #        objlist = self.getObjectsFromXmlElementByIds(actionXmlElement)
    #    if len(objlist) >= 1:
    #        entity = objlist[0]
    #        if entity.category() == 'entity':
    #            entity.updateEntityPorts(actionXmlElement)

    #    return resultStr

    def ApplicationCommand(self, actionDefn, actionContext, actionXmlElement):
        resultStr = 'No command'
        command = ''
        infoElement = actionDefn.actionElement.getXmlElementByName("info")
        if infoElement:
            command = infoElement.getAttribute("command")
        if actionXmlElement:
            infoElement = actionXmlElement.getXmlElementByName("info")
            if infoElement:
                cmd = infoElement.getAttribute("command")
                if cmd: command = cmd
        if command:
            resultStr = ''
            objlist = actionContext.targets
            #self._canvas.raiseCanvasEvent(grob.CANVAS_APPLICATION_REQUEST_EVENT,
            #    objlist, command)
            application_data = self.getApplicationData(actionXmlElement)
            objectsStr = self._canvas.diagram().saveObjectList(objlist, indent = None, level = 0, saveDefaults = True)
            self._canvas.raiseCanvasApplicationRequestEvent(application_data, command, '', objectsStr)
        return resultStr

    def ExplodeGroup(self, actionDefn, actionContext, actionXmlElement):
        if len(actionContext.targets) == 1 and actionContext.targets[0].category() == "group":
            pass
            topObjlist = list(map(toplevelise, actionContext.targets))
            initObjectsSaved = ''
            if actionContext.raiseEvent:
                if actionContext.initTargetsSaved:
                    initObjectsSaved = actionContext.initTargetsSaved
                else:
                    initObjectsSaved = self._canvas.diagram().saveObjectList(topObjlist, indent=None, level=0,
                                                                             saveDefaults=True)
            initSelectionSaved = self.getInitSelectionSaved(actionContext)
            explodedObjects = self._canvas.diagram().explodeGroup(actionContext.targets[0])
            insertedObjects = explodedObjects
            deletedObjects = actionContext.targets

            self._canvas.diagram().deleteObjects(deletedObjects)

            if actionContext.raiseEvent:
                deletedObjectsStr = self._canvas.diagram().saveObjectList(deletedObjects, indent=None, level=0,
                                                                          saveDefaults=True)
                insertedObjectsStr = self._canvas.diagram().saveObjectList(insertedObjects, indent=None, level=0,
                                                                           saveDefaults=True)
                application_data = self.getApplicationData(actionXmlElement)
                self._canvas.raiseCanvasChangedObjects(application_data,
                                                       '',  # infoStr
                                                       initSelectionSaved,
                                                       deletedObjectsStr,
                                                       initObjectsSaved,
                                                       '',  # updatedObjectsStr,
                                                       insertedObjectsStr)

    def GroupObjects(self, actionDefn, actionContext, actionXmlElement):
        if len(actionContext.targets) > 1:
            fixed = True
            infoElement = actionDefn.actionElement.getXmlElementByName("info")
            if infoElement:
                value = infoElement.getAttribute('fixed')
                if value == "true":
                    fixed = True
                elif value == "false":
                    fixed = False
            pass
            topObjlist = list(map(toplevelise, actionContext.targets))
            initObjectsSaved = ''
            if actionContext.raiseEvent:
                if actionContext.initTargetsSaved:
                    initObjectsSaved = actionContext.initTargetsSaved
                else:
                    initObjectsSaved = self._canvas.diagram().saveObjectList(topObjlist, indent=None, level=0,
                                                                             saveDefaults=True)
            initSelectionSaved = self.getInitSelectionSaved(actionContext)
            insertedGroup = self._canvas.diagram().groupObjects(actionContext.targets, fixed)
            insertedObjects = [insertedGroup]
            deletedObjects = actionContext.targets

            self._canvas.diagram().deleteObjects(deletedObjects)

            if actionContext.raiseEvent:
                deletedObjectsStr = self._canvas.diagram().saveObjectList(deletedObjects, indent=None, level=0,
                                                                          saveDefaults=True)
                insertedObjectsStr = self._canvas.diagram().saveObjectList(insertedObjects, indent=None, level=0,
                                                                           saveDefaults=True)
                application_data = self.getApplicationData(actionXmlElement)
                self._canvas.raiseCanvasChangedObjects(application_data,
                                                       '',  # infoStr
                                                       initSelectionSaved,
                                                       deletedObjectsStr,
                                                       initObjectsSaved,
                                                       '',  # updatedObjectsStr,
                                                       insertedObjectsStr)

    def SetZOrder(self, actionDefn, actionContext, actionXmlElement):
        resultStr = ''
        option = ""
        value = ""
        infoElement = actionDefn.actionElement.getXmlElementByName("info")
        if infoElement:
            option = infoElement.getAttribute('option')
            value = infoElement.getAttribute('value')
        if actionXmlElement:
            infoElement = actionXmlElement.getXmlElementByName("info")
            if infoElement:
                option = infoElement.getAttribute('option')
                toValue = infoElement.getAttribute('value')
        objlist = actionContext.targets
        if len(objlist) == 0:
            objlist = self.getObjectsFromXmlElementByIds(actionXmlElement)

        doUpdateDiagramZOrder = False
        newZOrderedObjectIds = []
        if (option == "swap" and len(objlist) == 2) or len(objlist) == 1:
            initSelectionSaved = self.getInitSelectionSaved(actionContext)
            initObjectsSaved = ''
            if actionContext.raiseEvent:
                if actionContext.initTargetsSaved:
                    initObjectsSaved = actionContext.initTargetsSaved
                else:
                    initObjectsSaved = self._canvas.diagram().saveObjectList(objlist, indent=None, level=0, saveDefaults=True, includeZOrder=True)
            if option == "swap":
                obj1Id = objlist[0].objectId()
                obj1ZOrder = objlist[0].getZOrder()
                obj2Id = objlist[1].objectId()
                obj2ZOrder = objlist[1].getZOrder()
                newZOrderedObjectIds, newZOrder = self._canvas.diagram().changeZOrder(obj1Id, None, "to", obj2ZOrder)
                if newZOrder != 0 and newZOrder != obj1ZOrder:
                    newZOrderedObjectIds, newZOrder = self._canvas.diagram().changeZOrder(obj2Id, newZOrderedObjectIds, "to", obj1ZOrder)
                    doUpdateDiagramZOrder = True
            elif option in ["top", "up", "down", "bottom", "to"]:
                toZOrder = 0
                if value:
                    toZOrder = int(value)
                objectId = objlist[0].objectId()
                objZOrder = objlist[0].getZOrder()
                newZOrderedObjectIds, newZOrder = self._canvas.diagram().changeZOrder(objectId, None, option, toZOrder)
                if newZOrder != 0 and newZOrder != objZOrder:
                    doUpdateDiagramZOrder = True
            pass
            if doUpdateDiagramZOrder:
                self._canvas.diagram().updateDiagramObjectsZOrders(newZOrderedObjectIds)

                if actionContext.raiseEvent:
                    application_data = self.getApplicationData(actionXmlElement)
                    updatedObjectsStr = self._canvas.diagram().saveObjectList(objlist, indent = None, level = 0, saveDefaults = True, includeZOrder=True)
                    self._canvas.raiseCanvasChangedObjects(application_data,
                                                           '',
                                                           initSelectionSaved,
                                                           '',
                                                           initObjectsSaved,
                                                           updatedObjectsStr,
                                                           '')
                    self._canvas.interactions().raiseCanvasSelectedObjects()
                # redraw everything
                self._canvas.Refresh()
        return resultStr
