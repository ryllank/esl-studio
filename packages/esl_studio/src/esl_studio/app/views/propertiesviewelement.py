#! /usr/bin/python

import sys

import wx
import wx.propgrid as wxpg

import esl_diagram.xmlutil as xut
import esl_diagram.canvas.fontwork as Fntwrk

from .. import utils as Utils
from ..propertiescontrol import PropertyRefSeparator, PropertyIdSeparator, PropertyChildSeparator
from .propertiesviewpage import PropertiesViewPage
from .properties.fontproperty import FontProperty, FontPropertiesButtonEditor
from .properties.coreproperties import CompoundProperty
from .properties.colourproperty import ColourProperty

LINEDRAWS = ["straight", "xy", "yx", "long", "short", "xyx", "yxy"]
if sys.platform == "win32":
    STROKESTYLES = ["solid", "dot", "dash", "dot-dash"] # no long-dash supported (it look same as dash)
    StrokeStyleHelp = "Style of line (solid, dotted, dash or dot-dash)"
else:
    STROKESTYLES = ["solid", "dot", "dash", "long-dash", "dot-dash"]
    StrokeStyleHelp = "Style of line (solid, dotted, dash, long-dash or dot-dash)"

ElementsProperties = {
    # We dont support "x", "y", "orientation"
    "rect": ["stroke", "stroke-width", "stroke-style", "fill", "width", "height", "corner"],
    "ellipse": ["stroke", "stroke-width", "stroke-style", "fill", "width", "height"],
    "line": ["stroke", "stroke-width", "stroke-style", "x2", "y2", "draw"],
    #"text": ["fill", "text", "font-family", "font-size", "font-style", "font-weight"], #text is actually contents of XML <text> element
    "text": ["font-colour", "text", "font"],
    "image": ["src"],
    "polyline": ["stroke", "stroke-width", "stroke-style"],
    "polygon": ["stroke", "stroke-width", "stroke-style", "fill"],
    "spline": ["stroke", "stroke-width", "stroke-style"],
    "annotation-text": ["font-colour", "font"],
}

ElementsPropertiesLabel = {
    "stroke": "Line colour",
    "stroke-width": "Line width",
    "stroke-style": "Line style",
    "fill": "Fill colour",
    "width": "Width",
    "height": "Height",
    "corner": "Corner radius",
    "x2": "End X-coordinate",
    "y2": "End Y-coordinate",
    "draw": "Line draw method",
    "font-colour": "Font colour",
    "text": "Text content",
    "font": "Font",
    "src": "Image file"
}

ElementsPropertiesHelp = {
    "stroke": "Colour of line (border)",
    "stroke-width": "With of line",
    "stroke-style": StrokeStyleHelp,
    "fill": "Colour of interior of element",
    "width": "Width of element",
    "height": "Height of element",
    "corner": "Radius for the corners",
    "x2": "X-coordinate for the end of the line",
    "y2": "Y-coordinate for the end of the line",
    "draw": "Line drawn straight or rectilinear (different ways)\n"+
        "straight - direct line drawn between the two end points\n"+
        "xy - rectilinear 2 segments - on x-axis direction from start point\n"+
        "yx - rectilinear 2 segments - on y-axis direction from start point\n"+
        "long - rectilinear 2 segments - on axis of long segment from start point\n"+
        "short - rectilinear 2 segments - on axis of short segment from start point\n" +
        "xyx - rectilinear 3 segments - on x-axis direction from start point and to end point\n" +
        "yxy - rectilinear 3 segments - on y-axis direction from start point and to end point",
    "font-colour": "Colour for the text",
    "text": "Content of the text item",
    "font": "Font properties",
    "src": "File for the image"
}

class ImageFileProperty(wxpg.FileProperty):
    def __init__(self, label, name, value):
        wxpg.FileProperty.__init__(self, label, name, value)

    def setValue(self, name, value):
        self.SetName(name)
        self.SetValue(value)

    def ValueToString(self, value, argFlags=0):
        filename = value
        filename = Utils.relativise(filename)
        if filename == value:
            filename = Utils.environmentalise(filename)
        return filename

class PropertiesViewElement(PropertiesViewPage):
    def __init__(self, propertiesView):
        PropertiesViewPage.__init__(self, propertiesView)
        self._application = self._propertiesView.application()
        self._page = self._propertiesView.page()
        self._pgm = self._propertiesView.pgm()
        self._pagePropertyId = ""
        self._elementXmlElementStr = ""
        self._newElementXmlElementStr = ""
        self._canvasId = ""
        self._objectId = ""
        # properties
        self._stroke = None
        self._strokeWidth = None
        self._strokeStyle = None
        self._fill = None
        self._width = None
        self._height = None
        self._corner = None
        self._x2 = None
        self._y2 = None
        self._draw = None
        self._fontColour = None
        self._text = None
        self._font = None
        self._src = None
        self._properties = {
            "stroke": self._stroke,
            "stroke-width": self._strokeWidth,
            "stroke-style": self._strokeStyle,
            "fill": self._fill,
            "width": self._width,
            "height": self._height,
            "corner": self._corner,
            "x2": self._x2,
            "y2": self._y2,
            "draw": self._draw,
            "font-colour": self._fontColour,
            "text": self._text,
            "font": self._font,
            "src": self._src
        }

    def page(self): return self._page
    def pgm(self): return self._pgm
    def elementXmlElementStr(self): return self._elementXmlElementStr
    def newElementXmlElementStr(self): return self._newElementXmlElementStr

    def setMode(self, mode):
        for property in self._properties.values():
            if property:
                if isinstance(property, CompoundProperty):
                    property.enableWithChildren(mode == "editing")
                else:
                    property.Enable(mode == "editing")

    def resetPropertiesForNewApplication(self):
        # Ensure first item called after this (for new application) is treated as a new item
        self._pagePropertyId = ""

    def setElementPropertyPage(self, pageType, propertyId, headerText, elementXmlElementNot):
        self._propertiesView.clearPropertyPage(headerText, pageType, pageType, 0, propertyId)

        newItem = propertyId != self._pagePropertyId
        self._pagePropertyId = propertyId

        propertyIdSplit = propertyId.split(PropertyIdSeparator)
        if propertyIdSplit and len(propertyIdSplit) == 2:
            self._canvasId = propertyIdSplit[0]
            self._objectId = propertyIdSplit[1]

            canvas = self._application.getCanvasForCanvasId(self._canvasId)
            if canvas:
                elementXmlElementStr = canvas.SaveObjectById(self._objectId)
                elementXmlElement = xut.xmlElement(elementXmlElementStr)

                elementName = pageType
                propertyFields = ElementsProperties[elementName]

                ref = 'X'
                if elementName == "annotation-text":
                    ref = 'Y'
                ref += PropertyRefSeparator +str(self._canvasId) + PropertyRefSeparator + str(self._objectId) + PropertyChildSeparator
                for propertyField in propertyFields:
                    prop = self._properties[propertyField]
                    propAbsent = not prop
                    label = ElementsPropertiesLabel[propertyField]
                    help = ElementsPropertiesHelp[propertyField]
                    fullRef = ref + propertyField
                    value = elementXmlElement.getAttribute(propertyField)

                    if elementName != 'text' and elementName != 'annotation-text':
                        if propertyField == 'fill' or propertyField == 'stroke':
                            if propAbsent:
                                prop = ColourProperty(label, fullRef, value=value, allowNone=True)
                            else:
                                prop.setNameAndValue(fullRef, value)
                        elif propertyField == 'stroke-style':
                            if sys.platform == "win32":
                                if value == "long-dash": # not supported in Windows
                                    value = "dash"
                            value = STROKESTYLES.index(value)
                            if propAbsent:
                                if sys.platform == "win32":
                                    indices = [0, 1, 2, 3]
                                else:
                                    indices = [0, 1, 2, 3, 4]
                                prop = wxpg.EnumProperty(label, fullRef, STROKESTYLES, indices, value)
                            else:
                                prop.SetName(fullRef)
                                prop.SetValue(value)
                        elif propertyField == 'src':
                            if propAbsent:
                                prop = ImageFileProperty(label, fullRef, value)
                                prop.SetAttribute(wxpg.PG_FILE_WILDCARD,
                                    "Image files (*.png;*.jpg;*.gif;*.bmp;*.ico)|*.png;*.jpg;*.gif;*.bmp;*.ico|All files (*.*)|*.*" )
                                prop.SetAttribute(wxpg.PG_FILE_DIALOG_TITLE, "Select an image file" )
                            else:
                                prop.setValue(fullRef, value)
                        elif propertyField == 'draw':
                            value = LINEDRAWS.index(value)
                            if propAbsent:
                                prop = wxpg.EnumProperty(label, fullRef, LINEDRAWS, [0,1,2,3,4,5,6], value)
                            else:
                                prop.SetName(fullRef)
                                prop.SetValue(value)
                        else: # an int
                            value = int(value)
                            if propAbsent:
                                prop = wxpg.IntProperty(label, fullRef, value)
                            else:
                                prop.SetName(fullRef)
                                prop.SetValue(value)
                    else:
                        if propertyField == 'font-colour':
                            value = elementXmlElement.getAttribute('fill')
                            if propAbsent:
                                prop = ColourProperty(label, fullRef, value=value)
                            else:
                                prop.setNameAndValue(fullRef, value)
                        elif propertyField == 'text':
                            value = elementXmlElement.getContent()
                            if propAbsent:
                                prop = wxpg.StringProperty(label, fullRef, value=value)
                            else:
                                prop.SetName(fullRef)
                                prop.SetValue(value)
                        elif propertyField == 'font':
                            value = Fntwrk.getFont(elementXmlElement)
                            if propAbsent:
                                prop = FontProperty(self, label, fullRef, value=value)
                            else:
                                prop.setValue(fullRef, value)
                                if newItem:
                                    self._page.Collapse(prop)
                    if propAbsent and prop: # i.e. just made it
                        prop.SetHelpString(help)
                        self._properties[propertyField] = prop
                        self._page.Append(prop)
                        if propertyField == 'font':
                            FontPropertiesButtonEditor.SetEditorToProperty(prop)
                for propertyField, prop in self._properties.items():
                    if prop:
                        prop.Hide(propertyField not in propertyFields)
        self.checkMode()

    def updateProperties(self, pageType, category, moduleId, propertyId, propertyTag, newValue):
        propertyIdSplit = propertyId.split(PropertyIdSeparator)
        if propertyIdSplit and len(propertyIdSplit) == 2:
            self._canvasId = propertyIdSplit[0]
            self._objectId = propertyIdSplit[1]

            canvas = self._application.getCanvasForCanvasId(self._canvasId)
            if canvas:
                elementXmlElementStr = canvas.SaveObjectById(self._objectId)
                elementXmlElement = xut.xmlElement(elementXmlElementStr)

                elementName = pageType
                propertyFields = ElementsProperties[elementName]

                ref = 'X' + PropertyRefSeparator +str(self._canvasId) + PropertyRefSeparator + str(self._objectId) + PropertyChildSeparator
                for propertyField in propertyFields:
                    prop = None
                    if propertyField == 'fill' or propertyField == 'stroke' or propertyField == 'font-colour':
                        if propertyField == 'font-colour':
                            value = elementXmlElement.getAttribute('fill')
                        else:
                            value = elementXmlElement.getAttribute(propertyField)
                    elif propertyField == 'text':
                        value = elementXmlElement.getContent()
                    elif propertyField == 'font':
                        value = Fntwrk.getFont(elementXmlElement)
                    else:
                        value = elementXmlElement.getAttribute(propertyField)
                        if propertyField == 'stroke-style':
                            value = STROKESTYLES.index(value)
                        elif propertyField == 'draw':
                            value = LINEDRAWS.index(value)
                        elif propertyField == 'src':
                            value = int(value)
                    prop = self._page.GetProperty(ref + propertyField)
                    if prop and value is not None:
                        prop.SetValue(value)

    def getElementPropertyChange(self, propertyTag, newValue):
        canvas = self._application.getCanvasForCanvasId(self._canvasId)
        self._elementXmlElementStr = canvas.SaveObjectById(self._objectId)
        elementXmlElement = xut.xmlElement(self._elementXmlElementStr)

        if propertyTag == 'font-colour' or propertyTag == 'stroke' or propertyTag == 'fill':
            colourProperty = self._properties[propertyTag]
            colourStr = colourProperty.convertFromWxColour(newValue)
            if propertyTag == 'font-colour':
                elementXmlElement.setAttribute('fill', colourStr)
            else:
                elementXmlElement.setAttribute(propertyTag, colourStr)
        elif propertyTag == 'stroke-style':
            elementXmlElement.setAttribute(propertyTag, STROKESTYLES[newValue])
        elif propertyTag == 'text':
             elementXmlElement.setContent(newValue)
        elif propertyTag == 'font':
            Fntwrk.setFontXmlElements(elementXmlElement, newValue)
        elif propertyTag == 'draw':
            elementXmlElement.setAttribute(propertyTag, LINEDRAWS[newValue])
        else:
            elementXmlElement.setAttribute(propertyTag, newValue)
        self._newElementXmlElementStr = elementXmlElement.xml()
        return self._elementXmlElementStr, self._newElementXmlElementStr
