#! /usr/bin/python

import esl_diagram.xmlutil as xut

from .. import utils as Utils
from ..config import Config
from .modelbase import ModelBase
from .callablediagramsubprogram import CallableDiagramSubprogram
from .simulationparameters import SimulationParameters
from .diagraminfo import DiagramInfo

class Segment(ModelBase, CallableDiagramSubprogram):

    def __init__(self, application, moduleId):
        ModelBase.__init__(self, application, moduleId, 'segment')
        CallableDiagramSubprogram.__init__(self)
        self._simulationParameters = SimulationParameters(self)
        self._diagramInfo = None
        self._segmentType = "segment" # "segment" "external-segment"

    def segmentType(self):
        return self._segmentType
    def set_segmentType(self, segmentType):
        self._segmentType = segmentType

    def simulationParameters(self):
        return self._simulationParameters

    def identification(self, showSubType=False):
        result = "Segment"
        if showSubType:
            if self._segmentType == 'external-segment':
                result += " (external)"
            else:
                result += " (emulated)"
        if self._eslname:
            result += " " + self._eslname
        return result

    def load(self, segmentXmlElement, preload=False):
        val = segmentXmlElement.getAttribute("eslname")
        if val:
            self._eslname = val
            self._blockNames.add(val, self)
        val = segmentXmlElement.getAttribute("type")
        if val: self._segmentType = val
        if self._application.compatibility() == 1: # old submodel for segment uses esl-type for segment-type
            val = segmentXmlElement.getAttribute("esl-type")
            if val: self._segmentType = val
        val = segmentXmlElement.getAttribute("description")
        if val: self._description = val
        addDetached = not Config.getBool('Application/Open Subprograms')
        tabname = self._application.moduleViewTabname(self)
        canvas = self._application.frame().viewManager().mainView().addSubprogramPage(tabname, addDetached)
        canvas.set_moduleId(self._moduleId)
        self._diagramInfo = DiagramInfo(self)
        self._diagramInfo.set_canvas(canvas)
        self._diagramInfo.load(segmentXmlElement)
        val = segmentXmlElement.getAttribute("show-eslname")
        if val is not None: self._show_eslname = val
        val = segmentXmlElement.getAttribute("show-description")
        if val is not None: self._show_description = val
        self._simulationParameters.load(segmentXmlElement)

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ind + '<segment eslname="' + self._eslname + '"'
        if self._segmentType != "segment" or saveDefaults:
            result += ' type="' + self._segmentType + '"'
        if self._description or saveDefaults:
            result += ' description="' + xut.entitise(self._description) + '"'
        if self._show_eslname and self._show_eslname == "true":
            result += ' show-eslname="true"'
        elif saveDefaults:
            result += ' show-eslname="false"'
        if self._show_description and self._show_description == "true":
            result += ' show-description="true"'
        elif saveDefaults:
            result += ' show-description="false"'
        result += '>' + nl
        result += self._simulationParameters.save(indent, level + 1, saveDefaults)
        result += self._diagramInfo.save(indent, level + 1, saveDefaults)
        result += ind + '</segment>' + nl
        return result
