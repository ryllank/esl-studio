#! /usr/bin/python

import sys
import os

import wx

import esl_diagram.xmlutil as xut

from . import utils as Utils
from . import auihandler as aui
from .views.view import View

class Toolbar(View, aui.AuiToolBar):

    TagAttributeProfileDict = {"item":"command"}

    def __init__(self, parent, viewtype):
        self._frame = parent
        bar = aui.AuiToolBar.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize)
        View.__init__(self, parent, viewtype)
        self._toolbarXmlProfile = xut.XmlElement("<toolbar-profile/>")


    def clear(self):
        self._toolbarXmlProfile = xut.XmlElement("<toolbar-profile/>")
        self.Clear()

    def loadFromFile(self, filepath):
        if os.path.exists(filepath):
            xmlElement, error = xut.xmlElementFromFile(filepath)
            if xmlElement:
                self.loadFromXml(xmlElement)

    def loadFromString(self, strng):
        xmlElement = xut.xmlElement(strng)
        if xmlElement:
            self.loadFromXml(xmlElement)

    def loadFromXml(self, xmlElement):
        if xmlElement.name() == "toolbar": toolbarXmlElement = xmlElement
        else: toolbarXmlElement = xmlElement.getXmlElementByName("toolbar", True)
        if toolbarXmlElement:
            itemXmlList = toolbarXmlElement.getChildren()
            for itemXmlElement in itemXmlList:
                self._toolbarXmlProfile.replaceOrAppendChild(itemXmlElement, Toolbar.TagAttributeProfileDict)

    def installProfile(self):
        itemXmlList = self._toolbarXmlProfile.getChildren()
        self.SetToolBitmapSize(wx.Size(16, 15))
        for itemXmlElement in itemXmlList:
            platform = itemXmlElement.getAttribute("platform")
            if not platform or platform == sys.platform:
                itemName = itemXmlElement.name()
                if itemName == "item":
                    self.addItem(itemXmlElement)
                elif itemName == "separator":
                    self.AddSeparator()
        self.Realize()
        if aui.UseAUI() == aui.AUI_WX:
            pane = self._frame.auiManager().GetPane(self)
            if pane.best_size != self.Size:
                pane.best_size = self.Size
        self._frame.auiManager().Update() # this seems to be needed (even though happens later in control)

    def addItem(self, itemXmlElement):
        bitmap = None
        command = itemXmlElement.getAttribute("command")
        text = itemXmlElement.getAttribute("text") # This 'label' doesnt seem to do anything.
        description = itemXmlElement.getContent()
        image = itemXmlElement.getAttribute("image")
        if image:
            bitmap = Utils.getButtonBitmap(image)
        if command and bitmap:
            commandDefn = self._frame.commands().commandDefnByName.get(command)
            if commandDefn:
                if not description:
                    description = commandDefn.commandXmlElement.getContent()
                if description is None: description = ""
                description = description.strip()
                checkable = False
                infoXmlElement = commandDefn.commandXmlElement.getXmlElementByName("info")
                if infoXmlElement:
                    checkable = infoXmlElement.getAttribute("checkable")
                itemkind = wx.ITEM_NORMAL
                if checkable:
                    itemkind = wx.ITEM_CHECK
                if text is None: text = ""
                self.AddTool(commandDefn.commandId, text, bitmap, wx.NullBitmap, itemkind, description, description, None) #2nd description s'posed to show on status bar but doesn't.
                self._frame.Bind(wx.EVT_MENU, self._frame.commands().invokeCommand,
                                 id = commandDefn.commandId)

    def defaultPaneInfo(self):
        info = aui.AuiPaneInfo()
        info.Name("toolbar")
        info.Caption("ESL Studio Toolbar")
        info.ToolbarPane()
        info.Top()
        return info

    def toggleItem(self, toolId, showing):
        self.ToggleTool(toolId, showing)
        # the above usually work but once in a while (?some path)
        # the button is in the wrong state till you mouse on the toolbar - so try:
        self.Refresh() # this seems to to it

    def enableItem(self, toolId, enable):
        self.EnableTool(toolId, enable)
        self.Refresh() # this seems needed
