#! /usr/bin/python

import wx

from . import colournames as Colours
from .transform import Scale, Orientation, Transform, doReorientation, expandRect

CompositeObjectSeparator = '+'

AlertObjectTime = 200
HitMargin = 1

class Object(object):
    """ Base of all graphical objects

    """
    def __init__(self, diagram, position=None, orientation=None):
        self._objectId = ''
        self._diagram = diagram
        self._category = "" # from definition
        self._type = "" # from definition
        self._defn = None # defn
        self._position = wx.Point(0, 0) # in description "x" & "y"
        if position: self._position = wx.Point(position) # on diagram - get rewritten when a component of a composite
        self._scale = Scale()
        self._orientation = Orientation.normal # in description "orientation"
        if orientation: self._orientation = orientation
        self._size = None

        self._parent = None # used when a component of a composite

        self._draggable = True # can drag it (description "drag")
        self._grabbable = False # it can be grabbed
        self._visible = True # it shows (description "visible")
        self._selectable = True # it can be selected (description "select")
        self._orientable = True # it can be re-orientated (description "orient")
        self._scalable = True # it can be re-orientated (description "scalable")
        self._copyable = True # it can be copied (description "copy")
        self._contextmenu = None # it has a context-menu 'menu' declared (description "context-menu")
        self._activate = None # it has a d-click 'action' declared (description "activate")

        self._moving = False # state - is moving (or not)
        self._selected = False # state - is selected (or not)

        self._startDragPosn = None # position of object when start drag
        self._dragDisplacement = None # cumulative drag displacemnt
        self._lastExtent = None # last extent object had while dragging in progress

        self._grabs = []

    def __str__(self):
        return "<Object>"

    def objectId(self):
        objectId = self._objectId
        if not objectId:
            objectId = ''
            obj = self
            upobj = obj._parent
            while upobj:
                ix = upobj.componentIndex(obj)
                if ix >= 0:
                    objId = str(ix)
                else:
                    objId = obj.objectId()
                if objectId:
                    objectId = objId + CompositeObjectSeparator + objectId
                else:
                    objectId = objId
                obj = upobj
                upobj = upobj._parent
                if upobj is None:
                    objId = obj._objectId
                    if objId:
                        if objectId:
                            objectId = objId + CompositeObjectSeparator + objectId
                        else:
                            objectId = objId
        return objectId

    def diagram(self): return self._diagram
    def category(self): return self._category
    def type(self): return self._type
    def set_type(self, type): self._type = type
    def defn(self): return self._defn

    def setObjectId(self, objId): # used in diagram by 'make' functions for top-level objects (also when map inserts and keepId)
        self._objectId = objId

    def setParent(self, parent):
        self._parent = parent

    def position(self): # Position of the object (diagram coords) - normally the centre (but may be off) about which it rotates etc.
        return self._position
    def setPosition(self, posn):
        self._position = wx.Point(posn)
    def objectTransform(self):
        return Transform(self._position, self._scale, self._orientation)
    def setObjectTransform(self, transform):
        self._position = wx.Point(transform.position)
        if self._category != "element":
            self._orientation = transform.orientation
            self._scale = transform.scale.copy()
        else:
            self.setScale(transform.scale)
            self.setOrientation(transform.orientation)

    def getTransform(self, belowTranform=None):
        transform = belowTranform
        if self._parent:
            par = self._parent
            parTransform = par.objectTransform()
            if belowTranform:
                transform = parTransform.applyTransform(belowTranform, self)
            else:
                transform = parTransform
            if par.parent():
                transform = par.getTransform(transform)
        return transform

    def getDiagramPosition(self, transform=None): # gets the object's position on the diagram
        if not transform:
            transform = self.getTransform()
        posn = wx.Point(self._position) #have to clone
        if transform:
            posn = wx.Point(transform.backTransformPoint(self._position, self))
        return posn

    def getDiagramPositioning(self, transform=None): # gets the object's position, orientation and size on the diagram
        posn = wx.Point(self._position) #have to clone
        orientation = self._orientation
        size = self._size
        if not transform:
            transform = self.getTransform()
        if transform:
            posn = wx.Point(transform.backTransformPoint(self._position, self))
            orientation = transform.orientation
            size = None
            if self._size:
                sizePt = transform.backTransformPoint(wx.Point(self._size.x, self._size.y), self)
                origPt = transform.backTransformPoint(wx.Point(0, 0), self)
                size = wx.Size(abs(round(sizePt.x - origPt.x)), abs(round(sizePt.y - origPt.y)))
        return posn, orientation, size

    def getDiagramPoint(self, pt, transform=None):
        newpt = wx.Point(pt)
        if not transform:
            transform = self.getTransform()
        if transform:
            newpt = wx.Point(transform.backTransformPoint(pt, self))
        return newpt

    def getScale(self): return self._scale
    def setScale(self, scale):
        result = False
        if self.isScalable():
            if not scale:
                scale = Scale()
            else:
                self._scale = scale.copy()
            result = True
        return result

    def orientation(self): return self._orientation

    def parent(self): return self._parent

    def draggable(self): return self._draggable
    def setDraggable(self, draggable): self._draggable = draggable
    def grabbable(self): return self._grabbable
    def setGrabbable(self, grabbable): self._grabbable = grabbable
    def visible(self): return self._visible
    def setVisible(self, visible): self._visible = visible
    def selectable(self): return self._selectable
    def setSelectable(self, selectable): self._selectable = selectable
    def orientable(self): return self._orientable
    def isOrientable(self):
        orientable = self._orientable
        if orientable:
            if self._parent:
                orientable = self._parent.isOrientable()
        return orientable
    def setOrientable(self, orientable): self._orientable = orientable
    def scalable(self): return self._scalable
    def setScalable(self, scalable): self._scalable = scalable
    def isScalable(self):
        scalable = self._scalable
        if scalable:
            if self._parent:
                scalable = self._parent.isScalable()
        return scalable
    def copyable(self): return self._copyable
    def setCopyable(self, copyable): self._copyable = copyable
    def contextmenu(self): return self._contextmenu
    def activate(self): return self._activate

    def moving(self): return self._moving
    def selected(self): return self._selected

    def extent(self, includeInvisible=False): # Extent (equal either side of centre) (diagram coords)
        result = None
        if includeInvisible or self._visible:
            posn, orientation, size = self.getDiagramPositioning()
            if size:
                hw = round(size.width / 2)
                hh = round(size.height / 2)
            else:
                hw = 1
                hh = 1
            result = wx.Rect(posn.x - hw, posn.y - hh, 2 * hw, 2 * hh)
        return result

    def setOrientation(self, orientation):
        result = False
        if self._orientable:
            self._orientation = orientation
            result = True
        return result

    def getOrientation(self):
        orientation = self._orientation
        return orientation

    def applyOrientation(self, dc, orientation):
        if self.isOrientable():
            currentOrientation = self._orientation
            newOrientation = doReorientation(currentOrientation, orientation)
            self.setOrientation(newOrientation)
        self.handleGrabs()

    def setSelected(self, selected):
        result = False
        if self._selectable:
            self._selected = selected
            self.handleGrabs()
            self.refreshOverlayExtent(None)
            result = True
        return result

    def handleGrabs(self):
        if self._grabbable:
            if self._selected:
                self.setGrabs()
            else:
                self.clearGrabs()

    def setGrabs(self): # override
        pass

    def clearGrabs(self):
        self._grabs = []

    def checkHitGrab(self, ptr):
        result = None
        for grab in self._grabs:
            if grab.HitTest(ptr) is not None:
                result = grab
                break
        return result

    def alertObject(self, alertTime=None):
        if alertTime is None:
            alertTime = self._diagram.themeProperties().AlertObjectTime
        if alertTime:
            self.setAlerted(True)
            wx.CallLater(alertTime, self.endAlertObject)

    def setAlerted(self, alerted): # use selection for alert (just visually) - unless override
        self.setSelected(alerted)

    def endAlertObject(self):
        self.setAlerted(False)

    def startDragging(self):
        drag = self._draggable
        if drag:
            self._moving = True
            self._visible = self._diagram.properties().DragObjectVisible
            self._startDragPosn = wx.RealPoint(self._position)
            self._dragDisplacement = wx.RealPoint()
            self._lastExtent = self.getGrabOverlayExtent(None)
        return drag

    def stopDragging(self):
        drag = False
        if self._moving:
            drag = True
            self._moving = False
            self._visible = True
            self._startDragPosn = None
            self._dragDisplacement = None
            self.refreshOverlayExtent(None)
        return drag

    def dragBy(self, dc, displacement, refreshCache=None):
        drag = False
        if displacement.x != 0 or displacement.y != 0:
            drag = self._draggable
            if drag:
                relativeDisplacement = displacement
                if self._dragDisplacement:
                    self._dragDisplacement += wx.RealPoint(displacement)
                else:
                    self._dragDisplacement = wx.RealPoint(displacement)
                relativeDragDisplacement = self._dragDisplacement
                if self._parent is not None:                # dragging a component
                    transform = self.getTransform()
                    transform.position.x = 0
                    transform.position.y = 0
                    relativeDisplacement = transform.transformPoint(displacement, self)
                    relativeDragDisplacement = transform.transformPoint(self._dragDisplacement, self)
                if self._startDragPosn is None: # has bypassed startDragging
                    self._startDragPosn = wx.RealPoint(self._position)
                newPosition = wx.RealPoint(self._startDragPosn.x + relativeDragDisplacement.x, self._startDragPosn.y + relativeDragDisplacement.y)
                self._position = wx.Point(newPosition)
                for grab in self._grabs:
                    grab._position = wx.Point(wx.RealPoint(grab._position) + wx.RealPoint(displacement))
                self.refreshOverlayExtent(relativeDisplacement, refreshCache)
        return drag

    def Draw(self, dc, transform=None):
        if self._visible:
            self.drawObject(dc, transform)
        if self._selected:
            self.drawOverlay(dc)
            for grab in self._grabs:
                grab.drawObject(dc)

    def getOverlayExtent(self):
        ext = self.extent()
        if ext is not None:
            ext = wx.Rect(ext.x - self._diagram.properties().OverlayMargin,
                          ext.y - self._diagram.properties().OverlayMargin,
                          ext.width + 2 * self._diagram.properties().OverlayMargin,
                          ext.height + 2 * self._diagram.properties().OverlayMargin)
        return ext

    def drawOverlay(self, dc):
        dc.SetPen(wx.Pen(Colours.get(self._diagram.properties().OverlayPenColour),
                         self._diagram.properties().OverlayPenWidth,
                         self._diagram.properties().OverlayPenStyle))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        ext = self.getOverlayExtent()
        dc.DrawRectangle(ext)

    def getGrabOverlayExtent(self, displacement):
        ext = self.getOverlayExtent()
        if displacement is not None:
            expandRect(ext, displacement)
        ext.Inflate(self._diagram.properties().OverlayMargin, self._diagram.properties().OverlayMargin)
        if self._grabs and len(self._grabs) != 0:
            grabSize = self._grabs[0].getSize()
            ext.Inflate(grabSize.width, grabSize.height)
        return ext

    def refreshOverlayExtent(self, displacement, refreshCache=None):
        ext = self.getGrabOverlayExtent(displacement)
        moved = displacement is not None and (displacement.x != 0 or displacement.y != 0)
        fullExtent = wx.Rect(ext)
        if self._lastExtent is not None:
            fullExtent.Union(self._lastExtent)
        if refreshCache is None:
            self._diagram._canvas.refreshExtent(fullExtent)
        else:
            refreshCache.Union(fullExtent)
        if moved:
            self._lastExtent = ext
        else:
            self._lastExtent = None

    def setContextMenu(self):
        return None

    def showContextMenu(self):
        menu = self.setContextMenu()
        if menu is not None:
            self._diagram._canvas.PopupMenu(menu)
            menu.Destroy()

    def HitTest(self, pos):
        hitMe = None
        if self._visible:
            ext = self.extent() # diagram coords
            if ext is not None:
                margin = HitMargin
                if (pos.x >= ext.x - margin and pos.x <= ext.x + ext.width + margin) and \
                   (pos.y >= ext.y - margin and pos.y <= ext.y + ext.height + margin):
                    hitMe = self
        return hitMe

    def gatherDeleteList(self, deleteList):
        deleteList.append(self)

    def gatherCopyList(self, copyList):
        pass

    def getZOrder(self) -> int:
        zOrder = self._diagram.getZOrder(self)
        return zOrder

class Composite(Object):
    def __init__(self, diagram, position=None, orientation=None):
        Object.__init__(self, diagram, position, orientation)
        self._components = []

    def add(self, obj):
        self._components.append(obj)
        obj._parent = self

    def removeClses(self, cls):
        objlist = self._components[:]
        self._components = []
        for obj in objlist:
            if not isinstance(obj, cls):
                self._components.append(obj)

    def remove(self, obj):
        if obj in self._components:
            self._components.remove(obj)

    def removeAll(self):
        self._components = []

    def components(self):
        return self._components

    def componentIndex(self, obj):
        ix = -1
        if obj in self._components:
            ix = self._components.index(obj)
        return ix

    def componentAtIndex(self, ix):
        component = None
        if ix >= 0 and ix < len(self._components):
            component = self._components[ix]
        return component

    def drawObject(self, dc, transform=None):
        if self._visible:
            belowTransform = self.objectTransform()
            if not transform and self._parent is not None:
                aboveTransform = self.getTransform()
                if aboveTransform:
                    belowTransform = aboveTransform.applyTransform(belowTransform, self)
            if transform:
                belowTransform = transform.applyTransform(belowTransform, self)
            for obj in self._components: # last added on top
                obj.Draw(dc, belowTransform)

    def extent(self, includeInvisible=False):
        ext = None
        if self._visible:
            posn = self.getDiagramPoint(self._position)
            ext = wx.Rect(posn.x - 1, posn.y - 1, 2, 2)
            for obj in self._components:
                obj_ext = obj.extent(includeInvisible)
                if obj_ext:
                    ext = ext.Union(obj_ext)
        return ext

    def getSize(self, transform=None):
        ext = wx.Rect(0, 0, 2, 2)
        belowTransform = self.objectTransform()
        if transform:
            belowTransform = belowTransform.applyTransform(transform, self)
        for obj in self._components:  # last added on top
            objSize = obj.getSize(belowTransform)
            if objSize:
                ext = ext.Union(objSize)
        return ext

    def HitTest(self, pos):
        result = None # for a group to be hit a visible component element must be hit
        if self._visible:
            components = self._components[:]
            components.reverse()
            for obj in components: # hit last added first
                gotHit = obj.HitTest(pos)
                if gotHit is not None:
                    result = gotHit
                    break
        return result

    def anyComponentSelected(self):
        result = False
        for obj in self._components:
            result = obj.selected()
            if not result and isinstance(obj, Composite):
                result = obj.anyComponentSelected()
            if result:
                break
        return result

def toplevelise(obj):
    while obj.parent():
        obj = obj.parent()
    return obj
