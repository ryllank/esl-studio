#! /usr/bin/python

import wx.propgrid as wxpg

from ..application.diagraminfo import DiagramInfo
from .propertiesviewsimulationentity import PropertiesViewSimulationEntity
from .properties.coreproperties import FlagsProperty

class PropertiesViewCallEntity(PropertiesViewSimulationEntity):

    def __init__(self, propertiesViewEntityPage):
        PropertiesViewSimulationEntity.__init__(self, propertiesViewEntityPage)

    def setEntityProperties(self, newItem, simulationEntity, ref):
        categoryProp = self._entityPage._entityCategory
        propType = "description"
        value = simulationEntity.description()
        propLabel = PropertiesViewSimulationEntity.EntityPropertyLabels.get(propType)
        helpText = PropertiesViewSimulationEntity.EntityPropertyHelpTexts.get(propType)
        prop = self._entityPage._entityProperties.get(propType)
        if not prop:
            prop = wxpg.StringProperty(propLabel, ref + propType, value=value)
            prop.SetHelpString(helpText)
            #self._entityPage._page.AppendIn(categoryProp, prop) - dont want these in a category
            self._entityPage._page.Insert(categoryProp, prop) # insert prior to the dummy category property
            self._entityPage._entityProperties[propType] = prop
        else:
            prop.SetName(ref + propType)
            prop.SetValue(value)

        propType = "submodel"
        propLabel = PropertiesViewSimulationEntity.EntityPropertyLabels.get(propType)
        helpText = PropertiesViewSimulationEntity.EntityPropertyHelpTexts.get(propType)
        prop = self._entityPage._entityProperties.get(propType)
        if not prop:
            prop = wxpg.EnumProperty(propLabel, ref + propType)
            prop.SetHelpString(helpText)
            annotationsProp = self._entityPage._entityProperties.get("annotations")
            if annotationsProp:
                self._entityPage._page.Insert(annotationsProp, prop) # Insert above previously existing annotations property
            else:
                self._entityPage._page.Insert(categoryProp, prop) # insert prior to the dummy category property
            self._entityPage._entityProperties[propType] = prop

        if simulationEntity.isSubmodelCall():
            subprogramNames = [""]
            sub = ""
            inSubprogram = None
            if isinstance(simulationEntity.parent(), DiagramInfo):
                inSubprogram = simulationEntity.parent().parent()
            subprograms = list(self._entityPage._application.submodels().values())
            subprograms += self._entityPage._application.getCodeSubprograms("submodel")
            for s in subprograms:
                if s != inSubprogram:
                    subName = s.eslname()
                    #if not s.valid():      -- no longer show invalid subprograms
                    #    subName += "*"
                    if s.valid():
                        subprogramNames.append(subName)
            subprogramNames.sort(key=lambda n: n.upper())
            sub = simulationEntity.getSubprogramName()
            value = 0
            for i in range(len(subprogramNames)):
                if sub.upper() == subprogramNames[i].upper():
                    value = i
                    break

            prop.SetName(ref + 'submodel')
            prop.SetChoices(wxpg.PGChoices(subprogramNames, list(range(len(subprogramNames)))))
            prop.SetValue(value)

        prop.Hide(not simulationEntity.isSubmodelCall())

        propType = "segment"
        propLabel = PropertiesViewSimulationEntity.EntityPropertyLabels.get(propType)
        helpText = PropertiesViewSimulationEntity.EntityPropertyHelpTexts.get(propType)
        prop = self._entityPage._entityProperties.get(propType)
        if not prop:
            prop = wxpg.EnumProperty(propLabel, ref + propType)
            prop.SetHelpString(helpText)
            annotationsProp = self._entityPage._entityProperties.get("annotations")
            if annotationsProp:
                self._entityPage._page.Insert(annotationsProp,
                                              prop)  # Insert above previously existing annotations property
            else:
                self._entityPage._page.Insert(categoryProp, prop)  # insert prior to the dummy category property
            self._entityPage._entityProperties[propType] = prop

        if simulationEntity.isSegmentCall():
            subprogramNames = [""]
            sub = ""
            inSubprogram = None
            if isinstance(simulationEntity.parent(), DiagramInfo):
                inSubprogram = simulationEntity.parent().parent()
            subprograms = list(self._entityPage._application.segments().values())
            subprograms += self._entityPage._application.getCodeSubprograms("segment")
            subprograms += self._entityPage._application.getCodeSubprograms("external-segment")
            for s in subprograms:
                if s != inSubprogram:
                    subName = s.eslname()
                    #if not s.valid():      -- no longer show invalid subprograms
                    #    subName += "*"
                    if s.valid():
                        subprogramNames.append(subName)
            subprogramNames.sort(key=lambda n: n.upper())
            sub = simulationEntity.getSubprogramName()
            value = 0
            for i in range(len(subprogramNames)):
                if sub.upper() == subprogramNames[i].upper():
                    value = i
                    break
            prop.SetName(ref + 'segment')
            prop.SetChoices(wxpg.PGChoices(subprogramNames, list(range(len(subprogramNames)))))
            prop.SetValue(value)

        prop.Hide(not simulationEntity.isSegmentCall())

        propType = "function"
        propLabel = PropertiesViewSimulationEntity.EntityPropertyLabels.get(propType)
        helpText = PropertiesViewSimulationEntity.EntityPropertyHelpTexts.get(propType)
        prop = self._entityPage._entityProperties.get(propType)
        if not prop:
            prop = wxpg.EnumProperty(propLabel, ref + propType)
            prop.SetHelpString(helpText)
            annotationsProp = self._entityPage._entityProperties.get("annotations")
            if annotationsProp:
                self._entityPage._page.Insert(annotationsProp,
                                              prop)  # Insert above previously existing annotations property
            else:
                self._entityPage._page.Insert(categoryProp, prop)  # insert prior to the dummy category property
            self._entityPage._entityProperties[propType] = prop

        if simulationEntity.isFunctionCall():
            subprogramNames = [""]
            sub = ""
            inSubprogram = None
            if isinstance(simulationEntity.parent(), DiagramInfo):
                inSubprogram = simulationEntity.parent().parent()
            #subprograms = list(self._entityPage._application.submodels().values())
            subprograms = self._entityPage._application.getCodeSubprograms("function")
            subprograms += self._entityPage._application.getCodeSubprograms("external-function")
            for s in subprograms:
                if s != inSubprogram:
                    subName = s.eslname()
                    #if not s.valid():      -- no longer show invalid subprograms
                    #    subName += "*"
                    if s.valid():
                        subprogramNames.append(subName)
            subprogramNames.sort(key=lambda n: n.upper())
            sub = simulationEntity.getSubprogramName()
            value = 0
            for i in range(len(subprogramNames)):
                if sub.upper() == subprogramNames[i].upper():
                    value = i
                    break
            prop.SetName(ref + 'function')
            prop.SetChoices(wxpg.PGChoices(subprogramNames, list(range(len(subprogramNames)))))
            prop.SetValue(value)

        prop.Hide(not simulationEntity.isFunctionCall())

        propType = "annotations"
        value = None
        propLabel = PropertiesViewSimulationEntity.EntityPropertyLabels.get(propType)
        helpText = PropertiesViewSimulationEntity.EntityPropertyHelpTexts.get(propType)
        annotations = 0
        if simulationEntity.show_description() == "true": annotations += 1
        showAnnotations = [PropertiesViewSimulationEntity.EntityPropertyLabels["description"]]
        annotationHints = [PropertiesViewSimulationEntity.EntityAnnotationHelpTexts["description"]]
        choiceBits = [1]
        if simulationEntity.isSubmodelCall():
            if simulationEntity.show_subprogram() == "true": annotations += 2
            showAnnotations.append(PropertiesViewSimulationEntity.EntityPropertyLabels["submodel"])
            annotationHints.append(PropertiesViewSimulationEntity.EntityAnnotationHelpTexts["submodel"])
            choiceBits = [1, 2]
        elif simulationEntity.isSegmentCall():
            if simulationEntity.show_subprogram() == "true": annotations += 2
            showAnnotations.append(PropertiesViewSimulationEntity.EntityPropertyLabels["segment"])
            annotationHints.append(PropertiesViewSimulationEntity.EntityAnnotationHelpTexts["segment"])
            choiceBits = [1, 2]
        elif simulationEntity.isFunctionCall():
            if simulationEntity.show_subprogram() == "true": annotations += 2
            showAnnotations.append(PropertiesViewSimulationEntity.EntityPropertyLabels["function"])
            annotationHints.append(PropertiesViewSimulationEntity.EntityAnnotationHelpTexts["function"])
            choiceBits = [1, 2]
        prop = self._entityPage._entityProperties.get(propType)
        if not prop:
            prop = FlagsProperty(propLabel, ref + propType, showAnnotations, choiceBits,
                                              annotations)
            prop.SetHelpString(helpText)
            self._entityPage._page.SetPropertyReadOnly(prop, True, wxpg.PG_DONT_RECURSE)
            #self._entityPage._page.AppendIn(categoryProp, prop) - dont want these in a category
            self._entityPage._page.Insert(categoryProp, prop)  # insert prior to the dummy category property
            self._entityPage._entityProperties[propType] = prop
        else:
            prop.setNameChoicesAndValue(ref + propType, showAnnotations, choiceBits, annotations)
            if newItem:
                self._entityPage._page.Collapse(prop)
        prop.SetValue(annotations)
        prop.setHelpStrings(annotationHints)

        #### TODO - what's this for
        for propType in self._entityPage._entityProperties.keys():
            if propType not in PropertiesViewSimulationEntity.EntityPropertyLabels.keys():  ####
                self._entityPage._entityProperties[propType].Hide(True)
