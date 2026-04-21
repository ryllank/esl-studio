#! /usr/bin/python

import esl_diagram.xmlutil as xut

from .. import utils as Utils
from ..config import Config
from .modelbase import ModelBase
from .callablediagramsubprogram import CallableDiagramSubprogram
from .diagraminfo import DiagramInfo

class Submodel(ModelBase, CallableDiagramSubprogram):
    def __init__(self, application, moduleId):
        ModelBase.__init__(self, application, moduleId, 'submodel')
        CallableDiagramSubprogram.__init__(self)
        self._diagramInfo = None

    def load(self, submodelXmlElement, preload=False):
        val = submodelXmlElement.getAttribute("eslname")
        if val:
            self._eslname = val
            self._blockNames.add(val, self)
        val = submodelXmlElement.getAttribute("description")
        if val: self._description = val
        addDetached = not Config.getBool('Application/Open Subprograms')
        tabname = self._application.moduleViewTabname(self)
        canvas = self._application.frame().viewManager().mainView().addSubprogramPage(tabname, addDetached)
        canvas.set_moduleId(self._moduleId)
        self._diagramInfo = DiagramInfo(self)
        self._diagramInfo.set_canvas(canvas)
        self._diagramInfo.load(submodelXmlElement)
        val = submodelXmlElement.getAttribute("show-eslname")
        if val is not None: self._show_eslname = val
        val = submodelXmlElement.getAttribute("show-description")
        if val is not None: self._show_description = val

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ind + '<submodel eslname="' + self._eslname + '"'
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
        result += self._diagramInfo.save(indent, level + 1, saveDefaults)
        result += ind + '</submodel>' + nl
        return result
