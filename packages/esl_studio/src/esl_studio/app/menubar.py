#! /usr/bin/python

import os
import sys

import wx

import esl_diagram.xmlutil as xut

from .views.view import View

from .commands import Commands, CommandDefn

REQUIRED_MENU_COMMANDS = ["Open Application", "Show Options", "Exit Application"]
REQUIRED_MENU_TEXTS = {"Open Application":"&Open...", "Show Options":"Preferences/&Options...", "Exit Application":"E&xit"}
REQUIRED_MENU_DEFNS = {
    "Open Application":"<commands><command name=\"Open Application\" procedure=\"OpenApplication\"/></commands>",
    "Show Options":"<commands><command name=\"Show Options\" procedure=\"ShowOptions\"/></commands>",
    "Exit Application":"<commands><command name=\"Exit Application\" procedure=\"ExitApp\"/></commands>"}
MENU_TEXT_FOR_REQUIRED_COMMANDS = "&File"

class Menubar(View, wx.MenuBar):

    TagAttributeProfileDict = {"menu":"text"}

    def __init__(self, parent):
        View.__init__(self, parent, "menubar")
        self._parent = parent
        self._frame = parent
        self._topLevelMenus = {}
        self._requiredMenuCommands = {}
        self._menubarXmlProfile = xut.XmlElement("<menubar-profile/>")
        mb = wx.MenuBar.__init__(self)

        file_menu = wx.Menu()
        file_menu.Append(wx.ID_EXIT, "E&xit")

        self._frame.Bind(wx.EVT_MENU, self._frame.commands().ExitApp, id = wx.ID_EXIT)

        self.Append(file_menu, "&File")

    def clear(self):
        nMenus = self.GetMenuCount()
        for menuix in range(nMenus):
            self.Remove(0)
        self._topLevelMenus = {}
        self._requiredMenuCommands = {}
        self._menubarXmlProfile = xut.XmlElement("<menubar-profile/>")

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
        if xmlElement.name() == "menubar": menubarXmlElement = xmlElement
        else: menubarXmlElement = xmlElement.getXmlElementByName("menubar", True)
        if menubarXmlElement:
            itemXmlList = menubarXmlElement.getChildren()
            for itemXmlElement in itemXmlList:
                self._menubarXmlProfile.replaceOrAppendChild(itemXmlElement, Menubar.TagAttributeProfileDict)

    def installProfile(self):
        itemXmlList = self._menubarXmlProfile.getChildren()
        for itemXmlElement in itemXmlList:
            platform = itemXmlElement.getAttribute("platform")
            if not platform or platform == sys.platform:
                itemName = itemXmlElement.name()
                if itemName == "menu":
                    self.addMenu(self, itemXmlElement)
                elif itemName == "item":
                    self.addItem(self, itemXmlElement)
                elif itemName == "separator":
                    self.addSeparator(self, itemXmlElement)
                elif itemName == "history":
                    self.addHistoryItem(self, itemXmlElement)

    def addMenu(self, baseitem, itemXmlElement):
        text = itemXmlElement.getAttribute("text")
        if text:
            menu = None
            if isinstance(baseitem, wx.MenuBar):
                menu = self._topLevelMenus.get(text)
                if not menu:
                    menu = wx.Menu()
                    baseitem.Append(menu, text)
                    self._topLevelMenus[text] = menu
            else:
                menu = wx.Menu()
                baseitem.AppendSubMenu(menu, text)
            subitemXmlList = itemXmlElement.getChildren()
            for subitemXmlElement in subitemXmlList:
                platform = subitemXmlElement.getAttribute("platform")
                if not platform or platform == sys.platform:
                    itemName = subitemXmlElement.name()
                    if itemName == "menu":
                        self.addMenu(menu, subitemXmlElement)
                    elif itemName == "item":
                        self.addItem(menu, subitemXmlElement)
                    elif itemName == "separator":
                        self.addSeparator(menu, subitemXmlElement)
                    elif itemName == "history":
                        self.addHistoryItem(menu, subitemXmlElement)

    def addItem(self, baseitem, itemXmlElement):
        command = itemXmlElement.getAttribute("command")
        text = itemXmlElement.getAttribute("text")
        description = itemXmlElement.getContent()
        if command and text:
            commandDefn = self._frame.commands().commandDefnByName.get(command)
            if commandDefn:
                if command in REQUIRED_MENU_COMMANDS:
                    self._requiredMenuCommands[command] = True
                self.addItemToMenu(baseitem, text, description, commandDefn)

    def addItemToMenu(self, baseitem, text, description, commandDefn):
        if not description:
            description = commandDefn.commandXmlElement.getContent()
        if description is None: description = ""
        # checkable = False
        infoXmlElement = commandDefn.commandXmlElement.getXmlElementByName("info")
        itemKind = wx.ITEM_NORMAL
        if infoXmlElement:
            checkable = infoXmlElement.getAttribute("checkable")
            if checkable:
                itemKind = wx.ITEM_CHECK
        item = wx.MenuItem(baseitem, commandDefn.commandId, text, description, itemKind)
        # baseitem.Append(commandDefn.commandId, text, description)
        baseitem.Append(item)
        self._frame.Bind(wx.EVT_MENU, self._frame.commands().invokeCommand,
                         id=commandDefn.commandId)

    def addSeparator(self, baseitem, itemXmlElement):
        baseitem.AppendSeparator()

    def addHistoryItem(self, baseitem, itemXmlElement):
        self._frame.applicationHistory().useMenu(baseitem)

    def findItemsById(self, itemId):
        # Assumes may occur once in each top-level menu
        items = []
        for menuNText in self.GetMenus():
            self._findItemsById(menuNText[0], itemId, items)
        return items
    def _findItemsById(self, menu, itemId, items):
        menuitem = menu.FindItemById(itemId)
        if menuitem:
            items.append(menuitem)

    def checkItem(self, itemId, check):
        #menuitem = self.FindItemById(itemId)
        menuItems = self.findItemsById(itemId)
        for menuitem in menuItems:
            if menuitem and menuitem.IsCheckable():
                menuitem.Check(check)

    def enableItem(self, itemId, enable):
        menuitem = self.FindItemById(itemId)
        if menuitem:
            menuitem.Enable(enable)

    def checkRequiredMenuCommands(self):
        menu = None
        for command in REQUIRED_MENU_COMMANDS:
            if not self._requiredMenuCommands.get(command):
                if not menu:
                    menu = self._topLevelMenus.get(MENU_TEXT_FOR_REQUIRED_COMMANDS)
                    if not menu:
                        menu = wx.Menu()
                        self.Insert(0, menu, MENU_TEXT_FOR_REQUIRED_COMMANDS) # put as first toplevel menu
                        self._topLevelMenus[MENU_TEXT_FOR_REQUIRED_COMMANDS] = menu
                        createdFileMenu = True
                    else:
                        createdFileMenu = False
                commandDefn = self._frame.commands().commandDefnByName.get(command)
                if not commandDefn:
                    self._frame.commands().loadFromString(REQUIRED_MENU_DEFNS.get(command))
        self._frame.commands().installProfile()
        for command in REQUIRED_MENU_COMMANDS:
            if not self._requiredMenuCommands.get(command):
                commandDefn = self._frame.commands().commandDefnByName.get(command)
                if commandDefn:
                    text = REQUIRED_MENU_TEXTS.get(command)
                    if not createdFileMenu or command != REQUIRED_MENU_COMMANDS[0]:
                        menu.AppendSeparator()
                    self.addItemToMenu(menu, text, None, commandDefn)

    def enableDisableSubMenus(self):
        for menu, label in self.GetMenus():
            for subitem in menu.GetMenuItems():
                self.enableDisableSubMenusSubitem(subitem)

    def enableDisableSubMenusSubitem(self, item):
        if item.IsSubMenu():
            submenu = item.GetSubMenu()
            for subitem in submenu.GetMenuItems():
                self.enableDisableSubMenusSubitem(subitem)
            anyEnabled = False
            for subitem in submenu.GetMenuItems():
                if subitem.IsEnabled():
                    anyEnabled = True
                    break
            item.Enable(anyEnabled)
