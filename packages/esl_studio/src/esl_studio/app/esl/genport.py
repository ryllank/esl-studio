#! /usr/bin/python

from .generate import nl, eslDatatype
from .lexer import inclusionStartString, inclusionEndString
from ..application.port import Port

class GenPort(object):
    def __init__(self, parent, portId, diagType, diagDirection, diagSign):
        self._parent = parent
        self._portId = portId
        self._appSimEntity = self._parent.appSimEntity()
        self._appPort = None
        self._appPort = self._appSimEntity.ports().get(str(self._portId))
        if not self._appPort:
            pass
        self._diagType = diagType
        self._diagDirection = diagDirection
        self._diagSign = diagSign
        self._tag = ''
        self._eslname = '' # the variable to use in ESL
        self._natural_in_eslname = ''
        self._sign = ''

    def generate(self):
        return self._appSimEntity.generate()

    def portId(self):
        return self._portId

    def appPort(self):
        return self._appPort

    def tag(self):
        if not self._tag:
            self._tag = self._appPort.tag()
            if not self._tag:
                if self._appPort.direction() == 'input': self._tag = 'I'+str(self._portId)
                if self._appPort.direction() == 'output': self._tag = 'O'+str(self._portId)
                else: self._tag = 'IO'+str(self._portId)
        return self._tag

    def eslname(self):
        if not self._eslname:
            self._eslname = self._appPort.eslname()
            if not self._eslname:
                tag = self.tag()
                self._eslname = self._parent.makeEslName(tag)
        return self._eslname
    def set_eslname(self, eslname):
        self._eslname = eslname
    def set_natural_in_eslname(self, eslname):
        self._natural_in_eslname = eslname
    def natural_in_eslname(self):
        return self._natural_in_eslname

    def direction(self):
        result = None
        if self._appPort:
            result = self._appPort.direction()
        else:
            result = self._diagDirection
        return result

    def datatype(self):
        result = None
        if self._appPort:
            result = self._appPort.datatype()
        return result

    def dimensions(self):
        result = None
        if self._appPort:
            result = self._appPort.dimensions()
        return result

    def kind(self):
        result = None
        if self._appPort:
            result = self._appPort.kind()
        return result

    def sign(self):
        if not self._sign:
            self._sign = self._diagSign
            #if not self._sign:
            #    self._sign = self._appPort.sign()
        return self._sign

    def generateArgDeclaration(self, tag):
        result = ""
        if self._appPort:
            result = eslDatatype(self._appPort.datatype())
            result += ': '
            if not tag:
                tag = self.tag()
            result += tag
        #self._eslname = tag
        return result

    def generateESLDeclaration(self):
        result = ''
        if self._appPort:
            kind = self._appPort.kind()
            if self._appPort.datatype() != 'String' and (
                (kind == 'ESL-value' and self._appPort.direction() == 'output') or
                kind == 'natural'
            ):
                result += '-- Output '
                result += self.tag()
                description = self._appPort.description()
                if description:
                    result += ' (' + description + ')'
                result += ' for ' + self._appSimEntity.identification() + nl
                if kind == 'ESL-value':
                    result += eslDatatype(self._appPort.datatype())
                elif kind == 'natural':
                    result += 'REAL'
                result += ': '
                result += self.eslname()
                portResolveDimensionsData = self._appPort.resolvePortDimensions(
                    entityPortsConnectionsDict=self._parent.genDiagramInfo().appEntityPortsConnectionsDict(),
                    portResolveDimensionsDict=self._parent.genDiagramInfo().appPortResolveDimensionsDict())
                dimensions = portResolveDimensionsData.resolvedDimensions
                rejectMsg = portResolveDimensionsData.resolvedRejectMsg
                if rejectMsg or Port.isGenericDimensions(dimensions):
                    if not rejectMsg:
                        rejectMsg = "no resolved connections"
                    dimensions = " " + self.dimensions() + " " + inclusionStartString + "is generic - not resolved: " + rejectMsg + inclusionEndString
                if portResolveDimensionsData.resolvedDimensions:
                    result += "(" + dimensions  + ")"
        return result
