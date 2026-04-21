#! /usr/bin/python

import sys
import os
import re

import wx

from . import fontwork as Fntwrk
from . import colournames as Colours

from .transform import StraightOrientations, Transform, reorientatePoint
from .object import Object
from .objectxml import setObjectProperties

ElementTypes = [ "rect", "ellipse", "line", "text", "image", "polyline", "polygon", "spline" ]

DefaultObjects = {}

def hitLine(pos, pt1, pt2, margin, lineDraw="straight"):
    result = False
    x1 = pt1.x
    y1 = pt1.y
    x2 = pt2.x
    y2 = pt2.y
    x = pos.x
    y = pos.y
    # see if in box
    if (x > min(x1, x2) - margin and
        y > min(y1, y2) - margin and
        x < max(x1, x2) + margin and
        y < max(y1, y2) + margin):
        # see if line is horizontal or vertical
        if abs(x1 - x2) <= margin or abs(y1 - y2) <= margin:
            result = True
        else:
            if lineDraw == "long":
                if abs(x2-x1) > abs(y2-y1):
                    lineDraw = "xy"
                else:
                    lineDraw = "yx"
            elif lineDraw == "short":
                if abs(x2-x1) > abs(y2-y1):
                    lineDraw = "yx"
                else:
                    lineDraw = "xy"
            if lineDraw == "xy":
                if abs(y - y1) <= margin or abs(x - x2) <= margin:
                    result = True
            elif lineDraw == "yx":
                if abs(x - x1) <= margin or abs(y - y2) <= margin:
                    result = True
            elif lineDraw == "xyx":
                midX = (x1 + x2)//2
                if ((x < max(x1, midX) + margin and abs(y - y1) <= margin) or
                    (abs(x - midX) <= margin) or
                    (x > min(x2, midX) + margin and abs(y - y2) <= margin)):
                    result = True
            elif lineDraw == "yxy":
                midY = (y1 + y2)//2
                if ((y < max(y1, midY) + margin and abs(x - x1) <= margin) or
                    (abs(y - midY) <= margin) or
                    (y > min(y2, midY) + margin and abs(x - x2) <= margin)):
                    result = True
            else:  # straight or anything else
                # see how close to line
                # Calculate the gradient m.
                m = float(y2 - y1) / float(x2 - x1)

                # Using y=mx+c
                # then  y1=m * x1+c
                # so    c = y1 - m * x1
                c = float(y1) - m * float(x1)
                # Equation of a line is Ax+By+C=0
                # The distance to the line d =  |Ax+By+C|
                #                               ------------
                #                               sqrt(A2+B2)
                # Using y=mx+c, then A=m, B=-1, C=c
                # So, d =  |mx-y+c|
                #         -----------
                #          sqrt(m2+1)
                #
                # And d2 = (mx-y+c)2
                #          ---------
                #            m2+1
                #
                temp = (m * float(x) - float(y) + c)
                d2 = temp * temp / (m * m + 1)

                # Check if d2 is within the margin.
                if (d2 <= margin * margin):
                    result = True
    return result

def getClosestPtOnLine(pos, pt1, pt2, margin, lineDraw="straight"):
    onLinePt = None
    x1 = pt1.x
    y1 = pt1.y
    x2 = pt2.x
    y2 = pt2.y
    x = pos.x
    y = pos.y
    # see if in box
    gotThePoint = False
    if (x > min(x1, x2) - margin and
        y > min(y1, y2) - margin and
        x < max(x1, x2) + margin and
        y < max(y1, y2) + margin):
        gotThePoint = True
        # see if line is horizontal or vertical
        if abs(x1 - x2) <= margin:
            x = x1
        elif abs(y1 - y2) <= margin:
            y = y1
        else:
            if lineDraw == "long":
                if abs(x2-x1) > abs(y2-y1):
                    lineDraw = "xy"
                else:
                    lineDraw = "yx"
            elif lineDraw == "short":
                if abs(x2-x1) > abs(y2-y1):
                    lineDraw = "yx"
                else:
                    lineDraw = "xy"
            if lineDraw == "xy":
                if abs(y - y1) <= abs(x - x2):
                    y = y1
                else:
                    x = x2
            elif lineDraw == "yx":
                if abs(x - x1) <= abs(y - y2):
                    x = x1
                else:
                    y = y2
            elif lineDraw == "xyx":
                midX = (x1 + x2)//2
                if abs(y - y1) <= abs(x - midX):
                    y = y1
                if abs(y - y2) <= abs(x - midX):
                    y = y2
                else:
                    x = midX
            elif lineDraw == "yxy":
                midY = (y1 + y2)//2
                if abs(x - x1) <= abs(y - midY):
                    x = x1
                if abs(x - x2) <= abs(y - midY):
                    x = x2
                else:
                    y = midY
            else:  # straight or anything else
                m = float(y2 - y1) / float(x2 - x1)
                c = float(y1) - m * float(x1)
                mp = -1 / m
                k = float(y) - mp * float(x)
                x = (c - k)/(mp - m)
                y = round(m*float(x)+c)
                x = round(x)
        if gotThePoint:
            onLinePt = wx.Point(x, y)
    return onLinePt

def getPoints(xmlElement):
    points = []
    pointsstr = xmlElement.getAttribute("points")
    if pointsstr:
        pointsstr = pointsstr.replace(',', ' ')
        pointsstrlist = pointsstr.split() # each coord
        n = len(pointsstrlist) // 2
        for i in range(n):
            x = int(pointsstrlist[2 * i])
            y = int(pointsstrlist[2 * i + 1])
            points.append(wx.Point(x, y))
    return points

def pointsStr(pointlist):
    result = ' points="'
    first = True
    for pt in pointlist:
        if not first: result += ' '
        result += str(pt.x) + ',' + str(pt.y)
        first = False
    result += '"'
    return result

class Element(Object):

    def __init__(self, type, diagram, position=None, orientation=None, descr=None, altDefn=None):
        Object.__init__(self, diagram, position, orientation)
        self._category = "element"
        self._type = type
        if altDefn:
            self._defn = altDefn
        else:
            self._defn = self._diagram.registry().get(self._category, self._type)
        self._descr = descr
        if self._type == "text" or self._type == "image":
            self._orientable = False
            self._scalable = False
        self.setDefaults()
        if self._defn: self.setShape(self._defn)
        if self._descr: self.setShape(self._descr)
        self.clearGrabDragInfo()

    def __str__(self):
        result = "<" + self._category + "-" + str(self.objectId()) + "(" + self._type + ")@" + str(self.position())
        if self._type in ["rect", "ellipse"]:
            result += ":"+str(self._size.width)+"x"+str(self._size.height)
        result += ">"
        return result

    def justify(self):
        result = ""
        if self._type == "text":
            result = self._justify
        return result

    def setJustify(self, justify):
        if self._type == "text":
            self._justify = justify

    def update(self, updateDescr, deleteList):
        self._descr = updateDescr
        #self.setDefaults()
        if self._descr: self.setShape(self._descr)

    def setDefaults(self):
        #self._pen = wx.Pen(wx.BLACK, 1, wx.PENSTYLE_SOLID) #BlackForegroundPen
        #col = wx.Colour(255, 0, 0, 0) #alpha not used (windows)
        #self._brush = wx.Brush(col, wx.BRUSHTYLE_SOLID) #wx.WHITE_BRUSH
        #self._font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) #NormalFont
        #self._textColour = wx.BLACK
        self._pen = None
        self._brush = None
        self._stroke = "black"
        self._strokewidth = 1
        self._strokestyle = "solid"
        self._fill = "black"
        if self._type == "rect":
            self._size = wx.Size(50, 50)
            self._corner = 0
        elif self._type == "ellipse":
            self._size = wx.Size(50, 50)
        elif self._type == "line":
            self._extension = wx.Point(0, 0)
            self._lineDraw = "straight"
        elif self._type == "text":
            self._font = None
            self._justify = "centre"
            self._text = ""
        elif self._type == "image":
            self._bitmap = None
            self._imagefile = ""
            self._size = wx.Size(1, 1)
        elif self._type in ["polyline", "polygon", "spline"]:
            self._points = [wx.Point(0, -10), wx.Point(10, 0), wx.Point(0, 10)]

    def setShape(self, xmlElement):
        setObjectProperties(self, xmlElement)
        # pen stroke colour & width for shape border/line
        if self._type in [ "rect", "ellipse", "line", "polyline", "polygon", "spline" ]:
            if xmlElement:
                stroke = xmlElement.getAttribute("stroke")
                if stroke: self._stroke = stroke
            if xmlElement:
                strokewidth = xmlElement.getAttribute("stroke-width")
                if strokewidth: self._strokewidth = strokewidth
                strokestyle = xmlElement.getAttribute("stroke-style")
                if strokestyle: self._strokestyle = strokestyle
            if self._stroke != "none" and int(self._strokewidth) != 0:
                penstyle = penStyle(self._strokestyle)
                self._pen = wx.Pen(Colours.get(self._stroke), int(self._strokewidth), penstyle)
            else:
                self._pen = wx.TRANSPARENT_PEN
        # brush fill colour for shape, also for text
        if self._type in [ "rect", "ellipse", "text", "polygon" ]:
            if xmlElement:
                fill = xmlElement.getAttribute("fill")
                if fill: self._fill = fill
            if self._fill != "none":
                colour = Colours.get(self._fill)
                if colour:
                    self._brush = wx.Brush(Colours.get(self._fill), wx.BRUSHSTYLE_SOLID)
                else:
                    self._brush = wx.TRANSPARENT_BRUSH
            else:
                self._brush = wx.TRANSPARENT_BRUSH
        # size for shape
        if self._type in [ "rect", "ellipse" ]:
            width = self._size.width
            height = self._size.height
            if xmlElement:
                value = xmlElement.getAttribute("width")
                if value: width = value
                value = xmlElement.getAttribute("height")
                if value: height = value
                self._size = wx.Size(int(width), int(height))
        # corner for rect
        if self._type == "rect":
            if xmlElement:
                corner = xmlElement.getAttribute("corner")
                if corner == "": corner = "0"
                if corner: self._corner = int(corner)
        # extension for line
        if self._type == "line":
            x2 = self._extension.x
            y2 = self._extension.y
            if xmlElement:
                value = xmlElement.getAttribute("x2")
                if value: x2 = value
                value = xmlElement.getAttribute("y2")
                if value: y2 = value
                self._extension = wx.Point(int(x2), int(y2))
                value = xmlElement.getAttribute("draw")
                if value: self._lineDraw = value
        # imagefile (src) for image
        if self._type == "image":
            if xmlElement:
                imagefile = xmlElement.getAttribute("src")
                self.setImage(imagefile)
        # text for text - also justify
        if self._type == "text":
            if xmlElement:
                text = xmlElement.getContent()
                if text:
                    text = text.strip()
                self._text = text
                value = xmlElement.getAttribute("justify")
                if value:
                    if value == "center": value = "centre"
                    self._justify = value
        # + font for text
        if self._type == "text":
            fnt = Fntwrk.getFont(xmlElement, self._font)
            if fnt:
                self._font = fnt
            if not self._font:
                self._font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        # points for
        if self._type in ["polyline", "polygon", "spline"]:
            if xmlElement:
                pts = getPoints(xmlElement)
                if pts: self._points = pts

    def setLineDraw(self, lineDraw):
        if lineDraw == "default": lineDraw = "straight"
        self._lineDraw = lineDraw

    def setExtension(self, x, y):
        self._extension.x = x
        self._extension.y = y

    def drawObject(self, dc, transform=None):
        if self._pen is not None: dc.SetPen(self._pen)
        if self._brush is not None: dc.SetBrush(self._brush)
        posn, orientation, size = self.getDiagramPositioning(transform)
        if self._type == "rect":
            hw = round(size.width / 2)
            hh = round(size.height / 2)
            x1 = posn.x - hw
            y1 = posn.y - hh
            if self._corner:
                corner = self._corner
                if transform:
                    if orientation in StraightOrientations:
                        if size.height > size.width:
                            corner = corner * transform.scale.x # we pick the scale width to scale the corner by
                        else:
                            corner = corner * transform.scale.y  # we pick the scale height to scale the corner by
                    else:
                        if size.height > size.width:
                            corner = corner * transform.scale.y  # we pick the scale height to scale the corner by
                        else:
                            corner = corner * transform.scale.x  # we pick the scale width to scale the corner by
                dc.DrawRoundedRectangle(x1, y1, size.width, size.height, corner)
            else:
                dc.DrawRectangle(x1, y1, size.width, size.height)
        elif self._type == "ellipse":
            hw = round(size.width / 2)
            hh = round(size.height / 2)
            x1 = posn.x - hw
            y1 = posn.y - hh
            dc.DrawEllipse(x1, y1, size.width, size.height)
        elif self._type == "line":
            x1 = posn.x
            y1 = posn.y
            extn = self._extension
            end = wx.RealPoint(self._position) + wx.RealPoint(extn)
            end = self.getDiagramPoint(end, transform)
            lineDraw = self._lineDraw
            if lineDraw == "long":
                if abs(self._extension.x) > abs(self._extension.y):
                    lineDraw = "xy"
                else:
                    lineDraw = "yx"
            if lineDraw == "short":
                if abs(self._extension.x) > abs(self._extension.y):
                    lineDraw = "yx"
                else:
                    lineDraw = "xy"
            if lineDraw == "xy":
                dc.DrawLine(x1, y1, end.x, y1)
                dc.DrawLine(end.x, y1, end.x, end.y)
            elif lineDraw == "yx":
                dc.DrawLine(x1, y1, x1, end.y)
                dc.DrawLine(x1, end.y, end.x, end.y)
            elif lineDraw == "xyx":
                midX = (x1 + end.x)//2
                dc.DrawLine(x1, y1, midX, y1)
                dc.DrawLine(midX, y1, midX, end.y)
                dc.DrawLine(midX, end.y, end.x, end.y)
            elif lineDraw == "yxy":
                midY = (y1 + end.y) // 2
                dc.DrawLine(x1, y1, x1, midY)
                dc.DrawLine(x1, midY, end.x, midY)
                dc.DrawLine(end.x, midY, end.x, end.y)
            else: #straight or anything else
                dc.DrawLine(x1, y1, end.x, end.y)
        elif self._type == "text":
            dc.SetTextForeground(self._fill)
            dc.SetFont(self._font)
            text = unescapeText(self._text)
            size = dc.GetMultiLineTextExtent(text)
            x1 = round(posn.x - size[0] / 2) # default for justify = centre
            y1 = round(posn.y - size[1] / 2)
            if self._justify == "left":
                x1 = posn.x
            elif self._justify == "right":
                x1 = posn.x - size[0]
            dc.DrawText(text, x1, y1)
        elif self._type == "image":
            if self._bitmap is not None:
                x1 = round(posn.x - self._size.width / 2)
                y1 = round(posn.y - self._size.height / 2)
                dc.DrawBitmap(self._bitmap, x1, y1, True)
        elif self._type in ["polyline", "polygon", "spline"]:
            pts = []
            for pt in self._points:
                pt = wx.Point(reorientatePoint(pt, self._orientation))
                pt = self.getDiagramPoint(wx.RealPoint(self._position) + wx.RealPoint(pt), transform)
                pts.append(pt)
            if self._type == "polyline":
                dc.DrawLines(pts)
            elif self._type == "polygon":
                dc.DrawPolygon(pts)
            elif self._type == "spline":
                dc.DrawSpline(pts)

    def setGrabPos(self, type, grabIx, pos):
        if len(self._grabs) > grabIx:
            grab = self._grabs[grabIx]
            grab._position = pos
        else: # we assume grabIx increments each time
            grab, errorMsg = self._diagram.makeGrab(type, pos, self, None)
            if not errorMsg:
                self._grabs.append(grab)
        return grab

    def setGrabs(self):
        if self._type == "rect" or self._type == "ellipse":
            extnt = self.extent() # this has been transformed to diagram coords
            pos = wx.Point(extnt.x, extnt.y)  # top left (on diagram)
            self.setGrabPos("element", 0, pos)
            pos = wx.Point(extnt.x + extnt.width, extnt.y)  # top right
            self.setGrabPos("element", 1, pos)
            pos = wx.Point(extnt.x + extnt.width, extnt.y + extnt.height)  # bottom right
            self.setGrabPos("element", 2, pos)
            pos = wx.Point(extnt.x, extnt.y + extnt.height)  # bottom left
            self.setGrabPos("element", 3, pos)
            pass
        else:
            transform = self.getTransform()
            if self._type == "line":
                pos = self.getDiagramPoint(self._position, transform)
                self.setGrabPos("line", 0, pos)
                extn = wx.Point(reorientatePoint(self._extension, self._orientation))
                end = wx.RealPoint(self._position) + wx.RealPoint(extn)
                end = self.getDiagramPoint(end, transform)
                self.setGrabPos("line", 1, end)
            elif self._type in ["polyline", "polygon", "spline"]:
                ix = 0
                for pt in self._points:
                    pt = wx.Point(reorientatePoint(pt, self._orientation))
                    pt = self.getDiagramPoint(wx.RealPoint(self._position) + wx.RealPoint(pt), transform)
                    self.setGrabPos("element", ix, pt)
                    ix += 1
        pass

    def clearGrabDragInfo(self):
        # element grab drag info
        self._grabDrag = None
        self._grabDragIndex = -1
        self._grabDragTransform = None
        # for rect ellipse
        self._grabDragOrigDiagramSizePoint = None
        self._grabDragStartDragPosns = []
        # for line
        self._grabDragOrigPosn = None
        # for polyline polygon spline
        self._grabDragOrigPosn = None
        self._grabDragOrigPoints = []

    def startGrabDragging(self, grab):
        self._grabDrag = grab
        self._grabDragIndex = -1
        for i in range(len(self._grabs)):
            if self._grabDrag == self._grabs[i]:
                self._grabDragIndex = i
                break
        self._grabDragTransform = self.getTransform()
        if self._grabDragTransform is None:
            self._grabDragTransform = Transform()
        else:
            self._grabDragTransform.position.x = 0
            self._grabDragTransform.position.y = 0
        if self._type == "rect" or self._type == "ellipse":
            self._grabDragOrigDiagramSizePoint = self._grabDragTransform.backTransformPoint(wx.Point(self._size.width, self._size.height), self)
            self._grabDragStartDragPosns = []
            for g in self._grabs:
                self._grabDragStartDragPosns.append(wx.RealPoint(g._position))
        elif self._type == "line":
            self._grabDragOrigPosn = wx.RealPoint(self._position)
            self._grabDragOrigExtension = wx.RealPoint(self._extension)
        elif self._type in ["polyline", "polygon", "spline"]:
            self._grabDragOrigPosn = wx.RealPoint(self._position)
            self._grabDragOrigPoints = []
            for pt in self._points:
                self._grabDragOrigPoints.append(wx.RealPoint(pt))

    def stopGrabDragging(self):
        self.clearGrabDragInfo()
        # for rect ellipse - in case grabs were dragged over
        if self._type == "rect" or self._type == "ellipse":
            self._size.width = abs(self._size.width)
            self._size.height = abs(self._size.height)
            self.setGrabs() # recreate the grabs so order on diagram is as expected

    def grabDragBy(self, dragDisplacement):
        if dragDisplacement.x != 0 or dragDisplacement.y != 0:
            displaced = self._grabDragTransform.transformPoint(dragDisplacement, self)

            if self._type == "rect" or self._type == "ellipse":
                if len(self._grabs) == 4:
                    diagramWidth = abs(self._grabDragOrigDiagramSizePoint.x)
                    diagramHeight = abs(self._grabDragOrigDiagramSizePoint.y)
                    if self._grabDragIndex == 0:  # top-left (on diagram)
                        diagramWidth -= 2*dragDisplacement.x
                        diagramHeight -= 2*dragDisplacement.y
                    elif self._grabDragIndex == 1:  # top-right
                        diagramWidth += 2*dragDisplacement.x
                        diagramHeight -= 2*dragDisplacement.y
                    elif self._grabDragIndex == 2:  # bottom-right
                        diagramWidth += 2*dragDisplacement.x
                        diagramHeight += 2*dragDisplacement.y
                    elif self._grabDragIndex == 3:  # bottom-left
                        diagramWidth -= 2*dragDisplacement.x
                        diagramHeight += 2*dragDisplacement.y

                    sizePoint = self._grabDragTransform.transformPoint(wx.RealPoint(diagramWidth, diagramHeight), self)
                    self._size.width = round(sizePoint.x)
                    self._size.height = round(sizePoint.y)

                    #move other grabs
                    if self._grabDragIndex == 0:  # top-left (on diagram)
                        #self._grabs[0]._position
                        self._grabs[1]._position = wx.Point(round(self._grabDragStartDragPosns[1].x - dragDisplacement.x),
                                                            round(self._grabDragStartDragPosns[1].y + dragDisplacement.y))
                        self._grabs[2]._position = wx.Point(round(self._grabDragStartDragPosns[2].x - dragDisplacement.x),
                                                            round(self._grabDragStartDragPosns[2].y - dragDisplacement.y))
                        self._grabs[3]._position = wx.Point(round(self._grabDragStartDragPosns[3].x + dragDisplacement.x),
                                                            round(self._grabDragStartDragPosns[3].y - dragDisplacement.y))
                    elif self._grabDragIndex == 1:  # top-right
                        self._grabs[0]._position = wx.Point(round(self._grabDragStartDragPosns[0].x - dragDisplacement.x),
                                                            round(self._grabDragStartDragPosns[0].y + dragDisplacement.y))
                        #self._grabs[1]._position
                        self._grabs[2]._position = wx.Point(round(self._grabDragStartDragPosns[2].x + dragDisplacement.x),
                                                            round(self._grabDragStartDragPosns[2].y - dragDisplacement.y))
                        self._grabs[3]._position = wx.Point(round(self._grabDragStartDragPosns[3].x - dragDisplacement.x),
                                                            round(self._grabDragStartDragPosns[3].y - dragDisplacement.y))
                    elif self._grabDragIndex == 2:  # bottom-right
                        self._grabs[0]._position = wx.Point(round(self._grabDragStartDragPosns[0].x - dragDisplacement.x),
                                                            round(self._grabDragStartDragPosns[0].y - dragDisplacement.y))
                        self._grabs[1]._position = wx.Point(round(self._grabDragStartDragPosns[1].x + dragDisplacement.x),
                                                            round(self._grabDragStartDragPosns[1].y - dragDisplacement.y))
                        #self._grabs[2]._position
                        self._grabs[3]._position = wx.Point(round(self._grabDragStartDragPosns[3].x - dragDisplacement.x),
                                                            round(self._grabDragStartDragPosns[3].y + dragDisplacement.y))
                    elif self._grabDragIndex == 3:  # bottom-left
                        self._grabs[0]._position = wx.Point(round(self._grabDragStartDragPosns[0].x + dragDisplacement.x),
                                                            round(self._grabDragStartDragPosns[0].y - dragDisplacement.y))
                        self._grabs[1]._position = wx.Point(round(self._grabDragStartDragPosns[1].x - dragDisplacement.x),
                                                            round(self._grabDragStartDragPosns[1].y - dragDisplacement.y))
                        self._grabs[2]._position = wx.Point(round(self._grabDragStartDragPosns[2].x - dragDisplacement.x),
                                                            round(self._grabDragStartDragPosns[2].y + dragDisplacement.y))
                        #self._grabs[3]._position
                pass
            elif self._type == "line":
                if len(self._grabs) == 2:
                    if self._grabDragIndex == 0: # origin
                        self._position = wx.Point(self._grabDragOrigPosn + displaced)
                        self._extension = wx.Point(self._grabDragOrigExtension - displaced)
                        pass
                    else: # extension
                        self._extension = wx.Point(self._grabDragOrigExtension + displaced)
            elif self._type in ["polyline", "polygon", "spline"]:
                if len(self._grabs) == len(self._points):
                    if self._grabDragIndex != 0:
                        self._points[self._grabDragIndex] = wx.Point(self._grabDragOrigPoints[self._grabDragIndex] + displaced)
                    else:
                        self._position = wx.Point(self._grabDragOrigPosn + displaced)
                        for i in range(1, len(self._points)):
                            self._points[i] = wx.Point(self._grabDragOrigPoints[i] - displaced)

    def extent(self, includeInvisible=False):
        result = None
        if includeInvisible or self._visible:
            if self._type in ["line", "text", "polyline", "polygon", "spline"]:
                transform = self.getTransform()
                posn = self.getDiagramPoint(self._position, transform)
                if self._type == "line":
                    extn = wx.Point(self._extension)
                    end = wx.RealPoint(self._position) + wx.RealPoint(extn)
                    end = self.getDiagramPoint(end, transform)
                    x = posn.x
                    if end.x < x: x = end.x
                    y = posn.y
                    if end.y < y: y = end.y
                    w = max(int(self._strokewidth)+1, abs(end.x - posn.x))
                    h = max(int(self._strokewidth)+1, abs(end.y - posn.y))
                    result = wx.Rect(x, y, w, h)
                elif self._type == "text":
                    dc = wx.ClientDC(self._diagram._canvas)
                    self._diagram._canvas.PrepareDC(dc)
                    dc.SetUserScale(self._diagram._canvas._scale, self._diagram._canvas._scale)
                    dc.SetFont(self._font)
                    text = unescapeText(self._text)
                    size = dc.GetMultiLineTextExtent(text)
                    # default for justify = centre
                    w = 2 * round(size[0] / 2)
                    h = 2 * round(size[1] / 2)
                    x = posn.x - int(w / 2)
                    y = posn.y - int(h / 2)
                    x1 = round(posn.x - size[0] / 2)
                    y1 = round(posn.y - size[1] / 2)
                    if self._justify == "left":
                        w = size[0]
                        x = posn.x
                    elif self._justify == "right":
                        w = size[0]
                        x = posn.x - w
                    result = wx.Rect(x, y, w, h)
                elif self._type in ["polyline", "polygon", "spline"]:
                    xmin = None
                    for pt in self._points:
                        #pt = wx.Point(reorientatePoint(pt, self._orientation))
                        pt = self.getDiagramPoint(wx.RealPoint(self._position) + wx.RealPoint(pt), transform)
                        if xmin is None:
                            xmin = pt.x
                            ymin = pt.y
                            xmax = xmin + 1
                            ymax = ymin + 1
                        else:
                            xmin = min(xmin, pt.x)
                            ymin = min(ymin, pt.y)
                            xmax = max(xmax, pt.x)
                            ymax = max(ymax, pt.y)
                    result = wx.Rect(xmin, ymin, xmax - xmin, ymax - ymin)
            elif self._size:
                x1 = round(self._position.x - round(self._size.width / 2))
                y1 = round(self._position.y - round(self._size.height / 2))
                x2 = round(self._position.x + round(self._size.width / 2))
                y2 = round(self._position.y + round(self._size.height / 2))
                topLeft = wx.RealPoint(x1, y1)
                bottomRight = wx.RealPoint(x2, y2)
                topLeft = self.getDiagramPoint(topLeft)
                bottomRight = self.getDiagramPoint(bottomRight)
                result = wx.Rect(topLeft, bottomRight)
        return result

    def getSize(self, transform=None):
        # TODO use transform
        posn = self.position()
        sizeRect = wx.Rect(posn.x, posn.y, 1, 1)
        if self._type in ["rect", "ellipse"]:
            sizeRect.width = self._size.width
            sizeRect.height = self._size.height
            sizeRect.x = round(posn.x - self._size.width/2)
            sizeRect.y = round(posn.y -self._size.height/2)
        elif self._type == "line":
            sizeRect.width = abs(self._extension.x)
            sizeRect.height = abs(self._extension.y)
            if sizeRect.width == 0: sizeRect.width = 1
            if sizeRect.height == 0: sizeRect.height = 1
            if self._extension.x < 0:
                sizeRect.x = posn.x + self._extension.x
            if self._extension.y < 0:
                sizeRect.y = posn.y + self._extension.y
        return sizeRect

    def getClosestPtOnLine(self, pt):
        onLinePt = None
        if self._type == "line":
            margin = float(self._pen.GetWidth() / 2) + 2
            transform = self.getTransform()
            posn = self.getDiagramPoint(self._position, transform)
            end = wx.RealPoint(self._position) + wx.RealPoint(self._extension)
            end = self.getDiagramPoint(end, transform)
            onLinePt = getClosestPtOnLine(pt, posn, end, margin, self._lineDraw)
        return onLinePt

    def endAlignment(self):
        alignment = None
        if self._type == "line":
            transform = self.getTransform()
            posn = self.getDiagramPoint(self._position, transform)
            end = wx.RealPoint(self._position) + wx.RealPoint(self._extension)
            end = self.getDiagramPoint(end, transform)
            ###
            xdiff = end.x - posn.x
            ydiff = end.y - posn.y
            if self._lineDraw == "long":
                if xdiff >= ydiff:
                    alignment = "horizontal"
                else:
                    alignment = "vertical"
            elif self._lineDraw == "short":
                if xdiff <= ydiff:
                    alignment = "horizontal"
                else:
                    alignment = "vertical"
            elif self._lineDraw == "xy" or self._lineDraw == "xyx":
                alignment = "vertical"
            elif self._lineDraw == "yx" or self._lineDraw == "yxy":
                alignment = "horizontal"
            else:  # straight or anything else
                alignment = None
            ###
        return alignment

    def HitTest(self, pos):
        result = None
        if self._visible:
            result = Object.HitTest(self, pos)
            if result is not None:
                transform = self.getTransform()
                posn = self.getDiagramPoint(self._position, transform)
                if self._type == "line":
                    result = None
                    margin = float(self._pen.GetWidth() / 2) + 2
                    extn = wx.Point(reorientatePoint(self._extension, self._orientation))
                    end = wx.RealPoint(self._position) + wx.RealPoint(extn)
                    end = self.getDiagramPoint(end, transform)
                    hitIt = hitLine(pos, posn, end, margin, self._lineDraw)
                    if hitIt:
                        result = self
                elif self._type == "polyline":
                    result = None
                    n = len(self._points)
                    if n > 1:
                        margin = float(self._pen.GetWidth() / 2) + 2
                        for i in range(n - 1):
                            pt0 = wx.Point(reorientatePoint(self._points[i], self._orientation))
                            pt0 = self.getDiagramPoint(wx.RealPoint(self._position) + wx.RealPoint(pt0), transform)
                            pt1 = wx.Point(reorientatePoint(self._points[i + 1], self._orientation))
                            pt1 = self.getDiagramPoint(wx.RealPoint(self._position) + wx.RealPoint(pt1), transform)
                            hitIt = hitLine(pos, pt0, pt1, margin)
                            if hitIt:
                                result = self
                                break
                #else: # incl spline as general object (hit by extent)
        return result

    def setImage(self, imagefile):
        if imagefile is None:
            imagefile = ""
        if not self._bitmap or imagefile != self._imagefile:
            self._bitmap = None
            if imagefile and not os.path.splitext(imagefile)[1]:
                imagefile += '.png'
            self._imagefile = imagefile  # keep/save as given
            if imagefile:
                filepath = disEnvVarPath(imagefile) # absolute, relative or with expanded env-var
                if os.path.exists(filepath):
                    self._image = wx.Image(filepath)
                    if self._image is not None and self._image.IsOk():
                        self._bitmap = wx.Bitmap(self._image)
                        self._size = self._bitmap.GetSize()
            if not self._bitmap:
                self._bitmap = wx.ArtProvider.GetBitmap(wx.ART_ERROR)
                self._size = self._bitmap.GetSize()
                if imagefile:
                    msg = 'Cannot find image file "' + imagefile + '"'
                    self._diagram._canvas.raiseCanvasApplicationNotifyEvent('', "display", msg)

    def getPoints(self):
        return self._points

    def setPoints(self, points):
        self._points = points

    def setScale(self, scale): # overrides for elements that doesnt change the
        result = False
        if self.isScalable():
            if scale and (scale.x != 1.0 or scale.y != 1.0):
                if self._type in ["rect", "ellipse"]:
                    width = self._size.width
                    height = self._size.height
                    self._size = wx.Size(round(width*scale.x), round(height*scale.y))
                    pass

                elif self._type == "line":
                    extension = wx.Point(round(self._extension.x*scale.x), round(self._extension.y*scale.y))
                    self._extension = extension
                    pass

                # text & image don't scale

                elif self._type in ["polyline", "polygon", "spline"]:
                    pts = []
                    for pt in self._points:
                        pt = wx.Point(round(pt.x*scale.x), round(pt.y*scale.y))
                        pts.append(pt)
                    self._points = pts
                    pass
            result = True
        return result

    def setOrientation(self, orientation):
        result = False
        if self.isOrientable():
            if self._type in ["rect", "ellipse"]:
                if orientation not in StraightOrientations:
                    width = self._size.height
                    height = self._size.width
                    self._size = wx.Size(int(width), int(height))
                pass

            elif self._type == "line":
                extension = wx.Point(reorientatePoint(self._extension, orientation))
                self._extension = extension
                pass

            # text & image don't orient

            elif self._type in ["polyline", "polygon", "spline"]:
                pts = []
                for pt in self._points:
                    pt = wx.Point(reorientatePoint(pt, orientation))
                    pts.append(pt)
                self._points = pts
                pass
            result = True
        return result

    def save(self, indent=None, level=0, saveDefaults=False, defaultObject=None, includeZOrder=False):
        result = ''
        nl = '\n'
        ind = ''
        if indent is not None:
            for i in range(level): ind += indent
        else:
            nl = ''
        result = ind + result
        if not saveDefaults and not defaultObject:
            defaultObject = DefaultObjects.get(self._defn)
            if not defaultObject:
                defaultObject = Element(self._type, self._diagram, None, None, None, self._defn)
                if defaultObject:
                    defaultObject.setDefaults()
                    defaultObject.setShape(self._defn)
                    if self._defn:
                        DefaultObjects[self._defn] = defaultObject
        posn = self.position()
        result += '<' + self._type
        result += ' id="' + str(self.objectId()) + '"'
        if defaultObject:
            defaultPosn = defaultObject.position()
        if (saveDefaults or not defaultObject or posn.x != defaultPosn.x
                or posn.y != defaultPosn.y):
            result += ' x="' + str(posn.x) + '" y="' + str(posn.y) + '"'
        if includeZOrder:
            zOrder = self.getZOrder()
            if zOrder > 0:
                result += ' z-order="' + str(zOrder) + '"'
        orientation = self.getOrientation()
        if saveDefaults or not defaultObject or orientation != defaultObject.getOrientation():
            result += ' orientation="' + str(orientation) + '"'
        selectable = self.selectable()
        if saveDefaults or (not defaultObject and not selectable) or (defaultObject and selectable != defaultObject.selectable()):
            result += ' select="' + ("true" if selectable else "false") + '"'
        draggable = self.draggable()
        if saveDefaults or (not defaultObject and not draggable) or (defaultObject and draggable != defaultObject.draggable()):
                result += ' drag="' + ("true" if draggable else "false") + '"'
        orientable = self.orientable()
        if saveDefaults or (not defaultObject and not orientable) or (defaultObject and orientable != defaultObject.orientable()):
            result += ' orient="' + ("true" if orientable else "false") + '"'
        scalable = self.scalable()
        if saveDefaults or (not defaultObject and not scalable) or (defaultObject and scalable != defaultObject.scalable()):
            result += ' scalable="' + ("true" if scalable else "false") + '"'
        grabbable = self.grabbable()
        if saveDefaults or (not defaultObject and not grabbable) or (defaultObject and grabbable != defaultObject.grabbable()):
            result += ' grabbable="' + ("true" if grabbable else "false") + '"'
        if self._type in [ "rect", "ellipse", "line", "polyline", "polygon", "spline" ]:
            if saveDefaults or not defaultObject or self._stroke != defaultObject._stroke:
                result += ' stroke="' + self._stroke + '"'
            if saveDefaults or not defaultObject or self._strokewidth != defaultObject._strokewidth:
                result += ' stroke-width="' + str(self._strokewidth) + '"'
            if saveDefaults or not defaultObject or self._strokestyle != defaultObject._strokestyle:
                result += ' stroke-style="' + str(self._strokestyle) + '"'
        if self._type in [ "rect", "ellipse", "text", "polygon" ]:
            if saveDefaults or not defaultObject or self._fill != defaultObject._fill:
                result += ' fill="' + self._fill + '"'
        if self._type in [ "rect", "ellipse" ]:
            if (saveDefaults or not defaultObject or self._size.width != defaultObject._size.width
                or self._size.height != defaultObject._size.height):
                    result += ' width="' + str(self._size.width) + '"'
                    result += ' height="' + str(self._size.height) + '"'
        if self._type == "rect":
            if saveDefaults or not defaultObject or self._corner != defaultObject._corner:
                result += ' corner="' + str(self._corner) + '"'
        if self._type == "line":
            if (saveDefaults or not defaultObject or self._extension.x != defaultObject._extension.x
                or self._extension.y != defaultObject._extension.y):
                    result += ' x2="' + str(self._extension.x) + '"'
                    result += ' y2="' + str(self._extension.y) + '"'
            if saveDefaults or not defaultObject or self._lineDraw != "straight":
                result += ' draw="' + self._lineDraw + '"'
        if self._type == "image":
            if saveDefaults or not defaultObject or self._imagefile != defaultObject._imagefile:
                result += ' src="' + self._imagefile + '"'
        if self._type == "text":
            defaultFont = None
            if not saveDefaults and defaultObject:
                defaultFont = defaultObject._font
                if not defaultFont:
                    defaultFont = Fntwrk.getFont(defaultObject._defn, defaultObject._font)
            result += Fntwrk.fontStr(self._font, defaultFont, saveDefaults)
            if saveDefaults or not defaultObject or (self._justify != "centre" and self._justify != "center"):
                result += ' justify="' + self._justify + '"'
        # points for
        if self._type in ["polyline", "polygon", "spline"]:
            if saveDefaults or not defaultObject or self._points != defaultObject._points:
                result += pointsStr(self._points)
        if self._type == "text" and (saveDefaults or not defaultObject or self._text != defaultObject._text):
            result += '><![CDATA[' + self._text + ']]></' + self._type + '>'
        else:
            result += '/>'
        result += nl
        return result

def penStyle(strokestyle):
    result = None
    if not strokestyle or strokestyle == "solid":
        result = wx.PENSTYLE_SOLID
    elif strokestyle == "dot":
        result = wx.PENSTYLE_DOT
    elif strokestyle == "dash":
        result = wx.PENSTYLE_SHORT_DASH
    elif strokestyle == "long-dash":
        result = wx.PENSTYLE_LONG_DASH
    elif strokestyle == "dot-dash":
        result = wx.PENSTYLE_DOT_DASH
    return result

# Looks for a single environment variable at the beginning of a path,
# i.e. for a directory path, and if it finds one it expands the environment
# variable to give a full path and also converts \ to / or / to \ to suit
# the current operating system.
# It accepts the $... or $.../ or $...\ and $(...), and the %...% formats.
# And also ${...}
# This is a cut down copy of what's in esl_studio utils
def disEnvVarPath(filepath):
    newFilepath = filepath
    envstart = 0
    envend = -1
    keepend = False
    quoted = False
    if filepath.startswith('"') and filepath.endswith('"'):
        quoted = True
        filepath = filepath[1:-1]
        newFilepath = filepath
    if filepath.startswith('$('):
        envstart = 2
        envend = filepath.find(')')
    elif filepath.startswith('${'):
        envstart = 2
        envend = filepath.find('}')
    elif filepath.startswith('$'):
        envstart = 1
        envend = filepath.find('/')
        envend2 = filepath.find('\\')
        if envend > 0 and envend2 > 0:
            envend = min(envend, envend2)
            keepend = True
        elif envend < 0 and envend2 < 0:
            envend = len(filepath)
        else:
            envend = max(envend, envend2)
            keepend = True
    elif filepath.startswith('%'):
        envstart = 1
        envend = filepath.find('%', envstart)
    if envend > 0:
        envvar = filepath[envstart:envend]
        envvar_value = os.getenv(envvar)
        if envvar_value:
            if not keepend:
                envend += 1
            newFilepath = envvar_value + filepath[envend:]
    if quoted:
        newFilepath = '"' + newFilepath + '"'
    if sys.platform == 'win32':
        newFilepath = newFilepath.replace('/', '\\')
    else:
        newFilepath = newFilepath.replace('\\', '/')
    return newFilepath

# This is the same as what's in esl_studio utils
def unescapeText(text):
    result = text
    result = re.sub(r"\\\\",  '#back/slash#', result)
    result = re.sub(r'\\n', '\n', result)
    result = re.sub(r"\\r", '\r', result)
    result = re.sub(r"\\t", '\t', result)
    result = result.replace('#back/slash#', '\\')
    return result
