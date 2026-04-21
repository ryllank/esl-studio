#! /usr/bin/python

from .view import ModuleView
from .eslview import EslView

class CodeView(ModuleView, EslView):
    def __init__(self, parent):
        EslView.__init__(self, parent)
        ModuleView.__init__(self, parent, 'page')
        self.setText('')

    def setMode(self, mode):
        ModuleView.setMode(self, mode)
        readOnly = self.readOnly or mode == "browsing"
        self.SetReadOnly(readOnly)

# Use .LoadFile(filepath, readonly=True) to load a file
# Use .SetValue(text) to set text
