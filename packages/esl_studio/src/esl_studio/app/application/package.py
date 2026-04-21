#! /usr/bin/python

from esl_diagram.canvas.diagram import sortedValues
import esl_diagram.xmlutil as xut

from .. import utils as Utils
from ..config import Config
from .module import Module
from .subprogram import Subprogram
from .variable import Variable
from ..esl.esl import EslNameMaxChars

class Package(Module, Subprogram):
    def __init__(self, application, moduleId):
        Module.__init__(self, application, moduleId, 'package')
        Subprogram.__init__(self, 'diagram') # Sets ESL-Studio package .subprogramBaseType as "diagram" to easily distinguish from package in Code.
        self._usingModules = [] # model or submodels that import/use this package

    def usingModules(self):
        return self._usingModules

    def eslnameIsInUse(self, eslname):
        result = self._blockNames.isin(eslname)
        if not result:
            for module in self._usingModules:
                if module.eslnameIsInModule(eslname):
                    result = True
                    break
        return result

    def getUnusedName(self, stem):
        name = stem
        count = 0
        while True:
            if not self.eslnameIsInUse(name):
                break
            else:
                count += 1
                name = stem + "_" + str(count)
                if len(name) > EslNameMaxChars:
                    name = ''
                    raise Exception('Cannot get an unused name based on "' + stem + '"')
                    # break
        return name

    def load(self, packageXmlElement):
        val = packageXmlElement.getAttribute("eslname")
        if val:
            self._eslname = val
            self._blockNames.add(val, self)
        val = packageXmlElement.getAttribute("description")
        if val: self._description = val
        variableXmlList = packageXmlElement.getXmlElementListByName("variable", False)
        for variableXmlElement in variableXmlList:
            var = Variable(self)
            var.load(variableXmlElement)
            self.addVariable(var)
        tabname = self._application.moduleViewTabname(self)
        addDetached = not Config.getBool('Application/Open Packages')
        packageview = self._application.frame().viewManager().mainView().addPackagePage(tabname, addDetached)
        if packageview:
            packageview.loadPackage(self)

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ind + '<package eslname="' + self._eslname + '"'
        if self._description:
            result += ' description="' + xut.entitise(self._description) + '"'
        elif saveDefaults:
            result += ' description=""'
        result += '>' + nl
        for variable in sortedValues(self._variables):
            result += variable.save(indent, level + 1, saveDefaults)
        result += ind + '</package>' + nl
        return result
