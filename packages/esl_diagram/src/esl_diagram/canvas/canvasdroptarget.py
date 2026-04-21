#! /usr/bin/python

import wx

from .. import xmlutil as xut
from .actions import ActionContext

#class CanvasDropData(wx.DataObject):
#    def __init__(self):
#        wx.DataObject.__init__(self)

class CanvasDropTarget(wx.TextDropTarget): #wx.FileDropTarget):#wx.DropTarget):
    def __init__(self, canvas):
        self._canvas = canvas
        """wx.DropTarget.__init__(self)
        self._canvas = canvas
        self._dropData = wx.DataObjectComposite() #CanvasDropData()
        self._dropData.Add(wx.FileDataObject())
        self._dropData.Add(wx.TextDataObject())
        self.SetDataObject(self._dropData)
        """
        #wx.FileDropTarget.__init__(self)
        wx.TextDropTarget.__init__(self)

    ##def OnDrop(self, x, y):
    ##    return True

    """def OnData(self, x, y, defResult):
        if self.GetData():
            format = self._dropData.GetReceivedFormat()
            formatType = format.GetType()
            if formatType == wx.DF_FILENAME:
                dataObj = self._dropData.GetObject(format)
                filenames = dataObj.GetDataHere()
                self.onFileDrop(filenames)
            elif formatType == wx.DF_TEXT or formatType == wx.DF_UNICODETEXT:
                dataObj = self._dropData.GetObject(format) #in wxPy302 we see TODO: Fix this to use OOR and return the right object type.
                text = dataObj.GetDataHere() # This nearly works (see correct thing in dbgr) but not quite
                print type(text)
                #fileDO = wx.TextDataObject(dataObj)
                #text = fileDO.GetText()
                self.onTextDrop(x, y, text)
    """

    def OnDropText(self, x, y, text):
        result = self.onTextDrop(x, y, text)
        return result

    def onTextDrop(self, x, y, text):
        result = False
        pos = self._canvas.screenCoordsToDiagramPos(x, y)
        actionContext = ActionContext()
        actionContext.type = 'drop-element'
        #actionContext.dc
        actionContext.ptr = pos
        try:
            action = "Insert"
            actionXmlElement = xut.xmlElement(text)
            if actionXmlElement:
                self._canvas.actions().InvokeAction(action, actionContext, actionXmlElement)
                result = True
        except Exception as e:
            errorMsg = "Cannot insert \""+text+"\"\nException: " + str(e)
            self._canvas.raiseCanvasApplicationNotifyEvent('', "display", errorMsg)
            #wx.MessageBox(text)
        return result

    def OnDropFiles(self, x, y, filenames): ## need a FileDropTarget
        self.onFileDrop(filenames)

    def onFileDrop(self, filenames):
        applicationdata = ''
        infoStr = '|'.join(filenames)
        infoStr = 'filenames="'+infoStr+'"' #?enitised
        self._canvas.raiseCanvasApplicationRequestEvent(applicationdata, "File Drop", infoStr, '')
