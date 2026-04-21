#! /usr/bin/python

import wx

from . import canvas as grob
from .diagram import Diagram
from .selection import Selection
from .actions import ActionContext
from .contextmenus import ContextMenus
from .keyshortcuts import Keyshortcuts
from .object import Object, Composite, toplevelise
from .connectable import Connectable
from .node import Node
from .port import Port

UseDoInteractions = True

class InteractionStateInfo(object):
    def __init__(self, interactions):
        self._interactions = interactions
        self.thisPtr = None # where mouse ptr is - set by canvas (with setMousePointer) in diagram coords before handling mouse event
        self.lastPtr = None # where mouse ptr was last time - set by canvas
        self.interaction = '' # set at commencement of each processed mouse interaction
        self.operation = 'normal'
        self.dc = None
        self.downPtr = None # where mouse ptr was last down - set here in setDownInfo
        self.modifiers = 0
        self.actionTarget = None
        self.hit = None
        self.component = None
        self.grab = None
        self.at = None
        self.hasMoved = False
        self.inDrag = False
        self.inGrab = False
        self.hadDClick = False
        self.extendingLink = None
        self.rubberband = None # or of no size
        self.initTargetsSaved = ''
        self.initSelectionSaved = ''

    def __str__(self):
        s = '<InteractionStateInfo interaction=' + str(self.interaction)
        s += ' operation='+str(self.operation)
        s += ' modifiers=' + str(self.modifiers)
        s += ' actionTarget=' + str(self.actionTarget)
        s += ' hit=' + str(self.hit)
        s += ' component=' + str(self.component)
        s += ' grab=' + str(self.grab)
        s += ' at=' + str(self.at)
        s += ' hasMoved=' + str(self.hasMoved)
        s += ' inDrag=' + str(self.inDrag)
        s += ' inGrab=' + str(self.inGrab)
        s += ' hadDClick=' + str(self.hadDClick)
        #s += ' extendingLink=' + str(self.extendingLink)
        #s += ' rubberband=' + str(self.rubberband)
        s += '>'
        return s

class Interactions(object):
    def __init__(self, canvas):
        self._canvas = canvas
        self._selection = Selection(self)
        self._mouseInteractions = {}
        self._contextmenus = ContextMenus(self, canvas)
        self._keyshortcuts = Keyshortcuts(self)

        self._diagram = None

        self._stateInfo = InteractionStateInfo(self)
        self._refreshCache = None
        self.clearState()
        self.debugging = False

    def canvas(self): return self._canvas
    def selection(self): return self._selection
    def contextmenus(self): return self._contextmenus
    def keyshortcuts(self): return self._keyshortcuts

    def clearInteractionsDefinitions(self):
        self._mouseInteractions = {}
        self._contextmenus.clearContextMenuDefinitions()
        self._keyshortcuts.clearKeyshortcutDefinitions()

    def setInteractionDefinitions(self, canvasDefinitions):
        self._diagram = self._canvas.diagram()
        self._contextmenus.setContextMenuDefinitions(canvasDefinitions)
        self._keyshortcuts.setKeyshortcutDefinitions(canvasDefinitions)
        self.loadMouseInteractionsFromXml(canvasDefinitions)
        self._dragUpdateCount = self._diagram.properties().DragUpdateCount
        self._dragUpdate = 0

    def loadMouseInteractionsFromXml(self, xmlElement):
        if xmlElement:
            if xmlElement.name() == "interactions": interactionsElements = [xmlElement]
            else: interactionsElements = xmlElement.getXmlElementListByName("interactions", True)
            if interactionsElements:
                for interactionsElement in interactionsElements:
                    interactionElements = interactionsElement.getXmlElementListByName("interaction", False)
                    for interactionElement in interactionElements:
                        mouseInteraction = interactionElement.getAttribute("mouse")
                        if mouseInteraction not in self._mouseInteractions:
                            self._mouseInteractions[mouseInteraction] = [ interactionElement ]
                        else:
                            self._mouseInteractions[mouseInteraction].append(interactionElement)

    def setMousePointer(self, currentPtr):
        self._stateInfo.lastPtr = self._stateInfo.thisPtr
        #currentPtr = self._diagram.snapPoint(currentPtr) # too global? only want this when drag/move/end-node? - what about hits? - they can miss
        self._stateInfo.thisPtr = currentPtr

    def clearState(self, keepSelection = False):
        rect = None
        if not keepSelection: self.resetSelection()
        if self._stateInfo.operation == "linking" and self._stateInfo.extendingLink is not None:
            self._diagram.removeLink(self._stateInfo.extendingLink)
        self._stateInfo.extendingLink = None
        if self._stateInfo.operation == "rubberbanding" and self._stateInfo.rubberband: # has a size
            rect = self._stateInfo.rubberband
            rect = rect.Inflate(1, 1)
        self._stateInfo.rubberband = None
        if rect is not None:
            self._canvas.refreshExtent(rect)
        self._stateInfo.operation = 'normal'

    def removeFromSelection(self, objOrList = None):
        if objOrList is not None:
            if isinstance(objOrList, list):
                for obj in objOrList:
                    self._selection.remove(obj)
            else:
                self._selection.remove(objOrList)

    def resetSelection(self, objOrList = None):
        if self._selection.len() > 0:
            self._selection.map(Object.setSelected, False) # not polymorphic
        self._selection.clear()
        if objOrList is not None:
            if isinstance(objOrList, list):
                for it in objOrList:
                    self.selectObject(it)
            else:
                self.selectObject(objOrList)

    def raiseCanvasSelectedObjects(self):
        objectsStr = self._diagram.saveObjectList(self._selection.selection(), indent = None, level = 0, saveDefaults = True)
        self._canvas.raiseCanvasSelectedObjectsEvent(objectsStr)

    def selectObject(self, obj):
        if obj.selectable():
            self._selection.add(obj)
            obj.setSelected(True)

    def deselectObject(self, obj):
        self._selection.remove(obj)
        obj.setSelected(False)

    def checkHit(self, ptr, excludeObjs):
        hit = self._diagram.getObject(ptr, toplevel = True) # try toplevel object
        if hit in excludeObjs: hit = None
        if not hit:
            hit = self._diagram.getNode(ptr) # try toplevel node
        if hit in excludeObjs: hit = None
        if not hit:
            # try toplevel link - but not the current link being extended (if any)
            hit = self._diagram.getLink(ptr, excludeObjs)
        return hit

    def setDownInfo(self, evt, dc):
        self._stateInfo.dc = dc
        self._stateInfo.downPtr = self._stateInfo.thisPtr
        #self._stateInfo.modifiers = evt.GetModifiers() #<< when 2.9.?
        self._stateInfo.modifiers = 0
        if evt.AltDown(): self._stateInfo.modifiers += 1
        if evt.ControlDown(): self._stateInfo.modifiers += 2
        if evt.ShiftDown(): self._stateInfo.modifiers += 4
        ptr = self._stateInfo.thisPtr
        self._stateInfo.hit = self.checkHit(ptr, [self._stateInfo.extendingLink])
        self._stateInfo.component = None
        self._stateInfo.grab = None
        if self._stateInfo.hit:
            hitCategory = self._stateInfo.hit.category()
            if hitCategory == "entity" or hitCategory == "display":
                self._stateInfo.component = self._diagram.getPort(ptr) # see if on a port
            if not self._stateInfo.component and (hitCategory == "entity" or hitCategory == "display" or hitCategory == "info" or hitCategory == "group"):
                self._stateInfo.component = self._diagram.getObject(ptr, toplevel = False)
                if self._stateInfo.component: # see if in an annotation
                    obj = self._stateInfo.component
                    while obj._parent is not None:
                        if obj._parent.type() == "annotation":
                            self._stateInfo.component = obj._parent
                            break
                        else:
                            obj = obj._parent
            grab = None
            if self._stateInfo.hit:
                grab = self._stateInfo.hit.checkHitGrab(ptr)
            if not grab and self._stateInfo.component:
                grab = self._stateInfo.component.checkHitGrab(ptr)
            if grab:
                self._stateInfo.grab = grab
        self._stateInfo.hasMoved = False
        self._stateInfo.inDrag = False
        self._stateInfo.inGrab = False
        self._stateInfo.hadDClick = False
        #self._stateInfo.extendingLink = None
        #self._stateInfo.rubberband = None # or of no size
        self._stateInfo.initTargetsSaved = ''
        self._stateInfo.initSelectionSaved = ''
        self.at = None

    def onMouseLeftDown(self, evt, dc):
        self._stateInfo.interaction = "left-down"
        self.doInteractions(evt, dc)

    def onMouseLeftUp(self, evt, dc):
        if not self._stateInfo.hadDClick: # Second Up after a DClick - clears it
            self._stateInfo.interaction = "left-up"
            #if self._canvas.HasCapture():
            #    self._canvas.ReleaseMouse()
            self.doInteractions(evt, dc)
        else:
            self._stateInfo.hadDClick = False

    def onMouseLeftDClick(self, evt, dc):
        #note: see sequence:
        #>grob.Interactions.onMouseUp state=normal
        #>grob.Interactions.onMouseDown state=normal
        #>grob.Interactions.onMouseUp state=dragging
        #>grob.Interactions.onMouseDClick state=normal
        #>grob.Interactions.onMouseUp state=normal
        self._stateInfo.interaction = "left-dclick"
        self._stateInfo.hadDClick = True
        self.doInteractions(evt, dc)

    def onMouseRightDown(self, evt, dc):
        self._stateInfo.interaction = "right-down"
        self.doInteractions(evt, dc)

    def onMouseRightUp(self, evt, dc):
        if not self._stateInfo.hadDClick: # Second Up after a DClick - clears it
            self._stateInfo.interaction = "right-up"
            self.doInteractions(evt, dc)
        else:
            self._stateInfo.hadDClick = False

    def onMouseRightDClick(self, evt, dc):
        self._stateInfo.interaction = "right-dclick"
        self._stateInfo.hadDClick = True
        self.doInteractions(evt, dc)

    def onMouseMiddleDown(self, evt, dc):
        self._stateInfo.interaction = "middle-down"
        self.doInteractions(evt, dc)

    def onMouseMiddleUp(self, evt, dc):
        if not self._stateInfo.hadDClick: # Second Up after a DClick - clears it
            self._stateInfo.interaction = "middle-up"
            self.doInteractions(evt, dc)
        else:
            self._stateInfo.hadDClick = False

    def onMouseMiddleDClick(self, evt, dc):
        self._stateInfo.interaction = "middle-dclick"
        self._stateInfo.hadDClick = True
        self.doInteractions(evt, dc)

    def onMouseMove(self, evt, dc):
        self._stateInfo.interaction = "mouse-move"
        ptr = self._stateInfo.thisPtr
        if self._refreshCache is None:
            self._refreshCache = wx.Rect()
        if ptr != self._stateInfo.downPtr:
            self._stateInfo.hasMoved = True
        if self._stateInfo.operation == "dragging" and self._selection.len() > 0:
            # Check if out of bounds
            ext = self._selection.extent()
            displacement = ptr - self._stateInfo.lastPtr
            ext.Offset(displacement)
            diagramView = self._canvas.GetVisibleDiagramArea()
            #print("ext="+str(ext)+" diagramView="+str(diagramView))
            margin = 5 # inner margin
            indent = 2 # additional indent (so as not to be caught here again next drag)
            diagramView = diagramView.Inflate(-margin)
            if (ext.x <= diagramView.x or ext.x + ext.width >= diagramView.x + diagramView.width or
                ext.y <= diagramView.y or ext.y + ext.height >= diagramView.y + diagramView.height):
                if ext.x <= diagramView.x:
                    displacement.x += diagramView.x - ext.x + indent
                if ext.x + ext.width >= diagramView.x + diagramView.width:
                    displacement.x += diagramView.x + diagramView.width - (ext.x + ext.width) - indent
                if ext.y <= diagramView.y:
                    displacement.y += diagramView.y - ext.y + indent
                if ext.y + ext.height >= diagramView.y + diagramView.height:
                    displacement.y += diagramView.y + diagramView.height - (ext.y + ext.height) - indent
                if self._stateInfo.hasMoved and not self._stateInfo.inDrag:
                    self._stateInfo.inDrag = True
                    for obj in self._selection.selection():  # polymorphic
                        obj.startDragging()
                for obj in self._selection.selection(): # polymorphic
                    obj.dragBy(dc, displacement, self._refreshCache)
                for obj in self._selection.selection(): # polymorphic
                    obj.stopDragging()
                self._stateInfo.operation = "normal"
                self.onLeaving(evt, dc)
            else:
                if self._diagram.gridSnap() != 0:
                    displacement = self._diagram.snapPoint(ptr) - self._diagram.snapPoint(self._stateInfo.lastPtr) # snap dragin' objects
                    if self._selection.len() == 1: # single top-level object
                        obj = self._selection.get(0)
                        if obj.parent() == None:
                            origin = obj.position()
                            displacement += origin - self._diagram.snapPoint(origin)
                if self._stateInfo.hasMoved and not self._stateInfo.inDrag:
                    self._stateInfo.inDrag = True
                    for obj in self._selection.selection():  # polymorphic
                        obj.startDragging()
                #if self._selection.len() == 1:
                #    selected = self._selection.get(0)
                #    #if isinstance(selected, Node):
                #    selected.dragBy(dc, displacement)
                #else:
                for obj in self._selection.selection(): # polymorphic
                    obj.dragBy(dc, displacement, self._refreshCache)
            if self._dragUpdateCount > 0:
                self._dragUpdate += 1
                if self._dragUpdate == self._dragUpdateCount:
                    self._canvas.Update()
                    self._dragUpdate = 0
        elif self._stateInfo.operation == "linking" and self._stateInfo.extendingLink is not None:
            ptr = self._diagram.snapPoint(ptr)  # snap dragin' link end
            self._stateInfo.thisPtr = ptr
            self._stateInfo.extendingLink.dragLinkEnd(dc, ptr, self._refreshCache)
            # check if over another connectable
            hit = self._diagram.getNode(ptr)  # try toplevel node
            if not hit:
                hit = self._diagram.getPort(ptr)  # see if on a port
            if hit:
                # TODO see if can make a connection
                if self.debugging:
                    print("hit connectable "+str(hit))
                pass

        elif self._stateInfo.operation == "rubberbanding":
            # d
            x = min(self._stateInfo.downPtr.x, self._stateInfo.thisPtr.x)
            y = min(self._stateInfo.downPtr.y, self._stateInfo.thisPtr.y)
            w = abs(self._stateInfo.downPtr.x - self._stateInfo.thisPtr.x)
            h = abs(self._stateInfo.downPtr.y - self._stateInfo.thisPtr.y)
            self._stateInfo.rubberband = wx.Rect(x, y, w, h)
            if self._stateInfo.lastPtr:
                x = min(x, self._stateInfo.lastPtr.x)
                y = min(y, self._stateInfo.lastPtr.y)
                w = max(w, abs(self._stateInfo.downPtr.x - self._stateInfo.lastPtr.x))
                h = max(h, abs(self._stateInfo.downPtr.y - self._stateInfo.lastPtr.y))
            rect = wx.Rect(x, y, w, h)
            rect = rect.Inflate(1, 1)
            self._canvas.refreshExtent(rect)

        elif self._stateInfo.operation == "grabbing":
            displacement = self._diagram.snapPoint(ptr) - self._diagram.snapPoint(self._stateInfo.lastPtr)
            if self._stateInfo.grab:
                if not self._stateInfo.inGrab:
                    self._stateInfo.inGrab = True
                    self._stateInfo.grab.startGrabDragging() # use the grab object
                self._stateInfo.grab.grabDragBy(displacement)
                #self._stateInfo.grab.grabbedObject.grabDragBy(dc, self._stateInfo.grab, displacement)
            pass

        elif self._stateInfo.operation == "panning":
            deltaX = ptr.x - self._stateInfo.downPtr.x
            deltaY = ptr.y - self._stateInfo.downPtr.y
            if deltaX != 0 or deltaY != 0:
                self._canvas.panDiagram(deltaX, deltaY) # This pans just in the view by scrolling - is jerky due to CANVAS_SCROLL_RATE(20pixels).
            pass

        if self._refreshCache is not None and (self._refreshCache.width != 0 and self._refreshCache.height != 0):
            self._canvas.refreshExtent(self._refreshCache)
        self._refreshCache = None

    def onLeaving(self, evt, dc):
        self._stateInfo.interaction = "mouse-leaving"
        if evt.LeftIsDown():
            self.onMouseLeftUp(None, dc)
        else:
            self.clearState(keepSelection = True)

    def onEntering(self, evt, dc):
        self._stateInfo.interaction = "mouse-entering"
        #if evt.LeftIsDown():
        #     print "*grob.Interactions.onEntering has left down"

    def onMouseWheel(self, evt, dc):
        self._stateInfo.interaction = "mouse-wheel"
        rotn = evt.GetWheelRotation()
        delta = evt.GetWheelDelta()
        if evt.ControlDown():
            scale = self._canvas.GetScale()
            scale = scale * (1 + float(rotn) / float(10 * delta))
            self._canvas.SetScale(scale, self._stateInfo.thisPtr)
        else:
            xs, ys = self._canvas.GetViewStart()
            ys -= float(rotn) / float(delta)
            self._canvas.Scroll(round(xs), round(ys))

    def onKeyDown(self, evt, dc):
        self._keyshortcuts.onKeyDown(evt, dc)

    def startOfInteraction(self):
        startInteraction = False
        startInteraction = (self._stateInfo.interaction == "left-down" or self._stateInfo.interaction == "right-down"
                            or self._stateInfo.interaction == "middle-down")
        return startInteraction

    def matchCondition(self, conditionElement, evt, dc):
        condition = True
        modifier = conditionElement.getAttribute('modifier')
        state = conditionElement.getAttribute('state')
        selection = conditionElement.getAttribute('selection')
        hit = conditionElement.getAttribute('hit')
        hitSelected = conditionElement.getAttribute('hit-selected')
        anyComponentSelected = conditionElement.getAttribute('any-component-selected')
        aboveComponentSelected = conditionElement.getAttribute("above-component-selected")
        drillDownable = conditionElement.getAttribute("drill-downable")
        component = conditionElement.getAttribute('component')
        grabHit = conditionElement.getAttribute('grab-hit')
        componentSelected = conditionElement.getAttribute('component-selected')
        hasMoved = conditionElement.getAttribute('has-moved')
        conditionTarget = 'none'
        at = conditionElement.getAttribute('at')
        #modifier=           any|none|alt|ctrl|shift (only support one modifier)
        #if self._stateInfo.interaction == 'left-up':
        if self._stateInfo.interaction == 'left-dclick':
            pass
        if modifier and modifier != "any":
            if modifier == "none":
                condition = (self._stateInfo.modifiers == 0)
            elif modifier == "alt":
                condition = (self._stateInfo.modifiers == 1)
            elif modifier == "ctrl":
                condition = (self._stateInfo.modifiers == 2)
            elif modifier == "shift":
                condition = (self._stateInfo.modifiers == 4)
        #state= any|normal|<operation> currently=rubberbanding|dragging|linking
        if condition:
            if state and state != "any" and state != self._stateInfo.operation:
                condition = False
        if condition:
            #selection= any|none|multiple|one|<type>(if one)
            if selection and selection != "any":
                nSelected = self._selection.len()
                if selection == "none":
                    condition = (nSelected == 0)
                elif selection == "one":
                    condition = (nSelected == 1)
                elif selection == "some": # 1+
                    condition = (nSelected > 0)
                elif selection == "multiple": #2+
                    condition = (nSelected > 1)
                elif nSelected != 1:    # here we are looking for a single selection of given category|type
                    condition = False
                elif nSelected == 1:
                    category = self._selection.get(0).category()
                    condition = (selection == category)
                    if not condition: # try type
                        type = self._selection.get(0).type()
                        condition = (selection == type)
        if condition:
            #hit=                any|none|one|<type>
            if hit and hit != "any":
                if hit == "none":
                    condition = (self._stateInfo.hit is None)
                elif hit == "one":
                    condition = (self._stateInfo.hit is not None)
                elif self._stateInfo.hit is None:    # here we are looking for a single hit of given category|type
                    condition = False
                else:
                    category = self._stateInfo.hit.category()
                    condition = (hit == category)
                    if not condition: # try type
                        type = self._stateInfo.hit.type()
                        condition = (hit == type)
        if condition:
            #hit-selected=       any|true|false
            if hitSelected and hitSelected != "any":
                if self._stateInfo.hit is None or not self._stateInfo.hit.selectable():
                    condition = False
                elif hitSelected == "true":
                    condition = self._stateInfo.hit.selected()
                elif hitSelected == "false":
                    condition = not self._stateInfo.hit.selected()
        if condition:
            #any-component-selected=       any|true|false
            if anyComponentSelected and anyComponentSelected != "any":
                if self._stateInfo.hit is None or not isinstance(self._stateInfo.hit, Composite):
                    condition = False
                else:
                    aComponentIsSelected = self._stateInfo.hit.anyComponentSelected()
                    if anyComponentSelected == "true":
                        condition = aComponentIsSelected
                    elif anyComponentSelected == "false":
                        condition = not aComponentIsSelected
        if condition:
            # above-component-selected=       any|true|false
            if aboveComponentSelected and aboveComponentSelected != "any":
                if self._stateInfo.component is None:
                    condition = False
                else:
                    aParentIsSelected = False
                    obj = self._stateInfo.component
                    while obj._parent is not None:
                        aParentIsSelected = obj._parent.selected()
                        if aParentIsSelected:
                            break
                        obj = obj._parent
                    if aboveComponentSelected == "true":
                        condition = aParentIsSelected
                    elif aboveComponentSelected == "false":
                        condition = not aParentIsSelected
        if condition:
            # drill-downable=       any|true|false
            if drillDownable and drillDownable != "any":
                canDrillDown = False
                if self._selection.len() == 1:
                    selectedObj = self._selection.get(0)
                    if selectedObj.category() == "group":
                        belowSelectionObj = None
                        obj = self._stateInfo.component
                        while obj._parent is not None:
                            if obj._parent == selectedObj:
                                belowSelectionObj = obj
                                break
                            obj = obj._parent
                        if belowSelectionObj is not None:
                            canDrillDown = belowSelectionObj.selectable()
                if drillDownable == "true":
                    condition = canDrillDown
                elif drillDownable == "false":
                    condition = not canDrillDown
        if condition:
            if at:
                self._stateInfo.at = self.checkHit(self._stateInfo.thisPtr, [self._stateInfo.hit, self._stateInfo.extendingLink])
                if at != 'any':
                    if at == "none":
                        condition = (self._stateInfo.at is None)
                    elif at == "one":
                        condition = (self._stateInfo.at is not None)
                    elif self._stateInfo.at is None:  # here we are looking for a single hit of given category|type
                        condition = False
                    else:
                        category = self._stateInfo.at.category()
                        condition = (at == category)
                        if not condition:  # try type
                            type = self._stateInfo.at.type()
                            condition = (at == type)
                if self._stateInfo.at:
                    atCategory = self._stateInfo.at.category()
                    self._stateInfo.component = None
                    if atCategory == "entity" or atCategory == "display":
                        self._stateInfo.component = self._diagram.getPort(self._stateInfo.thisPtr)  # see if on a port
                    if not self._stateInfo.component and (atCategory == "entity" or atCategory == "display" or atCategory == "group"):
                        self._stateInfo.component = self._diagram.getObject(self._stateInfo.thisPtr, toplevel=False)
        if condition:
            #component=          any|none|one|<type>
            if component and component != "any":
                if component == "none":
                    condition = (self._stateInfo.component is None)
                elif component == "one":
                    condition = (self._stateInfo.component is not None)
                elif self._stateInfo.component is None:    # here we are looking for a single component of given category|type
                    condition = False
                else:
                    category = self._stateInfo.component.category()
                    condition = (component == category)
                    if not condition: # try type
                        type = self._stateInfo.component.type()
                        condition = (component == type)
        if condition:
            #component-selected= any|true|false
            if componentSelected and componentSelected != "any":
                if self._stateInfo.component is None:
                    condition = False
                elif componentSelected == "true":
                    condition = self._stateInfo.component.selected()
                elif componentSelected == "false":
                    condition = not self._stateInfo.component.selected()
        if condition:
            #grabHit=               any|true|false
            if grabHit and grabHit != "any":
                if grabHit == "true":
                    condition = self._stateInfo.grab is not None
                elif grabHit == "false":
                    condition = self._stateInfo.grab is None
        if condition and not self.startOfInteraction():
            #has-moved=          any|true|false (? or a minimum distance ?) (this doesnt apply to ..-down interactions)
            if hasMoved and hasMoved != "any":
                self._stateInfo.hasMoved = max(abs(self._stateInfo.thisPtr.x - self._stateInfo.downPtr.x),
                                               abs(self._stateInfo.thisPtr.y - self._stateInfo.downPtr.y))
                if hasMoved == "true":
                    condition = self._stateInfo.hasMoved > 0
                elif hasMoved == "false":
                    condition = self._stateInfo.hasMoved == 0
                elif int(hasMoved) > 0:
                    condition = self._stateInfo.hasMoved >= int(hasMoved)
        if condition:
            if at:
                conditionTarget = 'at'
            elif component:
                if component != "none":
                    conditionTarget = 'component'
                else: # as "hit"
                    conditionTarget = 'hit'
            elif hit:
                conditionTarget = 'hit'
            elif selection:
                conditionTarget = 'selection'
        return condition, conditionTarget

    def doInteractions(self, evt, dc):
        if self.debugging:
            print('>doInterations '+str(self._stateInfo))
        effectElement = None
        conditionTarget = 'none'
        xmlElementList = self._mouseInteractions.get(self._stateInfo.interaction)
        if xmlElementList:
            if self.startOfInteraction():
                self.setDownInfo(evt, dc)
            i = 0
            for xmlElement in xmlElementList:
                modeOk = False
                if self._canvas.mode() == "editing":
                    modeOk = True
                elif self._canvas.mode() == "browsing":
                    browsable = xmlElement.getAttribute("browse")
                    if browsable and browsable == "true":
                        modeOk = True
                if modeOk:
                    id = xmlElement.getAttribute("id")
                    conditionElement = xmlElement.getXmlElementByName("condition", False)
                    condition = True
                    if conditionElement:
                        if self.debugging:
                            print('-doInterations id='+str(id)+' '+str(self._stateInfo.interaction)+' #'+str(i) + ' ?' + conditionElement.xml())
                        condition, conditionTarget = self.matchCondition(conditionElement, evt, dc)
                    if condition:
                        #self._stateInfo.actionTarget = conditionTarget
                        effectElement = xmlElement.getXmlElementByName("effect", False)
                        effectTxt = ''
                        if effectElement: effectTxt = effectElement.xml()
                        if self.debugging:
                            print('-doInterations id='+str(id)+' matches :'+effectTxt + ' hit=' + str(self._stateInfo.hit))
                        break
                    i += 1
            if effectElement:
                self.performEffect(effectElement, conditionTarget, evt, dc)

    def performEffect(self, effectElement, conditionTarget, evt, dc):
        if self.startOfInteraction():
            if len(self._selection.selection()) > 0:
                self._stateInfo.initSelectionSaved = self._diagram.saveObjectList(self._selection.selection(),
                                                                                  indent=None, level=0,
                                                                                  saveDefaults=True)
        select = effectElement.getAttribute('select')
        action = effectElement.getAttribute('action')
        actionTarget = effectElement.getAttribute('action-target')
        if not actionTarget: actionTarget = conditionTarget
        self._stateInfo.actionTarget = actionTarget
        operation = effectElement.getAttribute('operation')

        #select=             none|set|add|remove|clear|rubberband|component|top (none means we dont change the selection) (rubberband only for rubberbanding operation)
        ##target = None
        ##if conditionTarget == 'hit':
        ##    target = self._stateInfo.hit
        target = self._stateInfo.hit
        if conditionTarget == 'component' and self._stateInfo.component is not None:
            target = self._stateInfo.component
        elif conditionTarget == 'at':
            target = self._stateInfo.at
        if select and select != 'none':
            if select == 'set':
                self.resetSelection(target)
            elif select == 'add':
                if target.parent() is not None:
                    preventAdd = True
                else:
                    preventAdd = self._selection.mapTillTrue(lambda obj: obj._parent is not None)
                if not preventAdd:
                    self.selectObject(target)
            elif select == 'remove':
                self.deselectObject(target)
            elif select == 'clear':
                self.resetSelection()
            elif select == 'rubberband' and self._stateInfo.rubberband:
                objs = []
                if self._stateInfo.thisPtr != self._stateInfo.downPtr: # it moved
                    objs = self._diagram.getObjectsAndNodesInRect(self._stateInfo.rubberband)
                #############self.clearState()
                for obj in objs:
                    self.selectObject(obj)
            elif select == 'component':
                if self._stateInfo.component.selectable():
                    self.resetSelection(self._stateInfo.component)
            elif select == 'drill-down':
                obj = self._stateInfo.component
                while obj._parent is not None and not obj._parent.selected():
                    obj = obj._parent
                if obj and obj.selectable():
                    self.resetSelection(obj)
            elif select == 'hit':
                if self._stateInfo.hit.selectable():
                    self.resetSelection(self._stateInfo.hit)
            self.raiseCanvasSelectedObjects()

        #action=             none|<action>   to include (new) Activate|Context Menu
        if action and action != 'none':
            actionContext = ActionContext()
            actionContext.dc = dc
            actionContext.ptr = self._stateInfo.thisPtr
            actionContext.type = 'interaction'
            self.setActionContextTarget(actionContext, actionTarget)
            actionXmlElement = effectElement.getXmlElementByName("action")
            resultStr = self._canvas.actions().InvokeAction(action, actionContext, actionXmlElement)

        #operation=          none|normal|rubberbanding|dragging|linking|<others to be invented> (none means we dont change the operation)
        suppressChangeOperation = False
        if operation and operation != 'none':
            if self._stateInfo.operation != operation:
                # clean up current operation
                self.cleanUpCurrentOperation(dc, operation, target)

                # setup for new operation
                if not suppressChangeOperation:
                    if operation == 'normal':
                        self.clearState(keepSelection = True)
                    elif operation == 'new-link':
                        pass                # handled above
                    elif operation == 'rubberbanding':
                        self.clearState()
                        self._stateInfo.operation = operation
                    elif operation == 'dragging':
                        if self._selection.mapTillTrue(Object.draggable): # leave in current operation if nothing to drag
                            self.clearState(keepSelection = True)
                            self._stateInfo.operation = operation
                    elif operation == 'linking':
                        self.clearState(keepSelection=True)
                        # Start extending link
                        connectable = self._stateInfo.component
                        if not connectable or connectable.category() != "port":
                            connectable = self._stateInfo.hit
                            if connectable.category() != "node": connectable = None
                        if connectable:
                            link, errorMsg = connectable.startLink()
                            if link is not None:
                                self._stateInfo.operation = operation
                                self._stateInfo.extendingLink = link
                                #self.resetSelection() (done by select="clear")
                            else:
                                if errorMsg:
                                    self._canvas.raiseCanvasApplicationNotifyEvent('', "display", errorMsg)
                    elif operation == 'grabbing':
                        self.clearState(keepSelection = True)
                        self._stateInfo.operation = operation
                    elif operation == 'panning':
                        self.clearState(keepSelection = True)
                        self._stateInfo.operation = operation

                    # save init targets (text) for dragging, also grabbing
                    if self.startOfInteraction():
                        objList = []
                        if operation == 'dragging':
                            self._stateInfo.initTargetsSaved = ''
                            if actionTarget == 'selection':
                                objList = self._selection.selection()
                            elif actionTarget == 'hit':
                                if self._stateInfo.hit:
                                    objList = [ self._stateInfo.hit ]
                            elif actionTarget == 'component':
                                if self._stateInfo.component:
                                    objList = [ self._stateInfo.component ]
                            elif actionTarget == 'at':
                                if self._stateInfo.at:
                                    objList = [ self._stateInfo.at ]
                        elif operation == 'grabbing':
                            objList = [self._stateInfo.hit]
                        if len(objList) > 0:
                            objList = list(map(toplevelise, objList))
                            self._stateInfo.initTargetsSaved = self._diagram.saveObjectList(objList,
                                indent = None, level = 0, saveDefaults = True)
            pass

    def cleanUpCurrentOperation(self, dc, operation=None, target=None):
        # clean up rubberbanding
        if self._stateInfo.operation == 'rubberbanding':
            # This already covered by select="rubberband" above (if wasn't have code above here + raiseCanvasSelectedObjects)
            pass
        # clean up dragging
        elif self._stateInfo.operation == 'dragging':
            for obj in self._selection.selection():  # polymorphic
                obj.stopDragging()
            self._stateInfo.inDrag = False
            # Say we've just finished dragging here (if moved)
            if self._stateInfo.hasMoved and self._diagram.snapPoint(self._stateInfo.thisPtr) != self._diagram.snapPoint(self._stateInfo.downPtr):  # it has moved
                # Use Move action without performing action to produce the proper event
                action = "Move"
                actionContext = ActionContext()
                actionContext.dc = dc
                actionContext.ptr = self._stateInfo.thisPtr
                actionContext.type = 'interaction'
                # self.setActionContextTarget(actionContext, actionTarget)
                actionContext.targets = self._selection.selection()
                actionContext.initTargetsSaved = self._stateInfo.initTargetsSaved
                actionContext.initSelectionSaved = self._stateInfo.initSelectionSaved
                actionContext.suppressAction = True
                actionXmlElement = None
                resultStr = self._canvas.actions().InvokeAction(action, actionContext, actionXmlElement)
            if self._selection.len() > 0:
                if isinstance(self._selection.get(0), Node):
                    self.resetSelection()
        # clean up linking
        elif self._stateInfo.operation == 'linking':
            # Possibly end link (abort-link, on connectable, on canvas)
            if self._stateInfo.extendingLink is not None:
                # abort link
                if operation == "abort-link":
                    self.clearState(keepSelection=True)
                    self._stateInfo.operation = "normal"
                    operation = "normal"
                else:
                    # see if end on connectable (not start of extending link)
                    connectable = self._stateInfo.component
                    if not connectable or connectable.category() != "port":
                        connectable = target
                        if connectable and connectable.category() != "node":
                            connectable = None
                    if connectable and connectable == self._stateInfo.extendingLink.startObject():
                        connectable = None
                    if connectable:
                        # use Join Link action to end this extending link
                        action = "Join Link"
                        actionContext = ActionContext()
                        actionContext.dc = dc
                        actionContext.ptr = self._stateInfo.thisPtr
                        actionContext.type = 'interaction'
                        actionContext.targets = [self._stateInfo.extendingLink, connectable]  # link & connectable
                        actionContext.initTargetsSaved = ''
                        actionContext.initSelectionSaved = self._stateInfo.initSelectionSaved
                        actionXmlElement = None
                        resultStr = self._canvas.actions().InvokeAction(action, actionContext, actionXmlElement)
                        if resultStr:  # error joining - continue as before
                            suppressChangeOperation = True
                        else:
                            self._stateInfo.extendingLink = None  # so clearState wont detach it
                            self.clearState()
                    else:
                        # see if end on canvas
                        if target is None:
                            node = None
                            # use Create Node End Link action to end this extending link on a new node
                            action = "Create Node End Link"
                            actionContext = ActionContext()
                            actionContext.dc = dc
                            self._stateInfo.thisPtr = self._diagram.snapPoint(
                                self._stateInfo.thisPtr)  # node at link end
                            actionContext.ptr = self._stateInfo.thisPtr
                            actionContext.type = 'interaction'
                            actionContext.targets = [self._stateInfo.extendingLink]  # link
                            actionContext.initTargetsSaved = ''
                            actionContext.initSelectionSaved = self._stateInfo.initSelectionSaved
                            actionXmlElement = None
                            resultStr = self._canvas.actions().InvokeAction(action, actionContext, actionXmlElement)
                            if not resultStr:
                                node = self._stateInfo.extendingLink.endObject()
                                self._stateInfo.extendingLink = None
                            if node and operation == 'new-link':  # add new link after node
                                link, errorMsg = node.startLink()
                                if link is not None:
                                    self._stateInfo.downPtr = node.position()  # Consider as a fresh start
                                    self._stateInfo.operation = "linking"
                                    self._stateInfo.extendingLink = link
                                else:
                                    self._stateInfo.operation = "normal"
                                    if errorMsg:
                                        self._canvas.raiseCanvasApplicationNotifyEvent('', "display", errorMsg)
                        else:
                            # just clear the extending link
                            self._diagram.removeLink(self._stateInfo.extendingLink)
                            self._stateInfo.extendingLink = None
                            self._stateInfo.operation = operation

        # clean up grabbing
        elif self._stateInfo.operation == "grabbing":
            if self._stateInfo.grab:
                self._stateInfo.grab.stopGrabDragging()
            self._stateInfo.inGrab = False
            if self._stateInfo.hasMoved:  # it moved
                # Use Update action without performing action to produce the proper event
                action = "Update"
                actionContext = ActionContext()
                actionContext.dc = dc
                actionContext.ptr = self._stateInfo.thisPtr
                actionContext.type = 'interaction'
                # self.setActionContextTarget(actionContext, actionTarget)
                actionContext.targets = self._selection.selection()
                actionContext.initTargetsSaved = self._stateInfo.initTargetsSaved
                actionContext.initSelectionSaved = self._stateInfo.initSelectionSaved
                actionContext.suppressAction = True
                actionXmlElement = None
                resultStr = self._canvas.actions().InvokeAction(action, actionContext, actionXmlElement)

        # anything else - leave

    def ContextMenuActionContext(self):
        actionContext = ActionContext()
        actionContext.dc = self._stateInfo.dc
        actionContext.ptr = self._stateInfo.downPtr
        actionContext.type = 'context-menu-item'
        self.setActionContextTarget(actionContext, self._stateInfo.actionTarget)
        return actionContext

    def setActionContextTarget(self, actionContext, actionTarget):
        actionContext.targets = []
        if actionTarget == 'selection':
            actionContext.targets = self._selection.selection()
        elif actionTarget == 'hit' and self._stateInfo.hit:
            actionContext.targets = [ self._stateInfo.hit ]
        elif actionTarget == 'component' and self._stateInfo.component:
            actionContext.targets = [self._stateInfo.component]
        elif actionTarget == 'at' and self._stateInfo.at:
            actionContext.targets = [ self._stateInfo.at ]
        actionContext.initTargetsSaved = self._stateInfo.initTargetsSaved
        actionContext.initSelectionSaved = self._stateInfo.initSelectionSaved

    def Draw(self, dc):
        if self._stateInfo.operation == 'rubberbanding' and self._stateInfo.rubberband: # has size
            dc.SetPen(wx.BLACK_PEN)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangle(self._stateInfo.rubberband.x, self._stateInfo.rubberband.y,
                             self._stateInfo.rubberband.width, self._stateInfo.rubberband.height)
