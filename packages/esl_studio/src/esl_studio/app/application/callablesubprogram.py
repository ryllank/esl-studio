#! /usr/bin/python

from collections import OrderedDict

from .. import utils as Utils
from .applicationtypes import CALLABLECODESUBPROGRAMTYPES
from .subprogram import Subprogram

class CallableSubprogram(Subprogram): # mixin class super for mixins for Submodel and Segment and CodeSubprogram

    def __init__(self, subprogramBaseType):
        Subprogram.__init__(self, subprogramBaseType)
        self._subprogramCalls = []

    def subprogramCalls(self):
        return self._subprogramCalls

    def getPorts(self, allowBlankTag=False):                 # override this in sub-class CallableDiagramSubprogram or CallableCodeSubprogram
        ports = OrderedDict()
        return ports

    def getAttributes(self):            # override this in sub-class CallableDiagramSubprogram or CallableCodeSubprogram
        atts = OrderedDict()
        return atts

    def argumentsTemplate(self):        # override this in sub-class CallableDiagramSubprogram or CallableCodeSubprogram
        result = ""
        return result

    def hasSubprogramCalls(self):
        result = len(self._subprogramCalls) > 0
        return result

    def checkNameIsInCalledModule(self, eslname):
        result = False
        calledDiagramInfos = []
        for call in self._subprogramCalls:
            Utils.extendNew(calledDiagramInfos, call.parent())
        for diagramInfo in calledDiagramInfos:
            result = diagramInfo.parent().blockNames().isin(eslname)
            if result:
                break
        return result

    def callableType(self): # 'submodel' or 'segment' or 'function'
        callableType = None
        if self._subprogramBaseType == 'code':
            callableType = self.subprogramType()
            if callableType == CALLABLECODESUBPROGRAMTYPES[2]:      # 'external-segment'
                callableType = CALLABLECODESUBPROGRAMTYPES[1]       # 'segment'
            elif callableType == CALLABLECODESUBPROGRAMTYPES[4]:    # 'external-function'
                callableType = CALLABLECODESUBPROGRAMTYPES[3]       # 'function'
        else: # 'diagram'
            callableType = self.moduleType()
        return callableType
