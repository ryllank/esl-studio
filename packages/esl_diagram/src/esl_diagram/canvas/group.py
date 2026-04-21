#! /usr/bin/python

from collections import OrderedDict

import wx

from .. import xmlutil as xut

from . import arraylinking
from .object import Composite, CompositeObjectSeparator, Orientation, Scale, Object
from .objectxml import setObjectProperties, getSelectable
from .element import Element, ElementTypes
from .transform import Transform

DefaultGroups = {}

AnnotationIndicator = '@'

class Group(Composite):

    def __init__(self, category, type, diagram, position = None, orientation = None, descr = None):
        Composite.__init__(self, diagram, position, orientation)
        self._category = category
        self._type = type
        self._baseType = "" # for linkables - that may be for arrays
        self._dimensionsInfo = None # for linkables - that may be for arrays
        isAnnotation = self._category == 'group' and self._type == 'annotation'
        isAnonymous = self._category == 'group' and not self._type
        self._defn = self._diagram.registry().get(self._category, self._type)
        if category in arraylinking.LINKABLES:
            self._baseType, self._dimensionsInfo = arraylinking.parseDatatype(type)
            if self._defn is None and self._baseType:
                self._defn = arraylinking.findCompatibleDefn(diagram, category, self._type, self._baseType, self._dimensionsInfo)
        elif (self._defn is None and not (isAnnotation or isAnonymous)):
            msg = 'Cannot create undefined object - category "'+str(self._category)+'" type "'+str(self._type)+'"'
            self._diagram.canvas().raiseCanvasApplicationNotifyEvent('', "display", msg)
        self._descr = descr
        self._draggable = True
        self._orientable = True
        self._scalable = True
        self._contextmenu = None
        if not self._type:
            self._contextmenu = self._diagram.properties().AnonymousGroupContextMenu
        self._activate = None
        self._annotations = OrderedDict()
        if self._defn is not None or isAnnotation or isAnonymous:
            self.setShape()

    def __str__(self):
        result =  "<" + self._category + "-" + str(self.objectId())
        if self._type:
            result += "(" + self._type + ")"
        result += "@" + str(self.position()) + ">"
        return result

    def baseType(self): return self._baseType
    def dimensionsInfo(self): return self._dimensionsInfo

    def setShape(self, xmlElement=None):
        if xmlElement is None:
            defnElement = self._defn
            setObjectProperties(self, defnElement)
            descrElement = None
            if self._descr is not None:
                if isinstance(self._descr, xut.XmlElement):
                    descrElement = self._descr
                else:
                    descrElement = xut.xmlElement(self._descr)
            setObjectProperties(self, descrElement)
            self.addObjects(defnElement)
            if self._descr:
                self.addObjects(self._descr)
        else: # updating
            setObjectProperties(self, xmlElement)

    def addObjects(self, xmlElement):
        added = []
        if xmlElement:
            xmlItemElements = xmlElement.getChildren()
            for xmlItemElement in xmlItemElements:
                existingComponent = None
                componentId = xmlItemElement.getAttribute("id")
                if componentId:
                    componentIdElements = str(componentId).split(CompositeObjectSeparator)
                    if len(componentIdElements) > 1:
                        componentIx = int(componentIdElements[-1])
                        existingComponent = self.componentAtIndex(componentIx)

                addedComponent = self.addComponentObject(xmlItemElement, existingComponent)
                if addedComponent:
                    added.append(addedComponent)
        return added

    def addComponentObject(self, xmlItemElement, existingComponent):
        addedComponent = None
        fix_elements = self._category == "entity" or self._category == "display" or self._category == "info"  # entities have fixed elements
        if existingComponent is not None:
            existingComponent.setShape(xmlItemElement)
            if isinstance(existingComponent, Group):
                existingComponent.addObjects(xmlItemElement)
        else:
            itemname = xmlItemElement.name()
            # draggable = getDraggable(xmlItemElement)
            selectable = getSelectable(xmlItemElement)
            if itemname and itemname in ElementTypes:
                altDefn = None
                if self._type == 'annotation' and itemname == 'text':
                    altDefn = self._diagram.themeProperties().AnnotationTextDescr
                    if self.background():
                        altDefn = self._diagram.themeProperties().BackgroundAnnotationTextDescr
                element = Element(itemname, self._diagram, None, None, xmlItemElement, altDefn)
                if element is not None:
                    # if draggable is None: element.setDraggable(False)
                    if fix_elements:
                        if selectable is None: element.setSelectable(False)
                    self.add(element)
                    addedComponent = element
            elif itemname == "group":
                type = xmlItemElement.getAttribute("type")
                if not type or type != self._type:
                    group = Group("group", type, self._diagram, None, None, xmlItemElement)
                    if group is not None:
                        # if draggable is None: group.setDraggable(False)
                        if fix_elements:
                            if selectable is None: group.setSelectable(False)
                        self.add(group)
                        addedComponent = group
            elif itemname == "annotation":
                annotation = self.setAnnotation(xmlItemElement)
                addedComponent = annotation
        return addedComponent

    def setAnnotation(self, annotationElement, posn=None):
        annotation = None
        annotationId = annotationElement.getAttribute("id")
        if annotationId:
            annotation = self._annotations.get(annotationId)
            if not annotation:
                annotation = Annotation(annotationId, self._diagram, posn, None, annotationElement)
                self._annotations[annotationId] = annotation
                annotation.setParent(self)
                if posn is None:
                    x = annotationElement.getAttribute("x")
                    y = annotationElement.getAttribute("y")
                    if x and y:
                        posn = wx.Point(int(x), int(y))
            else:
                annotation.update(annotationElement, [])
            if posn is not None:
                annotation.setPosition(posn)
        return annotation

    def getAnnotation(self, annotationId):
        annotation = self._annotations.get(annotationId)
        return annotation

    def removeAnnotation(self, annotation):
        annotationId = annotation.annotationId()
        del self._annotations[annotationId]
        annotation.setParent(None)

    def replaceAnnotationId(self, annotation, annotationId):
        oldAnnotationId = annotation.annotationId()
        del self._annotations[oldAnnotationId]
        annotation.set_annotationId(annotationId)
        self._annotations[annotationId] = annotation

    def update(self, updateDescr, deleteList):
        added = []
        if updateDescr is not None:
            if not isinstance(updateDescr, xut.XmlElement):
                updateDescr = xut.xmlElement(updateDescr)
            if updateDescr:
                Group.setShape(self, updateDescr)
                added = self.addObjects(updateDescr)
                self.setAnnotations(updateDescr)
        return added

    def setAnnotations(self, addnlDescr):
        annotationElementList = addnlDescr.getXmlElementListByName("annotation")   #not recurse
        for annotationElement in annotationElementList:
            annotationId = annotationElement.getAttribute('id')
            annotation = self.getAnnotation(annotationId)
            if annotation:
                annotation.update(annotationElement, [])
            else:
                spacing = self._diagram.themeProperties().AnnotationSpacing
                ext = self.extent(True)
                posn = self.position()
                x = 0
                y = ext.y - posn.y + ext.height + spacing
                posn = wx.Point(x, y)
                annotation = self.setAnnotation(annotationElement, posn)

    def savePositioning(self, saveDefaults, defaultGroup=None, includeZOrder=False):
        result = ' x="' + str(self._position.x) + '" y="' + str(self._position.y) + '"'
        if includeZOrder:
            zOrder = self.getZOrder()
            if zOrder > 0:
                result += ' z-order="' + str(zOrder) + '"'
        if saveDefaults or (not defaultGroup and self._orientation != Orientation.normal) or \
                (defaultGroup and self._orientation != defaultGroup.orientation()):
            result += ' orientation="' + str(self._orientation) + '"'
        if saveDefaults or (not defaultGroup and self._scale != Scale()) or \
                (defaultGroup and (self._scale != defaultGroup.getScale())):
            result += ' scale="' + str(self._scale) + '"'
        return result

    def save(self, indent=None, level=0, saveDefaults=False, defaultObject=None, includeZOrder=False):
        result = ''
        nl = '\n'
        ind = ''
        if indent is not None:
            for i in range(level): ind += indent
        else:
            nl = ''
        result = ind + result
        result += '<' + self._category + ' id="' + str(self.objectId()) + '"'
        if self._type:
            result += ' type="' + self._type + '"'

        gotComponents = ""
        defaultGroup = None
        if not saveDefaults:
            if self._defn:
                defaultGroup = DefaultGroups.get(self._defn)
                if not defaultGroup:
                    defaultGroup = Group(self._category, self._type, self._diagram, None, None, None)
                    if defaultGroup:
                        DefaultGroups[self._defn] = defaultGroup

        result += self.savePositioning(saveDefaults, defaultGroup, includeZOrder=includeZOrder)
        copyable = self.copyable()
        if saveDefaults or (not defaultGroup and not copyable) or (defaultGroup and copyable != defaultGroup.copyable()):
            result += ' copy="' + ("true" if copyable else "false") + '"'
        selectable = self.selectable()
        if saveDefaults or (not defaultGroup and not selectable) or (defaultGroup and selectable != defaultGroup.selectable()):
            result += ' select="' + ("true" if selectable else "false") + '"'
        draggable = self.draggable()
        if saveDefaults or (not defaultGroup and not draggable) or (defaultGroup and draggable != defaultGroup.draggable()):
            result += ' drag="' + ("true" if draggable else "false") + '"'
        orientable = self.orientable()
        if saveDefaults or (not defaultGroup and not orientable) or (defaultGroup and orientable != defaultGroup.orientable()):
            result += ' orient="' + ("true" if orientable else "false") + '"'
        scalable = self.scalable()
        if saveDefaults or (not defaultGroup and not scalable) or (defaultGroup and scalable != defaultGroup.scalable()):
            result += ' scalable="' + ("true" if scalable else "false") + '"'

        nComponents = len(self._components)
        for ix in range(nComponents):
            component = self.componentAtIndex(ix)
            defaultComponent = None
            if defaultGroup:
                defaultComponent = defaultGroup.componentAtIndex(ix)
            doGotComponent = True
            gotComponent = component.save(indent, level + 1, saveDefaults, defaultObject=defaultComponent)
            if not saveDefaults and defaultComponent:
                if component.type() in ElementTypes:
                    emptyComponent = ind
                    if indent is not None: emptyComponent += indent
                    emptyComponent += '<' + component.type() + ' id="' + str(component.objectId()) + '"' + '/>' + nl
                    doGotComponent = gotComponent != emptyComponent
                elif component.category() == "group":
                    defaultComponent.setObjectId(component.objectId()) # force the objectId to match
                    defaultComponentSaved = defaultComponent.save(indent, level + 1, saveDefaults)
                    doGotComponent = gotComponent != defaultComponentSaved
            if doGotComponent:
                gotComponents += gotComponent
        # annotations
        hasContents = gotComponents or len(self._annotations) > 0
        if hasContents:
            result += '>' + nl
        else:
            result += '/>' + nl
        result += gotComponents
        for annotation in list(self._annotations.values()):
            result += annotation.save(indent, level + 1, saveDefaults)
        if hasContents:
            result += ind
            result += '</' + self._category + '>' + nl
        return result

    def drawObject(self, dc, transform=None):
        super(Group, self).drawObject(dc, transform)
        belowTransform = self.objectTransform()
        if not transform and self._parent is not None:
            aboveTransform = self.getTransform()
            if aboveTransform:
                belowTransform = aboveTransform.applyTransform(belowTransform, self)
        if transform:
            belowTransform = transform.applyTransform(belowTransform, self)
        for annotation in list(self._annotations.values()):
            if annotation._visible:
                annotation.Draw(dc, belowTransform)
            pass

    def extent(self, includeInvisible=False):
        ext = super(Group, self).extent()
        if self._visible:
            for annotation in list(self._annotations.values()):
                obj_ext = annotation.extent(includeInvisible)
                if obj_ext:
                    ext = ext.Union(obj_ext)
        return ext

    def HitTest(self, pos):
        result = super(Group, self).HitTest(pos)  # check components
        if result is None:
            if self._visible:
                annotations = list(self._annotations.values()).copy()
                annotations.reverse()
                for annotation in annotations:
                    gotHit = annotation.HitTest(pos)
                    if gotHit is not None:
                        result = gotHit
                        break
        return result

class Annotation(Group):

    def __init__(self, annotationId, diagram, position = None, orientation = None, descr = None):
        self._annotationId = annotationId
        self._background = False
        self._offset = wx.RealPoint(0,0)
        self._startDragOffset = None
        backgroundAnnotation = descr.getAttribute("background")
        if backgroundAnnotation and backgroundAnnotation == "true":
            self._background = True
        Group.__init__(self, "group", "annotation", diagram, position, orientation, descr)
        self._orientable = False
        self._scalable = False
        self._copyable = False
        if self._descr is not None:
            if isinstance(self._descr, xut.XmlElement):
                descrElement = self._descr
            else:
                descrElement = xut.xmlElement(self._descr)
            offset = getXmlOffsetPosition(descrElement)
            if offset is not None:
                self._offset = offset

    def annotationId(self):
        return self._annotationId
    def set_annotationId(self, annotationId):
        self._annotationId = annotationId

    def objectId(self):
        result = ""
        result = AnnotationIndicator + str(self._annotationId)
        return result

    def background(self):
        return self._background

    def setShape(self, xmlElement=None):
        super(Annotation, self).setShape(xmlElement)
        if xmlElement:
            offset = getXmlOffsetPosition(xmlElement)
            if offset is not None:
                self._offset = offset

    def getTextElement(self):
        textElement = None
        for component in self._components:
            if component.category() == "element" and component.type() == "text":
                textElement = component
                break # just get the first
        return textElement

    def update(self, updateDescr, deleteList):
        self.setShape(updateDescr)
        backgroundAnnotation = updateDescr.getAttribute("background")
        if backgroundAnnotation:
            if backgroundAnnotation == "true":
                self._background = True
            elif backgroundAnnotation == "false":
                self._background = False
        # Currently annotations always have (just) one text item.
        # To find matching components: compare child XML from updateDescr with component by index (i.e. in turn)
        # seeking to match category/+type for elements - till fail to match.
        # Then add remove subsequent components and add remaining children.
        children = updateDescr.getChildren()
        for childIx in range(len(children)):
            childXml = children[childIx]
            component = self.componentAtIndex(childIx)
            if component:
                matches = False
                itemname = childXml.name()
                if itemname in ElementTypes:
                    if component.category() == "element" and component.type() == itemname:
                        matches = True
                elif component.category() == itemname:
                    matches = True
                if matches:
                    addedComponent = self.addComponentObject(childXml, component)
                else:
                    compIx = childIx
                    while component:
                        self.remove(component)
                        compIx += 1
                        component = self.componentAtIndex(compIx)
                    #while unmatched components removed
                pass
            else:
                addedComponent = self.addComponentObject(childXml, None)

    def save(self, indent=None, level=0, saveDefaults=False, includeZOrder=False):
        result = ''
        nl = '\n'
        ind = ''
        if indent is not None:
            for i in range(level): ind += indent
        else:
            nl = ''
        result = ind + result
        result += '<annotation id="' + str(self._annotationId) + '"'
        result += self.savePositioning(saveDefaults)
        if self._offset != wx.RealPoint(0,0) or saveDefaults:
            result += ' x-offset="' + str(round(self._offset.x)) + '" y-offset="' + str(round(self._offset.y)) + '"'
        if not self._visible or saveDefaults:
            if self._visible:
                result += ' visible="true"'
            else:
                result += ' visible="false"'
        if self._background:
            result += ' background="true"'
        elif saveDefaults:
            result += ' background="false"'
        result += '>' + nl
        for obj in self._components: # last added on top
            result += obj.save(indent, level+1, saveDefaults)
        result += ind + '</annotation>' + nl
        return result

    def extent(self, includeInvisible=False):
        ext = super(Group, self).extent()
        ##print(">Annotation.extent offset="+str(self._offset)+" position="+str(self._position)+" w dragDisplacement="+str(self._dragDisplacement)+" ext="+str(ext))
        # Set according to parent position as transformed
        if ext is not None:
            parentTransform = self._parent.objectTransform()
            transform = self._parent.getTransform(parentTransform)
            position = wx.RealPoint(self._position)
            screenPosition = wx.RealPoint(self.getDiagramPoint(self._position))
            if self._dragDisplacement is not None:
                position -= self._dragDisplacement
            newPosition = transform.backTransformPoint(position, self._parent)
            newPosition -= screenPosition
            offset = newPosition + self._offset
            if self._startDragPosn is not None:
                if self._dragDisplacement is not None:
                    offset += self._dragDisplacement
            ext.Offset(wx.Point(offset))
        ##print("<Annotation.extent final ext="+str(ext))
        return ext

    def drawObject(self, dc, transform=None):
        if not transform and self._parent is not None:
            transform = self.getTransform()
        #print(">Annotation.drawObject position="+str(self._position)+" offset="+str(self._offset)+" transform="+str(transform)+" ownTransform="+str(self.objectTransform()))
        if transform:
            parentTransform = self._parent.objectTransform()
            transform = self._parent.getTransform(parentTransform)
            position = wx.RealPoint(self._position)
            if self._dragDisplacement is not None:
                position -= self._dragDisplacement
            newPosition = transform.backTransformPoint(position, self._parent)
            newPosition -= wx.RealPoint(position)
            newPosition += self._offset
            transform = Transform(newPosition)
        #print("<Annotation.drawObject final transform="+str(transform))
        super(Annotation, self).drawObject(dc, transform)

    def startDragging(self):
        self._startDragOffset = self._offset
        drag = super(Annotation, self).startDragging()
        return drag

    def stopDragging(self):
        #print(">Annotation.stopDragging offset="+str(self._offset)+" w dragDisplacement="+str(self._dragDisplacement)+" position="+str(self._position)
        #      +" startDragPosn="+str(self._startDragPosn)+" startDragOffset="+str(self._startDragOffset))
        if self._startDragPosn is not None:
            self._offset = self._startDragOffset + wx.RealPoint(self._position) - self._startDragPosn
            self._position = wx.Point(self._startDragPosn)
        #print("<Annotation.stopDragging offset="+str(self._offset)+" position="+str(self._position))
        super(Annotation, self).stopDragging()

    def HitTest(self, pos):
        result = Object.HitTest(self, pos) # not Group (which would be the super)
        return result

def getXmlOffsetPosition(xmlElement):
    result = None
    xstr = xmlElement.getAttribute("x-offset")
    ystr = xmlElement.getAttribute("y-offset")
    if xstr and ystr:
        x = int(xstr)
        y = int(ystr)
        result = wx.RealPoint(x, y)
    return result
