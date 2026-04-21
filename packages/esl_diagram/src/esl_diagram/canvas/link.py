#! /usr/bin/python

import wx

from .. import xmlutil as xut

from . import arraylinking
from . import colournames as Colours
from .group import Group
from .node import Node
from .port import PortDirection, directionEnum
from .element import Element, penStyle
from .object import Orientation, doReorientation

lineMargin = 2

ANY_TYPE = "*"

class Link(Group):
    # _linkType - string for type of Link
    # _startObj - Connectable at start of Link
    # _endObj - Connectable at end of Link
    def __init__(self, type, startObj, descr = None):
        self._type = type
        self._startObj = startObj
        self._endObj = None
        self._linkLine = None
        ###Composite.__init__(self, startObj._diagram, startObj.position())
        ###self._type = type
        ###self._category = "link"
        ###self._descr = descr
        ###self._defn = self._diagram.registry().get(self._category, self._type)
        Group.__init__(self, "link", type, startObj._diagram, startObj.getDiagramPosition(), None, descr)
        ###self.setShape()
        self._draggable = False
        self._orientable = False
        self._scalable = False

    def __str__(self):
        return "<Link-" + str(self.objectId()) + "(" + self._type + ")@" + str(self.position()) + "->" + str(self._linkLine._extension) + ">"

    def startObject(self):
        return self._startObj

    def endObject(self):
        return self._endObj

    def linkLine(self):
        return self._linkLine

    def setShape(self, newType=""):
        if newType:
            self.set_type(newType)
            self._defn = self._diagram.registry().get(self._category, self._type)
            self.removeAll()
        self._stroke = "black"
        self._strokewidth = 1
        self._strokestyle = "solid"
        self._lineDraw = "straight"
        stroke = self._defn.getAttribute("stroke")
        if stroke: self._stroke = stroke
        strokewidth = self._defn.getAttribute("stroke-width")
        if strokewidth: self._strokewidth = strokewidth
        strokestyle = self._defn.getAttribute("stroke-style")
        if strokestyle: self._strokestyle = strokestyle
        lineDraw = self._defn.getAttribute("draw")
        if self._descr:
            line_dr = self._descr.getAttribute("draw")
            if line_dr: lineDraw = line_dr
        if lineDraw: self._lineDraw = lineDraw
        if not self._linkLine:
            self._linkLine = Element("line", self._diagram)#, None, None, '<element type="line" x="0" y="0"/>')
            self._linkLine.setExtension(0, 0)
        self.add(self._linkLine)
        self._linkLine.setLineDraw(self.smartRectilinearLink(None))
        self._linkLine._pen = wx.Pen(Colours.get(self._stroke), int(self._strokewidth), penStyle(self._strokestyle))
        self._linkLine._draggable = False
        Group.setShape(self)

    def smartRectilinearLink(self, endPt):
        lineDraw = self._lineDraw
        if lineDraw.startswith("smart"):
            smartDraw = lineDraw
            if smartDraw == "smart":
                smartDraw = self._diagram.properties().SmartLinkDraw
            if smartDraw in ["smart2segments", "smart3segments"]:
                if self._startObj:
                    if self._startObj.category() == "node":
                        if len(self._startObj.links()) > 0:
                            firstLink = self._startObj.links()[0]
                            line = firstLink.linkLine()
                            alignment = line.endAlignment()
                            if alignment == "horizontal":
                                lineDraw = "yx"
                            elif alignment == "vertical":
                                lineDraw = "xy"
                            else:
                                lineDraw = "long"
                    elif self._startObj.category() == "port":
                        if not endPt:
                            if self._endObj:
                                endPt = self._endObj.getDiagramPosition()
                        orientation = self._startObj.orientation()
                        entity = self._startObj.entity()
                        startPt = self._startObj.getDiagramPosition()
                        orientation = doReorientation(entity.orientation(), orientation) #check: ?or other way round
                        entityPt = entity.position()
                        if (orientation == Orientation.normal or orientation == Orientation.rotate180
                            or orientation == Orientation.mirrorYAxis or orientation == Orientation.mirrorXAxis):
                            lineDraw = "xy"
                            if endPt:
                                if ((startPt.x > entityPt.x and endPt.x < startPt.x) or
                                    (startPt.x < entityPt.x and endPt.x > startPt.x)):
                                        lineDraw = "yx"
                        else:
                            lineDraw = "yx"
                            if endPt:
                                if ((startPt.y < entityPt.y and endPt.y > startPt.y) or
                                    (startPt.y > entityPt.y and endPt.y < startPt.y)):
                                        lineDraw = "xy"
                if smartDraw == "smart3segments":
                    if lineDraw == "xy":
                        lineDraw = "xyx"
                    elif lineDraw == "yx":
                        lineDraw = "yxy"
            else:
                lineDraw = "straight"
        return lineDraw

    def setLineDraw(self, lineDraw):
        if lineDraw == "default":
            lineDraw = "straight"
            if self._defn is not None:
                lineDraw = self._defn.getAttribute("draw")
        self._lineDraw = lineDraw
        self._linkLine.setLineDraw(self.smartRectilinearLink(None))

    def moveLink(self, newStartPt, newEndPt):
        if newStartPt is not None:
            startPt = self._position
            endPt = self._position + self._linkLine._extension
            self._position = newStartPt
            #self._linkLine._extension = endPt - self._position
            self._linkLine._extension = endPt - newStartPt
        if newEndPt is not None:
            self._linkLine._extension = newEndPt - self._position
        self._linkLine.setLineDraw(self.smartRectilinearLink(None))

    def dragLink(self, dc, startPt, endPt, refreshCache=None):
        #print(">dragLink start="+str(startPt)+" end="+str(endPt)+" last="+str(self._lastExtent)+" lle="+str(self._linkLine._extension))
        if self._lastExtent is None:
            self._lastExtent = self.extent()
        self.moveLink(startPt, endPt)
        # causes flickering - self.Draw(dc)
        extent = self.extent()
        fullExtent = wx.Rect(extent)
        fullExtent.Union(self._lastExtent)
        fullExtent.Inflate(lineMargin, lineMargin)
        if refreshCache is None:
            self._diagram._canvas.refreshExtent(fullExtent)
        else:
            refreshCache.Union(fullExtent)
        self._lastExtent = extent
        #print("<dragLink last="+str(self._lastExtent)+" full="+str(fullExtent)+" lle="+str(self._linkLine._extension))

    def dragLinkEnd(self, dc, endPt, refreshCache=None):
        #print(">dragLinkEnd end="+str(endPt)+" last="+str(self._lastExtent)+" lle="+str(self._linkLine._extension))
        if self._lastExtent is None:
            self._lastExtent = self.extent()
        extension = endPt - self._position
        self._linkLine._extension = extension
        # causes flickering - self.Draw(dc)
        extent = self._linkLine.extent()
        fullExtent = wx.Rect(extent)
        fullExtent.Union(self._lastExtent)
        fullExtent.Inflate(lineMargin, lineMargin)
        if refreshCache is None:
            self._diagram._canvas.refreshExtent(fullExtent)
        else:
            refreshCache.Union(fullExtent)
        self._linkLine.setLineDraw(self.smartRectilinearLink(endPt))
        self._lastExtent = extent
        #print("<dragLinkEnd last="+str(self._lastExtent)+" full="+str(fullExtent)+" lle="+str(self._linkLine._extension))

    def detach(self):
        if self._startObj is not None:
            self._startObj.detachLink(self)
            self._startObj = None
        if self._endObj is not None:
            self._endObj.detachLink(self)
            self._endObj = None

    def endWithNode(self, pos):
        node, errorMsg = self._diagram.makeNode(self._type, pos, self)
        if not node:
            if self._defn:
                alternateLinkTypes = self._defn.getAttribute("equivalent-types")
                if alternateLinkTypes:
                    alternateLinkTypes = list(map(lambda item: item.strip(), alternateLinkTypes.split("|")))
                    for alternateLinkType in alternateLinkTypes:
                        node, errorMsg = self._diagram.makeNode(alternateLinkType, pos, self)
                        if node:
                            break
        if node:
            self._endObj = node
            self.moveLink(None, pos)
            node.refreshOverlayExtent(None)
        return node, errorMsg

    def endOnConnectable(self, connectable):
        if self._endObj and self._endObj != connectable:
            self._endObj.detachLink(self)
        if self._endObj != connectable:
            self._endObj = connectable
            extent = self.extent()
            self.moveLink(None, self._endObj.getDiagramPosition())
            extent = extent.Union(self.extent())
            extent.Inflate(lineMargin, lineMargin)
            self._diagram._canvas.refreshExtent(extent)

    def startOnConnectable(self, connectable):
        if self._startObj and self._startObj != connectable:
            self._startObj.detachLink(self)
        if self._startObj != connectable:
            self._startObj = connectable
            self.moveLink(self._startObj.getDiagramPosition(), None)

    def otherEnd(self, oneEnd):
        theOtherEnd = None
        if (oneEnd == self._startObj):
            theOtherEnd = self._endObj
        elif (oneEnd == self._endObj):
            theOtherEnd = self._startObj
        return theOtherEnd

    def update(self, updateDescr, deleteList):
        if updateDescr is not None:
            if not isinstance(updateDescr, xut.XmlElement):
                updateDescr = xut.xmlElement(updateDescr)
            if updateDescr:
                Group.update(self, updateDescr, deleteList)
                start_id = updateDescr.getAttribute("start-id")
                end_id = updateDescr.getAttribute("end-id")
                if start_id:
                    start = self._diagram.findObject(start_id)
                    if start:
                        self.startOnConnectable(start)
                        added, errorMsg = start.addLink(self, False)
                if end_id:
                    end = self._diagram.findObject(end_id)
                    if end:
                        self.endOnConnectable(end)
                        added, errorMsg = end.addLink(self, True)
                line_draw = updateDescr.getAttribute("draw")
                if line_draw:
                    self.setLineDraw(line_draw)

    def getClosestPtOnLine(self, pt):
        return self._linkLine.getClosestPtOnLine(pt)

    def gatherNodeDeleteList(self, deleteList, doneNodes):
        if self not in deleteList:
            if isinstance(self._startObj, Node):
                self._startObj.gatherNodeDeleteList(self, deleteList, doneNodes)
            if isinstance(self._endObj, Node):
                self._endObj.gatherNodeDeleteList(self, deleteList, doneNodes)
            if self not in deleteList:
               deleteList.append(self)

    def gatherDeleteList(self, deleteList):
        self.gatherNodeDeleteList(deleteList, [])

    def gatherCopyList(self, copyList):
        include = False
        if self._startObj is not None and self._endObj is not None:
            otherObj = self._startObj
            if otherObj.category() == 'port':
                otherObj = otherObj.entity()
                if otherObj and otherObj in copyList:
                    include = True
            elif otherObj in copyList:
                include = True
            if include:
                include = False
                otherObj = self._endObj
                if otherObj.category() == 'port':
                    otherObj = otherObj.entity()
                    if otherObj and otherObj in copyList:
                        include = True
                elif otherObj in copyList:
                    include = True
        if include:
            if self not in copyList: copyList.append(self)

    def directionAndSource(self, trail):
        dirn = PortDirection.unknown
        sourcePort = None
        if self.connectsToDisplay([]) is None:
            if self._startObj and self._startObj not in trail:
                dirn, sourcePort = self._startObj.directionAndSource(trail)
            if self._endObj and self._endObj not in trail:
                endDirn, endSourcePort = self._endObj.directionAndSource(trail)
                if endDirn == PortDirection.output:
                    dirn = endDirn
                    sourcePort = endSourcePort
        return dirn, sourcePort

    def validConnectable(self, connectable):
        valid = False
        errorMsg = ""
        # same-type
        if self._type == connectable._type:
            valid = True
        else:
            if connectable._defn:
                alternateLinkTypes = connectable._defn.getAttribute("equivalent-types")
                if alternateLinkTypes:
                    alternateLinkTypes = list(map(lambda item: item.strip(), alternateLinkTypes.split("|")))
                    if self._type in alternateLinkTypes:
                        valid = True
            if not valid:
                valid, errorMsg = arraylinking.arrayTypesCompatible(self, connectable)
        connectionXml = self._defn.getXmlElementByName("connection")
        if connectionXml:
            conditions = connectionXml.getChildren()
            for conditionXml in conditions:
                errorMsg = ""
                conditionType = conditionXml.name()
                if conditionType == "valid":
                    if not valid:
                        # Test if turns valid.
                        testCond = self.testConnectableCondition(connectable, conditionXml)
                        if testCond:
                            valid = True
                elif conditionType == "reject":
                    # Test if have to reject (whether currently valid or not).
                    testCond = self.testConnectableCondition(connectable, conditionXml)
                    if testCond:
                        valid = False
                        errorMsg = conditionXml.getAttribute("description")
                        break
        return valid, errorMsg

    def testConnectableCondition(self, connectable, conditionXml):
        match = True # all conditions ANDed - any fail fail match immediately
        type = self._type
        base_type = self.baseType()
        dimensions = ""
        if self.dimensionsInfo():
            dimensions = self.dimensionsInfo().dimensions()
        dst_type = connectable.type()
        dst_base_type = connectable.baseType()
        dst_dimensions = ""
        if connectable.dimensionsInfo():
            dst_dimensions = connectable.dimensionsInfo().dimensions()
        trail = []
        dirn, sourcePort = self.directionAndSource(trail)
        sourceEntity = sourcePort.entity() if sourcePort else None
        dst_dirn, dst_sourcePort = connectable.directionAndSource([])
        dst_sourceEntity = dst_sourcePort.entity() if dst_sourcePort else None
        link_entity = None
        if self._startObj and self._startObj.category() == "port":
            link_entity = self._startObj.entity()
        dst_entity = None
        if connectable.category() == "port":
            dst_entity = connectable.entity()
        if match:
            cond = conditionXml.getAttribute("types")
            if cond:
                if cond == "same":
                    match = type == dst_type
                else:
                    match = False
        if match:
            cond = conditionXml.getAttribute("type")
            if cond:
                match = type == cond or cond == ANY_TYPE # identical match (or any)
                if not match:
                    condBaseType, condDimensionsInfo = arraylinking.parseDatatype(cond)
                    compatibility = arraylinking.compatibleTypes(type, base_type, self.dimensionsInfo(), cond, condBaseType, condDimensionsInfo, allowGeneric="second")
                    match = bool(compatibility)
        if base_type and match:
            cond = conditionXml.getAttribute("base-type")
            if cond:
                match = base_type == cond or cond == ANY_TYPE
        if dimensions and match:
            cond = conditionXml.getAttribute("dimensions")
            if cond:
                match = dimensions == cond or cond == ANY_TYPE
        if match:
            cond = conditionXml.getAttribute("dst-type")
            if cond:
                match = dst_type == cond or cond == ANY_TYPE # identical match (or any)
                if not match:
                    condBaseType, condDimensionsInfo = arraylinking.parseDatatype(cond)
                    compatibility = arraylinking.compatibleTypes(dst_type, dst_base_type, connectable.dimensionsInfo(), cond, condBaseType, condDimensionsInfo, allowGeneric="second")
                    match = bool(compatibility)
        if dst_base_type and match:
            cond = conditionXml.getAttribute("dst-base-type")
            if cond:
                match = dst_base_type == cond or cond == ANY_TYPE
        if dst_dimensions and match:
            cond = conditionXml.getAttribute("dst-dimensions")
            if cond:
                match = dst_dimensions == cond or cond == ANY_TYPE
        if match:
            cond = conditionXml.getAttribute("directions")
            if cond:
                if cond == "same":
                    match = dirn == dst_dirn
                else:
                    match = False
        if match:
            cond = conditionXml.getAttribute("direction")
            if cond:
                condDirn = directionEnum(cond)
                match = dirn == condDirn
        if match:
            cond = conditionXml.getAttribute("dst-direction")
            if cond:
                condDirn = directionEnum(cond)
                match = dst_dirn == condDirn
        if match:
            cond = conditionXml.getAttribute("sources")
            if cond:
                if cond == "same" and sourcePort and dst_sourcePort:
                    match = sourcePort == dst_sourcePort
                else:
                    match = False
        if match:
            cond = conditionXml.getAttribute("source")
            if cond:
                if sourcePort:
                    match = sourcePort.category() or sourcePort.type()
                else:
                    match = False
        if match:
            cond = conditionXml.getAttribute("dst-source")
            if cond:
                if dst_sourcePort:
                    match = dst_sourcePort.category() == cond or dst_sourcePort.type() == cond or cond == ANY_TYPE
                else:
                    match = False
        if match:
            cond = conditionXml.getAttribute("source-entities")
            if cond:
                if cond == "same" and sourceEntity and dst_sourceEntity:
                    match = sourceEntity == dst_sourceEntity
                else:
                    match = False
        if match:
            cond = conditionXml.getAttribute("source-entity")
            if cond:
                if sourceEntity:
                    match = sourceEntity.category() == cond or sourceEntity.type() == cond or cond == ANY_TYPE
                else:
                    match = False
        if match:
            cond = conditionXml.getAttribute("dst-source-entity")
            if cond:
                if dst_sourceEntity:
                    match = dst_sourceEntity.category() == cond or dst_sourceEntity.type() == cond or cond == ANY_TYPE
                else:
                    match = False
        if match:
            cond = conditionXml.getAttribute("link-start")
            if cond:
                if self._startObj:
                    match = self._startObj.category() == cond or self._startObj.type() == cond or cond == ANY_TYPE
                else:
                    match = False
        if match:
            cond = conditionXml.getAttribute("link-dst-entity")
            if cond:
                if cond == "same" and link_entity and dst_entity:
                    match = link_entity == dst_entity
                else:
                    match = False
        if match:
            cond = conditionXml.getAttribute("link-entity")
            if cond:
                if link_entity:
                    match = link_entity.category() == cond or link_entity.type() == cond or cond == ANY_TYPE
                else:
                    match = False
        if match:
            cond = conditionXml.getAttribute("dst-entity")
            if cond:
                if dst_entity:
                    match = dst_entity.category() == cond or dst_entity.type() == cond or cond == ANY_TYPE
                else:
                    match = False

        if match:
            cond = conditionXml.getAttribute("special")
            if cond == "display-already-has-connection-to-output":
                match = self.specialDisplayAlreadyHasConnectionToOutput(dst_sourcePort)
        return match

    def connectsToDisplay(self, trail):
        # Instrumentation links connects to at a display, or a node that does, or ..
        display = None
        trail.append(self)
        if self._startObj:
            if self._startObj.category() == "port":
                if self._startObj.entity().category() == "display":
                    display = self._startObj.entity()
            else: # node
                otherLink = None
                for link in self._startObj.links():
                    if link not in trail and link.type() == self._type:
                        otherLink = link # first link will do
                        break
                if otherLink:
                    display = otherLink.connectsToDisplay(trail)
        if display is None:
            if self._endObj:
                if self._endObj.category() == "port":
                    if self._endObj.entity().category() == "display":
                        display = self._endObj.entity()
                else: # node
                    otherLink = None
                    for link in self._endObj.links():
                        if link not in trail and link.type() == self._type:
                            otherLink = link # first link will do
                            break
                    if otherLink:
                        display = otherLink.connectsToDisplay(trail)
        return display

    def specialDisplayAlreadyHasConnectionToOutput(self, dstSourcePort):
        match = False
        display = self.connectsToDisplay([])
        if display is not None:
            displayPort = list(display.ports().values())[0] # displays only have one port
            for link in displayPort.links():
                if link != self: # other instrumentation links
                    endConnectable = None
                    nextLink = link
                    while nextLink and not endConnectable:
                        connectable = nextLink.endObject() # instrumentation links start at display
                        if connectable.type() != self._type:
                            endConnectable = connectable
                        else:
                            nextLinkSave = nextLink
                            nextLink = None
                            for lnk in connectable.links():
                                if lnk != nextLinkSave and lnk != self:
                                    nextLink = lnk
                                    break
                    #endwhile
                    if endConnectable:
                        endDirn, endSourcePort = endConnectable.directionAndSource([])
                        if endSourcePort == dstSourcePort:
                            match = True
                            break
        return match

    def save(self, indent=None, level=0, saveDefaults=False, includeZOrder=False):
        result = ''
        nl = '\n'
        ind = ''
        if indent is not None:
            for i in range(level): ind += indent
        else:
            nl = ''
        result = ind + result
        result += '<link id="' + str(self.objectId()) + '" type="' + self._type + '"'
        if self._startObj is not None:
            otherId = self._startObj.objectId()
            result += ' start-id="' + str(otherId) + '"'
        if self._endObj is not None:
            otherId = self._endObj.objectId()
            result += ' end-id="' + str(otherId) + '"'
        line_draw = "straight"
        if self._defn is not None:
            line_draw = self._defn.getAttribute("draw")
        if saveDefaults or self._lineDraw != line_draw:
            result += ' draw="' + self._lineDraw + '"'
        result += '/>' + nl
        return result
