#! /usr/bin/python

import wx

import esl_diagram.xmlutil as xut

from .general import APPLICATION_VERSION_STRING

from .application import diagramactions as dgAction
from .application.eslvalue import ESLValue

class Clipboard(object):
    def __init__(self, control):
        self._control = control

    def setup(self):
        self._frame = self._control.frame()

    def ClipObjects(self, objectsXmlStr):
        xmlstr = '<esl-studio-clipboard version="' + APPLICATION_VERSION_STRING + '">\n'
        xmlstr += objectsXmlStr
        #xmlstr += '<!-- entities with non default attributes -->\n'
        simEntities = ""
        page = self._control.currentCanvas()
        if page:
            diagramInfo = self._frame.application().getCanvasDiagramInfo(page)
            if diagramInfo:
                objectsXmlElement = xut.xmlElement(objectsXmlStr)
                if objectsXmlElement:
                    if objectsXmlElement.name() != "objects":
                        objectsXmlElement = objectsXmlElement.getXmlElementByName("objects", True)
                    if objectsXmlElement:
                        objectXmlList = objectsXmlElement.getChildren()
                        for objectXmlElement in objectXmlList:
                            if objectXmlElement.name() == "entity":
                                objectId = objectXmlElement.getAttribute("id")
                                simEntity = diagramInfo.getEntity(objectId)
                                if simEntity:
                                    simEntities += simEntity.save(None, 0, False)
        if simEntities:
            xmlstr += '\n<simulation-entities>'
            xmlstr += simEntities
            xmlstr += '</simulation-entities>'
        xmlstr += '\n</esl-studio-clipboard>\n'
        dataObj = wx.TextDataObject(xmlstr)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(dataObj)
            wx.TheClipboard.Close()

    def PasteObjects(self):
        msg = ""
        page = self._control.currentCanvas()
        if page:
            dataObj = wx.TextDataObject()
            if wx.TheClipboard.Open():
                ok = wx.TheClipboard.GetData(dataObj)
                wx.TheClipboard.Close()
                if ok: # is ok in Windows
                    n = dataObj.GetFormatCount()
                    text = dataObj.GetText()
                    if text.startswith('<esl-studio-clipboard'):
                        diagramInfo = self._frame.application().getCanvasDiagramInfo(page)
                        if diagramInfo:
                            newObjectIds = []
                            clipXmlElement = xut.xmlElement(text)
                            if clipXmlElement:
                                errors = self.validateEntities(clipXmlElement, diagramInfo)
                            else:
                                errors = [ "invalid data on clipboard\n" ]
                            if len(errors) == 0:
                                try:
                                    newObjectIds = diagramInfo.load(clipXmlElement, raiseEvent=True, selectObjects=True, pasting=True)
                                except Exception as e:
                                    errors.append("Cannot paste \"" + text + "\"\nException: " + str(e))
                            if len(errors) == 0:
                                updateActionStr = ""
                                for objectId in newObjectIds:
                                    entity = diagramInfo.getEntity(objectId)
                                    if entity:
                                        updateActionStr += dgAction.makeUpdateEntitySetupAnnotationsActionStr(entity)
                                if updateActionStr:
                                    dgAction.sendDiagramUpdate(diagramInfo, updateActionStr, applicationDataType="annotation",
                                                               applicationDataContents="",
                                                               secondary=False, raiseEvent=False)
                            if len(errors) != 0:
                                if len(errors) == 1:
                                    msg = "Paste: "+errors[0]
                                else:
                                    msg = "Paste: errors:\n"
                                    for error in errors:
                                        msg += "- "+error
                    else:
                        msg = "Paste: failed to get ESL-Studio data from clipboard\n"
            else:
                msg = "Paste: failed to open clipboard\n"
        if msg:
            self._control.appendMessage(msg)

    def validateEntities(self, clipXmlElement, diagramInfo):
        errors = []
        entitiesElement = clipXmlElement.getXmlElementByName("simulation-entities", False)
        if entitiesElement:
            entityXmlList = entitiesElement.getXmlElementListByName("entity", False)
            for entityXmlElement in entityXmlList:
                errorMsg = ""
                subprogram = None
                type = entityXmlElement.getAttribute('type')
                entityDefnXmlElement = self._control.entities().getEntityDefnXmlElement(type)
                if not entityDefnXmlElement:
                    errorMsg = "Simulation entity \""+type+"\" not defined (library or profile file may be missing)\n"
                    errors.append(errorMsg)
                else:
                    specialType = entityDefnXmlElement.getAttribute("special-type")
                    if specialType == "Submodel Call" or specialType == "Segment Call" or specialType == "Function Call":
                        subprogramTxt = "submodel"
                        if specialType == "Segment Call":
                            subprogramTxt = "segment"
                        subprogramName = entityXmlElement.getAttribute(subprogramTxt)
                        if subprogramName:
                            if specialType == "Submodel Call":
                                subprogram = self._frame.application().getSubmodelByName(subprogramName)
                            elif specialType == "Segment Call":
                                subprogram = self._frame.application().getSegmentByName(subprogramName)
                            elif specialType == "Function Call":
                                subprogram = self._frame.application().getFunctionByName(subprogramName)
                            #### TODO Consider extending this text to cover preloaded subprograms - see diagramInfo.checkValidToInsert (or use some of it)
                            if not subprogram:
                                errorMsg = subprogramTxt.title() + " \"" + subprogramName + "\" not declared in the application\n"
                                errors.append(errorMsg)
                            else: # Check if ports match the ports in the diagram
                                errorMsg = self.checkValidPorts(clipXmlElement, diagramInfo, entityXmlElement, subprogram)
                                if errorMsg:
                                    errors.append(errorMsg)
                    elif specialType == "Input Argument" or specialType == "Output Argument":
                        # See if the arg name need changing
                        argNameAttributeElement = entityXmlElement.findXmlElementWithAttribute("attribute", "tag", "ARG")
                        if argNameAttributeElement:
                            argNameValue = argNameAttributeElement.getAttribute("value")
                            argNameESLValue = ESLValue(None)
                            argNameESLValue.loadStr(argNameValue)
                            argName = argNameESLValue.valueStr()
                            if argName:
                                module = diagramInfo.parent()
                                newName = module.blockNames().getUnusedName(argName)
                                if newName != argName:
                                    argNameESLValue.loadStr(newName)
                                    argNameAttributeElement.setAttribute("value", argNameESLValue.saveStr())
                if len(errors) == 0:
                    self.validateEntityVariables(clipXmlElement, diagramInfo, entityXmlElement, subprogram)
        return errors

    def validateEntityVariables(self, clipXmlElement, diagramInfo, entityXmlElement, subprogram):
        # See if any attribute or port eslnames need changing
        module = diagramInfo.parent()
        entityAttributes = entityXmlElement.getXmlElementListByName("attribute")
        for entityAttribute in entityAttributes:
            eslname = entityAttribute.getAttribute("eslname")
            if eslname:
                newName = module.blockNames().getUnusedName(eslname)
                if newName != eslname:
                    entityAttribute.setAttribute("eslname", newName)
        entityPorts = entityXmlElement.getXmlElementListByName("port")
        for entityPort in entityPorts:
            eslname = entityPort.getAttribute("eslname")
            if eslname:
                newName = module.blockNames().getUnusedName(eslname)
                if newName != eslname:
                    entityPort.setAttribute("eslname", newName)
        pass

    def checkValidPorts(self, clipXmlElement, diagramInfo, entityXmlElement, subprogram):
        errorMsg = ""
        portsXml = None
        portXmlList = []
        ports = subprogram.getPorts()
        subprogramTxt = subprogram.callableType().title()
        id = entityXmlElement.getAttribute('id')
        objectsElement = clipXmlElement.getXmlElementByName("objects", False)
        if objectsElement:
            objectElement = objectsElement.findXmlElementWithAttribute("entity", "id", id)
            if objectElement:
                portsXml = objectElement.getXmlElementByName("ports")
                if portsXml:
                    portXmlList = portsXml.getXmlElementListByName("port")
        if len(portXmlList) != len(ports):
            errorMsg = subprogramTxt + " call has different number of ports ("+str(len(portXmlList))+") from submodel ("+str(len(ports))+")\n"
        elif len(portXmlList) > 0:
            for port in ports.values():
                portId = port.id()
                portXml = portsXml.findXmlElementWithAttribute("port", "id", portId)
                if not portXml:
                    errorMsg = subprogramTxt + " call does not have port id "+portId+"\n"
                    break
                else:
                    portType = port.datatype()
                    portDirection = port.direction()
                    if port.dimensions():
                        portType += "("+port.dimensions()+")"
                    callPortType = portXml.getAttribute("type")
                    callPortDirection = portXml.getAttribute("direction")
                    if portType != callPortType or portDirection != callPortDirection:
                        errorMsg = subprogramTxt + " call port id "+portId+" type/direction ("+callPortType+"/"+callPortDirection+") does not match submodel's ("+portType+"/"+portDirection+")\n"
                        break
        return errorMsg
