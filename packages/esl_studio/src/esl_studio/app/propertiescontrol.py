#! /usr/bin/python

import os

from . import utils as Utils
from .propertieschangeevent import EVT_PROPERTIES_CHANGE
from .alterations import PropertyAlteration
from .application import diagramactions as dgAction
from .application.attribute import Attribute

PropertiesKnownElements = [ "rect", "ellipse", "line", "text", "image", "polyline", "polygon", "spline" ]

PropertyRefSeparator = '|'
PropertyIdSeparator = ':'
PropertyChildSeparator = '.'

ElementsProperties = {
    # We dont support "x", "y", "orientation"
    "rect": ["stroke", "stroke-width", "fill", "width", "height", "corner"],
    "ellipse": ["stroke", "stroke-width", "fill", "width", "height"],
    "line": ["stroke", "stroke-width", "x2", "y2"],
    "text": ["fill", "text", "font-family", "font-size", "font-style", "font-weight"], #text is actually contents of XML <text> element
    "image": ["src"],
    "polyline": ["stroke", "stroke-width"],
    "polygon": ["stroke", "stroke-width", "fill"],
    "spline": ["stroke", "stroke-width" "fill", "width", "height", "corner"],
    "annotation-text": ["fill", "font-family", "font-size", "font-style", "font-weight"]
}
ElementPropertyValuetypes = { # if not text
    "font-style":"choiceFontStyle",
    "font-weight":"choiceFontWeight"}

class PropertiesRowDefn(object):
    def __init__(self, tag, name, value, valuetype, col2text = None):
        self.tag = tag # id of property
        self.name = name
        self.value = value
        self.valuetype = valuetype
        self.col2text = col2text

class PropertiesPageDefn(object):
    def __init__(self, category):
        self.category = category
        self.propertyId = ''
        self.colHeadings = None
        self.propertyRowDefns = []

class PropertiesControl(object):
    def __init__(self, control):
        self._control = control

    def setup(self):
        self._frame = self._control.frame()
        self._entities = self._control.entities()
        self._application = self._frame.application()
        propertiesview = self._frame.viewManager().propertiesView()

        self.registerEvents()

    def registerEvents(self):
        self._frame.Bind(EVT_PROPERTIES_CHANGE, self.onPropertiesChange) # it doesnt like source propertiesview

    def resetPropertiesForNewApplication(self):
        self._frame.viewManager().propertiesView().resetPropertiesForNewApplication()

    def clearPropertyPage(self, headerText = 'No Properties'):
        propertiesview = self._frame.viewManager().propertiesView()
        propertiesview.clearPropertyPage(headerText)

    def setEntityPropertyPage(self, type, canvas, objectId):
        canvasinfo = self._application.getCanvasInfo(canvas)#[canvasId, model/submodel, name]
        if canvasinfo:
            pageType = 'entity'
            canvasId = canvasinfo[0]
            canvasname = canvasinfo[2]
            propertyId = str(canvasId) + PropertyIdSeparator + str(objectId)
            headerText = type + ' (' + str(objectId) + ') in ' + canvasinfo[1] + ' ' + canvasname
            propertiesview = self._frame.viewManager().propertiesView()
            entity = self._application.getEntityForCanvasObjectIds(canvasId, objectId)
            if entity:
                propertiesview.setEntityPropertyPage(pageType, propertyId, headerText)
            else:
                headerText = "Invalid entity "+headerText
                self.clearPropertyPage(headerText)
        else:
            self.clearPropertyPage()

    def refreshEntityProperties(self, entity):
        propertiesView = self._frame.viewManager().propertiesView()
        category = 'entity'
        if propertiesView.category() == category:
            canvasId = entity.parent().canvas().canvasId()
            objectId = entity.objectId()
            propertyId = str(canvasId) + PropertyIdSeparator + str(objectId)
            if propertiesView.propertyId() == propertyId:
                propertiesView.updateProperties(category, propertyId, None, None)

    def setCanvasPropertyPage(self, canvas):
        moduleId = canvas.moduleId()
        if moduleId:
            module = self._application.getModuleById(moduleId)
            pageType = module.moduleType()
            propertyId = moduleId
            headerText = module.identification()
            propertiesview = self._frame.viewManager().propertiesView()
            propertiesview.setCanvasPropertyPage(pageType, propertyId, headerText)
        else:
            self.clearPropertyPage()

    def setCodePropertyPage(self, moduleId):
        if moduleId:
            module = self._application.getModuleById(moduleId)
            moduleType = module.moduleType() # submodel
            propertyId = moduleId
            pageType = module.codeType()
            headerText = module.identification(showSubType=True)
            propertiesview = self._frame.viewManager().propertiesView()
            #propertiesview.setPropertyPage(category, propertyId, caption,
            #    colHeadings, tags, names, values, valuetypes, col2texts)
            propertiesview.setCodePropertyPage(pageType, propertyId, headerText)
        else:
            self.clearPropertyPage()

    def setCodeProperty(self, moduleId, propertyName, value, change=False):
        if moduleId:
            module = self._application.getModuleById(moduleId)
            propertiesview = self._frame.viewManager().propertiesView()
            if moduleId == propertiesview.moduleId():
                propertiesview.setCodeProperty(moduleId, propertyName, value, change)

    def setElementPropertyPage(self, elementName, canvas, objectId, elementXmlElement):
        canvasinfo = self._application.getCanvasInfo(canvas)#[canvasId, moduleType, name]
        tags = ElementsProperties[elementName]
        if canvasinfo and tags:
            pageType = elementName
            canvasId = canvasinfo[0]
            canvasname = canvasinfo[2]
            propertyId = str(canvasId) + PropertyIdSeparator + str(objectId)
            headerText = elementName + ' (' + str(objectId) + ') in ' + canvasinfo[1] + ' ' + canvasname
            propertiesview = self._frame.viewManager().propertiesView()
            propertiesview.setElementPropertyPage(pageType, propertyId, headerText,
                elementXmlElement)
        else:
            self.clearPropertyPage()

    def setDisplayPropertyPage(self, type, canvas, objectId):
        canvasinfo = self._application.getCanvasInfo(canvas)#[canvasId, moduleType, name]
        if canvasinfo:
            pageType = 'display'
            canvasId = canvasinfo[0]
            canvasname = canvasinfo[2]
            propertyId = str(canvasId) + PropertyIdSeparator + str(objectId)
            headerText = type + ' (' + str(objectId) + ') in ' + canvasinfo[1] + ' ' + canvasname
            propertiesview = self._frame.viewManager().propertiesView()
            propertiesview.setDisplayPropertyPage(pageType, propertyId, headerText)
        else:
            self.clearPropertyPage()

    def setGroupPropertyPage(self, groupType, canvas, objectId, groupXmlElement):
        canvasinfo = self._application.getCanvasInfo(canvas)#[canvasId, moduleType, name]
        if canvasinfo:
            pageType = "group"
            canvasId = canvasinfo[0]
            canvasname = canvasinfo[2]
            propertyId = str(canvasId) + PropertyIdSeparator + str(objectId)
            headerText = groupType
            if not headerText: headerText = "group"
            headerText += ' (' + str(objectId) + ') in ' + canvasinfo[1] + ' ' + canvasname
            propertiesview = self._frame.viewManager().propertiesView()
            propertiesview.setGroupPropertyPage(pageType, propertyId, headerText,
                groupXmlElement)
            ##self.clearPropertyPage(headerText)
        else:
            self.clearPropertyPage()

    def onPropertiesChange(self, propertieschange_event, suppressSelectionChange=False):
        valid, updatedPropertyValue = self.validatePropertyChange(
            propertieschange_event.category,
            propertieschange_event.propertyId,
            propertieschange_event.propertyTag,
            propertieschange_event.newValue,
            propertieschange_event.oldValue)
        msg = "PROPERTY: "
        msg += ' cat='+propertieschange_event.category
        msg += ' pid='+str(propertieschange_event.propertyId)
        msg += ' tag='+str(propertieschange_event.propertyTag)
        msg += ' new='+str(propertieschange_event.newValue)
        msg += ' old='+str(propertieschange_event.oldValue)
        msg += ' valid='+str(valid)
        msg += ' updatedPropertyValue='+str(updatedPropertyValue)
        msg += '\n'
        self._frame.control().appendMessage(msg, 1)
        if not valid:
            propertieschange_event.Veto()
        else:
            newValue = propertieschange_event.newValue
            if updatedPropertyValue is not None:
                newValue = updatedPropertyValue
            self.doPropertyChange(propertieschange_event.category,
                                  propertieschange_event.propertyId,
                                  propertieschange_event.propertyTag,
                                  newValue,
                                  propertieschange_event.oldValue,
                                  propertieschange_event.newValue,
                                  raiseSelectionEvent=False,
                                  updatePropertiesView=False,
                                  suppressSelectionChange=suppressSelectionChange)
        return valid

    def validatePropertyChange(self, category, propertyId, propertyTag, newValue, oldValue):
        valid = False
        updatedPropertyValue = None
        updatedOldPropertyValue = None
        val_type = ''
        val_item = propertyTag
        val_oldValue = str(oldValue)
        val_newValue = str(newValue)
        rejection = ''
        moduleId = 0
        canvas = None
        restorePropertiesView = False
        if category == 'module-property':
            val_type = 'Module Property'
            moduleId = int(propertyId) # propertyId is (now) moduleId
            module = self._application.getModuleById(moduleId)
            if module:
                val_item = module.eslname() + PropertyChildSeparator + propertyTag
                valid, rejection, val_type, val_item, val_oldValue, val_newValue = module.validateModulePropertyChange(propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue)

                # Extra handling to validate code subprograms.
                if valid and module.moduleType() == 'code':
                    if propertyTag == 'ESL':
                        items = val_oldValue.split("\n")
                        val_oldValue = ""
                        for item in items:
                            if item:
                                val_oldValue = item
                                break
                        if val_oldValue: val_oldValue += "..."
                        items = val_newValue.split("\n")
                        val_newValue = ""
                        for item in items:
                            if item:
                                val_newValue = item
                                break
                        if val_newValue: val_newValue += "..."

                    validateCodeResults = module.validateCodeSubprograms(propertyTag, newValue, askForReplacing=True)
                    rejection = validateCodeResults[0]
                    valid = not rejection
                    if valid:
                        updatedPropertyValue = validateCodeResults[1]
                        updatedOldPropertyValue = validateCodeResults[2]
                        if not module.valid():
                            codeCheckErrTxt = module.identification(showSubType=True) + " code check (warning) message(s):\n" + module.parseMessages() + "\n"
                            self._control.appendMessage(codeCheckErrTxt)
                            Utils.bleep()
                    elif propertyTag == 'ESL':
                        restorePropertiesView = True

        elif category == 'entity-property':
            val_type = 'Entity'
            val_item = propertyTag
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                entity = self._application.getEntityForCanvasObjectIds(propertyIdSplit[0], propertyIdSplit[1])
                moduleId = entity.parent().parent().moduleId()
                val_type = "'"+entity.identification()+"'"
                valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue = \
                    entity.validateEntityPropertyChange(propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue)

        elif category == 'special-property':
            val_type = 'Special'
            val_item = propertyTag
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                entity = self._application.getEntityForCanvasObjectIds(propertyIdSplit[0], propertyIdSplit[1])
                moduleId = entity.parent().parent().moduleId()
                val_type = "'"+entity.identification()+"'"
                valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue = \
                    entity.validateEntityPropertyChange(propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue)

        elif category == 'entity-attribute':
            val_type = 'Attribute'
            if propertyTag.endswith(Attribute.ValueEnumRefExtn):    # If property is an ESLValue posing as a ValueEnun - remove the property ref extension to find the corresponding entity's attribute..
                propertyTag = propertyTag[:-len(Attribute.ValueEnumRefExtn)]
            val_item = propertyTag
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                entity = self._application.getEntityForCanvasObjectIds(propertyIdSplit[0], propertyIdSplit[1])
                canvas = self._application.getCanvasForCanvasId(propertyIdSplit[0])
                if entity and canvas:
                    moduleId = canvas.moduleId()
                    val_item = "'"+entity.identification()+"'"
                    attribute = entity.attributes().get(propertyTag)
                    if attribute:
                        valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue = \
                            entity.validateEntityAttributePropertyChange(propertyTag, newValue, attribute, val_type, val_item, val_oldValue, val_newValue)

        elif category == 'entity-port':
            val_type = 'Port'
            val_item = propertyTag
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                entity = self._application.getEntityForCanvasObjectIds(propertyIdSplit[0], propertyIdSplit[1])
                canvas = self._application.getCanvasForCanvasId(propertyIdSplit[0])
                portId = propertyTag
                if entity and canvas:
                    val_item = "'"+entity.identification()+"'"
                    moduleId = canvas.moduleId()
                    module = entity.parent().parent()
                    port = entity.ports().get(portId)
                    if port:
                        valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue = \
                            port.validatePortPropertyChange(propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue)

        elif category == 'simulationparameter':
            val_type = 'Simulation Parameter'
            moduleNameDotSimulationParameterName = propertyId.split(PropertyChildSeparator)
            if len(moduleNameDotSimulationParameterName) == 2:
                module = self._application.getModuleByName(moduleNameDotSimulationParameterName[0])
                if module and module.simulationParameters():
                    moduleId = module.moduleId()
                    simPar = module.simulationParameters().parameters().get(moduleNameDotSimulationParameterName[1])
                    if simPar:
                        valid, rejection, val_type, val_item, updatedPropertyValue = simPar.validateSimulationParameterPropertyChange(module, propertyTag, newValue, val_type, val_item)

        elif category == 'setupinfo':
            val_type = 'Setup Info'
            moduleId = self._application.setupInfo().moduleId()
            valid = True # setup always valid

        elif category == 'package-property':
            val_type = 'Package Property'
            moduleId = int(propertyId) # propertyId is package moduleId
            package = self._application.getPackageById(moduleId)
            if package:
                val_item = package.eslname() + PropertyChildSeparator + propertyTag
                valid, rejection, val_type, val_item, val_oldValue, val_newValue = package.validateModulePropertyChange(propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue)

        elif category == 'package-variable': # change value or other feature
            val_type = 'Package Variable'
            moduleId = int(propertyId)
            package = self._application.getPackageById(moduleId)    # propertyId is package moduleId
            if package:
                variable = package.getVariableById(int(propertyTag))     # propertyTag is variable variableId
                if variable:
                    val_item = package.eslname() + PropertyChildSeparator + variable.eslname()
                    valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue = \
                        variable.validateVariablePropertyChange(package, propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue)

        elif category == 'module-parameter': # change value or other feature
            val_type = 'Parameter'
            moduleId = int(propertyId)
            if moduleId and moduleId == self._application.program().moduleId():
                if self._application.program().model():
                    moduleId = self._application.program().model().moduleId()
            module = self._application.getModuleById(moduleId)
            if module:
                variable = module.getVariableById(int(propertyTag))     # propertyTag is variable variableId
                if variable:
                    val_item = module.eslname() + PropertyChildSeparator + variable.eslname()
                    valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue = \
                        variable.validateVariablePropertyChange(module, propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue)

        elif category == 'element-property' or category == 'annotation-text':
            val_type = 'Element'
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                canvas = self._application.getCanvasForCanvasId(propertyIdSplit[0])
                if canvas:
                    moduleId = canvas.moduleId()
                    valid = True

        elif category == 'display-property':
            val_type = 'Display'
            val_item = propertyTag
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                display = self._application.getDisplayForCanvasObjectIds(propertyIdSplit[0], propertyIdSplit[1])
                moduleId = display.parent().parent().moduleId()
                val_type = (display.type() + '-' + str(display.objectId())).title()
                valid, rejection, val_type, val_item = display.validateDisplayPropertyChange(propertyTag, newValue, val_type, val_item)

        elif category == 'group-property':
            val_type = 'Group'
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                canvas = self._application.getCanvasForCanvasId(propertyIdSplit[0])
                if canvas:
                    moduleId = canvas.moduleId()
                    valid = True

        if valid and moduleId:
            if updatedPropertyValue is not None:
                if val_newValue == newValue:
                    val_newValue = updatedPropertyValue
                newValue = updatedPropertyValue
            if updatedOldPropertyValue is not None:
                oldValue = updatedOldPropertyValue
            self._control.alterationStack().add(
                PropertyAlteration(moduleId, category, propertyId, propertyTag, oldValue, newValue))
        msg = "Change " + val_type + " property '" + val_item + "' from '" + val_oldValue + "' to '" + val_newValue + "'"
        diagnosticVerbosity = 1
        if not valid:
            if not rejection:
                rejection = "invalid property change"
            msg += " rejected - " + rejection
            diagnosticVerbosity = 0
        msg += '\n'
        self._control.appendMessage(msg, diagnosticVerbosity)
        if not valid:
            Utils.bleep()
            if restorePropertiesView:
                propertiesview = self._frame.viewManager().propertiesView()
                propertiesview.updateProperties(category, propertyId, propertyTag, oldValue)
        return valid, updatedPropertyValue

    def doPropertyChange(self, category, propertyId, propertyTag, newValue, oldValue, origNewValue,
                         raiseSelectionEvent=True, updatePropertiesView=True,
                         suppressSelectionChange=False, suppress_action=False, alterationReason=None):
        if category == 'module-property': # propertyId is (now) moduleId
            moduleId = int(propertyId)
            module = self._application.getModuleById(moduleId)
            if module:
                self._application.updateModuleProperty(module, propertyTag, newValue, suppress_action=suppress_action, alterationReason=alterationReason)
                moduleType = module.moduleType()

                if not updatePropertiesView and moduleType == "program" and propertyTag == "programType" and module.model():
                    updatePropertiesView = True

                if not updatePropertiesView and moduleType == 'code' and (propertyTag == 'ESL' or propertyTag == 'file'):
                    updatePropertiesView = True

                if propertyTag == "experiment" or propertyTag == "modelType":
                    simulationparametersview = self._frame.viewManager().simulationParametersView()
                    simulationparametersview.hideExperimentWarning(newValue == "")
                    # -- cant invoke updateProperties as this called in OnPropGridChanging
                    #    updatePropertiesView = True # may need to redisplay the properties (for the experiment)

                if moduleType != 'code':
                    canvas = None
                    if moduleType == "program":
                        if module.model():
                            canvas = module.model().diagramInfo().canvas()
                    else:
                        canvas = module.diagramInfo().canvas()
                    if canvas:
                        self._control.selectObjects(canvas, [], raiseSelectionEvent)
                else:
                    page = self._frame.viewManager().mainView().getCodeViewByModuleId(moduleId)
                    pageindex = self._frame.viewManager().mainView().GetPageIndex(page)
                    if not suppressSelectionChange:
                        self._frame.viewManager().mainView().SetSelection(pageindex)
                        self._frame.viewManager().applicationView().selectItem('submodel', moduleId)
                if updatePropertiesView:
                    propertiesview = self._frame.viewManager().propertiesView()
                    propertiesview.updateProperties(category, propertyId, propertyTag, newValue)

        elif category == 'entity-property':
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                canvas = self._application.getCanvasForCanvasId(propertyIdSplit[0])
                entity = self._application.getEntityForCanvasObjectIds(propertyIdSplit[0], propertyIdSplit[1])
                if entity and canvas:
                    refreshEntityProperty = entity.updateEntityProperty(propertyTag, newValue, suppress_action=suppress_action)
                    dgAction.sendUpdateEntityPropertyAnnotations(entity)
                    self._control.selectObjects(canvas, [entity.objectId()], raiseSelectionEvent)
                    if updatePropertiesView or refreshEntityProperty:
                        # Queue a deferred call to refreshEntityProperties - works around the property grid temporarily reverts to pre-update value if click on the grid issue.
                        Utils.queueFunctionCall(self.refreshEntityProperties, entity)

        elif category == 'special-property':
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                canvas = self._application.getCanvasForCanvasId(propertyIdSplit[0])
                entity = self._application.getEntityForCanvasObjectIds(propertyIdSplit[0], propertyIdSplit[1])
                if entity and canvas:
                    refreshEntityProperty = entity.updateEntityProperty(propertyTag, newValue, suppress_action=suppress_action)
                    dgAction.sendUpdateEntityPropertyAnnotations(entity)
                    if updatePropertiesView or refreshEntityProperty or origNewValue != newValue:
                        # Queue a deferred call to refreshEntityProperties - works around the property grid temporarily reverts to pre-update value if click on the grid issue.
                        Utils.queueFunctionCall(self.refreshEntityProperties, entity)

                    self._control.selectObjects(canvas, [entity.objectId()], raiseSelectionEvent)

        elif category == 'entity-attribute':
            propertyTagInEntity = propertyTag
            if propertyTag.endswith(Attribute.ValueEnumRefExtn):
                propertyTagInEntity = propertyTag[:-len(Attribute.ValueEnumRefExtn)]
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                entity = self._application.getEntityForCanvasObjectIds(propertyIdSplit[0], propertyIdSplit[1])
                canvas = self._application.getCanvasForCanvasId(propertyIdSplit[0])
                if entity and canvas:
                    moduleId = canvas.moduleId()
                    module = entity.parent().parent()
                    attribute = entity.getAttribute(propertyTagInEntity)
                    if attribute:
                        tempOldAttribute = Attribute(None)
                        tempOldAttribute.loadData(attribute.save(None, 0, True), suppressAddName=True)
                        attribute.set_valueData(newValue, suppressAddName=True)
                        updateEntityPropertiesView = entity.updateEntityAttributeProperty(propertyTag, newValue, attribute, tempOldAttribute, suppress_action=suppress_action)
                        if updateEntityPropertiesView:
                            updatePropertiesView = True

                        annotationId, annotationTxt, annotationVisible = dgAction.setEntityAttributeAnnotations(attribute)
                        dgAction.sendAnnotationUpdate(entity, annotationId, annotationTxt, annotationVisible)

                        propertiesview = self._frame.viewManager().propertiesView()
                        if updatePropertiesView:
                            propertiesview.updateProperties("entity", propertyId, propertyTag, newValue)
                        else:
                            propertyRef = propertiesview.getAttPropertyRef(category, propertyId, propertyTag)
                            attributeProperty = propertiesview.variableProperties().get(propertyRef)
                            if attributeProperty:
                                if oldValue != newValue:
                                    attributeProperty.updateFields(newValue)

                    self._control.selectObjects(canvas, [entity.objectId()], raiseSelectionEvent)

        elif category == 'entity-port':
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                entity = self._application.getEntityForCanvasObjectIds(propertyIdSplit[0], propertyIdSplit[1])
                canvas = self._application.getCanvasForCanvasId(propertyIdSplit[0])
                portId = propertyTag
                if entity and canvas:
                    moduleId = canvas.moduleId()
                    module = entity.parent().parent()
                    port = entity.ports().get(portId)
                    if port:
                        port.updatePortProperty(propertyTag, newValue, suppress_action=suppress_action)
                        refreshPortProperty = None
                        propertiesview = self._frame.viewManager().propertiesView()
                        propertyRef = 'O' + PropertyRefSeparator + propertyId + PropertyRefSeparator + propertyTag
                        portProperty = propertiesview.variableProperties().get(propertyRef)
                        if portProperty:
                            currentValue = portProperty.propertyValue()
                            if currentValue != newValue:
                                refreshPortProperty = port
                        if updatePropertiesView:
                            propertiesview.updateProperties(category, propertyId, propertyTag, newValue)
                        elif refreshPortProperty:
                            portProperty.updateFields(newValue)
                    self._control.selectObjects(canvas, [entity.objectId()], raiseSelectionEvent)

        elif category == 'simulationparameter':
            moduleNameDotSimulationParameterName = propertyId.split(PropertyChildSeparator)
            if len(moduleNameDotSimulationParameterName) == 2:
                module = self._application.getModuleByName(moduleNameDotSimulationParameterName[0])
                if module and module.simulationParameters():
                    simPar = module.simulationParameters().parameters().get(moduleNameDotSimulationParameterName[1])
                    if simPar:
                        simPar.eslValue().loadStr(newValue, checkValidity=False)
                        self._frame.viewManager().showView("SimulationParametersView")
                        if updatePropertiesView or origNewValue != newValue:
                            simulationparametersview = self._frame.viewManager().simulationParametersView()
                            # Queue a deferred call to updateSimulationParameters - works around the simulation parameter view property grid temporarily reverts to pre-update value if click on the grid issue.
                            Utils.queueFunctionCall(
                                simulationparametersview.updateSimulationParameters, (propertyId, newValue))

        elif category == 'setupinfo':
            self._frame.viewManager().showView("SetupView")
            setupInfo = self._application.setupInfo()
            setupInfo.setData(newValue)
            setupView = self._frame.viewManager().setupView()
            setupView.updateData(newValue)

        elif category == 'package-property':
            package = self._application.getPackageById(int(propertyId))   # propertyId is package moduleId
            if package:
                if propertyTag == 'eslname':
                    prevName = package.eslname()
                    self._application.updatePackageName(package, newValue)
                elif propertyTag == 'description':
                    package.set_description(newValue)
                packageview = self._frame.viewManager().mainView().getPackageViewByModuleId(package.moduleId())
                if updatePropertiesView:
                    packageview.updatePackage(category, propertyId, propertyTag, newValue)
                pageindex = self._frame.viewManager().mainView().GetPageIndex(packageview)
                self._frame.viewManager().mainView().SetSelection(pageindex)
                self._frame.viewManager().applicationView().selectItem('package', package.moduleId())
                self.clearPropertyPage()
                if propertyTag == 'eslname':
                    # Update any entity attribute annotations that have any of these package variables as Source.
                    for variable in list(package.variables().values()):
                        for attribute in variable.assignedAttributes():
                            attribute.set_source(package.eslname())
                            annotationId, annotationTxt, annotationVisible = dgAction.setEntityAttributeAnnotations(attribute)
                            dgAction.sendAnnotationUpdate(attribute.parent(), annotationId, annotationTxt, annotationVisible)


        elif category == 'package-variable': # change value or other feature
            package = self._application.getPackageById(int(propertyId))    # propertyId is package moduleId
            if package:
                variable = package.getVariableById(int(propertyTag))     # propertyTag is variable variableId
                if variable:
                    variable.updateVariableProperty(package, propertyTag, newValue, suppress_action=suppress_action)
                    packageview = self._frame.viewManager().mainView().getPackageViewByModuleId(package.moduleId())
                    refreshVariableProperty = None
                    propertyRef = packageview.getVarPropertyRef(propertyId, propertyTag)
                    variableProperty = packageview.variableProperties().get(propertyRef)
                    if variableProperty:
                        currentValue = variableProperty.propertyValue()
                        if currentValue != newValue:
                            refreshVariableProperty = variable
                    if updatePropertiesView:
                        packageview.updatePackage(category, propertyId, propertyTag, newValue)
                    elif refreshVariableProperty:
                        variableProperty.updateFields(newValue)
                    pageindex = self._frame.viewManager().mainView().GetPageIndex(packageview)
                    self._frame.viewManager().mainView().SetSelection(pageindex)
                    self._frame.viewManager().applicationView().selectItem('package', package.moduleId())
                    self.clearPropertyPage()

        elif category == 'module-parameter': # change value or other feature
            moduleId = int(propertyId)
            if moduleId and moduleId == self._application.program().moduleId():
                if self._application.program().model():
                    moduleId = self._application.program().model().moduleId()
            module = self._application.getModuleById(moduleId)
            if module:
                variable = module.getVariableById(int(propertyTag))     # propertyTag is variable variableId
                if variable:
                    variable.updateVariableProperty(module, propertyTag, newValue, suppress_action=suppress_action)
                    page = self._frame.viewManager().mainView().getCanvasByModuleId(module.moduleId())
                    pageindex = self._frame.viewManager().mainView().GetPageIndex(page)
                    self._frame.viewManager().mainView().SetSelection(pageindex)
                    self._frame.viewManager().applicationView().selectItem(module.moduleType(), module.moduleId())
                    propertiesview = self._frame.viewManager().propertiesView()
                    refreshVariableProperty = None
                    propertyRef = propertiesview.getVarPropertyRef(propertyId, propertyTag)
                    variableProperty = propertiesview.variableProperties().get(propertyRef)
                    if variableProperty:
                        currentValue = variableProperty.propertyValue()
                        if currentValue != newValue:
                            refreshVariableProperty = variable
                    if updatePropertiesView:
                        propertiesview.updateProperties(category, propertyId, propertyTag, newValue)
                    elif refreshVariableProperty:
                        variableProperty.updateFields(newValue)

        elif category == 'element-property' or category == 'annotation-text':
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                subprogram = self._application.getSubprogramForCanvasId(propertyIdSplit[0])
                objectId = propertyIdSplit[1]
                dgAction.sendDiagramUpdate(subprogram.diagramInfo(), newValue, applicationDataType="", applicationDataContents="", secondary=False, raiseEvent=False)
                canvas = subprogram.diagramInfo().canvas()
                canvas.Refresh()
                #canvas.SelectObjects([objectId], True)
                if category == 'annotation-text':
                    CompositeObjectSeparator = "+" # from grob.object
                    idSplit = objectId.split(CompositeObjectSeparator)
                    # go up a level - which will be the annotation
                    objectId = CompositeObjectSeparator.join(idSplit[0:-1])
                self._control.selectObjects(canvas, [objectId], raiseSelectionEvent) # not sure if should force this selection here

        elif category == 'display-property':
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                canvas = self._application.getCanvasForCanvasId(propertyIdSplit[0])
                display = self._application.getDisplayForCanvasObjectIds(propertyIdSplit[0], propertyIdSplit[1])
                if display and canvas:
                    display.updateDisplayProperty(propertyTag, newValue)
                    self._control.selectObjects(canvas, [display.objectId()], raiseSelectionEvent)

        elif category == 'group-property':
            propertyIdSplit = propertyId.split(PropertyIdSeparator)
            if propertyIdSplit and len(propertyIdSplit) == 2:
                subprogram = self._application.getSubprogramForCanvasId(propertyIdSplit[0])
                objectId = propertyIdSplit[1]
                dgAction.sendDiagramUpdate(subprogram.diagramInfo(), newValue, applicationDataType="", applicationDataContents="", secondary=False, raiseEvent=False)
                canvas = subprogram.diagramInfo().canvas()
                canvas.Refresh()
                #canvas.SelectObjects([objectId], True)
                self._control.selectObjects(canvas, [objectId], raiseSelectionEvent) # not sure if should force this selection here
