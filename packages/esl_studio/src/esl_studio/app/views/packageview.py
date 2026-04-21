#! /usr/bin/python

import sys
from collections import OrderedDict
from esl_diagram.canvas.diagram import sortedValues, sortedItems

import wx
import wx.propgrid as wxpg

from .. import utils as Utils
from ..config import Config
from .. import auihandler as aui
from .view import ModuleView
from .properties.variableproperty import VariableProperty, VariablePropertiesButtonEditor
from ..propertiescontrol import PropertyRefSeparator, PropertyChildSeparator
from ..propertieschangeevent import PropertiesChangeEvent
from ..moduleschangeevent import ModulesChangeEvent
from .propertiesview import ImageButtonSize, GridSpacing

class PackagePropertySet(object):
    def __init__(self, view, package):
        self._view = view
        self._package = package

        self.eslname = package.eslname()
        self.description = package.description()

        ref = 'P' + PropertyRefSeparator +str(package.moduleId()) + PropertyChildSeparator
        self._eslnameProp = wxpg.StringProperty("ESL Name", ref + 'eslname', value=self.eslname)
        self._eslnameProp.SetHelpString("An ESL identifier (A..Z 0..9 _) for the package\nThe ESL Name must be unique (in 28chars) in the application scope\n(i.e. as opposed to other packages, the model, submodels)")
        self._view.page().Append(self._eslnameProp)

        self._descriptionProp = wxpg.StringProperty("Description", ref + 'description', value=self.description)
        self._descriptionProp.SetHelpString("Description (not used in generated ESL)")
        self._view.page().Append(self._descriptionProp)

        self._variablesCategory = wxpg.PropertyCategory('Package Variables')
        self._view.page().Append(self._variablesCategory)

        for variable in sortedValues(package.variables()):
            self._view.addVariableProperty(variable, False)

class PackageView(ModuleView, wx.Panel):
    def __init__(self, parent, viewtype):

        self.testMode = 1       # 1=one page/tab, packages are a property set (all top level)

        style = ( wxpg.PG_BOLD_MODIFIED
                | wxpg.PG_SPLITTER_AUTO_CENTER
                #| wxpg.PG_DESCRIPTION
                #| wxpg.PG_COMPACTOR
                | wxpg.PGMAN_DEFAULT_STYLE
                | wxpg.PG_TOOLTIPS
        )
        helpbox = Config.getBool('Views/Package/Help')
        self._setHelpBoxSize = False
        if helpbox:
            style |= wxpg.PG_DESCRIPTION

        wx.Panel.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize)

        self._pgm = wxpg.PropertyGridManager(self, -1, wx.DefaultPosition, wx.DefaultSize, style=style)
        self._pgm.GetGrid().SetVerticalSpacing(GridSpacing)

        ModuleView.__init__(self, parent, viewtype)
        self.set_caption('Packages')

        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self._setupHeader(hsizer)
        vsizer.Add(hsizer, 0, wx.EXPAND)
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
        self.detectToCheckSelectedInMainView(self)

        self._page = self._pgm.AddPage("Package Page")
        self._pgm.SelectPage(0)

        self._package = None
        self._variableProperties = OrderedDict() #

    def page(self): return self._page
    def pgm(self): return self._pgm

    def variableProperties(self):
        return self._variableProperties

    def setMode(self, mode):
        ModuleView.setMode(self, mode)
        self._add.Enable(mode == "editing")
        self._del.Enable(mode == "editing")
        self._packagePropertySet._eslnameProp.Enable(mode == "editing")
        self._packagePropertySet._descriptionProp.Enable(mode == "editing")
        for varProp in self._variableProperties.values():
            varProp.Enable(mode == "editing")

    def _setupHeader(self, hsizer):
        self._label = wx.StaticText(self, -1, "Package: ")
        hsizer.Add(self._label, 1, wx.LEFT | wx.TOP | wx.ALIGN_CENTRE_VERTICAL, 5)

        helpbox = self._pgm.GetWindowStyleFlag() & wxpg.PG_DESCRIPTION
        checkbox = wx.CheckBox(self, -1, "Help")
        hsizer.Add(checkbox, 0, wx.RIGHT | wx.TOP | wx.ALIGN_CENTRE_VERTICAL, 5)
        checkbox.SetWindowStyle(wx.ALIGN_RIGHT)
        checkbox.SetValue(helpbox)
        self.Bind(wx.EVT_CHECKBOX, self.toggleDescription, checkbox)
        hsizer.AddSpacer(5)
        varstatic = wx.StaticText(self, -1, "Variable")
        hsizer.Add(varstatic, 0, wx.RIGHT | wx.TOP | wx.ALIGN_CENTRE_VERTICAL, 5)
        self._del = wx.Button(self, wx.ID_ANY, "", wx.DefaultPosition, wx.Size(ImageButtonSize, ImageButtonSize))
        self._del.SetBitmapLabel(Utils.getButtonBitmap(Utils.buttonIconFile("btnminus")))
        self.Bind(wx.EVT_BUTTON, self.onHeaderRemoveClick, self._del)
        hsizer.Add(self._del, 0, wx.RIGHT | wx.TOP, 5)
        self._del.Enable(False)
        self._add = wx.Button(self, wx.ID_ANY, "", wx.DefaultPosition, wx.Size(ImageButtonSize, ImageButtonSize))
        self._add.SetBitmapLabel(Utils.getButtonBitmap(Utils.buttonIconFile("btnplus")))
        hsizer.Add(self._add, 0, wx.RIGHT | wx.TOP, 5)
        self.Bind(wx.EVT_BUTTON, self.onHeaderAddClicked, self._add)

    def Reparent(self, newParent):
        result = True
        #result = super(wxpg.PropertyGridManager, self).Reparent(newParent)
        #result = self._pgm.Reparent(newParent) #OR
        #result = super(wx.Panel, self).Reparent(newParent)
        #v = super(View, self)
        #v.set_parent(newParent) # this doesnt seem to work - but the parent is the same anyway
        return result

    def defaultPaneInfo(self):
        info = aui.AuiPaneInfo()
        info.Name("PackagesView")
        info.Caption("Packages")
        info.MinimizeButton(True)
        info.MaximizeButton(True)
        info.CloseButton(True)
        info.PaneBorder(True)
        info.Right()
        return info

    def loadPackage(self, package):
        self._package = package
        self.set_moduleId(package.moduleId())
        self.setPackageHeaderName(package.eslname())
        self.addPackageProperties(package)
        self.resetPage()
        self._pgm.SetSplitterLeft(True, True)

    def updatePackage(self, category, propertyId, propertyTag, newValue):
        self._pgm.ClearSelection()
        self._pgm.ClearPage(0)
        self._variableProperties = OrderedDict()
        self.setPackageHeaderName(self._package.eslname())
        self.addPackageProperties(self._package)
        self.resetPage()
        self._pgm.SetSplitterLeft(True, True)

    def setPackageHeaderName(self, eslname):
        self._label.SetLabelText('Package: '+eslname)

    def resetPage(self):
        pass
        #self.SetColumnTitle(0,'Packages')
        #self.SetColumnTitle(1,'')
        #self.SetSplitterLeft()
        #self.CollapseAll()

    def addPackageProperties(self, package):
        self._packagePropertySet = PackagePropertySet(self, package)

    def addVariableProperty(self, variable, select=True):
        if variable.parent() != self._package:
            raise Exception('addVariableProperty: variable to add is not for this package')
        varRef = self.getVarPropertyRef(self._package.moduleId(), variable.variableId())
        property = VariableProperty(self, varRef, variable)
        priorProperty = None
        for item in sortedItems(self._variableProperties):
            if item[0] > varRef:
                priorProperty = item[1]
                break
        if priorProperty:
            prop = self._pgm.Insert(priorProperty, property)
        else:
            prop = self._pgm.Append(property)
        VariablePropertiesButtonEditor.SetEditorToProperty(property)
        property.checkValueShowFeatures()
        self._variableProperties[varRef] = property
        if select:
            res = self._pgm.SelectProperty(varRef)
            pass

    def removeVariableProperty(self, moduleId, variableId):
        varRef = self.getVarPropertyRef(moduleId, variableId)
        property = self._variableProperties.get(varRef)
        if property:
            if property.variable().parent() != self._package:
                raise Exception('removeVariableProperty: variable to remove is not for this package')
            self._pgm.ClearSelection()
            self._pgm.DeleteProperty(varRef)
            del self._variableProperties[varRef]

    def getIsLastVariable(self, property):
        isLast = False
        variablePropertiesList = list(sortedValues(self._variableProperties))
        nrVariables = len(variablePropertiesList)
        if nrVariables > 0 and variablePropertiesList[nrVariables - 1] == property:
            isLast = True
        return isLast

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
        Config.setBool('Views/Package/Help', helpbox)

    def registerEvents(self):
        self._pgm.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self._pgm.Bind(wxpg.EVT_PG_CHANGING, self.OnPropGridChanging)
        self._pgm.Bind(wxpg.EVT_PG_CHANGED, self.OnPropGridChange)
        self._pgm.Bind(wxpg.EVT_PG_SELECTED, self.OnPropGridSelectionChange)

    def OnLeaveWindow(self, mouse_event):
        #if self.IsSelection():
        #self.ClearSelection()
        #if self.IsCellEditControlShown():
        #    self.SaveEditControlValue() # this seems needed for choices
        #    ##self.HideCellEditControl() # this seems to save the current editing value
        pass

    def OnPropGridChanging(self, propertygridevent):
        property = propertygridevent.GetProperty()
        changedvalue = propertygridevent.GetPropertyValue()
        currentvalue = property.GetValueAsString()
        ref = property.GetName()
        variableProperty = self._variableProperties.get(ref)
        propertyId = ''
        proptag = ''
        oldvalue = ''
        newvalue = ''
        splitref = ref.split(PropertyRefSeparator)
        if ref[0:1] == 'P':
            category = 'package-property'
            if len(splitref) == 2:
                splitdot = splitref[1].split(PropertyChildSeparator)
                propertyId = int(splitdot[0]) # package moduleId
                proptag = splitdot[1] # eslname or description
                newvalue = changedvalue
                oldvalue = currentvalue
        else:
            category = 'package-variable'
            propertyId = int(splitref[1]) # package moduleId
            proptag = int(splitref[2]) # variableId
            newvalue = variableProperty.propertyValue()
            oldvalue = variableProperty.priorPropertyValue()

        if newvalue != oldvalue:
            valid = self.dispatchPropertyChange(category, propertyId, proptag, newvalue, oldvalue)
            if valid:
                # or should these be done in OnPropGridChange (i.e. after)
                if category == 'package-variable':
                    parent = property.GetMainParent()
                    if variableProperty.childIndexChanged() == 0:
                        eslname = variableProperty.variable().eslname()
                        #parent.SetLabel(eslname)
                        variableProperty.SetLabel(eslname)
                    #parent.SetLabel(property.GetValueAsString())
                elif category == 'package-property' and proptag == 'eslname':
                    self.setPackageHeaderName(newvalue)
            else:
                pgVFBlags = 0 #wxpg.PG_VFB_BEEP
                #pgVFBlags |= wxpg.PG_VFB_STAY_IN_PROPERTY
                #pgVFBlags |= wxpg.PG_VFB_MARK_CELL
                ## Used to have to use a bytes data-type for SetValidationFailureBehavior (wxPython error?)
                ##vfbFlags = bytes([pgVFBlags]) - fixed in 4.1.1
                propertygridevent.SetValidationFailureBehavior(pgVFBlags)
                propertygridevent.Veto()
                #reset ?
                if category == 'package-property':
                    property.SetValue(currentvalue)
                else:
                    if variableProperty:
                        variableProperty.updateFields(variableProperty.priorPropertyValue())
        pass

    def OnPropGridChange(self, propertygridevent):
        property = propertygridevent.GetProperty()
        if property:
            changedvalue = propertygridevent.GetPropertyValue()
            currentvalue = property.GetValueAsString()
            ref = property.GetName()
        pass

    def OnPropGridSelectionChange(self, propertygridevent):
        property = propertygridevent.GetProperty()
        changedvalue = propertygridevent.GetPropertyValue()
        if property:
            currentvalue = property.GetValueAsString()
            ref = property.GetName()
        delButtonActive = False
        if self._mode != "browsing":
            if property: #and not for package
                ref = property.GetName()
                if ref[0:1] != 'P':
                    delButtonActive = True
            self._del.Enable(delButtonActive)

    def onHeaderAddClicked(self, event):
        self.newVariable()

    def onHeaderRemoveClick(self, event):
        property = self._pgm.GetSelectedProperty()
        self.removeVariable(property)
        pass

    def dispatchPropertyChange(self, category, propertyId, propertyTag, newValue, oldValue):
        propertieschange_event = PropertiesChangeEvent(category, propertyId,
                                                        propertyTag, newValue, oldValue)
        self._parent.GetEventHandler().ProcessEvent(propertieschange_event) # cant be AddPendingEvent as need to get back valid
        valid = propertieschange_event.IsAllowed()
        return valid

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
                        variable = self._package.getVariableById(variableId)
                        if variable:
                            data = variable.save(None, 0, True)
                            self.dispatchModulesChange(
                                'remove-package-variable', self._moduleId, variableId, data)
        pass

    def newVariable(self):
        self.dispatchModulesChange('add-package-variable', self._moduleId)
        pass

    def getVarPropertyRef(self, moduleId, variableId):
        varRef = 'V' + PropertyRefSeparator
        varRef += str(moduleId)
        intVarId = int(variableId)
        varIdStr = format(intVarId, '03d')
        varRef += PropertyRefSeparator + varIdStr
        return varRef
