#! /usr/bin/python

from collections import OrderedDict

import wx

from .. import xmlutil as xut

from . import canvas as grob
from . import colournames as Colours
from .registry import Registry
from .object import Object, Composite, CompositeObjectSeparator
from .connectable import Connectable
from .node import Node
from .port import Port, PortConnectorSeparator
from .link import Link, lineMargin
from .entity import Entity
from .group import Group, AnnotationIndicator
from .grab import Grab
from .element import Element, ElementTypes

class DiagramProperties(object):

    def __init__(self, diagram):
        self._diagram = diagram

    def setDefaultCanvasProperties(self):
        # Highlight selected objects by putting a box round them
        self.Width = 1024
        self.Height = 1024
        self.BackgroundFill = '#E0FFFF' #'LightCyan'
        self.BackgroundStroke = 'Black'
        self.BackgroundStrokeWidth = 1
        self.GridStroke = 'Grey'
        self.GridStrokeWidth = 1
        self.GridHorizontal = 100
        self.GridVertical = 100
        self.GridShow = True
        self.GridSnap = 0
        self.SmartLinkDraw = "smart2segments"
        self.OverlayMargin = 3
        self.OverlayPenWidth = 1 # <=OverlayMargin
        self.OverlayPenColour = "blue"
        self.OverlayPenStyle = wx.PENSTYLE_SOLID #wx.PENSTYLE_DOT #wx.PENSTYLE_LONG_DASH #wx.PENSTYLE_TRANSPARENT
        self.DragObjectVisible = True
        self.DragUpdateCount = 1
        self.BackgroundContextMenu = None
        self.SelectionContextMenu = None
        self.PairSelectionContextMenu = None
        self.GroupableSelectionContextMenu = None
        self.GroupablePairSelectionContextMenu = None
        self.AnonymousGroupContextMenu = None

    def setOptionsForDiagramProperties(self, options):
        nr = len(options)
        if nr > 0: self.GridShow = options[0]
        if nr > 1: self.GridSnap = options[1]
        if nr > 2: self.SmartLinkDraw = options[2]

    def setDiagramProperties(self, xmlElement):
        if xmlElement:
            if xmlElement.name() == "properties": diagramElements = [xmlElement]
            else: diagramElements = xmlElement.getXmlElementListByName("properties", True)
            if diagramElements:
                for diagramElement in diagramElements:
                    width = diagramElement.getAttribute("width")
                    if width: self.Width = int(width)
                    height = diagramElement.getAttribute("height")
                    if height: self.Height = int(height)
                    backgroundElement = diagramElement.getXmlElementByName("background")
                    if backgroundElement:
                        backgroundfill = backgroundElement.getAttribute("fill")
                        if backgroundfill: self.BackgroundFill = str(backgroundfill)
                        backgroundstroke = backgroundElement.getAttribute("stroke")
                        if backgroundstroke: self.BackgroundStroke = str(backgroundstroke)
                        backgroundstrokewidth = backgroundElement.getAttribute("stroke-width")
                        if backgroundstrokewidth: self.BackgroundStrokeWidth = int(backgroundstrokewidth)
                    gridElement = diagramElement.getXmlElementByName("grid")
                    if gridElement:
                        gridstroke = gridElement.getAttribute("stroke")
                        if gridstroke: self.GridStroke = str(gridstroke)
                        gridstrokewidth = gridElement.getAttribute("stroke-width")
                        if gridstrokewidth: self.GridStrokeWidth = int(gridstrokewidth)
                        gridhorizontal = gridElement.getAttribute("horizontal")
                        if gridhorizontal: self.GridHorizontal = int(gridhorizontal)
                        gridvertical = gridElement.getAttribute("vertical")
                        if gridvertical: self.GridVertical = int(gridvertical)
                        gridshow = gridElement.getAttribute("show")
                        if gridshow and gridshow == 'false': self.GridShow = False
                        gridsnap = gridElement.getAttribute("snap")
                        if gridsnap: self.GridSnap = int(gridsnap)
                    smartLinksElement = diagramElement.getXmlElementByName("smart-links")
                    if smartLinksElement:
                        self.SmartLinkDraw = smartLinksElement.getAttribute("smart-draw")
                    dragElement = diagramElement.getXmlElementByName("drag")
                    if dragElement:
                        dragmargin = dragElement.getAttribute("box-margin")
                        if dragmargin: self.OverlayMargin = int(dragmargin)
                        dragstrokewidth = dragElement.getAttribute("box-stroke-width")
                        if dragstrokewidth: self.OverlayPenWidth = int(dragstrokewidth)
                        dragstroke = dragElement.getAttribute("box-stroke")
                        if dragstroke: self.OverlayPenColour = str(dragstroke)
                        dragvisible = dragElement.getAttribute("object-visible")
                        if dragvisible == "true": self.DragObjectVisible = True
                        elif dragvisible == "false": self.DragObjectVisible = False
                        updatecount = dragElement.getAttribute("update-count")
                        if updatecount: self.DragUpdateCount = int(updatecount)
                    backgroundcontextmenuElement = diagramElement.getXmlElementByName("background-context-menu")
                    if backgroundcontextmenuElement:
                        self.BackgroundContextMenu = backgroundcontextmenuElement.getAttribute('menu')
                    selectioncontextmenuElement = diagramElement.getXmlElementByName("selection-context-menu")
                    if selectioncontextmenuElement:
                        self.SelectionContextMenu = selectioncontextmenuElement.getAttribute('menu')
                    pairselectioncontextmenuElement = diagramElement.getXmlElementByName("pair-selection-context-menu")
                    if pairselectioncontextmenuElement:
                        self.PairSelectionContextMenu = pairselectioncontextmenuElement.getAttribute('menu')
                    groupableselectioncontextmenuElement = diagramElement.getXmlElementByName("groupable-selection-context-menu")
                    if groupableselectioncontextmenuElement:
                        self.GroupableSelectionContextMenu = groupableselectioncontextmenuElement.getAttribute('menu')
                    groupablepairselectioncontextmenuElement = diagramElement.getXmlElementByName("groupable-pair-selection-context-menu")
                    if groupablepairselectioncontextmenuElement:
                        self.GroupablePairSelectionContextMenu = groupablepairselectioncontextmenuElement.getAttribute('menu')
                    anonymousGroupContextmenuElement = diagramElement.getXmlElementByName("anonymous-group-context-menu")
                    if anonymousGroupContextmenuElement:
                        self.AnonymousGroupContextMenu = anonymousGroupContextmenuElement.getAttribute('menu')

    def DrawBackground(self, dc):
        pen = wx.Pen(Colours.get(self.BackgroundStroke), int(self.BackgroundStrokeWidth), wx.PENSTYLE_SOLID)
        brush = wx.Brush(Colours.get(self.BackgroundFill), wx.BRUSHSTYLE_SOLID)
        dc.SetPen(pen)
        dc.SetBrush(brush)
        dc.DrawRectangle(0, 0, self.Width, self.Height)
        if self.GridShow:
            pen = wx.Pen(Colours.get(self.GridStroke), int(self.GridStrokeWidth), wx.PENSTYLE_SOLID)
            dc.SetPen(pen)
            x = self.GridHorizontal
            while x < self.Width:
                dc.DrawLine(x, 0, x, self.Height)
                x += self.GridHorizontal
            y = self.GridVertical
            while y < self.Height:
                dc.DrawLine(0, y, self.Width, y)
                y += self.GridVertical

class ThemeProperties(object):

    def __init__(self, diagram):
        self._diagram = diagram

    def setDefaultThemeProperties(self):
        self.PortSpacing = 20
        self.PortTagSnap = 5
        self.PortLabelTextDescr = xut.xmlElement('<text font-size="8"/>')
        self.PortLabelHMargin = 6
        self.PortLabelVMargin = 3
        self.AnnotationSpacing = 20
        self.AnnotationTextDescr = xut.xmlElement('<text font-size="10"/>')
        self.BackgroundAnnotationTextDescr = xut.xmlElement('<text font-size="12" justify="left"/>')
        self.AlertObjectTime = 200
        self.AlertConnectionTime = 0

    def setThemeProperties(self, xmlElement):
        if xmlElement:
            if xmlElement.name() == "theme": themeElements = [xmlElement]
            else: themeElements = xmlElement.getXmlElementListByName("theme", True)
            if themeElements:
                for themeElement in themeElements:
                    portPositioningElement = themeElement.getXmlElementByName("port-positioning")
                    if portPositioningElement:
                        spacing = portPositioningElement.getAttribute("spacing")
                        if spacing: self.PortSpacing = int(spacing)
                        tag_snap = portPositioningElement.getAttribute("tag-snap")
                        if tag_snap: self.PortTagSnap = int(tag_snap)
                    portLabelTextElement = themeElement.getXmlElementByName("port-label-text")
                    if portLabelTextElement:
                        self.PortLabelTextDescr = portLabelTextElement
                        value = portLabelTextElement.getAttribute("hmargin")
                        if value: self.PortLabelHMargin = int(value)
                        value = portLabelTextElement.getAttribute("vmargin")
                        if value: self.PortLabelVMargin = int(value)
                    annotationElement = themeElement.getXmlElementByName("annotation")
                    if annotationElement:
                        spacing = annotationElement.getAttribute("spacing")
                        if spacing: self.AnnotationSpacing = int(spacing)
                    annotationTextElement = themeElement.getXmlElementByName("annotation-text")
                    if annotationTextElement:
                        self.AnnotationTextDescr = annotationTextElement
                    backgroundAnnotationTextElement = themeElement.getXmlElementByName("background-annotation-text")
                    if backgroundAnnotationTextElement:
                        self.BackgroundAnnotationTextDescr = backgroundAnnotationTextElement
                    alertObjectElement = themeElement.getXmlElementByName("alert-object")
                    if alertObjectElement:
                        value = alertObjectElement.getAttribute("alert-time")
                        if value: self.AlertObjectTime = int(value)
                        value = alertObjectElement.getAttribute("alert-connection")
                        if value:
                            if value == "true": self.AlertConnectionTime = self.AlertObjectTime
                            elif value == "false": self.AlertConnectionTime = 0
                            else: self.AlertConnectionTime = int(value)
        pass

class Diagram(object):
    """ Handles the objects (and links) on the diagram.
    """
    def __init__(self, canvas):
        self._canvas = canvas
        self._registry = Registry(self)
        self._properties = DiagramProperties(self)
        self._themeProperties = ThemeProperties(self)
        self.clearObjects()
        self._properties.setDefaultCanvasProperties()
        self._themeProperties.setDefaultThemeProperties()

    def clearObjects(self):
        self._allocatedObjectNr = 0 # when add any object, node or link to diagram incr this and set as its objid
        self._objects = OrderedDict()
        self._nodes = OrderedDict()
        self._links = OrderedDict()

    def clearDiagramDefinitions(self):
        self._properties.setDefaultCanvasProperties()
        self._themeProperties.setDefaultThemeProperties()
        self._registry.clearRegistry()

    def setDiagramDefinitions(self, canvasDefinitions):
        self._properties.setDiagramProperties(canvasDefinitions)
        self._themeProperties.setThemeProperties(canvasDefinitions)
        self._registry.setObjectDefinitions(canvasDefinitions)

    def canvas(self): return self._canvas
    def properties(self): return self._properties
    def themeProperties(self): return self._themeProperties
    def registry(self): return self._registry

    def setOptionsForDiagramProperties(self, options):
        self._properties.setOptionsForDiagramProperties(options)

    def Redraw(self, dc):
        """ Draws the objects (and links) in the diagram on the specified device context.
        """
        #self._canvas.SetCursor(wx.HOURGLASS_CURSOR)
        self._properties.DrawBackground(dc)
        for link in list(self._links.values()):
            link.Draw(dc)
        for node in list(self._nodes.values()):
            node.Draw(dc)
        for obj in list(self._objects.values()):
            obj.Draw(dc)
        self._canvas.interactions().Draw(dc)
        #self._canvas.SetCursor(wx.STANDARD_CURSOR)

    def RedrawRect(self, dc, rect):
        """ Draws the objects (and links) in the diagram on the specified device context.
        """
        #self._canvas.SetCursor(wx.HOURGLASS_CURSOR)
        self._properties.DrawBackground(dc)
        for link in list(self._links.values()):
            if link.extent().Intersects(rect):
                link.Draw(dc)
        for node in list(self._nodes.values()):
            if node.extent().Intersects(rect):
                node.Draw(dc)
        for obj in list(self._objects.values()):
            if obj.extent(True).Intersects(rect):
                obj.Draw(dc)
        self._canvas.interactions().Draw(dc)
        #self._canvas.SetCursor(wx.STANDARD_CURSOR)

    def _updateObjectId(self, obj, descr, keepObjectId):
        objectId = ''
        if descr and keepObjectId:
            objectId = descr.getAttribute('id')
            nrObjectId = int(objectId)
            if nrObjectId and nrObjectId > self._allocatedObjectNr:
                self._allocatedObjectNr = nrObjectId
        if not objectId:
            self._allocatedObjectNr += 1
            objectId = str(self._allocatedObjectNr)
        if objectId:
            obj.setObjectId(objectId)
        return objectId

    def makeElement(self, elementType, pos, orientation=None, descr=None, keepObjectId=False):
        element = None
        errorMsg = ""
        if self.registry().get("element", elementType):
            element = Element(elementType, self, pos, orientation, descr)
            if element is not None:
                objectId = self._updateObjectId(element, descr, keepObjectId)
                self._objects[objectId] = element
        else:
            errorMsg = "Element \""+elementType+"\" not defined"
        return element, errorMsg

    def makeGroup(self, category, groupType, pos, orientation=None, descr=None, keepObjectId=False):
        group = None
        errorMsg = ""
        if not groupType or self.registry().get("group", groupType):
            group = Group(category, groupType, self, pos, orientation, descr)
            if group is not None:
                objectId = self._updateObjectId(group, descr, keepObjectId)
                self._objects[objectId] = group
        else:
            errorMsg = "Group \""+groupType+"\" not defined"
        return group, errorMsg

    def makeEntity(self, category, entityType, pos, orientation=None, descr=None, keepObjectId=False):
        errorMsg = ""
        entity = Entity(category, entityType, self, pos, orientation, descr)
        if entity is not None:
            objectId = self._updateObjectId(entity, descr, keepObjectId)
            self._objects[objectId] = entity
        else:
            categoryName = category.title()
            errorMsg = categoryName+" \""+entityType+"\" not defined"
        return entity, errorMsg

    def makePort(self, portType, portElement=None, portIndex=0):
        errorMsg = ""
        port = Port(portType, self, position=None, orientation=None, descr=portElement, index=portIndex)
        if port._defn is None:
            if portElement:
                alternatePortTypes = portElement.getAttribute("equivalent-types")
                if alternatePortTypes:
                    alternatePortTypes = list(map(lambda item: item.strip(), alternatePortTypes.split("|")))
                    for alternatePortType in alternatePortTypes:
                        port = Port(alternatePortType, self, position=None, orientation=None, descr=portElement, index=portIndex)
                        if port:
                            break
        if port._defn is None:
            errorMsg = "Port "+str(portIndex)+" \""+portType+"\" not defined"
            port = None
        return port, errorMsg

    def makeNode(self, nodeType, pos, link=None, descr=None, keepObjectId=False):
        errorMsg = ""
        node = Node(nodeType, self, pos, link, descr)
        if node._defn is None:
            errorMsg = "Node \"" + nodeType + "\" not defined"
            node = None
        if node is not None:
            objectId = self._updateObjectId(node, descr, keepObjectId)
            self._nodes[objectId] = node
        return node, errorMsg

    def makeGrab(self, grabType, pos, grabbable, descr=None, keepObjectId=False):
        grab = None
        errorMsg = ""
        if self.registry().get("grab", grabType):
            grab = Grab(grabType, self, pos, grabbable, descr)
            if grab is not None:
                objectId = self._updateObjectId(grab, descr, keepObjectId)
        else:
            errorMsg = "Grab \""+grabType+"\" not defined"
        return grab, errorMsg

    def makeLink(self, linkType, startConnectable, descr=None, keepObjectId=False):
        errorMsg = ""
        link = Link(linkType, startConnectable, descr)
        if link._defn is None:
            errorMsg = "Link \""+linkType+"\" not defined"
            link = None
        if link is not None:
            objectId = self._updateObjectId(link, descr, keepObjectId)
            self._links[objectId] = link
        return link, errorMsg

    def getObject(self, pos, toplevel = True):
        """ Gets an object (not link or node) at a position in the diagram
        """
        obj = None
        x = pos[0]
        y = pos[1]
        objects = list(self._objects.values())
        objects.reverse()
        for o in objects:
            obj = o.HitTest(pos)
            if obj is not None:
                if toplevel and obj._parent is not None:
                    while obj._parent is not None:
                        obj = obj._parent
                break
            pass
        return obj

    def getLayeredObjects(self, pos):
        """ Gets list of toplevel objects (not link or node) at a position in the diagram
        """
        objectList = []
        x = pos[0]
        y = pos[1]
        objects = list(self._objects.values())
        objects.reverse()
        for o in objects:
            obj = o.HitTest(pos)
            if obj is not None:
                while obj._parent is not None:
                    obj = obj._parent
                objectList.append(obj)
        return objectList

    def getPort(self, pos):
        obj = self.getObject(pos, toplevel = False)
        while obj is not None and not isinstance(obj, Port):
            obj = obj._parent
        return obj

    def getObjectsAndNodesInRect(self, rect):
        objs = []
        objects = list(self._objects.values())
        objects.reverse()
        for o in objects:
            ext = o.extent()
            if rect.Contains(ext):
                objs.append(o)
        nodes = list(self._nodes.values())
        nodes.reverse()
        for n in nodes:
            ext = n.extent()
            if rect.Contains(ext):
                objs.append(n)
        return objs

    def getConnectable(self, pos):
        obj = self.getNode(pos)
        if not obj:
            obj = self.getObject(pos, toplevel = False)
            while obj is not None and not isinstance(obj, Connectable):
                obj = obj._parent
        return obj

    def getLink(self, pos, excludeLinks=None):
        """ Gets a link (not object or node) at a position in the diagram
            other than excludeLink (if given)
        """
        obj = None
        links = list(self._links.values())
        links.reverse()
        for l in links:
            if not excludeLinks or l not in excludeLinks:
                obj = l.HitTest(pos)
                if obj is not None:
                    while obj._parent is not None:
                        obj = obj._parent
                    break
        return obj

    def getNode(self, pos):
        """ Gets a node (not object or link) at a position in the diagram
        """
        obj = None
        nodes = list(self._nodes.values())
        nodes.reverse()
        for n in nodes:
            obj = n.HitTest(pos)
            if obj is not None:
                while obj._parent is not None:
                    obj = obj._parent
                break
        return obj

    def removeLink(self, link):
        if isinstance(link, Link):
            extent = link.extent()
            link.detach()
            #if link in self._links:
                #self._links.remove(link)
            objectId = link.objectId()
            if objectId in self._links:
                del self._links[objectId]
            extent.Inflate(lineMargin, lineMargin)
            self._canvas.refreshExtent(extent)

    def removeNode(self, node):
        if isinstance(node, Node):
            extent = node.getOverlayExtent()
            #if node in self._nodes:
            #    self._nodes.remove(node)
            objectId = node.objectId()
            if objectId in self._nodes:
                del self._nodes[objectId]
            #self._canvas.refreshExtent(extent)
            node.refreshOverlayExtent(None)

    def removeEntity(self, entity):
        self.removeObject(entity)

    def removeObject(self, obj):
        if isinstance(obj, Object):
           #if obj in self._objects:
           #    self._objects.remove(obj)
           objectId = obj.objectId()
           if objectId in self._objects:
                del self._objects[objectId]
           obj.refreshOverlayExtent(None)

    #def loadObjectsFromFile(self, filepath):
    #    oldToNewObjectIds = {}
    #    xmlElement = xut.xmlElementFromFile(filepath)
    #    if xmlElement:
    #        oldToNewObjectIds = self.loadObjectsFromXml(xmlElement)
    #    return oldToNewObjectIds

    def loadObjectsFromString(self, strng, pos = None):
        oldToNewObjectIds = {}
        xmlElement = xut.xmlElement(strng)
        if xmlElement:
            oldToNewObjectIds = self.loadObjectsFromXml(xmlElement, pos)
        return oldToNewObjectIds

    def undeleteObjects(self, descr, pos, raiseCreateEvent, application_data=''):
        selectObjects = True
        objects, oldToNewObjectIds = self.insertObjects(descr, pos, selectObjects=selectObjects, keepObjectIds=True)

    def insertObjects(self, descr, pos, selectObjects=False, keepObjectIds=False, linksOnlyOrNotLinks=None):
        oldToNewObjectIds = {}
        objects = []
        self._canvas.interactions().clearState()
        if isinstance(descr, xut.XmlElement): descrElement = descr
        else: descrElement = xut.xmlElement(descr)
        if descrElement:
            # allow diagram or objects
            if descrElement.name() == "diagram": objectsElement = descrElement
            else: objectsElement = descrElement.getXmlElementByName("diagram", True)
            self._objectMap = {}
            if not objectsElement:
                if descrElement.name() == "objects": objectsElement = descrElement
                else: objectsElement = descrElement.getXmlElementByName("objects", True)
            if objectsElement:
                objectElements = objectsElement.getChildren()
                if linksOnlyOrNotLinks is None or linksOnlyOrNotLinks == "notLinks":
                    for objectElement in objectElements:
                        obj = self.addObject(objectElement, pos, True, keepObjectIds)
                        if obj: objects.append(obj)
                    #endfor
                if linksOnlyOrNotLinks is None or linksOnlyOrNotLinks == "linksOnly":
                    for objectElement in objectElements: # do links after all others
                        link, errorMsg = self.addLink(objectElement, keepObjectIds)
                        if link: objects.append(link)
                    #endfor
            else: # lets just try for one obj (not link)
                obj = self.addObject(descrElement, pos, False, keepObjectIds)
                if obj: objects.append(obj)
            for oldId in self._objectMap:
                oldToNewObjectIds[oldId] = self._objectMap[oldId].objectId()
            self._objectMap = None
            if objects:
                if selectObjects:
                    selectables = []
                    for obj in objects:
                        if obj.category() != 'link' and obj.selectable():
                            selectables.append(obj)
                    self._canvas.interactions().resetSelection(selectables)
            if selectObjects:
                self._canvas.interactions().raiseCanvasSelectedObjects()
            #self._canvas.Refresh()
        return objects, oldToNewObjectIds

    def addObject(self, xmlElement, pos=None, mapping=False, keepObjectId=False):
        obj = None
        errorMsg = ""
        if pos:
            pos = self.snapPoint(pos)
        category = xmlElement.name()
        if category and category in ElementTypes:
            type = category
            category = 'element'
        else:
            type = xmlElement.getAttribute("type")
            if type is None: type = ''
        if category == 'element':
            obj, errorMsg = self.makeElement(type, pos, None, xmlElement, keepObjectId)
        elif category != "link": # we dont add links here (from old) - but reconstruct from connections, and make them in addLink
            if category == 'group':
                obj, errorMsg = self.makeGroup(category, type, pos, None, xmlElement, keepObjectId)
            elif category in ["entity", "node", "link", "display", "info"]:
                oldId = None
                if mapping:
                    oldId = xmlElement.getAttribute("id")
                type = xmlElement.getAttribute("type")
                if type: #and (not mapping or oldId): - now create entity even if no oldId (can't map it of course)
                    if category == "entity" or category == "display" or category == "info":
                        obj, errorMsg = self.makeEntity(category, type, pos, None, xmlElement, keepObjectId)
                        if category == "display" or category == "info":
                            obj.setOrientable(False)
                            obj.setScalable(False)
                            obj.setCopyable(False)
                    elif category == "node":
                        obj, errorMsg = self.makeNode(type, pos, None, xmlElement, keepObjectId)
                    if obj and mapping and oldId:
                        self._objectMap[oldId] = obj
            if obj is None:
                errorMsg = 'Cannot add undefined object category "' + category
                if type:
                    errorMsg += '" type "' + type + '"'
        if errorMsg:
            self._canvas.raiseCanvasApplicationNotifyEvent('', "display", errorMsg)
        return obj

    def addLink(self, xmlElement, keepObjectId=False):
        link = None
        errorMsg = ""
        itemname = xmlElement.name()
        if itemname == "link":
            type = xmlElement.getAttribute("type")
            startId = xmlElement.getAttribute("start-id")
            endId = xmlElement.getAttribute("end-id")
            if startId and endId:
                startConnectable = self.getConnectableFromId(startId)
                endConnectable = self.getConnectableFromId(endId)
                if startConnectable and endConnectable:
                    #startConnectable.checkPosition()
                    link, errorMsg = self.makeLink(type, startConnectable, xmlElement, keepObjectId)
                    if link:
                        added, errorMsg = startConnectable.addLink(link, False)
                        #endConnectable.checkPosition()
                        if added:
                            link.endOnConnectable(endConnectable)
                            added, errorMsg = endConnectable.addLink(link, True)
                        if errorMsg:
                            link = None
        return link, errorMsg

    def findObject(self, objectId):
        obj = None
        objectId = objectId
        if objectId:
            obj = self._objects.get(objectId)
            if obj is None:
                obj = self._nodes.get(objectId)
            if obj is None:
                obj = self._links.get(objectId)
            if obj is None:
                # look for port
                parts = objectId.split(PortConnectorSeparator)
                if len(parts) == 2:
                    entity = self._objects.get(parts[0])
                    if entity:
                        obj = entity.getPort(parts[1])
            if obj is None:
                # Look for component
                parts = objectId.split(CompositeObjectSeparator)
                if len(parts) >= 2:
                    upobj = self._objects.get(parts[0])
                    n = 1
                    while upobj and n < len(parts):
                        objId = parts[n]
                        if objId[0] == AnnotationIndicator: # upobj must be a group (of some kind), the id is for the annotation id
                            obj = upobj.getAnnotation(objId[1:])
                        else: # regular component
                            ix = int(parts[n])
                            obj = upobj.componentAtIndex(ix)
                        n += 1
                        if n < len(parts):
                            upobj = obj
        return obj

    def updateObject(self, objectId, descr, deleteList):
        obj = self.findObject(objectId)
        if obj:
            obj.update(descr, deleteList)
            obj.clearGrabs()  # to force them to be recalc if selected
            obj.handleGrabs()
        return obj

    def updateObjects(self, descr, deleteList, linksOnlyOrNotLinks=None, includeZOrder=False):
        if isinstance(descr, xut.XmlElement): descrElement = descr
        else: descrElement = xut.xmlElement(descr)
        if descrElement:
            # allow diagram or objects
            if descrElement.name() == "diagram": objectsElement = descrElement
            else: objectsElement = descrElement.getXmlElementByName("diagram", True)
            if not objectsElement:
                if descrElement.name() == "objects": objectsElement = descrElement
                else: objectsElement = descrElement.getXmlElementByName("objects", True)
            if objectsElement:
                objectElements = objectsElement.getChildren()
                if linksOnlyOrNotLinks is None or linksOnlyOrNotLinks == "notLinks":
                    zOrderedObjectIds = None
                    doUpdateDiagramZOrder = False
                    for objectElement in objectElements:
                        name = objectElement.name()
                        if name != "link":
                            objectId = objectElement.getAttribute('id')
                            if objectId:
                                obj = self.updateObject(objectId, objectElement, deleteList)
                                if includeZOrder:
                                    toZOrderStr = objectElement.getAttribute('z-order')
                                    if toZOrderStr:
                                        toZOrder = int(toZOrderStr)
                                        if toZOrder > 0:
                                            zOrderedObjectIds, newZOrder = self._canvas.diagram().changeZOrder(objectId, zOrderedObjectIds, "to", toZOrder)
                                            if newZOrder != 0:
                                                doUpdateDiagramZOrder = True
                    #endfor
                    if doUpdateDiagramZOrder:
                        self.updateDiagramObjectsZOrders(zOrderedObjectIds)
                if linksOnlyOrNotLinks is None or linksOnlyOrNotLinks == "linksOnly":
                    for objectElement in objectElements: # do links after all others
                        name = objectElement.name()
                        if name == "link":
                            objectId = objectElement.getAttribute('id')
                            if objectId: self.updateObject(objectId, objectElement, deleteList)
                    #endfor
            else: # lets just try for one obj
                objectId = descrElement.getAttribute('id')
                if objectId: self.updateObject(objectId, descrElement, deleteList)
            self._canvas.Refresh()

    def explodeGroup(self, group):
        objects = []
        for component in group.components():
            transform = component.objectTransform()
            transform = component.getTransform(transform)
            componentXmlStr = component.save(None, 0, True)
            componentXml = xut.xmlElement(componentXmlStr)
            componentXml.setAttribute("id", "")
            componentXml.setAttribute("x", "")
            componentXml.setAttribute("y", "")
            componentXml.setAttribute("select", "") # so can handle exploded fixed group components
            newObject = self.addObject(componentXml, pos=None, mapping=False, keepObjectId=False)
            newObject.setObjectTransform(transform)
            objects.append(newObject)
        if objects:
            selectables = []
            for obj in objects:
                if obj.selectable():
                    selectables.append(obj)
            self._canvas.interactions().resetSelection(selectables)
            self._canvas.interactions().raiseCanvasSelectedObjects()
        return objects

    def groupObjects(self, objects, fixed=True):
        # pos is centre of objects (better for rotation)
        ext = None
        for object in objects:
            if ext is None: ext = object.extent()
            else: ext = ext.Union(object.extent())
        x = 0
        y = 0
        if ext:
            x = round(ext.x + (ext.width / 2))
            y = round(ext.y + (ext.height / 2))
        pos = wx.Point(x, y)
        pos = self.snapPoint(pos)
        # make anonymous group
        group, errorMsg = self.makeGroup("group", "", pos, orientation=None, descr=None, keepObjectId=False)
        if group:
            for object in objects:
                objectXmlStr = object.save(None, 0, True)
                objectXml = xut.xmlElement(objectXmlStr)
                posn = object.position()
                posn = wx.Point(wx.RealPoint(posn) - wx.RealPoint(pos))
                objectXml.setAttribute("id", "")
                objectXml.setAttribute("x", "")
                objectXml.setAttribute("y", "")
                newObject = self.addObject(objectXml, pos=posn, mapping=False, keepObjectId=False)
                objectId = newObject.objectId()
                if objectId in self._objects:
                    del self._objects[objectId]
                # if doing fixed grroup - set various editing properties fixed - actually just one - don't allow component selection
                newObject.setSelectable(not fixed)  # select
                #newObject.setDraggable(not fixed)  # drag
                #newObject.setOrientable(not fixed) # orient
                #newObject.setGrabbable(not fixed)  # grabbable
                newObject.setObjectId("")
                group.add(newObject)
            selectables = []
            if group.selectable():
                selectables.append(group)
            self._canvas.interactions().resetSelection(selectables)
            self._canvas.interactions().raiseCanvasSelectedObjects()
        if errorMsg:
            self._canvas.raiseCanvasApplicationNotifyEvent('', "display", errorMsg)
        return group

    def getConnectableFromId(self, id):
        connectable = None
        parts = id.split(PortConnectorSeparator)
        if len(parts) == 2:
            entity = self._objectMap.get(parts[0]) # newly created
            if not entity:
                entity = self._objects.get(parts[0]) # pre-existing
            if entity:
                connectable = entity.getPort(parts[1])
        else:
            connectable = self._objectMap.get(id)
            if not connectable:
                connectable = self._nodes.get(id)
        return connectable

        # objects
        # - <entity>s
        # - <node>s
        # nodeType???
        # node = self.makeNode(nodeType, ?pos)
        # node.load(xmlElement[strng or wx.XmlNode])
        # - else: <element>
        # <link>s ?startConnectable
        # do connections

    def saveObjects(self, indent = None, level = 0, saveDefaults=False, includeVersion=True, includeZOrder=False):
        result = ''
        objects = ''
        nl = '\n'
        ind = ''
        if indent is not None:
            for i in range(level): ind += indent
        else:
            nl = ''
        for obj in self._objects.values():          # no longer sort by objectId, but save in current z-order order
            objects += obj.save(indent, level + 1, includeZOrder=includeZOrder)
        for node in sortedValues(self._nodes):
            objects += node.save(indent, level + 1)
        for link in sortedValues(self._links):
            objects += link.save(indent, level + 1)
        if objects:
            result += ind
            result += '<diagram'
            if includeVersion: result += ' version="' + grob.GrobVersionString + '"'
            result += '>' + nl
            result += objects
            result += ind
            result += '</diagram>' + nl
        return result

    def saveObjectList(self, objlist, indent = None, level = 0, saveDefaults=False, includeZOrder=False):
        nl = '\n'
        ind = ''
        if indent is not None:
            for i in range(level): ind += indent
        else:
            nl = ''
        result = ind + '<objects version="' + grob.GrobVersionString + '">' + nl
        for obj in objlist:
            result += obj.save(indent, level, saveDefaults, includeZOrder=includeZOrder)
        result += '</objects>' + nl
        return result

    def deleteObjects(self, objList):
        for obj in objList:
            if obj.category() == 'link':
                obj.detach()
        for obj in objList:
            if obj.category() == 'link':
                self.removeLink(obj)
            elif obj.category() == 'node':
                self.removeNode(obj)
            elif obj.category() == 'entity':
                self.removeEntity(obj)
            else:
                self.removeObject(obj)

    #def selectObjects(self, objectIdList, raiseSelectionEvent):
    #    self._canvas.interactions().resetSelection()
    #    for objectId in objectIdList:
    #        obj = self.findObject(objectId)
    #        if obj:
    #            self._canvas.interactions().selectObject(obj)
    #    if raiseSelectionEvent: self._canvas.interactions().raiseCanvasSelectedObjects()

    def getPortsInfo(self, entityObjectId):
        result = []
        obj = self._objects.get(entityObjectId)
        if isinstance(obj, Entity):
            result = obj.getPortsInfo()
        return result

    def establishPortsConnections(self, entityObjectId):
        result = []
        obj = self._objects.get(entityObjectId)
        if isinstance(obj, Entity):
            result = obj.establishPortsConnections(obj)
        return result

    def establishLinksConnections(self, linkObjectId):
        result = []
        link = self._links.get(linkObjectId)
        if link:
            start = link.startObject()
            startConnections = [start.objectId()]
            if start:
                start.establishConnections(None, startConnections, None, inputLink=link)
            end = link.endObject()
            endConnections = [end.objectId()]
            if end:
                end.establishConnections(None, endConnections, None, inputLink=link)
            result = [ startConnections, endConnections ]
        return result

    def saveObjectById(self, objectId, includeZOrder=False):
        result = ''
        obj = self.findObject(objectId)
        if obj:
            result = obj.save(None, 0, True, includeZOrder=includeZOrder)
        return result

    def getFullExtent(self):
        extent = None
        for object in list(self._objects.values()):
            if extent is None: extent = object.extent(True)
            else: extent = extent.Union(object.extent(True))
        if extent is not None:
            for link in list(self._links.values()):
                extent = extent.Union(link.extent())
            for node in list(self._nodes.values()):
                extent = extent.Union(node.extent())
        return extent

    def getSelectedExtent(self):
        extent = self._canvas.interactions().selection().extent()
        return extent

    def selectAllObjectsAndNodes(self, raiseSelectionEvent=True):
        self._canvas.interactions().resetSelection()
        for obj in list(self._objects.values()):
            if obj.selectable():
                self._canvas.interactions().selectObject(obj)
        for obj in list(self._nodes.values()):
            if obj.selectable():
                self._canvas.interactions().selectObject(obj)
        if raiseSelectionEvent: self._canvas.interactions().raiseCanvasSelectedObjects()

    def removeLooseLinks(self, srcObjList):
        objList = []
        for obj in srcObjList:
            if obj.category() == 'link':
                loose = True
                otherObj = obj.startObject()
                if otherObj:
                    if otherObj.category() == 'port':
                        otherObj = otherObj.entity()
                        if otherObj and otherObj in srcObjList:
                            loose = False
                    elif otherObj in srcObjList:
                        loose = False
                if not loose:
                    loose = True
                    otherObj = obj.endObject()
                    if otherObj:
                        if otherObj.category() == 'port':
                            otherObj = otherObj.entity()
                            if otherObj and otherObj in srcObjList:
                                loose = False
                        elif otherObj in srcObjList:
                            loose = False
                if not loose:
                    objList.append(obj)
            else:
                objList.append(obj)
        return objList

    def gridSnap(self):
        return self._properties.GridSnap

    def snapPoint(self, point):
        newPoint = point
        gridSnap = self._properties.GridSnap
        if gridSnap != 0:
            newPoint[0] = gridSnap * round(newPoint[0] / gridSnap)
            newPoint[1] = gridSnap * round(newPoint[1] / gridSnap)
        return newPoint

    def getZOrder(self, object) -> int:
        zOrder = 0
        objectId = object.objectId()
        if object.objectId and object.parent() == None:
            obj = self._objects.get(objectId)
            if obj and obj == object:
                objIx = -1
                try:
                    objIx = list(self._objects.keys()).index(objectId)
                except:
                    pass
                if objIx >= 0:
                    zOrder = objIx + 1
        return zOrder

    def changeZOrder(self, objectId:str, zOrderedObjectIds:list[str], option:str, toZOrder:int) -> (list[str], int):
        """ option: "up"|"down"|"top""bottom"|"to"(use value)  """
        """ returns: valid:bool, rejection:str, val_type:str, val_item:str, updatedESLValue """
        if zOrderedObjectIds is None:
            zOrderedObjectIds = list(self._objects.keys())
        lenZOrderedObjectIds = len(zOrderedObjectIds)
        newZOrderedObjectIds = zOrderedObjectIds
        newZOrder = 0 # no change
        objIx = -1
        try:
            objIx = zOrderedObjectIds.index(objectId)
        except: pass
        if objIx >= 0:
            # check no annotations (for group (+entities, infos etc) or components are in the zOrderedObjectIds
            object = self._objects.get(objectId)
            if object is not None:
                if isinstance(object, Group):
                    for annotation in object._annotations.values():
                        if annotation.objectId():
                            if annotation.objectId() in zOrderedObjectIds:
                                raise Exception("Diagram.changeZOrder objectId="+str(objectId)+" has annotation "+str(annotation.objectId())+
                                                " in diagram._objects")
                if isinstance(object, Composite):
                    for component in object._components:
                        if component.objectId():
                            if component.objectId() in zOrderedObjectIds:
                                raise Exception("Diagram.changeZOrder objectId="+str(objectId)+" has component "+str(component.objectId())+
                                                " in diagram._objects")
            objZOrder = objIx + 1
            if option == "up":
                if objZOrder < lenZOrderedObjectIds:
                    newZOrder = objZOrder + 1
            elif option == "down":
                if objZOrder > 1:
                    newZOrder = objZOrder - 1
            elif option == "top":
                if objZOrder < lenZOrderedObjectIds:
                    newZOrder = lenZOrderedObjectIds
            elif option == "bottom":
                if objZOrder > 1:
                    newZOrder = 1
            elif option == "to" and toZOrder >= 1 and toZOrder <= lenZOrderedObjectIds:
                newZOrder = toZOrder
            else:
                raise Exception("Diagram.changeZOrder objectId=" + str(objectId) + " bad options - option="+option+
                                " toZOrder="+str(toZOrder)+" [objZOrder="+str(objZOrder)+"]")
            if newZOrder != 0 and newZOrder == objZOrder:
                newZOrder = 0
            if newZOrder != 0:
                newZOrderedObjectIds = []
                newObjIx = newZOrder - 1
                ix = 0
                newIx = 0
                while ix < lenZOrderedObjectIds or newIx < lenZOrderedObjectIds:
                    objId = ""
                    if ix < lenZOrderedObjectIds:
                        objId = zOrderedObjectIds[ix]
                    if newIx == newObjIx:
                        newZOrderedObjectIds.append(objectId)
                        newIx += 1
                    if objId and objId != objectId:
                        newZOrderedObjectIds.append(objId)
                        newIx += 1
                    ix += 1
        return newZOrderedObjectIds, newZOrder

    def updateDiagramObjectsZOrders(self, newZOrderedObjectIds):
        newObjects = OrderedDict()
        for objId in newZOrderedObjectIds:
            newObjects[objId] = self._objects.get(objId)
        self._objects = newObjects

def sortIntOrAlpha(item):
    result = item[0]
    if isinstance(result, str) and result.isdigit():
        result = int(result)
    return result

def sortedItems(orderedDict):
    sorted_items = sorted(orderedDict.items(), key=sortIntOrAlpha)
    return sorted_items

def sortedValues(orderedDict):
    sorted_items = sortedItems(orderedDict)
    sorted_values = map(lambda keyValue: keyValue[1], sorted_items)
    return sorted_values
