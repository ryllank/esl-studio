#! /usr/bin/python

# aboutdlg.py

import wx
from wx import xrc

from .. import utils as Utils
from ..general import APP_NAME, APPLICATION_VERSION_STRING, APPLICATION_BUILD_DATE, APP_COPYRIGHT, APP_WEBSITE, APP_DESCRIPTION

class AboutDlg(wx.Dialog):

    _instance = None

    @classmethod
    def Instance(cls, parent):
        if cls._instance == None:
            cls._instance = cls(parent)
        return cls._instance

    def __init__(self, parent):
        wx.Dialog.__init__(self)
        self._parent = parent
        resfile = Utils.resourceFile("aboutdlg.xrc")
        if resfile:
            res = xrc.XmlResource(resfile)
            if res:
                res.LoadDialog(self, parent, "AboutDlg")
                self.setup()

    def setup(self):
        self._btnClose = xrc.XRCCTRL(self, "btnClose")
        self.Bind(wx.EVT_BUTTON, self.onCloseClicked, self._btnClose)
        self._togLicence = xrc.XRCCTRL(self, "togLicence")
        self.Bind(wx.EVT_TOGGLEBUTTON, self.onTogLicenceClicked, self._togLicence)
        self._bmpIcon = xrc.XRCCTRL(self, "bmpIcon")
        file = Utils.resourceFile("esl-studio-32x32.ico")
        icon = wx.Icon(file)
        self._bmpIcon.SetIcon(icon)
        self._lblNameNVersion = xrc.XRCCTRL(self, "lblNameNVersion")
        # Make text bold
        font = self._lblNameNVersion.GetFont()
        font = font.Bold()
        self._lblNameNVersion.SetFont(font)
        nameNVersion = APP_NAME + " v"+APPLICATION_VERSION_STRING
        self._lblNameNVersion.SetLabel(nameNVersion)
        self._pnlMain = xrc.XRCCTRL(self, "pnlMain")
        self._lblDescription = xrc.XRCCTRL(self, "lblDescription")
        self._lblDescription.SetLabel(APP_DESCRIPTION)
        self._lnkAppWebsite = xrc.XRCCTRL(self, "lnkAppWebsite")
        self._lnkAppWebsite.SetLabel(APP_WEBSITE)
        self._lblCopyright = xrc.XRCCTRL(self, "lblCopyright")
        self._lblBuildDate = xrc.XRCCTRL(self, "lblBuildDate")
        # Reduce text size
        font = self._lblCopyright.GetFont()
        font = font.Smaller()
        self._lblCopyright.SetFont(font)
        self._lblCopyright.SetLabel(APP_COPYRIGHT)
        font = self._lblBuildDate.GetFont()
        font = font.Smaller()
        self._lblBuildDate.SetFont(font)
        buildDate = APPLICATION_BUILD_DATE
        if buildDate:
            buildDate = "Build date: " + buildDate
        else:
            buildDate = "Development build"
        self._lblBuildDate.SetLabel(buildDate)
        self._pnlLicence = xrc.XRCCTRL(self, "pnlLicence")
        self._lblLicenceTxt = xrc.XRCCTRL(self, "lblLicenceTxt")
        # Reduce text size
        font = self._lblLicenceTxt.GetFont()
        font = font.Smaller()
        self._lblLicenceTxt.SetFont(font)
        file = Utils.docFile("licence.txt")
        f = None
        try:
            f = open(file, 'r')
        except Exception:
            pass
        if f:
            licenseTxt = f.read()
            f.close()
            self._lblLicenceTxt.SetLabel(licenseTxt)

    def closeDlg(self):
        self.EndModal(wx.ID_CANCEL)
        return True

    def onCloseClicked(self, event):
        self.EndModal(wx.ID_OK)

    def onTogLicenceClicked(self, event):
        if self._pnlMain.IsShown():
            self._pnlMain.Hide()
            self._pnlLicence.Show()
        else:
            self._pnlMain.Show()
            self._pnlLicence.Hide()
        self.Layout()
        #event.Skip()

class MyApp(wx.App):
    def OnInit(self):
        self.dialog = AboutDlg(None)
        self.SetTopWindow(self.dialog)
        self.dialog.ShowModal()
        self.dialog.Destroy()
        return True

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
