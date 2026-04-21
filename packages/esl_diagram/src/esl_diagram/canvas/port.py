#! /usr/bin/python

from enum import Enum

import wx

from .. import xmlutil as xut

from . import arraylinking
from .transform import Orientation, Side, doSideReorientation
from .objectxml import getXmlOrientation
from .connectable import Connectable
from .group import Group
from .element import Element

PortConnectorSeparator = '-'

# Port direction
class PortDirection(Enum):
    unknown = 0
    input = 1
    output = 2
    io = 3


def directionEnum(directionStr):
    result = PortDirection.unknown
    if directionStr:
        if directionStr == 'input': result = PortDirection.input
        elif directionStr == 'output': result = PortDirection.output
        elif directionStr == 'io': result = PortDirection.io
    return result

def getDirection(xmlElement):
    result = None
    directionStr = xmlElement.getAttribute("direction")
    if directionStr:
        result = directionEnum(directionStr)
    return result

def directionStr(direction):
    result = "?"
    if direction:
        if direction == PortDirection.input : result = 'input'
        elif direction == PortDirection.output : result = 'output'
        elif direction == PortDirection.io : result = 'io'
    return result

class Port(Connectable, Group):
    # _portType - string for type of Port
    # _direction - PortDirectionEnum attribute (input, output, io)
    # parent() is the entity
    def __init__(self, type, diagram, position = None, orientation = None, descr = None, index = 0):
        self._type = type
        self._direction = PortDirection.unknown
        self._sign = ''
        self._signOptions = []
        self._id = index
        self._tag = ''
        self._tagObject = None
        Connectable.__init__(self)
        ###Composite.__init__(self, diagram, position, orientation)
        ###self._category = "port"
        ###self._type = type
        ###self._descr = descr
        Group.__init__(self, "port", type, diagram, position, orientation, descr)
        portElement = descr
        if not portElement: portElement = self._defn
        if portElement:
            id = portElement.getAttribute("id")
            if id: self._id = id
            tag = portElement.getAttribute("tag")
            if tag: self._tag = tag
        ###self.setShape()
        self._draggable = False
        #self._orientable = False - need this to use setOrientation
        self._scalable = False
        self._copyable = False

    def objectId(self):
        return str(self._parent.objectId()) + PortConnectorSeparator + str(self._id)

    def id(self): return self._id

    def __str__(self):
        entityInfo = ""
        if self._parent is not None:
            entityInfo = self._parent.category() + "-" + str(self._parent.objectId())
            entityInfo += ":" + str(self._id)
        return "<Port(" + self._type + ")" + entityInfo + ">"

    def direction(self):
        return self._direction
    def directionAndSource(self, trail):
        dirn = self._direction
        sourcePort = None
        if dirn == PortDirection.output:
            sourcePort = self
        elif dirn == PortDirection.input:
            for link in self._links:
                trail.append(self)
                lnkDirn, lnkSourcePort = link.directionAndSource(trail)
                if lnkDirn == PortDirection.output or dirn == PortDirection.unknown:
                    dirn = lnkDirn
                    sourcePort = lnkSourcePort
        return dirn, sourcePort
    def tag(self): return self._tag
    def sign(self): return self._sign

    def autoPositioning(self):
        result = True
        if self._descr:
            x = self._descr.getAttribute("x")
            y = self._descr.getAttribute("y")
            result = x is None and y is None
        return result

    def autoOrientating(self):
        result = True
        if self._descr:
            orientation = self._descr.getAttribute("orientation")
            result = orientation is None
        return result

    #def setPosition(self, posn): # a port's position is given relative (so we overide the component stuff)
    #    self._position = posn

    def portSide(self):
        side = None
        orient = self.orientation()
        if orient == Orientation.mirrorYAxis or orient == Orientation.rotate180:
            side = Side.left
        elif orient == Orientation.rotate90 or orient == Orientation.mirrorUpDiag:
            side = Side.top
        elif orient == Orientation.rotate270 or orient == Orientation.mirrorDownDiag:
            side = Side.bottom
        elif orient == Orientation.normal or orient == Orientation.mirrorXAxis:
            side = Side.right
        return side

    def addTagText(self, tag):
        side = None
        tagExt = wx.Rect()
        self._tag = tag
        if self._tagObject: self.remove(self._tagObject)
        self._tagObject = None
        if tag:
            label_text_descr = self._diagram.themeProperties().PortLabelTextDescr
            tagStr = '<text>' + self._tag +'</text>'
            self._tagObject = Element('text', self._diagram, None, None, label_text_descr)
            self._tagObject.update(xut.xmlElement(tagStr), [])
            self.add(self._tagObject)
            tagExt = self._tagObject.extent()
            side = self.portSide()
        return side, tagExt

    def positionPortTag(self):
        if self._tagObject is not None:
            entityOrientation = self._parent.orientation()
            hmargin = self._diagram.themeProperties().PortLabelHMargin
            vmargin = self._diagram.themeProperties().PortLabelVMargin
            tagExt = self._tagObject.extent()
            baseExt = self.baseSize()
            stalk = -baseExt.x
            side = self.portSide()
            showSide = doSideReorientation(side, entityOrientation)
            posn = self.getDiagramPoint(self._position)
            entityPosn = self._parent.position()
            if showSide == Side.left or showSide == Side.right:
                if posn.x < entityPosn.x:
                    offset = wx.Point(stalk, 0)
                    offset.x += round(tagExt.width / 2)
                    offset.x += hmargin
                else:
                    offset = wx.Point(-stalk, 0)
                    offset.x -= round(tagExt.width / 2)
                    offset.x -= hmargin
            else:
                if posn.y < entityPosn.y:
                    offset = wx.Point(0, stalk)
                    offset.y += round(tagExt.height / 2)
                    offset.y += vmargin
                else:
                    offset = wx.Point(0, -stalk)
                    offset.y -= round(tagExt.height / 2)
                    offset.y -= vmargin
            self._tagObject.setPosition(offset)

    def setShape(self, newType=""):
        if newType:
            newDefn = self._diagram.registry().get(self._category, newType)
            baseType, dimensionsInfo = arraylinking.parseDatatype(newType)
            if newDefn is None:
                if baseType:
                    newDefn = arraylinking.findCompatibleDefn(self._diagram, self._category, newType, baseType, dimensionsInfo)
            if newDefn:
                self.set_type(newType)
                self._defn = newDefn
                self._baseType = baseType
                self._dimensionsInfo = dimensionsInfo
                self.removeAll()
        if self._descr:
            direction = getDirection(self._descr)
            if direction: self._direction = direction
            if not self._sign:
                sign = self._descr.getAttribute("sign")
                if sign: self._sign = sign
        Group.setShape(self)
        # Look for optional extra graphics depending on direction
        optionElement = self._defn.findXmlElementWithAttribute("option",
            "direction", directionStr(self._direction))
        if optionElement:
            Group.update(self, optionElement, [])
        # Look for optional extra graphics depending on sign
        optionElement = self._defn.findXmlElementWithAttribute("option",
               "sign", self._sign)
        if optionElement:
            self._signOptions = Group.update(self, optionElement, [])
        #if self._tag:
        #    self.setTag(self._tag)

    def update(self, updateDescr, deleteList):
        if updateDescr is not None:
            if not isinstance(updateDescr, xut.XmlElement):
                updateDescr = xut.xmlElement(updateDescr)
            if updateDescr:
                newType = ""
                type = updateDescr.getAttribute("type")
                if type != self._type:
                    newType = type
                sign = updateDescr.getAttribute("sign")
                if sign:
                    self._sign = sign
                    for obj in self._signOptions:
                        self.remove(obj)
                self.setShape(newType)

    def entity(self):
        return self._parent

    def startLink(self):
        link = None
        link, errorMsg = self._diagram.makeLink(self._type, self)
        if not link:
            if self._defn:
                alternateLinkTypes = self._defn.getAttribute("equivalent-types")
                if alternateLinkTypes:
                    alternateLinkTypes = list(map(lambda item: item.strip(), alternateLinkTypes.split("|")))
                    for alternateLinkType in alternateLinkTypes:
                        link, errorMsg = self._diagram.makeLink(alternateLinkType, self)
                        if link:
                            break
        if link:
            added, errorMsg = self.addLink(link, False)
            if not added:
                link = None
        if not link and not errorMsg:
            errorMsg = "No link definition found for port type " + self._type
        return link, errorMsg

    def endLink(self, link, alertNode=True):
        result = False
        errorMsg = ""
        result, errorMsg = link.validConnectable(self)
        if result:
            added, errorMsg = self.addLink(link, False)
            if added:
                link.endOnConnectable(self)
                result = True
                if alertNode:
                    self.alertObject(self._diagram.themeProperties().AlertConnectionTime)
        return result, errorMsg

    def portConnectionStr(self):
        return

    def togglesign(self):
        if self._sign:
            if self._sign == 'plus': self._sign = 'minus'
            elif self._sign == 'minus': self._sign = 'plus'
            for obj in self._signOptions:
                self.remove(obj)
            self.setShape()
        # Look for optional extra graphics depending on sign
        #optionElement = self._defn.findXmlElementWithAttribute("option",
        #       "sign", self._sign)
        #if optionElement:
        #    self.update(optionElement)

    def baseExtent(self):
        #transform = self.getTransform()
        posn = self.getDiagramPoint(self._position)
        ext = wx.Rect(posn.x - 1, posn.y - 1, 2, 2)
        for obj in self._components:
            if obj != self._tagObject and obj not in self._signOptions:
                #pt = self.getDiagramPoint(obj._position, transform)
                obj_ext = obj.extent()
                if obj_ext:
                    #obj_ext.Offset(pt)
                    ext = ext.Union(obj_ext)
        return ext

    def baseSize(self, transform=None):
        ext = wx.Rect(0, 0, 2, 2)
        belowTransform = self.objectTransform()
        if transform:
            belowTransform = belowTransform.applyTransform(transform, self)
        for obj in self._components: # last added on top
            if obj != self._tagObject and obj not in self._signOptions:
                objSize = obj.getSize(belowTransform)
                if objSize:
                    ext = ext.Union(objSize)
        return ext

    def save(self, indent = None, level = 0, saveDefaults=False, dynamicPorts=False, fullObjectId=True, includeZOrder=False):
        result = ''
        nl = '\n'
        ind = ''
        if indent is not None:
            for i in range(level): ind += indent
        else:
            nl = ''

        doAllFields = saveDefaults or dynamicPorts
        descrSign = None
        descrOrientation = None
        descrTag = None
        if self._descr is not None:
            descrSign = self._descr.getAttribute('sign')
            descrX = self._descr.getAttribute("x")
            descrX = int(descrX) if descrX else 0
            descrY = self._descr.getAttribute("y")
            descrY = int(descrY) if descrY else 0
            descrOrientation = getXmlOrientation(self._descr)
            descrTag = self._descr.getAttribute('tag')
        port_id = self._id
        if fullObjectId:
            port_id = self.objectId()
        head = '<' + self._category + ' id="' + str(port_id) + '"'
        body = ''
        if doAllFields: body += ' type="' + self._type + '"'
        if doAllFields: body += ' direction="' + directionStr(self._direction) + '"'
        if self._tag and (doAllFields or (descrTag and self._tag != descrTag)):
            body += ' tag="' + self._tag +'"'
        if ((not self.autoPositioning() and (self._position.x != descrX or self._position.y != descrY)) or
            (not self.autoPositioning() and saveDefaults)):
            body += ' x="' + str(self._position.x) + '" y="' + str(self._position.y) + '"'
        if saveDefaults or (not self.autoOrientating() and self._orientation != descrOrientation):
            body += ' orientation="' + str(self._orientation) + '"'
        # we dont support scaled ports
        if self._sign: # now always save sign if has one ###and (doAllFields or self._sign != descrSign):
            body += ' sign="' + self._sign + '"'
        if body: result = ind + head + body + '/>' + nl
        return result
