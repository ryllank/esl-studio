#! /usr/bin/python

import esl_diagram.xmlutil as xut

from .. import utils as Utils

class DisplayNames(object):
    def __init__(self):
        self._displayNames = []
    def isin(self, name):
        result = name in self._displayNames
        return result
    def add(self, name):
        count = 1
        stem = name
        while name in self._displayNames:
            name = stem + " " + str(count)
            count += 1
        self._displayNames.append(name)
        return name
    def delete(self, name):
        if name in self._displayNames:
            self._displayNames.remove(name)
    def valid(self, name):
        result = ""
        stripped = name.strip()
        if not name or not stripped:
            result = 'no name given'
        elif name != stripped:
            result = 'name has leading or trailing blanks'
        return result

class PlotAxis(object):
    Origin_values = ["auto", "zero", "min", "max"]
    Default_min = 0.0               # used when auto-scale
    Default_max = 0.0
    Default_divs = 0.0
    Default_origin = "auto"         # "auto"(default) | "zero" | "min" | "max"
    Default_autoScale = True
    Default_log = False
    Default_grid = True
    def __init__(self):
        self.min = PlotAxis.Default_min
        self.max = PlotAxis.Default_max
        self.divs = PlotAxis.Default_divs
        self.origin = PlotAxis.Default_origin
        self.autoScale = PlotAxis.Default_autoScale
        self.log = PlotAxis.Default_log
        self.grid = PlotAxis.Default_grid
    def load(self, axisXmlElement):
        self.min = PlotAxis.Default_min
        self.max = PlotAxis.Default_max
        self.divs = PlotAxis.Default_divs
        self.origin = PlotAxis.Default_origin
        self.autoScale = PlotAxis.Default_autoScale
        self.log = PlotAxis.Default_log
        self.grid = PlotAxis.Default_grid
        value = axisXmlElement.getAttribute("min")
        if value:
            self.min = float(value)
        value = axisXmlElement.getAttribute("max")
        if value:
            self.max = float(value)
        value = axisXmlElement.getAttribute("divs")
        if value:
            self.divs = int(value)
        value = axisXmlElement.getAttribute("origin")
        if value:
            self.origin = value
        value = axisXmlElement.getAttribute("auto-scale")
        if value and value == "false":
            self.autoScale = False
        value = axisXmlElement.getAttribute("log")
        if value and value == "true":
            self.log = True
        value = axisXmlElement.getAttribute("grid")
        if value and value == "true":
            self.grid = True
    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = "" # don't include the element here - as will do in PlotSpec's save
        maxMinNotDefault = self.min != PlotAxis.Default_min or self.max != PlotAxis.Default_max
        if saveDefaults or maxMinNotDefault:
            result += " min=\"" + str(float(self.min)) + "\""
        if saveDefaults or maxMinNotDefault:
            result += " max=\"" + str(float(self.max)) + "\""
        if saveDefaults or self.divs != PlotAxis.Default_divs:
            result += " divs=\"" + str(int(self.divs)) + "\""
        if saveDefaults or self.origin != PlotAxis.Default_origin:
            result += " origin=\"" + self.origin + "\""
        if saveDefaults or self.autoScale != PlotAxis.Default_autoScale:
            result += " auto-scale=\"" + ("true" if self.autoScale else "false") + "\""
        if saveDefaults or self.log != PlotAxis.Default_log:
            result += " log=\"" + ("true" if self.log else "false") + "\""
        if saveDefaults or self.grid != PlotAxis.Default_grid:
            result += " grid=\"" + ("true" if self.grid else "false") + "\""
        # don't include the end of the element either
        return result
    def loadData(self, data):
        xmlElement = xut.xmlElement("<axis" + data + "/>")
        if xmlElement:
            self.load(xmlElement)

class PlotSpec(object):
    PlotStyle_values = ["line", "symbol", "line+symbol"]
    Default_plotStyle = "line"  # "line"(default) | "symbol" | "line+symbol"
    Default_x = 0
    Default_y = 0
    Default_width = 640  # or 500
    Default_height = 600  # or 300
    def __init__(self):
        self.plotStyle = PlotSpec.Default_plotStyle
        self.x = PlotSpec.Default_x
        self.y = PlotSpec.Default_y
        self.width = PlotSpec.Default_width
        self.height = PlotSpec.Default_height
        self.xAxis = PlotAxis()
        self.yAxis = PlotAxis()
    def load(self, displayDescrXmlElement):
        self.plotStyle = "line"
        self.plotStyle = PlotSpec.Default_plotStyle
        self.x = PlotSpec.Default_x
        self.y = PlotSpec.Default_y
        self.width = PlotSpec.Default_width
        self.height = PlotSpec.Default_height
        self.xAxis = PlotAxis()
        self.yAxis = PlotAxis()
        plotXmlElement = displayDescrXmlElement.getXmlElementByName("plot")
        if plotXmlElement:
            value = plotXmlElement.getAttribute("plot-style")
            if value:
                self.plotStyle = value
            if plotXmlElement.getAttribute("x"):
                self.x = int(plotXmlElement.getAttribute("x"))
                self.y = int(plotXmlElement.getAttribute("y"))
                self.width = int(plotXmlElement.getAttribute("width"))
                self.height = int(plotXmlElement.getAttribute("height"))
            axisXmlElement = plotXmlElement.getXmlElementByName("x-axis")
            if axisXmlElement:
                self.xAxis.load(axisXmlElement)
            axisXmlElement = plotXmlElement.getXmlElementByName("y-axis")
            if axisXmlElement:
                self.yAxis.load(axisXmlElement)
    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        xAxis = self.xAxis.save(indent, level + 1, saveDefaults)
        yAxis = self.yAxis.save(indent, level + 1, saveDefaults)
        result = ind + "<plot"
        if saveDefaults or self.plotStyle != PlotSpec.Default_plotStyle:
            result += " plot-style=\"" + self.plotStyle + "\""
        if (self.x != PlotSpec.Default_x or self.y != PlotSpec.Default_y or
            self.width != PlotSpec.Default_width or self.height != PlotSpec.Default_height):
            result += " x=\"" + str(self.x) + "\" y=\"" + str(self.y) + "\" width=\"" + str(self.width) + "\" height=\"" + str(self.height) + "\""
        if not xAxis and not yAxis:
            result += "/>"
        else:
            result += ">" + nl
            if xAxis: result += ind2 + "<x-axis" + xAxis + "/>" + nl
            if yAxis: result += ind2 + "<y-axis" + yAxis + "/>" + nl
            result += ind + "</plot>"
        result += nl
        return result

class TableSpec(object):
    Output_values = ["window", "tabfile", "csvfile"]
    Default_output = "window"  # "window"(default) | "tabfile" | "csvfile"
    TableStyle_values = ["trend", "monitor"]
    Default_tableStyle = "trend"  # "trend"(default) | "monitor"
    Default_x = 0  # if window
    Default_y = 0
    Default_width = 640  # or 500
    Default_height = 600  # or 300
    Default_outputFile = ""  # for output!="window" - defaults to display name + appropriate extension (tab|csv)

    def __init__(self):
        self.output = TableSpec.Default_output
        self.tableStyle = TableSpec.Default_tableStyle
        self.x = TableSpec.Default_x
        self.y = TableSpec.Default_y
        self.width = TableSpec.Default_width
        self.height = TableSpec.Default_height
        self.outputFile = TableSpec.Default_outputFile
    def load(self, displayDescrXmlElement):
        self.output = TableSpec.Default_output
        self.tableStyle = TableSpec.Default_tableStyle
        self.x = TableSpec.Default_x
        self.y = TableSpec.Default_y
        self.width = TableSpec.Default_width
        self.height = TableSpec.Default_height
        self.outputFile = TableSpec.Default_outputFile
        tableXmlElement = displayDescrXmlElement.getXmlElementByName("table")
        if tableXmlElement:
            value = tableXmlElement.getAttribute("output")
            if value:
                self.output = value
            self.tableStyle = "trend"
            value = tableXmlElement.getAttribute("table-style")
            if value:
                self.tableStyle = value
            if self.output == "window":
                if tableXmlElement.getAttribute("x"):
                    self.x = int(tableXmlElement.getAttribute("x"))
                    self.y = int(tableXmlElement.getAttribute("y"))
                    self.width = int(tableXmlElement.getAttribute("width"))
                    self.height = int(tableXmlElement.getAttribute("height"))
            else:
                self.outputFile = tableXmlElement.getContent()
    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ind + "<table"
        if saveDefaults or self.output != TableSpec.Default_output:
            result += " output=\"" + self.output + "\""
        if self.output == "window":
            if saveDefaults or self.tableStyle != TableSpec.Default_tableStyle:
                result += " table-style=\"" + self.tableStyle + "\""
            if (self.x != TableSpec.Default_x or self.y != TableSpec.Default_y or
                self.width != TableSpec.Default_width or self.height != TableSpec.Default_height):
                result += " x=\"" + str(self.x) + "\" y=\"" + str(self.y) + "\" width=\"" + str(self.width) + "\" height=\"" + str(self.height) + "\""
            result += "/>"
        else:
            result += "><![CDATA["+self.outputFile+"]]></table>"
        result += nl
        return result

class PrepareSpec(object):
    Default_prepareFile = ""  # defaults to display name + dsp extension
    def __init__(self):
        self.prepareFile = PrepareSpec.Default_prepareFile
    def load(self, displayDescrXmlElement):
        self.prepareFile = PrepareSpec.Default_prepareFile
        xmlElement = displayDescrXmlElement.getXmlElementByName("prepare-file")
        if xmlElement: self.prepareFile = xmlElement.getContent()
    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ind + "<prepare-file><![CDATA["+self.prepareFile+"]]></prepare-file>" + nl
        return result

class DisplayDefinition(object):
    Update_values = ["communication", "communication-discontinuities", "step"]
    Display_values = ["ESL-SEC", "ESL-statement", "ESL-SEC+ESL-statement"]
    Default_update = "communication"  # "communication"(default) | "communication-discontinuities" | "step"
    Default_createOnLoad = True  # "true"(default) | "false"
    Default_name = ""  # display names must be unique in the application (not merely module) - property to validate
    Default_title = ""
    Default_subtitle = ""
    Default_display = "ESL-SEC"
    def __init__(self, parent, type = "", objectId = ""):
        self._parent = parent
        self._application = self._parent.parent().application()
        self._type = type                   # "plot" | "table" | "prepare"
        self._objectId = objectId
        self._entityDefnXmlElement = None
        self._prefix = ""
        self._summary = ""
        self._help = ""
        self._view = ""
        self.update = DisplayDefinition.Default_update
        self.display = DisplayDefinition.Default_display
        self.createOnLoad = DisplayDefinition.Default_createOnLoad
        self.name = DisplayDefinition.Default_name
        self.title = DisplayDefinition.Default_title
        self.subtitle = DisplayDefinition.Default_subtitle
        self.plotSpec = None
        self.tableSpec = None
        self.prepareSpec = None
        if self._type == "plot" : self.plotSpec = PlotSpec()
        if self._type == "table" : self.tableSpec = TableSpec()
        if self._type == "prepare" : self.prepareSpec = PrepareSpec()
        if type:
            entities = self._parent._parent._application._frame.control().entities()
            self._entityDefnXmlElement = entities.getEntityDefnXmlElement(self._type)
            if self._entityDefnXmlElement:
                prefix = self._entityDefnXmlElement.getAttribute("prefix")
                if prefix: self._prefix = prefix
                summaryXmlElement = self._entityDefnXmlElement.getXmlElementByName("summary")
                if summaryXmlElement: self._summary = summaryXmlElement.getContent()
                helpXmlElement = self._entityDefnXmlElement.getXmlElementByName("help")
                if helpXmlElement:
                    help = helpXmlElement.getAttribute("src")
                    if help: self._help = help
                viewXmlElement = self._entityDefnXmlElement.getXmlElementByName("view")
                if viewXmlElement:
                    view = viewXmlElement.getAttribute("src")
                    if view: self._view = view
                # Set an initial name
                self.name = "Display "
                if self._type == "plot": self.name += "Plot"
                if self._type == "table": self.name += "Table"
                if self._type == "prepare": self.name += "Prepare"
                # validate current uniqueness
                self.name = self._application.displayNames().add(self.name)
            else:
                msg = "No display definition for type \""+self._type+"\" found\n"
                self._application.frame().control().appendMessage(msg, 0)
                self._type = ""
    def parent(self): return self._parent
    def type(self): return self._type
    def summary(self): return self._summary
    def help(self): return self._help
    def view(self): return self._view
    def objectId(self): return self._objectId
    def entityDefnXmlElement(self): return self._entityDefnXmlElement
    def prefix(self): return self._prefix

    def load(self, displayDescrXmlElement):
        self._type = displayDescrXmlElement.getAttribute("type")
        self._objectId = displayDescrXmlElement.getAttribute("id")
        self.update = DisplayDefinition.Default_update
        self.display = DisplayDefinition.Default_display
        self.createOnLoad = DisplayDefinition.Default_createOnLoad
        #self.name
        self.title = DisplayDefinition.Default_title
        self.subtitle = DisplayDefinition.Default_subtitle
        self.plotSpec = None
        self.tableSpec = None
        self.prepareSpec = None
        if self._type == "plot" : self.plotSpec = PlotSpec()
        if self._type == "table" : self.tableSpec = TableSpec()
        if self._type == "prepare" : self.prepareSpec = PrepareSpec()
        value = displayDescrXmlElement.getAttribute("update")
        if value:
            self.update = value
        value = displayDescrXmlElement.getAttribute("display")
        if value:
            self.display = value
        value = displayDescrXmlElement.getAttribute("create-on-load")
        if value and value == "false":
            self.createOnLoad = False
        xmlElement = displayDescrXmlElement.getXmlElementByName("name")
        if xmlElement:
            new_name = xmlElement.getContent()
            if new_name == "" and self.name == "":
                new_name = "Display "
                if self._type == "plot": new_name += "Plot"
                if self._type == "table": new_name += "Table"
                if self._type == "prepare": new_name += "Prepare"
            if new_name != self.name:
                if self.name:
                    self._application.displayNames().delete(self.name)
                self.name = new_name
                # validate current uniqueness
                self.name = self._application.displayNames().add(self.name)
        xmlElement = displayDescrXmlElement.getXmlElementByName("title")
        if xmlElement: self.title = xmlElement.getContent()
        xmlElement = displayDescrXmlElement.getXmlElementByName("subtitle")
        if xmlElement: self.subtitle = xmlElement.getContent()
        if self._type == "plot":
            self.plotSpec.load(displayDescrXmlElement)
        elif self._type == "table":
            self.tableSpec.load(displayDescrXmlElement)
        elif self._type == "prepare":
            self.prepareSpec.load(displayDescrXmlElement)

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ind + "<display id=\"" + str(self._objectId) + "\" type=\"" + self._type + "\""
        if saveDefaults or self.update != DisplayDefinition.Default_update:
            result += " update=\"" + self.update + "\""
        if saveDefaults or self.display != DisplayDefinition.Default_display:
            result += " display=\"" + self.display + "\""
        if saveDefaults or self.createOnLoad != DisplayDefinition.Default_createOnLoad:
            result += " create-on-load=\"" + ("true" if self.createOnLoad else "false") + "\""
        result += ">" + nl
        # There's always a name
        result += ind2 + "<name><![CDATA["+self.name+"]]></name>" + nl
        if saveDefaults or self.title != DisplayDefinition.Default_title:
            result += ind2 + "<title><![CDATA["+self.title+"]]></title>" + nl
        if saveDefaults or self.subtitle != DisplayDefinition.Default_subtitle:
            result += ind2 + "<subtitle><![CDATA["+self.subtitle+"]]></subtitle>" + nl
        if self._type == "plot":
            result += self.plotSpec.save(indent, level + 1, saveDefaults)
        elif self._type == "table":
            result += self.tableSpec.save(indent, level + 1, saveDefaults)
        elif self._type == "prepare":
            result += self.prepareSpec.save(indent, level + 1, saveDefaults)
        result += ind + "</display>" + nl
        return result

    def updateEntity(self, updateXmlElement):
        # We don't update the display icon when the display definition properties change
        pass

    def updateEntityFromDiagramChange(self, diagramChangeUpdateXmlElement):
        # We don't update the display icon when the diagram features change
        pass

    def validateDisplayPropertyChange(self, propertyTag, newValue, val_type, val_item):
        valid = True
        rejection = ""
        if propertyTag == 'name':
            rejection = self._application.displayNames().valid(newValue)
            if rejection:
                valid = False
            else:
                if self._application.displayNames().isin(newValue):
                    rejection = 'display name is already in use in the application'
                    valid = False
        elif propertyTag == 'xAxis' or propertyTag == 'yAxis':
            testAxis = PlotAxis()
            testAxis.loadData(newValue)
            if testAxis.min != testAxis.max and testAxis.min > testAxis.max:
                rejection = "axis minimum ("+str(testAxis.min)+" must be less than or equal to maximum (" + str(testAxis.max) + ")"
                valid = False
        return valid, rejection, val_type, val_item

    def updateDisplayProperty(self, propertyTag, newValue):
        if propertyTag == 'name':
            oldName = self.name
            self.name = newValue
            if oldName != newValue:
                self._application.displayNames().delete(oldName)
            if not self._application.displayNames().isin(newValue):
                self._application.displayNames().add(newValue)
        elif propertyTag == 'title':
            self.title = newValue
        elif propertyTag == 'subtitle':
            self.subtitle = newValue
        elif propertyTag == 'update':
            self.update = DisplayDefinition.Update_values[int(newValue)]
        elif propertyTag == 'display':
            self.display = DisplayDefinition.Display_values[int(newValue)]
        elif propertyTag == 'plotStyle':
            self.plotSpec.plotStyle = PlotSpec.PlotStyle_values[int(newValue)]
        elif propertyTag == 'xAxis':
            self.plotSpec.xAxis.loadData(newValue)
        elif propertyTag == 'yAxis':
            self.plotSpec.yAxis.loadData(newValue)
        elif propertyTag == 'output':
            self.tableSpec.output = TableSpec.Output_values[int(newValue)]
        elif propertyTag == 'tableStyle':
            self.tableSpec.tableStyle = TableSpec.TableStyle_values[int(newValue)]
        elif propertyTag == 'outputFile':
            self.tableSpec.outputFile = newValue
        elif propertyTag == 'prepareFile':
            self.prepareSpec.prepareFile = newValue

    def saveForSEC(self, displayIcon, variables):
        indent = '\t'
        level = 2
        nl, ind, ind2 = Utils.indentation(indent, level)
        saveDefaults = False
        type = self._type
        if type == "plot":
            type = "runtime-plot"
        result = ind + "<display display-icon=\"" + str(displayIcon) + "\" type=\"" + type + "\""
        # Copied from save
        if saveDefaults or self.update != DisplayDefinition.Default_update:
            result += " update=\"" + self.update + "\""
        if saveDefaults or self.createOnLoad != DisplayDefinition.Default_createOnLoad:
            result += " create-on-load=\"" + ("true" if self.createOnLoad else "false") + "\""
        result += ">" + nl
        # There's always a name
        result += ind2 + "<name><![CDATA["+self.name+"]]></name>" + nl
        if saveDefaults or self.title != DisplayDefinition.Default_title:
            result += ind2 + "<title><![CDATA["+self.title+"]]></title>" + nl
        if saveDefaults or self.subtitle != DisplayDefinition.Default_subtitle:
            result += ind2 + "<subtitle><![CDATA["+self.subtitle+"]]></subtitle>" + nl
        # insert the variable references - there's always time
        result += ind2 + "<variable><![CDATA["+"(RESERVED) T"+"]]></variable>" + nl
        for variable in variables:
            result += ind2 + "<variable><![CDATA[" + variable + "]]></variable>" + nl
        if self._type == "plot":
            result += self.plotSpec.save(indent, level + 1, saveDefaults)
        elif self._type == "table":
            result += self.tableSpec.save(indent, level + 1, saveDefaults)
        elif self._type == "prepare":
            result += self.prepareSpec.save(indent, level + 1, saveDefaults)
        result += ind + "</display>" + nl
        return result

    def updateFromSEC(self, displayXml):
        # Based on load
        self.update = DisplayDefinition.Default_update
        #self.display
        self.createOnLoad = DisplayDefinition.Default_createOnLoad
        #self.name
        self.title = DisplayDefinition.Default_title
        self.subtitle = DisplayDefinition.Default_subtitle
        self.plotSpec = None
        self.tableSpec = None
        self.prepareSpec = None
        if self._type == "plot" : self.plotSpec = PlotSpec()
        if self._type == "table" : self.tableSpec = TableSpec()
        if self._type == "prepare" : self.prepareSpec = PrepareSpec()
        value = displayXml.getAttribute("update")
        if value:
            self.update = value
        value = displayXml.getAttribute("create-on-load")
        if value and value == "false":
            self.createOnLoad = False
        xmlElement = displayXml.getXmlElementByName("title")
        if xmlElement: self.title = xmlElement.getContent()
        xmlElement = displayXml.getXmlElementByName("subtitle")
        if xmlElement: self.subtitle = xmlElement.getContent()
        if self._type == "plot":
            self.plotSpec.load(displayXml)
        elif self._type == "table":
            self.tableSpec.load(displayXml)
        elif self._type == "prepare":
            self.prepareSpec.load(displayXml)
