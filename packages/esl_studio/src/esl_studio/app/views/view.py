#! /usr/bin/python

import wx

class View(object):

    def __init__(self, parent, viewtype):
        self._parent = parent
        self._viewtype = viewtype           # floatable 'pane' or 'std-pane' or mainview 'page' or 'std-page'
        self._viewName = ""
        self._caption = ''
        self._tooltip = ''
        self._mode = "editing"

    def mode(self):
        return self._mode
    def setMode(self, mode):
        self._mode = mode

    def parent(self): return self._parent
    def viewtype(self): return self._viewtype
    def viewName(self): return self._viewName
    def caption(self): return self._caption
    def tooltip(self): return self._tooltip

    def set_viewName(self, viewName):
        self._viewName = viewName

    def set_parent(self, newParent):
        self._parent = newParent

    def set_caption(self, caption, tooltip=None):
        self._caption = caption
        if tooltip is not None:
            self._tooltip = tooltip
        else:
            self._tooltip = caption
        if self._viewtype == 'page' or self._viewtype == 'std-page':
            page_idx = self._parent.GetPageIndex(self)
            if page_idx != wx.NOT_FOUND:
                self._parent.SetPageText(page_idx, self._caption)
                #self._parent.SetPageToolTip(page_idx, self._tooltip)

    def checkSelectedInMainView(self):
        mainView = None
        if self._parent and (self._viewtype == "page" or self._viewtype == "std-page"):
            mainView = self._parent
        if mainView:
            pageIndex = mainView.GetPageIndex(self)
            if pageIndex != wx.NOT_FOUND:
                currentPageIndex = mainView.GetSelection()
                if pageIndex != currentPageIndex:
                    #print("*View.checkSelectedInMainView selecting from currentPageIndex=" + str(currentPageIndex) + " to pageIndex=" + str(pageIndex))
                    mainView.SetSelection(pageIndex)

    def detectToCheckSelectedInMainView(self, window, noChildFocus=False):
        window.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)
        if not noChildFocus:
            window.Bind(wx.EVT_CHILD_FOCUS, self.OnChildFocus)
        for child in window.GetChildren():
            self.detectToCheckSelectedInMainView(child)

    def clearView(self):        # Override this in Views that need to clear something for new application (such as property grids' properties).
        pass

    def OnMouseEvents(self, mouseEvent):
        if mouseEvent.ButtonDown(): # Any button
            #print(">View.OnMouseEvents button down")
            self.checkSelectedInMainView()
        mouseEvent.Skip()

    def OnChildFocus(self, childFocusEvent):
        #print(">View.OnChildFocus")
        self.checkSelectedInMainView()
        childFocusEvent.Skip()

class ModuleView(View):
    def __init__(self, parent, viewtype):
        View.__init__(self, parent, viewtype)
        self._moduleId = 0

    def moduleId(self): return self._moduleId
    def set_moduleId(self, moduleId):
        self._moduleId = moduleId
