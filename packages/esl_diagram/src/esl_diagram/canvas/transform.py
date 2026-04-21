#! /usr/bin/python

from enum import IntEnum
from typing import Union

import wx

AnyPoint = Union[wx.Point, wx.RealPoint]

# Orientations
# Port direction
class Orientation(IntEnum):
    normal = 0
    rotate90 = 1
    rotate180 = 2
    rotate270 = 3
    mirrorXAxis = 4
    mirrorYAxis = 5
    mirrorUpDiag = 6
    mirrorDownDiag = 7

    def __str__(orientation) -> str:
        result = "?"
        if orientation is not None:
            if orientation == Orientation.normal : result = 'normal'
            elif orientation == Orientation.rotate90 : result = 'rotate90'
            elif orientation == Orientation.rotate180 : result = 'rotate180'
            elif orientation == Orientation.rotate270 : result = 'rotate270'
            elif orientation == Orientation.mirrorXAxis : result = 'mirrorXAxis'
            elif orientation == Orientation.mirrorYAxis : result = 'mirrorYAxis'
            elif orientation == Orientation.mirrorUpDiag : result = 'mirrorUpDiag'
            elif orientation == Orientation.mirrorDownDiag : result = 'mirrorDownDiag'
        return result

class Scale():
    def __init__(self, sync:bool=False, x:float=1.0, y:float=1.0) -> None:
        self.sync:bool = sync # whether scaling in x & y is synchronised (to preserve aspect) or not
        self.x:float = x # i.e. width scaling
        self.y:float = y # i.e. height scaling (when sync then use .x for this (if different)
        if sync and x != y:
            self.y = x

    def __eq__(self, other:'Scale') -> bool:
        result = False
        if self.sync == other.sync:
            if self.sync:
                result = self.x == other.x
            else:
                result = self.x == other.x and self.y == other.y
        return result

    def __str__(self) -> str:
        result = "?"
        if self is not None:
            result = str(self.x)
            if not self.sync:
                result += "," + str(self.y)
        return result

    def copy(self) -> 'Scale':
        result = Scale(self.sync, self.x, self.y)
        return result

    def normalise(self, orientation:Orientation) -> 'Scale':
        result = None
        if orientation in StraightOrientations:
            result = self.copy()
        else:
            result = Scale(self.sync, self.y, self.x)
        return result

    def scalePoint(self, pt:AnyPoint) -> wx.RealPoint:
        x = pt.x * self.x
        y = pt.y * self.y
        newPt = wx.RealPoint(x, y)
        return newPt

    def unscalePoint(self, pt:AnyPoint) -> wx.RealPoint:
        x = pt.x / self.x
        y = pt.y / self.y
        newPt = wx.RealPoint(x, y)
        return newPt

_reorientations = \
[
    [Orientation.normal, Orientation.rotate90, Orientation.rotate180, Orientation.rotate270,
        Orientation.mirrorXAxis, Orientation.mirrorYAxis, Orientation.mirrorUpDiag, Orientation.mirrorDownDiag],
    [Orientation.rotate90, Orientation.rotate180, Orientation.rotate270, Orientation.normal,
        Orientation.mirrorDownDiag, Orientation.mirrorUpDiag, Orientation.mirrorXAxis, Orientation.mirrorYAxis],
    [Orientation.rotate180, Orientation.rotate270, Orientation.normal, Orientation.rotate90,
        Orientation.mirrorYAxis, Orientation.mirrorXAxis, Orientation.mirrorDownDiag, Orientation.mirrorUpDiag],
    [Orientation.rotate270, Orientation.normal, Orientation.rotate90, Orientation.rotate180,
        Orientation.mirrorUpDiag, Orientation.mirrorDownDiag, Orientation.mirrorYAxis, Orientation.mirrorXAxis],
    [Orientation.mirrorXAxis, Orientation.mirrorUpDiag, Orientation.mirrorYAxis, Orientation.mirrorDownDiag,
        Orientation.normal, Orientation.rotate180, Orientation.rotate90, Orientation.rotate270],
    [Orientation.mirrorYAxis, Orientation.mirrorDownDiag, Orientation.mirrorXAxis, Orientation.mirrorUpDiag,
        Orientation.rotate180, Orientation.normal, Orientation.rotate270, Orientation.rotate90],
    [Orientation.mirrorUpDiag, Orientation.mirrorYAxis, Orientation.mirrorDownDiag, Orientation.mirrorXAxis,
        Orientation.rotate270, Orientation.rotate90, Orientation.normal, Orientation.rotate180],
    [Orientation.mirrorDownDiag, Orientation.mirrorXAxis, Orientation.mirrorUpDiag, Orientation.mirrorYAxis,
        Orientation.rotate90, Orientation.rotate270, Orientation.rotate180, Orientation.normal]
]
def doReorientation(oldOrientation:Orientation, newOrientation:Orientation) -> Orientation: # returns orientation as a result of applying a newOrientation on to an oldOrientation
    return _reorientations[oldOrientation][newOrientation]

_oppositeReorientation = \
    [Orientation.normal,
     Orientation.rotate270,
     Orientation.rotate180,
     Orientation.rotate90,
     Orientation.mirrorXAxis,
     Orientation.mirrorYAxis,
     Orientation.mirrorUpDiag,
     Orientation.mirrorDownDiag
     ]
def doOppositeReorientation(orientation:Orientation) -> Orientation: # returns orientation needed to reverse (invert) the given orientation
    return _oppositeReorientation[orientation]

StraightOrientations = [Orientation.normal, Orientation.rotate180, Orientation.mirrorXAxis, Orientation.mirrorYAxis]

# Sides are given in order 0..3
class Side(IntEnum):
    left = 0
    right = 1
    top = 2
    bottom = 3
_sideReorientations = \
[
    [Side.left, Side.right, Side.top, Side.bottom], # Orientation.normal
    [Side.bottom, Side.top, Side.left, Side.right], # Orientation.rotate90
    [Side.right, Side.left, Side.bottom, Side.top], # Orientation.rotate180
    [Side.top, Side.bottom, Side.right, Side.left], # Orientation.rotate270
    [Side.right, Side.left, Side.top, Side.bottom], # Orientation.mirrorXAxis
    [Side.left, Side.right, Side.bottom, Side.top], # Orientation.mirrorYAxis
    [Side.bottom, Side.top, Side.right, Side.left], # Orientation.mirrorUpDiag
    [Side.top, Side.bottom, Side.left, Side.right]  # Orientation.mirrorDownDiag
]
def doSideReorientation(side:Side, orientation:Orientation) -> Side:
    return _sideReorientations[orientation][side]

def reorientatePoint(pt:AnyPoint, orientation:Orientation) -> wx.RealPoint:
    if orientation == Orientation.rotate90: newpt = wx.RealPoint(pt.y, -pt.x)
    elif orientation == Orientation.rotate180: newpt = wx.RealPoint(-pt.x, -pt.y)
    elif orientation == Orientation.rotate270: newpt = wx.RealPoint(-pt.y, pt.x)
    elif orientation == Orientation.mirrorXAxis: newpt = wx.RealPoint(pt.x, -pt.y)
    elif orientation == Orientation.mirrorYAxis: newpt = wx.RealPoint(-pt.x, pt.y)
    elif orientation == Orientation.mirrorUpDiag: newpt = wx.RealPoint(-pt.y, -pt.x)
    elif orientation == Orientation.mirrorDownDiag: newpt = wx.RealPoint(pt.y, pt.x)
    else: newpt = wx.RealPoint(pt.x, pt.y)
    return newpt

def reorientateSize(size:wx.Size, orientation:Orientation) -> wx.Size:
    if (orientation == Orientation.rotate90 or
        orientation == Orientation.rotate270 or
        orientation == Orientation.mirrorUpDiag or
        orientation == Orientation.mirrorDownDiag):
        newsize = wx.Size(size.height, size.width)
    else:
        newsize = wx.Size(size.width, size.height)
    return newsize

def expandRect(rect:wx.Rect, displacement:AnyPoint) -> None:
    if displacement.x > 0: rect.x = round(rect.x - displacement.x)
    rect.width = round(rect.width + abs(displacement.x))
    if displacement.y > 0: rect.y = round(rect.y - displacement.y)
    rect.height = round(rect.height + abs(displacement.y))

class Transform:
    def __init__(self, position=wx.RealPoint(), scale=Scale(), orientation=Orientation.normal) -> None:
        self.position:wx.RealPoint = wx.RealPoint(position.x, position.y) # wx.RealPoint
        self.scale:Scale = scale.copy() # a Scale
        self.orientation:Orientation = orientation # an Orientation

    def __eq__(self, other) -> bool:
        result = False
        if self.position == other.position and self.scale == other.scale and self.orientation == other.orientation:
            result = True
        return result

    def __str__(self) -> str:
        s = '<Transform position=' + str(self.position.x)+','+ str(self.position.y)
        s += ' scale=' + str(self.scale)
        s += ' orientation=' + str(self.orientation)
        s += '>'
        return s

    def copy(self) -> 'Transform':
        result = Transform(self.position, self.scale, self.orientation)
        return result

    def applyTransform(self, transform:'Transform', obj) -> 'Transform': # returns new Transform result of applying a given transform to this (self) (to go down a grouping level)
        newTransform = self.copy()
        # reorientate
        if obj is None or obj.isOrientable():
            orientation = doReorientation(transform.orientation, self.orientation)
            newTransform.orientation = orientation
        # scale
        if obj is None or obj.isScalable():
            selfScale = self.scale.normalise(transform.orientation)
            newTransform.scale.x = transform.scale.x * selfScale.x
            newTransform.scale.y = transform.scale.y * selfScale.y
        # translate (shift origin)
        newTransform.position = self.backTransformPoint(transform.position, obj)
        return newTransform

    def transformPoint(self, hiPt:AnyPoint, obj) -> wx.RealPoint: # returns result of transforming hiPt to go down (downPt) to lower grouping level with this (self) transform
        downPt = wx.RealPoint()
        # translate
        downPt.x = hiPt.x - self.position.x
        downPt.y = hiPt.y - self.position.y
        # unscale
        orientation = doOppositeReorientation(self.orientation)
        if obj is None or obj.isScalable():
            scale = self.scale.normalise(orientation)
            downPt = scale.unscalePoint(downPt)
        # reorientate
        if obj is None or obj.isOrientable():
            downPt = reorientatePoint(downPt, orientation)
        return downPt

    def backTransformPoint(self, loPt:AnyPoint, obj) -> wx.RealPoint: # returns result of transforming loPt to go up (upPt) to higher grouping level from (lower) group with this (self) transform
        upPt = wx.RealPoint(loPt)
        # back-orientate
        backOrientation = self.orientation
        if obj is None or obj.isOrientable():
            upPt = reorientatePoint(loPt, backOrientation)
        # scale back
        if obj is None or obj.isScalable():
            scale = self.scale.normalise(backOrientation)
            upPt = scale.scalePoint(upPt)
        # back-translate
        upPt.x = upPt.x + self.position.x
        upPt.y = upPt.y + self.position.y
        return upPt
