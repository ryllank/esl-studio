#! /usr/bin/python

from collections import OrderedDict

import wx

# these views imported into globals()
from .menubar import Menubar
from . import auihandler as aui
#from .toolbar import Toolbar - have to defer the impartation as depends on AUI
#from .mainview import MainView - have to defer the impartation as depends on AUI
from .views.elementsview import ElementsView
from .views.messagesview import MessagesView
from .views.propertiesview import PropertiesView
from .views.simulationparametersview import SimulationParametersView
from .views.applicationview import ApplicationView
from .views.setupview import SetupView

# A view may be a 'pane' or 'std-pane' or a 'page' or 'std-page' (or 'menubar').
# Panes belong to the auiManager and can be docked or floating (and in wxPython superimposed) and includes Toolbar(s) ?? Menubar.
# MainView is a special case of pane (which can't be undocked) at the "centre" of the application window.
# Pages are tabs in the MainView.

StdViews = OrderedDict(
    [
        ("MainView", ["MainView", 'std-pane']),
        ("Toolbar", ["Toolbar", 'std-pane']),
        ("ApplicationView", ["ApplicationView", 'std-pane']),
        ("ElementsView", ["ElementsView", 'std-pane']),
        ("MessagesView", ["MessagesView", 'std-pane']),
        ("PropertiesView", ["PropertiesView", 'std-pane']),
        ("SimulationParametersView", ["SimulationParametersView", 'std-page']),
        ("SetupView", ["SetupView", 'std-page'])
    ]
)

class ViewManager(object):

    def __init__(self, frame):
        self._frame = frame
        self._views = {}
        self._mainView = None
        self._mode = "editing"

    def MakeStdPanes(self):
        for viewName in StdViews:
            viewinfo = StdViews[viewName]
            classname = viewinfo[0]
            viewtype = viewinfo[1]
            cls = self._getclass(classname)
            if cls:
                if viewtype == 'std-pane':
                    view = cls(self._frame, viewtype)
                    if view:
                        if viewName == 'MainView':
                            self._mainView = view
                        self.addPane(view, viewName)
                else: # std-page
                    view = cls(self._mainView, viewtype)
                    if view:
                        self.addView(view, viewName)
                        # we dont add it to the mainView at this stage
                        if view:
                            view.Hide()
                        #    self.mainView().AddPage(page, page.caption())

    def CreateMenuBar(self):
        # create menu
        self._menubar = Menubar(self._frame)
        self._views["Menubar"] = self._menubar
        self._frame.SetMenuBar(self._menubar)

    def mainView(self): return self._mainView
    def menubar(self): return self._views.get("Menubar")
    def toolbar(self): return self._views.get("Toolbar")
    def elementsView(self): return self._views.get("ElementsView")
    def messagesView(self): return self._views.get("MessagesView")
    def propertiesView(self): return self._views.get("PropertiesView")
    def simulationParametersView(self): return self._views.get("SimulationParametersView")
    def applicationView(self): return self._views.get("ApplicationView")
    def setupView(self): return self._views.get("SetupView")

    def getView(self, viewName):
        return self._views.get(viewName)

    def addView(self, view, viewName):
        self._views[viewName] = view
        view.set_viewName(viewName)

    def addPane(self, view, viewName):
        if viewName in self._views:
            raise Exception("View (pane) \""+viewName+"\" is already in the application")
        else:
            self.addView(view, viewName)
            if hasattr(view, "defaultPaneInfo"):
                paneinfo = view.defaultPaneInfo()
            else:
                paneinfo = aui.AuiPaneInfo()
                paneinfo.Caption("Unknown")
                paneinfo.Float()
                paneinfo.BestSize(200, 150)
                paneinfo.MinimizeButton(True)
                paneinfo.MaximizeButton(True)
                paneinfo.CloseButton(True)
                paneinfo.PaneBorder(True)
                paneinfo.Show(True)
            paneinfo.Name(viewName)
            self._frame.auiManager().AddPane(view, paneinfo)

    def viewIsShowing(self, viewName):
        showing = False
        view = self._views.get(viewName)
        if view:
            viewtype = view.viewtype()
            if viewtype == 'pane' or viewtype == 'std-pane':
                paneinfo = self._frame.auiManager().GetPane(view)
                showing = paneinfo.IsShown()
            else: #page or std-page
                page_index = self._mainView.GetPageIndex(view)
                showing = page_index != wx.NOT_FOUND
        return showing

    def showView(self, viewName, showing = True):
        view = self._views.get(viewName)
        if view:
            viewtype = view.viewtype()
            if viewtype == 'pane' or viewtype == 'std-pane':
                paneinfo = self._frame.auiManager().GetPane(view)
                if showing != paneinfo.IsShown():
                    self.showPaneView(paneinfo, showing)
            else: # page or std-page
                page_index = self._mainView.GetPageIndex(view)
                if page_index != wx.NOT_FOUND:
                    if showing:
                        self._mainView.SetSelection(page_index) # go to it
                    else:
                        self._mainView.detachPage(view)
                else:
                    if showing:
                        self._mainView.reattachPage(view)

    def toggleView(self, viewName):
        showing = False
        view = self._views.get(viewName)
        if view:
            viewtype = view.viewtype()
            if viewtype == 'pane' or viewtype == 'std-pane':
                paneinfo = self._frame.auiManager().GetPane(view)
                showing = not paneinfo.IsShown()
                self.showPaneView(paneinfo, showing)
            else: # page or std-page
                page_index = self._mainView.GetPageIndex(view)
                if page_index != wx.NOT_FOUND:
                    self._mainView.detachPage(view)
                    showing = False
                else:
                    self._mainView.reattachPage(view)
                    showing = True
                    # show it now?
                    page_index = self._mainView.GetPageIndex(view)
                    self._mainView.SetSelection(page_index)
        return showing

    def showPaneView(self, paneinfo, showing):
        paneinfo.Show(showing)
        self._frame.auiManager().checkNotebookPaneShow(paneinfo, showing)
        if showing:
            paneinfo.window.setMode(self._frame.control().mode())
        self._frame.auiManager().Update()

    def stdViewName(self, view):
        result = ''
        for viewName in self._views:
            if self._views[viewName] == view:
                result = viewName
                break
        return result

    def _getclass(self, classname):
        from .toolbar import Toolbar # deferred till now as depends on AUI
        from .mainview import MainView # deferred till now as depends on AUI
        if classname == "Toolbar":
            cls = Toolbar
        elif classname == "MainView":
            cls = MainView
        else:
            cls = globals().get(classname)
            if cls is None:
                classinfo = classname.split('.')
                if len(classinfo) == 2:
                    pkg = globals().get(classinfo[0])
                    if pkg:
                        cls = pkg.__dict__.get(classinfo[1])
        return cls

    def resetMainview(self):
        self._mainView.resetMainview()

    def setPaneCaption(self, view, caption):
        paneinfo = self._frame.auiManager().GetPane(view)
        paneinfo.Caption(caption)

    def resetPanes(self):
        views = self._views.copy()
        for viewName, view in views.items():
            if view.viewtype() == 'pane': # not std-pane
                paneinfo = self._frame.auiManager().GetPane(view)
                self._frame.viewManager().showPaneView(paneinfo, False)
                self._frame.auiManager().DetachPane(paneinfo)
                #paneinfo.DestroyOnClose(True)
                #self._frame.auiManager().ClosePane(paneinfo)
                del self._views[viewName]
        pass

    def setMode(self, mode):
        for view in self._views.values():
            view.setMode(mode)

    def clearViews(self):
        for view in self._views.values():
            view.clearView()
