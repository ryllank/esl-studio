#! /usr/bin/python

from collections import OrderedDict

class Registry(object):

    def __init__(self, diagram):
        self._diagram = diagram
        self.clearRegistry()

    def setObjectDefinitions(self, canvasDefinitions):
        definitionsElements = canvasDefinitions.getXmlElementListByName("definitions", True)
        if definitionsElements:
            for definitionsElement in definitionsElements:
                self.loadFromXml(definitionsElement)

    def clearRegistry(self):
        self._registry = OrderedDict()

    def get(self, category, type):
        result = None
        catdict = self._registry.get(category)
        if catdict: result = catdict.get(type)
        return result

    def getCategoryValues(self, category):
        result = []
        catdict = self._registry.get(category)
        if catdict:
            result = list(catdict.values())
        return result

    def has_entry(self, category, type):
        result = False
        catdict = self._registry.get(category)
        if catdict: result = type in catdict
        return result

    def loadFromXml(self, xmlElement):
        defnElements = xmlElement.getXmlElementListByName("def")
        designElements = xmlElement.getXmlElementListByName("design")
        if defnElements or designElements:
            for defnElement in defnElements + designElements:
                self.setDefnElement(defnElement)

    def setDefnElement(self, defnElement):
        category = defnElement.getAttribute("category")
        if category:
            type = defnElement.getAttribute("type")
            if type:
                if category not in self._registry:
                    self._registry[category] = OrderedDict()
                if defnElement.hasChildren() or defnElement.getNrAttributes() > 2:
                    self._registry[category][type] = defnElement
                else:
                    if type in self._registry[category]:
                        del self._registry[category][type]

    def __str__(self):
        result = ''
        for category in self._registry:
            catdict = self._registry[category]
            for type in catdict:
                defn = catdict[type]
                s = str(defn)
                result += "category: " + category + " type: " + type + " := \n" + s
