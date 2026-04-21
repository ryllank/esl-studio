#! /usr/bin/python

import sys
from collections import OrderedDict

import wx
import wx.propgrid as wxpg

from .. import utils as Utils
from ..config import Config
from .. import auihandler as aui
from .view import ModuleView
from ..application.applicationtypes import PROGRAMTYPES, MODELTYPES, SEGMENTTYPES
from ..application.argumententity import ArgumentEntity
from ..application.codeinsert import CodeInsert
from ..application.attribute import Attribute
from ..propertieschangeevent import PropertiesChangeEvent
from ..moduleschangeevent import ModulesChangeEvent
from ..propertiescontrol import PropertyRefSeparator, PropertyIdSeparator, PropertyChildSeparator, PropertiesKnownElements
from .propertiesviewpage import PropertiesViewPage
from .propertiesviewentity import PropertiesViewEntity
from .propertiesviewcanvas import PropertiesViewCanvas
from .propertiesviewcode import PropertiesViewCode
from .propertiesviewelement import PropertiesViewElement
from .propertiesviewdisplay import PropertiesViewDisplay
from .propertiesviewgroup import PropertiesViewGroup
from .propertiesviewargumententity import PropertiesViewArgumentEntity

ImageButtonSize = 16
GridSpacing = 2
if sys.platform == 'linux':
    ImageButtonSize = 32
    GridSpacing = 3

class PropertiesView(ModuleView, wx.Panel):
    def __init__(self, parent, viewtype):

        style = ( wxpg.PG_BOLD_MODIFIED
                | wxpg.PG_SPLITTER_AUTO_CENTER
                | wxpg.PGMAN_DEFAULT_STYLE
                | wxpg.PG_TOOLTIPS
        )
        helpbox = Config.getBool('Views/Properties/Help')
        self._setHelpBoxSize = False
        if helpbox:
            style |= wxpg.PG_DESCRIPTION

        wx.Panel.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize)

        self._pgm = wxpg.PropertyGridManager(self, -1, wx.DefaultPosition, wx.DefaultSize, style=style)
        self._pgm.GetGrid().SetVerticalSpacing(GridSpacing)

        ModuleView.__init__(self, parent, viewtype)

        self._frame = parent
        self._application = self._frame.application()

        self._pageType = ''
        self._category = ''
        self._propertyId = ''
        self._headerText = ''

        self.set_caption('Properties')

        vsizer = wx.BoxSizer(wx.VERTICAL)
        self._headerSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._setupHeader(self._headerSizer)
        vsizer.Add(self._headerSizer, 0, wx.EXPAND)
        vsizer.Add(self._pgm, 1, wx.EXPAND ^ wx.ALL, 5)
        self.SetSizer(vsizer)
        self.Layout()

        if helpbox:
            sz = self._parent.GetSize()
            self._pgm.SetDescBoxHeight(int(sz.height/5)+10, True)
            self._setHelpBoxSize = True

        extrastyle = 0 # Ensure initially clear
        # Show help as tooltips if no help box
        if not helpbox:
            extrastyle ^= wxpg.PG_EX_HELP_AS_TOOLTIPS
        self._pgm.SetExtraStyle(extrastyle)

        self.registerEvents()

        self._variableProperties = OrderedDict()
        self._moduleId = 0

        # Create the pages
        self._pageViews = []
        self._page = self._pgm.AddPage("Properties")
        self._pgm.SelectPage(0)                             # 0 Blank
        self._pageViews.append(None)
        self._page = self._pgm.AddPage("Properties")
        self._pgm.SelectPage(1)                             # 1 Canvas
        self._propertiesViewCanvas = PropertiesViewCanvas(self)
        self._pageViews.append(self._propertiesViewCanvas)
        self._page = self._pgm.AddPage("Properties")
        self._pgm.SelectPage(2)                             # 2 Code
        self._propertiesViewCode = PropertiesViewCode(self)
        self._pageViews.append(self._propertiesViewCode)
        self._page = self._pgm.AddPage("Properties")
        self._pgm.SelectPage(3)                             # 3 Element
        self._propertiesViewElement = PropertiesViewElement(self)
        self._pageViews.append(self._propertiesViewElement)
        self._page = self._pgm.AddPage("Properties")
        self._pgm.SelectPage(4)                             # 4 Entity
        self._propertiesViewEntity = PropertiesViewEntity(self)
        self._pageViews.append(self._propertiesViewEntity)
        self._page = self._pgm.AddPage("Properties")
        self._pgm.SelectPage(5)                             # 5 Display
        self._propertiesViewDisplay = PropertiesViewDisplay(self)
        self._pageViews.append(self._propertiesViewDisplay)
        self._page = self._pgm.AddPage("Properties")
        self._pgm.SelectPage(6)                             # 6 Group
        self._propertiesViewGroup = PropertiesViewGroup(self)
        self._pageViews.append(self._propertiesViewGroup)

    def setMode(self, mode):
        ModuleView.setMode(self, mode)
        self._add.Enable(mode == "editing")
        self._del.Enable(mode == "editing")
        for pageView in self._pageViews:
            if pageView:
                pageView.setMode(self._mode)

    def pageType(self): return self._pageType
    def category(self): return self._category
    def propertyId(self): return self._propertyId
    def moduleId(self): return self._moduleId

    def frame(self): return self._frame
    def application(self): return self._application
    def page(self): return self._page
    def pgm(self): return self._pgm
    def variableProperties(self): return self._variableProperties

    def defaultPaneInfo(self):
        info = aui.AuiPaneInfo()
        info.Name("PropertiesView")
        info.Caption("Properties")
        info.CaptionVisible(True)
        info.Dockable(True)
        info.Floatable(True)
        info.Right()
        info.Layer(1)
        info.FloatingPosition(wx.Point(100, 100))
        info.FloatingSize(wx.Size(200, 300))
        info.MinimizeButton(True)
        info.MaximizeButton(True)
        info.CloseButton(True)
        info.PaneBorder(True)
        info.Resizable(True)
        info.BestSize(wx.Size(200, -1))
        return info

    def _setupHeader(self, hsizer):
        self._label = wx.StaticText(self, -1, "Properties: ")
        hsizer.Add(self._label, 1, wx.LEFT | wx.TOP | wx.EXPAND, 5)

        headervsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer.Add(headervsizer, 0, wx.RIGHT)
        helpbox = self._pgm.GetWindowStyleFlag() & wxpg.PG_DESCRIPTION
        checkbox = wx.CheckBox(self, -1, "Help")
        checkbox.SetWindowStyle(wx.ALIGN_RIGHT)
        checkbox.SetValue(helpbox)
        self.Bind(wx.EVT_CHECKBOX, self.toggleDescription, checkbox)
        headervsizer.Add(checkbox, 0, wx.RIGHT | wx.TOP, 5)

        headerhsizer = wx.BoxSizer(wx.HORIZONTAL)
        headervsizer.Add(headerhsizer, 1, wx.EXPAND)
        self._parameterLabel = wx.StaticText(self, -1, "Parameter")
        headerhsizer.Add(self._parameterLabel, 0, wx.RIGHT | wx.TOP | wx.ALIGN_CENTRE_VERTICAL, 5)
        self._del = wx.Button(self, wx.ID_ANY, "", wx.DefaultPosition, wx.Size(ImageButtonSize, ImageButtonSize))
        self._del.SetBitmapLabel(Utils.getButtonBitmap(Utils.buttonIconFile("btnminus")))
        self.Bind(wx.EVT_BUTTON, self.onHeaderRemoveClick, self._del)
        headerhsizer.Add(self._del, 0, wx.RIGHT | wx.TOP, 5)
        self._del.Enable(False)
        self._add = wx.Button(self, wx.ID_ANY, "", wx.DefaultPosition, wx.Size(ImageButtonSize, ImageButtonSize))
        self._add.SetBitmapLabel(Utils.getButtonBitmap(Utils.buttonIconFile("btnplus")))
        headerhsizer.Add(self._add, 0, wx.RIGHT | wx.TOP, 5)
        self.Bind(wx.EVT_BUTTON, self.onHeaderAddClicked, self._add)

    def toggleDescription(self, event):
        style = self._pgm.GetWindowStyleFlag()
        style ^= wxpg.PG_DESCRIPTION
        self._pgm.SetWindowStyleFlag(style)
        helpbox = style & wxpg.PG_DESCRIPTION
        extrastyle = self._pgm.GetExtraStyle()
        extrastyle ^= wxpg.PG_EX_HELP_AS_TOOLTIPS
        self._pgm.SetExtraStyle(extrastyle)
        if helpbox:
            if not self._setHelpBoxSize:
                sz = self._parent.GetSize()
                self._pgm.SetDescBoxHeight(int(sz.height/5)+10, True)
                self._setHelpBoxSize = True
        Config.setBool('Views/Properties/Help', style & wxpg.PG_DESCRIPTION)

    def registerEvents(self):
        self._pgm.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self._pgm.Bind(wxpg.EVT_PG_CHANGING, self.OnPropGridChanging)
        self._pgm.Bind(wxpg.EVT_PG_CHANGED, self.OnPropGridChange)
        self._pgm.Bind(wxpg.EVT_PG_SELECTED, self.OnPropGridSelectionChange)
        self._pgm.Bind(wxpg.EVT_PG_DOUBLE_CLICK, self.OnPropGridDClicked)

    def OnLeaveWindow(self, mouse_event):
        #if self.IsSelection():
        #self.ClearSelection()
        #if self.IsCellEditControlShown():
        #    self.SaveEditControlValue() # this seems needed for choices
        #    ##self.HideCellEditControl() # this seems to save the current editing value
        pass

    def OnPropGridChanging(self, propertygridevent):
        property = propertygridevent.GetProperty()
        oldPropertyValue = property.GetValue()
        newPropertyValue = propertygridevent.GetPropertyValue()
        if isinstance(property, wxpg.ColourProperty) and newPropertyValue is None: # a bad colour
            pgVFBlags = 0 #wxpg.PG_VFB_BEEP
            propertygridevent.SetValidationFailureBehavior(pgVFBlags)
            property.SetValue(oldPropertyValue)
            property.SetWasModified(False)
            propertygridevent.Veto()
            return
        newPropertyValueStr = property.ValueToString(newPropertyValue, 0)
        oldPropertyValueStr = property.GetValueAsString()
        propertyId = ''
        propertyTag = ''
        ref = property.GetName()
        category = self._category   # unless is a parameter change
        variableProperty = None
        attributeProperty = None
        portProperty = None
        specialAttributeProperty = None
        # want the application format's for the values - these should be strings (will be stringised)
        newValue = newPropertyValue
        oldValue = oldPropertyValue
        splitref = ref.split(PropertyRefSeparator)
        if splitref[0] == 'M': #module-property
            category = 'module-property'
            if len(splitref) == 2:
                splitdot = splitref[1].split(PropertyChildSeparator)
                propertyId = splitdot[0] # moduleId
                propertyTag = splitdot[1] # eslname, description, moduleType, ESL or file or annotations
                if propertyTag == 'programType':
                    newValue = PROGRAMTYPES[int(newPropertyValue)]
                    oldValue = PROGRAMTYPES[int(oldPropertyValue)]
                elif propertyTag == 'modelType':
                    newValue = MODELTYPES[int(newPropertyValue)]
                    oldValue = MODELTYPES[int(oldPropertyValue)]
                elif propertyTag == 'segmentType':
                    newValue = SEGMENTTYPES[1 if newPropertyValue else 0]
                    oldValue = SEGMENTTYPES[1 if oldPropertyValue else 0]
                elif propertyTag == 'ESL':
                    newValue = Utils.unescapeText(newPropertyValue)
                    oldValue = Utils.unescapeText(oldPropertyValue)
                elif propertyTag == 'file':
                    newValue = newPropertyValueStr
                    oldValue = oldPropertyValueStr
                elif propertyTag == 'packages':
                    newValue = newPropertyValueStr
                    oldValue = oldPropertyValueStr
                elif propertyTag == 'experiment':
                    newValue = Utils.unescapeText(newPropertyValue)
                    oldValue = Utils.unescapeText(oldPropertyValue)
                    generate = self._frame.control().generate()
                    generate.refresh()
                    defaultExperimentText = generate.generateESLExperiment()
                    if newValue == defaultExperimentText:
                        newValue = ""
                    if oldValue == defaultExperimentText:
                        oldValue = ""
                    if oldValue == newValue: # For LongStringProperty pressed OK with no change - suppress this as a property change
                        propertyId = ""
                elif propertyTag == 'annotations':
                    newValue = newPropertyValueStr
                    oldValue = oldPropertyValueStr
                elif propertyTag == 'programAnnotations':
                    newValue = newPropertyValueStr
                    oldValue = oldPropertyValueStr
        elif splitref[0] == 'V':
            category = 'module-parameter'
            variableProperty = self._variableProperties.get(ref)
            propertyId = splitref[1] # moduleId
            propertyTag = splitref[2] # variableId
            newValue = variableProperty.propertyValue()
            oldValue = variableProperty.priorPropertyValue()

        elif splitref[0] == 'E': #entity
            category = 'entity-property'
            if len(splitref) == 3:
                splitdot = splitref[2].split(PropertyChildSeparator)
                propertyId = splitref[1] + PropertyIdSeparator + splitdot[0]
                propertyTag = splitdot[1] # description or annotations
                if (propertyTag == 'annotations' or
                    propertyTag == 'submodel' or propertyTag == 'segment' or propertyTag == 'function'): # for call-entity
                    newValue = newPropertyValueStr
                    oldValue = oldPropertyValueStr
                elif propertyTag == 'region': # for code-block
                    newValue = CodeInsert.Region_values[int(newPropertyValue)]
                    oldValue = CodeInsert.Region_values[int(oldPropertyValue)]
                elif propertyTag == 'insert': # for code-block
                    newValue = CodeInsert.Insert_values[int(newPropertyValue)]
                    oldValue = CodeInsert.Insert_values[int(oldPropertyValue)]
                elif propertyTag == 'esl': # for code-block
                    newValue = Utils.unescapeText(newPropertyValue)
                    oldValue = Utils.unescapeText(oldPropertyValue)
                    if oldValue == newValue: # For LongStringProperty pressed OK with no change - suppress this as a property change
                        propertyId = ""
                elif propertyTag == 'frequency' or propertyTag == 'frequency'+Attribute.ValueEnumRefExtn: # for segment-call
                    specialAttributeProperty = self._propertiesViewEntity._specialProperties.get(propertyTag)
                    newValue = specialAttributeProperty.propertyValue()
                    oldValue = specialAttributeProperty.priorPropertyValue()
                elif propertyTag == 'delay' or propertyTag == 'delay'+Attribute.ValueEnumRefExtn: # for segment-call
                    specialAttributeProperty = self._propertiesViewEntity._specialProperties.get(propertyTag)
                    newValue = specialAttributeProperty.propertyValue()
                    oldValue = specialAttributeProperty.priorPropertyValue()

        elif splitref[0] == 'S':
            category = 'special-property'
            propertyId = splitref[1] # canvasId|objectId
            propertyTag = splitref[2] # attribute tag
            #if propertyTag in PropertiesViewArgumentEntity.Prop_types:
            #    specialAttributeProperty = self._propertiesViewEntity._specialProperties.get(propertyTag)
            #    newValue = newPropertyValueStr
            #    oldValue = oldPropertyValueStr

        elif splitref[0] == 'A':
            category = 'entity-attribute'
            propertyId = splitref[1] # canvasId|objectId
            propertyTag = splitref[2] # attribute tag
            attributeProperty = self._variableProperties.get(ref)
            if attributeProperty is not None:
                newValue = attributeProperty.propertyValue()
                oldValue = attributeProperty.priorPropertyValue()

        elif splitref[0] == 'O':
            category = 'entity-port'
            portProperty = self._variableProperties.get(ref)
            propertyId = splitref[1] # canvasId|objectId
            propertyTag = splitref[2] # port id
            newValue = portProperty.propertyValue()
            oldValue = portProperty.priorPropertyValue()

        elif splitref[0] == 'X' or splitref[0] == 'Y': #element
            category = 'element-property'
            if splitref[0] == 'Y':
                category = 'annotation-text'
            splitdot = splitref[2].split(PropertyChildSeparator)
            propertyId = splitref[1] + PropertyIdSeparator + splitdot[0]
            propertyTag = splitdot[1]
            oldValue, newValue = self._propertiesViewElement.getElementPropertyChange(propertyTag, newValue)

        elif splitref[0] == 'D': #display
            category = 'display-property'
            if len(splitref) == 3:
                splitdot = splitref[2].split(PropertyChildSeparator)
                propertyId = splitref[1] + PropertyIdSeparator + splitdot[0]
                propertyTag = splitdot[1]
                if propertyTag == "xAxis" or propertyTag == "yAxis":
                    newValue = property.propertyValue()
                    oldValue = property.priorPropertyValue()

        elif splitref[0] == 'G': #group
            category = 'group-property'
            if len(splitref) == 3:
                splitdot = splitref[2].split(PropertyChildSeparator)
                propertyId = splitref[1] + PropertyIdSeparator + splitdot[0]
                propertyTag = splitdot[1]
                oldValue, newValue = self._propertiesViewGroup.getGroupPropertyChange(propertyTag, newValue)

        # raise the appropriate propertieschange_event
        if propertyId:
            if str(newValue) != str(oldValue):
                valid = self.dispatchPropertyChange(category, propertyId,
                                                    propertyTag, str(newValue), str(oldValue))
                if valid:
                    # or should these be done in OnPropGridChange (i.e. after)
                    if category == 'module-parameter':
                        parent = property.GetMainParent()
                        if variableProperty.childIndexChanged() == 0:
                            eslname = variableProperty.variable().eslname()
                            #parent.SetLabel(eslname)
                            variableProperty.SetLabel(eslname)
                        #parent.SetLabel(property.GetValueAsString())
                    elif category == 'module-property' and propertyTag == 'eslname':
                        module = self._application.getModuleById(int(propertyId))
                        if module:
                            headerText = module.identification()
                            self.setHeaderLabel(headerText)
                else:
                    pgVFBlags = 0 #wxpg.PG_VFB_BEEP
                    #pgVFBlags |= wxpg.PG_VFB_STAY_IN_PROPERTY
                    #pgVFBlags |= wxpg.PG_VFB_MARK_CELL
                    ## Used to have to use a bytes data-type for SetValidationFailureBehavior (wxPython error?)
                    ##vfbFlags = bytes([pgVFBlags]) - fixed in 4.1.1
                    propertygridevent.SetValidationFailureBehavior(pgVFBlags)
                    propertygridevent.Veto()
                    #reset ?
                    if category == 'module-property':
                        property.SetValue(oldPropertyValue) #was oldValueStr
                    elif category == 'module-parameter':
                        if variableProperty:
                            variableProperty.updateFields(variableProperty.priorPropertyValue())
                    elif category == 'entity-attribute':
                        if attributeProperty:
                            attributeProperty.updateFields(attributeProperty.priorPropertyValue())
                    elif category == 'entity-port':
                        if portProperty:
                            portProperty.updateFields(portProperty.priorPropertyValue())
                    elif category == 'display-property':
                        property.updateFields(property.priorPropertyValue())
                    elif category == 'entity-property':
                        if specialAttributeProperty is not None:
                            specialAttributeProperty.updateFields(specialAttributeProperty.priorPropertyValue())
                        else:
                            property.SetValue(oldPropertyValue)
                    elif category == 'special-property':
                        property.SetValue(oldPropertyValue)
            pass
        pass

    def OnPropGridChange(self, propertygridevent):
        pass

    def OnPropGridSelectionChange(self, propertygridevent):
        ref = propertygridevent.GetPropertyName()
        #print("OnPropGridSelectionChange category="+self._category+" selected=" + ref)
        if self._category == 'module-property':
            # For selecting a variable enable the Del button here in propertiesview.
            property = propertygridevent.GetProperty()
            delButtonActive = False
            if self._mode != "browsing":
                if property:
                    if ref[0:1] == 'V': #variable
                        delButtonActive = True
                self._del.Enable(delButtonActive)
        pass

    def OnPropGridDClicked(self, propertygridevent):
        value = propertygridevent.GetPropertyValue()
        property = propertygridevent.GetProperty()
        ref = property.GetName()
        if ref.endswith('help') and value:
            Utils.openUrl(value)
        elif ref.endswith('view') and value:
            self._frame.commands().openView(value)

    def onHeaderAddClicked(self, event):
        self.newVariable()
        pass

    def onHeaderRemoveClick(self, event):
        property = self._pgm.GetSelectedProperty()
        self.removeVariable(property)
        pass

    def dispatchPropertyChange(self, category, propertyId, propertyTag, newValue, oldValue):
        propertieschange_event = PropertiesChangeEvent(category, propertyId,
                                                        propertyTag, newValue, oldValue)
        self._parent.GetEventHandler().ProcessEvent(propertieschange_event)
        valid = propertieschange_event.IsAllowed()
        return valid

    def setHeaderLabel(self, headerText):
        self._headerText = headerText
        self._label.SetLabelText(headerText)
        #self.set_caption(text) #or do separately?

    def showParameterButtons(self, show):
        self._parameterLabel.Show(show)
        self._add.Show(show)
        self._del.Show(show)
        self.Layout()

    def clearPropertyPage(self, headerText, pageType='', category='', moduleId=0, propertyId=""):
        self._pageType = pageType
        self._category = category
        self._moduleId = moduleId
        self._propertyId = propertyId
        self._pgm.ClearSelection()
        self._del.Enable(False)
        if not pageType:
            self.setPage(0)
        self._pgm.SetDescription('', '')
        if headerText is not None:
            self.setHeaderLabel(headerText)
        self.showParameterButtons(False)
        paneinfo = self._parent.auiManager().GetPane(self)
        paneinfo.Caption("Properties")
        self._parent.auiManager().Update()
        pass

    def setPage(self, index):
        self._pgm.SelectPage(index)
        self._page = self._pgm.GetPage(index)

    def setBlankPropertyPage(self, pageType, propertyId, headerText):
        self.setPage(0)

    def setCanvasPropertyPage(self, pageType, propertyId, headerText):
        self.setPage(1)
        self._propertiesViewCanvas.setCanvasPropertyPage(pageType, propertyId, headerText)

    def setCodePropertyPage(self, pageType, propertyId, headerText):
        self.setPage(2)
        self._propertiesViewCode.setCodePropertyPage(pageType, propertyId, headerText)

    def setElementPropertyPage(self, pageType, propertyId, headerText, elementXmlElement):
        self.setPage(3)
        self._propertiesViewElement.setElementPropertyPage(pageType, propertyId, headerText, elementXmlElement)

    def setEntityPropertyPage(self, pageType, propertyId, headerText):
        self.setPage(4)
        self._propertiesViewEntity.setEntityPropertyPage(pageType, propertyId, headerText)

    def setDisplayPropertyPage(self, pageType, propertyId, headerText):
        self.setPage(5)
        self._propertiesViewDisplay.setDisplayPropertyPage(pageType, propertyId, headerText)

    def setGroupPropertyPage(self, pageType, propertyId, headerText, groupXmlElement):
        self.setPage(6)
        self._propertiesViewGroup.setGroupPropertyPage(pageType, propertyId, headerText, groupXmlElement)

    def resetPropertiesForNewApplication(self):
        # Reset property views that may have cached state info that may be reused to ensure not if load a new application
        self._propertiesViewCanvas.resetPropertiesForNewApplication()
        self._propertiesViewCode.resetPropertiesForNewApplication()
        self._propertiesViewElement.resetPropertiesForNewApplication()
        self._propertiesViewEntity.resetPropertiesForNewApplication()
        self._propertiesViewDisplay.resetPropertiesForNewApplication()
        self._propertiesViewGroup.resetPropertiesForNewApplication()

    def updateProperties(self, category, propertyId, propertyTag, newValue):
        samePageShowing = category == self._category and str(propertyId) == str(self._propertyId) # shows what did last time
        if not samePageShowing: # check page for other compatiblities
            if category == 'module-parameter' and self._category == 'module-property':
                if (str(propertyId) == str(self._propertyId) or
                    (str(self._propertyId) == str(self._application.program().moduleId()) and
                     self._application.program().model() is not None and
                     str(propertyId) == str(self._application.program().model().moduleId()))):
                    samePageShowing = True
        if samePageShowing: # We're on the same page
            pageType = self._pageType
            moduleId = self._moduleId
            self._variableProperties = OrderedDict()
            if pageType == 'program' or pageType == 'model' or pageType == 'submodel':
                self.setPage(1)
                self._propertiesViewCanvas.updateProperties(pageType, category, moduleId, propertyId, propertyTag, newValue)
            elif pageType == 'ESL' or pageType == 'file':
                self.setPage(2)
                self._propertiesViewCode.updateProperties(pageType, category, moduleId, propertyId, propertyTag, newValue)
            elif pageType in PropertiesKnownElements:  # a graphical element
                self.setPage(3)
                self._propertiesViewElement.updateProperties(pageType, category, moduleId, propertyId, propertyTag, newValue)
            elif pageType == 'entity':
                self.setPage(4)
                self._propertiesViewEntity.updateProperties(pageType, category, moduleId, propertyId, propertyTag, newValue)
            elif pageType == 'display':
                self.setPage(5)
                self._propertiesViewDisplay.updateProperties(pageType, category, moduleId, propertyId, propertyTag, newValue)
            elif pageType == 'group':
                self.setPage(5)
                self._propertiesViewGroup.updateProperties(pageType, category, moduleId, propertyId, propertyTag, newValue)
            else:
                self.setPage(0)

    def dispatchModulesChange(self, category, moduleId, variableId=0, data=''):
        moduleschange_event = ModulesChangeEvent(category, moduleId, '', variableId, data)
        #self._parent.GetEventHandler().ProcessEvent(moduleschange_event)
        # don't use ProcessEvent as may be called from VariablePropertiesButtonEditor so must be deferred
        # also does seem to like QueueEvent.
        self._parent.GetEventHandler().AddPendingEvent(moduleschange_event)

    def removeVariable(self, property):
        if property:
            ref = property.GetName()
            if ref[0:1] != 'P':
                splitref = ref.split(PropertyRefSeparator)
                if len(splitref) == 3:
                    splitdot = splitref[2].split(PropertyChildSeparator)
                    variableId = int(splitdot[0])
                    if variableId:
                        module = self._application.getModuleById(self._moduleId)
                        if module == self._application.program():
                            module = self._application.program().model()
                        if module:
                            variable = module.getVariableById(variableId)
                            if variable:
                                data = variable.save(None, 0, True)
                                self.dispatchModulesChange(
                                    'remove-parameter', self._moduleId, variableId, data)
        pass

    def newVariable(self):
        self.dispatchModulesChange('add-parameter', self._moduleId)
        pass

    def addVariableProperty(self, variable, select=True):
        self._propertiesViewCanvas.addVariableProperty(variable, select)

    def removeVariableProperty(self, moduleId, variableId):
        self._propertiesViewCanvas.removeVariableProperty(moduleId, variableId)

    def setCodeProperty(self, moduleId, propertyName, value, change=False):
        if moduleId == self._moduleId:
            if self._propertiesViewCode:
                self._propertiesViewCode.setProperty(propertyName, value, change)

    def getVarPropertyRef(self, moduleId, variableId):
        propertyRef = None
        pageIndex = self._pgm.GetSelectedPage()
        if pageIndex == 1:
            propertyRef = self._propertiesViewCanvas.getVarPropertyRef(moduleId, variableId)
        return propertyRef

    def getAttPropertyRef(self, category, canvasNObjectId, attributeTag):
        propertyRef = None
        pageIndex = self._pgm.GetSelectedPage()
        if pageIndex == 4:
            propertyRef = self._propertiesViewEntity.getAttPropertyRef(category, canvasNObjectId, attributeTag)
        return propertyRef

    def clearView(self): # Reset variable properties and remove any existing properties in the grid (for new application).
        for viewPage in self._pageViews:
            if viewPage:
                viewPage.clearViewPage()
        self._pageType = ''
        self._category = ''
        self._propertyId = ''
        self._headerText = ''
        self._moduleId = 0
        self._variableProperties = OrderedDict()
