#! /usr/bin/python

import esl_diagram.xmlutil as xut

from .. import utils as Utils
from .modelbase import ModelBase
from .diagraminfo import DiagramInfo

class Program(ModelBase):       # so can support annotation (not a Subprogram)

    def __init__(self, application):
        ModelBase.__init__(self, application, 0, 'program')
        self._programType = "study"  # "study" "embedded-program" "remote-program"
        self._diagramInfo = DiagramInfo(self)
        self._diagramInfo.set_canvas(application.frame().viewManager().mainView().programPage())
        self._name = ""
        self._show_type = "false"
        self._show_name = "false"
        self._model = None
        self._experiment = ""
        self._programAnnotation = None

    def eslname(self): return "" # Not used - but may be given a name (as well as description (from ModelBase))

    def programType(self):
        return self._programType
    def set_programType(self, programType):
        self._programType = programType
    def name(self):
        return self._name
    def set_name(self, name):
        self._name = name
    def show_type(self): return self._show_type
    def set_show_type(self, value): self._show_type = value
    def show_name(self): return self._show_name
    def set_show_name(self, value): self._show_name = value
    def model(self):
        return self._model
    def set_model(self, model):
        self._model = model
    def experiment(self):
        return self._experiment
    def set_experiment(self, experiment):
        self._experiment = experiment

    def identification(self, showSubType=False):
        result = "Program"
        if showSubType:
            if self._programType == 'study':
                result += " (study)"
            elif self._programType == 'embedded-program':
                result += " (embedded)"
            elif self._programType == 'remote-program':
                result += " (remote)"
        if self._name:
            result += " " + self._name
        return result

    def load(self, programXmlElement):
        val = programXmlElement.getAttribute("name")
        if val is not None:
            self._name = val
        val = programXmlElement.getAttribute("type")
        if val is not None:
            self._programType = val
        val = programXmlElement.getAttribute("description")
        if val is not None:
            self._description = val
        val = programXmlElement.getAttribute("show-type")
        if val is not None:
            self._show_type = val
        val = programXmlElement.getAttribute("show-name")
        if val is not None:
            self._show_name = val
        val = programXmlElement.getAttribute("show-description")
        if val is not None:
            self._show_description = val
        exptXmlElement = programXmlElement.getXmlElementByName("experiment")
        if exptXmlElement:
            self._experiment = exptXmlElement.getContent()

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ind + '<program type="' + str(self._programType) + '"'
        if self._name:
            result += ' name="' + xut.entitise(self._name) + '"'
        elif saveDefaults:
            result += ' name=""'
        if self._description:
            result += ' description="' + xut.entitise(self._description) + '"'
        elif saveDefaults:
            result += ' description=""'
        if self._show_type and self._show_type == "true":
            result += ' show-type="true"'
        elif saveDefaults:
            result += ' show-type="false"'
        if self._show_name and self._show_name == "true":
            result += ' show-name="true"'
        elif saveDefaults:
            result += ' show-name="false"'
        if self._show_description and self._show_description == "true":
            result += ' show-description="true"'
        elif saveDefaults:
            result += ' show-description="false"'
        if self._experiment or saveDefaults:
            result += '>' + nl
            result += ind2 + '<experiment>' + nl
            if self._experiment:
                result += ind2 + '<![CDATA[' + str(self._experiment) + ']]>' + nl
            result += ind2 + '</experiment>' + nl
            result += ind + '</program>' + nl
        else:
            result += "/>" + nl
        return result
