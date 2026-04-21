#! /usr/bin/python

from collections import OrderedDict

import wx

from .. import xmlutil as xut

from .transform import Orientation, doReorientation, StraightOrientations, Side, Scale, reorientatePoint, doOppositeReorientation
from .object import Composite
from .objectxml import setObjectProperties
from .port import Port, directionStr, PortDirection
from .group import Group

def roundup(dist, snap):
    fract = int(dist/snap)
    result = (fract+1)*snap
    return result

class Entity(Group):

    def __init__(self, category, type, diagram, position = None, orientation = None, descr = None):
        Group.__init__(self, category, type, diagram, position, orientation, descr)
        self._ports = OrderedDict()
        self._dynamic_ports = False
        self._show_port_tags = False
        self._adjust_body = True
        if self._defn:
            self._defnPortsElement = self._defn.getXmlElementByName("ports")
            if self._defnPortsElement:
                if self._defnPortsElement.getAttribute("dynamic") == 'true':
                    self._dynamic_ports = True
                if self._defnPortsElement.getAttribute("show-tags") == 'true':
                    self._show_port_tags = True
                if self._defnPortsElement.getAttribute("adjust-body") == 'false':
                    self._show_port_tags = False
        descrPortsElement = None
        if self._descr and self._dynamic_ports:
            descrPortsElement = self._descr.getXmlElementByName("ports")
        deleteList = []
        if descrPortsElement:
            self.updatePorts(descrPortsElement, deleteList)
        else:
            self.setPorts(self._defn, descr, deleteList)
        self.portsAdjustment()

    def __str__(self):
        return "<" + self._category + "-" + str(self.objectId()) + "(" + self._type + ")@" + str(self.position()) + ">"

    def setShape(self, newType=""):
        if newType:
            defn = self._diagram.registry().get(self._category, newType)
            if defn:
                self._defn = defn
                self.set_type(newType)
                self.removeAll()
        Group.setShape(self)

    def ports(self):
        return self._ports

    def unlinkPorts(self, portsODict, deleteList):
        portsDeleteList = []
        for port in list(portsODict.values()):
            for link in port.links():
                link.gatherDeleteList(portsDeleteList)
        if len(portsDeleteList) > 0:
            newThings = filter(lambda thing: thing not in deleteList, portsDeleteList)
            deleteList.extend(newThings)

    def getOrderedPriorPorts(self, priorPorts:OrderedDict) -> (list, list):
        priorPortsInputs = []
        priorPortsOthers = []
        for priorPort in priorPorts.values():
            if priorPort.direction() == PortDirection.input:
                priorPortsInputs.append(priorPort)
            else:
                priorPortsOthers.append(priorPort)
        return priorPortsInputs, priorPortsOthers

    def setPorts(self, descrElement, addnlDescr, deleteList):
        priorPorts = OrderedDict(self._ports)
        priorPortsInputs, priorPortsOthers = self.getOrderedPriorPorts(priorPorts)
        newPorts = []
        if descrElement is not None:
            portsElement = None
            if descrElement.name() == "ports": portsElement = descrElement
            else: portsElement = descrElement.getXmlElementByName("ports")
            if portsElement:
                portElements = portsElement.getXmlElementListByName("port")
                portIndex = 0
                inputIx = 0
                otherIx = 0
                for portElement in portElements:
                    portIndex += 1
                    type = portElement.getAttribute("type")
                    if type:
                        port, errorMsg = self._diagram.makePort(type, portElement, portIndex)
                        if port:
                            self.add(port)
                            priorPort = None
                            if port.direction() == PortDirection.input:
                                if inputIx < len(priorPortsInputs):
                                    priorPort = priorPortsInputs[inputIx]
                                inputIx += 1
                            else:
                                if otherIx < len(priorPortsOthers):
                                    priorPort = priorPortsOthers[otherIx]
                                otherIx += 1
                            if (priorPort and priorPort.type() == port.type() and
                                priorPort.direction() == port.direction()):
                                self.transferLinks(priorPort, port)
                            newPorts.append(port)
                        elif errorMsg:
                            self._diagram._canvas.raiseCanvasApplicationNotifyEvent('', "display", errorMsg)

                self.unlinkPorts(priorPorts, deleteList)
                self.removePorts(priorPorts)
                for port in newPorts:
                    self.addPort(port)
                if addnlDescr:
                    self.setPortFeatures(addnlDescr)

    def setPortFeatures(self, addnlDescr):
        portElementList = addnlDescr.getXmlElementListByName("port")   #not recurse
        for portElement in portElementList:
            sign = portElement.getAttribute("sign")
            type = portElement.getAttribute("type")
            if sign or type:
                portId = int(portElement.getAttribute("id"))
                port = self._ports.get(portId)
                if port:
                    port.update(portElement, [])

    def getPortsPerSide(self):
        nPortsPerSide = [0, 0, 0, 0]
        for port in list(self._ports.values()):
            portAutoOrientating = port.autoOrientating()
            if portAutoOrientating:
                if port.direction() == PortDirection.input:
                    port.setOrientation(Orientation.mirrorYAxis)
                else:
                    port.setOrientation(Orientation.normal)
            side = port.portSide()
            if side is not None:
                nPortsPerSide[side] += 1
        return nPortsPerSide

    def addPortTags(self):
        maxTagSizes = [wx.Size(), wx.Size(), wx.Size(), wx.Size()]
        for port in list(self._ports.values()):
            tag = port.tag()
            if tag:
                side, tagExt = port.addTagText(tag)
                if side is not None:
                    maxTagSizes[side].width = max(maxTagSizes[side].width, tagExt.width)
                    maxTagSizes[side].height = max(maxTagSizes[side].height, tagExt.height)
        return maxTagSizes

    def positionPortTags(self):
        for port in list(self._ports.values()):
            port.positionPortTag()

    def getBase(self):
        base = None
        baseSize = wx.Size(60, 40)
        for obj in self._components:
            type = obj.type()
            if obj.category() == 'group' and (type != 'annotation'):
                base = obj
                break
            elif obj.category() == 'element' and (type == 'rect' or type == 'ellipse'):
                base = obj
                break
        if base:
            if base._descr:
                if base.category() == 'group':
                    ext = base.getSize()
                    baseSize.width = ext.width
                    baseSize.height = ext.height
                else:
                    # Use original size (from definition)
                    width = base._descr.getAttribute("width")
                    height = base._descr.getAttribute("height")
                    if width:
                        baseSize.width = int(width)
                    if height:
                        baseSize.height = int(height)
        return base, baseSize

    def portsAdjustment(self):
        nPorts = len(self._ports)
        base, baseSize = self.getBase()
        newSize = wx.Size(baseSize)
        transposed = not self._orientation in StraightOrientations
        if nPorts > 0:
            nPortsPerSide = self.getPortsPerSide()
            ##print(">Entity.portsAdjustment self=" + str(self) + " orientation=" + str(self._orientation) + " baseSize=" + str(baseSize)+" nPortsPerSide="+str(nPortsPerSide))
            nLR = max(nPortsPerSide[Side.left], nPortsPerSide[Side.right])
            nTB = max(nPortsPerSide[Side.bottom], nPortsPerSide[Side.top])

            maxTagSizes = None
            if self._show_port_tags:
                maxTagSizes = self.addPortTags()

            spacing = self._diagram.themeProperties().PortSpacing
            tag_snap = self._diagram.themeProperties().PortTagSnap
            hmargin = self._diagram.themeProperties().PortLabelHMargin
            vmargin = self._diagram.themeProperties().PortLabelVMargin

            # TODO redo?
            vSpacing = spacing
            hSpacing = spacing
            widthLRTags = 0
            heightLRTags = 0
            widthTBTags = 0
            heightTBTags = 0
            widthSpaced = 0
            heightSpaced = 0
            if maxTagSizes:
                if not transposed:
                    if nLR > 0:
                        widthLRTags = baseSize.width + 2 * (max(maxTagSizes[Side.left].width, maxTagSizes[Side.right].width) + hmargin)
                        heightLRTags = nLR * (max(maxTagSizes[Side.left].height, maxTagSizes[Side.right].height) + vmargin)
                    if nTB > 0:
                        widthTBTags = max(maxTagSizes[Side.top].width, maxTagSizes[Side.bottom].width) + hmargin
                        if nTB > 1:
                            hSpacing = roundup(widthTBTags, tag_snap)
                        heightTBTags = baseSize.height + 2 * max(maxTagSizes[Side.top].height, maxTagSizes[Side.bottom].height) + vmargin
                else: # transposed
                    if nTB > 0:
                        widthTBTags = nTB * (max(maxTagSizes[Side.top].height, maxTagSizes[Side.bottom].height) + vmargin)
                        heightTBTags = baseSize.height + 2 * (max(maxTagSizes[Side.top].width, maxTagSizes[Side.bottom].width) + hmargin)
                    if nLR > 0:
                        widthLRTags = baseSize.width + 2 * max(maxTagSizes[Side.left].height, maxTagSizes[Side.right].height) + vmargin
                        heightLRTags = max(maxTagSizes[Side.left].width, maxTagSizes[Side.right].width) + hmargin
                        if nLR > 1:
                            hSpacing = roundup(heightLRTags, tag_snap)
                pass

            if not transposed:
                widthSpaced = nTB * hSpacing
                heightSpaced = nLR * vSpacing
            else:
                widthSpaced = nTB * vSpacing
                heightSpaced = nLR * hSpacing

            newSize.width = max(baseSize.width, widthSpaced, widthLRTags, widthTBTags)
            newSize.height = max(baseSize.height, heightSpaced, heightLRTags, heightTBTags)

            yLeft = - (nPortsPerSide[Side.left] // 2) * hSpacing
            if nPortsPerSide[Side.left] % 2 == 0:
                yLeft += hSpacing // 2
            yRight = - (nPortsPerSide[Side.right] // 2) * hSpacing
            if nPortsPerSide[Side.right] % 2 == 0:
                yRight += hSpacing // 2
            xBottom = - (nPortsPerSide[Side.bottom] // 2) * vSpacing
            if nPortsPerSide[Side.bottom] % 2 == 0:
                xBottom += vSpacing // 2
            xTop = - (nPortsPerSide[Side.top] // 2) * vSpacing
            if nPortsPerSide[Side.top] % 2 == 0:
                xTop += vSpacing // 2

            for port in list(self._ports.values()):
                portAutoPositioning = port.autoPositioning()
                ##print("*Entity.portsAdjustment port=" + str(port) + " auto="+str(portAutoPositioning)+" descr="+str(port._descr))
                if portAutoPositioning:
                    side = port.portSide()
                    x = 0
                    portPosn = port.position()
                    ext = port.baseSize()
                    stalk = -ext.x
                    if side == Side.left:
                        port.setPosition(wx.Point(-round(newSize.width/2) - stalk, yLeft))
                        yLeft += hSpacing
                    elif side == Side.right:
                        port.setPosition(wx.Point(+round(newSize.width/2) + stalk, yRight))
                        yRight += hSpacing
                    elif side == Side.bottom:
                        port.setPosition(wx.Point(xBottom, +round(newSize.height/2) + stalk))
                        xBottom += vSpacing
                    elif side == Side.top:
                        port.setPosition(wx.Point(xTop, -round(newSize.height/2) - stalk))
                        xTop += vSpacing
                    ##print("**Entity.portsAdjustment port="+str(port)+" side="+str(side)+" ext="+str(ext))
        #pass # end nPorts
        self.positionPortTags()

        # adjust base size even if no ports
        if base:
            if base.category() == 'group':
                scale = Scale(False, float(newSize.width) / float(baseSize.width), float(newSize.height) / float(baseSize.height))
                base.setScale(scale)
            else:
                base._size = newSize
            baseSize = newSize
        return baseSize

    def transferLinks(self, priorPort, newPort):
        links = priorPort.links().copy()
        for link in links:
            if link.startObject() == priorPort:
                added, errorMsg = newPort.addLink(link, False)
                link.startOnConnectable(newPort)
            else:
                added, errorMsg = newPort.addLink(link, True)
                link.endOnConnectable(newPort)
            priorPort.detachLink(link)

    def findPortForAnnotation(self, annotationId):
        portForAnnotation = None
        if annotationId.startswith('port'):
            annotationIdParts = annotationId.split('-')
            direction = PortDirection.unknown
            index = 0
            if len(annotationIdParts) == 3:
                if annotationIdParts[1] == "input":
                    direction = PortDirection.input
                    index = int(annotationIdParts[2])
            elif len(annotationIdParts) == 2:
                direction = PortDirection.output
                index = int(annotationIdParts[1])
            if direction != PortDirection.unknown:
                count = 0
                for port in list(self._ports.values()):
                    if port.direction() == direction:
                        count += 1
                        if count == index:
                            portForAnnotation = port
                            break
        return portForAnnotation

    def determinePortAnnotationPosition(self, annotation, baseSize):
        posn = None
        annotationId = annotation.annotationId()
        port = self.findPortForAnnotation(annotationId)
        if port is not None:
            spacing = self._diagram.themeProperties().AnnotationSpacing
            posn = port.position()
            portPosn = port.getDiagramPoint(port.position())
            x = portPosn.x
            y = portPosn.y
            if portPosn.y < self._position.y - baseSize.y//2:  # Top
                y -= spacing
                if portPosn.x > self._position.x + baseSize.x//2: # on right
                    x += spacing
                if portPosn.x < self._position.x < baseSize.x//2: # on left
                    x -= spacing
                else: # central port
                    y -= spacing
            elif portPosn.y > self._position.y + baseSize.y//2: # Bottom
                y += spacing
                if portPosn.x > self._position.x + baseSize.x//2: # on right
                    x += spacing
                if portPosn.x < self._position.x < baseSize.x//2: # on left
                    x -= spacing
                else: # central port
                    y += spacing
            elif portPosn.x > self._position.x + baseSize.x//2: # Right
                y -= spacing
                x -= spacing
                if port.sign():
                    y -= spacing
            else: # Left
                y -= spacing
                x += spacing
                if port.sign():
                    y -= spacing
            transform = port.getTransform()
            posn = wx.Point(transform.transformPoint(wx.RealPoint(x, y), port))
        return posn, port

    def getPortExtentLevels(self):
        portExtentHigh = None
        portExtentLow = None
        inputIx = 0
        otherIx = 0
        for port in self._ports.values():
            if port.direction() == PortDirection.input: # port annotation-ids are indexed (1+) by input or not.
                inputIx += 1
            else:
                otherIx += 1
            ext = port.extent() # does not include any port annotation
            if ext and abs(ext.height) > abs(ext.width): # Only want ports that go up or down
                # See if port has an annotation
                annotationId = "port-"
                if port.direction() == PortDirection.input:
                    annotationId += "input-" + str(inputIx)
                else:
                    annotationId += str(otherIx)
                annotation = self._annotations.get(annotationId) # It has
                if annotation:
                    annotationExt = annotation.extent()
                    if annotationExt:
                        ext = ext.Union(annotationExt)  # Merge in the extent of the port annotation with that of the port.
                high = ext.y
                if ext.height < 0:
                    high += ext.height
                low = ext.y
                if ext.height > 0:
                    low += ext.height
                if portExtentHigh is None or high < portExtentHigh:
                    portExtentHigh = high
                if portExtentLow is None or low > portExtentLow:
                    portExtentLow = low
        return portExtentHigh, portExtentLow

    def determineEntityAnnotationPosition(self, annotation, baseSize, lastAnnotation, portExtentHigh, portExtentLow):
        posn = None
        spacing = self._diagram.themeProperties().AnnotationSpacing
        isAttributeAnnotation = annotation.annotationId().startswith('attribute')
        if lastAnnotation is None:
            if self._category == "info":
                posn = wx.Point(0,0)
                posn.y -= spacing # so first annotation for the info is aligned to the info's position
            else:
                if baseSize is not None:
                    if isAttributeAnnotation:
                        posn = wx.Point(0, -baseSize.height//2)
                        if portExtentHigh is not None and portExtentHigh - self._position.y < posn.y:
                            posn.y = portExtentHigh - self._position.y
                        posn.y -= spacing
                    else:
                        posn = wx.Point(0, baseSize.height//2)
                        if portExtentLow is not None and portExtentLow - self._position.y > posn.y:
                            posn.y = portExtentLow - self._position.y
                        posn.y += spacing
                    posn = reorientatePoint(posn, doOppositeReorientation(self._orientation))
        else:
            posn = wx.Point(lastAnnotation.position())
            lastAnnotationExt = lastAnnotation.extent()
            if lastAnnotationExt is not None:
                adjustment = lastAnnotationExt.height
                if isAttributeAnnotation:
                    adjustment = - adjustment
                InvertedOrientations = [Orientation.rotate180, Orientation.mirrorXAxis, Orientation.rotate90, Orientation.mirrorUpDiag]
                inverted = self._orientation in InvertedOrientations
                if inverted:
                    adjustment = - adjustment
                if self._orientation in StraightOrientations:
                    posn.y += adjustment
                else:
                    posn.x += adjustment
        return posn

    def determineAnnotationPositions(self, baseSize=None):
        entityAnnotations = []
        attributeAnnotations = []
        portAnnotations = []
        for annotation in list(self._annotations.values()):
            if annotation.visible():
                annotationId = annotation.annotationId()
                if annotationId.startswith('port'):
                    portAnnotations.append(annotation)
                elif annotationId.startswith('attribute'):
                    attributeAnnotations.append(annotation)
                else:
                    entityAnnotations.append(annotation)
        if baseSize is None:
            base, baseSize = self.getBase()
        if not self._orientation in StraightOrientations:
            baseSize = wx.Size(baseSize.height, baseSize.width)
        for annotation in portAnnotations:
            posn, port = self.determinePortAnnotationPosition(annotation, baseSize) #### TODO
            if port is not None:
                if posn is not None:
                    annotation.setPosition(posn)
                # Set port's annotation text's justification
                text = annotation.getTextElement()
                portPosn = port.getDiagramPoint(port.position())
                if text is not None:
                    if portPosn.x < self._position.x:
                        text.setJustify("right")
                    elif portPosn.x > self._position.x:
                        text.setJustify("left")
                    else:
                        text.setJustify("centre")
        portExtentHigh, portExtentLow =self.getPortExtentLevels()
        lastAnnotation = None
        for annotation in entityAnnotations:
            posn = self.determineEntityAnnotationPosition(annotation, baseSize, lastAnnotation, portExtentHigh, portExtentLow)
            if posn is not None:
                annotation.setPosition(posn)
            lastAnnotation = annotation
        lastAnnotation = None
        attributeAnnotations.reverse()
        for annotation in attributeAnnotations:
            posn = self.determineEntityAnnotationPosition(annotation, baseSize, lastAnnotation, portExtentHigh, portExtentLow)
            if posn is not None:
                annotation.setPosition(posn)
            lastAnnotation = annotation

    def setAnnotations(self, addnlDescr, baseSize=None):
        clear = addnlDescr.getAttribute("clear-annotations")
        clearAnnotations = False
        if clear and clear == "true":
            clearAnnotations = True
        annotationElementList = addnlDescr.getXmlElementListByName("annotation")   #not recurse
        annotationIds = []
        for annotationElement in annotationElementList:
            annotationId = annotationElement.getAttribute('id')
            annotationIds.append(annotationId)
            annotation = self.getAnnotation(annotationId)
            if not annotation:
                replaceId = annotationElement.getAttribute('replace-id')
                if replaceId:
                    annotation = self.getAnnotation(replaceId)
                    if annotation:
                        self.replaceAnnotationId(annotation, annotationId)
            if annotation:
                remove = annotationElement.getAttribute('remove')
                if remove and remove != 'false': # so 'true'
                    self.removeAnnotation(annotation)
                else:
                    annotation.update(annotationElement, [])
            else:
                if annotationElement.getAttribute('visible') != "false":
                    annotation = self.setAnnotation(annotationElement)
        if clearAnnotations:
            for id, annotation in list(self._annotations.items()):
                if id not in annotationIds:
                    self.remove(annotation)
                    del self._annotations[id]
        self.determineAnnotationPositions(baseSize)

    def update(self, updateDescr, deleteList):
        if updateDescr is not None:
            if not isinstance(updateDescr, xut.XmlElement):
                updateDescr = xut.xmlElement(updateDescr)
            if updateDescr:
                # Special case when update used to change entity's type.
                type = updateDescr.getAttribute("type")
                if type and type != self._type:
                    self.setShape(type)
                setObjectProperties(self, updateDescr)
                if self._dynamic_ports:
                    if updateDescr.name() == 'ports': portsElement = updateDescr
                    else: portsElement = updateDescr.getXmlElementByName("ports", recurse=True)
                    if portsElement:
                        self.updatePorts(portsElement, deleteList)
                baseSize = self.portsAdjustment()
                self.setAnnotations(updateDescr, baseSize)
                self.setPortFeatures(updateDescr)
                self.moveLinks()

    def updatePorts(self, portsElement, deleteList):
        if self._dynamic_ports:
            self.setPorts(portsElement, None, deleteList)

    def removePorts(self, portsODict):
        for port in list(portsODict.values()):
            self.remove(port)
            del self._ports[int(port.id())]

    def addPort(self, port):
        portId = int(port.id())
        if portId in self._ports:
            raise Exception('Entity cannot have duplicate port id "' + portId + '"')
        else:
            self._ports[portId] = port

    def getPort(self, portId):
        port = self._ports.get(int(portId))
        return port

    def adjustLinks(self, dc, refreshCache=None):
        self.portsAdjustment()
        self.dragLinks(dc, refreshCache)

    def dragLinks(self, dc, refreshCache=None):
        for port in list(self._ports.values()):
            pos = port.getDiagramPosition()
            for link in port.links():
                if link.startObject() is port:
                    link.dragLink(dc, pos, None, refreshCache)
                else:
                    link.dragLink(dc, None, pos, refreshCache)

    def moveLinks(self):
        for port in list(self._ports.values()):
            pos = port.getDiagramPosition()
            for link in port.links():
                if link.startObject() is port:
                    link.moveLink(pos, None)
                else:
                    link.moveLink(None, pos)

    def dragBy(self, dc, displacement, refreshCache=None):
        initPos = self.position()
        Composite.dragBy(self, dc, displacement, refreshCache)
        self.dragLinks(dc, refreshCache)

    def gatherDeleteList(self, deleteList):
        if self not in deleteList:
            for port in list(self._ports.values()):
                allLinks = port.links()[:]
                for link in allLinks:
                    if link not in deleteList:
                        link.gatherDeleteList(deleteList)
                        if link not in deleteList:
                            deleteList.append(link)
            if self not in deleteList:
                deleteList.append(self)

    def gatherCopyList(self, copyList):
        for port in list(self._ports.values()):
            for link in port.links():
                if link not in copyList:
                    link.gatherCopyList(copyList)

    def applyOrientation(self, dc, orientation):
        extent = self.getOverlayExtent()
        oldOrientation = self._orientation
        newOrientation = doReorientation(self._orientation, orientation)
        self.setOrientation(newOrientation)
        baseSize = self.portsAdjustment()
        self.determineAnnotationPositions(baseSize)
        extent = extent.Union(self.getOverlayExtent())
        extent.Inflate(self._diagram.properties().OverlayMargin,
                       self._diagram.properties().OverlayMargin)
        self._diagram._canvas.refreshExtent(extent)
        self.adjustLinks(dc)

    def getPortsInfo(self):
        result = []
        for port in list(self._ports.values()):
            result.append([port.id(), port.type(), directionStr(port.direction()), port.sign()])
        return result

    def establishPortsConnections(self, initialEntity):
        result = []
        for port in list(self._ports.values()):
            connections = []
            port.establishConnections(initialEntity, connections, port)
            # Get other ports connected to this
            connections = list(set(connections)) # removes duplicates (shouldn't happen)
            if initialEntity.category() != "display": # For a display can stop at the first port
                portId = port.objectId()
                for otherPortId in connections:
                    otherPort = self._diagram.findObject(otherPortId)
                    if otherPort:
                        if otherPort.parent().category() != "display": # Don't track connections through displays
                            otherConnections = []
                            otherPort.establishConnections(initialEntity, otherConnections, otherPort)
                            otherConnections = list(set(otherConnections)) # remove duplicates
                            if portId in otherConnections: otherConnections.remove(portId)
                            if len(otherConnections) > 0:
                                connections = list(set(connections).union(set(otherConnections))) # merge
            result.append([port.objectId(), connections])
        return result

    def save(self, indent = None, level = 0, saveDefaults=False, includeZOrder=False):
        result = ''
        nl = '\n'
        ind = ''
        if indent is not None:
            for i in range(level): ind += indent
            ind2 = ind + indent
        else:
            nl = ''
            ind2 = ''
        result = ind + result
        result += ('<' + self._category + ' id="' + str(self.objectId()) + '" type="' + self._type + '"')
        result += self.savePositioning(saveDefaults, includeZOrder=includeZOrder)

        portsContents = ''
        for port in list(self._ports.values()):
            portsContents += port.save(indent, level + 2, saveDefaults, self._dynamic_ports, fullObjectId=False)
        hasContents = saveDefaults or len(self._annotations) > 0 or portsContents or self._dynamic_ports
        if hasContents:
            result += '>' +nl
        else:
            result += '/>' + nl
        if self._dynamic_ports:
            result += ind2
            result += '<ports>' + nl
            result += portsContents
            result += ind2
            result += '</ports>' + nl
        elif portsContents:
            result += portsContents
        for annotation in list(self._annotations.values()):
            result += annotation.save(indent, level + 1, saveDefaults)
        if hasContents:
            result += ind + '</' + self._category + '>' + nl
        return result
