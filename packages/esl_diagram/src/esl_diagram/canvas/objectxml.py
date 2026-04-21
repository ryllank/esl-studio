#! /usr/bin/python

import wx

from .object import Orientation, Scale

def getXmlPosition(xmlElement, pos):
    result = None
    x = pos.x
    y = pos.y
    xstr = xmlElement.getAttribute("x")
    ystr = xmlElement.getAttribute("y")
    if xstr: x = int(xstr)
    if ystr: y = int(ystr)
    if xstr or ystr:
        result = wx.Point(x, y)
    return result

def getXmlScale(xmlElement):
    result = None
    scaleStr = xmlElement.getAttribute("scale")
    if scaleStr:
        scaleStrElements = scaleStr.split(",")
        nrElements = len(scaleStrElements)
        if nrElements == 1:
            result = Scale(True, float(scaleStr), float(scaleStr))
        elif nrElements == 2:
            result = Scale(False, float(scaleStrElements[0]), float(scaleStrElements[1]))
    return result

def getXmlOrientation(xmlElement):
    result = None
    orientation = xmlElement.getAttribute("orientation")
    if orientation:
        if orientation == 'normal': result = Orientation.normal
        elif orientation == 'rotate90': result = Orientation.rotate90
        elif orientation == 'rotate180': result = Orientation.rotate180
        elif orientation == 'rotate270': result = Orientation.rotate270
        elif orientation == 'mirrorXAxis': result = Orientation.mirrorXAxis
        elif orientation == 'mirrorYAxis': result = Orientation.mirrorYAxis
        elif orientation == 'mirrorUpDiag': result = Orientation.mirrorUpDiag
        elif orientation == 'mirrorDownDiag': result = Orientation.mirrorDownDiag
        else:
            raise Exception('Unrecognised orientation string ("%s") - expecting one of "normal" "rotate90" "rotate180" "rotate270" "mirrorXAxis" "mirrorYAxis" "mirrorUpDiag" or "mirrorDownDiag"' %orientation)
    return result

def getDraggable(xmlElement):
    result = None
    value = xmlElement.getAttribute("drag")
    if value:
        if value == "true": result = True
        elif value == "false": result = False
    return result

def getGrabbable(xmlElement):
    result = None
    value = xmlElement.getAttribute("grabbable")
    if value:
        if value == "true": result = True
        elif value == "false": result = False
    return result

def getVisible(xmlElement):
    result = None
    value = xmlElement.getAttribute("visible")
    if value:
        if value == "true": result = True
        elif value == "false": result = False
    return result

def getSelectable(xmlElement):
    result = None
    value = xmlElement.getAttribute("select")
    if value:
        if value == "true": result = True
        elif value == "false": result = False
    return result

def getOrientable(xmlElement):
    result = None
    value = xmlElement.getAttribute("orient")
    if value:
        if value == "true": result = True
        elif value == "false": result = False
    return result

def getScalable(xmlElement):
    result = None
    value = xmlElement.getAttribute("scalable")
    if value:
        if value == "true": result = True
        elif value == "false": result = False
    return result

def getCopyable(xmlElement):
    result = None
    value = xmlElement.getAttribute("copy")
    if value:
        if value == "true": result = True
        elif value == "false": result = False
    return result

def getContextMenu(xmlElement):
    result = None
    contextMenuElement = xmlElement.getXmlElementByName("context-menu")
    if contextMenuElement:
        result = contextMenuElement.getAttribute("menu")
    return result

def getActivate(xmlElement):
    result = None
    activateElement = xmlElement.getXmlElementByName("activate")
    if activateElement:
        result = activateElement.getAttribute("action")
    return result

def setObjectProperties(obj, xmlElement):
    if xmlElement:
        posn = obj.position()
        value = getXmlPosition(xmlElement, posn)
        if value is not None:
            obj.setPosition(value)
        value = getXmlScale(xmlElement)
        if value is not None:
            obj.setScale(value)
        value = getXmlOrientation(xmlElement)
        if value is not None:
            obj.setOrientation(value)
        value = getDraggable(xmlElement)
        if value is not None: obj._draggable = value
        value = getGrabbable(xmlElement)
        if value is not None: obj._grabbable = value
        value = getVisible(xmlElement)
        if value is not None: obj._visible = value
        value = getSelectable(xmlElement)
        if value is not None: obj._selectable = value
        value = getOrientable(xmlElement)
        if value is not None: obj._orientable = value
        value = getScalable(xmlElement)
        if value is not None: obj._scalable = value
        value = getCopyable(xmlElement)
        if value is not None: obj._copyable = value
        value = getContextMenu(xmlElement)
        if value is not None: obj._contextmenu = value
        value = getActivate(xmlElement)
        if value is not None: obj._activate = value
