#! /usr/bin/python

import wx
import wx.aui as wxaui
import wx.lib.agw.aui as agwaui
import six

from .config import Config

AUI_AGW = 1
AUI_WX = 2
_AUI_SET = 0
_AUI_BUGS = 0
wxPythonVersionStr = wx.__version__
if wxPythonVersionStr.startswith("4.1.1"):
    _AUI_BUGS = 1

# Export aui classed
AuiPaneInfo = None
AuiToolBar = None
AuiNotebook = None
AuiManager = None
# Export aui events (used by mainview and control)
EVT_AUINOTEBOOK_PAGE_CLOSE = None
EVT_AUINOTEBOOK_PAGE_CHANGED = None
EVT_AUI_PANE_CLOSE = None

def SetUseAUI(aui_type):
    global _AUI_SET
    global AuiPaneInfo, AuiToolBar, AuiNotebook, AuiManager
    global EVT_AUINOTEBOOK_PAGE_CLOSE, EVT_AUINOTEBOOK_PAGE_CHANGED, EVT_AUI_PANE_CLOSE
    if _AUI_SET != 0:
        raise Exception("SetUseAUI has already been set")
    else:
        _AUI_SET = aui_type
        if _AUI_SET == AUI_AGW:
            AuiPaneInfo = _agwAuiPaneInfo
            AuiToolBar = _agwAuiToolBar
            AuiNotebook = _agwAuiNotebook
            AuiManager = _agwAuiManager
            EVT_AUINOTEBOOK_PAGE_CLOSE = agwaui.EVT_AUINOTEBOOK_PAGE_CLOSE
            EVT_AUINOTEBOOK_PAGE_CHANGED = agwaui.EVT_AUINOTEBOOK_PAGE_CHANGED
            EVT_AUI_PANE_CLOSE = agwaui.EVT_AUI_PANE_CLOSE

        elif _AUI_SET == AUI_WX:
            AuiPaneInfo = _wxAuiPaneInfo
            AuiToolBar = _wxAuiToolBar
            AuiNotebook = _wxAuiNotebook
            AuiManager = _wxAuiManager
            EVT_AUINOTEBOOK_PAGE_CLOSE = wxaui.EVT_AUINOTEBOOK_PAGE_CLOSE
            EVT_AUINOTEBOOK_PAGE_CHANGED = wxaui.EVT_AUINOTEBOOK_PAGE_CHANGED
            EVT_AUI_PANE_CLOSE = wxaui.EVT_AUI_PANE_CLOSE
        else:
            raise Exception("SetUseAUI given invalid setting")

def UseAUI():
    global _AUI_SET
    return _AUI_SET

# AuiPaneInfo
class _agwAuiPaneInfo(agwaui.AuiPaneInfo):
    def __init__(self):
        agwaui.AuiPaneInfo.__init__(self)

class _wxAuiPaneInfo(wxaui.AuiPaneInfo):
    def __init__(self):
        wxaui.AuiPaneInfo.__init__(self)

# AuiToolBar
class _agwAuiToolBar(agwaui.AuiToolBar):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
        style = 0
        agwStyle = agwaui.AUI_TB_DEFAULT_STYLE | agwaui.AUI_TB_OVERFLOW
        agwaui.AuiToolBar.__init__(self, parent, id, pos, size, style, agwStyle)

class _wxAuiToolBar(wxaui.AuiToolBar):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
        style = wxaui.AUI_TB_DEFAULT_STYLE | wxaui.AUI_TB_OVERFLOW
        wxaui.AuiToolBar.__init__(self, parent, id, pos, size, style)

# AuiNotebook
class _agwAuiNotebook(agwaui.AuiNotebook):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
        style = wx.NO_BORDER
        agwStyle = agwaui.AUI_NB_DEFAULT_STYLE
        #agwStyle -= agwaui.AUI_NB_TAB_SPLIT
        #agwStyle -= agwaui.AUI_NB_DRAW_DND_TAB # helps to see when move tab or split
        agwStyle |= agwaui.AUI_NB_TAB_EXTERNAL_MOVE
        #agwStyle |= agwaui.AUI_NB_TAB_FLOAT # yuck - don't think this works nicely - can it be made to
        #agwStyle |= agwaui.AUI_NB_HIDE_ON_SINGLE_TAB # dont ever hide
        ##agwStyle |= agwaui.AUI_NB_SUB_NOTEBOOK #?experiment
        agwStyle |= agwaui.AUI_NB_WINDOWLIST_BUTTON
        agwStyle |= agwaui.AUI_NB_CLOSE_BUTTON
        #agwStyle |= agwaui.AUI_NB_TAB_FIXED_WIDTH
        name = "AuiNotebook"
        agwaui.AuiNotebook.__init__(self, parent, id, pos, size, style, agwStyle, name)
        tabArt = agwaui.AuiDefaultTabArt()
        self.SetArtProvider(tabArt)

class _wxAuiNotebook(wxaui.AuiNotebook):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
        style = wx.NO_BORDER
        style |= wxaui.AUI_NB_DEFAULT_STYLE
        style |= wxaui.AUI_NB_TAB_EXTERNAL_MOVE
        style |= wxaui.AUI_NB_WINDOWLIST_BUTTON
        style |= wxaui.AUI_NB_CLOSE_BUTTON
        wxaui.AuiNotebook.__init__(self, parent, id, pos, size, style)
        tabArt = wxaui.AuiDefaultTabArt()
        self.SetArtProvider(tabArt)

# AuiManager
class _agwAuiManager(agwaui.AuiManager):
    def __init__(self, managed_window=None):  # vs self, managed_wnd=None, flags=None
        #AUI_MGR_DEFAULT = AUI_MGR_ALLOW_FLOATING(1) | AUI_MGR_TRANSPARENT_HINT(8) | AUI_MGR_HINT_FADE(64) | AUI_MGR_NO_VENETIAN_BLINDS_FADE(128)
        agwFlags = agwaui.AUI_MGR_ALLOW_FLOATING
        agwFlags |= agwaui.AUI_MGR_VENETIAN_BLINDS_HINT | agwaui.AUI_MGR_NO_VENETIAN_BLINDS_FADE
        agwFlags |= agwaui.AUI_MGR_LIVE_RESIZE
        #agwFlags |= agwaui.AUI_MGR_ALLOW_ACTIVE_PANE - doesnt work as I would like for properties
        if Config.getBool('Advanced/AUIAeroStyle'):
            agwFlags |= agwaui.AUI_MGR_AERO_DOCKING_GUIDES
        # agwFlags |= agwaui.AUI_MGR_WHIDBEY_DOCKING_GUIDES
        agwaui.AuiManager.__init__(self, managed_window, agwFlags)

    def _getNotebookForId(self, notebook_id):
        notebook = None
        # The notebook_id would seem to be the index into autoNotebooks
        autoNotebooks = self.GetNotebooks()
        if notebook_id >= 0 and notebook_id < len(autoNotebooks):
            notebook = autoNotebooks[notebook_id]
        return notebook

    def _getNotebookPageForPaneName(self, notebook, paneName):
        notebookPage = None
        nPages = notebook.GetPageCount()
        for i in range(nPages):
            page = notebook.GetPage(i)
            pane = self.GetPane(page)
            if pane and pane.name == paneName:
                notebookPage = page
                break
        return notebookPage

    def getBasePanes(self, paneinfo):
        panes = []
        hasNotebook = paneinfo.HasNotebook()
        notebook_id = paneinfo.notebook_id
        isNotebookControl = paneinfo.IsNotebookControl()
        if isNotebookControl:
            notebook = self._getNotebookForId(notebook_id)
            if notebook:
                nPages = notebook.GetPageCount()
                for i in range(nPages):
                    page = notebook.GetPage(i)
                    pane = self.GetPane(page)
                    panes.append(pane)
        else:
            panes.append(paneinfo)
        return panes

    def checkNotebookPaneShow(self, paneinfo, showing):
        notebook_id = paneinfo.notebook_id
        #print(">checkNotebookPaneShow paneinfo.name=%s .state=%d .notebook_id=%d showing=%d" % (paneinfo.name, paneinfo.state, notebook_id, showing))
        if paneinfo.IsNotebookControl():
            paneinfo = paneinfo
            pass
        elif paneinfo.IsNotebookPage():
            notebook = self._getNotebookForId(notebook_id)
            if notebook:
                notebook_pane = self.GetPane(notebook)
                if showing and not notebook_pane.IsShown():
                    notebook_pane.Show(showing)
                page_idx = notebook.GetPageIndex(paneinfo.window)
                notebook.HidePage(page_idx, not showing)
                if showing:
                    notebook.SetSelection(page_idx)

    if _AUI_BUGS == 1:
        # Bug fix 1: Crashes when try to float off a docked pane.
        # See actual fix in _agwAuiCenterDockingGuide CreateShapesWithStyle.
        def CreateGuideWindows(self):
            """ Creates the VS2005 HUD guide windows. """

            self.DestroyGuideWindows()

            self._guides.append(agwaui.AuiDockingGuideInfo().Left().
                                Host(agwaui.AuiSingleDockingGuide(self._frame, wx.LEFT)))
            self._guides.append(agwaui.AuiDockingGuideInfo().Top().
                                Host(agwaui.AuiSingleDockingGuide(self._frame, wx.TOP)))
            self._guides.append(agwaui.AuiDockingGuideInfo().Right().
                                Host(agwaui.AuiSingleDockingGuide(self._frame, wx.RIGHT)))
            self._guides.append(agwaui.AuiDockingGuideInfo().Bottom().
                                Host(agwaui.AuiSingleDockingGuide(self._frame, wx.BOTTOM)))
            self._guides.append(agwaui.AuiDockingGuideInfo().Centre().
                                Host(_agwAuiCenterDockingGuide(self._frame)))

    #END if _AUI_BUGS == 1

    if _AUI_BUGS == 1:
        # Bug fix 2: When drop pane onto centre guide get two added tabbed panes - in Windows.
        def UpdateNotebook(self):
            """ Updates the automatic :class:`~wx.lib.agw.aui.auibook.AuiNotebook` in the layout (if any exists). """

            # Workout how many notebooks we need.
            max_notebook = -1

            # destroy floating panes which have been
            # redocked or are becoming non-floating
            for paneInfo in self._panes:
                if max_notebook < paneInfo.notebook_id:
                    max_notebook = paneInfo.notebook_id

            # We are the master of our domain
            extra_notebook = len(self._notebooks)
            max_notebook += 1

            for i in range(extra_notebook, max_notebook):
                self.CreateNotebook()

            # Remove pages from notebooks that no-longer belong there ...
            for nb, notebook in enumerate(self._notebooks):
                pages = notebook.GetPageCount()
                pageCounter, allPages = 0, pages

                # Check each tab ...
                for page in range(pages):

                    if page >= allPages:
                        break

                    window = notebook.GetPage(pageCounter)
                    paneInfo = self.GetPane(window)
                    if paneInfo.IsOk() and paneInfo.notebook_id != nb:
                        notebook.RemovePage(pageCounter)
                        window.Hide()
                        window.Reparent(self._frame)
                        pageCounter -= 1
                        allPages -= 1
                        paneInfo.Direction(self.GetPane(notebook).dock_direction)

                    pageCounter += 1

                notebook.DoSizing()

            # Add notebook pages that aren't there already...
            pages_and_panes = {}
            for paneInfo in self._panes:
                if paneInfo.IsNotebookPage():

                    title = (paneInfo.caption == "" and [paneInfo.name] or [paneInfo.caption])[0]

                    notebook = self._notebooks[paneInfo.notebook_id]
                    page_id = notebook.GetPageIndex(paneInfo.window)

                    if page_id < 0:

                        if paneInfo.notebook_id not in pages_and_panes:
                            pages_and_panes[paneInfo.notebook_id] = []
                        pages_and_panes[paneInfo.notebook_id].append(paneInfo)

                    # Update title and icon ...
                    else:

                        notebook.SetPageText(page_id, title)
                        notebook.SetPageBitmap(page_id, paneInfo.icon)

                    notebook.DoSizing()

                # Wire-up newly created notebooks
                elif paneInfo.IsNotebookControl() and not paneInfo.window:
                    paneInfo.window = self._notebooks[paneInfo.notebook_id]

            for notebook_id, pnp in six.iteritems(pages_and_panes):
                # sort the panes with dock_pos
                sorted_pnp = sorted(pnp, key=lambda pane: pane.dock_pos)
                notebook = self._notebooks[notebook_id]
                for pane in sorted_pnp:

                    # FIX: Check pane not already in notebook...
                    alreadyIn = False
                    page = self._getNotebookPageForPaneName(notebook, pane.name)
                    if page is not None:
                        alreadyIn = True
                    if not alreadyIn:
                        # ENDFIX - we can add the page as its not already in
                        title = (pane.caption == "" and [pane.name] or [pane.caption])[0]
                        pane.window.Reparent(notebook)
                        notebook.AddPage(pane.window, title, True, pane.icon)
                notebook.DoSizing()

            # Delete empty notebooks, and convert notebooks with 1 page to
            # normal panes...
            remap_ids = [-1]*len(self._notebooks)
            nb_idx = 0

            for nb, notebook in enumerate(self._notebooks):
                if notebook.GetPageCount() == 1:

                    # Convert notebook page to pane...
                    window = notebook.GetPage(0)
                    child_pane = self.GetPane(window)
                    notebook_pane = self.GetPane(notebook)
                    if child_pane.IsOk() and notebook_pane.IsOk():

                        child_pane.SetDockPos(notebook_pane)
                        child_pane.Show(notebook_pane.IsShown())
                        child_pane.window.Hide()
                        child_pane.window.Reparent(self._frame)
                        child_pane.frame = None
                        child_pane.notebook_id = -1
                        if notebook_pane.IsFloating():
                            child_pane.Float()

                        self.DetachPane(notebook)

                        notebook.RemovePage(0)
                        notebook.Destroy()

                    else:

                        raise Exception("Odd notebook docking")

                elif notebook.GetPageCount() == 0:

                    self.DetachPane(notebook)
                    notebook.Destroy()

                else:

                    self._notebooks[nb_idx] = notebook

                    # It's a keeper.
                    remap_ids[nb] = nb_idx
                    nb_idx += 1

            # Apply remap...
            nb_count = len(self._notebooks)

            if nb_count != nb_idx:

                self._notebooks = self._notebooks[0:nb_idx]
                for p in self._panes:
                    if p.notebook_id >= 0:
                        p.notebook_id = remap_ids[p.notebook_id]
                        if p.IsNotebookControl():
                            p.SetNameFromNotebookId()

            # Make sure buttons are correct ...
            for notebook in self._notebooks:
                want_max = True
                want_min = True
                want_close = True

                pages = notebook.GetPageCount()
                for page in range(pages):

                    win = notebook.GetPage(page)
                    pane = self.GetPane(win)
                    if pane.IsOk():

                        if not pane.HasCloseButton():
                            want_close = False
                        if not pane.HasMaximizeButton():
                            want_max = False
                        if not pane.HasMinimizeButton():
                            want_min = False

                notebook_pane = self.GetPane(notebook)
                if notebook_pane.IsOk():
                    if notebook_pane.HasMinimizeButton() != want_min:
                        if want_min:
                            button = agwaui.AuiPaneButton(agwaui.AUI_BUTTON_MINIMIZE)
                            notebook_pane.state |= AuiPaneInfo.buttonMinimize
                            notebook_pane.buttons.append(button)

                        # todo: remove min/max

                    if notebook_pane.HasMaximizeButton() != want_max:
                        if want_max:
                            button = agwaui.AuiPaneButton(agwaui.AUI_BUTTON_MAXIMIZE_RESTORE)
                            notebook_pane.state |= AuiPaneInfo.buttonMaximize
                            notebook_pane.buttons.append(button)

                        # todo: remove min/max

                    if notebook_pane.HasCloseButton() != want_close:
                        if want_close:
                            button = agwaui.AuiPaneButton(agwaui.AUI_BUTTON_CLOSE)
                            notebook_pane.state |= AuiPaneInfo.buttonClose
                            notebook_pane.buttons.append(button)

                        # todo: remove close
    #END if _AUI_BUGS == 1

class _wxAuiManager(wxaui.AuiManager):
    def __init__(self, managed_window=None): #vs self, managed_wnd=None, flags=None
        #wxaui.AUI_MGR_DEFAULT(201)=AUI_MGR_ALLOW_FLOATING(1)|AUI_MGR_TRANSPARENT_HINT(8)|AUI_MGR_HINT_FADE(64)|AUI_MGR_NO_VENETIAN_BLINDS_FADE(128)
        flags = wxaui.AUI_MGR_ALLOW_FLOATING
        flags |= wxaui.AUI_MGR_VENETIAN_BLINDS_HINT | wxaui.AUI_MGR_NO_VENETIAN_BLINDS_FADE
        flags |= wxaui.AUI_MGR_LIVE_RESIZE
        #flags |= wxaui.AUI_MGR_ALLOW_ACTIVE_PANE - doesnt work as I would like for properties
        wxaui.AuiManager.__init__(self, managed_window, flags)

    def checkNotebookPaneShow(self, paneinfo, showing): # wx aui doesn't have combined (notebouk) panes
        pass

class _agwAuiCenterDockingGuide(agwaui.AuiCenterDockingGuide):
    """ A docking guide window for multiple docking hint (diamond-shaped HUD). """

    def __init__(self, parent):
        agwaui.AuiCenterDockingGuide.__init__(self, parent)

    if _AUI_BUGS == 1:
        def CreateShapesWithStyle(self):
            """ Creates the docking guide window shape based on which docking bitmaps are used. """

            useAero = (agwaui.GetManager(self.GetParent()).GetAGWFlags() & agwaui.AUI_MGR_AERO_DOCKING_GUIDES) != 0
            useWhidbey = (agwaui.GetManager(self.GetParent()).GetAGWFlags() & agwaui.AUI_MGR_WHIDBEY_DOCKING_GUIDES) != 0

            self._useAero = 0
            if useAero:
                self._useAero = 1
            elif useWhidbey:
                self._useAero = 2

            if useAero:
                sizeX, sizeY = agwaui.aeroguideSizeX, agwaui.aeroguideSizeY
            elif useWhidbey:
                sizeX, sizeY = agwaui.whidbeySizeX, agwaui.whidbeySizeY
            else:
                sizeX, sizeY = agwaui.guideSizeX, agwaui.guideSizeY

            rectLeft = wx.Rect(0, sizeY, sizeY, sizeX)
            rectTop = wx.Rect(sizeY, 0, sizeX, sizeY)
            rectRight = wx.Rect(sizeY+sizeX, sizeY, sizeY, sizeX)
            rectBottom = wx.Rect(sizeY, sizeX + sizeY, sizeX, sizeY)
            rectCenter = wx.Rect(sizeY, sizeY, sizeX, sizeX)

            if not self._useAero:

                self.targetLeft = agwaui.AuiDockingGuideWindow(self, rectLeft, wx.LEFT, True, useAero)
                self.targetTop = agwaui.AuiDockingGuideWindow(self, rectTop, wx.TOP, True, useAero)
                self.targetRight = agwaui.AuiDockingGuideWindow(self, rectRight, wx.RIGHT, True, useAero)
                self.targetBottom = agwaui.AuiDockingGuideWindow(self, rectBottom, wx.BOTTOM, True, useAero)
                self.targetCenter = agwaui.AuiDockingGuideWindow(self, rectCenter, wx.CENTER, True, useAero)


                # top-left diamond
                tld = [wx.Point(rectTop.x, rectTop.y+rectTop.height-8),
                       wx.Point(rectLeft.x+rectLeft.width-8, rectLeft.y),
                       rectTop.GetBottomLeft()]
                # bottom-left diamond
                bld = [wx.Point(rectLeft.x+rectLeft.width-8, rectLeft.y+rectLeft.height),
                       wx.Point(rectBottom.x, rectBottom.y+8),
                       rectBottom.GetTopLeft()]
                # top-right diamond
                trd = [wx.Point(rectTop.x+rectTop.width, rectTop.y+rectTop.height-8),
                       wx.Point(rectRight.x+8, rectRight.y),
                       rectRight.GetTopLeft()]
                # bottom-right diamond
                brd = [wx.Point(rectRight.x+8, rectRight.y+rectRight.height),
                       wx.Point(rectBottom.x+rectBottom.width, rectBottom.y+8),
                       rectBottom.GetTopRight()]

                self._triangles = [tld[0:2], bld[0:2],
                                   [wx.Point(rectTop.x+rectTop.width-1, rectTop.y+rectTop.height-8),
                                    wx.Point(rectRight.x+7, rectRight.y)],
                                   [wx.Point(rectRight.x+7, rectRight.y+rectRight.height),
                                    wx.Point(rectBottom.x+rectBottom.width-1, rectBottom.y+8)]]

                region = wx.Region()
                region.Union(rectLeft)
                region.Union(rectTop)
                region.Union(rectRight)
                region.Union(rectBottom)
                region.Union(rectCenter)
                # see what happens here - cant make a region from a list of points
                #reg = wx.Region(tld)
                #region.Union(reg)
                #region.Union(wx.Region(bld))
                #region.Union(wx.Region(trd))
                #region.Union(wx.Region(brd))

            elif useAero:

                self._aeroBmp = self.getPyEmbeddedImageBitmap(agwaui.aero_dock_pane)
                region = wx.Region(self._aeroBmp)

                self._allAeroBmps = [self.getPyEmbeddedImageBitmap(agwaui.aero_dock_pane_left), self.getPyEmbeddedImageBitmap(agwaui.aero_dock_pane_top),
                                     self.getPyEmbeddedImageBitmap(agwaui.aero_dock_pane_right), self.getPyEmbeddedImageBitmap(agwaui.aero_dock_pane_bottom),
                                     self.getPyEmbeddedImageBitmap(agwaui.aero_dock_pane_center), self.getPyEmbeddedImageBitmap(agwaui.aero_dock_pane)]
                self._deniedBitmap = self.getPyEmbeddedImageBitmap(agwaui.aero_denied)
                self._aeroRects = [rectLeft, rectTop, rectRight, rectBottom, rectCenter]
                self._valid = True

            elif useWhidbey:

                self._aeroBmp = self.getPyEmbeddedImageBitmap(agwaui.whidbey_dock_pane)
                region = wx.Region(self._aeroBmp)

                self._allAeroBmps = [self.getPyEmbeddedImageBitmap(agwaui.whidbey_dock_pane_left), self.getPyEmbeddedImageBitmap(agwaui.whidbey_dock_pane_top),
                                     self.getPyEmbeddedImageBitmap(agwaui.whidbey_dock_pane_right), self.getPyEmbeddedImageBitmap(agwaui.whidbey_dock_pane_bottom),
                                     self.getPyEmbeddedImageBitmap(agwaui.whidbey_dock_pane_center), self.getPyEmbeddedImageBitmap(agwaui.whidbey_dock_pane)]
                self._deniedBitmap = self.getPyEmbeddedImageBitmap(agwaui.whidbey_denied)
                self._aeroRects = [rectLeft, rectTop, rectRight, rectBottom, rectCenter]
                self._valid = True


            self.region = region
    #END if _AUI_BUGS == 1

    if _AUI_BUGS == 1:
        # Bug fix 3: Transparent parts of Aero guide bitmaps show old (left over) bitmap bits - in Windows.
        # This puts gray where the alpha is. Strictly not needed for Linux as that put white there, but now it's also gray.
        def getPyEmbeddedImageBitmap(self, embeddedImage):
            image = embeddedImage.GetImage()
            image.ConvertAlphaToMask(200,200,200) # light gray
            bitmap = wx.Bitmap(image)
            bitmap.SetMask(None)
            return bitmap
    #END if _AUI_BUGS == 1
