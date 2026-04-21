#! /usr/bin/python

import wx
import wx.propgrid as wxpg

from .. import utils as Utils

from ..application.applicationtypes import CODETYPES
from ..propertiescontrol import PropertyRefSeparator, PropertyChildSeparator
from .propertiesviewpage import PropertiesViewPage
from .properties.coreproperties import CompoundProperty
from .properties.longstringproperty import LongStringProperty

class CodeFileProperty(wxpg.FileProperty):
    def __init__(self, label, name, value):
        wxpg.FileProperty.__init__(self, label, name, value)

    def setValue(self, name, value):
        self.SetName(name)
        self.SetValue(value)

    def ValueToString(self, value, argFlags=0):
        filename = value
        filename = Utils.relativise(filename)
        if filename:
            if filename == value:
                filename = Utils.environmentalise(filename)
        return filename

class PropertiesViewCode(PropertiesViewPage):
    def __init__(self, propertiesView):
        PropertiesViewPage.__init__(self, propertiesView)
        self._application = self._propertiesView.application()
        self._page = self._propertiesView.page()
        self._pgm = self._propertiesView.pgm()
        self._pagePropertyId = ""
        # properties
        self._description = None
        self._codeType = None
        self._file = None
        self._ESL = None

    def page(self): return self._page
    def pgm(self): return self._pgm

    def setMode(self, mode):
        properties = [ #self._eslname self._codeType - always disabled
            self._description,
            self._file,
            self._ESL
        ]
        for property in properties:
            if property:
                if isinstance(property, CompoundProperty):
                    property.enableWithChildren(mode == "editing")
                else:
                    property.Enable(mode == "editing")

    def resetPropertiesForNewApplication(self):
        # Ensure first item called after this (for new application) is treated as a new item
        self._pagePropertyId = ""

    def setCodePropertyPage(self, pageType, propertyId, headerText):
        self._propertiesView.clearPropertyPage(headerText, pageType, 'module-property', int(propertyId), propertyId)

        newItem = propertyId != self._pagePropertyId
        self._pagePropertyId = propertyId

        self._propertiesView.showParameterButtons(False)
        moduleId = self._propertiesView.moduleId()
        module = self._application.getModuleById(moduleId)
        moduleType = module.moduleType()
        codeType = module.codeType()
        description = module.description()
        ref = 'M' + PropertyRefSeparator +str(moduleId) + PropertyChildSeparator

        if not self._description:
            self._description = wxpg.StringProperty("Description", ref + 'description', value=description)
            self._description.SetHelpString("Description of this module" +
                               "\nNote: This is not used in generated ESL)")
            self._page.Append(self._description)
        else:
            self._description.SetName(ref + 'description')
            self._description.SetValue(description)

        if not self._codeType:
            self._codeType = wxpg.EnumProperty("Code Type", ref + "codeType", CODETYPES, [0,1,2], CODETYPES.index(codeType))
            self._codeType.SetHelpString("Code Type - \"text\" for an internal textual subprograms," +
                               "\n - \"file\" for a textual subprograms read from a file")
            self._page.Append(self._codeType)
        else:
            self._codeType.SetName(ref + 'codeType')
            self._codeType.SetValue(CODETYPES.index(codeType))
        self._codeType.Enable(False)

        if codeType == 'file':
            fileValue = module.file()
            if not self._file:
                self._file = CodeFileProperty("File", ref + "file", fileValue)
                self._file.SetHelpString("ESL file containing the submodel source code")
                self._file.SetAttribute(wxpg.PG_FILE_WILDCARD, "ESL files (*.esl)|*.esl|All files (*.*)|*.*" )
                self._file.SetAttribute(wxpg.PG_FILE_DIALOG_TITLE, "Select an ESL submodel file" )
                #self._page.SetPropertyReadOnly(prop, True, wxpg.PG_DONT_RECURSE) #- wont browse if have this
                self._page.Append(self._file)
            else:
                self._file.setValue(ref + "file", fileValue)
        else:
            esl = Utils.escapeText(module.eslText())
            if not self._ESL:
                self._ESL = LongStringProperty("ESL", ref + "ESL")
                self._ESL.SetHelpString("ESL text (source code) for the submodel")
                self._ESL.SetValue(esl)
                #self._page.SetPropertyReadOnly(prop, True, wxpg.PG_DONT_RECURSE) #- allow direct text entry
                self._page.Append(self._ESL)
            else:
                self._ESL.SetName(ref + 'ESL')
                self._ESL.SetValue(esl)
        if self._file: self._file.Hide(codeType != "file")
        if self._ESL: self._ESL.Hide(codeType == "file")
        self.checkMode()

    def updateProperties(self, pageType, category, moduleId, propertyId, propertyTag, newValue):
        module = self._application.getModuleById(moduleId)
        headerText = module.identification(showSubType=True)
        self.setCodePropertyPage(pageType, propertyId, headerText)

    def setProperty(self, propertyName, value, change=False):
        ref = 'M' + PropertyRefSeparator +str(self._propertiesView.moduleId()) + PropertyChildSeparator
        propId = ref + propertyName
        if propertyName == 'ESL':
            value = Utils.escapeText(value)
        if change:
            self._pgm.ChangePropertyValue(propId, value) # will validate every time
                # also loses focus - yuck
        else:
            self._pgm.SetPropertyValue(propId, value) # doesnt validate when move away
                # also doesnt persist
