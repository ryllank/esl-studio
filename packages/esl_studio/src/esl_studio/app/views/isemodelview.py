#! /usr/bin/python

import esl_diagram.canvas as canv

from .view import ModuleView

class IseModelView(ModuleView, canv.Canvas):
    def __init__(self, parent):
        canv.Canvas.__init__(self, parent)
        ModuleView.__init__(self, parent, 'page')
        self.detectToCheckSelectedInMainView(self, noChildFocus=True)

    #def setup(self, isecanvasdefinitionsfile):
    #    canv.Canvas.SetupCanvas(self, isecanvasdefinitionsfile)

    def setMode(self, mode):
        ModuleView.setMode(self, mode)
        self.SetMode(mode)


class IseSubmodelView(ModuleView, canv.Canvas):
    def __init__(self, parent):
        canv.Canvas.__init__(self, parent)
        ModuleView.__init__(self, parent, 'page')
        self.detectToCheckSelectedInMainView(self, noChildFocus=True)

    #def setup(self, isecanvasdefinitionsfile):
    #    canv.Canvas.SetupCanvas(self, isecanvasdefinitionsfile)

    def setMode(self, mode):
        ModuleView.setMode(self, mode)
        self.SetMode(mode)
