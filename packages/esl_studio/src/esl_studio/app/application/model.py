#! /usr/bin/python

import esl_diagram.xmlutil as xut

from .. import utils as Utils
from ..config import Config
from .modelbase import ModelBase
from .subprogram import Subprogram
from .diagraminfo import DiagramInfo
from .simulationparameters import SimulationParameters

class Model(ModelBase, Subprogram):
    def __init__(self, application, moduleId):
        ModelBase.__init__(self, application, moduleId, 'model')
        Subprogram.__init__(self, 'diagram')
        self._eslname = self._application.blockNames().getUnusedName("Mod")
        self._modelType = "model"               # "model" "embedded-segment" "remote-segment"
        self._diagramInfo = DiagramInfo(self)
        self._simulationParameters = SimulationParameters(self)

    def modelType(self):
        return self._modelType
    def simulationParameters(self):
        return self._simulationParameters

    def set_modelType(self, modelType):
        self._modelType = modelType

    def identification(self, showSubType=False):
        result = ""
        if self._modelType == 'model':
            result += "Model"
        else:
            result += "Segment"
        if showSubType:
            if self._modelType == 'embedded-segment':
                result += " (embedded)"
            elif self._modelType == 'remote-segment':
                result += " (remote)"
        if self._eslname:
            result += " " + self._eslname
        return result

    def load(self, modelXmlElement):
        if modelXmlElement:
            val = modelXmlElement.getAttribute("eslname")
            if val is not None:
                self._eslname = val
                self._blockNames.add(val, self)
            val = modelXmlElement.getAttribute("type")
            if val is not None:
                if self._application.compatibility() == 1:
                    if val == "embedded":
                        val = "embedded-segment"
                    if val == "remote":
                        val = "remote-segment"
                self._modelType = val
            val = modelXmlElement.getAttribute("description")
            if val is not None: self._description = val
            tabname = self._application.moduleViewTabname(self)
            canvas = None
            addDetached = not Config.getBool('Application/Open Subprograms')
            if len(self._application.models()) == 0: # first model
                canvas = self._application.frame().viewManager().mainView().programPage()
                if not self._application.program().model():
                    self._application.program().set_model(self)
            else:
                canvas = self._application.frame().viewManager().mainView().addModelPage(tabname, addDetached=addDetached)
            canvas.set_moduleId(self._moduleId)
            canvas.set_caption(tabname)
            self._diagramInfo.set_canvas(canvas)
            self._diagramInfo.load(modelXmlElement)
            val = modelXmlElement.getAttribute("show-eslname")
            if val is not None: self._show_eslname = val
            val = modelXmlElement.getAttribute("show-description")
            if val is not None: self._show_description = val
            self._simulationParameters.load(modelXmlElement)
            if self._application.compatibility() == 1:
                exptXmlElement = modelXmlElement.getXmlElementByName("experiment")
                if exptXmlElement:
                    self._application.program().set_experiment(exptXmlElement.getContent())

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        if not self._diagramInfo._canvas:
            self._diagramInfo._canvas = self._application.frame().viewManager().mainView().programPage()
        result = ind + '<model eslname="' + self._eslname + '" type="' + str(self._modelType) + '"'
        if self._description:
            result += ' description="' + xut.entitise(self._description) + '"'
        elif saveDefaults:
            result += ' description=""'
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
        result += ind + '</model>' + nl
        return result
