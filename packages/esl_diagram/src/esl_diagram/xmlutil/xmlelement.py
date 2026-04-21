#! /usr/bin/python

import os

import xml.dom.minidom as dom

class XmlElement(object):

    def __init__(self, xmlStrOrNode=None):
        self._domNode = None
        self._error = ""
        if xmlStrOrNode:
            if isinstance(xmlStrOrNode, dom.Node):
                self._domNode = xmlStrOrNode
            else:
                self.loadFromString(xmlStrOrNode)

    def isok(self):
        return self._domNode is not None

    def error(self):
        return self._error

    def loadFromString(self, xmlStr):
        self._domNode = None
        if xmlStr is not None and xmlStr:
            try:
                domDoc = dom.parseString(xmlStr)
            except Exception as e:
                domDoc = None
                self._error = "XML Parsing: " + str(e)
            if domDoc:
                self._domNode = domDoc.documentElement
                #domDoc.unlink() # may have to detach to prevent being garbage collected with the doc

    def loadFromFile(self, filepath):
        self._domNode = None
        if os.path.exists(filepath):
            try:
                domDoc = dom.parse(filepath)
            except Exception as e:
                domDoc = None
                self._error = "XML Parsing: " + str(e)
            if domDoc:
                self._domNode = domDoc.documentElement
                #domDoc.unlink() # may have to detach to prevent being garbage collected with the doc
                
    def name(self):
        value = ''
        if self._domNode:
            value = self._domNode.localName
        return value
                
    def getAttribute(self, attributeName): # get the value - as a string
        value = None
        if self._domNode and self._domNode.hasAttribute(attributeName):
            value = self._domNode.getAttribute(attributeName)
        return value

    def setAttribute(self, attributeName, valueStr):
        if self._domNode:
            #self._domNode.removeAttribute(attributeName) - if need will need to try or has first
            self._domNode.setAttribute(attributeName, valueStr)

    def getContent(self): # get the text/CDATA value - as a string
        #print(">getContent _domNode="+str(self._domNode))
        value = ''
        if self._domNode:
            for node in self._domNode.childNodes:
                if node.nodeType in [node.TEXT_NODE, node.CDATA_SECTION_NODE]:
                    if node.nodeType != node.TEXT_NODE or not node.data.isspace():
                        value += node.data
        #print("<getContent value="+str(value))
        return value

    def setContent(self, valueStr):
        # we assume we are always using one CDATA section (not necessarily the first mind).
        gotIt = False
        for node in self._domNode.childNodes:
            if node.nodeType == node.CDATA_SECTION_NODE:
                node.data = valueStr
                gotIt = True
                break
            elif node.nodeType == node.TEXT_NODE:
                if not node.data.isspace():
                    self._domNode.removeChild(node)
        if not gotIt:
            cdata = self._domNode.ownerDocument.createCDATASection(valueStr)
            self._domNode.appendChild(cdata)

    def hasChildren(self):
        result = False
        if self._domNode:
            if self._domNode.firstChild:
                result = True
        return result

    def getChildren(self):
        elementList = []
        if self._domNode:
            for node in self._domNode.childNodes:
                if node.nodeType == node.ELEMENT_NODE:
                    element = XmlElement(node)
                    elementList.append(element)
        return elementList

    def getNrAttributes(self):
        nrAttributes = 0
        if self._domNode:
            nrAttributes = self._domNode.attributes.length
        return nrAttributes

    def getXmlElementByName(self, elementName, recurse=False):
        element = _getXmlElementByName(self._domNode, elementName, recurse)
        return element

    def getXmlElementListByName(self, elementName, recurse=False):
        elementList = _getXmlElementListByName(self._domNode, elementName, recurse)
        return elementList

    def removeNamedChild(self, elementName):
        element = _getXmlElementByName(self._domNode, elementName, False)
        if element:
            oldDomNode = self._domNode.removeChild(element._domNode)
            oldDomNode.unlink()

    def findXmlElementWithAttribute(self, elementName, attributeName, attributeValue=None):
        element = None
        resultNode = _findXmlElementNodeWithAttribute(self._domNode, elementName, attributeName, attributeValue)
        if resultNode:
            element = XmlElement(resultNode)
        return element
    
    def xml(self, indent = None, level = 0):
        result = _xml(self._domNode, indent, level)
        return result

    def appendChild(self, xmlElement):
        copiedElement = xmlElement.copy()
        if self._domNode: self._domNode.appendChild(copiedElement._domNode)

    def prependChild(self, xmlElement):
        copiedElement = xmlElement.copy()
        firstChild = self._domNode.firstChild
        if self._domNode: self._domNode.insertBefore(copiedElement._domNode, firstChild)

    def insertChildAfter(self, xmlElement, afterXmlElement):
        copiedElement = xmlElement.copy()
        nextSibling = afterXmlElement._domNode.nextSibling
        if self._domNode: self._domNode.insertBefore(copiedElement._domNode, nextSibling)

    def removeChild(self, xmlElement):
        for node in self._domNode.childNodes:
            if node == xmlElement._domNode:
                oldDomNode = self._domNode.removeChild(xmlElement._domNode)
                oldDomNode.unlink()
                break

    def copy(self):
        node = self._domNode.cloneNode(True)
        xmlElement = XmlElement(node)
        return xmlElement

    def replaceOrAppendChild(self, childXmlElement, tagAttributeDict):
        #- tagAttributeDict is dict of tagName & attributeName  - e.g. { "entity":"type", "display":"type", "info":"type" } or {"menu":"text"}
        elementName = childXmlElement.name()
        attributeName = tagAttributeDict.get(elementName)
        if attributeName:
            attributeValue = childXmlElement.getAttribute(attributeName)
            matchingChild = self.findXmlElementWithAttribute(elementName, attributeName, attributeValue)
            matchingChildNode = _findXmlElementNodeWithAttribute(self._domNode, elementName, attributeName, attributeValue)
            if matchingChildNode:
                copiedElement = childXmlElement.copy()
                if self._domNode:
                    self._domNode.insertBefore(copiedElement._domNode, matchingChildNode)
                    self._domNode.removeChild(matchingChildNode)
            else:
                # append the unmatched child
                self.appendChild(childXmlElement)
        else:
            # append the new child
            self.appendChild(childXmlElement)

    def __str__(self):
        return '[XmlElement:'+self.xml()+']'

def _getXmlElementByName(domNode, elementName, recurse):
    #print(">_getXmlElementByName elementName="+elementName+" recurse="+str(recurse))
    element = None
    if domNode:
        for node in domNode.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                if node.localName == elementName:
                    element = XmlElement(node)
                    break
                if recurse: # depth-first
                    lowerElement = _getXmlElementByName(node, elementName, recurse)
                    if lowerElement is not None:
                        element = lowerElement
                        break
    #print("<_getXmlElementByName element="+str(element))
    return element

def _getXmlElementListByName(domNode, elementName, recurse):
    #print(">_getXmlElementListByName elementName="+elementName+" recurse="+str(recurse))
    elementList = []
    if domNode:
        for node in domNode.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                if node.localName == elementName:
                    element = XmlElement(node)
                    elementList.append(element)
                if recurse: # depth-first
                    lowerElementList = _getXmlElementListByName(node, elementName, recurse)
                    elementList.extend(lowerElementList)
    #print("<_getXmlElementListByName elementList="+str(elementList))
    return elementList

def _findXmlElementNodeWithAttribute(domNode, elementName, attributeName, attributeValue=None):
    resultNode = None
    if domNode:
        for node in domNode.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                if node.localName == elementName and node.hasAttribute(attributeName):
                    valid = True
                    if attributeValue is not None:
                        valid = node.getAttribute(attributeName) == attributeValue
                    if valid:
                        resultNode = node
                        break
    return resultNode

def _xml(domNode, indent, level):
    result = ""
    nl = '\n'
    ind = ''
    if indent is not None:
        for i in range(level): ind += indent
    else:
        nl = ''
    if domNode:
        node_type = domNode.nodeType
        if node_type in [domNode.TEXT_NODE, domNode.CDATA_SECTION_NODE]:
            s = domNode.data
            if node_type == domNode.CDATA_SECTION_NODE:
                result += ind +'<![CDATA[' + str(s) + ']]>'
            elif not s.isspace(): # ignore whitespace text nodes (truly wanted whitespace will have to be in a CDATA)
                result += ind + str(s)
        elif node_type == domNode.ELEMENT_NODE:
            result += ind + '<'
            name = domNode.localName
            if name: result += str(name)
            for i in range(0, domNode.attributes.length):
                attr = domNode.attributes.item(i)
                result += ' ' + str(attr.localName) + '="' + str(attr.value) + '"'
            if domNode.firstChild is None:
                result += '/>'
            else:
                result += '>'
                if domNode.firstChild == domNode.lastChild and domNode.firstChild.nodeType in [domNode.TEXT_NODE, domNode.CDATA_SECTION_NODE]:
                    result += _xml(domNode.firstChild, '', 0) + '</' + str(name) + '>'
                else:
                    result += nl
                    for node in domNode.childNodes:
                        chldResult = _xml(node, indent, level + 1)
                        if chldResult:
                            result += chldResult + nl
                    result += ind + '</' + str(name) + '>'
    return result

def xmlElement(xmlStr=None):
    result = XmlElement(xmlStr)
    if not result.isok():
        result = None
    return result

def xmlElementFromFile(filepath):
    result = XmlElement()
    error = ""
    result.loadFromFile(filepath)
    if not result.isok():
        error = result.error()
        result = None
    return result, error
