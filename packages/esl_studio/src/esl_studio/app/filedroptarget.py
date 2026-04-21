#! /usr/bin/python

import os

import wx

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, frame):
       wx.FileDropTarget.__init__(self)
       self._frame = frame

    def OnDropFiles(self, x, y, filenames):
        if len(filenames) > 0:
            self._frame.commands().dropFiles(filenames)
