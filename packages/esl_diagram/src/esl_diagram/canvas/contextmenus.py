#! /usr/bin/python

import wx

from .diagram import Diagram
#from selection import Selection
#from interactions import Interactions
from .actions import ActionContext

class ContextMenus(object):
    def __init__(self, interactions, canvas):
        self._interactions = interactions
        self._canvas = canvas
        self._menus = {}
        self._menuItemById = {}
        self._lastMenuItemId = 0
        #_lastMenuItemId = wx.ID_HIGHEST + 1
        #_lastMenuItemId += 400  # safety margin

    def clearContextMenuDefinitions(self):
        self._menus = {}
        self._menuItemById = {}

    def setContextMenuDefinitions(self, canvasDefinitions):
        self.loadMenusFromXml(canvasDefinitions)

    def loadMenusFromXml(self, xmlElement):
        if xmlElement:
            if xmlElement.name() == "menus": menusElements = [xmlElement]
            else: menusElements = xmlElement.getXmlElementListByName("menus", True)
            if menusElements:
                for menusElement in menusElements:
                    menuElements = menusElement.getXmlElementListByName("menu", False)
                    for menuElement in menuElements:
                        name = menuElement.getAttribute("name")
                        self._menus[name] = menuElement

    def setBackgroundContextMenu(self):
        menu = None
        if self._canvas.diagram().properties().BackgroundContextMenu:
            menuElement = self._menus.get(self._canvas.diagram().properties().BackgroundContextMenu)
            if menuElement:
                menu = wx.Menu()
                self.addMenu(menu, menuElement, None)
        return menu

    def showBackgroundContextMenu(self):
        menu = self.setBackgroundContextMenu()
        if menu:
            self._canvas.PopupMenu(menu)
            menu.Destroy()

    def setSelectionContextMenu(self):
        menu = None
        menuElement = None
        selectedObjects = self._interactions.selection().selection()
        pair = len(selectedObjects) == 2
        if self._canvas.diagram().properties().GroupableSelectionContextMenu:
            groupable = True
            for object in selectedObjects:
                category = object.category()
                if category != "group" and category != "element":
                    groupable = False
                    break
            if groupable:
                if pair and self._canvas.diagram().properties().GroupablePairSelectionContextMenu:
                    menuElement = self._menus.get(self._canvas.diagram().properties().GroupablePairSelectionContextMenu)
                if not menuElement:
                    menuElement = self._menus.get(self._canvas.diagram().properties().GroupableSelectionContextMenu)
        if not menuElement:
            if self._canvas.diagram().properties().SelectionContextMenu:
                if pair and self._canvas.diagram().properties().PairSelectionContextMenu:
                    menuElement = self._menus.get(self._canvas.diagram().properties().PairSelectionContextMenu)
                if not menuElement:
                    menuElement = self._menus.get(self._canvas.diagram().properties().SelectionContextMenu)
        if menuElement:
            menu = wx.Menu()
            self.addMenu(menu, menuElement, self._interactions.selection())
        return menu

    def showSelectionContextMenu(self):
        menu = self.setSelectionContextMenu()
        if menu:
            self._canvas.PopupMenu(menu)
            menu.Destroy()

    def setObjectContextMenu(self, obj):
        menu = None
        if obj.contextmenu():
            menuElement = self._menus.get(obj.contextmenu())
            if menuElement:
                menu = wx.Menu()
                self.addMenu(menu, menuElement, obj)
        return menu

    def showObjectContextMenu(self, obj):
        if obj.contextmenu():
            menu = self.setObjectContextMenu(obj)
            if menu:
                self._canvas.PopupMenu(menu)
                menu.Destroy()
        else:
            obj.showContextMenu()

    def addMenu(self, basemenu, menuElement, target):
        menuItemElements = menuElement.getChildren()
        for menuItemElement in menuItemElements:
            itemname = menuItemElement.name()
            if itemname == "block":
                text = menuItemElement.getAttribute("text")
                if text:
                    menu = wx.Menu()
                    basemenu.AppendSubMenu(menu, text)
                    self.addMenu(menu, menuItemElement, target)
            elif itemname == "item":
                self.addItem(basemenu, menuItemElement, target)
            elif itemname == "separator":
                basemenu.AppendSeparator()
            elif itemname == "menu":
                name = menuItemElement.getAttribute("name")
                subMenuElement = self._menus.get(name)
                if subMenuElement:
                    self.addMenu(basemenu, subMenuElement, target)

    def addItem(self, baseitem, menuItemElement, target):
        action = menuItemElement.getAttribute("action")
        text = menuItemElement.getAttribute("text")
        if action and text:
            description = menuItemElement.getContent()
            baseitem.Append(self._lastMenuItemId, text, description)
            self._menuItemById[self._lastMenuItemId] = menuItemElement
            self._canvas.Bind(wx.EVT_MENU, self._canvas.actions().ContextMenuAction,
                             source=None,
                             id=self._lastMenuItemId,
                             id2=-1)
            self._lastMenuItemId += 1

    def getMenuItemById(self, menuItemId):
        menuItemElement = self._menuItemById.get(menuItemId)
        return menuItemElement
