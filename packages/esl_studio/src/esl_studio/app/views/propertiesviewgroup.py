#! /usr/bin/python

import wx.propgrid as wxpg

import esl_diagram.xmlutil as xut

from ..propertiescontrol import PropertyRefSeparator, PropertyIdSeparator, PropertyChildSeparator
from .propertiesviewpage import PropertiesViewPage
from .properties.coreproperties import CompoundProperty
from .properties.scaleproperty import ScaleProperty
from .properties.orientationproperty import OrientationProperty

class PropertiesViewGroup(PropertiesViewPage):
    def __init__(self, propertiesView):
        PropertiesViewPage.__init__(self, propertiesView)
        self._application = self._propertiesView.application()
        self._page = self._propertiesView.page()
        self._pgm = self._propertiesView.pgm()
        self._pagePropertyId = ""
        self._groupXmlElementStr = ''
        self._newGroupXmlElementStr = ''
        self._canvasId = ''
        self._objectId = ''
        # properties
        self._type = None
        self._scale = None
        self._orientation = None
        self._properties = { # "type": self._type - always disabled
            "scale": self._scale
            #"orientation": self._orientation
        }

    def page(self): return self._page
    def pgm(self): return self._pgm
    def groupXmlElementStr(self): return self._groupXmlElementStr
    def newGroupXmlElementStr(self): return self._newGroupXmlElementStr

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

    def setGroupPropertyPage(self, pageType, propertyId, headerText, groupXmlElementNot):
        self._propertiesView.clearPropertyPage(headerText, pageType, pageType, 0, propertyId)

        newItem = propertyId != self._pagePropertyId
        self._pagePropertyId = propertyId

        propertyIdSplit = propertyId.split(PropertyIdSeparator)
        if propertyIdSplit and len(propertyIdSplit) == 2:
            self._canvasId = propertyIdSplit[0]
            self._objectId = propertyIdSplit[1]

            canvas = self._application.getCanvasForCanvasId(self._canvasId)
            if canvas:
                groupXmlElementStr = canvas.SaveObjectById(self._objectId)
                groupXmlElement = xut.xmlElement(groupXmlElementStr)
                
                ref = 'G' + PropertyRefSeparator +str(self._canvasId) + PropertyRefSeparator + str(self._objectId) + PropertyChildSeparator

                # Group Type (for typed groups) - not Enabled
                type = groupXmlElement.getAttribute("type")
                if not self._type:
                    self._type = wxpg.StringProperty("Group Type", ref + 'type')
                    self._type.SetHelpString("The type of group - given when group defined (i.e. is not an anonymous group)")
                    self._page.Append(self._type)
                if self._type:
                    if type:
                        self._type.SetName(ref + 'type')
                        self._type.SetValue(type)
                        self._type.Hide(False)
                    else:
                        self._type.Hide(True)
                    self._type.Enable(False)

                # Orientation
                orientation = groupXmlElement.getAttribute("orientation")
                if not orientation:
                    orientation = "normal"
                #print("*** orientation="+str(orientation))
                if not self._orientation:
                    self._orientation = OrientationProperty("Orientation", ref + "orientation", value=orientation)
                    self._orientation.SetHelpString("Orientation (rotation or mirroring) for the group (from normal state)")
                    self._page.Append(self._orientation)
                else:
                    self._orientation.setNameAndValue(ref + "orientation", orientation)

                # Scale
                scale = groupXmlElement.getAttribute("scale")
                if not scale:
                    scale = "1.0,1.0"
                if not self._scale:
                    self._scale =  ScaleProperty(self, "Scale", ref + "scale", value=scale)
                    self._scale.SetHelpString("Scale for width and height of the group when in normal orientation")
                    self._page.Append(self._scale)
                else:
                    self._scale.setValue(ref + "scale", scale)
                    if newItem:
                        self._page.Collapse(self._scale)

        self.checkMode()

    def updateProperties(self, pageType, category, moduleId, propertyId, propertyTag, newValue):
        propertyIdSplit = propertyId.split(PropertyIdSeparator)
        if propertyIdSplit and len(propertyIdSplit) == 2:
            canvasId = int(propertyIdSplit[0])
            objectId = int(propertyIdSplit[1])
            headerText = None # don't change current header
            self.setGroupPropertyPage(pageType, propertyId, headerText)

    def getGroupPropertyChange(self, propertyTag, newValue):
        canvas = self._application.getCanvasForCanvasId(self._canvasId)
        self._groupXmlElementStr = canvas.SaveObjectById(self._objectId)
        groupXmlElement = xut.xmlElement(self._groupXmlElementStr)

        if propertyTag == 'scale':
            groupXmlElement.setAttribute("scale", newValue)
        if propertyTag == 'orientation':
            orientation = OrientationProperty.GetOrientation(newValue)
            groupXmlElement.setAttribute("orientation", orientation)

        self._newGroupXmlElementStr = groupXmlElement.xml()
        return self._groupXmlElementStr, self._newGroupXmlElementStr
