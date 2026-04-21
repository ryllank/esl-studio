#! /usr/bin/python

from collections import OrderedDict

import wx
import wx.propgrid as wxpg

from ...config import Config
from ... import utils as Utils
from ...application.eslvalue import ESLValue
from ...application.attribute import Attribute
from ...esl.parseesl import ParseEsl
from ...esl.esl import EslBaseTypeNames, EslTypeNames
from ...propertiescontrol import PropertyRefSeparator
from .coreproperties import CompoundProperty, LogicalProperty, FlagsProperty, PROPERTY_STANDARD_COLOUR, PROPERTY_DEFAULT_COLOUR, PROPERTY_ALERT_COLOUR, PROPERTY_UNCHECKED_COLOUR
from ..properties.eslvaluestrproperty import ESLValueStrProperty, ESLValueStrPropertyButtonEditor

def makeAttributeProperty(view, attRef, attribute, propertyForm=None):
    valueEnumProperty = None
    if propertyForm is None and attribute.show_valueOnTop() == 'true':
        if attribute.datatype().title() in ['Enum', 'Boolean', 'String']:
            propertyForm = attribute.datatype().title()
        else:
            propertyForm = 'ESLValue'
            # Also make the ValueEnum form
            valueEnumProperty, noProperty = makeAttributeProperty(view, attRef+Attribute.ValueEnumRefExtn, attribute, 'ValueEnum')
    if propertyForm == 'ESLValue':
        attributeProperty = AttributePropertyFormESLValue(view, attRef, attribute)
    elif propertyForm == 'ValueEnum':
        attributeProperty = AttributePropertyFormValueEnum(view, attRef, attribute)
    elif propertyForm == 'Enum':
        attributeProperty = AttributePropertyFormEnum(view, attRef, attribute)
    elif propertyForm == 'Boolean':
        attributeProperty = AttributePropertyFormBoolean(view, attRef, attribute)
    elif propertyForm == 'String':
        attributeProperty = AttributePropertyFormString(view, attRef, attribute)
    else:
        #propertyForm = 'Display'
        attributeProperty = AttributePropertyFormDisplay(view, attRef, attribute)
    return attributeProperty, valueEnumProperty

class AttributeValueEnumProperty(wxpg.EnumProperty):
    def __init__(self, attributeProperty, label, name, enumLabels=[], values=[], value=0):
        wxpg.EnumProperty.__init__(self, label, name, enumLabels, values, value)
        self._attributeProperty = attributeProperty
        self._priorValue = ""
        self._postValue = ""
        self._dropdownIx = 0

    def OnEvent(self, propgrid, wnd_primary, event):
        #print(">>>AttributeValueEnumProperty event=" + str(event))
        if event.IsCommandEvent():
            type = event.GetEventType()
            #if type < 10311:
            #    print(">>>AttributeValueEnumProperty event="+str(event)+" type="+str(event.GetEventType())+" category="+str(event.GetEventCategory()))
            # type 10218 (combo opens [not wxEVT_TREE_KEY_DOWN] but wxEVT_PG_CHANGING
            # type 10219 (combo closes [not wxEVT_TREE_ITEM_ACTIVATED] but wxEVT_PG_CHANGED
            # type 10214 (combo has selection [not wxEVT_TREE_ITEM_COLLAPSED - not necessarily changed
            #x = wx.wxEVT_COMBOBOX #=10020+194 10214
            #x = wx.wxEVT_COMBOBOX_CLOSEUP #= 10025+194 10219
            #x = wx.wxEVT_COMBOBOX_DROPDOWN #= 10024+194 10218
            if type == wx.wxEVT_COMBOBOX_DROPDOWN: #10218:
                # Workaround to to set correct dropdown selection. It seems to happen when a top level (not child) property.
                if self._attributeProperty._propertyForm == 'ValueEnum':
                    self._dropdownIx = event.EventObject.GetSelection()
                    selectionIx = self.GetValue()
                    if self._dropdownIx != selectionIx:
                        event.EventObject.SetSelection(selectionIx)
                self._priorValue = event.EventObject.GetValue()  # this is the text
            if type == wx.wxEVT_COMBOBOX: #10214:
                #self._postValue = self.GetValue()   # this hasnt changed at this time so cant use below to test if selection not changed
                self._postValue = event.EventObject.GetValue() # this has
                if self._priorValue == self._postValue: # selection not changed
                    self._attributeProperty.onRepickedAttributeValueEnum(self._postValue, self.GetValue())
                elif self._attributeProperty._propertyForm == 'ValueEnum':
                    currentIx = event.EventObject.GetSelection()
                    if currentIx == self._dropdownIx: # A top level (not child) property doesnt recognise this may be a change so explicitly fire change property event.
                        valid = self._attributeProperty.firePropertyChangeEventForEnumValueChange(self._postValue, self._priorValue)
        return True

class AttributeProperty(wxpg.PGProperty, CompoundProperty):
    def __init__(self, view, attRef, attribute, propertyForm=""):
        self._propertyForm = propertyForm
        CompoundProperty.__init__(self)
        self._view = view
        self._attRef = attRef
        self._attribute = attribute.detachedCopy(attribute.parent())
        self._valueOnTop = self._attribute.show_valueOnTop() == 'true'
        self._useOtherProperty = None
        self._entity = attribute.parent()
        self._datatype = self._attribute.datatype()
        self._dimensions = self._attribute.dimensions()
        self._dimensionality = ParseEsl.get_dimensionality(self._dimensions)
        diagramInfo = self._entity.parent()
        self._module = diagramInfo.parent()
        self._sources = []
        self._sourceEnumValues = {}
        # properties
        self._tagChild = None
        self._datatypeChild = None
        self._eslnameChild = None
        self._sourceChild = None
        self._valueChild = None
        self._valueEnumChild = None
        self._annotationsChild = None

        self.SetHelpString(attribute.hint())

        self._tagChild = wxpg.StringProperty("Tag", "tag", value=attribute.tag())
        self._tagChild.SetHelpString("Short tag-name for this attribute of the simulation entity.")
        self._tagChild.Enable(False)
        self.AddPrivateChild(self._tagChild)                 # 0 Tag

        datatypeDimensions = self._datatype
        if self._dimensions:
            datatypeDimensions += "(" + self._dimensions + ")"
        self._datatypeChild = wxpg.StringProperty("Data Type", "datatype", value=datatypeDimensions)
        self._datatypeChild.SetHelpString("The value for this attribute must have this data-type.")
        self._datatypeChild.Enable(False)
        self.AddPrivateChild(self._datatypeChild)        # 1 Data Type
        doHide = self._attribute.hide_datatype() == "true"
        self._datatypeChild.Hide(doHide)

        self._eslnameChild = wxpg.StringProperty("ESL Name", 'eslname', value=attribute.eslname())
        self._eslnameChild.SetHelpString("An ESL identifier (A..Z 0..9 _) for the attribute." +
                           "\nThe ESL Name must be unique (in 28chars) in its scope (model, submodel)." +
                           "\nIf not supplied an ESL name will be generated (shown with an asterisk).")
        self.AddPrivateChild(self._eslnameChild)             # 2 ESL Name
        self.checkGeneratedEslName()
        doHide = self._attribute.has_eslname() == "false"
        self._eslnameChild.Hide(doHide)

        self._sources, self._sourceEnumValues = self._attribute.get_valid_sources_and_sourceEnumValues()
        source = self._attribute.check_valid_source_and_enumValue(self._sources, self._sourceEnumValues)
        self._lastValueValueStr = ""
        self._lastSourceEnumValue = OrderedDict()
        self._lastSource = source
        if source == Attribute.SourceValue:
            self._lastValueValueStr = self._attribute.eslValue().saveStr()
        if source != Attribute.SourceValue:
            self._lastSourceEnumValue[source] = self._attribute.eslValue().valueStr()
        self._sourceChild = wxpg.EnumProperty("Source", "source", self._sources, list(range(len(self._sources))), value=self._sources.index(source))
        self._sourceChild.SetHelpString("Where the value for this attribute comes from:" +
                           "\nValue - when the actual value is given" +
                           "\nParameter - when the module has suitable parameter(s) that can be assigned" +
                           "\nName of a Package - when used (imported) into the module" +
                           "\nRESERVED - when the attribute is assigned the value of a simulation parameter" +
                           "\nOutput - for a named output in the module (of the right data type).")
        self.AddPrivateChild(self._sourceChild)              # 3 Source
        if len(self._sources) < 2:
            self._sourceChild.Enable(False)
        doHide = self._attribute.has_sources() == "None"
        self._sourceChild.Hide(doHide)

        self.setupValueProperty(source) # may add child items 4 Value and 5 ValueEnum

        annotations = self.get_annotations()
        showAnnotations, showAnnotationFlags, annotationHints = self.checkAnnotations()
        self._annotationsChild = FlagsProperty("Annotations", 'annotations', showAnnotations, showAnnotationFlags, annotations)
        self._annotationsChild.SetHelpString("Show an annotation for the attribute on the diagram.")
        self._annotationsChild.setHelpStrings(annotationHints)
        self._view.pgm().SetPropertyReadOnly(self._annotationsChild, True, wxpg.PG_DONT_RECURSE)
        self.AddPrivateChild(self._annotationsChild)         # 4 or 6 Annotations
        doHide = self._attribute.has_annotations() == "false"
        self._annotationsChild.Hide(doHide)

        self._childIndexChanged = -1
        self._priorPropertyValue = self.propertyValue()

        self._view.pgm().Bind(wxpg.EVT_PG_CHANGING, self.OnPropGridChanging)
        if not self._valueOnTop:
            self.setCellBgColNoEdit()

    def setTopESLValueVisibility(self):
        topValueShow = True
        if self._propertyForm == 'ESLValue' or self._propertyForm == 'ValueEnum':
            entityAttribute = self._entity.getAttribute(self._attribute.tag())
            source = entityAttribute.source()
            if self._propertyForm == 'ESLValue' and source != Attribute.SourceValue:
                topValueShow = False
            if self._propertyForm == 'ValueEnum' and source == Attribute.SourceValue:
                topValueShow = False
            self.Hide(not topValueShow)
        return topValueShow

    def valueStrOrDefault(self, checkTopLevelFeatures=True):
        displayStr = self._attribute.valueStr()
        if not displayStr:
            displayStr = self._attribute.eslValue().defaultValueStr()
        return displayStr

    def checkTopLevelValueFeatures(self):
        feature = ''
        if self._attribute.valueStr() == "" and self._attribute.eslValue().defaultValueStr() != "":
            feature = 'default'
        else:
            if self._datatype.upper() in EslTypeNames or self._datatype == "ESLValue":
                source = self._attribute.source()
                if not source:
                    source = Attribute.SourceValue
                if source == Attribute.SourceValue:
                    feature = self._attribute.eslValue().validity()
        self.checkTopLevelFeatures(feature)

    def checkTopLevelFeatures(self, feature):
        label = self._attribute.description()
        priorLabel = self.GetLabel()
        priorBgColour = self.GetCell(0).GetBgCol()
        helpString = self._attribute.hint()
        bgColour = PROPERTY_STANDARD_COLOUR
        if feature == 'default':
            bgColour = PROPERTY_DEFAULT_COLOUR
            label += " *"
            if helpString: helpString += "\n"
            helpString += ESLValueStrProperty.DefaultValueHelpAddition
        elif feature == 'invalid':
            bgColour = PROPERTY_ALERT_COLOUR
            label += " !"
            if helpString: helpString += "\n"
            helpString += ESLValueStrProperty.InvalidValueHelpAddition
            validityMsg = self._attribute.eslValue().validityMsg()
            if validityMsg:
                helpString += "\n" + validityMsg
        elif feature == 'unchecked':
            bgColour = PROPERTY_UNCHECKED_COLOUR
            label += " ?"
            if helpString: helpString += "\n"
            helpString += ESLValueStrProperty.UncheckedValueHelpAddition
        #print("<AttributeProperty.checkTopLevelFeatures label="+label+" priorLabel="+priorLabel+" changed="+str(bool(label != priorLabel)))
        if label != priorLabel or bgColour != priorBgColour:
            self.GetCell(0).SetBgCol(bgColour)
            self.GetCell(1).SetBgCol(bgColour)
            self.SetLabel(label)
            self.SetHelpString(helpString)
            grid = self.GetGrid()
            if grid:
                grid.RefreshProperty(self)
                pass
            pass
        self.RefreshEditor()

    def enableWithChildren(self, enable):
        self.Enable(enable) # this sets all children
        if enable: # disable unsettable (view-only) properties
            self._tagChild.Enable(False)
            self._datatypeChild.Enable(False)
        # handle ones selectively enabled/disabled
        self._sourceChild.Enable(enable and len(self._sources) >= 2)

    def attRef(self):
        return self._attRef

    def attribute(self):
        return self._attribute

    def entity(self):
        return self._entity

    def propertyForm(self):
        return self._propertyForm

    def attTag(self):
        attRefBase = self._attRef
        if attRefBase.endswith(Attribute.ValueEnumRefExtn):
            attRefBase = attRefBase[:-len(Attribute.ValueEnumRefExtn)]
        attTag = ""
        pos = attRefBase.rfind(PropertyRefSeparator)
        if pos >= 0:
            attTag = attRefBase[pos + 1:]
        return attTag

    def setAttributeProperty(self, attRef, attribute):
        #print(">setAttributeProperty attRef="+attRef+" attr-ix="+str(self.GetIndexInParent())+" children="+str(self.GetChildCount()))
        self._attRef = attRef
        self.SetName(attRef)
        self._attribute = attribute.detachedCopy(attribute.parent())
        self._entity = attribute.parent()
        self._datatype = self._attribute.datatype()
        self._dimensions = self._attribute.dimensions()
        diagramInfo = self._entity.parent()
        self._module = diagramInfo.parent()
        self.SetLabel(attribute.description())
        self._priorPropertyValue = self.propertyValue()
        self._useOtherProperty = None
        self._tagChild.SetValue(attribute.tag())
        datatypeDimensions = self._datatype
        if self._dimensions:
            datatypeDimensions += "(" + self._dimensions + ")"
        self._datatypeChild.SetValue(datatypeDimensions)
        doHide = self._attribute.hide_datatype() == "true"
        self._datatypeChild.Hide(doHide)
        self._eslnameChild.SetValue(attribute.eslname())
        doHide = self._attribute.has_eslname() == "false"
        self._eslnameChild.Hide(doHide)
        #print("-setAttributeProperty _eslnameChild doHide="+str(doHide)+" vis="+str(self._eslnameChild.IsVisible())+" index="+str(self._eslnameChild.GetIndexInParent()))
        self._sources, self._sourceEnumValues = self._attribute.get_valid_sources_and_sourceEnumValues()
        source = self._attribute.check_valid_source_and_enumValue(self._sources, self._sourceEnumValues)
        self._lastSource = source
        if source == Attribute.SourceValue:
            if self._lastValueValueStr == "":
                self._lastValueValueStr = self._attribute.eslValue().saveStr()
        else:
            if self._lastSourceEnumValue.get(source) is None:
                self._lastSourceEnumValue[source] = self._attribute.eslValue().valueStr()
        self._sourceChild.SetChoices(wxpg.PGChoices(self._sources, list(range(len(self._sources)))))
        self._sourceChild.SetValue(self._sources.index(source))
        self._sourceChild.Enable(len(self._sources) > 1)
        doHide = self._attribute.has_sources() == "None"
        self._sourceChild.Hide(doHide)
        self.setupValueProperty(source)
        annotations = self.get_annotations()
        showAnnotations, showAnnotationFlags, annotationHints = self.checkAnnotations()
        self._annotationsChild.SetChoices(wxpg.PGChoices(showAnnotations, showAnnotationFlags))
        self._annotationsChild.SetValue(annotations)
        self._annotationsChild.setHelpStrings(annotationHints)
        doHide = self._attribute.has_annotations() == "false"
        self._annotationsChild.Hide(doHide)
        self._childIndexChanged = -1
        self.RefreshChildren()
        self.checkTopLevelValueFeatures()

    def childIndexChanged(self):
        return self._childIndexChanged

    def priorPropertyValue(self):
        return self._priorPropertyValue

    def getOtherProperty(self):
        otherProperty = None
        if self._propertyForm == 'ESLValue' or self._propertyForm == 'ValueEnum':
            otherAttRef = ""
            if self._propertyForm == 'ESLValue':
                otherAttRef = self._attRef + Attribute.ValueEnumRefExtn
            elif self._propertyForm == 'ValueEnum':
                if self._attRef.endswith(Attribute.ValueEnumRefExtn):
                    otherAttRef = self._attRef[:-len(Attribute.ValueEnumRefExtn)]
            otherProperty = self._view.page().GetProperty(otherAttRef)
        return otherProperty

    def propertyValue(self):
        if self._useOtherProperty is not None:
            result = self._useOtherProperty._attribute.save(None, 0, True)
        else:
            result = self._attribute.save(None, 0, True)
        return result

    def setupValueProperty(self, source):
        if not self._valueOnTop:
            self.setupChildValueProperty(source)
        else:
            self.setupTopValueProperty(source)

    def setupChildValueProperty(self, source):
        update = self._valueChild is not None
        if not self._datatype:
            raise Exception("Attribute has no Data Type")
        eslValue:ESLValue = self._attribute.eslValue()
        displayStr = self.valueStrOrDefault()
        datatypeUpper = self._datatype.upper()
        doHideValue = False
        if datatypeUpper in EslTypeNames or self._datatype == "ESLValue":
            if not self._valueChild:
                self._valueChild = ESLValueStrProperty("Value", 'value', eslValue=eslValue,
                    helpString="Enter a value for the attribute - consistent with its Data Type and Dimensions.")
                propertyGrid = self._view.pgm().GetGrid()
                ESLValueStrPropertyButtonEditor.SetEditorToProperty(self._valueChild, propertyGrid)
                self._valueChild.checkShowFeatures()
            else:
                self._valueChild.SetValue(eslValue)
            doHideValue = source != Attribute.SourceValue
        else:
            if self._dimensions:
                raise Exception("Attribute for Data Type \""+self._datatype+"\" has Dimensions ("+self._dimensions+")")
            if self._datatype == "Boolean": # treat as a truthValue Bool and use BoolProperty with checkbox
                boolValue = True if displayStr.lower() == "true" else False
                if not self._valueChild:
                    self._valueChild = wxpg.BoolProperty("Value", 'value', value=boolValue)
                    self._valueChild.SetAttribute(wxpg.PG_BOOL_USE_CHECKBOX, True)
                else:
                    self._valueChild.SetValue(boolValue)
            elif self._datatype == "Enum":
                if not self._valueChild:
                    self._valueChild = wxpg.EnumProperty("Value",  'value')
                enums = self._attribute.enums()
                enumValues = Attribute.splitEnums(enums)
                self._valueChild.SetChoices(wxpg.PGChoices(enumValues, list(range(len(enumValues)))))
                enumIx = 0
                if displayStr in enumValues:
                    enumIx = enumValues.index(displayStr)
                self._valueChild.SetValue(enumIx)
            else: # treat anything else as a plain String (and use StringProperty)
                if not self._valueChild:
                    self._valueChild = wxpg.StringProperty("Value", 'value', value=displayStr)
                else:
                    self._valueChild.SetValue(displayStr)
            self._valueChild.SetHelpString("Enter a value for the attribute - consistent with its Data Type.")
        if not update:
            self.AddPrivateChild(self._valueChild)           # 4 Value(by data)

        self._valueChild.Hide(doHideValue)
        #print("-setupValueProperty _valueChild doHide="+str(doHideValue)+" vis="+str(self._valueChild.IsVisible())+" index="+str(self._valueChild.GetIndexInParent()))

        doHideValueEnum = True
        if self._valueEnumChild is None:
            self._valueEnumChild = AttributeValueEnumProperty(self, "Value", 'valueEnum')
            self._valueEnumChild.SetHelpString("Select the value for the attribute - depending on the source.")
        enumValue = "Dummy"
        enumValues = ["Dummy"]
        if datatypeUpper in EslTypeNames or self._datatype == "ESLValue":
            if source != Attribute.SourceValue:
                enumValue = displayStr
                if enumValue.endswith(")"):
                    enumValue += "..."
                enumValues = self._attribute.get_initial_enumValues(source, self._sources, self._sourceEnumValues)
                if enumValue not in enumValues:
                    attrValueEnum, baseEnumValue, reference = Attribute.check_enumValue_reference(enumValue)
                    if baseEnumValue:
                        idx = Attribute.get_enumValue_index(baseEnumValue, enumValues)
                        if idx >= 0:
                            enumValue = baseEnumValue + "(" + reference + ")..."
                            enumValues[idx] = enumValue
                if enumValue not in enumValues:
                    if len(enumValues) > 0:
                        enumValue = enumValues[0]
                    else:
                        enumValue = ""
                doHideValueEnum = False
        if enumValue:
            self._valueEnumChild.SetChoices(wxpg.PGChoices(enumValues, list(range(len(enumValues)))))
            self._valueEnumChild.SetValue(enumValues.index(enumValue))
        if not update:
            self.AddPrivateChild(self._valueEnumChild)           # 5 ValueEnum (for variable)
        self._valueEnumChild.Hide(doHideValueEnum)
        #print("<setupValueProperty _valueEnumChild doHide="+str(doHideValueEnum)+" vis="+str(self._valueEnumChild.IsVisible())+" index="+str(self._valueEnumChild.GetIndexInParent()))
        pass

    def setupTopValueProperty(self, source):
        eslValue = self._attribute.eslValue()
        if self._propertyForm == 'ValueEnum':
            if source != Attribute.SourceValue:
                enumValues = self._attribute.get_initial_enumValues(source, self._sources, self._sourceEnumValues)
                enumValue = eslValue.valueStr()
                if enumValue.endswith(")"):
                    enumValue += "..."
                attrValueEnum, baseEnumValue, reference = Attribute.check_enumValue_reference(enumValue)
                is_valid = True
                if enumValue not in enumValues:
                    is_valid = False
                    if baseEnumValue:
                        idx = Attribute.get_enumValue_index(baseEnumValue, enumValues)
                        if idx >= 0:
                            enumValue = baseEnumValue + "(" + reference + ")..."
                            enumValues[idx] = enumValue
                            is_valid = True
                self.SetChoices(wxpg.PGChoices(enumValues, list(range(len(enumValues)))))
                self._attribute.setESLValueForEnumValue(enumValue, is_valid=is_valid)
                self.SetValue(self._attribute.eslValue())
        elif self._propertyForm == 'ESLValue':
            if source == Attribute.SourceValue:
                self.SetValue(eslValue)
        else:
            self.SetValue(eslValue)

    def checkAnnotations(self):
        showAnnotations = [ 'Attribute Name', 'Tag', 'ESL Name', 'Source', 'Value']
        showAnnotationFlags = [1, 2, 4, 8, 16]
        annotationHints = ["Include the attribute name in the attribute's annotation",
                           "Include the short tag-name for the attribute in its annotation",
                           "Include the name to be used in generated ESL in the attribute's annotation\n"+
                                "This is the value given for the ESL Name property or the generated name",
                           "Include source information in the attribute's annotation:\n"+
                                "- When the source is the value property itself, a RESERVED variable (simulation parameter) or a named output variable value this shows same as for value\n"+
                                "- When it is a module parameter or package variable it shows the name of the parameter or package.variable name",
                           "Include the value in the attribute's annotation:\n"+
                                "- When the source is a RESERVED variable (simulation parameter) or a named output variable this shows the variable name\n"+
                                "- When the source is a module parameter or package variable this shows its initial value"
                           ]
        noSourceValueAnnotationHint = "Include the value in the attribute's annotation"
        if self._attribute.has_sources() == "None":
            showAnnotations.remove('Source')
            showAnnotationFlags.remove(8)
            annotationHints.remove(annotationHints[3])
            annotationHints[3] = noSourceValueAnnotationHint
        if self._attribute.has_eslname() == "false":
            showAnnotations.remove('ESL Name')
            showAnnotationFlags.remove(4)
            annotationHints.remove(annotationHints[2])
        return showAnnotations, showAnnotationFlags, annotationHints

    def updateFields(self, propertyValue):
        priorSource = self._attribute.source()
        lastSource = self._lastSource
        otherProperty = None
        useProperty = self
        if self._valueOnTop:
            otherProperty = self._useOtherProperty
            if otherProperty:
                useProperty = otherProperty
                # TEMP check other property is correct one
                temp_otherProperty = self.getOtherProperty()
                if otherProperty != temp_otherProperty:
                    raise Exception("AttributeProperty.updateFields otherProperty != temp_otherProperty")
            # TEMP check got other property when should have and v.v.
            shouldHaveOtherProperty = False
            if (self._propertyForm == 'ESLValue' and lastSource != Attribute.SourceValue):
                shouldHaveOtherProperty = True
            if (self._propertyForm == 'ValueEnum' and lastSource == Attribute.SourceValue):
                shouldHaveOtherProperty = True
            if shouldHaveOtherProperty and otherProperty is None:
                raise Exception("AttributeProperty.updateFields shouldHaveOtherProperty but doesnt"
                                " - propertyForm="+self._propertyForm+" lastSource="+lastSource)
            if not shouldHaveOtherProperty and otherProperty is not None:
                raise Exception("AttributeProperty.updateFields should*NOT*HaveOtherProperty but does"
                                " - propertyForm="+self._propertyForm+" lastSource="+lastSource)
        useProperty._attribute.loadData(propertyValue, suppressAddName=True)
        useProperty.SetValue(useProperty._attribute.eslValue())
        source = useProperty._attribute.source()
        if source != priorSource:
            print("AttributeProperty.checkAnnotations priorSource="+priorSource+" source="+source)
        useProperty.RefreshChildren()

        newESLValueSaveStr = useProperty._attribute.eslValue().saveStr()

        self._useOtherProperty = None

        if source == Attribute.SourceValue and useProperty._propertyForm in ['Display', 'ESLValue']:
            useProperty._lastValueValueStr = newESLValueSaveStr

        if source != Attribute.SourceValue and useProperty._propertyForm in ['Display', 'ValueEnum']:
            useProperty._lastSourceEnumValue[source] = useProperty._attribute.eslValue().valueStr()

        if otherProperty:
            Utils.queueFunctionCall(self.switchTopESLValueVisibility, otherProperty)
        else:
            self.checkTopLevelValueFeatures()
        pass

    def switchTopESLValueVisibility(self, otherProperty):
        self.Hide(True)
        otherProperty.Hide(False)
        otherProperty.checkTopLevelValueFeatures()

    def GetClassName(self):
        return self.__class__.__name__

    def ValueToString(self, value, argFlags=0):
        returnStr = ""
        if argFlags ^ 0:
            returnStr = self.valueStrOrDefault()
        else:
            returnStr =self._attribute.save(None, 0, True)
        return returnStr

    def RefreshChildren(self):
        #print(">RefreshChildren attRef="+self._attRef+" attr-ix="+str(self.GetIndexInParent()))
        # 0 Tag
        # 1 Data Type
        self._eslnameChild.SetValue(self._attribute.eslname())
        self.checkGeneratedEslName()
        source = self._attribute.source()
        if not source:
            source = Attribute.SourceValue
        if source not in self._sources:
            source = self._sources[0]
        self._sourceChild.SetValue(self._sources.index(source))
        value = self._attribute.eslValue()
        if source == Attribute.SourceValue:
            if not self._valueOnTop:
                displayStr = self.valueStrOrDefault()
                if self._datatype == "Boolean":
                    boolValue = True if displayStr.lower() == "true" else False
                    self._valueChild.SetValue(boolValue)
                elif self._datatype == "Enum":
                    enums = self._attribute.enums()
                    enumValues = Attribute.splitEnums(enums)
                    displayStr = self.valueStrOrDefault()
                    enumIx = 0
                    if displayStr in enumValues:
                        enumIx = enumValues.index(displayStr)
                    self._valueChild.SetValue(enumIx)
                elif self._datatype.upper() in EslBaseTypeNames:
                    self._valueChild.SetValue(value)
                else:
                    self._valueChild.SetValue(displayStr)
            else:
                #self.SetValue(value) - if do this invokes RefreshChildren and get infinite recursion
                pass
        else:
            enumValues = self._attribute.get_initial_enumValues(source, self._sources, self._sourceEnumValues)
            valueEnum = self._attribute.eslValue().valueStr()
            attrValueEnum = self.update_value_enum(valueEnum, enumValues)

        if self._annotationsChild:
            annotations = self.get_annotations()
            self._annotationsChild.SetValue(annotations)

    def ChildChanged(self, thisValue, childIndex, childValue):
        #print(">ChildChanged attRef="+self._attRef+" attr-ix"+str(self.GetIndexInParent()))
        # 0 Tag
        # 1 Data Type
        annotationsItem = 4 if self._valueOnTop else 6
        self._priorPropertyValue = self.propertyValue()
        self._childIndexChanged = childIndex
        if childIndex == 2:                                     # 2 ESL Name
            self._attribute.set_eslname(childValue)
        elif childIndex == 3:                                   # 3 Source
            self.sourceChanged(childValue)
        elif not self._valueOnTop and childIndex == 4:                                   # 4 Value(by data)
            valueStr = childValue
            if self._datatype == "Enum":
                choices = self._valueChild.GetChoices()
                nr = choices.GetCount()
                if childValue >=0 and childValue < nr:
                    valueStr = choices.GetLabel(childValue)
                elif nr > 0:
                    valueStr = choices.GetLabel(0)
                else:
                    valueStr = ""
                self._attribute.setESLValueForEnumValue(valueStr)
            else:
                if self._datatype == "Boolean":
                    valueStr = "true" if childValue else "false"
                self._attribute.eslValue().loadStr(valueStr, checkValidity=False)
        elif not self._valueOnTop and childIndex == 5:                                   # 5 ValueEnum (for variable)
            self.valueEnumChanged(childValue)
        elif childIndex == annotationsItem:                                   # Annotations
            self._attribute.set_show_description("true" if (childValue & 1) else "false")
            self._attribute.set_show_tag("true" if (childValue & 2) else "false")
            self._attribute.set_show_eslname("true" if (childValue & 4) else "false")
            self._attribute.set_show_source("true" if (childValue & 8) else "false")
            self._attribute.set_show_value("true" if (childValue & 16) else "false")
        return None

    def sourceChanged(self, childValue):
        useProperty = self
        self._useOtherProperty = None
        lastSource = self._lastSource
        source = self._sources[childValue]
        self._lastSource = source
        if self._valueOnTop:
            if ((lastSource == Attribute.SourceValue and source != Attribute.SourceValue) or
                (lastSource != Attribute.SourceValue and source == Attribute.SourceValue)): # will change property
                self._useOtherProperty = self.getOtherProperty()
                self._useOtherProperty._lastSource = source
                # copy over any features that may have changed (but not eslValue)
                self._useOtherProperty._attribute.set_eslname(self._attribute.eslname())
                self._useOtherProperty._attribute.set_show_tag(self._attribute.show_tag())
                self._useOtherProperty._attribute.set_show_eslname(self._attribute.show_eslname())
                self._useOtherProperty._attribute.set_show_description(self._attribute.show_description())
                self._useOtherProperty._attribute.set_show_source(self._attribute.show_source())
                self._useOtherProperty._attribute.set_show_value(self._attribute.show_value())
                # set other property to same expansion state as self
                self._useOtherProperty.SetExpanded(self.IsExpanded())
                annotationsItem = 4
                self._useOtherProperty.Item(annotationsItem).SetExpanded(self.Item(annotationsItem).IsExpanded())
                useProperty = self._useOtherProperty
        pass
        useProperty._attribute.set_source(source)
        useProperty._sources, useProperty._sourceEnumValues = self._attribute.get_valid_sources_and_sourceEnumValues()
        if source != Attribute.SourceValue:
            enumValues = useProperty._attribute.get_initial_enumValues(source, self._sources, self._sourceEnumValues)
            if useProperty._lastSourceEnumValue.get(source) is not None:
                valueEnum = useProperty._lastSourceEnumValue[source]
            else:
                valueEnum = enumValues[0]
            attrValueEnum = useProperty.update_value_enum(valueEnum, enumValues)

        else: #source == Attribute.SourceValue
            if useProperty._lastValueValueStr:
                valueValueStr = useProperty._lastValueValueStr
            else:
                valueValueStr = self._attribute.eslValue().defaultValueStr()
            useProperty._attribute.eslValue().loadStr(valueValueStr, checkValidity=False)
            useProperty.SetValue(useProperty._attribute.eslValue())
            useProperty._sourceChild.SetChoices(wxpg.PGChoices(self._sources, list(range(len(self._sources)))))
            useProperty._sourceChild.SetValue(self._sources.index(source))
            useProperty._sourceChild.Enable(len(self._sources) > 1)
            pass
        if not self._valueOnTop:
            self._valueChild.Hide(source != Attribute.SourceValue)
            self._valueEnumChild.Hide(source == Attribute.SourceValue)

    def valueEnumChanged(self, enumIndex):
        # enumValues are as set as labels for the current value-enum child or top property
        if not self._valueOnTop:
            enumValues = self._valueEnumChild.GetChoices().GetLabels()
        else:
            enumValues = self.GetChoices().GetLabels()
        enumValue = enumValues[enumIndex]
        attrValueStr = self._attribute.eslValue().valueStr()
        attrValueEnum, baseEnumValue, initReference = Attribute.check_enumValue_reference(enumValue)
        if attrValueEnum != attrValueStr:
            if initReference:
                newReference = self.promptForArrayMatrixReference(baseEnumValue, initReference)
                if not newReference:
                    attrValueEnum = self._attribute.eslValue().valueStr()   # current attribute value - is prior changing enum value
                elif newReference != initReference:
                    attrValueEnum = baseEnumValue + "(" + newReference + ")"
        attrValueEnum = self.update_value_enum(attrValueEnum, enumValues)

    def get_annotations(self):
        annotations = 0
        if self._attribute.show_description() == "true": annotations += 1
        if self._attribute.show_tag() == "true": annotations += 2
        if self._attribute.show_eslname() == "true": annotations += 4
        if self._attribute.show_source() == "true": annotations += 8
        if self._attribute.show_value() == "true": annotations += 16
        return annotations

    def checkGeneratedEslName(self):
        if not self._attribute.eslname():
            tag = self._attribute.tag()
            genEslName = self._entity.makeEslName(tag)
            self._eslnameChild.SetValue(genEslName)
            self._eslnameChild.GetCell(0).SetBgCol(PROPERTY_DEFAULT_COLOUR)
            self._eslnameChild.GetCell(1).SetBgCol(PROPERTY_DEFAULT_COLOUR)
            self._eslnameChild.SetLabel("ESL Name *")
        else:
            self._eslnameChild.GetCell(0).SetBgCol(PROPERTY_STANDARD_COLOUR)
            self._eslnameChild.GetCell(1).SetBgCol(PROPERTY_STANDARD_COLOUR)
            self._eslnameChild.SetLabel("ESL Name")

    def update_value_enum(self, enumValueOrAttrValueEnum:str, enumValues:list, inRefreshChildren:bool=False) -> str:
        # returns attrValueEnum
        priorEnumValue = self._attribute.eslValue().valueStr().replace(")", ")...")
        attrValueEnum, baseEnumValue, reference = Attribute.check_enumValue_reference(enumValueOrAttrValueEnum)
        enumValue = attrValueEnum
        if reference:
            enumValue += "..."
        if enumValue not in enumValues:
            if baseEnumValue:
                idx = Attribute.get_enumValue_index(baseEnumValue, enumValues)
                enumValue = baseEnumValue + "(" + reference + ")..."
                enumValues[idx] = enumValue
            else:
                if len(enumValues) > 0:
                    enumValue = enumValues[0]
                else:
                    enumValue = ""
        if enumValue:
            if enumValue != priorEnumValue:
                self._attribute.setESLValueForEnumValue(attrValueEnum)
            if not self._valueOnTop:
                labels = self._valueEnumChild.GetChoices().GetLabels()
                if enumValues != labels:
                    self._valueEnumChild.SetChoices(wxpg.PGChoices(enumValues, list(range(len(enumValues)))))
                priorChoice = self._valueEnumChild.GetChoiceSelection()
                priorSelection = ""
                if priorChoice >= 0 and priorChoice < len(enumValues):
                    priorSelection = enumValues[priorChoice]
                if enumValue != priorEnumValue or (priorSelection and enumValue != priorSelection):
                    self._valueEnumChild.SetValue(enumValues.index(enumValue))
            elif not inRefreshChildren:
                labels = self.GetChoices().GetLabels()
                if enumValues != labels:
                    self.SetChoices(wxpg.PGChoices(enumValues, list(range(len(enumValues)))))
                if enumValue != priorEnumValue:
                    self.SetValue(self._attribute.eslValue())
        return attrValueEnum

    def get_variable_for_source(self, source, varName):
        variable = None
        if source == 'Parameter':
            variable = self._module.blockNames().get(varName)
        else: # a module's used package variable
            for packName in self._module.diagramInfo().importedPackageNames():
                if source == packName:
                    package = self._module.application().getPackageByName(packName)
                    if package:
                        variable = package.blockNames().get(varName)
                    break
        return variable

    def promptForArrayMatrixReference(self, baseEnumValue, initReference):
        caption = "Attribute needs array/matrix element"
        if self._dimensionality.number() > 0:
            caption = "Attribute needs array/matrix slice"
        source = self._sources[self._sourceChild.GetValue()]
        variable = self.get_variable_for_source(source, baseEnumValue)
        varDimensions = ""
        rejectMsg = ""
        if variable:
            varDimensions = "("+variable.dimensions()+")"
        promptMsg = "Give element reference from " + baseEnumValue + varDimensions
        if self._dimensionality.number() > 0:
            promptMsg = "Give array/matrix reference from " + baseEnumValue + varDimensions
        while True:
            msg = promptMsg
            if rejectMsg:
                msg += "\n" + rejectMsg
            reference = wx.GetTextFromUser(msg, caption, initReference)
            reference = reference.strip()
            if not reference:
                break
            else:
                rejectMsg = self._attribute.check_valid_variable_reference(reference, variable)
                if not rejectMsg:
                    break
        return reference

    def firePropertyChangeEvent(self, newValue, oldValue):
        # Explicitly dispatch property change event as enum property doesn't recognise this as a change.
        category = 'entity-attribute'
        splitref = self._attRef.split(PropertyRefSeparator)
        propertyId = splitref[1]
        propertyTag = splitref[2]
        valid = self._view.propertiesView().dispatchPropertyChange(category, propertyId,
                                                                       propertyTag, str(newValue), str(oldValue))
        return valid

    def onRepickedAttributeValueEnum(self, enumValue, enumValueIdx):
        attrValueEnum, baseEnumValue, initReference = Attribute.check_enumValue_reference(enumValue)
        if initReference:
            newReference = self.promptForArrayMatrixReference(baseEnumValue, initReference)
            if newReference and newReference != initReference:
                oldValue = self.propertyValue()
                self._priorPropertyValue = oldValue
                newAttrValueEnum = baseEnumValue + "(" + newReference + ")"
                self._attribute.setESLValueForEnumValue(newAttrValueEnum)
                newValue = self.propertyValue()
                if str(newValue) != str(oldValue):
                    valid = self.firePropertyChangeEvent(newValue, oldValue)
                    if valid:
                        enumValues = self._attribute.get_initial_enumValues(self._attribute.source(), self._sources, self._sourceEnumValues)
                        attrValueEnum = self.update_value_enum(newAttrValueEnum, enumValues)
                pass

    def firePropertyChangeEventForEnumValueChange(self, newEnumValue, oldEnumValue):
        if newEnumValue.endswith("..."):
            newEnumValue = newEnumValue[:-3]
        if oldEnumValue.endswith("..."):
            oldEnumValue = oldEnumValue[:-3]
        oldValue = self.propertyValue()
        newValue = oldValue.replace('value="{valid|raw|' + oldEnumValue + '}"',
                                    'value="{valid|raw|' + newEnumValue + '}"')
        valid = self.firePropertyChangeEvent(newValue, oldValue)
        return valid

    def OnEvent(self, propgrid, wnd_primary, event):
        expandChildren = True
        if self._valueOnTop:
            expandChildren = Config.getBool('Views/Properties/Expand Property')
        if expandChildren:
            if not self.IsExpanded() and isinstance(event, wx.ChildFocusEvent):
                propgrid.EnsureVisible(self.Item(0))
        return True

    def OnPropGridChanging(self, propertygridevent):
        property = propertygridevent.GetProperty()
        if property == self:
            changingNativeValue = propertygridevent.GetPropertyValue() #not.GetValue()
            if changingNativeValue is not None:   # when child property is changed
                currentNativeValue = property.GetValue()
                if changingNativeValue != currentNativeValue:
                    self._priorPropertyValue = self.propertyValue()
                    self.setAttributeValue(changingNativeValue)
        propertygridevent.Skip() # on to next event handler

    def OnSetValue(self):
        pass

    def setAttributeValue(self, nativeValue): # override in the different forms of AttributeProperty
        pass

    def checkHiddenChildren(self):
        doHide = self._attribute.hide_datatype() == "true"
        self._datatypeChild.Hide(doHide)
        doHide = self._attribute.has_eslname() == "false"
        self._eslnameChild.Hide(doHide)
        doHide = self._attribute.has_sources() == "None"
        self._sourceChild.Hide(doHide)
        source = self._attribute.source()
        if not source:
            source = Attribute.SourceValue
        self._sources, self._sourceEnumValues = self._attribute.get_valid_sources_and_sourceEnumValues()
        if source not in self._sources:
            source = self._sources[0]
        if not self._valueOnTop:
            doHide = source != Attribute.SourceValue
            self._valueChild.Hide(doHide)
            doHide = source == Attribute.SourceValue
            self._valueEnumChild.Hide(doHide)
        doHide = self._attribute.has_annotations() == "false"
        self._annotationsChild.Hide(doHide)

class AttributePropertyFormDisplay(wxpg.StringProperty, AttributeProperty):
    def __init__(self, view, attRef, attribute):
        wxpg.StringProperty.__init__(self, attribute.description(), attRef)
        AttributeProperty.__init__(self, view, attRef, attribute, "Display")
        self._view.pgm().SetPropertyReadOnly(self, True, wxpg.PG_DONT_RECURSE)

    def SetValue(self, eslValue:ESLValue, pList=None, flags=wxpg.PG_SETVAL_REFRESH_EDITOR):
        valueStr = eslValue.valueStr()
        super(wxpg.StringProperty, self).SetValue(valueStr)

    def SetHelpString(self, helpString):
        super(wxpg.StringProperty, self).SetHelpString(helpString)

class AttributePropertyFormESLValue(ESLValueStrProperty, AttributeProperty):
    def __init__(self, view, attRef, attribute):
        ESLValueStrProperty.__init__(self, attribute.description(), attRef, attribute.eslValue())
        AttributeProperty.__init__(self, view, attRef, attribute, "ESLValue")
        propertyGrid = self._view.pgm().GetGrid()
        ESLValueStrPropertyButtonEditor.SetEditorToProperty(self, propertyGrid)

    def setAttributeValue(self, nativeValue):
        if isinstance(nativeValue, ESLValue):
            self._attribute.eslValue().copyFrom(nativeValue, self._attribute)
        else:
            self._attribute.eslValue().loadStr(str(nativeValue), checkValidity=False)
        pass

    def SetValue(self, eslValue:ESLValue, pList=None, flags=wxpg.PG_SETVAL_REFRESH_EDITOR):
        self._eslValue.copyFrom(eslValue, self._eslValue.parent())
        super(ESLValueStrProperty, self).SetValue(eslValue.saveStr())

    def SetHelpString(self, helpString):
        super(ESLValueStrProperty, self).SetHelpString(helpString)

class AttributePropertyFormValueEnum(AttributeValueEnumProperty, AttributeProperty):
    def __init__(self, view, attRef, attribute):
        AttributeValueEnumProperty.__init__(self, self, attribute.description(), attRef)
        AttributeProperty.__init__(self, view, attRef, attribute, "ValueEnum")

    def setAttributeValue(self, nativeValue):
        self.valueEnumChanged(nativeValue)

    def SetValue(self, eslValue:ESLValue, pList=None, flags=wxpg.PG_SETVAL_REFRESH_EDITOR):
        valueStr = eslValue.valueStr()
        enumValue = valueStr
        if enumValue.endswith(")"):
            enumValue += "..."
        choices = self.GetChoices()
        enumIx = choices.Index(enumValue)
        if valueStr and enumIx >= 0:
            super(AttributeValueEnumProperty, self).SetValue(enumIx, pList, flags)
        pass

    def SetHelpString(self, helpString):
        super(AttributeValueEnumProperty, self).SetHelpString(helpString)

    def ValueToString(self, value, argFlags=0):
        returnStr = ""
        if argFlags ^ 0:
            choices = self.GetChoices()
            returnStr = choices.GetLabel(value)
        else:
            returnStr = self._attribute.save(None, 0, True)
        return returnStr

class AttributePropertyFormEnum(wxpg.EnumProperty, AttributeProperty):
    def __init__(self, view, attRef, attribute):
        wxpg.EnumProperty.__init__(self, attribute.description(), attRef)
        AttributeProperty.__init__(self, view, attRef, attribute, "Enum")

    def setAttributeValue(self, nativeValue):
        choices = self.GetChoices()
        valueStr = choices.GetLabel(nativeValue)
        self._attribute.setESLValueForEnumValue(valueStr)

    def SetValue(self, eslValue:ESLValue, pList=None, flags=wxpg.PG_SETVAL_REFRESH_EDITOR):
        enums = self._attribute.enums()
        enumValues = Attribute.splitEnums(enums)
        displayStr = self.valueStrOrDefault()
        self.SetChoices(wxpg.PGChoices(enumValues, list(range(len(enumValues)))))
        enumIx = 0
        if displayStr in enumValues:
            enumIx = enumValues.index(displayStr)
        super(wxpg.EnumProperty, self).SetValue(enumIx)

    def SetHelpString(self, helpString):
        super(wxpg.EnumProperty, self).SetHelpString(helpString)

    def ValueToString(self, value, argFlags=0):
        returnStr = ""
        if argFlags ^ 0:
            choices = self.GetChoices()
            returnStr = choices.GetLabel(value)
        else:
            returnStr =self._attribute.save(None, 0, True)
        return returnStr

class AttributePropertyFormBoolean(wxpg.BoolProperty, AttributeProperty):
    def __init__(self, view, attRef, attribute):
        displayStr = attribute.valueStr()
        if not displayStr:
            displayStr = attribute.eslValue().defaultValueStr()
        boolValue = True if displayStr.lower() == "true" else False
        wxpg.BoolProperty.__init__(self, attribute.description(), attRef, boolValue)
        AttributeProperty.__init__(self, view, attRef, attribute, "Boolean")
        self.SetAttribute(wxpg.PG_BOOL_USE_CHECKBOX, True)

    def setAttributeValue(self, nativeValue):
        valueStr = "true" if nativeValue else "false"
        self._attribute.eslValue().loadStr(valueStr, checkValidity=False)

    def SetValue(self, eslValue:ESLValue, pList=None, flags=wxpg.PG_SETVAL_REFRESH_EDITOR):
        displayStr = self.valueStrOrDefault()
        boolValue = True if displayStr.lower() == "true" else False
        super(wxpg.BoolProperty, self).SetValue(boolValue)

    def SetHelpString(self, helpString):
        super(wxpg.BoolProperty, self).SetHelpString(helpString)

    def ValueToString(self, value, argFlags=0):
        returnStr = ""
        if argFlags ^ 0:
            returnStr = "true" if value else "false"
        else:
            returnStr =self._attribute.save(None, 0, True)
        return returnStr

class AttributePropertyFormString(wxpg.StringProperty, AttributeProperty):
    def __init__(self, view, attRef, attribute):
        wxpg.StringProperty.__init__(self, attribute.description(), attRef)
        AttributeProperty.__init__(self, view, attRef, attribute, "String")

    def setAttributeValue(self, nativeValue):
        self._attribute.eslValue().set_valueStr(str(nativeValue))

    def SetValue(self, eslValue:ESLValue, pList=None, flags=wxpg.PG_SETVAL_REFRESH_EDITOR):
        displayStr = self.valueStrOrDefault()
        super(wxpg.StringProperty, self).SetValue(displayStr)

    def SetHelpString(self, helpString):
        super(wxpg.StringProperty, self).SetHelpString(helpString)
