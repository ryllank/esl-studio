#! /usr/bin/python

import wx
import wx.propgrid as wxpg

from ..config import Config
from .. import auihandler as aui
from .view import ModuleView
from ..application.simulationparameters import ApplicationDefaultSimulationParameters, ApplicationAlgoOptionTexts
from ..application.eslvalue import ESLValue
from ..propertiescontrol import PropertyChildSeparator
from ..propertieschangeevent import PropertiesChangeEvent
from .properties.eslvaluestrproperty import ESLValueStrProperty, ESLValueStrPropertyButtonEditor

class SimulationParametersView(ModuleView, wx.Panel):

    def __init__(self, parent, viewtype):
        self._application = parent.frame().application()

        style = ( wxpg.PG_BOLD_MODIFIED
                | wxpg.PG_SPLITTER_AUTO_CENTER
                | wxpg.PGMAN_DEFAULT_STYLE
                | wxpg.PG_TOOLTIPS
        )
        helpbox = Config.getBool('Views/Simulation Parameters/Help')
        self._setHelpBoxSize = False
        if helpbox:
            style |= wxpg.PG_DESCRIPTION

        wx.Panel.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize)

        self._pgm = wxpg.PropertyGridManager(self, -1, wx.DefaultPosition, wx.DefaultSize, style=style)
        ModuleView.__init__(self, parent, viewtype)

        self.set_caption('Simulation Parameters')

        self._algoEnumStringList = []
        self._algoEnumValueList = []
        for algoStr in ApplicationAlgoOptionTexts:
            self._algoEnumStringList.append(algoStr)
            self._algoEnumValueList.append(int(ApplicationAlgoOptionTexts[algoStr]))

        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.setupHeader(hsizer)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.setupModuleChoice(hsizer)
        vsizer.Add(hsizer, 0, wx.EXPAND)
        self.setupSimulationParameterProperties()
        # Category used for experiment
        self._experimentCategory = wxpg.PropertyCategory('Warning: Program experiment is set')
        self._experimentCategory.SetHelpString("Simulation Parameters explicitly set here (generated in the ESL \"initial\" region) will override any explicitly set by the program experiment.")
        self._pgm.Append(self._experimentCategory)
        vsizer.Add(self._pgm, 1, wx.EXPAND ^ wx.ALL, 5)
        self.SetSizer(vsizer)
        self.Layout()

        self._moduleName = ""

        self._experimentSelected = False
        self.hideExperimentWarning(True)

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

        self._page = self._pgm.AddPage("Simulation Parameters")
        self._pgm.SelectPage(0)
        self.detectToCheckSelectedInMainView(self)

    def moduleName(self):
        return self._moduleName
    def set_moduleName(self, moduleName):
        self._moduleName = moduleName

    def setMode(self, mode):
        ModuleView.setMode(self, mode)
        properties = self._page.GetPyIterator(wx.propgrid.PG_ITERATE_ALL)
        for property in properties:
            property.Enable(mode == "editing")

    def defaultPaneInfo(self):
        info = aui.AuiPaneInfo()
        info.Name("SimulationParametersView")
        info.Caption("Simulation Parameters")
        info.MinimizeButton(True)
        info.MaximizeButton(True)
        info.CloseButton(True)
        info.PaneBorder(True)
        info.Right()
        return info

    def setupHeader(self, hsizer):
        self._label = wx.StaticText(self, -1, "Simulation Parameters")
        hsizer.Add(self._label, 1, wx.LEFT | wx.TOP, 5)

        helpbox = self._pgm.GetWindowStyleFlag() & wxpg.PG_DESCRIPTION
        checkbox = wx.CheckBox(self, -1, "Help")
        hsizer.Add(checkbox, 0, wx.RIGHT | wx.TOP, 5)
        checkbox.SetWindowStyle(wx.ALIGN_RIGHT)
        checkbox.SetValue(helpbox)
        self.Bind(wx.EVT_CHECKBOX, self.toggleDescription, checkbox)

    def setupModuleChoice(self, hsizer):
        self._moduleLabel = wx.StaticText(self, -1, "Module")
        hsizer.Add(self._moduleLabel, 1, wx.LEFT | wx.TOP, 5)

        self._moduleChoice = wx.Choice(self, -1)
        hsizer.Add(self._moduleChoice, 0, wx.RIGHT | wx.TOP, 5)
        self._moduleChoice.SetWindowStyle(wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHOICE, self.onModuleChoice, self._moduleChoice)

    def setupSimulationParameterProperties(self):
        for propertyName in ApplicationDefaultSimulationParameters:
            info = ApplicationDefaultSimulationParameters[propertyName]
            defaultStr = info[1]
            helpStr = info[2]
            if propertyName != 'ALGO':
                newEslValue = ESLValue(None, info[0], "", "", defaultStr)
                prop = ESLValueStrProperty(propertyName, propertyName, eslValue=newEslValue, helpString=helpStr)
                propertyGrid = self._pgm.GetGrid()
                ESLValueStrPropertyButtonEditor.SetEditorToProperty(prop, propertyGrid)
                prop.checkShowFeatures()
            else:
                prop = wxpg.EnumProperty(propertyName, propertyName,
                                         self._algoEnumStringList, self._algoEnumValueList)
                defaultValue = int(defaultStr)
                prop.SetValue(defaultValue)
                prop.SetHelpString(helpStr)
            self._pgm.Append(prop)

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
        Config.setBool('Views/Simulation Parameters/Help', style & wxpg.PG_DESCRIPTION)

    def updateView(self):
        #print("SimulationParametersView.updateView")
        moduleName = self.setModuleChoices()
        module = self.setModuleParameters(moduleName)
        #print("SimulationParametersView.updateView")

    def showModuleInApplicationView(self):
        if self._moduleName:
            module = self._application.getModuleByName(self._moduleName)
            if module:
                canvasType = module.moduleType()
                self._parent.frame().viewManager().applicationView().selectItem(canvasType, module.moduleId(), None, suppressPropagation=True)

    def showModuleProperties(self):
        if self._moduleName:
            module = self._application.getModuleByName(self._moduleName)
            if module:
                canvas = None
                moduleId = module.moduleId()
                if moduleId:
                    canvas = self._parent.frame().viewManager().mainView().getCanvasByModuleId(moduleId)
                if not canvas and module == self._application.program().model():
                    moduleId = self._application.program().moduleId()
                    canvas = self._parent.frame().viewManager().mainView().getCanvasByModuleId(moduleId)
                if canvas:
                    self._parent.frame().control().setCanvasProperties(canvas)

    def setModuleChoices(self):
        moduleName = ""
        options = []
        for mod in self._application.models().values():
            options.append("Model "+mod.eslname())
        for seg in self._application.segments().values():
            options.append("Segment "+seg.eslname())
        self._moduleChoice.SetItems(options)
        if len(options) > 0:
            indx = 0
            optionNames = list(map(lambda label: label.rsplit(" ")[1], options))
            if self._moduleName:
                for i in range(len(options)):
                    if self._moduleName.upper() == optionNames[i].upper():
                        indx = i
                        break
            self._moduleChoice.Select(indx)
            moduleName = optionNames[indx]
        return moduleName

    def setModuleParameters(self, moduleName=""):
        #print("SimulationParametersView.setModuleParameters moduleName="+moduleName)
        module = None
        if not moduleName:
            moduleName = self._moduleName
        if moduleName:
            module = self._application.getModuleByName(moduleName)
            if module and module.simulationParameters():
                parameters = module.simulationParameters().parameters()
                for parameter in parameters.values():
                    parameter.eslValue().checkValidity()
                    self.setValue(parameter.eslname(), parameter.eslValue())
                self._moduleName = moduleName
        return module

    def onModuleChoice(self, event):
        indx = self._moduleChoice.GetSelection()
        if indx != wx.NOT_FOUND:
            choice = self._moduleChoice.GetString(indx)
            moduleName = choice.rsplit(" ")[1]
            module = self.setModuleParameters(moduleName)
            if module:
                self.showModuleInApplicationView()
                self.showModuleProperties()

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
        newValue = propertygridevent.GetPropertyValue()
        oldValue = property.GetValue() # full saveStr of the property's ESLValue *before* the change
        if self._moduleName:
            propertyName = property.GetName()
            propertyId = self._moduleName + PropertyChildSeparator + propertyName
            # look for mode changed
            # raise the propertieschange_event
            if str(newValue) != str(oldValue):
                valid = self.dispatchPropertyChange('simulationparameter', propertyId,
                                                    propertyName, str(newValue), str(oldValue))
                if not valid:
                    pgVFBlags = 0  # wxpg.PG_VFB_BEEP
                    # pgVFBlags |= wxpg.PG_VFB_STAY_IN_PROPERTY
                    # pgVFBlags |= wxpg.PG_VFB_MARK_CELL
                    ## Used to have to use a bytes data-type for SetValidationFailureBehavior (wxPython error?)
                    ##vfbFlags = bytes([pgVFBlags]) - fixed in 4.1.1
                    propertygridevent.SetValidationFailureBehavior(pgVFBlags)
                    propertygridevent.Veto()
                    # reset ?
                    property.SetValue(oldValue)
                pass
            pass

    def OnPropGridChange(self, propertygridevent):
        pass

    def OnPropGridSelectionChange(self, propertygridevent):
        #print("SimulationParametersView.OnPropGridSelectionChange")
        property = propertygridevent.GetProperty()
        if property == self._experimentCategory:
            self._experimentSelected = True
        else:
            self._experimentSelected = False
        pass

    def dispatchPropertyChange(self, category, propertyId, propertyTag, newValue, oldValue):
        propertieschange_event = PropertiesChangeEvent(category, propertyId,
                                                        propertyTag, newValue, oldValue)
        #self._parent.GetEventHandler().AddPendingEvent(propertieschange_event) # see below about AddPendingEvent
        self._parent.GetEventHandler().ProcessEvent(propertieschange_event) # cant be AddPendingEvent as need to get back valid
        valid = propertieschange_event.IsAllowed()
        return valid

    def setValue(self, propertyName, value):
        info = ApplicationDefaultSimulationParameters[propertyName]
        property = self._pgm.GetProperty(propertyName)
        #print("SimulationParametersView.setValue propertyName="+propertyName+" value="+str(value))
        if propertyName != 'ALGO':
            property.SetValue(value)
        else:
            valueStr = value.valueStr()
            if not valueStr:
                valueStr = info[1]
            property.SetValue(int(valueStr))
        pass

    def updateSimulationParameters(self, propertyTag, value):
        #print("SimulationParametersView.updateSimulationParameters propertyTag="+propertyTag+" value="+str(value))
        moduleNameDotSimulationParameterName = propertyTag.split(PropertyChildSeparator)
        if len(moduleNameDotSimulationParameterName) == 2:
            if moduleNameDotSimulationParameterName[0] != self._moduleName:
                module = self._application.getModuleByName(moduleNameDotSimulationParameterName[0])
                if module and (module.moduleType() == 'model' or module.moduleType() == 'segment'):
                    self._moduleName = moduleNameDotSimulationParameterName[0]
                self.updateView()
            self.setValue(moduleNameDotSimulationParameterName[1], value)

    def hideExperimentWarning(self, hide):
        self._experimentCategory.Hide(hide)
        if hide:
            if self._experimentSelected: # Have to explicitly blank the description box
                self._pgm.SetDescription("", "")
