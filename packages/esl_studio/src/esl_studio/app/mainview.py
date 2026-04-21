#! /usr/bin/python

import wx

from .config import Config
from . import auihandler as aui
from .views.view import View
from .views.view import ModuleView
from .views.isemodelview import IseModelView, IseSubmodelView
from .views.codeview import CodeView
from .views.packageview import PackageView
from .views.viewtextview import ViewTextView
from .views.eslview import EslView
from .views.stc import Stc

class MainView(View, aui.AuiNotebook):
    def __init__(self, frame, viewtype):
        self._frame = frame
        View.__init__(self, frame, viewtype)
        self._detachedPages = []

        client_size = frame.GetClientSize()
        main = aui.AuiNotebook.__init__(self, frame, -1, wx.Point(client_size.x, client_size.y), wx.Size(430, 200))

        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnMainViewPageClose)
        # Note override for OnTabMiddleUp
        # not OnTabBeginDrag/OnTabDragMotion/OnTabEndDrag

        self._programPage = IseModelView(self)
        self.AddPage(self._programPage, "Program")
        if aui.UseAUI() == aui.AUI_AGW:
            self.GetPageInfo(0).hasCloseButton = False #HACK to remove close button from main (model) page - but seems to work
        #self.GetActiveTabCtrl().Bind(wx.EVT_MOTION, self.OnTabMotion) #HACK

    def frame(self): return self._frame
    def programPage(self): return self._programPage

    def setup(self):
        pass

    def defaultPaneInfo(self):
        info = aui.AuiPaneInfo()
        info.Name("mainView")
        info.CenterPane()
        info.PaneBorder(False)
        return info

    #def OnTabMotion(self, event):
    #    if event.Dragging():
    #        tabctl = event.GetEventObject()
    #        page = tabctl.GetPointedToTab()
    #        if not isinstance(page, IseModelView):
    #            event.GetEventObject().OnMotion(event)
    #    else:
    #        event.GetEventObject().OnMotion(event)

    #def OnTabBeginDrag(self, auinotebook_event):
    #    #pageindex = auinotebook_event.GetSelection()
    #    #page = self.GetPage(pageindex)
    #    page = auinotebook_event.GetDragSource()
    #    if not isinstance(page, IseModelView):
    #        super(MainView, self).OnTabBeginDrag(auinotebook_event)
    #def OnTabDragMotion(self, auinotebook_event):
    #    #pageindex = auinotebook_event.GetSelection()
    #    #page = self.GetPage(pageindex)
    #    page = auinotebook_event.GetDragSource()
    #    if not isinstance(page, IseModelView):
    #        super(MainView, self).OnTabDragMotion(auinotebook_event)
    #def OnTabEndDrag(self, auinotebook_event):
    #    #pageindex = auinotebook_event.GetSelection()
    #    #page = self.GetPage(pageindex)
    #    page = auinotebook_event.Page
    #    if not isinstance(page, IseModelView):
    #        super(MainView, self).OnTabEndDrag(auinotebook_event)

    def OnTabMiddleUp(self, auinotebook_event):
        #pageindex = auinotebook_event.GetSelection()
        #page = self.GetPage(pageindex)
        page = auinotebook_event.Page
        if not isinstance(page, IseModelView):
            super(MainView, self).OnTabMiddleUp(auinotebook_event)

    def OnMainViewPageClose(self, auinotebook_event):
        pageindex = auinotebook_event.GetSelection()
        #ctrl = event.GetEventObject()
        #if isinstance(ctrl.GetPage(event.GetSelection()), wx.html.HtmlWindow):
        page = self.GetPage(pageindex)
        msg = ""
        if isinstance(page, IseModelView) or isinstance(page, IseSubmodelView):
            info = self._frame.application().getCanvasInfo(page) #[canvasId, model/submodel, name]
            hasSubprogramCalls = False
            if not info or info[1] == 'program':
                msg = "Cannot close the Program view"
                wx.MessageBox(msg)
                auinotebook_event.Veto()
            else:
                subprogram = self._frame.application().getModuleByName(info[2])
                if self._frame.application().program().model() and subprogram == self._frame.application().program().model():
                    #### Currently
                    msg = "Cannot close the Program's Model view"
                    wx.MessageBox(msg)
                    auinotebook_event.Veto()
                    #### TODO Alternatively ask and support removing the Model from the application but not removing (or even closing) the page - ensure canvas properties OK after
                else:
                    if info[1] == 'submodel' or info[1] == 'segment':
                        if subprogram.hasSubprogramCalls():
                            hasSubprogramCalls = True
                    if hasSubprogramCalls:
                        msg = "Are you sure you want to close this "+info[1]+" view"
                        msg += "\n(cannot remove it as it is being used - i.e. has "+info[1]+" calls)"
                        res = wx.MessageBox(msg, "Close " + self.GetPageText(pageindex),
                                            wx.YES_NO)#, self._frame)
                        if res == wx.YES:
                            self.detachPage(page)
                        auinotebook_event.Veto()
                    else:
                        msg = "Do you want to remove (delete) the "+info[1]+" from the application (Yes)"
                        msg += "\nor just close this view (No)"
                        res = wx.MessageBox(msg, "Remove " + self.GetPageText(pageindex),
                                            wx.YES_NO | wx.CANCEL)#, self._frame)
                        if res == wx.YES:
                            valid = self._frame.control().modulesControl().removeSubprogram(page.moduleId())
                            # the above will delete the page so now always
                            auinotebook_event.Veto()
                            #if not valid:
                            #    auinotebook_event.Veto()
                        elif res == wx.NO:
                            auinotebook_event.Veto()
                            self.detachPage(page)
                        #elif res == wx.CANCEL:
                        else:
                            auinotebook_event.Veto()
        elif isinstance(page, CodeView):
            code = self._frame.application().getModuleById(page.moduleId())
            hasSubprogramCalls = False
            if code and code.hasSubprogramCalls() > 0:
                hasSubprogramCalls = True
            hasPackageVariableInUse = code.hasPackageVariableInUse()
            if hasSubprogramCalls or hasPackageVariableInUse:
                why = ""
                if hasSubprogramCalls:
                    why += "has subprogram calls"
                if hasPackageVariableInUse:
                    if why: why += " and "
                    why += "has package variables in use"
                msg = "Are you sure you want to close this text subprograms window"
                msg += "\n(cannot remove it as it is being used - " + why + ")"
                res = wx.MessageBox(msg, "Close " + self.GetPageText(pageindex),
                                    wx.YES_NO)#, self._frame)
                if res == wx.YES:
                    self.detachPage(page)
                auinotebook_event.Veto()
            else:
                msg = "Do you want to remove (delete) the text subprograms from the application (Yes)"
                msg += "\nor just close this window (No)"
                res = wx.MessageBox(msg, "Remove " + self.GetPageText(pageindex),
                                    wx.YES_NO | wx.CANCEL)#, self._frame)
                if res == wx.YES:
                    valid = self._frame.control().modulesControl().removeCode(page.moduleId())
                    # the above will delete the page so now always
                    auinotebook_event.Veto()
                    #if not valid:
                    #    auinotebook_event.Veto()
                elif res == wx.NO:
                    auinotebook_event.Veto()
                    self.detachPage(page)
                #elif res == wx.CANCEL:
                else:
                    auinotebook_event.Veto()
        elif isinstance(page, PackageView):
            hasVariablesInUse = self._frame.application().packageVariableInUse(page.moduleId())
            if hasVariablesInUse:
                msg = "Are you sure you want to close this package window"
                msg += "\n(cannot remove it as it is being used - i.e. has variables in use in diagrams)"
                res = wx.MessageBox(msg, "Close " + self.GetPageText(pageindex),
                                    wx.YES_NO)#, self._frame)
                if res == wx.YES:
                    self.detachPage(page)
                auinotebook_event.Veto()
            else:
                msg = "Do you want to remove (delete) the package from the application (Yes)"
                msg += "\nor just close this window (No)"
                res = wx.MessageBox(msg, "Remove " + self.GetPageText(pageindex),
                                    wx.YES_NO | wx.CANCEL)#, self._frame)
                if res == wx.YES:
                    valid = self._frame.control().modulesControl().removePackage(page.moduleId())
                    # the above will delete the page so now always
                    auinotebook_event.Veto()
                    #if not valid:
                    #    auinotebook_event.Veto()
                elif res == wx.NO:
                    auinotebook_event.Veto()
                    self.detachPage(page)
                #elif res == wx.CANCEL:
                else:
                    auinotebook_event.Veto()
        else:
            viewname = self._frame.viewManager().stdViewName(page)
            if viewname:
                auinotebook_event.Veto()
                self._frame.viewManager().showView(viewname, False)
                self._frame.control().checkAllToggleViewItems()
            else:
                ask = True
                if isinstance(page, Stc):
                    if page.readOnly:
                        ask = False
                if ask:
                    msg = "Are you sure you want to close page"
                    res = wx.MessageBox(msg, "Close " + self.GetPageText(pageindex),
                                        wx.YES_NO)#, self._frame)
                    if res != wx.YES:
                        auinotebook_event.Veto()

    def addViewTextPage(self, tabname):
        viewTextPage = ViewTextView(self)
        self.AddPage(viewTextPage, tabname, False)
        return viewTextPage

    def addViewEslPage(self, tabname, filepath):
        for i in range(self.GetPageCount() - 1, 0, -1):
            page = self.GetPage(i)
            if isinstance(page, EslView):
                if page.filepath() == filepath:
                    self.DeletePage(i)
        viewEslPage = EslView(self)
        viewEslPage.LoadFile(filepath, True)#readonly
        self.AddPage(viewEslPage, tabname, False)
        return viewEslPage

    def addModelPage(self, tabname, addDetached=False):
        modelPage = IseModelView(self)
        modelPage.set_caption(tabname)
        modelPage.SetupCanvas(self._frame.control().iseModelDiagramDefinitions(), Config.getBlockDiagramPropertyOptions())
        if not addDetached:
            self.AddPage(modelPage, tabname, False)
        else:
            modelPage.Hide()
            self._detachedPages.append(modelPage)
        return modelPage

    def addSubprogramPage(self, tabname, addDetached=False):
        subprogramPage = IseSubmodelView(self)      #### TODO currently IseSubmodelView used for Segment too
        subprogramPage.set_caption(tabname)
        subprogramPage.SetupCanvas(self._frame.control().iseSubprogramDiagramDefinitions(), Config.getBlockDiagramPropertyOptions())
        if not addDetached:
            self.AddPage(subprogramPage, tabname, False)
        else:
            subprogramPage.Hide()
            self._detachedPages.append(subprogramPage)
        return subprogramPage

    def addCodePage(self, tabname, addDetached=False):
        codePage = CodeView(self)
        codePage.set_caption(tabname)
        if not addDetached:
            self.AddPage(codePage, tabname, False)
        else:
            self._detachedPages.append(codePage)
        return codePage

    def addPackagePage(self, tabname, addDetached=False):
        packagePage = PackageView(self, 'page')
        packagePage.set_caption(tabname)
        if not addDetached:
            self.AddPage(packagePage, tabname, False)
        else:
            packagePage.Hide()
            self._detachedPages.append(packagePage)
        return packagePage

    def detachPage(self, page, refresh=True):
        page_idx = self.GetPageIndex(page)
        self._detachedPages.append(page)
        self.RemovePage(page_idx)
        page.Hide()
        if refresh:
            self.Refresh()

    def reattachPage(self, page, refresh=True):
        self.AddPage(page, page.caption())
        page.set_caption(page.caption(), page.tooltip())
        if page in self._detachedPages:
            self._detachedPages.remove(page)
        if refresh:
            page.Refresh()

    def getPageIndex(self, page):
        result = -1
        if page in self._detachedPages: #list
            self.reattachPage(page)
        result = self.GetPageIndex(page)
        return result

    def getPageByCanvasId(self, canvasId):
        result = None
        for page in self._detachedPages: #list
            if isinstance(page, IseModelView) or isinstance(page, IseSubmodelView):
                if int(page.canvasId()) == int(canvasId):
                    result = page
                    self.reattachPage(page)
                    break
        if not result:
            nPages = self.GetPageCount()
            for i in range(nPages):
                page = self.GetPage(i)
                if isinstance(page, IseModelView) or isinstance(page, IseSubmodelView):
                    if int(page.canvasId()) == int(canvasId):
                        result = page
                        break
        return result

    def getCanvasByModuleId(self, moduleId):
        result = None
        for page in self._detachedPages: #list
            if isinstance(page, IseModelView) or isinstance(page, IseSubmodelView):
                if int(page.moduleId()) == int(moduleId):
                    result = page
                    self.reattachPage(page)
                    break
        if not result:
            nPages = self.GetPageCount()
            for i in range(nPages):
                page = self.GetPage(i)
                if isinstance(page, IseModelView) or isinstance(page, IseSubmodelView):
                    if int(page.moduleId()) == int(moduleId):
                        result = page
                        break
        return result

    def getPackageViewByModuleId(self, moduleId):
        result = None
        for page in self._detachedPages: #list
            if isinstance(page, PackageView):
                if int(page.moduleId()) == int(moduleId):
                    result = page
                    self.reattachPage(page)
                    break
        if not result:
            nPages = self.GetPageCount()
            for i in range(nPages):
                page = self.GetPage(i)
                if isinstance(page, PackageView):
                    if int(page.moduleId()) == int(moduleId):
                        result = page
                        break
        return result

    def getCodeViewByModuleId(self, moduleId):
        result = None
        for page in self._detachedPages: #list
            if isinstance(page, CodeView):
                if int(page.moduleId()) == int(moduleId):
                    result = page
                    self.reattachPage(page)
                    break
        if not result:
            nPages = self.GetPageCount()
            for i in range(nPages):
                page = self.GetPage(i)
                if isinstance(page, CodeView):
                    if int(page.moduleId()) == int(moduleId):
                        result = page
                        break
        return result

    def getModuleViewByModuleId(self, moduleId):
        result = None
        for page in self._detachedPages: #list
            if isinstance(page, ModuleView):
                if int(page.moduleId()) == int(moduleId):
                    result = page
                    self.reattachPage(page)
                    break
        if not result:
            nPages = self.GetPageCount()
            for i in range(nPages):
                page = self.GetPage(i)
                if isinstance(page, ModuleView):
                    if int(page.moduleId()) == int(moduleId):
                        result = page
                        break
        return result

    def deleteModuleViewByModuleId(self, moduleId):
        gotPage = None
        for page in self._detachedPages: #list
            if isinstance(page, ModuleView):
                if int(page.moduleId()) == int(moduleId):
                    gotPage = page
                    break
        if gotPage:
            self._detachedPages.remove(gotPage)
        else:
            got_page_idx = -1
            nPages = self.GetPageCount()
            for page_idx in range(nPages):
                page = self.GetPage(page_idx)
                if isinstance(page, ModuleView):
                    if int(page.moduleId()) == int(moduleId):
                        got_page_idx = page_idx
                        break
            if got_page_idx >= 0:
                self.DeletePage(got_page_idx)

    def resetProgramPage(self):
        self._programPage.ClearObjects()
        self._programPage.SetScale(1)
        self._programPage.set_caption("Program")
        #self._detachedPages = []

    def resetMainview(self):
        self.resetProgramPage()
        nPages = self.GetPageCount()
        if nPages > 1:
            for i in range(nPages - 1, 0, -1):
                page = self.GetPage(i)
                if page.viewtype() == 'std-page':
                    self.detachPage(page, False)
                else:
                    self.DeletePage(i)

    def setupModelCanvases(self, modelDiagramDefinitions, blockDiagramPropertyOptions):
        for page in self._detachedPages: #list
            if isinstance(page, IseModelView):
                page.SetupCanvas(modelDiagramDefinitions, blockDiagramPropertyOptions)
        nPages = self.GetPageCount()
        for page_idx in range(nPages):
            page = self.GetPage(page_idx)
            if isinstance(page, IseModelView):
                page.SetupCanvas(modelDiagramDefinitions, blockDiagramPropertyOptions)

    def clearModelCanvases(self):
        for page in self._detachedPages:  # list
            if isinstance(page, IseModelView):
                page.ClearCanvasDefinitions()
        nPages = self.GetPageCount()
        for page_idx in range(nPages):
            page = self.GetPage(page_idx)
            if isinstance(page, IseModelView):
                page.ClearCanvasDefinitions()

    def setupSubprogramCanvases(self, subprogramDiagramDefinitions, blockDiagramPropertyOptions):
        for page in self._detachedPages: #list
            if isinstance(page, IseSubmodelView):
                page.SetupCanvas(subprogramDiagramDefinitions, blockDiagramPropertyOptions)
        nPages = self.GetPageCount()
        for page_idx in range(nPages):
            page = self.GetPage(page_idx)
            if isinstance(page, IseSubmodelView):
                page.SetupCanvas(subprogramDiagramDefinitions, blockDiagramPropertyOptions)

    def clearSubprogramCanvases(self):
        for page in self._detachedPages:  # list
            if isinstance(page, IseSubmodelView):
                page.ClearCanvasDefinitions()
        nPages = self.GetPageCount()
        for page_idx in range(nPages):
            page = self.GetPage(page_idx)
            if isinstance(page, IseSubmodelView): #### TODO IseSubprogram-ise (or better - currently IseSubmodelView is for Segment too
                page.ClearCanvasDefinitions()

    def setPage(self, page):
        currentPage = self.GetCurrentPage()
        if currentPage != page:
            pageIndex = self.GetPageIndex(page)
            if pageIndex != wx.NOT_FOUND:
                self.SetSelection(pageIndex)

    def setMode(self, mode):
        View.setMode(self, mode)
        for pageIx in range(self.GetPageCount()):
            page = self.GetPage(pageIx)
            page.setMode(mode)

    def SetSelection(self, pageindex):
        page = self.GetPage(pageindex)
        if hasattr(page, "updateView"):
            page.updateView()
        aui.AuiNotebook.SetSelection(self, pageindex)

    def onCharHook(self, evt):
        handled = False
        keyCode = evt.GetKeyCode()
        modifiers = evt.GetModifiers()
        ctrlOnly = modifiers == wx.MOD_CONTROL
        ctrlNShift = modifiers == (wx.MOD_CONTROL | wx.MOD_SHIFT)
        if keyCode == wx.WXK_TAB and (ctrlOnly or ctrlNShift):  # change tab
            nPages = self.GetPageCount()
            if nPages > 1:
                pageIx = self.GetSelection()
                if ctrlOnly:
                    pageIx += 1
                    if pageIx > nPages - 1:
                        pageIx = 0
                elif ctrlNShift:
                    pageIx -= 1
                    if pageIx < 0:
                        pageIx = nPages - 1
                self.SetSelection(pageIx)
            handled = True
        elif ctrlNShift and (keyCode == wx.WXK_PAGEUP or keyCode == wx.WXK_PAGEDOWN):  # move tab
            nPages = self.GetPageCount()
            if nPages > 2: # we dont shift the 0th tab
                pageIx = self.GetSelection()
                if keyCode == wx.WXK_PAGEDOWN:
                    if pageIx > 0 and pageIx + 1 < nPages:
                        page = self.GetPage(pageIx)
                        did = self.RemovePage(pageIx)
                        if did:
                            self.InsertPage(pageIx + 1, page, page.caption(), True)
                elif keyCode == wx.WXK_PAGEUP:
                    if pageIx > 1:
                        page = self.GetPage(pageIx)
                        did = self.RemovePage(pageIx)
                        if did:
                            self.InsertPage(pageIx - 1, page, page.caption(), True)
            handled = True
        else:
            evt.Skip(True)
        return handled

#poss useful:
#bool AddPage(wxWindow* page, const wxString& caption, bool select = false, const wxBitmap& bitmap = wxNullBitmap)
#bool InsertPage(size_t page_idx, wxWindow* page, const wxString& caption, bool select = false, const wxBitmap& bitmap = wxNullBitmap)
#bool DeletePage(size_t page)
#??bool RemovePage(size_t page) - Removes a page, without deleting the window pointer ??
#size_t GetPageCount() const
#wxWindow* GetPage(size_t page_idx) const
#int GetPageIndex(wxWindow* page_wnd) const [else wxNOT_FOUND]
#wxString GetPageText(size_t page) const - means tab label
#bool SetPageText(size_t page, const wxString& text)
#int GetSelection() const - current page
#EVT_AUINOTEBOOK_PAGE_CHANGED(id, func):
# func takes a wxAuiNotebookEvent (has GetSelection())
