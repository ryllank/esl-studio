#! /usr/bin/python

import esl_diagram.xmlutil as xut

from .module import Module
from ..esl.esl import EslNameMaxChars

class ModelBase(Module):        # For *diagram* Modules (subprograms) ? + Program
    ProgramAnnotation_pos = (50, 30)
    ProgramAnnotation_programName_pos = (0, 0)
    ProgramAnnotation_programDescription_pos = (0, 30)
    ProgramAnnotation_types = ["STUDY", "EMBEDDED", "REMOTE"]
    ModuleAnnotation_pos = (50, 100)
    ModuleAnnotation_eslname_pos = (0, 0)
    ModuleAnnotation_description_pos = (0, 30)
    def __init__(self, application, moduleId, moduleType):
        Module.__init__(self, application, moduleId, moduleType)
        self._diagramInfo = None
        self._show_eslname = "false"
        self._show_description = "false"
        self._importedPackages = []
        self._moduleAnnotation = None
        self._simulationParameters = None

    def show_eslname(self): return self._show_eslname
    def show_description(self): return self._show_description
    def set_show_eslname(self, value): self._show_eslname = value
    def set_show_description(self, value): self._show_description = value

    def diagramInfo(self):
        return self._diagramInfo
    def simulationParameters(self):
        return self._simulationParameters

    def setupSubprogramCalls(self):
        if self._diagramInfo:
            self._diagramInfo.setupSubprogramCalls()

    def eslnameIsInModule(self, eslname):
        result = self._blockNames.isin(eslname)
        if not result:
            for package in self._importedPackages:
                if package.blockNames().isin(eslname):
                    result = True
                    break
        if not result and self._diagramInfo:
            result = self._diagramInfo.checkNameIsCalledSubprogramName(eslname)
        return result

    def okToImportPackages(self, packageNamesPropertyValue):
        result = ''
        packageNames = packageNamesPropertyValue
        if isinstance(packageNamesPropertyValue, str):
            if not packageNamesPropertyValue:
                packageNames = []
            else:
                packageNames = packageNamesPropertyValue.split(",")
                packageNames = list(map(lambda item: item.strip(), packageNames))
        removingPackages = []
        upperisedPackageNames = list(map(lambda item: item.upper(), packageNames))
        for package in self._importedPackages:
            if package.eslname().upper() not in upperisedPackageNames:
                removingPackages.append(package)
                for var in list(package.variables().values()):
                    for attribute in var.assignedAttributes():
                        parent = attribute.parent()
                        while parent:
                            if parent != self: # not in this module
                                if hasattr(parent, "parent"):
                                    parent = parent.parent()
                                else:
                                    parent = None
                            else:
                                result = 'removing package ' + package.eslname() + ' has variable "' + var.eslname() + '" that is in use in ' + self.identification() +\
                                    " (" + attribute.description() + " in "+attribute.parent().identification()+")"
                                break
        addingPackages = []
        for packageName in packageNames:
            package = self._application.getPackageByName(packageName)
            if package and package not in self._importedPackages:
                addingPackages.append(package)
                for var in list(package.variables().values()):
                    if self.eslnameIsInModule(var.eslname()):
                        # See if the name is in one of the packages to be removed.
                        goingToBeRemoved = False
                        for removing in removingPackages:
                            if removing.blockNames().isin(var.eslname()):
                                goingToBeRemoved = True
                                break
                        if not goingToBeRemoved:
                            result = 'adding package '+package.eslname() + ' has variable "' + var.eslname() + '" that is already in use in ' + self.identification()
                        break
            if result: break
        if not result and len(addingPackages) > 1:
            n = len(addingPackages)
            for iPack in range(n-1):
                for jPack in range(iPack+1,n):
                    for var in list(addingPackages[iPack].variables().values()):
                        if addingPackages[jPack].blockNames().isin(var.eslname()):
                            result = 'adding package ' + addingPackages[iPack].eslname() + ' has variable "' + var.eslname() + '" that is also in package ' + addingPackages[jPack].eslname()
                            break
                    pass # end loop eslnames
                    if result: break
                pass # end loop jPack
                if result: break
            pass # end loop iPack
        return result

    def setupImportedPackages(self):
        if self._diagramInfo is not None:
            importedPackageNames = self._diagramInfo.importedPackageNames()
            if len(importedPackageNames) > 0:
                for packageName in importedPackageNames:
                    package = self._application.blockNames().get(packageName)
                    if package:
                        self._importedPackages.append(package)
                        package.usingModules().append(self._diagramInfo.parent())

    def setupLinkedAttributes(self):
        if self._diagramInfo is not None:
            for entity in list(self._diagramInfo.simulationEntities().values()):
                for attribute in list(entity.attributes().values()):
                    variableOrPort = attribute.getVariableFromSource()
                    attribute.linkAttributeWithVariableOrPort(variableOrPort)

    def setupAnnotationTexts(self):
        if self._diagramInfo is not None:
            program = None
            if self._moduleType == 'program':
                program = self
            else:
                if self._application.program().model() and self == self._application.program().model():
                    program = self._application.program()
            if program and (program._show_type != "false" or program._show_name != "false" or program._show_description != "false"):
                self.checkProgramAnnotations("annotations")
            if self._moduleType != 'program':
                if self._show_eslname != "false" or self._show_description != "false":
                    self.checkModuleAnnotations("annotations")
            self._diagramInfo.setupAnnotationTexts()

    def updateImportedPackages(self, packageNamesPropertyValue):
        packageNames = packageNamesPropertyValue
        if isinstance(packageNamesPropertyValue, str):
            if not packageNamesPropertyValue:
                packageNames = []
            else:
                packageNames = packageNamesPropertyValue.split(",")
                packageNames = list(map(lambda item: item.strip(), packageNames))
        for package in self._importedPackages:
            package.usingModules().remove(self)
        self._importedPackages = []
        for packageName in packageNames:
            package = self._application.getPackageByName(packageName)
            if package:
                self._importedPackages.append(package)
                package.usingModules().append(self)
        self._diagramInfo.set_importedPackageNames(packageNames)

    def renameImportedPackageName(self, oldName, newName):
        packageNames = self._diagramInfo.importedPackageNames()
        ix = packageNames.index(oldName)
        if ix >= 0:
            packageNames[ix] = newName
            self._diagramInfo.set_importedPackageNames(packageNames)

    def getUnusedName(self, stem):
        name = stem
        count = 0
        while True:
            if not self.eslnameIsInModule(name):
                break
            else:
                count += 1
                name = stem + "_" + str(count)
                if len(name) > EslNameMaxChars:
                    name = ""
                    raise Exception("Cannot get an unused name based on \"" + stem + "\"")
                    # break
        return name

    def checkProgramAnnotations(self, propertyTag, suppress_action=False):
        program = None
        if self._moduleType == 'program':
            program = self
        else:
            if self._application.program().model() and self == self._application.program().model():
                program = self._application.program()
        if not program:
            raise Exception("Inserting program annotation into module that is not a program model")
        else:
            if self._diagramInfo is not None:
                if program._programAnnotation is None:
                    if not suppress_action:
                        if propertyTag == "programAnnotations":
                            #if self._show_eslname or self._show_description:
                            self.addProgramAnnotation()
                else:
                    application_data = "<application-data type=\"annotation\" secondary=\"true\"/>"
                    actionStr = "<action name=\"Update\" raise-event=\"false\"><objects>"
                    actionStr += "<info id=\"" + program._programAnnotation.objectId() + "\">"
                    actionStr += self.setProgramAnnotationsXmlStr(program)
                    actionStr += "</info>"
                    actionStr += "</objects>" + application_data + "</action>"
                    self._diagramInfo.canvas().Action(actionStr)
        pass

    def checkModuleAnnotations(self, propertyTag, suppress_action=False):
        if self._diagramInfo is not None:
            if self._moduleAnnotation is None:
                if not suppress_action:
                    if propertyTag == "annotations":
                        #if self._show_eslname or self._show_description:
                        self.addModuleAnnotation()
            else:
                application_data = "<application-data type=\"annotation\" secondary=\"true\"/>"
                actionStr = "<action name=\"Update\" raise-event=\"false\"><objects>"
                actionStr += "<info id=\"" + self._moduleAnnotation.objectId() + "\">"
                actionStr += self.setModuleAnnotationsXmlStr()
                actionStr += "</info>"
                actionStr += "</objects>" + application_data + "</action>"
                self._diagramInfo.canvas().Action(actionStr)
        pass

    def addProgramAnnotation(self):
        annotationType = "Program Annotation"
        application_data = "<application-data secondary=\"true\"/>"
        actionStr = "<action name=\"Insert\"><objects>"
        x = ModelBase.ProgramAnnotation_pos[0]
        y = ModelBase.ProgramAnnotation_pos[1]
        actionStr += "<info type=\""+annotationType+"\" x=\""+str(x)+"\" y=\""+str(y)+"\">"
        actionStr += self.setProgramAnnotationsXmlStr(self._application.program(), setPositions=True)
        actionStr += "</info></objects>" + application_data + "</action>"
        self._diagramInfo.canvas().Action(actionStr)

    def addModuleAnnotation(self):
        annotationType = "Module Annotation"
        application_data = "<application-data secondary=\"true\"/>"
        actionStr = "<action name=\"Insert\"><objects>"
        x = ModelBase.ModuleAnnotation_pos[0]
        y = ModelBase.ModuleAnnotation_pos[1]
        actionStr += "<info type=\""+annotationType+"\" x=\""+str(x)+"\" y=\""+str(y)+"\">"
        actionStr += self.setModuleAnnotationsXmlStr(setPositions=True)
        actionStr += "</info></objects>" + application_data + "</action>"
        self._diagramInfo.canvas().Action(actionStr)

    def programAnnotationInserted(self, entity):
        program = None
        if self._moduleType == 'program':
            program = self
        else:
            if self._application.program().model() and self == self._application.program().model():
                program = self._application.program()
        if not program:
            raise Exception("Inserting program annotation into module that is not a program model")
        else:
            if program._programAnnotation is None:
                program._programAnnotation = entity
                # If had been deleted and undone, need to restore program state from what's in diagram.
                canvas = entity.parent().canvas()
                infoXmlElementStr = canvas.SaveObjectById(entity.objectId())
                if infoXmlElementStr:
                    infoXmlElement = xut.XmlElement(infoXmlElementStr)
                    if infoXmlElement:
                        element = infoXmlElement.findXmlElementWithAttribute("annotation", "id", "programName")
                        if element:
                            value = element.getAttribute("visible")
                            if value:
                                program._show_type = value
                                program._show_name = value
                                if value == "true":
                                    # Currently don't distinguish type from name - so look in sub-element "text" contents for STUDY EMBEDDED or REMOTE.
                                    textElement = element.getXmlElementByName("text")
                                    if textElement:
                                        textContents = textElement.getContent()
                                        if textContents:
                                            if textContents in ModelBase.ProgramAnnotation_types:
                                                program._show_name = "false" # no name set
                                            elif not (textContents.startswith("STUDY ") or textContents.startswith("EMBEDDED ") or  textContents.startswith("REMOTE ")):
                                                program._show_type = "false" # no type set
                        element = infoXmlElement.findXmlElementWithAttribute("annotation", "id", "programDescription")
                        if element:
                            value = element.getAttribute("visible")
                            if value:
                                program._show_description = value
            else:
                raise Exception("Inserting program annotation when one exists")

    def moduleAnnotationInserted(self, entity):
        if self._moduleType == 'program':
            raise Exception("Inserting module annotation into a program")
        else:
            if self._moduleAnnotation is None:
                self._moduleAnnotation = entity
                # If had been deleted and undone, need to restore module state from what's in diagram.
                canvas = entity.parent().canvas()
                infoXmlElementStr = canvas.SaveObjectById(entity.objectId())
                if infoXmlElementStr:
                    infoXmlElement = xut.XmlElement(infoXmlElementStr)
                    if infoXmlElement:
                        element = infoXmlElement.findXmlElementWithAttribute("annotation", "id", "eslname")
                        if element:
                            value = element.getAttribute("visible")
                            if value:
                                self._show_eslname = value
                        element = infoXmlElement.findXmlElementWithAttribute("annotation", "id", "description")
                        if element:
                            value = element.getAttribute("visible")
                            if value:
                                self._show_description = value
            else:
                raise Exception("Inserting module annotation when one exists")

    def setProgramAnnotationsXmlStr(self, program, setPositions=False):
        annotationsXmlStr = ""
        annotationStyle = "background"
        ###annotationStyle = "big-background" - not supported in esl_diagram
        annotationId = 'programName'
        annotationTxt = ""
        if program._show_type == "true":
            annotationTxt = "STUDY"
            if program._programType == 'embedded-program':
                annotationTxt = "EMBEDDED"
            elif program._programType == 'remote-program':
                annotationTxt = "REMOTE"
        if program._show_name == "true":
            if annotationTxt: annotationTxt += " "
            annotationTxt += program._name
        annotationVisible = program._show_name
        if annotationVisible == "false":
            annotationVisible = program._show_type
        annotationsXmlStr += "<annotation id=\"" + annotationId + "\" "+annotationStyle+"=\"true\""
        if setPositions:
            x = ModelBase.ProgramAnnotation_programName_pos[0]
            y = ModelBase.ProgramAnnotation_programName_pos[1]
            annotationsXmlStr += " x=\""+str(x)+"\" y=\""+str(y)+"\""
        annotationsXmlStr += " visible=\"" + annotationVisible + "\">"
        annotationsXmlStr += "<text><![CDATA[" + annotationTxt + "]]></text>"
        annotationsXmlStr += "</annotation>"
        annotationId = 'programDescription'
        annotationTxt = program._description
        annotationVisible = program._show_description
        annotationsXmlStr += "<annotation id=\"" + annotationId + "\" "+annotationStyle+"=\"true\""
        if setPositions:
            x = ModelBase.ProgramAnnotation_programDescription_pos[0]
            y = ModelBase.ProgramAnnotation_programDescription_pos[1]
            annotationsXmlStr += " x=\"" + str(x) + "\" y=\"" + str(y) + "\""
        annotationsXmlStr += " visible=\"" + annotationVisible + "\">"
        annotationsXmlStr += "<text><![CDATA[" + annotationTxt + "]]></text>"
        annotationsXmlStr += "</annotation>"
        return annotationsXmlStr

    def setModuleAnnotationsXmlStr(self, setPositions=False):
        annotationsXmlStr = ""
        annotationStyle = "background"
        annotationId = "eslname"
        annotationTxt = self._eslname
        annotationVisible = self._show_eslname
        annotationsXmlStr += "<annotation id=\"" + annotationId + "\" "+annotationStyle+"=\"true\""
        if setPositions:
            x = ModelBase.ModuleAnnotation_eslname_pos[0]
            y = ModelBase.ModuleAnnotation_eslname_pos[1]
            annotationsXmlStr += " x=\""+str(x)+"\" y=\""+str(y)+"\""
        annotationsXmlStr += " visible=\"" + annotationVisible + "\">"
        annotationsXmlStr += "<text><![CDATA[" + annotationTxt + "]]></text>"
        annotationsXmlStr += "</annotation>"
        annotationId = "description"
        annotationTxt = self._description
        annotationVisible = self._show_description
        annotationsXmlStr += "<annotation id=\"" + annotationId + "\" "+annotationStyle+"=\"true\""
        if setPositions:
            x = ModelBase.ModuleAnnotation_description_pos[0]
            y = ModelBase.ModuleAnnotation_description_pos[1]
            annotationsXmlStr += " x=\"" + str(x) + "\" y=\"" + str(y) + "\""
        annotationsXmlStr += " visible=\"" + annotationVisible + "\">"
        annotationsXmlStr += "<text><![CDATA[" + annotationTxt + "]]></text>"
        annotationsXmlStr += "</annotation>"
        return annotationsXmlStr

    def programAnnotationRemoved(self, entity):
        program = None
        if self._moduleType == 'program':
            program = self
        else:
            if self._application.program().model() and self == self._application.program().model():
                program = self._application.program()
        if not program:
            raise Exception("Removing program annotation from module that is not a program model")
        else:
            if entity == program._programAnnotation:
                program._programAnnotation = None
                program._show_type = "false"
                program._show_name = "false"
                program._show_description = "false"
            else:
                raise Exception("Removing program annotation which isn't")

    def moduleAnnotationRemoved(self, entity):
        if self._moduleType == 'program':
            raise Exception("Removing module annotation from a program")
        else:
            if entity == self._moduleAnnotation:
                self._moduleAnnotation = None
                self._show_eslname = "false"
                self._show_description = "false"
            else:
                raise Exception("Removing module annotation which isn't")
