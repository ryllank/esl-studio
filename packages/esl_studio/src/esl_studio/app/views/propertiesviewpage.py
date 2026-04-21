#! /usr/bin/python

# app.views.propertiesviewpage.py

class PropertiesViewPage():
    def __init__(self, propertiesView):
        self._propertiesView = propertiesView
        self._mode = "editing"

    def propertiesView(self):
        return self._propertiesView

    def mode(self):
        return self._mode

    def setMode(self, mode): # override this
        print("PropertiesViewPage.setMode should be overriden")
        raise Exception("PropertiesViewPage.setMode should be overriden")
        pass

    def checkMode(self): # call this at the end of setup (for editing)
        mode = self._propertiesView.mode()
        if mode != "editing":
            self.setMode(mode)

    def clearViewPage(self):        # Override this in PropertiesViewPages that need to clear something for new application (such as property grids' properties).
        pass
