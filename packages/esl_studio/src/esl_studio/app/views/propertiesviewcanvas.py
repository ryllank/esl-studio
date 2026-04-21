#! /usr/bin/python

import sys
from collections import OrderedDict

import wx
import wx.propgrid as wxpg

from esl_diagram.canvas.diagram import sortedValues, sortedItems

from .. import utils as Utils
from ..application.applicationtypes import PROGRAMTYPES, MODELTYPES, SEGMENTTYPES
from ..propertiescontrol import PropertyRefSeparator, PropertyChildSeparator
from .propertiesviewpage import PropertiesViewPage
from .properties.variableproperty import VariableProperty, VariablePropertiesButtonEditor
from .properties.experimentproperty import ExperimentProperty, ExperimentPropertyButtonEditor
from .properties.multichoiceproperty import MultiChoiceProperty, MultiChoicePropertyButtonEditor
from .properties.coreproperties import CompoundProperty, FlagsProperty

class PropertiesViewCanvas(PropertiesViewPage):
    def __init__(self, propertiesView):
        PropertiesViewPage.__init__(self, propertiesView)
        self._application = self._propertiesView.application()
        self._page = self._propertiesView.page()
        self._pgm = self._propertiesView.pgm()
        self._pagePropertyId = ""
        # properties
        self._programCategory = None
        self._programType = None
        self._programName = None
        self._programDescription = None
        self._experiment = None
        self._programAnnotations = None
        self._moduleCategory = None
        self._eslname = None
        self._description = None
        self._annotations = None
        self._modelType = None      # Just for show when Model is that of Program
        self._segmentType = None
        #### TODO consider how to do/access model & segment simulation-parameters from here
            #### eg a button that when main view shows this module's diagram says/does "Show Simulation Parameters"
            #### and when main view shows the simulation parameters says/does "Show module diagram"
            #### Simulation Parameters "properties" should be those for the module whose simpars are being shown
        self._packages = None
        self._parametersCategory = None
        self._variablePropertiesOD = OrderedDict()

    def page(self): return self._page
    def pgm(self): return self._pgm

    def setMode(self, mode):
        properties = [
            #self._programCategory,
            self._programType,
            self._programName,
            self._programDescription,
            self._experiment,
            self._programAnnotations,
            #self._moduleCategory,
            self._eslname,
            self._description,
            self._annotations,
            self._modelType,
            self._segmentType,
            self._packages,
            #self._parametersCategory
        ]
        properties.extend(self._variablePropertiesOD.values())
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
        if not self._programCategory:
            self._programCategory = wxpg.PropertyCategory("")
            self._page.Append(self._programCategory)

            self._programType = wxpg.EnumProperty("Program Type", ref + "programType", PROGRAMTYPES, [0,1,2], 0)
            self._programType.SetHelpString("Program Type - \"study\" for a normal MODEL (recommended - for use here)" +
                               "\n - \"embedded-program\" to generate an EMBEDDED SEGMENT (that may be compiled and embedded in an exectuable program)" +
                               "\n - \"remote-program\" to generate a REMOTE SEGMENT (that may run with a MODEL or program in another process or computer)")
            self._page.Append(self._programType)

            self._programName = wxpg.StringProperty("Program Name", ref + 'programName')
            self._page.Append(self._programName)
            self._programName.SetHelpString("A name you can give for the Program."
                               "\nThis can be any text, but should be short."
                               "\nNote: This is not used in generated ESL")

            self._programDescription = wxpg.StringProperty("Program Description", ref + 'programDescription')
            self._programDescription.SetHelpString("Description of the Program"
                               "\nNote: This is not used in generated ESL")
            self._page.Append(self._programDescription)

            self._experiment = ExperimentProperty(self, "Experiment", ref + "experiment")
            help = "Experiment ESL text (source code).\nThis only applies for a STUDY Program (ignored for remote or embedded program).\n"
            help += "Note that when this is set it will override any values set in simulation parameters.\n"
            help += "Use the first button to see and edit the experiment in a multi-line dialog.\n"
            help += "Use the second button to pre-load the dialog with the default experiment (including simulation parameters and any IO) that would be generated.\n"
            help += "Clear this experiment property value to reset to the default."
            self._experiment.SetHelpString(help)
            self._page.Append(self._experiment)
            ExperimentPropertyButtonEditor.SetEditorToProperty(self._experiment)

            showAnnotations = ["Program Type", "Program Name", "Program Description"]
            annotationHints = ["Show the Program's type annotation on the diagram",
                               "Show the Program's name annotation on the diagram",
                               "Show the module's description annotation on the diagram"]
            choiceBits = [1, 2, 4]
            self._programAnnotations = FlagsProperty("Annotations", ref + 'programAnnotations', showAnnotations, choiceBits, 0)
            self._programAnnotations.SetHelpString("Show annotations for the Program on the diagram")
            self._page.SetPropertyReadOnly(self._programAnnotations, True, wxpg.PG_DONT_RECURSE)
            self._page.Append(self._programAnnotations)
            self._programAnnotations.setHelpStrings(annotationHints)

            self._moduleCategory = wxpg.PropertyCategory("")
            self._page.Append(self._moduleCategory)

            self._eslname = wxpg.StringProperty("ESL Name", ref + 'eslname')
            self._page.Append(self._eslname)
            self._eslname.SetHelpString("An ESL identifier (A..Z 0..9 _) of this module."
                               "\nThe ESL Name must be unique (in 28chars) in the application scope" +
                               "\n(i.e. as opposed to the model, submodels & packages)")

            self._description = wxpg.StringProperty("Description", ref + 'description')
            self._description.SetHelpString("Description of this module"
                               "\nNote: This is not used in generated ESL")
            self._page.Append(self._description)

            showAnnotations = ["ESL Name", "Description"]
            annotationHints = ["Show the module's ESL name annotation on the diagram",
                               "Show the module's description annotation on the diagram"]
            choiceBits = [1, 2]
            self._annotations = FlagsProperty("Annotations", ref + 'annotations', showAnnotations, choiceBits, 0)
            self._annotations.SetHelpString("Show annotations for the module on the diagram")
            self._page.SetPropertyReadOnly(self._annotations, True, wxpg.PG_DONT_RECURSE)
            self._page.Append(self._annotations)
            self._annotations.setHelpStrings(annotationHints)

            self._modelType = wxpg.EnumProperty("Model Type", ref + "modelType", MODELTYPES, [0,1,2], 0)
            self._modelType.SetHelpString("Model Type - \"model\" for a normal MODEL (for use in a Study Program)" +
                               "\n - \"embedded\" to generate an EMBEDDED SEGMENT (that may be compiled and used in an Embedded Program)" +
                               "\n - \"remote\" to generate a REMOTE SEGMENT (that may run with a MODEL or program for a Remote Program in another process or computer)")
            self._page.Append(self._modelType)

            self._segmentType = wxpg.BoolProperty("External Segment", ref + "segmentType")
            self._segmentType.SetAttribute(wxpg.PG_BOOL_USE_CHECKBOX, True)
            self._segmentType.SetHelpString("Whether the segment is to be declared External (to be evaluated in an Remote Program/External Segment), or to be emulated here.")
            self._page.Append(self._segmentType)

    def setCanvasPropertyPage(self, pageType, propertyId, headerText):
        headerText = headerText[0].upper() + headerText[1:]
        self._propertiesView.clearPropertyPage(headerText, pageType, 'module-property', int(propertyId), propertyId) # for canvas moduleId is int(propertyId)

        program = None

        newItem = propertyId != self._pagePropertyId
        self._pagePropertyId = propertyId

        moduleId = self._propertiesView.moduleId()
        self._propertiesView.showParameterButtons(True)
        module = self._application.getModuleById(moduleId)
        moduleType = module.moduleType()

        if moduleType == "program":
            program = module
            module = program.model() # this could be None
            if module:
                moduleType = module.moduleType()
        elif moduleType == "model":
            if self._application.program().model():
                if self._application.program().model().moduleId() == moduleId:
                    program = self._application.program()
        moduleVariables = []
        if module:
            moduleVariables = list(sortedValues(module.variables()))
        if not newItem:
            if  len(moduleVariables) != len(self._variablePropertiesOD):
                newItem = True

        ref = 'M' + PropertyRefSeparator +str(moduleId) + PropertyChildSeparator
        self.setFixedProperties(ref)

        programCategoryTitle = "Program "
        if program:
            programCategoryTitle += "("+program.programType()+")"
            if program.name():
                programCategoryTitle += " " + program.name()
            self._programCategory.SetLabel(programCategoryTitle)
        self._programCategory.Hide(program is None)

        if program:

            self._programType.SetName(ref + 'programType')
            self._programType.SetValue(PROGRAMTYPES.index(program.programType()))

            self._programName.SetName(ref + 'programName')
            self._programName.SetValue(program.name())

            self._programDescription.SetName(ref + 'programDescription')
            self._programDescription.SetValue(program.description())

            self._experiment.SetName(ref + "experiment")
            self._experiment.SetValue(Utils.escapeText(program.experiment()))

            self._experiment.Hide(program.programType() != "study")

            annotations = 0
            if program.show_type() == "true": annotations += 1
            if program.show_name() == "true": annotations += 2
            if program.show_description() == "true": annotations += 4
            self._programAnnotations.setNameAndValue(ref + 'programAnnotations', annotations)
            if newItem:
                self._page.Collapse(self._programAnnotations)

        moduleCategoryTitle = "Module "
        if module:
            if moduleType == "model":
                moduleCategoryTitle = "Model ("+module.modelType()+")"
            elif moduleType == "submodel":
                moduleCategoryTitle = "Submodel"
            elif moduleType == "segment":
                moduleCategoryTitle = "Segment ("+module.segmentType()+")"
            moduleCategoryTitle += " " + module.eslname()
            self._moduleCategory.SetLabel(moduleCategoryTitle)

        self._moduleCategory.Hide(module is None)

        if module:
            self._eslname.SetName(ref + 'eslname')
            self._eslname.SetValue(module.eslname())

            self._description.SetName(ref + 'description')
            self._description.SetValue(module.description())

            annotations = 0
            if module.show_eslname() == "true": annotations += 1
            if module.show_description() == "true": annotations += 2
            self._annotations.setNameAndValue(ref + 'annotations', annotations)
            if newItem:
                self._page.Collapse(self._annotations)

            if moduleType == "model":
                self._modelType.SetName(ref + 'modelType')
                self._modelType.SetValue(MODELTYPES.index(module.modelType()))

                # Don't enable if this is the Program's Model (type will be determined by the Program Type)
                self._modelType.Enable(not program or module != program.model())

            self._modelType.Hide(moduleType != "model")

            if moduleType == "segment":
                self._segmentType.SetName(ref + 'segmentType')
                self._segmentType.SetValue(module.segmentType() == SEGMENTTYPES[1])
            self._segmentType.Hide(moduleType != "segment")

            allPackageNames = []
            for pack in list(self._application.packages().values()):
                allPackageNames.append(pack.eslname())
            for code in list(self._application.codes().values()):
                for sub in list(code.codeSubprograms().values()):
                    if sub.subprogramType() == "package":
                        allPackageNames.append(sub.eslname())
            usedNames = module.diagramInfo().importedPackageNames()
            #prop.SetValue(usedNames)
            if not self._packages:
                self._packages = MultiChoiceProperty("Use Packages", ref + 'packages', choices=allPackageNames, value=usedNames)
                self._packages.SetHelpString("Names of packages whose variables are imported and are available for use in this module" +
                                   "\nVariables in packages must not have the same name as a variable in (or imported into) this module")
                self._page.SetPropertyReadOnly(self._packages, True, wxpg.PG_DONT_RECURSE)
                self._page.Append(self._packages)
                MultiChoicePropertyButtonEditor.SetEditorToProperty(self._packages)
            else:
                self._packages.setNameChoicesAndValue(ref + 'packages', allPackageNames, usedNames)

            parametersCategoryTitle = "Model Parameters"
            if moduleType != 'model':
                parametersCategoryTitle = "Submodel Parameters"
            if not self._parametersCategory:
                self._parametersCategory = wxpg.PropertyCategory(parametersCategoryTitle)
                self._page.Append(self._parametersCategory)
            else:
                self._parametersCategory.SetLabel(parametersCategoryTitle)
            self._parametersCategory.Hide(len(moduleVariables) == 0)

            # Do fresh variables each time for a new item (and see also remove/append too)
            if newItem:
                for prop in sortedValues(self._variablePropertiesOD):
                    self._page.DeleteProperty(prop)
                self._variablePropertiesOD = OrderedDict()
            for i in range(len(moduleVariables)):
                variable = moduleVariables[i]
                varRef = self.getVarPropertyRef(self._propertiesView.moduleId(), variable.variableId())
                if newItem:
                    self.appendVariableProperty(varRef, variable)
                else:
                    property = list(sortedValues(self._variablePropertiesOD))[i]
                    property.setVariableProperty(varRef, variable)
                    self._propertiesView.variableProperties()[varRef] = property
        self.checkMode()

    def updateProperties(self, pageType, category, moduleId, propertyId, propertyTag, newValue):
        module = self._application.getModuleById(moduleId)
        headerText = module.identification()
        self.setCanvasPropertyPage(pageType, propertyId, headerText)

    def appendVariableProperty(self, varRef, variable):
        property = VariableProperty(self, varRef, variable)
        prop = self._page.Append(property)
        VariablePropertiesButtonEditor.SetEditorToProperty(property)
        property.checkValueShowFeatures()
        self._propertiesView.variableProperties()[varRef] = property
        self._variablePropertiesOD[varRef] = property
        return property

    def addInVariableProperty(self, varRef, variable):
        property = VariableProperty(self, varRef, variable)
        priorProperty = None
        for item in sortedItems(self._variablePropertiesOD):
            if item[0] > varRef:
                priorProperty = item[1]
                break
        if priorProperty:
            prop = self._page.Insert(priorProperty, property)
        else:
            prop = self._page.Append(property)
        VariablePropertiesButtonEditor.SetEditorToProperty(property)
        property.checkValueShowFeatures()
        self._propertiesView.variableProperties()[varRef] = property
        self._variablePropertiesOD[varRef] = property
        if self._parametersCategory:
            self._parametersCategory.Hide(False)
        return property

    def addVariableProperty(self, variable, select=True): # adds a new one to the shown list
        variablesModuleId = variable.parent().moduleId()
        varRef = self.getVarPropertyRef(variablesModuleId, variable.variableId())
        self.addInVariableProperty(varRef, variable)
        if select:
            res = self._pgm.SelectProperty(varRef)
            pass

    def removeVariableProperty(self, moduleId, variableId):
        varRef = self.getVarPropertyRef(moduleId, variableId)
        property = self._propertiesView.variableProperties().get(varRef)
        if property:
            property.Hide(True)
            self._page.DeleteProperty(property)
            del self._variablePropertiesOD[varRef]
            del self._propertiesView.variableProperties()[varRef]
            if self._parametersCategory:
                self._parametersCategory.Hide(len(self._variablePropertiesOD) == 0)

    def getIsLastVariable(self, property):
        isLast = False
        variablePropertiesList = list(sortedValues(self._variablePropertiesOD))
        nrVariables = len(variablePropertiesList)
        if nrVariables > 0 and variablePropertiesList[nrVariables - 1] == property:
            isLast = True
        return isLast

    def getVarPropertyRef(self, moduleId, variableId):
        varRef = 'V' + PropertyRefSeparator
        varRef += str(moduleId)
        intVarId = int(variableId)
        varIdStr = format(intVarId, '03d')
        varRef += PropertyRefSeparator + varIdStr
        return varRef
