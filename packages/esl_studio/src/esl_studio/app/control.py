#! /usr/bin/python

import sys
import os

import wx

import esl_diagram.xmlutil as xut
import esl_diagram.canvas as canv

from .general import APP_NAME, PROFILE_DEFAULT_DIR
from . import utils as Utils
from .config import Config
from .profile import Profile
from . import auihandler as aui
from .propertiescontrol import PropertiesControl, PropertiesKnownElements
from .modulescontrol import ModulesControl
from .simulationcontrol import SimulationControl
from .clipboard import Clipboard
from .views.view import ModuleView
from .views.isemodelview import IseModelView
from .views.codeview import CodeView
from .views.packageview import PackageView
from .views.simulationparametersview import SimulationParametersView
from .views.stc import Stc
from .alterations import AlterationStack, CanvasAlteration
from .application.simulationentity import SimulationEntity
from .application.displaydefinition import DisplayDefinition
from .application.infoblock import InfoBlock
from .application.setupinfo import SetupInfo

from .esl.entities import Entities
from .esl.generate import Generate

DEFAULT_BLOCK_DIAGRAM_ENTITY_COMPONENTS = \
    '<definitions>\
\
		<!-- Standard entity component definitions (may be overridden) -->\
\
		<!-- Nodes - Real Integer Logical -->\
		<def category="node" type="Real">\
			<ellipse width="8" height="8" stroke="blue" stroke-width="2" fill="yellow"/>\
			<context-menu menu="node"/>\
		</def>\
\
		<def category="node" type="Integer">\
			<ellipse width="8" height="8" stroke="green" stroke-width="2" fill="yellow"/>\
			<context-menu menu="node"/>\
		</def>\
\
		<def category="node" type="Logical">\
			<ellipse width="8" height="8" stroke="red" stroke-width="2" fill="yellow"/>\
			<context-menu menu="node"/>\
		</def>\
\
		<!-- Links - Real Integer Logical -->\
		<def category="link" type="Real" stroke="blue" stroke-width="2">\
			<context-menu menu="link"/>\
		</def>\
\
		<def category="link" type="Integer" stroke="green" stroke-width="2">\
			<context-menu menu="link"/>\
		</def>\
\
		<def category="link" type="Logical" stroke="red" stroke-width="2">\
			<context-menu menu="link"/>\
		</def>\
\
		<!-- Ports - Real Integer Logical (options for direction:input, sign:plus|minus) -->\
		<def category="port" type="Real">\
			<line x2="-14" y2="0" stroke="blue" stroke-width="3"/>\
			<ellipse width="8" height="8" stroke="blue" stroke-width="2" fill="yellow"/>\
			<option direction="input">\
				<polyline stroke="blue" stroke-width="2" points="-8,-6 -14,0 -8,6"/>\
			</option>\
			<option sign="plus">\
				<text x="-5" y="-10" font-size="12">+</text>\
				<context-menu menu="port"/>\
			</option>\
			<option sign="minus">\
				<text x="-5" y="-10" font-size="12">-</text>\
				<context-menu menu="port"/>\
			</option>\
			<activate action="Toggle Port Sign"/>\
		</def>\
\
		<def category="port" type="Integer">\
			<line x2="-14" y2="0" stroke="green" stroke-width="3"/>\
			<ellipse width="8" height="8" stroke="green" stroke-width="2" fill="yellow"/>\
			<option direction="input">\
				<polyline stroke="green" stroke-width="2" points="-8,-6 -14,0 -8,6"/>\
			</option>\
			<option sign="plus">\
				<text x="-5" y="-10" font-size="12">+</text>\
				<context-menu menu="port"/>\
			</option>\
			<option sign="minus">\
				<text x="-5" y="-10" font-size="12">-</text>\
				<context-menu menu="port"/>\
			</option>\
			<activate action="Toggle Port Sign"/>\
		</def>\
\
		<def category="port" type="Logical">\
			<line x2="-14" y2="0" stroke="red" stroke-width="3"/>\
			<ellipse width="8" height="8" stroke="red" stroke-width="2" fill="yellow"/>\
			<option direction="input">\
				<polyline stroke="red" stroke-width="2" points="-8,-6 -14,0 -8,6"/>\
			</option>\
			<option sign="plus">\
				<text x="-5" y="-10" font-size="12">+</text>\
				<context-menu menu="port"/>\
			</option>\
			<option sign="minus">\
				<text x="-5" y="-10" font-size="12">-</text>\
				<context-menu menu="port"/>\
			</option>\
			<activate action="Toggle Port Sign"/>\
		</def>\
\
		<!-- Standard entity shape definitions (may be overridden) -->\
		<def category="group" type="std-entity-box">\
			<rect width="60" height="40" corner="0" fill="light grey" stroke="black" stroke-width="2"/>\
		</def>\
\
		<def category="group" type="std-entity-circle">\
			<ellipse width="40" height="40" fill="light grey" stroke="black" stroke-width="2"/>\
		</def>\
\
		<def category="group" type="std-input-argument-box">\
			<rect width="60" height="40" corner="0" fill="light grey" stroke="black" stroke-width="2"/>\
		</def>\
\
		<def category="group" type="std-output-argument-box">\
			<rect width="60" height="40" corner="0" fill="light grey" stroke="black" stroke-width="2"/>\
		</def>\
\
		<def category="group" type="std-subprogram-box">\
			<rect width="60" height="40" corner="0" fill="light grey" stroke="black" stroke-width="2"/>\
		</def>\
    </definitions>'
DEFAULT_MODEL_DIAGRAM_ENTITY_COMPONENTS = \
    '<default-model-diagram-definitions>\n'+ \
    DEFAULT_BLOCK_DIAGRAM_ENTITY_COMPONENTS + '\n' + \
    '</default-model-diagram-definitions>'

DEFAULT_SUBPROGRAM_DIAGRAM_ENTITY_COMPONENTS = \
    '<default-subprogram-diagram-definitions>\n'+ \
    DEFAULT_BLOCK_DIAGRAM_ENTITY_COMPONENTS + '\n' + \
    '</default-subprogram-diagram-definitions>'

class Control(object):

    def __init__(self, frame):
        self._frame = frame
        self._application = self._frame.application()
        self._entities = Entities(self)
        self._generate = Generate(self)
        self._propertiesControl = PropertiesControl(self)
        self._modulesControl = ModulesControl(self)
        self._simulationControl = SimulationControl(self)
        self._clipboard = Clipboard(self)
        self._alterationStack = AlterationStack(self)
        self._iseModelDiagramDefinitions = xut.XmlElement(DEFAULT_MODEL_DIAGRAM_ENTITY_COMPONENTS)
        self._iseSubprogramDiagramDefinitions = xut.XmlElement(DEFAULT_SUBPROGRAM_DIAGRAM_ENTITY_COMPONENTS)

        self._mode = "editing" # | "browsing"

    def frame(self): return self._frame
    def entities(self): return self._entities
    def generate(self): return self._generate
    def propertiesControl(self): return self._propertiesControl
    def modulesControl(self): return self._modulesControl
    def simulationControl(self): return self._simulationControl
    def clipboard(self): return self._clipboard
    def alterationStack(self): return self._alterationStack
    def iseModelDiagramDefinitions(self): return self._iseModelDiagramDefinitions
    def iseSubprogramDiagramDefinitions(self): return self._iseSubprogramDiagramDefinitions

    def mode(self):
        return self._mode

    def setup(self):
        file = Utils.resourceFile("esl-studio.ico")
        if file:
            icon = wx.Icon(file)
            self._frame.SetIcon(icon)
        self._entities.setup()
        self._generate.setup()
        self._propertiesControl.setup()
        self._modulesControl.setup()
        SetupInfo.setup(self)
        self._simulationControl.setup()
        self._clipboard.setup()
        self._alterationStack.setup()
        self._frame.viewManager().mainView().setup()
        self._frame.printing().setup()

        self.registerEvents()

        self.setProfile()

    def clearForProfiles(self):
        self._frame.applicationHistory().clear()
        self._frame.commands().clear()
        self._frame.viewManager().elementsView().clear()
        self._frame.viewManager().menubar().clear()
        self._frame.viewManager().toolbar().clear()
        self._entities.clear()
        self._frame.viewManager().mainView().programPage().ClearCanvasDefinitions()
        self._frame.viewManager().mainView().clearModelCanvases()
        self._frame.viewManager().mainView().clearSubprogramCanvases()
        self._iseModelDiagramDefinitions = xut.XmlElement(DEFAULT_MODEL_DIAGRAM_ENTITY_COMPONENTS)
        self._iseSubprogramDiagramDefinitions = xut.XmlElement(DEFAULT_SUBPROGRAM_DIAGRAM_ENTITY_COMPONENTS)

    def setProfile(self):
        wx.BeginBusyCursor()
        self.clearForProfiles()
        availableProfileFiles, missingProfileDirs = Profile.availableProfileFiles()
        for missingProfileDir in missingProfileDirs:
            msg = 'Profile directory "' + missingProfileDir + '" is not available\n'
            self.appendMessage(msg)
        disEnvedAvailableProfileFiles = list(map(Utils.disEnvVarPath, availableProfileFiles))
        profileFilesStr = Config.getValue('Profile/Profile Files')
        if not profileFilesStr:
            profileFiles = availableProfileFiles
            profileFilesStr = Config.PATH_SEPARATOR.join(profileFiles)
            Config.setValue('Profile/Profile Files', profileFilesStr)
        profileFiles = profileFilesStr.split(Config.PATH_SEPARATOR)
        for profileFile in profileFiles:
            msg = ''
            fullFilePath = Utils.disEnvVarPath(profileFile)
            profileDir = os.path.dirname(profileFile)
            if profileDir == PROFILE_DEFAULT_DIR:
                fullFilePath = os.path.join(Utils.defaultProfileDir(), os.path.basename(profileFile))
            if not os.path.isfile(fullFilePath):
                msg = 'Profile file "' + profileFile + '" not found\n'
                self.appendMessage(msg)
            else:
                if profileDir != PROFILE_DEFAULT_DIR and fullFilePath not in disEnvedAvailableProfileFiles:
                    msg = 'Profile file "'+profileFile+'" is not included in the '+APP_NAME+' profile path - loading anyway\n'
                    self.appendMessage(msg)
                self.loadProfileFile(fullFilePath)
        self.installProfile()
        self._frame.viewManager().menubar().checkRequiredMenuCommands()

        options = self.getBlockDiagramPropertyOptions(self._iseModelDiagramDefinitions)
        Config.setupBlockDiagramThemePropertyOptions(options)
        blockDiagramPropertyOptions = Config.getBlockDiagramPropertyOptions()

        self._frame.viewManager().mainView().setupModelCanvases(self._iseModelDiagramDefinitions, blockDiagramPropertyOptions)
        self._frame.viewManager().mainView().setupSubprogramCanvases(self._iseSubprogramDiagramDefinitions, blockDiagramPropertyOptions)

        # set view states - e.g. menubar checkboxes relating to views visible
        self.checkAllToggleViewItems()
        self.enableDisableMenuItems()
        wx.EndBusyCursor()

    def installProfile(self):
        self._frame.commands().installProfile()
        self._frame.viewManager().elementsView().installProfile()
        self._frame.viewManager().menubar().installProfile()
        self._frame.viewManager().toolbar().installProfile()
        self._entities.installProfile()

    def loadProfileFile(self, profileFile):
        xmlElement, error = xut.xmlElementFromFile(Utils.disEnvVarPath(profileFile))
        if xmlElement:
            self._frame.commands().loadFromXml(xmlElement)   # setup the commands available
            self.gatherDiagramDefinitions(xmlElement)
            self._frame.viewManager().elementsView().loadFromXml(xmlElement)
            self._frame.viewManager().menubar().loadFromXml(xmlElement)
            self._frame.viewManager().toolbar().loadFromXml(xmlElement)
            self._entities.loadFromXml(xmlElement)
        else:
            msg = 'Failed to load profile file "' + profileFile + '" as XML\n'
            if error: msg += error + "\n"
            self.appendMessage(msg)

    def gatherDiagramDefinitions(self, xmlElement):
        if xmlElement.name() == "diagram":
            self.gatherDiagramDefinition(xmlElement)
        else:
            canvasXmlElements = xmlElement.getXmlElementListByName("diagram")
            for canvasXmlElement in canvasXmlElements:
                self.gatherDiagramDefinition(canvasXmlElement)

    def gatherDiagramDefinition(self, canvasXmlElement):
        type = canvasXmlElement.getAttribute('type')
        self.appendDiagramDefinition(canvasXmlElement, type)

    def appendDiagramDefinition(self, canvasXmlElement, type):
        if not type or type == 'block-diagram':
            self._iseModelDiagramDefinitions.appendChild(canvasXmlElement)
            self._iseSubprogramDiagramDefinitions.appendChild(canvasXmlElement)
        elif type == 'model-diagram':
            self._iseModelDiagramDefinitions.appendChild(canvasXmlElement)
        elif type == 'subprogram-diagram':
            self._iseSubprogramDiagramDefinitions.appendChild(canvasXmlElement)

    def getBlockDiagramPropertyOptions(self, canvasXmlElement):
        options = [
            True,       # Show Grid
            0,          # Grid Snap
            "smart2segments"  # Smart Link
        ]
        if canvasXmlElement.name() == "diagram":
            diagramElements = [canvasXmlElement]
        else:
            diagramElements = canvasXmlElement.getXmlElementListByName("diagram", True)
        if diagramElements:
            for diagramElement in diagramElements:
                propertiesElements = diagramElement.getXmlElementListByName("properties", True)
                if propertiesElements:
                    for propertiesElement in propertiesElements:
                        gridElement = propertiesElement.getXmlElementByName("grid")
                        if gridElement:
                            gridshow = gridElement.getAttribute("show")
                            if gridshow and gridshow == 'false': options[0] = False
                            gridsnap = gridElement.getAttribute("snap")
                            if gridsnap: options[1] = int(gridsnap)
                        smartLinksElement = propertiesElement.getXmlElementByName("smart-links")
                        if smartLinksElement:
                            options[2] = smartLinksElement.getAttribute("smart-draw")
        return options

    def registerEvents(self):
        # set to be notified of create. delete & selection change in canvases
        #source = self._frame.viewManager().mainView().modelPage() # doesnt seem to work
        source = None
        self._frame.Bind(canv.EVT_CANVAS_SELECTED_OBJECTS,
                         self.OnCanvasSelectedObjects, source)#, id=wx.ID_ANY, id2=wx.ID_ANY)
        self._frame.Bind(canv.EVT_CANVAS_CHANGED_OBJECTS,
                         self.OnCanvasChangedObjects, source)#, id=wx.ID_ANY, id2=wx.ID_ANY)
        self._frame.Bind(canv.EVT_CANVAS_APPLICATION_REQUEST,
                         self.OnCanvasApplicationRequest, source)#, id=wx.ID_ANY, id2=wx.ID_ANY)
        self._frame.Bind(canv.EVT_CANVAS_APPLICATION_NOTIFY,
                         self.OnCanvasApplicationNotify, source)#, id=wx.ID_ANY, id2=wx.ID_ANY)
        #self._frame.Bind(canv.EVT_CANVAS_CREATED_OBJECTS,
        #                 self.OnCanvasCreatedObjects, source)#, id=wx.ID_ANY, id2=wx.ID_ANY)
        #self._frame.Bind(canv.EVT_CANVAS_DELETED_OBJECTS,
        #                 self.OnCanvasDeletedObjects, source)#, id=wx.ID_ANY, id2=wx.ID_ANY)
        #self._frame.Bind(canv.EVT_CANVAS_DRAGGED_OBJECTS,
        #                 self.OnCanvasDraggedObjects, source)#, id=wx.ID_ANY, id2=wx.ID_ANY)
        #self._frame.Bind(canv.EVT_CANVAS_LINKED_OBJECTS,
        #                 self.OnCanvasLinkedObjects, source)#, id=wx.ID_ANY, id2=wx.ID_ANY)
        #self._frame.Bind(canv.EVT_CANVAS_CLIP_REQUESTED,
        #                 self.OnCanvasClipRequested, source)#, id=wx.ID_ANY, id2=wx.ID_ANY)
        #self._frame.Bind(canv.EVT_CANVAS_PASTE_REQUESTED,
        #                 self.OnCanvasPasteRequested, source)#, id=wx.ID_ANY, id2=wx.ID_ANY)
        #self._frame.Bind(canv.EVT_CANVAS_APPLICATION_COMMAND_REQUESTED,
        #                 self.OnCanvasApplicationCommandRequested, source)#, id=wx.ID_ANY, id2=wx.ID_ANY)

        # set to be notified if a view (docked or floating) pane closes (cant get all restores so treat all as open)
        self._frame.Bind(aui.EVT_AUI_PANE_CLOSE, self.OnViewPaneChange)
        #self._frame.Bind(aui.EVT_AUI_PANE_MAXIMIZE, self.OnViewPaneChange)
        #self._frame.Bind(aui.EVT_AUI_PANE_MINIMIZE, self.OnViewPaneChange)
        #self._frame.Bind(aui.EVT_AUI_PANE_RESTORE, self.OnViewPaneChange)
        #self._frame.Bind(aui.EVT_AUI_PANE_MIN_RESTORE, self.OnViewPaneChange) # doesnt come through
        # set to be notified of mainview page change
        self._frame.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnMainViewPageChanged,
                         self._frame.viewManager().mainView())
        #
        self._frame.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnElementsViewItemActivated,
                         self._frame.viewManager().elementsView())
        self._frame.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnElementsViewBeginDragItem,
                         self._frame.viewManager().elementsView())
        #
        self._frame.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnApplicationViewItemActivated,
                         self._frame.viewManager().applicationView())
        self._frame.Bind(wx.EVT_TREE_SEL_CHANGING, self.OnApplicationViewItemSelChange,
                         self._frame.viewManager().applicationView())
        #self._frame.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnApplicationViewItemSelChange,
        #                 self._frame.viewManager().applicationView())
        #
        self._frame.Bind(wx.EVT_CHAR_HOOK, self.OnCharHook) # in lieu of KEY_DOWN

    def currentPage(self):
        page = None
        pageIx = self._frame.viewManager().mainView().GetSelection()
        if pageIx >= 0:
            page = self._frame.viewManager().mainView().GetPage(pageIx)
        return page

    def currentCanvas(self):
        page = None
        pageIx = self._frame.viewManager().mainView().GetSelection()
        if pageIx >= 0:
            page = self._frame.viewManager().mainView().GetPage(pageIx)
            if page and not isinstance(page, canv.Canvas):
                page = None
        return page

    def checkAllToggleViewItems(self):
        for commandId in self._frame.commands().commandDefnByCommandId:
            commandDefn = self._frame.commands().commandDefnByCommandId[commandId]
            if commandDefn and commandDefn.procedure == 'ToggleView':
                infoXmlElement = commandDefn.commandXmlElement.getXmlElementByName("info")
                if infoXmlElement:
                    viewname = infoXmlElement.getAttribute("viewname")
                    if viewname:
                        showing = self._frame.viewManager().viewIsShowing(viewname)
                        self._frame.viewManager().menubar().checkItem(commandId, showing)
                        self._frame.viewManager().toolbar().toggleItem(commandId, showing)

    def getToggleViewCommandDefn(self, viewname):
        result = None
        for commandId in self._frame.commands().commandDefnByCommandId:
            commandDefn = self._frame.commands().commandDefnByCommandId[commandId]
            if commandDefn and commandDefn.procedure == 'ToggleView':
                infoXmlElement = commandDefn.commandXmlElement.getXmlElementByName("info")
                if infoXmlElement:
                    checkable = infoXmlElement.getAttribute("checkable")
                    aname = infoXmlElement.getAttribute("viewname")
                    if aname and aname == viewname:
                        result = commandDefn
                        break
        return result

    def enableDisableUndoRedo(self): # for when only alteration stack changed (similar logic also in enableDisableMenuItems)
        undoEnable = False
        redoEnable = False
        state = self._alterationStack.state() # empty, end, beginning, between
        if state == 'between' or state == 'end': undoEnable = True
        if state == 'between' or state == 'beginning': redoEnable = True
        for commandId in self._frame.commands().commandDefnByCommandId:
            commandDefn = self._frame.commands().commandDefnByCommandId[commandId]
            if commandDefn and commandDefn.procedure == 'Undo':
                self._frame.viewManager().menubar().enableItem(commandId, undoEnable)
                self._frame.viewManager().toolbar().enableItem(commandId, undoEnable)
                break
        for commandId in self._frame.commands().commandDefnByCommandId:
            commandDefn = self._frame.commands().commandDefnByCommandId[commandId]
            if commandDefn and commandDefn.procedure == 'Redo':
                self._frame.viewManager().menubar().enableItem(commandId, redoEnable)
                self._frame.viewManager().toolbar().enableItem(commandId, redoEnable)
                break

    def enableDisableMenuItems(self):
        printCommands = { # enable for diagram, textView
            'PrintSaveDiagram': [True, False],
            #'PageSetup': [True, True], #keep 'PageSetup' always enabled
            'PrintPreview': [True, True],
            'PrintView': [True, True],
            'SaveDiagram': [True, False],
            'PrintDiagram': [True, False],
            'PrintText': [False, True],
        }
        diagramEditCommands = [ # Always enable for diagram, disable for anything else
            'CanvasAction',
            'ZoomDialog',
            'ZoomAll',
            'ZoomSelected'
        ]
        undoEnable = False
        redoEnable = False
        state = self._alterationStack.state() # empty, end, beginning, between
        if state == 'between' or state == 'end': undoEnable = True
        if state == 'between' or state == 'beginning': redoEnable = True
        page = self.currentPage()
        diagramEnabled = False
        textViewEnabled = False
        if isinstance(page, canv.Canvas):
            diagramEnabled = True
        elif isinstance(page, Stc):
            textViewEnabled = True
        for commandId in self._frame.commands().commandDefnByCommandId:
            commandDefn = self._frame.commands().commandDefnByCommandId[commandId]
            enableIt = True
            if commandDefn:
                if commandDefn.procedure == 'Undo':
                    enableIt = undoEnable
                elif commandDefn.procedure == 'Redo':
                    enableIt = redoEnable
                elif commandDefn.procedure == 'LaunchESLSEC':
                    enableIt = self._simulationControl.gotESLSEC()
                elif commandDefn.procedure == 'LaunchESLDisplays':
                    enableIt = self._simulationControl.gotESLDisplays()
                elif commandDefn.procedure in printCommands:
                    enableOptions = printCommands[commandDefn.procedure]
                    enableIt = (diagramEnabled and enableOptions[0]) or (textViewEnabled and enableOptions[1])
                elif commandDefn.procedure in diagramEditCommands:
                    enableIt = diagramEnabled
            if enableIt:
                browse = None
                if commandDefn.commandXmlElement:
                    browse = commandDefn.commandXmlElement.getAttribute("browse")
                enableIt = self._mode == "editing" or browse == "true"
            if enableIt is not None:
                self._frame.viewManager().menubar().enableItem(commandId, enableIt)
                self._frame.viewManager().toolbar().enableItem(commandId, enableIt)
        self._frame.viewManager().menubar().enableDisableSubMenus()

    def propertyChanged(self, descr): # the propertiesview invokes this when user changes a property
        pass

    def appendMessage(self, lines, diagnosticLevel=0):
        if diagnosticLevel == 0 or Config.getBool('Advanced/Diagnostics'):
            msgView = self._frame.viewManager().messagesView()
            msgView.appendText(str(lines))
            self._frame.viewManager().showView("MessagesView")
        if not Utils.isFrozen() and not Utils.isDistributionPackage():
            print(str(lines))

    def clearMessages(self):
        msgView = self._frame.viewManager().messagesView()
        msgView.Clear()
        self._frame.viewManager().showView("MessagesView")

    def setStatusText(self, text):
        statusBar = self._frame.GetStatusBar()
        if statusBar:
            statusBar.SetStatusText(text)

    def setCanvas(self, canvasId):
        if canvasId:
            canvas = self._frame.viewManager().mainView().getPageByCanvasId(canvasId)
        else:
            canvas = self.currentCanvas()
        return canvas

    def addCanvasChangeAlteration(self, eventType, eventXmlElement, undoDeleteApplicationData, undoUpdateApplicationData, redoInsertApplicationData):
        canvasId = eventXmlElement.getAttribute("id")
        canvas = self.setCanvas(canvasId)
        if canvas:
            application_data = eventXmlElement.getXmlElementByName("application-data")
            alteration_type = ''
            if application_data: alteration_type = application_data.getAttribute("alteration")
            if not alteration_type:
                secondary = False
                if application_data:
                    secondaryStr = application_data.getAttribute("secondary")
                    secondary = secondaryStr == "true"
                self._alterationStack.add(CanvasAlteration(canvas.moduleId(), secondary, eventType, eventXmlElement,
                                                           undoDeleteApplicationData, undoUpdateApplicationData, redoInsertApplicationData))
            #else:
                #alterationStack.alterCanvasAlteration(category, application_data, objects, data)

    def OnCanvasSelectedObjects(self, canvas_event):
        msg = "SELECTED: "
        #if canvas_event.objects: msg += str(canvas_event.objects)
        if canvas_event.data: msg += '\n  data: ' + str(canvas_event.data)
        msg += '\n'
        self.appendMessage(msg, 1)
        eventXmlElement = xut.xmlElement(canvas_event.data)
        if eventXmlElement:
            eventCanvasId = eventXmlElement.getAttribute("id")
            canvas = self.setCanvas(eventCanvasId)
            if canvas and eventCanvasId and eventCanvasId == canvas.canvasId():
                canvasType = ''
                if isinstance(canvas, IseModelView):
                    canvasType = ''
                    module = self._application.getModelForCanvas(canvas)
                    if module:
                        canvasType = 'model'
                else:
                    module = self._application.getSubmodelForCanvas(canvas)
                    if module:
                        canvasType = 'submodel'
                    else:
                        module = self._application.getSegmentForCanvas(canvas)
                        if module:
                            canvasType = 'segment'
                #noprops = True
                clearprops = True
                objectXmlList = []
                objectsXmlElement = eventXmlElement.getXmlElementByName("objects")
                if objectsXmlElement:
                    objectXmlList = objectsXmlElement.getChildren()
                if not objectXmlList:
                    #self.clearPropertyPage('No objects selected')
                    self._propertiesControl.setCanvasPropertyPage(canvas)
                    clearprops = False
                    self._frame.viewManager().applicationView().selectItem(canvasType, module.moduleId())
                elif len(objectXmlList) > 1:
                    self._propertiesControl.clearPropertyPage('Multiple objects selected')
                    clearprops = False
                    self._frame.viewManager().applicationView().selectItem(None)
                else: # one object - is it an entity
                    objectXmlElementName = objectXmlList[0].name()
                    if objectXmlElementName == 'entity':
                        type = objectXmlList[0].getAttribute("type")
                        objectId = objectXmlList[0].getAttribute("id")
                        if type and objectId:
                            clearprops = False
                            alreadySelected = self._frame.viewManager().applicationView().selectItem('entity', module.moduleId(), objectId, suppressPropagation=False) # this will set the entity's property page
                            if alreadySelected:
                                self._propertiesControl.setEntityPropertyPage(type, canvas, objectId) # application view will do this unless had been alreadySelected

                    elif objectXmlElementName == "display":
                        type = objectXmlList[0].getAttribute("type")
                        objectId = objectXmlList[0].getAttribute("id")
                        if type and objectId:
                            self._propertiesControl.setDisplayPropertyPage(type, canvas,
                                                                          objectId)  # application will do this
                            clearprops = False
                            self._frame.viewManager().applicationView().selectItem(None)
                    elif objectXmlElementName == "info":
                        type = objectXmlList[0].getAttribute("type")
                        if type == "Module Annotation" or type == "Program Annotation":
                            self._propertiesControl.setCanvasPropertyPage(canvas)
                            clearprops = False
                            self._frame.viewManager().applicationView().selectItem(canvasType, canvas.moduleId())
                    elif objectXmlElementName == "group":
                        type = objectXmlList[0].getAttribute("type")
                        objectId = objectXmlList[0].getAttribute("id")
                        self._propertiesControl.setGroupPropertyPage(
                            type, canvas, objectId, objectXmlList[0])
                        clearprops = False
                        self._frame.viewManager().applicationView().selectItem(None)
                    elif objectXmlElementName == "annotation":
                        texts = objectXmlList[0].getXmlElementListByName("text")
                        if len(texts) == 1:
                            objectId = texts[0].getAttribute("id")
                            self._propertiesControl.setElementPropertyPage(
                                "annotation-text", canvas, objectId, texts[0])
                            clearprops = False
                    else: # is is a recognised graphic element
                        objectId = objectXmlList[0].getAttribute("id")
                        if objectXmlElementName in PropertiesKnownElements and objectId:
                            self._propertiesControl.setElementPropertyPage(
                                objectXmlElementName, canvas, objectId, objectXmlList[0])
                            clearprops = False
                            self._frame.viewManager().applicationView().selectItem(None)
                        else:
                            self._propertiesControl.clearPropertyPage()
                            clearprops = False
                            self._frame.viewManager().applicationView().selectItem(None)
                if clearprops:
                    self._propertiesControl.clearPropertyPage()
        # no alteration for selection change

    def OnCanvasChangedObjects(self, canvas_event):
        msg = "CHANGED: "
        #if canvas_event.objects: msg += str(canvas_event.objects)
        if canvas_event.data: msg += '\n  data: ' + str(canvas_event.data)
        msg += '\n'
        self.appendMessage(msg, 1)
        eventXmlElement = xut.xmlElement(canvas_event.data)
        if eventXmlElement:

            eventType = eventXmlElement.getAttribute("type")
            eventCanvasId = eventXmlElement.getAttribute("id")
            canvas = self.setCanvas(eventCanvasId)
            if canvas and eventCanvasId and eventCanvasId == canvas.canvasId():
                diagramInfo = self._application.getCanvasDiagramInfo(canvas)

                # Check if valid to delete update insert entities from/in/into application
                valid = True
                # deleted objects
                entitiesToDeleteList = [] # These entities are in the application
                if valid:
                    entitiesToDeleteList = self.getEntitiesToDelete(diagramInfo, eventXmlElement)
                    if entitiesToDeleteList:
                        valid = self._application.checkValidToRemove(diagramInfo, entitiesToDeleteList)

                # updated objects - nothing currently to be validated in application following a canvas update objects
                entitiesToUpdateList = [] # These entities are in the application
                updatedXmlElementList = []
                if valid:
                    entitiesToUpdateList, updatedXmlElementList = self.getEntitiesToUpdateAndUpdates(diagramInfo, eventXmlElement)

                # These newly created entities are NOT (yet) in the application
                if valid:
                    entityElementsToInsertList = self.getEntitityElementsToInsert(diagramInfo, eventXmlElement)
                    if entityElementsToInsertList:
                        valid = self._application.checkValidToInsert(diagramInfo, entityElementsToInsertList)
                    if valid:
                        newLinksInsertedList = self.getNewLinksInserted(diagramInfo, eventXmlElement)
                        if newLinksInsertedList:
                            valid = self._application.checkValidNewLinks(diagramInfo, newLinksInsertedList)

                # If valid can update application according to canvas change
                if valid:
                    # save application entities that are to be deleted or updated for later undo
                    saveUndoDeleteApplicationData = None
                    saveUndoUpdateApplicationData = None
                    saveRedoInsertApplicationData = None
                    if len(entitiesToDeleteList) > 0:
                        saveUndoDeleteApplicationData = self._application.setupUndoChangeApplicationData(diagramInfo, entitiesToDeleteList)
                    if len(entitiesToUpdateList) > 0:
                        saveUndoUpdateApplicationData = self._application.setupUndoChangeApplicationData(diagramInfo, entitiesToUpdateList)
                    # Inserted entities may have application-data for their simulation-entities if inserted via clipboard
                    application_data = eventXmlElement.getXmlElementByName("application-data")
                    if application_data:
                        saveRedoInsertApplicationData = application_data.getXmlElementByName("redo-inserted")
                        if saveRedoInsertApplicationData:
                            saveRedoInsertApplicationData = saveRedoInsertApplicationData.getXmlElementByName("simulation-entities")
                        savePreviousUndoUpdateApplicationData = application_data.getXmlElementByName("undo-updated")
                        if savePreviousUndoUpdateApplicationData:
                            saveUndoUpdateApplicationData = savePreviousUndoUpdateApplicationData.getXmlElementByName("simulation-entities")

                    self.addCanvasChangeAlteration(eventType, eventXmlElement, saveUndoDeleteApplicationData, saveUndoUpdateApplicationData, saveRedoInsertApplicationData)
                else:
                    alteration = CanvasAlteration(canvas.moduleId(), False, eventType, eventXmlElement) # as a convenience use a dummy alteration (not added to stack) & undo to reject
                    alteration.undo(reject=True)
                    msg = 'OnCanvasChangedObjects reject '+str(alteration)+'\n'
                    self.appendMessage(msg, 1)

                if valid:
                    self.doDiagramChange(diagramInfo, eventXmlElement, entitiesToDeleteList, entitiesToUpdateList, updatedXmlElementList)

    def doDiagramChange(self, diagramInfo, eventXmlElement, entitiesToDeleteList, entitiesToUpdateList, updatedXmlElementList):
        argumentChanged = False
        application_data_type = ""
        alteration_type = ''
        application_data = eventXmlElement.getXmlElementByName("application-data")
        if application_data:
            application_data_type = application_data.getAttribute("type")
            alteration_type = application_data.getAttribute("alteration")
        # deleted objects
        if entitiesToDeleteList and len(entitiesToDeleteList) > 0:
            for entity in entitiesToDeleteList:
                if not argumentChanged and isinstance(entity, SimulationEntity) and entity.isArgument():
                    argumentChanged = True
                diagramInfo.removeEntity(entity)

        # updated objects - let application update for diagram entity change
        if entitiesToUpdateList and len(entitiesToUpdateList) > 0:
            for i in range(len(entitiesToUpdateList)):
                entity = entitiesToUpdateList[i]
                if entity:
                    entity.updateEntityFromDiagramChange(updatedXmlElementList[i])

        # application updated simulation entities to be restored
        if application_data:
            if alteration_type == 'undo':
                undo_updated = application_data.getXmlElementByName("undo-updated")
                if undo_updated:
                    xmlSimulationEntities = undo_updated.getXmlElementByName("simulation-entities")
                    if xmlSimulationEntities:
                        xmlEntities = xmlSimulationEntities.getXmlElementListByName("entity")
                        for xmlEntity in xmlEntities:
                            objectId = xmlEntity.getAttribute("id")
                            entity = diagramInfo.getEntity(objectId)
                            if entity:
                                entity.updateEntity(xmlEntity)

        # inserted objects
        entitiesToInsertList = self.makeEntitiesToInsert(diagramInfo, eventXmlElement)
        if entitiesToInsertList and len(entitiesToInsertList) > 0:
            for entity in entitiesToInsertList:
                if not argumentChanged and isinstance(entity, SimulationEntity) and entity.isArgument():
                    argumentChanged = True
                diagramInfo.insertEntity(entity)
            # application pasted objects to be updated from diagram entity change
            if application_data:
                if application_data_type == "load" or alteration_type == "redo":
                    redoInserted = application_data.getXmlElementByName("redo-inserted")
                    if redoInserted:
                        redoInsertedSimulationEntities = redoInserted.getXmlElementByName("simulation-entities", True)
                        if redoInsertedSimulationEntities:
                            for entity in entitiesToInsertList:
                                entityXmlElement = redoInsertedSimulationEntities.findXmlElementWithAttribute("entity", "id", entity.objectId())
                                if entityXmlElement:
                                    entity.updateEntity(entityXmlElement)

        # application deleted simulation entities to be restored
        if application_data:
            if alteration_type == 'undo':
                undo_deleted = application_data.getXmlElementByName("undo-deleted")
                if undo_deleted:
                    xmlSimulationEntities = undo_deleted.getXmlElementByName("simulation-entities")
                    if xmlSimulationEntities:
                        xmlEntities = xmlSimulationEntities.getXmlElementListByName("entity")
                        for xmlEntity in xmlEntities:
                            objectId = xmlEntity.getAttribute("id")
                            entity = diagramInfo.getEntity(objectId)
                            if entity:
                                entity.updateEntity(xmlEntity)

        # any extra application processing - as for undo a delete, reverse an update or redo an insert
        if argumentChanged:
            suppress_action = True if alteration_type == "undo" else False
            self._application.onArgumentsChanged(diagramInfo.canvas().moduleId(), suppress_action)

    def getEntitiesToDelete(self, diagramInfo, canvasChangedObjectXmlElement):
        entitiesToDeleteList = []
        deletedXmlElement = canvasChangedObjectXmlElement.getXmlElementByName("deleted")
        if deletedXmlElement:
            objectsXmlElement = deletedXmlElement.getXmlElementByName("objects")
            if objectsXmlElement:
                entityXmlList = objectsXmlElement.getXmlElementListByName("entity", False)
                for entityXmlElement in entityXmlList:
                    objectId = entityXmlElement.getAttribute("id")
                    entity = diagramInfo.getEntity(objectId)
                    if entity:
                        entitiesToDeleteList.append(entity)
                entityXmlList = objectsXmlElement.getXmlElementListByName("display", False)
                for entityXmlElement in entityXmlList:
                    objectId = entityXmlElement.getAttribute("id")
                    entity = diagramInfo.getEntity(objectId)
                    if entity:
                        entitiesToDeleteList.append(entity)
                entityXmlList = objectsXmlElement.getXmlElementListByName("info", False)
                for entityXmlElement in entityXmlList:
                    objectId = entityXmlElement.getAttribute("id")
                    entity = diagramInfo.getEntity(objectId)
                    if entity:
                        entitiesToDeleteList.append(entity)
        return entitiesToDeleteList

    def getEntitityElementsToInsert(self, diagramInfo, canvasChangedObjectXmlElement):
        entityElementsToInsertList = []
        insertedXmlElement = canvasChangedObjectXmlElement.getXmlElementByName("inserted")
        if insertedXmlElement:
            objectsXmlElement = insertedXmlElement.getXmlElementByName("objects")
            if objectsXmlElement:
                entityElementsToInsertList = objectsXmlElement.getXmlElementListByName("entity", False)
                entityElementsToInsertList.extend(objectsXmlElement.getXmlElementListByName("display", False))
                entityElementsToInsertList.extend(objectsXmlElement.getXmlElementListByName("info", False))
        return entityElementsToInsertList

    def getNewLinksInserted(self, diagramInfo, canvasChangedObjectXmlElement):
        newLinksElementList = None
        insertedXmlElement = canvasChangedObjectXmlElement.getXmlElementByName("inserted")
        if insertedXmlElement:
            objectsXmlElement = insertedXmlElement.getXmlElementByName("objects")
            if objectsXmlElement:
                newLinksElementList = objectsXmlElement.getXmlElementListByName("link", False)
        return newLinksElementList

    def makeEntitiesToInsert(self, diagramInfo, canvasChangedObjectXmlElement):
        entitiesToInsertList = []
        insertedXmlElement = canvasChangedObjectXmlElement.getXmlElementByName("inserted")
        if insertedXmlElement:
            objectsXmlElement = insertedXmlElement.getXmlElementByName("objects")
            if objectsXmlElement:
                entityXmlList = objectsXmlElement.getXmlElementListByName("entity", False)
                for entityXmlElement in entityXmlList:
                    type = entityXmlElement.getAttribute("type")
                    objectId = entityXmlElement.getAttribute("id")
                    if type and objectId:
                        entity = self._application.makeSimulationEntity(diagramInfo, type, objectId)
                        if entity:
                            entitiesToInsertList.append(entity)
                entityXmlList = objectsXmlElement.getXmlElementListByName("display", False)
                for entityXmlElement in entityXmlList:
                    type = entityXmlElement.getAttribute("type")
                    objectId = entityXmlElement.getAttribute("id")
                    if type and objectId:
                        entity = DisplayDefinition(diagramInfo, type, objectId)
                        if entity:
                            entitiesToInsertList.append(entity)
                entityXmlList = objectsXmlElement.getXmlElementListByName("info", False)
                for entityXmlElement in entityXmlList:
                    type = entityXmlElement.getAttribute("type")
                    objectId = entityXmlElement.getAttribute("id")
                    if type and objectId:
                        entity = InfoBlock(diagramInfo, type, objectId)
                        if entity:
                            entitiesToInsertList.append(entity)
        return entitiesToInsertList

    def getEntitiesToUpdateAndUpdates(self, diagramInfo, canvasChangedObjectXmlElement):
        entitiesToUpdateList = []
        updatedXmlElementList = []
        updatedXmlElement = canvasChangedObjectXmlElement.getXmlElementByName("updated")
        if updatedXmlElement:
            objectsXmlElement = updatedXmlElement.getXmlElementByName("objects")
            if objectsXmlElement:
                entityXmlList = objectsXmlElement.getXmlElementListByName("entity", False)
                for entityXmlElement in entityXmlList:
                    objectId = entityXmlElement.getAttribute("id")
                    entity = diagramInfo.getEntity(objectId)
                    if entity:
                        entitiesToUpdateList.append(entity)
                        updatedXmlElementList.append(entityXmlElement)
                entityXmlList = objectsXmlElement.getXmlElementListByName("display", False)
                for entityXmlElement in entityXmlList:
                    objectId = entityXmlElement.getAttribute("id")
                    entity = diagramInfo.getEntity(objectId)
                    if entity:
                        entitiesToUpdateList.append(entity)
                        updatedXmlElementList.append(entityXmlElement)
        return entitiesToUpdateList, updatedXmlElementList

    def OnCanvasApplicationRequest(self, canvas_event):
        msg = "APPLICATION REQUEST: "
        #if canvas_event.objects: msg += str(canvas_event.objects)
        if canvas_event.data: msg += '\n  data: ' + str(canvas_event.data)
        msg += '\n'
        self.appendMessage(msg, 1)
        eventXmlElement = xut.xmlElement(canvas_event.data)
        if eventXmlElement:
            infoElement = eventXmlElement.getXmlElementByName("info")
            if infoElement:
                command = infoElement.getAttribute("command")
                if command:
                    if command == "Clip Paste Objects":
                        self._clipboard.PasteObjects()
                    elif command == "File Drop":
                        filenames = infoElement.getAttribute("filenames")
                        filenames = filenames.split('|')
                        self._frame.commands().dropFiles(filenames)
                    else:
                        objectsElement = eventXmlElement.getXmlElementByName("objects")
                        if objectsElement:
                            if command == "Clip Save Objects":
                                self._clipboard.ClipObjects(objectsElement.xml())
                            else:
                                moduleId = 0
                                focusWnd = wx.Window.FindFocus()
                                if isinstance(focusWnd, ModuleView):
                                    moduleId = focusWnd.moduleId()
                                self._frame.commands().executeCommand(command, objectsElement.xml())
                                if command == "Undo" or command == "Redo":
                                    if moduleId:
                                        page = self._frame.viewManager().mainView().getModuleViewByModuleId(moduleId)
                                        if page:
                                            page.SetFocus()

    def OnCanvasApplicationNotify(self, canvas_event):
        msg = ''
        eventXmlElement = xut.xmlElement(canvas_event.data)
        if eventXmlElement:
            infoElement = eventXmlElement.getXmlElementByName("info")
            if infoElement:
                notify = infoElement.getAttribute("notify")
                if notify and notify == "display":
                    msg = infoElement.getContent()
        if not msg:
            msg = "APPLICATION NOTIFY: "
            #if canvas_event.objects: msg += str(canvas_event.objects)
            if canvas_event.data: msg += '\n  data: ' + str(canvas_event.data)
        msg += '\n'
        self.appendMessage(msg, 0)

    def OnViewPaneChange(self, auimanager_event):
        change = '?'
        viewname = auimanager_event.GetPane().name
        evttype = auimanager_event.GetEventType()
        if evttype == aui.EVT_AUI_PANE_CLOSE.typeId: change = 'close'
        #if evttype == aui.EVT_AUI_PANE_MAXIMIZE.typeId: change = 'maximize'
        #if evttype == aui.EVT_AUI_PANE_MINIMIZE.typeId: change = 'minimize'
        #if evttype == aui.EVT_AUI_PANE_RESTORE.typeId: change = 'restore'
        #if evttype == aui.EVT_AUI_PANE_MIN_RESTORE.typeId: change = 'min-restore'
        paneinfo = auimanager_event.GetPane()
        panes = []
        if aui.UseAUI() == aui.AUI_AGW:
            panes = self._frame.auiManager().getBasePanes(paneinfo)
        elif aui.UseAUI() == aui.AUI_WX:
            panes.append(paneinfo)
        for pane in panes:
            showing = False
            self._frame.viewManager().showPaneView(pane, showing)
            commandDefn = self.getToggleViewCommandDefn(pane.name)
            if commandDefn:
                self._frame.viewManager().menubar().checkItem(commandDefn.commandId, showing)
                self._frame.viewManager().toolbar().toggleItem(commandDefn.commandId, showing)

    def setCanvasApplicationViewItem(self, canvas):
        canvasType = ''
        if isinstance(canvas, IseModelView):
            module = self._application.getModelForCanvas(canvas)
            if module:
                canvasType = 'model'
            else:
                canvasType = 'program'
        else:
            module = self._application.getSubmodelForCanvas(canvas)
            if module:
                canvasType = 'submodel'
            else:
                module = self._application.getSegmentForCanvas(canvas)
                if module:
                    canvasType = 'segment'
        selection = canvas.GetSelection()
        if len(selection) == 0:
            if canvasType == 'program':
                self._frame.viewManager().applicationView().selectItem(canvasType, self._application.program().moduleId())
            else:
                self._frame.viewManager().applicationView().selectItem(canvasType, module.moduleId())
        elif len(selection) > 1:
            self._frame.viewManager().applicationView().selectItem(None)
        elif selection[0].category() == "entity":
            self._frame.viewManager().applicationView().selectItem(
                'entity', module.moduleId(), selection[0].objectId())
        else:
            # no other types of application view object
            self._frame.viewManager().applicationView().selectItem(None)

    def setCanvasProperties(self, canvas):
        selection = canvas.GetSelection()
        if len(selection) == 0:
            self._propertiesControl.setCanvasPropertyPage(canvas)
        elif len(selection) > 1:
            self._propertiesControl.clearPropertyPage('Multiple objects selected')
        elif selection[0].category() == "entity":
            self._propertiesControl.setEntityPropertyPage(
                selection[0].type(), canvas, selection[0].objectId())
        elif selection[0].category() == "display":
            self._propertiesControl.setDisplayPropertyPage(
                selection[0].type(), canvas, selection[0].objectId())
        elif selection[0].category() == "element":
            self._propertiesControl.setElementPropertyPage(
                selection[0].type(), canvas, selection[0].objectId(), selection[0])
        elif selection[0].category() == "info":
            self._propertiesControl.setCanvasPropertyPage(canvas)
        elif selection[0].category() == "group":
            self._propertiesControl.setGroupPropertyPage(
                selection[0].type(), canvas, selection[0].objectId(), selection[0])
        else:
            # no other types of canvas object
            self._propertiesControl.clearPropertyPage()

    def OnMainViewPageChanged(self, auinotebook_event):
        self.setStatusText("")
        pageindex = auinotebook_event.GetSelection()
        page = self._frame.viewManager().mainView().GetPage(pageindex)
        #msg = "OnMainViewPageChanged - page: " + str(pageindex) + " class: " + page.__class__.__name__ + '\n'
        #self.appendMessage(msg, 2)
        page.setMode(self._mode)
        if isinstance(page, canv.Canvas):
            self.setCanvasProperties(page)
            self.setCanvasApplicationViewItem(page)
        elif isinstance(page, CodeView):
            self._frame.viewManager().applicationView().selectItem('code', page.moduleId())
            self._propertiesControl.setCodePropertyPage(page.moduleId())
        elif isinstance(page, PackageView):
            self._frame.viewManager().applicationView().selectItem('package', page.moduleId())
            self._propertiesControl.clearPropertyPage()
        elif isinstance(page, SimulationParametersView):
            page.showModuleInApplicationView()
            page.showModuleProperties()
        else:
            self._propertiesControl.clearPropertyPage()
            self._frame.viewManager().applicationView().selectItem(None)
        self.enableDisableMenuItems()

    def OnElementsViewItemActivated(self, tree_event):
        elementsView = self._frame.viewManager().elementsView()
        elementsView.onItemActivated(tree_event)
        if elementsView.mode() != "browsing":
            elementXmlElement = elementsView.getElementXml(tree_event)
            if elementXmlElement:
                descr = elementXmlElement.getChildren()[0]
                if descr:
                    page = self.currentCanvas()
                    if page:
                        if not isinstance(descr, str):
                            descr = descr.xml()
                        actionStr = '<action name="Insert">'
                        actionStr += '<info stagger="true"/>'
                        actionStr += '<objects>'
                        actionStr += descr
                        actionStr += '</objects></action>'
                        page.Action(actionStr)

    def OnElementsViewBeginDragItem(self, tree_event):
        elementsView = self._frame.viewManager().elementsView()
        if elementsView.mode() != "browsing":
            elementXmlElement = elementsView.getElementXml(tree_event)
            if elementXmlElement:
                contents = elementXmlElement.getChildren()
                descr = None
                if contents:
                    descr = contents[0]
                if descr:
                    dataobj = wx.TextDataObject(descr.xml())
                    dropSource = wx.DropSource(elementsView)
                    icon = None
                    imageName = elementXmlElement.getAttribute("image")
                    if imageName:
                        iconfile = Utils.elementIconFile(imageName)
                        if not iconfile:
                            image = wx.ArtProvider.GetBitmap(wx.ART_ERROR, size=wx.Size(32,32)).ConvertToImage()
                        else:
                            image = wx.Image(iconfile)
                        if not image.HasAlpha():
                            image.InitAlpha()
                        for ix in range(image.GetWidth()):
                            for iy in range(image.GetHeight()):
                                if image.IsTransparent(ix, iy):
                                    image.SetRGB(ix, iy, 200, 200, 200)
                        image.ClearAlpha()
                        image.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 16)
                        image.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 16)
                        if sys.platform == 'win32':
                            icon = wx.Cursor(image)
                            dropSource.SetCursor(wx.DragCopy, icon)
                        else:
                            bitmap = wx.Bitmap(image)
                            icon = wx.Icon(bitmap)
                            dropSource.SetIcon(wx.DragCopy, icon) # this (icon) doesnt work
                    dropSource.SetData(dataobj)
                    result = dropSource.DoDragDrop()
                    result = result

    def OnApplicationViewItemActivated(self, tree_event):
        applicationView = self._frame.viewManager().applicationView()
        applicationItem = applicationView.getApplicationItem(tree_event)
        if applicationItem:
            msg = ("OnApplicationViewItemActivated - applicationItem: " +
                    str(applicationItem.index) + ' ' + str(applicationItem.type) +
                    ' ' + str(applicationItem.moduleId) + ' ' +
                    str(applicationItem.componentId) + '\n')
        else:
            msg = "OnApplicationViewItemActivated - no applicationItem: " + '\n'
        self.appendMessage(msg, 2)

    def OnApplicationViewItemSelChange(self, tree_event):
        applicationView = self._frame.viewManager().applicationView()
        if applicationView.propagateSelChange():
            applicationItem = applicationView.getApplicationItem(tree_event)
            if applicationItem:
                if applicationItem.moduleId:
                    objectIdList = []
                    if applicationItem.type == 'entity':
                        objectIdList = [applicationItem.componentId]
                    module = self._application.getModuleById(applicationItem.moduleId)
                    moduleType = module.moduleType()
                    if moduleType == 'program' and module.model():
                        module = module.model()
                    if moduleType == 'program' or moduleType == 'model' or moduleType == 'submodel' or moduleType == 'segment':
                        if module.diagramInfo():
                            canvas = module.diagramInfo().canvas()
                            self.selectObjects(canvas, objectIdList, raiseSelectionEvent = False)
                            pageIndex = self._frame.viewManager().mainView().getPageIndex(canvas)
                            if pageIndex != self._frame.viewManager().mainView().GetSelection():
                                self._frame.viewManager().mainView().SetSelection(pageIndex) # will gen page change event
                            else:
                                self.setCanvasProperties(canvas)
                    elif moduleType == 'code':
                        page = self._frame.viewManager().mainView().getCodeViewByModuleId(applicationItem.moduleId)
                        pageIndex = self._frame.viewManager().mainView().getPageIndex(page)
                        if pageIndex != self._frame.viewManager().mainView().GetSelection():
                            self._frame.viewManager().mainView().SetSelection(pageIndex)
                        self._propertiesControl.setCodePropertyPage(applicationItem.moduleId)
                        if applicationItem.type == "code-subprogram":
                            eslname = applicationItem.componentId
                            if eslname:
                                module.findSubprogram(eslname)
                    elif moduleType == 'package':
                        page = self._frame.viewManager().mainView().getPackageViewByModuleId(applicationItem.moduleId)
                        pageIndex = self._frame.viewManager().mainView().getPageIndex(page)
                        if pageIndex != self._frame.viewManager().mainView().GetSelection():
                            self._frame.viewManager().mainView().SetSelection(pageIndex)
                        #else:
                        self._propertiesControl.clearPropertyPage()
        applicationView.set_propagateSelChange(True)

    def OnCharHook(self, evt):
        keyCode = evt.GetKeyCode()
        modifiers = evt.GetModifiers()
        handled = False
        if modifiers == wx.MOD_ALT and keyCode == wx.WXK_F12:
            self._frame.commands().RunCommand()
            handled = True
        if not handled:
            handled = self._frame.viewManager().mainView().onCharHook(evt)
        evt.Skip(not handled)

    def selectObjects(self, canvas, objectIdList, raiseSelectionEvent):
        actionStr = '<action name="Select"'
        if not raiseSelectionEvent:
            actionStr += ' raise-event="false"'
        actionStr += '><objects>'
        for objId in objectIdList:
            actionStr += '<object id="'+str(objId)+'"/>'
        actionStr += '</objects></action>'
        canvas.Action(actionStr)

    def setMode(self, mode):
        self._mode = mode
        self._frame.viewManager().setMode(mode)
        self._frame.applicationHistory().setMode(mode)
        self.enableDisableMenuItems()
