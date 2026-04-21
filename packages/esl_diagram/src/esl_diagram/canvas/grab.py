#! /usr/bin/python

import wx

from .group import Group

class Grab(Group):
    def __init__(self, type, diagram, position, grabbedObject, descr = None):
        Group.__init__(self, "grab", type, diagram, position, None, descr)
        self._selectable = False
        self._draggable = False
        self.grabbedObject = grabbedObject
        self._lastGrabbedObjectExtent = None

    def startGrabDragging(self):
        self._startDragPosn = wx.RealPoint(self._position)
        self._dragDisplacement = wx.RealPoint()
        self._lastGrabbedObjectExtent = self.grabbedObject.getGrabOverlayExtent(None) # ? or self.grabbedObject._lastExtent
        self.grabbedObject.startGrabDragging(self)

    def grabDragBy(self, displacement):
        if displacement is not None and (displacement.x != 0 or displacement.y != 0):
            self._dragDisplacement += wx.RealPoint(displacement)
            newPosition = wx.RealPoint(self._startDragPosn.x + self._dragDisplacement.x,
                                       self._startDragPosn.y + self._dragDisplacement.y)
            self._position = wx.Point(newPosition) # move this grab
            self.grabbedObject.grabDragBy(self._dragDisplacement) # does extent change ond may move other grabs
            self.refreshGrabbedObjectOverlayExtent()

    def stopGrabDragging(self):
        self.grabbedObject.stopGrabDragging()
        self.refreshGrabbedObjectOverlayExtent()
        self._startDragPosn = None
        self._dragDisplacement = None
        self._lastGrabbedObjectExtent = None

    def refreshGrabbedObjectOverlayExtent(self):
        ext = self.grabbedObject.getGrabOverlayExtent(None)
        if self._lastGrabbedObjectExtent is not None:
            self._diagram._canvas.refreshExtent(ext.Union(self._lastGrabbedObjectExtent))
        else:
            self._diagram._canvas.refreshExtent(ext)
        self._lastGrabbedObjectExtent = ext
