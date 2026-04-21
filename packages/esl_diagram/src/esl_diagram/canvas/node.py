#! /usr/bin/python

import wx

from .. import xmlutil as xut

from . import colournames as Colours
from .object import Composite
from .connectable import Connectable
from .port import Port, PortDirection
from .group import Group

class Node(Connectable, Group):
    # _nodeType - string for type of Node
    def __init__(self, type, diagram, position = None, link = None, descr = None):
        Connectable.__init__(self)
        ###Composite.__init__(self, diagram, position)
        ###self._type = type
        ###self._category = "node"
        ###self._descr = descr
        ###self._defn = self._diagram.registry().get(self._category, self._type)
        Group.__init__(self, "node", type, diagram, position, None, descr)
        ###self.setShape()
        if self._defn is not None and link is not None:
            added, errorMsg = self.addLink(link, True)
        self._draggable = True
        self._orientable = False
        self._scalable = False

    def __str__(self):
        return "<Node-" + str(self.objectId()) + "(" + self._type + ")@" + str(self.position()) + ">"

    def setShape(self, newType=""):
        if newType:
            self.set_type(newType)
            self._defn = self._diagram.registry().get(self._category, self._type)
            self.removeAll()
        Group.setShape(self)

    def links(self): return self._links

    def directionAndSource(self, trail):
        dirn = PortDirection.unknown
        sourcePort = None
        for link in self._links:
            trail.append(self)
            lnkDirn, lnkSourcePort = link.directionAndSource(trail)
            if lnkDirn == PortDirection.output or dirn == PortDirection.unknown:
                dirn = lnkDirn
                sourcePort = lnkSourcePort
        return dirn, sourcePort

    def drawOverlay(self, dc):
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetPen(wx.Pen(Colours.get(self._diagram.properties().OverlayPenColour),
                         self._diagram.properties().OverlayPenWidth,
                         self._diagram.properties().OverlayPenStyle))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        ext = self.getOverlayExtent()
        radius = round(ext.width / 2)
        dc.DrawCircle(self.position().x, self.position().y, radius)

    def dragBy(self, dc, displacement, refreshCache=None):
        newPos = self.position() + displacement
        Composite.dragBy(self, dc, displacement, refreshCache)
        for link in self._links:
            if self.linkConnectsAtEnd(link):
                link.dragLink(dc, None, newPos, refreshCache)
            else:
                link.dragLink(dc, newPos, None, refreshCache)

    def update(self, updateDescr, deleteList):
        if updateDescr is not None:
            if not isinstance(updateDescr, xut.XmlElement):
                updateDescr = xut.xmlElement(updateDescr)
            if updateDescr:
                Group.update(self, updateDescr, deleteList)
                self.moveLinks()

    def moveLinks(self):
        pos = self.getDiagramPosition()
        for link in self._links:
            if self.linkConnectsAtEnd(link):
                link.moveLink(None, pos)
            else:
                link.moveLink(pos, None)

    def startLink(self):
        link = None
        errorMsg = ""
        if len(self._links) > 0:
            #initialLink = self._links[0]
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
        return link, errorMsg

    def joinLink(self, link, alertNode=True):
        result, errorMsg = link.validConnectable(self)
        if result:
            result, errorMsg = self.addLink(link, True)
            if result:
                link.endOnConnectable(self)
                if alertNode:
                    self.alertObject(self._diagram.themeProperties().AlertConnectionTime)
        return result, errorMsg

    def isLoose(self, srcLink, deleteList, doneNodes):
        loose = True
        if self not in doneNodes:
            doneNodes.append(self)
            for link in self._links:
                if link is not srcLink and link.type() == srcLink.type():
                    otherEnd = link.otherEnd(self)
                    if otherEnd is not None:
                        if isinstance(otherEnd, Port):
                            if otherEnd.entity() not in deleteList:
                                loose = False
                            break
                        elif isinstance(otherEnd, Node):
                            loose = otherEnd.isLoose(link, deleteList, doneNodes)
        return loose

    def gatherNodeDeleteList(self, srcLink, deleteList, doneNodes):
        if self not in doneNodes:
            doneNodes.append(self)
            allLinks = self._links[:]
            srcLinkIsDisplay = srcLink.connectsToDisplay([]) is not None
            deleteSelf = True
            displayLinks = {}
            looseLinks = {}
            for link in allLinks:
                if link is not srcLink and link not in deleteList:
                    linkIsDisplayLink = link.connectsToDisplay([]) is not None
                    linkIsLoose = False
                    displayLinks[link] = linkIsDisplayLink
                    if srcLinkIsDisplay:
                        if not linkIsDisplayLink:
                            deleteSelf = False
                    else:
                        if not linkIsDisplayLink:
                            otherEnd = link.otherEnd(self)
                            if isinstance(otherEnd, Node):
                                linkIsLoose = otherEnd.isLoose(link, deleteList, [])
                            else:
                                linkIsLoose = False
                            if not linkIsLoose:
                                deleteSelf = False
                    looseLinks[link] = linkIsLoose
            for link in allLinks:
                if link is not srcLink and link not in deleteList:
                    doLink = False
                    linkIsDisplayLink = displayLinks[link]
                    if linkIsDisplayLink:
                        if deleteSelf:
                            doLink = True
                    else:
                        linkIsLoose = looseLinks[link]
                        if linkIsLoose and deleteSelf:
                            doLink = True
                    if doLink:
                        link.gatherNodeDeleteList(deleteList, doneNodes)
                        if link not in deleteList:
                            deleteList.append(link)
            if deleteSelf and self not in deleteList:
                deleteList.append(self)
        pass

    def gatherDeleteList(self, deleteList):
        if self not in deleteList:
            allLinks = self._links[:]
            for link in allLinks:
                if link not in deleteList:
                    link.gatherDeleteList(deleteList)
                    if link not in deleteList:
                        deleteList.append(link)
            if self not in deleteList:
                deleteList.append(self)

    def gatherCopyList(self, copyList):
        for link in self._links:
            if link not in copyList:
                link.gatherCopyList(copyList)
