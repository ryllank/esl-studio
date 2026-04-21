#! /usr/bin/python

import wx

from .. import xmlutil as xut

from .diagram import Diagram
from .actions import Actions
from .interactions import Interactions
from .canvasdroptarget import CanvasDropTarget

GrobVersionString = "0.1.0"


# operations on Canvas
# configure - register entity node link & port types
# - may include conection interaction specfication
# load; save
# undo; redo (?be notified when anything to undo/redo)
# iterate over grobs (does this mean expose the structure?) retrieving info (eg. for code gen)
# set to be notified:
# - when selection set changes -eg for property display
# - when a connection (?perhaps that goes back to a port is made (or broken) [consider right of veto? no - treat as broadcast ?multiple]

# Constants
CANVAS_SCROLL_RATE = 20  # pixels per scroll-unit - fixed

# Canvas events
CANVAS_SELECTED_OBJECTS_EVENT = wx.NewEventType()
CANVAS_CHANGED_OBJECTS_EVENT = wx.NewEventType()
CANVAS_APPLICATION_REQUEST_EVENT = wx.NewEventType()
CANVAS_APPLICATION_NOTIFY_EVENT = wx.NewEventType()
#CANVAS_DELETED_OBJECTS_EVENT = wx.NewEventType()
#CANVAS_CHANGED_OBJECTS_EVENT = wx.NewEventType()
#CANVAS_DRAGGED_OBJECTS_EVENT = wx.NewEventType()
#CANVAS_LINKED_OBJECTS_EVENT = wx.NewEventType()
#CANVAS_CLIP_REQUESTED_EVENT = wx.NewEventType()
#CANVAS_PASTE_REQUESTED_EVENT = wx.NewEventType()
# ??? CANVAS_MOVED_OBJECTS_EVENT
# ??? CANVAS_CONTEXTMENU_ITEM_EVENT

CanvasEventType = {
    "selected_objects":       CANVAS_SELECTED_OBJECTS_EVENT,
    "changed_objects":        CANVAS_CHANGED_OBJECTS_EVENT,
    "application_request":    CANVAS_APPLICATION_REQUEST_EVENT,
    "application_notify":     CANVAS_APPLICATION_NOTIFY_EVENT }


# These must be imported in grob's __init__.py
EVT_CANVAS_SELECTED_OBJECTS = wx.PyEventBinder(CANVAS_SELECTED_OBJECTS_EVENT, 0)
EVT_CANVAS_CHANGED_OBJECTS = wx.PyEventBinder(CANVAS_CHANGED_OBJECTS_EVENT, 0)
EVT_CANVAS_APPLICATION_REQUEST = wx.PyEventBinder(CANVAS_APPLICATION_REQUEST_EVENT, 0)
EVT_CANVAS_APPLICATION_NOTIFY = wx.PyEventBinder(CANVAS_APPLICATION_NOTIFY_EVENT, 0)
#EVT_CANVAS_CREATED_OBJECTS = wx.PyEventBinder(CANVAS_CREATED_OBJECTS_EVENT, 0) #evtType, expectedIDs(0..2)=#ids for Bind
#EVT_CANVAS_DELETED_OBJECTS = wx.PyEventBinder(CANVAS_DELETED_OBJECTS_EVENT, 0)
#EVT_CANVAS_DRAGGED_OBJECTS = wx.PyEventBinder(CANVAS_DRAGGED_OBJECTS_EVENT, 0)
#EVT_CANVAS_LINKED_OBJECTS = wx.PyEventBinder(CANVAS_LINKED_OBJECTS_EVENT, 0)
#EVT_CANVAS_CLIP_REQUESTED = wx.PyEventBinder(CANVAS_CLIP_REQUESTED_EVENT, 0)
#EVT_CANVAS_PASTE_REQUESTED = wx.PyEventBinder(CANVAS_PASTE_REQUESTED_EVENT, 0)

class CanvasEvent(wx.PyCommandEvent): # or wx.PyEvent
    def __init__(self, evtType):
        wx.PyCommandEvent.__init__(self, evtType)
        #self.objects = ''
        self.data = ''
        self.application_data = ''

    def __str__(self):
        s = '<CanvasEvent type=' + str(self.GetEventType())
        s += ' source=' + str(self.GetEventObject())
        s += ' id=' + str(self.GetId())
        s += '>'
        return s

#global/class data
_allocatedCanvasNr = 0

class Canvas(wx.ScrolledWindow):

    # ScrolledWindow units:
    # logical (for diagram)
    # device ??? is this the same as pixels
    # scroll-units
    def __init__(self, parent = None, id = -1, pos = wx.DefaultPosition,
                 size = wx.DefaultSize, style = wx.BORDER, name = "Canvas"):
        global _allocatedCanvasNr
        wx.ScrolledWindow.__init__(self, parent, id, pos, size, style, name)

        # Set scrollbars for canvas 1000x1000 pixels
        #self.SetScrollbars(20, 20, 50, 50)  #XPT if scroll RefreshRect is not aligned

        _allocatedCanvasNr += 1
        self._canvasId = str(_allocatedCanvasNr)

        self._scale = 1.0
        self.SetVirtualSize(wx.Size(1000, 1000)) # Gets changed when SetScale etc
        self.SetScrollRate(CANVAS_SCROLL_RATE, CANVAS_SCROLL_RATE) # pixels per scroll-unit - fixed
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        #self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
        #self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_SCROLLWIN, self.OnScrollWin)

        self._diagram = Diagram(self)
        self._actions = Actions(self)
        self._interactions = Interactions(self)
        self._droptarget = CanvasDropTarget(self)
        self.SetDropTarget(self._droptarget)

        self._mode = "editing" # | "browsing"

        self.SetFocus() # It seems this explicitly needed for ScrolledWindow in Linux to see key presses

    #def OnErase(self, evt):
    #    dc = evt.GetDC()
    #    if dc == None: dc = self.ClientDC()
    #    if dc != None: dc.Clear()

    def canvasId(self): return self._canvasId
    def diagram(self): return self._diagram
    def actions(self): return self._actions
    def interactions(self): return self._interactions
    def droptarget(self): return self._droptarget

    def mode(self):
        return self._mode

    def SetMode(self, mode):
        self._mode = mode

    def refreshExtent(self, extent):
        extent.x = round(extent.x * self._scale)
        extent.y = round(extent.y * self._scale)
        extent.width = round(extent.width * self._scale)
        extent.height = round(extent.height * self._scale)
        pos = self.CalcScrolledPosition(extent.x, extent.y) #logical to device units
        extent.x = pos[0]
        extent.y = pos[1]
        self.RefreshRect(extent, True)

    def screenRectToDiagramRect(self, rect):
        rect.x, rect.y = self.CalcUnscrolledPosition(rect.x, rect.y)
        rect.x = round(rect.x / self._scale)
        rect.y = round(rect.y / self._scale)
        rect.width = round(rect.width / self._scale)
        rect.height = round(rect.height / self._scale)
        return rect

    def OnPaint(self, evt):
        dc = wx.AutoBufferedPaintDC(self) #wx.PaintDC(self)
        self.PrepareDC(dc)
        dc.SetUserScale(self._scale, self._scale)

        dc.SetBackground(wx.Brush(self.GetBackgroundColour(), wx.BRUSHSTYLE_SOLID))

        #dc.DestroyClippingRegion()
        #dc.SetClippingRegionAsRegion(self.GetUpdateRegion())

        #if True:
        dc.Clear()
        self._diagram.Redraw(dc)                                            # draw all
        #else:
        #    self._diagram.RedrawRect(dc, self.GetUpdateRegion().GetBox())      # draw in outer box

        #wxRegionIterator upd(GetUpdateRegion()) // get the update rect list
        ##upd = wx.RegionIterator(self.GetUpdateRegion())                   # draw in each rectangle - not sure this works at all - has update probs
        ##count = 0
        ##while upd:
        ##    #wxRect rect(upd.GetRect());
        ##    rect = upd.GetRect()
        ##    self.screenRectToDiagramRect(rect)
        ##    self._diagram.RedrawRect(dc, rect)
        ##    #upd++;
        ##    upd = upd.Next()
        ##    count += 1
        ##print "OnPaint count="+str(count)         # seems to always be 1 (i.e. misses bits or no better than outer box)

    def OnMouseEvent(self, mouse_event):
        self.SetFocus()
        dc = wx.ClientDC(self)
        self.PrepareDC(dc)
        dc.SetUserScale(self._scale, self._scale)
        self._interactions.setMousePointer(mouse_event.GetLogicalPosition(dc))
        evttype = mouse_event.GetEventType()
        if evttype in wx.EVT_LEFT_DOWN.evtType:
            self._interactions.onMouseLeftDown(mouse_event, dc)
        elif evttype in wx.EVT_LEFT_UP.evtType:
            self._interactions.onMouseLeftUp(mouse_event, dc)
        elif evttype in wx.EVT_LEFT_DCLICK.evtType: # this immediately follows an onMouseDown+onMouseUp (no move) and will be followed by an onMouseUp
            self._interactions.onMouseLeftDClick(mouse_event, dc)
        elif evttype in wx.EVT_RIGHT_DOWN.evtType:
            self._interactions.onMouseRightDown(mouse_event, dc)
        elif evttype in wx.EVT_RIGHT_UP.evtType:
            self._interactions.onMouseRightUp(mouse_event, dc)
        elif evttype in wx.EVT_RIGHT_DCLICK.evtType:
            self._interactions.onMouseRightDClick(mouse_event, dc)
        elif evttype in wx.EVT_MIDDLE_DOWN.evtType:
            self._interactions.onMouseMiddleDown(mouse_event, dc)
        elif evttype in wx.EVT_MIDDLE_UP.evtType:
            self._interactions.onMouseMiddleUp(mouse_event, dc)
        elif evttype in wx.EVT_MIDDLE_DCLICK.evtType:
            self._interactions.onMouseMiddleDClick(mouse_event, dc)
        elif evttype in wx.EVT_MOTION.evtType:
            self._interactions.onMouseMove(mouse_event, dc)
        elif evttype in wx.EVT_ENTER_WINDOW.evtType:
            self._interactions.onEntering(mouse_event, dc)
        elif evttype in wx.EVT_LEAVE_WINDOW.evtType:
            self._interactions.onLeaving(mouse_event, dc)
        elif evttype in wx.EVT_MOUSEWHEEL.evtType:
            self._interactions.onMouseWheel(mouse_event, dc)
        #self._diagram.Redraw(dc)

    #def OnChar(self, evt):
    #    dc = wx.ClientDC(self)
    #    self.PrepareDC(dc)
    #    dc.SetUserScale(self._scale, self._scale)
    #    self._interactions.onChar(evt, dc)

    def OnKeyDown(self, evt):
        #print "grob.Canvas.OnChar"
        dc = wx.ClientDC(self)
        self.PrepareDC(dc)
        dc.SetUserScale(self._scale, self._scale)
        self._interactions.onKeyDown(evt, dc)

    def OnScrollWin(self, evt):
        # this prob happens before change (not after)
        centre = self.getCentrePoint()
        #seems correct for keys(arrows/PgUp) but not when slide sliders (centre coords dont show as changing)
        evt.Skip()

    def raiseCanvasEvent(self, evtTypeStr, application_data, dataStr):
        evt = CanvasEvent(CanvasEventType[evtTypeStr])
        event_data = '<canvas_event type="'+str(evtTypeStr)+'" id="'+str(self._canvasId)+'"'
        event_data += '>'
        event_data += dataStr
        if application_data:
            event_data += application_data
        event_data += '</canvas_event>'
        evt.data = event_data
        self.GetEventHandler().AddPendingEvent(evt)

    def raiseCanvasSelectedObjectsEvent(self, objectsStr):
        event_data = objectsStr
        self.raiseCanvasEvent("selected_objects", '', event_data)

    def raiseCanvasChangedObjectsEvent(self,
                                       application_data,
                                       infoStr,
                                       priorSelectedObjectsStr,
                                       deletedObjectsStr,
                                       preUpdatedObjectsStr,
                                       updatedObjectsStr,
                                       insertedObjectsStr,
                                       selectedObjectsStr):
        event_data = ''
        if infoStr:
            event_data += infoStr # assumed already entitised if necessary
        if priorSelectedObjectsStr: event_data += '<prior-selected>'+priorSelectedObjectsStr+'</prior-selected>'
        if deletedObjectsStr: event_data += '<deleted>'+deletedObjectsStr+'</deleted>'
        if preUpdatedObjectsStr: event_data += '<pre-updated>'+preUpdatedObjectsStr+'</pre-updated>'
        if updatedObjectsStr: event_data += '<updated>'+updatedObjectsStr+'</updated>'
        if insertedObjectsStr: event_data += '<inserted>'+insertedObjectsStr+'</inserted>'
        if selectedObjectsStr: event_data += '<selected>'+selectedObjectsStr+'</selected>'
        self.raiseCanvasEvent("changed_objects", application_data, event_data)

    def raiseCanvasChangedObjects(self,
                                  application_data,
                                  infoStr,
                                  priorSelectedObjectsStr,
                                  deletedObjectsStr,
                                  preUpdatedObjectsStr,
                                  updatedObjectsStr,
                                  insertedObjectsStr):
        selectedObjectsStr = self._diagram.saveObjectList(
                self._interactions.selection().selection(),
                indent=None, level=0, saveDefaults=True)
        self.raiseCanvasChangedObjectsEvent(
            application_data,
            infoStr,
            priorSelectedObjectsStr,
            deletedObjectsStr,
            preUpdatedObjectsStr,
            updatedObjectsStr,
            insertedObjectsStr,
            selectedObjectsStr)

    def raiseCanvasApplicationRequestEvent(self, application_data, commandStr, infoParametersStr, objectsStr):
        event_data = '<info command="'+str(commandStr)+'"'
        if infoParametersStr:
            event_data += ' ' + infoParametersStr # assumed already entitised if necessary
        event_data += '/>'
        event_data += objectsStr
        self.raiseCanvasEvent("application_request", application_data, event_data)

    def raiseCanvasApplicationNotifyEvent(self, application_data, notifyStr, msg):
        event_data = '<info notify="'+str(notifyStr)+'">'
        event_data += xut.entitise(msg)
        event_data += '</info>'
        self.raiseCanvasEvent("application_notify", application_data, event_data)

    def DoDrawing(self, dc, rect=None):                  # used for printing
        if rect is None:
            self._diagram.Redraw(dc)
        else:
            self._diagram.RedrawRect(dc, rect)

    def GetDiagramSize(self):                           # used for printing - returns value
        return (self._diagram.properties().Width,
                self._diagram.properties().Height)

    def SetScale(self, scale, ptr=None):                # used in commands (to scale)
        pos = self.getCentrePoint()
        priorScale = self._scale
        self._scale = scale
        self.SetVirtualSize(wx.Size(round(self._scale * self._diagram.properties().Width),
                                    round(self._scale * self._diagram.properties().Height)))
        #self.SetScrollRate(20, 20) - scroll units
        if ptr is not None:
            # Want to keep orig ptr coords in same relative view position after scale and pan.
            displacement_x = priorScale*(ptr.x - pos.x)
            displacement_y = priorScale*(ptr.y - pos.y)
            pos.x = ptr.x - round(displacement_x/self._scale)
            pos.y = ptr.y - round(displacement_y/self._scale)
        self.scrollToCentrePoint(pos)
        self.Refresh()

    def GetScale(self): return self._scale

    def ClearCanvasDefinitions(self):
        self._diagram.clearDiagramDefinitions()
        self._actions.clearActionsDefinitions()
        self._interactions.clearInteractionsDefinitions()

    def SetupCanvas(self, canvasDefinitionsOrFile, optionsForDiagramProperties):   # used when create a canvas (control, mainview, ismodelview)
        if canvasDefinitionsOrFile:
            if isinstance(canvasDefinitionsOrFile, xut.XmlElement):
                canvasDefinitions = canvasDefinitionsOrFile
            else:
                canvasDefinitions, error = xut.xmlElementFromFile(canvasDefinitionsOrFile)
            if canvasDefinitions:
                self._diagram.setDiagramDefinitions(canvasDefinitions)
                self._actions.setActionDefinitions(canvasDefinitions)
                self._interactions.setInteractionDefinitions(canvasDefinitions)
        if optionsForDiagramProperties:
            self.SetOptionsForDiagramProperties(optionsForDiagramProperties)

    def SetOptionsForDiagramProperties(self, optionsForDiagramProperties):
        self._diagram.setOptionsForDiagramProperties(optionsForDiagramProperties)

    def ClearObjects(self):                         # used in commands (New & Open application
        self.diagram().clearObjects()

    #def loadObjectsFromFile(self, filepath):        # ? not used
    #    return self.diagram().loadObjectsFromFile(filepath)

    def LoadObjectsFromXml(self, xmlnode, raiseEvent, selectObjects, pasting=False): # used by application/diagraminfo - returns value
        return self.actions().loadObjectsFromXml(xmlnode, raiseEvent, selectObjects, pasting=pasting)

    #def saveObjectsToFile(self, filepath):          # ? not used
    #    self.diagram().saveObjectsToFile(filepath)

    def SaveObjects(self, indent = None, level = 0, saveDefaults=False, includeVersion=True):  # used by application/diagraminfo - returns value
        return self.diagram().saveObjects(indent, level, saveDefaults, includeVersion)

    def getCentrePoint(self):
        size = self.GetClientSize()
        x = round(size.width / 2)
        y = round(size.height / 2)
        x, y = self.CalcUnscrolledPosition(x, y)
        x = round(x / self._scale)
        y = round(y / self._scale)
        pos = wx.Point(x, y)
        return pos

    def scrollToCentrePoint(self, pos):
        size = self.GetClientSize()
        x = round(pos.x * self._scale)
        y = round(pos.y * self._scale)
        xs = 0
        if x > round(size.width / 2):
            xs = round((x - size.width / 2) / CANVAS_SCROLL_RATE)
        ys = 0
        if y > round(size.height / 2):
            ys = round((y - size.height / 2) / CANVAS_SCROLL_RATE)
        self.Scroll(xs, ys)

    def panDiagram(self, panLeft, panUp):
        x, y = self.CalcUnscrolledPosition(0, 0)
        xs = x - panLeft * self._scale
        ys = y - panUp * self._scale
        self.Scroll(round(xs/CANVAS_SCROLL_RATE), round(ys/CANVAS_SCROLL_RATE))

    def screenCoordsToDiagramPos(self, x, y):
        x, y = self.CalcUnscrolledPosition(x, y)
        x = round(x / self._scale)
        y = round(y / self._scale)
        pos = wx.Point(x, y)
        return pos

    def Action(self, actionStr): # used in command CanvasAction
        #print(">Canvas.Action "+actionStr)
        dc = wx.ClientDC(self)
        self.PrepareDC(dc)
        dc.SetUserScale(self._scale, self._scale)
        pos = self.getCentrePoint()
        resultStr = self._actions.DirectAction(actionStr, dc, pos)

    def GetPortsInfo(self, entityObjectId):         # used by esl/generate  (gather) - returns value
        return self._diagram.getPortsInfo(entityObjectId)

    def EstablishPortsConnections(self, entityObjectId):    # used by esl/generate  (gather) - returns value
        return self._diagram.establishPortsConnections(entityObjectId)

    def EstablishLinksConnections(self, linkObjectId):
        return self._diagram.establishLinksConnections(linkObjectId)

    def SaveObjectById(self, objectId):
        return self._diagram.saveObjectById(objectId)

    #def UpdateObject(self, objectId, descr):        # was used in propertiescontrol
    #    obj = self._diagram.updateObject(objectId, descr)
    #    return obj

    #def UpdateEntityPorts(self, entityObjectId, portsDescr): # was used in commands, propertiescontrol & application/diagraminfo
    #    obj = self._diagram.updateEntityPorts(entityObjectId, portsDescr)
    #    return obj

    def GetSelection(self):                                 # used in control - returns value
        return self.interactions().selection().selection()

    def GetSelectedExtent(self):
        return self._diagram.getSelectedExtent()

    def GetFullExtent(self):
        return self._diagram.getFullExtent()

    def GetVisibleDiagramArea(self):
        x, y = self.CalcUnscrolledPosition(0, 0)
        size = self.GetClientSize()
        area = wx.Rect(round(x/self._scale), round(y/self._scale),
                       round(size.width/self._scale), round(size.height/self._scale))
        return area

    #def SelectObjects(self, objectIdList, raiseSelectionEvent): # was used in control, propertiescontrol & application/application
    #    self.diagram().selectObjects(objectIdList, raiseSelectionEvent)

    def ZoomAll(self):                                      # used in commands (ZoomAll)
        extent = self.diagram().getFullExtent()
        if extent:
            size = self.GetClientSize()
            scale = float(size.width - 20) / float(extent.width)
            self._scale = float(size.height - 20) / float(extent.height)
            if scale < self._scale: self._scale = scale
            self.SetVirtualSize(wx.Size(round(self._scale * self._diagram.properties().Width),
                                        round(self._scale * self._diagram.properties().Height)))
            self.scrollToCentrePoint(wx.Point(extent.x + round(extent.width / 2), extent.y + round(extent.height / 2)))
            self.Refresh()

    def ZoomSelected(self):                                      # used in commands (ZoomSelected)
        extent = self.diagram().getSelectedExtent()
        if extent:
            size = self.GetClientSize()
            scale = float(size.width - 20) / float(extent.width)
            self._scale = float(size.height - 20) / float(extent.height)
            if scale < self._scale: self._scale = scale
            self.SetVirtualSize(wx.Size(round(self._scale * self._diagram.properties().Width),
                                        round(self._scale * self._diagram.properties().Height)))
            self.scrollToCentrePoint(wx.Point(extent.x + round(extent.width / 2), extent.y + round(extent.height / 2)))
            self.Refresh()
