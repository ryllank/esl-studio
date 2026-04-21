#! /usr/bin/python

import wx

from .module import Module
from .simulationentity import SimulationEntity
from .diagraminfo import DiagramInfo
from .port import Port
from .attribute import Attribute
from ..esl.esl import EslBaseTypeNames

def sendDiagramUpdate(diagramInfo, updateActionStr:str, applicationDataType:str="", applicationDataContents="", secondary:bool=False, raiseEvent:bool=False):
    application_data = ""
    if applicationDataType or secondary or applicationDataContents:
        application_data = "<application-data"
        if applicationDataType:
            application_data += " type=\"" + applicationDataType + "\""
        if secondary:
            application_data += " secondary=\"true\""
        if not applicationDataContents:
            application_data += "/>"
        else:
            application_data += ">"
            application_data += applicationDataContents
            application_data += "</application-data>"
    raise_event = ""
    if not raiseEvent:
        raise_event = " raise-event=\"false\""
    action_text = "<action name=\"Update\"" + raise_event + ">"
    action_text += "<objects>"+updateActionStr+"</objects>"
    action_text += application_data + "</action>"
    msg = "DiagramActions.sendDiagramUpdate "+action_text
    wx.GetApp().frame().control().appendMessage(msg, 1)
    diagramInfo._canvas.Action(action_text)

def sendAnnotationUpdate(entity, annotationId, annotationTxt, annotationVisible, secondary=False):
    updateActionStr = '<entity id="'+entity.objectId()+'">'
    updateActionStr += makeUpdateAnnotationActionStr(annotationId, annotationTxt, annotationVisible)
    updateActionStr += '</entity>'
    diagramInfo = entity.parent()
    sendDiagramUpdate(diagramInfo, updateActionStr, applicationDataType="annotation", applicationDataContents="", secondary=secondary, raiseEvent=False)

def makeUpdateAnnotationActionStr(annotationId:str, annotationTxt:str, annotationVisible:str, replaceId:str= "", annotationRemove:bool=False):
    updateActionStr = "<annotation id=\"" + annotationId + "\""
    if annotationRemove:
        updateActionStr += " remove=\"true\"/>"
    else:
        if replaceId:
            updateActionStr += " replace-id=\"" + replaceId + "\""
        if annotationVisible:
            updateActionStr += " visible=\"" + annotationVisible + "\""
        updateActionStr += ">"
        updateActionStr += '<text><![CDATA[' + annotationTxt + ']]></text>'
        updateActionStr += '</annotation>'
    return updateActionStr

def makeUpdateEntitySetupAnnotationsActionStr(entity):
    updateEntityActionStr = ""
    annotationTexts = makeUpdateEntityPropertyAnnotationsActionStr(entity)
    for attribute in list(entity.attributes().values()):
        annotationId, annotationTxt, annotationVisible = setEntityAttributeAnnotations(attribute)
        replaceId = ""
        if entity.isCall() and wx.GetApp().frame().application().compatibility() == 1: # Might be using old-style default tags (A1 A2 etc).
            ix = list(entity.attributes().values()).index(attribute)
            if ix >= 0:
                replaceId = "attribute-A" + str(ix + 1)
        annotationTexts += makeUpdateAnnotationActionStr(annotationId, annotationTxt, annotationVisible, replaceId)
    for port in list(entity.ports().values()):
        annotationId, annotationTxt, annotationVisible = setEntityPortAnnotations(entity, port)
        if annotationTxt and annotationVisible:
            annotationTexts += makeUpdateAnnotationActionStr(annotationId, annotationTxt, annotationVisible)
    if annotationTexts:
        updateEntityActionStr += '<entity id="' + entity.objectId() + '"'
        updateEntityActionStr += ' clear-annotations="true">'
        updateEntityActionStr += annotationTexts
        updateEntityActionStr += '</entity>'
    return updateEntityActionStr

def setEntityPortAnnotations(entity, port):
    annotationId = 'port-'
    if port.direction() == "input":
        annotationId = 'port-input-'
    ix = 0
    for pt in list(entity.ports().values()):
        if pt.direction() == port.direction():
            ix += 1
        if pt.id() == port.id():
            break
    annotationId += str(ix)
    annotationTxt = ''
    description = ""
    initialValueLeadStr = ""
    if port.show_id() == 'true':
        value = str(port.id())
        if value:
            annotationTxt += value
            initialValueLeadStr = ":="
    if port.show_description() == 'true':
        description = port.description()
        if not description: # See if port inherits description from submodel
            if entity.isCall():
                subprogram = entity.subprogram()
                if subprogram:
                    id = port.id()
                    subPorts = subprogram.getPorts()
                    subPort = subPorts.get(id)
                    if subPort:
                        description = subPort.description()
        if description:
            if annotationTxt:
                annotationTxt += ': ' # after id, before description
            annotationTxt += description
            initialValueLeadStr = " :="
    if port.show_tag() == 'true':
        value = port.tag()
        if value:
            if annotationTxt:
                if port.show_description() == 'true' and description:
                    annotationTxt += ' ' # after description
                else:
                    annotationTxt += ':' # after id
            annotationTxt += value
            initialValueLeadStr = ":="
    if port.show_eslname() == 'true':
        value = port.eslname()
        if not value and (port.kind() != "ESL-value" or port.direction() != "input"):
            tag = port.tag()
            if not tag:
                tag = 'O' + str(port.id())
            value = entity.makeEslName(tag)
        if value:
            if annotationTxt:
                if port.show_tag() == 'true':
                    annotationTxt += '/' # after tag
                elif port.show_description() == 'true' and description:
                    annotationTxt += ' ' # after description
                else:
                    annotationTxt += ':' # after id
            annotationTxt += value
            initialValueLeadStr = ":="
    if port.show_initialValue() == 'true':
        valueStr = port.initialValueStr()
        annotationTxt += initialValueLeadStr + valueStr
    annotationVisible = 'true' if annotationTxt else 'false'
    return annotationId, annotationTxt, annotationVisible

def setEntityAttributeAnnotations(attribute):
    annotationId = 'attribute-' + attribute.tag()
    annotationTxt = ''
    withLeadCharAfter = ""
    if attribute.show_description() == 'true':
        value = attribute.description()
        if value:
            annotationTxt += value
            withLeadCharAfter = "Description"
    if attribute.show_tag() == 'true':
        value = attribute.tag()
        if value:
            withLeadCharAfter = "Tag"
            if annotationTxt:
                annotationTxt += ' ' # after Description
        annotationTxt += value
    if attribute.show_eslname() == 'true':
        value = attribute.eslname()
        if not value:
            tag = attribute.tag()
            value = attribute.parent().makeEslName(tag)
        if value:
            withLeadCharAfter = "ESL Name"
            if annotationTxt:
                if attribute.show_tag() == 'true':
                    annotationTxt += '/' # separates Tag from ESL Name
                else:
                    annotationTxt += ' '  # after Description
            annotationTxt += value
    if attribute.show_source() == 'true' or attribute.show_value() == 'true':
        annotationTxt += setEntityAttributeAnnotationsSourceValue(attribute, withLeadCharAfter)
    annotationVisible = 'true' if annotationTxt else 'false'
    return annotationId, annotationTxt, annotationVisible

def setEntityAttributeAnnotationsSourceValue(attribute, withLeadCharAfter=""):
    value = ""
    source = attribute.source()
    datatype = attribute.datatype()
    validity = attribute.eslValue().validity()
    validityIndicator = ""
    if validity == 'invalid':
        validityIndicator = "!"
    elif validity == 'unchecked':
        validityIndicator = "?"
    if datatype.upper() in EslBaseTypeNames:
        if source == Attribute.SourceValue or source == 'RESERVED' or source == 'Output':
            value = attribute.valueStr()
        if not value:
            simulationEntity = attribute.parent()
            if simulationEntity and isinstance(simulationEntity, SimulationEntity) and simulationEntity.isArgument() and attribute.tag() == "ARG":
                value = simulationEntity.getArgName()
        if not value and source == Attribute.SourceValue:
            if attribute.default_value() != "":
                value = "*" + attribute.default_value()
                validityIndicator = ""
        if value: # was one of the above
            if validityIndicator:
                value = validityIndicator + value
            if withLeadCharAfter == "Description":
                value = " " + value # space after Description
            elif withLeadCharAfter != "":
                value = "=" + value
        else: #Parameter or package
            valueLeadChar = ""
            if attribute.show_source() != "true": # just value (no Source)
                if withLeadCharAfter == "Description":
                    valueLeadChar = " "  # space after Description
                elif withLeadCharAfter != "":
                    valueLeadChar = "="  # = after other things

            if attribute.show_source() == "true":
                value = attribute.valueStr()
            if validityIndicator:
                value = validityIndicator + value
            if source == 'Parameter':
                if attribute.show_value() == "true":
                    varValue = "" #variable.valueStr()
                    module = attribute.parent()
                    while module and not isinstance(module, Module):
                        module = module.parent()
                    if module:
                        varValue = get_attribute_value_for_annotation(attribute, module)
                    if value:
                        value = value + "=" + varValue # = after Source
                    else:
                        value = valueLeadChar + varValue
            else: # package
                if attribute.show_source() == "true":
                    value = attribute.source() + "." + value
                if attribute.show_value() == "true":
                    varValue = ""  # variable.valueStr()
                    application = wx.GetApp().frame().application()
                    package = application.getPackageByName(attribute.source())
                    if package:
                        varValue = get_attribute_value_for_annotation(attribute, package)
                    if value:
                        value = value + "=" + varValue # = after Source
                    else:
                        value = valueLeadChar + varValue
            if attribute.show_source() == "true" and withLeadCharAfter != "":
                value = " " + value  # always use space before Source
    else: # 
        value = attribute.valueStr()
        if datatype == "Boolean":
            if value == True or value.lower() == 'true':
                value = "true"
            elif value == False or value == '' or value.lower() == 'false':
                value = "false"
        if value:
            if withLeadCharAfter == "Description":
                value = " " + value # space after Description
            elif withLeadCharAfter != "":
                value = "=" + value
    return value

def makeUpdateEntityPropertyAnnotationsActionStr(entity):
    updateActionStr = ""
    annotationTxt = entity.description()
    annotationVisible = entity.show_description()
    updateActionStr += makeUpdateAnnotationActionStr("description", annotationTxt, annotationVisible)
    if entity.isCall() and entity.show_subprogram():
        annotationTxt = entity.getSubprogramName()
        annotationVisible = entity.show_subprogram()
        updateActionStr += makeUpdateAnnotationActionStr("subprogram", annotationTxt, annotationVisible)
    elif entity.isArgument():
        updateActionStr += entity.makeUpdateEntityPropertyAnnotationsActionStr()
    return updateActionStr

def sendUpdateEntityPropertyAnnotations(entity):
    updateActionStr = '<entity id="'+entity.objectId()+'">'
    updateActionStr += makeUpdateEntityPropertyAnnotationsActionStr(entity)
    updateActionStr += '</entity>'
    diagramInfo = entity.parent()
    sendDiagramUpdate(diagramInfo, updateActionStr, applicationDataType="annotation", applicationDataContents="", secondary=False, raiseEvent=False)

def get_attribute_value_for_annotation(attribute, module):
    value = ""
    varName = attribute.valueStr()
    reference = ""
    if varName.endswith(")"):
        pos = varName.rfind("(")
        reference = varName[pos + 1:-1]
        varName = varName[:pos]
    variable = module.blockNames().get(varName)
    if variable:
        if reference:
            value = variable.get_reference_value(reference)
        else:
            value = variable.valueStr()
    return value

def makeSubprogramPortsActionStr(ports) -> str:
    portsActionStr = ""
    if ports is None or len(ports) == 0:
        portsActionStr = "<ports></ports>"
    else:
        portsActionStr = '<ports>\n'
        for port in list(ports.values()):
            dimensions = ""
            if port.dimensions():
                dimensions = port.dimensions()
            fixDimensions = port.fixDimensions()
            if fixDimensions:
                if fixDimensions == Port.ScalarFixDimensions[0]:
                    dimensions = ""
                else:
                    dimensions = fixDimensions
            if dimensions:
                dimensions = "(" + dimensions + ")"
            if port.direction() == 'input':
                portsActionStr += '<port id="' + port.id() + '" type="' + port.datatype() + dimensions + '"'
                portsActionStr += ' direction="input" tag="' + port.tag() + '"/>\n'
            elif port.direction() == 'output':
                portsActionStr += '<port id="' + port.id() + '" type="' + port.datatype() + dimensions + '"'
                portsActionStr += ' direction="output" tag="' + port.tag() + '"/>\n'
        portsActionStr += '</ports>\n'
    return portsActionStr

def makeSubprogramCallAnnotationsActionStr(entity, annotationsChangeInfo=None) -> str:
    commonPortIdAnnotationPairDict = {}
    obsoletePortIdToAnnotationIdDict = {}
    commonAttributeTagAnnotationPairDict = {}
    obsoleteAttributeTagToAnnotationIdDict = {}
    if annotationsChangeInfo is not None:
        commonPortIdAnnotationPairDict = annotationsChangeInfo[0]
        obsoletePortIdToAnnotationIdDict = annotationsChangeInfo[1]
        commonAttributeTagAnnotationPairDict = annotationsChangeInfo[2]
        obsoleteAttributeTagToAnnotationIdDict = annotationsChangeInfo[3]
    doClearAnnotations = len(commonPortIdAnnotationPairDict) == 0 and len(commonAttributeTagAnnotationPairDict) == 0
    annotationsActionStr = ""
    diagramInfo = entity.parent()
    if diagramInfo and isinstance(diagramInfo, DiagramInfo):
        for port in list(entity.ports().values()):
            annotationId, annotationTxt, annotationVisible = setEntityPortAnnotations(entity, port)
            replaceId = ""
            commonPortAnnotationPair = commonPortIdAnnotationPairDict.get(port.id())
            if commonPortAnnotationPair and commonPortAnnotationPair[0] != commonPortAnnotationPair[1]:
                replaceId = commonPortAnnotationPair[1]
            annotationsActionStr += makeUpdateAnnotationActionStr(annotationId, annotationTxt, annotationVisible, replaceId)
        for attribute in list(entity.attributes().values()):
            annotationId, annotationTxt, annotationVisible = setEntityAttributeAnnotations(attribute)
            replaceId = ""
            commonAttributeAnnotationPair = commonAttributeTagAnnotationPairDict.get(attribute.tag())
            if commonAttributeAnnotationPair and commonAttributeAnnotationPair[0] != commonAttributeAnnotationPair[1]:
                replaceId = commonAttributeAnnotationPair[1]
            annotationsActionStr += makeUpdateAnnotationActionStr(annotationId, annotationTxt, annotationVisible, replaceId)
        if entity.show_description() != "false":
            annotationTxt = entity.description()
            annotationsActionStr += makeUpdateAnnotationActionStr("description", annotationTxt, entity.show_description())
        if entity.isCall() and entity.show_subprogram():
            annotationTxt = entity.getSubprogramName()
            annotationsActionStr += makeUpdateAnnotationActionStr("subprogram", annotationTxt, entity.show_subprogram())
        if not doClearAnnotations:
            for obsoleteAnnotationId in obsoletePortIdToAnnotationIdDict.values():
                annotationsActionStr += makeUpdateAnnotationActionStr(obsoleteAnnotationId, "", "", "", annotationRemove=True)
            for obsoleteAnnotationId in obsoleteAttributeTagToAnnotationIdDict.values():
                annotationsActionStr += makeUpdateAnnotationActionStr(obsoleteAnnotationId, "", "", "", annotationRemove=True)
    return annotationsActionStr

def makeUpdateSubprogramCallActionStr(entity, portsActionStr, annotationsChangeInfo=None) -> str:
    updateActionStr = '<entity id="' + entity.objectId() + '"'
    updateActionStr += ' clear-annotations="true"'
    updateActionStr += '>' + portsActionStr
    updateActionStr += makeSubprogramCallAnnotationsActionStr(entity, annotationsChangeInfo)
    updateActionStr += '</entity>'
    return updateActionStr

def makeUpdateEntityPortActionStr(entity, port, newEntityObjectId="") -> str:
    entityId = entity.objectId()
    if newEntityObjectId:
        entityId = newEntityObjectId
    updateActionStr = "<entity id=\"" + entityId + "\">"
    updateActionStr += "<port id=\""+ str(port.id()) + "\""
    dimensions = ""
    if port.dimensions():
        dimensions = port.dimensions()
    fixDimensions = port.fixDimensions()
    if fixDimensions:
        if fixDimensions == Port.ScalarFixDimensions[0]:
            dimensions = ""
        else:
            dimensions = fixDimensions
    if dimensions:
        dimensions = "(" + dimensions + ")"
    updateActionStr += " type=\""+ port.datatype() + dimensions + "\""
    sign = ""
    if port.sign():
        updateActionStr += " sign=\"" + port.sign() + "\""
    updateActionStr += "/>"
    updateActionStr += '</entity>'
    return updateActionStr
