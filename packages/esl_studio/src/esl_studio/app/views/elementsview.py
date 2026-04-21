#! /usr/bin/python

import os

import wx

import esl_diagram.xmlutil as xut

from .. import auihandler as aui
from .view import View

class ElementItemId():
    def __init__(self, index):
        self._index = index

    def GetIndex(self):
        return self._index

class ElementsView(View, wx.TreeCtrl):

    TagAttributeProfileDict = {"section":"name"}

    def __init__(self, parent, viewtype):
        treeStyles = wx.TR_DEFAULT_STYLE | wx.NO_BORDER | wx.TR_HIDE_ROOT
        tree = wx.TreeCtrl.__init__(self, parent, -1, wx.Point(0, 0), wx.Size(160, 250), treeStyles)
        View.__init__(self, parent, viewtype)
        self._elementsXmlProfile = xut.XmlElement("<elements-profile/>")
        self.clear()

        #self.Expand(root) - this caused a crash in MSW
        self.Bind(wx.EVT_CLOSE, self.OnCloseView, self)
 #       self.Bind(wx.EVT_CANCEL, self.OnCancelView, self)

        #self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.onBeginDragItem, self)
        #self.Bind(wx.EVT_TREE_END_DRAG, self.onEndDragItem, self)
        #self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onItemActivated, self)
        #self.Bind(wx.EVT_TREE_DELETE_ITEM, self.onDeleteItem, self)

        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16, 16)))
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16)))
        self.AssignImageList(imglist)

    def defaultPaneInfo(self):
        info = aui.AuiPaneInfo()
        info.Name("elementsView")
        info.Caption("Elements")
        info.CaptionVisible(True)
        info.Dockable(True)
        info.Floatable(True)
        #info.Float()
        info.Left()
        info.Layer(1)
        info.FloatingPosition(wx.Point(100, 100))
        info.FloatingSize(wx.Size(150, 300))
        info.MinimizeButton(True)
        info.MaximizeButton(True)
        info.CloseButton(True)
        info.PaneBorder(True)
        info.Resizable(True)
        #info.Gripper(True)
#        info.DestroyOnClose(True)
        return info

    def clear(self):
        self._elementXmlElements = []
        self.DeleteAllItems()
        root = self.AddRoot("ROOT", 0)
        self._elementsXmlProfile = xut.XmlElement("<elements-profile/>")

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
        if xmlElement.name() == "elements": elementsXmlElement = xmlElement
        else: elementsXmlElement = xmlElement.getXmlElementByName("elements", True)
        if elementsXmlElement:
            root = self.GetRootItem()
            elementXmlList = elementsXmlElement.getChildren()
            for elementXmlElement in elementXmlList:
                self._elementsXmlProfile.replaceOrAppendChild(elementXmlElement, ElementsView.TagAttributeProfileDict)

    def installProfile(self):
        root = self.GetRootItem()
        elementXmlList = self._elementsXmlProfile.getChildren()
        for elementXmlElement in elementXmlList:
            elementName = elementXmlElement.name()
            if elementName == "section":
                self.addSection(root, elementXmlElement)
            elif elementName == "element":
                self.addElement(root, elementXmlElement)

    def addSection(self, baseitem, sectionXmlElement):
        name = sectionXmlElement.getAttribute("name")
        if name:
            sectionitem = self.AppendItem(baseitem, name, 0)
            elementXmlList = sectionXmlElement.getChildren()
            for elementXmlElement in elementXmlList:
                elementName = elementXmlElement.name()
                if elementName == "section":
                    self.addSection(sectionitem, elementXmlElement)
                elif elementName == "element":
                    self.addElement(sectionitem, elementXmlElement)

    def addElement(self, baseitem, elementXmlElement):
        name = elementXmlElement.getAttribute("name")
        if name:
            index = len(self._elementXmlElements)
            elementId = ElementItemId(index)
            item = self.AppendItem(baseitem, name, 1, -1)#, elementId) =- doesnt like this
            self.SetItemData(item, elementId)
            self._elementXmlElements.append(elementXmlElement)

    def getElementXml(self, tree_event):
        descr = None
        item = tree_event.GetItem()
        text = self.GetItemText(item)
        elementId = self.GetItemData(item)#item.GetId()
        elementXmlElement = None
        if elementId:
            ix = elementId.GetIndex()
            if ix >= 0:
                elementXmlElement = self._elementXmlElements[ix]
                #if elementXmlElement:
                #    descr = elementXmlElement.getChildren()[0]
        return elementXmlElement

    def OnCloseView(self, event):
        self._parent._elementsView = None
        self.Destroy()

    #def onEndDragItem(self, tree_event):
    #    item = tree_event.GetItem()
    #    text = self.GetItemText(item)

    def onItemActivated(self, tree_event):
        item = tree_event.GetItem()
        if self.ItemHasChildren(item):
            if self.IsExpanded(item):
                self.Collapse(item)
            else:
                self.Expand(item)
