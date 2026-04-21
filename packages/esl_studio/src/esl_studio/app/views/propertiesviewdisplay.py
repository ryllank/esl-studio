#! /usr/bin/python

import wx
import wx.propgrid as wxpg

from ..propertiescontrol import PropertyRefSeparator, PropertyIdSeparator, PropertyChildSeparator
from ..application.displaydefinition import DisplayDefinition, PlotSpec, TableSpec
from .propertiesviewpage import PropertiesViewPage
from .properties.plotaxisproperty import PlotAxisProperty
from .properties.coreproperties import CompoundProperty

class PropertiesViewDisplay(PropertiesViewPage):

    UpdateTexts = ["Communication Points", "Communication Points and Discontinuities", "Step Points"]
    DisplayTexts = ["ESL-SEC", "ESL statement", "Both ESL-SEC + ESL statement"]
    PlotStyleTexts = ["Line", "Symbol", "Line + Symbol"]
    OutputTexts = ["Window", "Tab File", "CSV File"]
    TableStyleTexts = ["Trend", "Monitor"]

    def __init__(self, propertiesView):
        PropertiesViewPage.__init__(self, propertiesView)
        self._application = self._propertiesView.application()
        self._page = self._propertiesView.page()
        self._pgm = self._propertiesView.pgm()
        self._pagePropertyId = ""
        # properties
        self._definedCategory = None
        self._summary = None
        self._help = None
        self._view = None
        self._displayCategory = None
        self._name = None
        self._title = None
        self._subtitle = None
        self._update = None
        self._display = None
        self._displaySpecCategory = None
        # in PlotSpec
        self._plotStyle = None
        self._xAxis = None
        self._yAxis = None
        # in TableSpec
        self._output = None
        self._tableStyle = None
        self._outputFile = None
        # in PrepareSpec
        self._prepareFile = None

        self._pgm.Bind(wxpg.EVT_PG_CHANGED, self.OnPropGridChange)

    def page(self): return self._page
    def pgm(self): return self._pgm

    def setMode(self, mode):
        properties = [ # self._summary self._help self._view - always disabled
            #self._definedCategory
            #self._displayCategory
            self._name,
            self._title,
            self._subtitle,
            self._update,
            self._display,
            #self._displaySpecCategory
            # in PlotSpec
            self._plotStyle,
            self._xAxis,
            self._yAxis,
            # in TableSpec
            self._output,
            self._tableStyle,
            self._outputFile,
            # in PrepareSpec
            self._prepareFile
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

    def setFixedProperties(self, ref):
        if not self._definedCategory:
            self._definedCategory = wxpg.PropertyCategory("Type")
            self._definedCategory.SetHelpString("The type of the display definition")
            self._page.Append(self._definedCategory)

            self._summary = wxpg.StringProperty("Summary")
            self._summary.Enable(False)
            self._page.Append(self._summary)

            self._help = wxpg.StringProperty("Help")
            self._help.SetHelpString("Source for help information for this type of display definition" +
                                     "\nDouble click property row to open.")
            self._help.Enable(False)
            self._page.Append(self._help)

            self._view = wxpg.StringProperty("View")
            self._view.SetHelpString("Source to view information for this type of display definition" +
                                     "\nDouble click property row to open.")
            self._view.Enable(False)
            self._page.Append(self._view)

            self._displayCategory = wxpg.PropertyCategory("Display Properties")
            self._page.Append(self._displayCategory)
            self._displayCategory.Hide(True) # we dont want to see this - is used to locate the display properties

            # These properties are inserted to the "root" property above the dummy entity category
            self._name = wxpg.StringProperty("Name")
            self._name.SetHelpString("Name of the display definition.")
            self._page.Insert(self._displayCategory, self._name)

            self._title = wxpg.StringProperty("Title")
            self._title.SetHelpString("Title to be displayed.")
            self._page.Insert(self._displayCategory, self._title)

            self._subtitle = wxpg.StringProperty("Subtitle")
            self._subtitle.SetHelpString("Subtitle to be displayed.")
            self._page.Insert(self._displayCategory, self._subtitle)

            self._update = wxpg.EnumProperty("Update")
            self._update.SetHelpString("Update rate of the display.")
            self._update.SetChoices(wxpg.PGChoices(PropertiesViewDisplay.UpdateTexts, [0,1,2]))
            self._page.Insert(self._displayCategory, self._update)

            self._display = wxpg.EnumProperty("Display")
            self._display.SetHelpString(
                "Locate display in ESL-SEC, by generating the appropriate ESL PLOT/TABULATE/PREPARE statement, or both.")
            self._display.SetChoices(wxpg.PGChoices(PropertiesViewDisplay.DisplayTexts, [0, 1, 2]))
            self._page.Insert(self._displayCategory, self._display)

            self._displaySpecCategory = wxpg.PropertyCategory('Display Specification')
            self._page.Append(self._displaySpecCategory)

            self._plotStyle = wxpg.EnumProperty("Plot Style", ref + 'plotStyle')
            self._plotStyle.SetHelpString(
                "Plot style - line, points or both.\n[Not used in ESL PLOT statement when run simulation directly (without SEC)]")
            self._plotStyle.SetChoices(wxpg.PGChoices(PropertiesViewDisplay.PlotStyleTexts, [0, 1, 2]))
            self._page.Append(self._plotStyle)

            self._xAxis = PlotAxisProperty(self, "X-Axis")
            self._xAxis.SetHelpString(
                "Configuration data for the X plot axis.\n[When run simulation directly (without SEC) set you may set min and max. Other features are not used]")
            self._page.Append(self._xAxis)

            self._yAxis = PlotAxisProperty(self, "Y-Axis")
            self._yAxis.SetHelpString(
                "Configuration data for the Y plot axis.\n[When run simulation directly (without SEC) set appropriate min and max. Other features are not used]")
            self._page.Append(self._yAxis)

            self._output = wxpg.EnumProperty("Output")
            helpStr = "Table output style - window or Tab or CSV file."
            helpStr += "\nNote: When this display generates an ESL TABULATE statement this always does the equivalent of Tab file."
            self._output.SetHelpString(helpStr)
            self._output.SetChoices(wxpg.PGChoices(PropertiesViewDisplay.OutputTexts, [0, 1, 2]))
            self._page.Append(self._output)

            self._tableStyle = wxpg.EnumProperty("Table Style")
            self._tableStyle.SetHelpString("Table window style - trend (list) or monitor (updates).")
            self._tableStyle.SetChoices(wxpg.PGChoices(PropertiesViewDisplay.TableStyleTexts, [0, 1]))
            self._page.Append(self._tableStyle)

            self._outputFile = wxpg.StringProperty("Output file")
            self._outputFile.SetHelpString("Output file path.")
            self._page.Append(self._outputFile)

            self._prepareFile = wxpg.StringProperty("Prepare file")
            self._prepareFile.SetHelpString("Output file path.")
            self._page.Append(self._prepareFile)

    def setDisplayPropertyPage(self, pageType, propertyId, headerText):
        headerText = headerText[0].upper() + headerText[1:]
        self._propertiesView.clearPropertyPage(headerText, pageType, 'display', 0, propertyId) # Currently this clobbers properties - so Noneify

        propertyIdSplit = propertyId.split(PropertyIdSeparator)
        if propertyIdSplit and len(propertyIdSplit) == 2:
            canvasId = propertyIdSplit[0]
            objectId = propertyIdSplit[1]
            displayDefinition = self._application.getDisplayForCanvasObjectIds(canvasId, objectId)
            if displayDefinition:

                newItem = propertyId != self._pagePropertyId
                self._pagePropertyId = propertyId

                ref = 'D' + PropertyRefSeparator +str(canvasId) + PropertyRefSeparator + str(objectId) + PropertyChildSeparator

                self.setFixedProperties(ref)

                type = displayDefinition.type()
                self._definedCategory.SetValue(type.title())

                value = displayDefinition.summary()
                self._summary.SetName(ref + 'summary')
                self._summary.SetValue(value)
                self._summary.SetHelpString(value) # hint is same as summary value
                self._summary.Hide(value == "")

                value = displayDefinition.help()
                self._help.SetName(ref + 'help')
                self._help.SetValue(value)
                self._help.Hide(value == "")

                value = displayDefinition.view()
                self._view.SetName(ref + 'view')
                self._view.SetValue(value)
                self._view.Hide(value == "")

                self._name.SetName(ref + 'name')
                self._name.SetValue(displayDefinition.name)

                self._title.SetName(ref + 'title')
                self._title.SetValue(displayDefinition.title)

                self._subtitle.SetName(ref + 'subtitle')
                self._subtitle.SetValue(displayDefinition.subtitle)

                self._update.SetName(ref + 'update')
                self._update.SetValue(DisplayDefinition.Update_values.index(displayDefinition.update))

                self._display.SetName(ref + 'display')
                self._display.SetValue(DisplayDefinition.Display_values.index(displayDefinition.display))

                caption = ""
                if type == "plot":
                    caption = "Plot Specification"
                if type == "table":
                    caption = "Table Specification"
                if type == "prepare":
                    caption = "Prepare Specification"
                if caption:
                    self._displaySpecCategory.SetLabel(caption)

                if type == "plot":
                    self._plotStyle.SetName(ref + 'plotStyle')
                    self._plotStyle.SetValue(PlotSpec.PlotStyle_values.index(displayDefinition.plotSpec.plotStyle))

                    self._xAxis.setAxis(ref + "xAxis", displayDefinition.plotSpec.xAxis)
                    if newItem:
                        self._page.Collapse(self._xAxis)

                    self._yAxis.setAxis(ref + "yAxis", displayDefinition.plotSpec.yAxis)
                    if newItem:
                        self._page.Collapse(self._yAxis)

                elif type == "table":
                    self._output.SetName(ref + 'output')
                    self._output.SetValue(TableSpec.Output_values.index(displayDefinition.tableSpec.output))

                    self._tableStyle.SetName(ref + 'tableStyle')
                    self._tableStyle.SetValue(TableSpec.TableStyle_values.index(displayDefinition.tableSpec.tableStyle))

                    self._outputFile.SetName(ref + 'outputFile')
                    self._outputFile.SetValue(displayDefinition.tableSpec.outputFile)

                elif type == "prepare":
                    self._prepareFile.SetName(ref + 'prepareFile')
                    self._prepareFile.SetValue(displayDefinition.prepareSpec.prepareFile)

                self._plotStyle.Hide(type != "plot")
                self._xAxis.Hide(type != "plot")
                self._yAxis.Hide(type != "plot")
                self._output.Hide(type != "table")
                self._tableStyle.Hide(type != "table" or displayDefinition.tableSpec.output != "window")
                self._outputFile.Hide(type != "table" or displayDefinition.tableSpec.output == "window")
                self._prepareFile.Hide(type != "prepare")
        self.checkMode()

    def updateProperties(self, pageType, category, moduleId, propertyId, propertyTag, newValue):
        propertyIdSplit = propertyId.split(PropertyIdSeparator)
        if propertyIdSplit and len(propertyIdSplit) == 2:
            canvasId = int(propertyIdSplit[0])
            objectId = int(propertyIdSplit[1])
            headerText = None # don't change current header
            self.setDisplayPropertyPage(pageType, propertyId, headerText, True)

    def OnPropGridChange(self, propertygridevent):
        property = propertygridevent.GetProperty()
        if property == self._output:
            propertyValue = propertygridevent.GetPropertyValue()
            if propertyValue == 0: # Window
                self._outputFile.Hide(True)
                self._tableStyle.Hide(False)
            else:
                self._outputFile.Hide(False)
                self._tableStyle.Hide(True)
