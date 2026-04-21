#! /usr/bin/python

import copy
import wx
import wx.propgrid as wxpg

from .coreproperties import CompoundProperty, FlagsProperty, PROPERTY_DEFAULT_COLOUR, PROPERTY_STANDARD_COLOUR
from .eslvaluestrproperty import ESLValueStrProperty, ESLValueStrPropertyButtonEditor
from ...esl import parseesl
from ...application.eslvalue import ESLValue

_SIGN_VALUES = ["plus", "minus"]

class PortProperty(wxpg.PGProperty, CompoundProperty):
    Prop_helps = [
        "Short tag-name for this port of the simulation entity (if defined).",
        "The value associated with this port has this data-type.",
        "An ESL identifier (A..Z 0..9 _) used an output port in ESL code." +
            "\nThe ESL Name must be unique (in 28chars) in its scope (model, submodel)." +
            "\nIf not supplied an ESL name will be generated (shown with an asterisk).",
        "Description for the port{0}.\nNote: This is not used in generated ESL.",
        "Initial value for the segment call output's variable." +
            "\nNote, this will override any default Initial Value which have been set for a diagram segment on the corresponding Output Argument simulation entity."
            "\nFor an Array/Matrix, scalar elements separated by commas, must have the full number of elements." +
            "\nFor a 2D/3D Array/Matrix you may enclose in square brackets for row-major order (the default), or specifically enclose with slashes for column-major order.",
        "Arithmetic sign for the port.",
        "Resolve a generic array dimensions to a fixed number of elements per dimension." +
            "\nSet this to resolve an ambiguity - i.e. if port not connected to an input with fixed dimensionality." +
            "\nFor a universal dimensionality (as for a function call result) enter \"SCALAR\" (or \"-\") to set to a scalar."
    ]
    ExtraDescriptionHelp = "\nIf this field is set blank it will inherit the from the subprogram's argument Arg Description if set (shown with an asterisk)"
    FullShowAnnotations = [ 'Id', 'Description', 'Tag', 'ESL Name', 'Initial Value']
    FullAnnotationBits = [1, 2, 4, 8, 16]
    FullAnnotationHints = ["Include the port identifier (number) in the port's annotation",
                           "Include the description (if given) in the port's annotation",
                           "Include the short tag-name for the port in its annotation",
                           "Include the name to be used in generated ESL in the ports's annotation\nThis is the value given for the ESL Name property or the generated name",
                           "Include the initial value for the segment output port in the port's annotation"]

    def __init__(self, view, portRef, port):
        CompoundProperty.__init__(self)
        self._view = view
        self._portRef = portRef
        self._port = port.detachedCopy(port.parent())
        self._entity = port.parent()
        self._datatype = self._port.datatype()
        self._parseEsl = parseesl.ParseEsl()
        self._includeESLName = True
        self._includeInitialValue = False
        self._includeFixDimensions = False
        # properties
        self._tag = None
        self._datatypeProp = None
        self._eslname = None
        self._description = None
        self._initialValueProp = None
        self._signProp = None
        self._fixDimensionsProp = None
        self._annotationsProp = None
        if self._port.kind() == "ESL-value" and self._port.direction() == "input":
            self._includeESLName = False
        subprogram = None
        if self._entity.isCall():
            subprogram = self._entity.subprogram()
            if subprogram.callableType() == 'segment' and self._port.direction() == "output":
                self._includeInitialValue = True
        if self._port.isGeneric():
            self._includeFixDimensions = True
        label = 'Port ' + self._port.id() + '(' + self._port.direction() + ')'
        wxpg.PGProperty.__init__(self, label, portRef)

        self._tag = wxpg.StringProperty("Tag", "tag", value=self._port.tag())
        self._tag.SetHelpString(PortProperty.Prop_helps[0])
        self._tag.Enable(False)
        self.AddPrivateChild(self._tag) # 0 Tag

        datatypeDimensions = self._port.datatype()
        if self._port.dimensions():
            datatypeDimensions += "(" + self._port.dimensions() + ")"
        self._datatypeProp = wxpg.StringProperty("Data Type", "datatype", value=datatypeDimensions)
        self._datatypeProp.SetHelpString(PortProperty.Prop_helps[1])
        self._datatypeProp.Enable(False)
        self.AddPrivateChild(self._datatypeProp) # 1 Data Type

        self._eslname = wxpg.StringProperty("ESL Name", 'eslname', value=self._port.eslname())
        self._eslname.SetHelpString(PortProperty.Prop_helps[2])
        self.AddPrivateChild(self._eslname) # 2 ESL Name
        if not self._includeESLName:
            self._eslname.Hide(True)

        self._description = wxpg.StringProperty("Description", 'description', value=self._port.description())
        extraDescriptionHelp = ""
        descriptionHelp = PortProperty.Prop_helps[3]
        if self._entity.isCall():
            subprogram = self._entity.subprogram()
            if subprogram and subprogram.subprogramBaseType() == "diagram":
                extraDescriptionHelp = PortProperty.ExtraDescriptionHelp
        descriptionHelp = descriptionHelp.format(extraDescriptionHelp)
        self._description.SetHelpString(descriptionHelp)
        self.AddPrivateChild(self._description) # 3 Description

        self._initialValueProp = ESLValueStrProperty("Initial Value", 'initialValue', eslValue=self._port.eslValue(), helpString=PortProperty.Prop_helps[4])
        self.AddPrivateChild(self._initialValueProp) # 4 Initial Value
        propertyGrid = self._view.pgm().GetGrid()
        ESLValueStrPropertyButtonEditor.SetEditorToProperty(self._initialValueProp, propertyGrid)
        if not self._includeInitialValue:
            self._initialValueProp.Hide(True)

        self._signProp = wxpg.EnumProperty("Sign", 'sign', _SIGN_VALUES, [0, 1])
        self._signProp.SetHelpString(PortProperty.Prop_helps[5])
        self.AddPrivateChild(self._signProp) # 5 Sign
        if self._port.sign():
            self._signProp.SetValue(_SIGN_VALUES.index(self._port.sign()))
        else:
            self._signProp.Hide(True)

        self._fixDimensionsProp = wxpg.StringProperty("Fix Dimensions", 'fix-dimensions', value="")
        self._fixDimensionsProp.SetHelpString(PortProperty.Prop_helps[6])
        self.AddPrivateChild(self._fixDimensionsProp) # 6 Fix Dimensions
        if not self._includeFixDimensions:
            self._fixDimensionsProp.Hide(True)

        annotations = self.get_annotations()
        showAnnotations = PortProperty.FullShowAnnotations.copy()
        annotationBits = PortProperty.FullAnnotationBits.copy()
        annotationHints = PortProperty.FullAnnotationHints.copy()
        if not self._includeInitialValue:
            showAnnotations = showAnnotations[:4]
            annotationBits = annotationBits[:4]
            annotationHints = annotationHints[:4]
        if not self._includeESLName:
            showAnnotations = showAnnotations[:3] + showAnnotations[4:]
            annotationBits = annotationBits[:3] + annotationBits[4:]
            annotationHints = annotationHints[:3] + annotationHints[4:]
        self._annotationsProp = FlagsProperty("Annotations", 'annotations', showAnnotations, annotationBits, annotations)
        self._annotationsProp.SetHelpString("Show an annotation for the port on the diagram")
        self._annotationsProp.setHelpStrings(annotationHints)
        self._view.pgm().SetPropertyReadOnly(self._annotationsProp, True, wxpg.PG_DONT_RECURSE)
        self.AddPrivateChild(self._annotationsProp) # 7 Annotations

        self.m_value = self.ValueToString(None, None)

        self._childIndexChanged = -1
        self._priorPropertyValue = self.propertyValue()

        self._view.pgm().SetPropertyReadOnly(self, True, wxpg.PG_DONT_RECURSE)
        self.setCellBgColNoEdit()

    def enableWithChildren(self, enable):
        self.Enable(enable) # this sets all children
        if enable: # disable unsettable (view-only) properties
            self._tag.Enable(False)
            self._datatypeProp.Enable(False)

    def portRef(self):
        return self._portRef

    def port(self):
        return self._port

    def setPortProperty(self, portRef, port):
        self._portRef = portRef
        self.SetName(portRef)
        self._port = port.detachedCopy(port.parent())
        self._entity = port.parent()
        self._datatype = self._port.datatype()
        if self._port.kind() == "ESL-value" and self._port.direction() == "input":
            self._includeESLName = False
        if self._port.isGeneric():
            self._includeFixDimensions = True
        label = 'Port ' + self._port.id() + '(' + self._port.direction() + ')'
        self.SetLabel(label)
        self._priorPropertyValue = self.propertyValue()
        self.Item(2).Hide(not self._includeESLName)
        self.Item(4).Hide(not self._includeInitialValue)
        self.Item(5).Hide(not self._port.sign())
        self.Item(6).Hide(not self._includeFixDimensions)
        self.RefreshChildren()

    def childIndexChanged(self):
        return self._childIndexChanged

    def priorPropertyValue(self):
        return self._priorPropertyValue

    def propertyValue(self):
        result = self._port.save(None, 0, True)
        return result

    def updateFields(self, propertyValue):
        self._port.loadData(propertyValue, suppressAddName=True)
        self.RefreshChildren()
        pass

    def GetClassName(self):
        return self.__class__.__name__

    def ValueToString(self, value, flags):
        if self._port.tag():
            valStr = self._port.tag()
        else:
            valStr = '#' + self._port.id()
        if self._port.eslname():
            valStr += ':' + self._port.eslname()
        if self._includeInitialValue:
            initialValue = self._port.eslValue().getInitialisationValue()
            if initialValue:
                valStr += initialValue
        sign = self._port.sign()
        if sign:
            valStr += "|+" if sign == "plus" else "|-"
        return valStr

    def RefreshChildren(self):
        # 0 Tag
        # 1 Data Type
        datatypeDimensions = self._port.datatype()
        if self._port.dimensions():
            datatypeDimensions += "(" + self._port.dimensions() + ")"
        self.Item(1).SetValue(datatypeDimensions)
        # 2 ESL Name
        self.Item(2).SetValue(self._port.eslname())
        self.checkGeneratedEslName()
        # 3 Description
        self.Item(3).SetValue(self._port.description())
        self.checkInheritedDescription()
        # 4 Initial Value
        self.Item(4).SetValue(self._port.eslValue())
        self.Item(4).checkShowFeatures()
        # 5 Sign
        sign = self._port.sign()
        if sign in _SIGN_VALUES:
            self.Item(5).SetValue(sign)
        # 6 Fix Dimensions
        self.Item(6).SetValue(self._port.fixDimensions())
        # 7 Annotations
        annotations = self.get_annotations()
        self.Item(7).SetValue(annotations)

    def ChildChanged(self, thisValue, childIndex, childValue):
        # 0 Tag
        # 1 Data Type
        self._priorPropertyValue = self.propertyValue()
        self._childIndexChanged = childIndex
        # 2 ESL Name
        if childIndex == 2:
            self._port.set_eslname(childValue)
        # 3 Description
        elif childIndex == 3:
            self._port.set_description(childValue)
        # 4 Initial Value
        elif childIndex == 4:
            self._port.eslValue().loadStr(childValue, checkValidity=False)
        if childIndex in [4]:
            self.Item(4).checkShowFeatures()
        # 5 Sign
        elif childIndex == 5:
            sign = "plus" if childValue == 0 else "minus"
            self._port.set_sign(sign)
        # 6 Fix Dimensions
        elif childIndex == 6:
            self._port.set_fixDimensions(childValue)
        # 7 Annotations
        elif childIndex == 7:
            self._port.set_show_id("true" if (childValue & 1) else "false")
            self._port.set_show_description("true" if (childValue & 2) else "false")
            self._port.set_show_tag("true" if (childValue & 4) else "false")
            self._port.set_show_eslname("true" if (childValue & 8) else "false")
            self._port.set_show_initialValue("true" if (childValue & 16) else "false")
        return None

    def get_annotations(self):
        annotations = 0
        if self._port.show_id() == "true": annotations += 1
        if self._port.show_description() == "true": annotations += 2
        if self._port.show_tag() == "true": annotations += 4
        if self._port.show_eslname() == "true": annotations += 8
        if self._port.show_initialValue() == "true": annotations += 16
        return annotations

    def checkGeneratedEslName(self):
        if self._includeESLName and not self._port.eslname():
            tag = self._port.tag()
            if not tag:
                tag = 'O' + str(self._port.id())
            genEslName = self._entity.makeEslName(tag)
            self.Item(2).SetValue(genEslName)
            self.Item(2).GetCell(0).SetBgCol(PROPERTY_DEFAULT_COLOUR)
            self.Item(2).GetCell(1).SetBgCol(PROPERTY_DEFAULT_COLOUR)
            self.Item(2).SetLabel("ESL Name *")
        else:
            self.Item(2).GetCell(0).SetBgCol(PROPERTY_STANDARD_COLOUR)
            self.Item(2).GetCell(1).SetBgCol(PROPERTY_STANDARD_COLOUR)
            self.Item(2).SetLabel("ESL Name")

    def checkInheritedDescription(self):
        description = self._port.description()
        inherited = False
        if not description: # See if port inherits description from submodel
            if self._entity.isCall():
                subprogram = self._entity.subprogram()
                if subprogram:
                    id = self._port.id()
                    subPorts = subprogram.getPorts()
                    subPort = subPorts.get(id)
                    if subPort:
                        description = subPort.description()
                        if description:
                            inherited = True
        if inherited:
            self.Item(3).SetValue(description)
            self.Item(3).GetCell(0).SetBgCol(PROPERTY_DEFAULT_COLOUR)
            self.Item(3).GetCell(1).SetBgCol(PROPERTY_DEFAULT_COLOUR)
            self.Item(3).SetLabel("Description *")
        else:
            self.Item(3).GetCell(0).SetBgCol(PROPERTY_STANDARD_COLOUR)
            self.Item(3).GetCell(1).SetBgCol(PROPERTY_STANDARD_COLOUR)
            self.Item(3).SetLabel("Description")

    def OnEvent(self, propgrid, wnd_primary, event):
        if not self.IsExpanded() and isinstance(event, wx.ChildFocusEvent):
            self.checkInheritedDescription()
            self.checkGeneratedEslName()
            propgrid.EnsureVisible(self.Item(0))
        return True
