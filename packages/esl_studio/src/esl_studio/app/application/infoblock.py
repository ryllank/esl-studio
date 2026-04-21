#! /usr/bin/python

from .. import utils as Utils

class InfoBlock(object):
    def __init__(self, parent, type = "", objectId = ""):
        self._parent = parent
        self._type = type
        self._objectId = objectId
        self._entityDefnXmlElement = None
        self._prefix = ""
        if type:
            entities = self._parent._parent._application._frame.control().entities()
            self._entityDefnXmlElement = entities.getEntityDefnXmlElement(self._type)
            if self._entityDefnXmlElement:
                prefix = self._entityDefnXmlElement.getAttribute('prefix')
                if prefix: self._prefix = prefix

    def parent(self): return self._parent
    def type(self): return self._type
    def objectId(self): return self._objectId
    def prefix(self): return self._prefix

    def load(self, displayDescrXmlElement):
        self._type = displayDescrXmlElement.getAttribute("type")
        self._objectId = displayDescrXmlElement.getAttribute("id")

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ind + "<info id=\"" + str(self._objectId) + "\" type=\"" + self._type + "\""
        result += "/>" + nl
        return result
