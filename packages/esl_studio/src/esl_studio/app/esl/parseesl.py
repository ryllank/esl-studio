#! /usr/bin/python

import re
from typing import Pattern

from . import esl

class ParseObject:
    def __init__(self, type:str, parentParseObject):
        self.type:str = type
        self.parent:ParseObject = parentParseObject

class SubprogramParseObject(ParseObject):
    def __init__(self, keyword:str, start:int, name:str):
        ParseObject.__init__(self, "Subprogram", None)
        self.keyword:str = keyword
        self.startPos:int = start               # position of start of subprogram keyword or name
        self.endSignaturePos:int = -1           # position of ; that ends the subprogram signature
        self.endPos:int = -1                    # position of start of END
        self.name:str = name
        self.signatureParseObject:[SignatureParseObject] = None
        self.packageVariables:list[VariableParseObject] = []
        self.messages:list[ParseMessage] = []

    def subprogramType(self):
        subprogramType = self.keyword.lower()
        if self.signatureParseObject:
            if self.signatureParseObject.returnType:
                subprogramType = "function"
            if self.signatureParseObject.isExternal:
                subprogramType = "external-"+subprogramType
        return subprogramType

    def __str__(self):
        messagesIndicator = ""
        if len(self.messages) > 0:
            messagesIndicator = "!"
        result = "<"+messagesIndicator+self.keyword+"@"+str(self.startPos)+".."+str(self.endPos)
        if len(self.messages) > 0:
            result += "{"+str(len(self.messages))+"}"
        result += " " + self.name
        if self.signatureParseObject:
            if self.signatureParseObject.openBracketPos >= 0:
                result += "("
                result += str(self.signatureParseObject)
                result += ")"
            if self.signatureParseObject.isExternal:
                result += " external"
            if self.signatureParseObject.returnType:
                result += " return "+self.signatureParseObject.returnType
        result += ">"
        if self.packageVariables and len(self.packageVariables) > 0:
            for packageVariable in self.packageVariables:
                result += "\n    "+str(packageVariable)
        return result

class SignatureParseObject(ParseObject):
    def __init__(self, subprogramParseObject:SubprogramParseObject):
        ParseObject.__init__(self, "Signature", subprogramParseObject)
        self.argumentParseObjects:list[ArgumentParseObject] = []
        self.openBracketPos:int = -1
        self.isExternal:bool = False
        self.returnType:str = ""

    def __str__(self):
        result = ",".join(map(lambda it: str(it), self.argumentParseObjects))
        return result

class ArgumentParseObject(ParseObject):
    def __init__(self, signatureParseObject:SignatureParseObject, datatype, name, isOutput, isConstant, dimensionality):
        ParseObject.__init__(self, "Argument", signatureParseObject)
        self.datatype = datatype
        self.name = name
        self.isOutput = isOutput
        self.isConstant = isConstant
        self.dimensionality = dimensionality

    def __str__(self):
        result = ""
        if self.isOutput:
            result += ">"
        if self.isConstant:
            result += "CONSTANT "
        result += self.datatype + ":" + self.name
        if self.dimensionality:
            result += "(" + str(self.dimensionality) + ")"
        return result

class DimensionalityParseObject(ParseObject):   # See also DimensionsInfo in esl_diagram/canvas/arraylinking
    UniversalToken = "..."      # Denotes universal dimensionality - generic and of any dimensionality.number - same as in esl_diagram for arraylinking DimensionsInfo
    StarDimension: int = -9999  # An integer that is not likely to be an actual dimension range element - representing use of a * dimension (upper and lower bound)
    ReferenceUnsliced: int = -9998 # An integer that is not likely to be an actual dimension range element - when parsing a reference representing (in the lower bound) that a slice was not specified
    def __init__(self, infoParseObject:ParseObject):
        ParseObject.__init__(self, "Dimensionality", infoParseObject)
        self.messages: list[ParseMessage] = []
        self.usable: bool = True        # if bounds are integers - else non-syntax but semantic
        self.universal: bool = False    # True for generic and of any dimensionality.number (used for function RESULT)
        self._bounds = []

    def copy(self):
        newDimensionalityParseObject = DimensionalityParseObject(self.parent)
        newDimensionalityParseObject.messages = []
        for parseMessage in self.messages:
            newDimensionalityParseObject.messages.append(parseMessage)
        newDimensionalityParseObject.usable = self.usable
        newDimensionalityParseObject.universal = self.universal
        newDimensionalityParseObject._bounds = self._bounds.copy()
        return newDimensionalityParseObject

    def bounds(self):
        return self._bounds

    def add_bounds(self, lowerBound, upperBound):
        self._bounds.append((lowerBound, upperBound))

    def number(self):
        return len(self._bounds)

    def sizes(self):
        sizes = []
        number = len(self._bounds)
        if number > 0 and number <= 3:
            for ix in range(number):
                if self._bounds[ix][1] == DimensionalityParseObject.StarDimension:
                    sizes.append(DimensionalityParseObject.StarDimension)
                elif self._bounds[ix][0] == DimensionalityParseObject.ReferenceUnsliced:
                    sizes.append(1)
                else:
                    sizes.append(self._bounds[ix][1] - self._bounds[ix][0] + 1)
        return sizes

    def size(self):
        sizes = self.sizes()
        size = 1
        for nr in sizes:
            if nr == DimensionalityParseObject.StarDimension:
                size = DimensionalityParseObject.StarDimension
                break
            size = size * nr
        return size

    def str_sizes(self):
        result = "("
        result += ",".join(map(lambda it: str(it), self.sizes()))
        result += ")"
        return result

    def dimensionsList(self): # std form
        result = []
        number = len(self._bounds)
        if number > 0 and number <= 3:
            for ix in range(number):
                if self._bounds[ix][1] == DimensionalityParseObject.StarDimension:
                    result.append("*")
                else:
                    boundStr = ""
                    if self._bounds[ix][0] != 1:
                        boundStr += str(self._bounds[ix][0]) + ".."
                    boundStr += str(self._bounds[ix][1])
                    result.append(boundStr)
        return result

    def dimensions(self): # print std form - no brackets/spaces
        if self.universal:
            result = DimensionalityParseObject.UniversalToken
        else:
            result = ",".join(self.dimensionsList())
        return result

    def __str__(self):
        result = ""
        if len(self.messages) > 0:
            result += "{"+str(len(self.messages))+"}"
        result += self.dimensions()
        return result

    def minimalFormSizes(self) -> list[int]:
        sizes = self.sizes()
        while len(sizes) >= 1 and sizes[0] == 1:
            sizes.pop(0)
        while len(sizes) >= 1 and sizes[-1] == 1:
            sizes.pop(-1)
        return sizes

    def compatibility(self, otherDimensionality) -> str:
        result = 'incompatible'
        if ((len(self.messages) == 0 and len(otherDimensionality.messages) == 0) and
            (self.usable and otherDimensionality.usable)):
            if self.dimensions() == otherDimensionality.dimensions():
                result = 'same'
            else:
                ownNumber = self.number()
                ownSizes = self.sizes()
                otherSizes = otherDimensionality.sizes()
                if (otherDimensionality.number() == ownNumber and
                    (ownNumber <= 0 or otherSizes[0] == ownSizes[0]) and
                    (ownNumber <= 1 or otherSizes[1] == ownSizes[1]) and
                    (ownNumber <= 2 or otherSizes[2] == ownSizes[2])):
                    result = 'compatible'
                else:
                    ownMinFormSizes = self.minimalFormSizes()
                    otherMinFormSizes = otherDimensionality.minimalFormSizes()
                    if ownMinFormSizes == otherMinFormSizes:
                        result = 'minimal-form-compatible'
                    elif (otherDimensionality.number() >= ownNumber and
                          (ownNumber <= 0 or otherSizes[0] >= ownSizes[0]) and
                          (ownNumber <= 1 or otherSizes[1] >= ownSizes[1]) and
                          (ownNumber <= 2 or otherSizes[2] >= ownSizes[2])):
                        result = 'sliceable'
        return result

class VariableParseObject(ParseObject):
    def __init__(self, subprogramParseObject:SubprogramParseObject, datatype, name, isConstant, isParameter, dimensionality, initialValue):
        ParseObject.__init__(self, "Variable", subprogramParseObject)
        self.datatype = datatype
        self.name = name
        self.isConstant = isConstant
        self.isParameter = isParameter
        self.dimensionality = dimensionality
        self.initialValue = initialValue

    def __str__(self):
        result = ""
        if self.isConstant:
            result += "CONSTANT "
        if self.isParameter:
            result += "PARAMETER "
        result += str(self.datatype) + ":" + self.name
        if self.dimensionality:
            result += "(" + str(self.dimensionality) + ")"
        if self.initialValue:
            result += self.initialValue
        return result

class ParseMessage:
    def __init__(self, parser, message:str, pos:int, parseObject):
        self.parser = parser
        self.message = message
        self.pos = pos
        self.parseObject = parseObject
        self.subprogramParseObject = None

    def formatMessage(self, giveLineNumber):
        subprogram = ""
        position = ""
        if self.parseObject:
            if self.subprogramParseObject:
                subprogram += " for " + self.subprogramParseObject.keyword
                if self.subprogramParseObject.name:
                    subprogram += " " + self.subprogramParseObject.name
                else:
                    if giveLineNumber:
                        lineNumber, characterNumber = self.parser._getLinePosition(self.subprogramParseObject.startPos)
                        subprogram += " @" + str(lineNumber) + ":" + str(characterNumber)
                    else:
                        subprogram += " @" + str(self.subprogramParseObject.startPos)
                if self.parseObject.type == "Signature":
                    subprogram += " signature"
                elif self.parseObject.type == "Argument":
                    subprogram += " argument"
                elif self.parseObject.type == "Variable":
                    subprogram += " variable"
            if self.pos >= 0:
                if giveLineNumber:
                    lineNumber, characterNumber = self.parser._getLinePosition(self.pos)
                    position = " at line " + str(lineNumber) + ":" + str(characterNumber)
                else:
                    position = " at " + str(self.pos)
        message = self.message.format(position=position, subprogram=subprogram)
        return message

class ParseEsl:

    regexOptions = re.IGNORECASE | re.DOTALL #| re.MULTILINE

    patternCache = {}

    commentPattern              = r"--([^\n]*)\n"
    libraryPattern              = r"--[ \t]*LIBRARY[ \t]+([^\n]+)\n"
    identifierPatternChars      = r"[A-Z][A-Z0-9_]*"
    identifierPattern           = r"\s*("+identifierPatternChars+")"
    usePackagesPattern          = r"USE\s+("+identifierPatternChars+r")((?:\s*,\s*"+identifierPatternChars+r"\s*)*)?\s*;"
    alternateTypes              = r"(REAL|INTEGER|LOGICAL|CHARACTER)"
    typePattern                 = r"\s*" + alternateTypes + r"(\s*:|\s+[^:])"
    subprogramKeywordPattern    = r"\s*(SUBMODEL|SEGMENT|MODEL|PACKAGE|PROCEDURE)\s"
    openBracketPattern          = r"\s*\("
    closeBracketPattern         = r"\s*\)"
    endingSemicolonPattern      = r"\s*;"
    separatingCommaPattern      = r"\s*,"
    endSigExternalPattern       = r"\s*EXTERNAL\s*;"
    sigReturnPattern            = r"\s*RETURN\s" + alternateTypes
    sigPostReturnPattern        = r"[\s;]"
    filePattern                 = r"\s*(FILE)(\s*:|\s+[^:])"
    dimensionPattern            = r"\s*([-]?\d+\s*\.\.)?\s*([-]?\d+)"  # for submodel and procedure args can use * (it's better in fact) but model and segment must NOT use *
    starPattern                 = r"\s*\*"
    startInputArgsPattern       = r"\s*:="
    optionalConstantPattern     = r"\s*(CONSTANT\s+)?"
    allowConstantHeadPattern    = optionalConstantPattern + typePattern
    subprogramEndPattern        = r"\s*END(\s+" + identifierPatternChars + r")?\s*;"
    variableTypePattern         = r"\s*(CONSTANT|PARAMETER\s+)?" + typePattern
    initialValuePattern         = r"\s*(\/[^/]*\/|\[[^\]]*\])"
    readStatementPattern        = r".*[^A-Z0-9_](READ|READEL|INTERACT)[^A-Z0-9_].*"

    def __init__(self):
        self.clear()

    def clear(self):
        self._fullText = ""
        self._source = ""
        self._text = "" # working text - comments and strings blanked to prevent spurious pattern matches
        self._libraryList = []
        self._importedPackageNames = []
        self._subprogramParseObjects = []
        self._messages = []
        self._linePositions = None
        self._lenText = 0

    # OLD parsing return list of
    #   [ subprogramType, subprogramName, pos, [ argumentParseObject* ], [ libname* ], [ message* ]
    #     where subprogramType is one of 'submodel' 'segment' and 'external segment' (future to allow 'model' (+remote, embedded) and procedure (+?function))
    #     where subprogramName is an ESL identifier (not necessarily valid, mind)
    #     where pos is the start position in the original string of the name
    #     where an argumentParseObject is [ argumentType, datatype, eslVariableName ] - or maybe 'bad-arguments'
    #       where argumentType is one of 'output' 'input' 'attribute' - if valid (else prefixed 'bad-')
    #       where datatype is one of 'Real' 'Integer' 'Logical' - if valid
    #       where eslVariableName is an ESL identifier (will be a tag name for subprogram calls) - if valid
    #    where a libname is just the library name (possibly with file path) as given in a --LIBRARY statement
    #    where message is a possible concise error (?or info) message to be displayed

    """ Pattern matching
        Note: when have valid match, while match.start(?group) is the position (index) in the text of the first matched character,
        the match.end(?group) is the position (index) in the text immediately *after* the last matched character.
        So it is more like a *len* of the match (but *is* a position not a length), and is directly available to be used 
        as the start position for a following match.
    """

    def parseEsl(self, eslText:str, source:str):
        self.clear()

        self._fullText = eslText
        self._source = source

        # look for libraries before strip comments (does not take into account multiple subprograms)
        self._libraryList:list[str] = self._scanLibraries(eslText)

        # print("Before strip ({0})".format(len(eslText)))
        self._text:str = self._blankOutComments(eslText)
        # print("After strip ({0}):\n{1}".format(len(eslText), eslText))

        # look for USE statement importing package(s) into this code (after strip comments)
        self._importedPackageNames:list[str] = self._scanUsePackages(self._text)

        self._findSubprograms()

    def libraryList(self) -> list[str]:
        result = self._libraryList
        return result

    def importedPackageNames(self) -> list[str]:
        result = self._importedPackageNames
        return result

    def subprogramParseObjects(self) -> list[SubprogramParseObject]:
        result = self._subprogramParseObjects
        return result

    def messages(self):
        result = self._messages
        return result

    def _getLinePosition(self, pos:int) -> (int, int):
        lineNumber: int = -1
        characterNumber: int = -1
        if not self._linePositions and self._fullText:
            self._lenText = len(self._fullText)
            self._linePositions = []
            eolPos = -1
            while True:
                eolPos = self._fullText.find("\n", eolPos + 1)
                if eolPos >= 0:
                    self._linePositions.append(eolPos)
                else:
                    break
        nrLines = len(self._linePositions)
        if pos >= 0 and pos < self._lenText:
            if nrLines == 0:
                lineNumber = 1
                characterNumber = pos + 1
            else:
                for ix in range(nrLines - 1, -1, -1):
                    if pos > self._linePositions[ix]:
                        lineNumber = ix + 2
                        characterNumber = pos - self._linePositions[ix]
                        #if pos == self._linePositions[ix]:  # fall back to last char on line (so not on the \n)
                        #    characterNumber -= 1
                        break
                if lineNumber < 0: # on first line
                    lineNumber = 1
                    characterNumber = pos + 1
        #TEMP
        """ix = self._getPositionFromLine(lineNumber, characterNumber)
        if ix > 0:
            if ix != pos:
                print("error pos="+str(pos)+"!= ix="+str(ix)+" for "+str(lineNumber)+":"+str(characterNumber))
            ch = self._fullText[ix]
            print('\\n' if ch == '\n' else ch)"""
        return lineNumber, characterNumber

    def _getPositionFromLine(self, lineNumber, characterNumber):
        pos = -1
        if lineNumber > 0 and characterNumber > 0:
            pos = characterNumber - 1
            if self._linePositions and len(self._linePositions) > 0:
                if lineNumber > 1:
                    pos = self._linePositions[lineNumber-2] + characterNumber
        return pos

    def messagesString(self, giveLineNumber:bool=True) -> str:
        messages = ""
        ix = 0
        nrMessages = len(self._messages)
        for parseMessage in self._messages:
            ix += 1
            message = parseMessage.formatMessage(giveLineNumber)
            messages += message
            if ix < nrMessages:
                messages += "\n"
        return messages

    def parseDimensions(self, dimensionsText:str, pos:int=0, infoParseObject:ParseObject=None, checkNothingLeft:bool=True, allowStar:bool=False, parseReference:bool=False) -> (int, list):
        #OLDresult = [0, 1, 1, 1, 1, 1, 1]  # list: [ nr dimensions defined (0 for scalar, -1 if encounter error),
        #         lowbound-dim1, highbound-dim1, lowbound-dim2, highbound-dim2, lowbound-dim3, highbound-dim3 ] - these all default to 1
        #### TODO Extend to allow for package variables (non-syntactic) semantic extensions, with messages, and set usable=False so as to not allow them to be used and referenced in diagrams.
        dimensionalityParseObject = DimensionalityParseObject(infoParseObject)
        count = 0
        if dimensionsText:
            if dimensionsText == DimensionalityParseObject.UniversalToken:
                dimensionalityParseObject.universal = True
                pos = len(DimensionalityParseObject.UniversalToken)
            else:
                dimensionPattern = self._getPattern("dimensionPattern")
                starPattern = None
                if allowStar:
                    starPattern = self._getPattern("starPattern")
                # Look for first dimension bounds
                match = dimensionPattern.match(dimensionsText, pos)
                if match:
                    count += 1
                    lowerBound = 1
                    if parseReference:
                        lowerBound = DimensionalityParseObject.ReferenceUnsliced
                    if match[1]:
                        lowBound = match[1].replace("..", "")
                        lowerBound = int(lowBound)
                    upperBound = int(match[2])
                    dimensionalityParseObject.add_bounds(lowerBound, upperBound)
                    if upperBound < lowerBound:
                        parseMessage = self._addMessage("first dimension upper bound less than lower bound", pos, infoParseObject)
                        dimensionalityParseObject.messages.append(parseMessage)
                elif allowStar:
                    match = starPattern.match(dimensionsText, pos)
                    if match:
                        count += 1
                        dimensionalityParseObject.add_bounds(1, DimensionalityParseObject.StarDimension)
                if not match:
                    msg = "no bounds for first dimension"
                    if not allowStar and dimensionsText.find("*", pos) != -1:
                        msg += " (star not allowed)"
                    parseMessage = self._addMessage(msg, pos, infoParseObject)
                    dimensionalityParseObject.messages.append(parseMessage)
                    pos = -1
                if pos >= 0:
                    pos = match.end()
                    match = self._getPattern("separatingCommaPattern").match(dimensionsText, pos)
                    if match:
                        pos = match.end()
                        # Look for second dimension range
                        match = dimensionPattern.match(dimensionsText, pos)
                        if match:
                            count += 1
                            lowerBound = 1
                            if parseReference:
                                lowerBound = DimensionalityParseObject.ReferenceUnsliced
                            if match[1]:
                                lowBound = match[1].replace("..", "")
                                lowerBound = int(lowBound)
                            upperBound = int(match[2])
                            dimensionalityParseObject.add_bounds(lowerBound, upperBound)
                            if upperBound < lowerBound:
                                parseMessage = self._addMessage("second dimension upper bound less than lower bound", pos, infoParseObject)
                                dimensionalityParseObject.messages.append(parseMessage)
                        elif allowStar:
                            match = starPattern.match(dimensionsText, pos)
                            if match:
                                count += 1
                                dimensionalityParseObject.add_bounds(1, DimensionalityParseObject.StarDimension)
                        if not match:
                            msg = "no bounds for second dimension"
                            if not allowStar and dimensionsText.find("*", pos) != -1:
                                msg += " (star not allowed)"
                            parseMessage = self._addMessage(msg, pos, infoParseObject)
                            dimensionalityParseObject.messages.append(parseMessage)
                            pos = -1
                if pos >= 0:
                    if match:
                        pos = match.end()
                    match = self._getPattern("separatingCommaPattern").match(dimensionsText, pos)
                    if match:
                        pos = match.end()
                        # Look for third dimension range
                        match = dimensionPattern.match(dimensionsText, pos)
                        if match:
                            count += 1
                            lowerBound = 1
                            if parseReference:
                                lowerBound = DimensionalityParseObject.ReferenceUnsliced
                            if match[1]:
                                lowBound = match[1].replace("..", "")
                                lowerBound = int(lowBound)
                            upperBound = int(match[2])
                            dimensionalityParseObject.add_bounds(lowerBound, upperBound)
                            if upperBound < lowerBound:
                                parseMessage = self._addMessage("third dimension upper bound less than lower bound", pos, infoParseObject)
                                dimensionalityParseObject.messages.append(parseMessage)
                        elif allowStar:
                            match = starPattern.match(dimensionsText, pos)
                            if match:
                                count += 1
                                dimensionalityParseObject.add_bounds(1, DimensionalityParseObject.StarDimension)
                        if not match:
                            msg = "no bounds for third dimension"
                            if not allowStar and dimensionsText.find("*", pos) != -1:
                                msg += " (star not allowed)"
                            parseMessage = self._addMessage(msg, pos, infoParseObject)
                            dimensionalityParseObject.messages.append(parseMessage)
                            pos = -1
                if pos >= 0:
                    if count == 3:
                        pos = match.end()
                    if checkNothingLeft:
                        whatsLeft = dimensionsText[pos:]
                        if whatsLeft and not whatsLeft.isspace():
                            parseMessage = self._addMessage("unexpected characters (\""+whatsLeft+"\") at end of array specification", pos, infoParseObject)
                            dimensionalityParseObject.messages.append(parseMessage)
                            pos = -1
        return pos, dimensionalityParseObject

    def hasReadStatement(self, eslText:str) -> bool:  # READ READEL or INTERACT will block if run direct
        result = False
        eslText = self._blankOutComments(eslText)
        match = self._getPattern("readStatementPattern").match(eslText)
        if match:
            # statement = match.group(1)
            # print("found "+statement)
            result = True
        return result

    def _getPattern(self, key:str) -> Pattern:
        pattern = ParseEsl.patternCache.get(key)
        if pattern is None:
            rawPattern = getattr(self, key, None)
            if rawPattern:
                pattern = re.compile(rawPattern, ParseEsl.regexOptions)
                ParseEsl.patternCache[key] = pattern
        return pattern

    def _appDatatype(self, datatype:str) -> str:
        result = ''
        datatype = datatype.upper()
        if datatype == 'REAL': result = 'Real'
        if datatype == 'INTEGER': result = 'Integer'
        if datatype == 'LOGICAL': result = 'Logical'
        if datatype == 'CHARACTER': result = 'Character'
        if datatype == 'FILE': result = 'File'
        return result

    def _blankOutComments(self, eslText, alsoBlankStrings=True):
        result = eslText
        matches = self._getPattern("commentPattern").finditer(eslText)
        for m in matches:
            if m:
                result = result[:m.start()] + " "*(len(m[0])-1)+ result[m.end()-1:]
        if alsoBlankStrings:
            result = self._blankOutStrings(result)
        return result

    def _blankOutStrings(self, text):
        result = ""
        maxLength = len(text)
        quote = None
        ix = 0
        while ix < maxLength:
            ch = text[ix]
            if not quote: # not in string
                result += ch # don't strip ch (including starting quote)
                if ch == "\"" or ch == "%":
                    quote = ch # start string
            else: # in string
                if ch == quote:
                    if ix < maxLength - 1 and text[ix + 1] == quote: # pair of quotes - move along, stay in string
                        ix += 1
                    else: # proper end of string
                        quote = None
                        result += ch # don't strip closing quote
                else:
                    if ch == "\n": # end string if hit eol
                        quote = None
                        result += ch
                    else:
                        result += " " # replace ch in string with blank
            ix += 1
        return result

    def _scanLibraries(self, eslText):
        matches = self._getPattern("libraryPattern").finditer(eslText)
        libraryList = [] # at present simply the list of libraries in the whole esl-text (so all subprograms will get all libraries)
        for m in matches:
            if m:
                libraryText = m.group(1)
                #libs = libraryText.split(',')
                libTokens = libraryText.split()
                for libToken in libTokens:
                    libs = re.split("[,;]", libToken)
                    for lib in libs:
                        lib = lib.strip()
                        if lib and lib not in libraryList:
                            libraryList.append(lib)
        return libraryList

    def _scanUsePackages(self, eslText):
        matches = self._getPattern("usePackagesPattern").finditer(eslText)
        importedPackageNames = [] # at present simply the list of libraries in the whole esl-text (so all subprograms will get all libraries)
        for m in matches:
            if m:
                for groupMatch in m.groups():
                    if groupMatch:
                        packageNames = groupMatch.split(",")
                        for packageName in packageNames:
                            packageName = packageName.strip()
                            if packageName:
                                upperisedList = list(map(lambda item: item.upper(), importedPackageNames))
                                if packageName.upper() not in upperisedList:
                                    importedPackageNames.append(packageName)
        return importedPackageNames

    def _addMessage(self, message, pos, parseObject) -> ParseMessage:
        parseMessage = ParseMessage(self, message, pos, parseObject)
        if parseObject:
            subprogramParseObject = parseObject
            while subprogramParseObject.parent is not None:
                subprogramParseObject = subprogramParseObject.parent
            if subprogramParseObject:
                parseMessage.subprogramParseObject = subprogramParseObject
                subprogramParseObject.messages.append(parseMessage)
        self._messages.append(parseMessage)
        return parseMessage

    def _findSubprograms(self):
        # look for subprograms by keywords
        matches = self._getPattern("subprogramKeywordPattern").finditer(self._text)
        lastSubprogramParseObject = None
        for matchSubprogram in matches:
            if matchSubprogram and ParseEsl.is_keyword(matchSubprogram):
                keyword = matchSubprogram[1].upper()
                subprogramStartPos = matchSubprogram.end(1) - len(keyword) # start of keyword
                pos = matchSubprogram.end()
                subprogramName = ""
                match = self._getPattern("identifierPattern").match(self._text, pos)
                if match:
                    pos = match.end()
                    subprogramName = match[1]
                    subprogramStartPos = match.start(1) - 1 # start of name - set to the character *before* the start of the name - so caret better positioned
                subprogramParseObject = SubprogramParseObject(keyword, subprogramStartPos, subprogramName)
                if lastSubprogramParseObject:
                    if subprogramStartPos > lastSubprogramParseObject.endSignaturePos:
                        if lastSubprogramParseObject.endPos < 0 or subprogramStartPos < lastSubprogramParseObject.endPos:
                            self._addMessage("got subprogram keyword{position} before end of previous subprogram{subprogram}", subprogramStartPos, lastSubprogramParseObject)
                    else:
                        break
                if not subprogramName:
                    self._addMessage("no subprogram name{position}{subprogram}", subprogramStartPos, subprogramParseObject)
                lastSubprogramParseObject = subprogramParseObject
                validNameErr = esl.ValidateName(subprogramName, silent=True)
                if validNameErr:
                    self._addMessage("subprogram name "+validNameErr+"{position}{subprogram}", pos, subprogramParseObject)
                    pos = -1
                    #break

                if subprogramName:
                    if keyword in ["SUBMODEL", "SEGMENT", "MODEL", "PROCEDURE"]:
                        errMsgs = []
                        pos = self._parseSubprogramSignature(subprogramParseObject, pos)

                    # Search on down for matching "END" with optional name (to validate) and closing semicolon.
                    matchEnd = self._getPattern("subprogramEndPattern").search(self._text, subprogramStartPos)
                    if matchEnd:
                        subprogramParseObject.endPos = matchEnd.start()
                        if matchEnd[1]:
                            endName = matchEnd[1].strip()
                            if endName.upper() != subprogramName.upper():
                                endPos = matchEnd.start(1) - 3
                                self._addMessage("got END for \""+endName+"\"{position} expecting \""+subprogramName+"\"{subprogram}", endPos, subprogramParseObject)
                    else:
                        self._addMessage("no subprogram END{subprogram}{position}", subprogramStartPos, subprogramParseObject)

                    if keyword == "PACKAGE":
                        match = self._getPattern("endingSemicolonPattern").match(self._text, pos)
                        if not match:
                            self._addMessage("no package statement closing semicolon{position}{subprogram}", pos, subprogramParseObject)
                        else:
                            # Having checked for the END, parse the package body
                            self._parsePackageBody(subprogramParseObject)

                    self._subprogramParseObjects.append(subprogramParseObject)
        pass
        # Note: Fortran and (plain) C EXTERNAL procedures/functions are declared in subprogram bodies and their names are
        # not in application scope, so we don't need to handle them here.
        # Note: C+ EXTERNAL procedures/functions are declared as a normal such subprogram but with EXTERNAL before the
        # signature end semicolon (just like an EXTERNAL segment).

    def _parseArgDeclarations(self, signatureParseObject:SignatureParseObject, pos:int, doingOutput:bool, allowConstantInput:bool, allowFileSpecifier:bool):
        while True:
            match = self._getPattern("closeBracketPattern").match(self._text, pos)
            if match:
                break   # Dont set pos as will be checking for close bracket again
            else:
                if doingOutput:
                    match = self._getPattern("startInputArgsPattern").match(self._text, pos)
                    if match:
                        doingOutput = False
                        pos = match.end()

                headPattern = self._getPattern("typePattern")
                filePattern = self._getPattern("filePattern")

                if not doingOutput and allowConstantInput:
                    headPattern = self._getPattern("allowConstantHeadPattern")

                datatype = ""
                match = headPattern.match(self._text, pos)
                if match:
                    nrGroups = len(match.groups())
                    isConstant = False
                    if allowConstantInput and nrGroups == 3:
                        constant = match.group(1)
                        if constant:
                            isConstant = constant.strip() != ''
                        datatype = match.group(2)
                    elif nrGroups == 2:
                        datatype = match.group(1)
                    colonGroup = match.group(nrGroups) # 2 for typePattern or 3 for allowConstantHeadPattern
                    if colonGroup.find(":") != -1:
                        pos = match.end()
                        pos = self._parseArgVariables(signatureParseObject, pos, doingOutput, datatype, isConstant)
                    else:
                        self._addMessage("no colon found after type \""+datatype+"\"{position}{subprogram}", pos, signatureParseObject)
                        pos = -1
                        break

                elif allowFileSpecifier:
                    match = filePattern.match(self._text, pos)
                    if match:
                        datatype = match.group(1)
                        colonGroup = match.group(2)  # 2 for filePattern
                        if colonGroup.find(":") != -1:
                            pos = match.end()
                            pos = self._parseArgFileSpecifiers(signatureParseObject, pos, doingOutput, datatype)
                        else:
                            self._addMessage("no colon found after \"" + datatype + "\"{position}{subprogram}",
                                             pos, signatureParseObject)
                            pos = -1
                            break

                if not datatype:
                    self._addMessage("no argument type{position}{subprogram}", pos, signatureParseObject)
                    pos = -1
                    break

                if pos >= 0:
                    match = self._getPattern("endingSemicolonPattern").match(self._text, pos)
                    if match:
                        pos = match.end()   # continue loop to try to get type for next set of args
                    else:
                        match = self._getPattern("closeBracketPattern").match(self._text, pos)
                        if match:
                            break  # dont set pos as currently check close bracket again << may change this
                else:
                    break
        return pos

    def _parseArgVariables(self, signatureParseObject, pos, doingOutput, datatype, isConstant):
        # Parse a set of argument variable declarations with the same type (comma separated).
        while True:
            match = self._getPattern("identifierPattern").match(self._text, pos)
            if match:
                pos = match.end()
                name = match[1]
                validNameErr = esl.ValidateName(name, silent=True)
                if validNameErr:
                    self._addMessage("argument name "+validNameErr+"{position}{subprogram}", pos, signatureParseObject)
                    pos = -1
                    break
                dimensionality = None
                match = self._getPattern("openBracketPattern").match(self._text, pos)
                if match:
                    # Got an array dimension start
                    pos = match.end()
                    pos, dimensionality = self.parseDimensions(self._text, pos, signatureParseObject, checkNothingLeft=False, allowStar=True)
                    if pos >= 0:
                        match = self._getPattern("closeBracketPattern").match(self._text, pos)
                        if match:
                            pos = match.end()  # Where the dimensions bracket closed
                        else:
                            self._addMessage("no argument dimensions closing bracket{position}{subprogram}", pos, signatureParseObject)
                            pos = -1
                            break
                    else: # problem parsing dimensions
                        break
                # Setup this argument
                argumentParseObject = ArgumentParseObject(signatureParseObject, datatype, name, doingOutput, isConstant, dimensionality)
                subprogramParseObject = signatureParseObject.parent
                signatureParseObject.argumentParseObjects.append(argumentParseObject)
                match = self._getPattern("separatingCommaPattern").match(self._text, pos)
                if not match:
                    break # exit this function so as to check for next thing in the signature.
                else: # Continue loop and get next argument for this datatype
                    pos = match.end()
            else:
                self._addMessage("no argument identifier{position}{subprogram}", pos, signatureParseObject)
                pos = -1  # stop parsing signature
                break
        return pos

    def _parseArgFileSpecifiers(self, signatureParseObject, pos, doingOutput, datatype):
        while True:
            match = self._getPattern("identifierPattern").match(self._text, pos)
            if match:
                pos = match.end()
                name = match[1]

                validNameErr = esl.ValidateName(name, silent=True)
                if validNameErr:
                    self._addMessage("file specifier "+validNameErr+"{position}{subprogram}", pos, signatureParseObject)
                    pos = -1
                    break

                # Setup this argument
                argumentParseObject = ArgumentParseObject(signatureParseObject, datatype, name, doingOutput, False, None)
                subprogramParseObject = signatureParseObject.parent
                signatureParseObject.argumentParseObjects.append(argumentParseObject)

                match = self._getPattern("separatingCommaPattern").match(self._text, pos)
                if not match:
                    break  # exit this function so as to check for next thing in the signature.
                else:  # Continue loop and get next argument for this datatype
                    pos = match.end()

            else:
                self._addMessage("no argument file specifier{position}{subprogram}", pos, signatureParseObject)
                pos = -1  # stop parsing signature
                break

        return pos

    def _parseSubprogramSignature(self, subprogramParseObject, pos):
        argumentParseObjects = []
        signatureStartPos = pos
        signatureParseObject = SignatureParseObject(subprogramParseObject)
        subprogramParseObject.signatureParseObject = signatureParseObject
        match = self._getPattern("openBracketPattern").match(self._text, pos)
        if match:
            pos = match.end()
            signatureParseObject.openBracketPos = pos - 1
            # Look for empty brackets before parsing any args
            match = self._getPattern("closeBracketPattern").match(self._text, pos)
            if match:
                pos = match.end()  # Where the empty signature brackets closed
            else:
                doingOutput = True
                allowConstantInput = True
                allowFileSpecifier = True
                if subprogramParseObject.keyword == "PROCEDURE":
                    doingOutput = False
                    allowConstantInput = False
                    allowFileSpecifier = False
                pos = self._parseArgDeclarations(signatureParseObject, pos, doingOutput, allowConstantInput, allowFileSpecifier)
                if pos >= 0:
                    match = self._getPattern("closeBracketPattern").match(self._text, pos)
                    if match:
                       pos = match.end() # Where the args bracket closed
                    else:
                        self._addMessage("no signature closing bracket{position}{subprogram}", signatureStartPos, subprogramParseObject)
                        #pos = -1 # DON'T stop - carry on and look for closing semicolon
        if pos >= 0:
            match = self._getPattern("endingSemicolonPattern").match(self._text, pos)
            if not match:
                if subprogramParseObject.keyword == "SEGMENT":
                    match = self._getPattern("endSigExternalPattern").match(self._text, pos)
                    if match:
                        signatureParseObject.isExternal = True
                elif subprogramParseObject.keyword == "PROCEDURE":
                    match = self._getPattern("endSigExternalPattern").match(self._text, pos)
                    if match:
                        signatureParseObject.isExternal = True         # C++ EXTERNAL PROCEDURE (not function)
                    if not match:
                        if signatureParseObject.openBracketPos >= 0: # SYNTAX says a function must have brackets (may be empty)
                            match = self._getPattern("sigReturnPattern").match(self._text, pos)
                            if match:
                                pos = match.end()
                                # check whatever follows is whitespace or ;
                                postMatch = self._getPattern("sigPostReturnPattern").match(self._text, pos)
                                if not postMatch:
                                    self._addMessage("unexpected character (\""+self._text[pos]+"\") after function return type{position}{subprogram}", pos, subprogramParseObject)
                                    #pos = -1
                                else:
                                    if postMatch[0] != ";":
                                        pos = postMatch.end()
                                    signatureParseObject.returnType = match[1]
                                    # Setup the return as a scalar output argument - RESULT
                                    dimensionalityParseObject = DimensionalityParseObject(subprogramParseObject)
                                    dimensionalityParseObject.universal = True # function return RESULT is generic and of any dimensionality.number
                                    argumentParseObject = ArgumentParseObject(signatureParseObject, signatureParseObject.returnType, "RESULT",
                                                                              isOutput=True, isConstant=False, dimensionality=dimensionalityParseObject)
                                    subprogramParseObject = signatureParseObject.parent
                                    signatureParseObject.argumentParseObjects.append(argumentParseObject)
                                    # Still need to check for end signature semicolon - possibly preceded by EXTERNAL
                                    match = self._getPattern("endingSemicolonPattern").match(self._text, pos)
                                    if not match:
                                        match = self._getPattern("endSigExternalPattern").match(self._text, pos)
                                        if match:
                                            signatureParseObject.isExternal = True  # C++ EXTERNAL function (not procedure)
            if match:
                pos = match.end()
                subprogramParseObject.endSignaturePos = pos - 1
            else:
                self._addMessage("no signature closing semicolon{position}{subprogram}", signatureStartPos, subprogramParseObject)
                pos = -1
        return pos


    def _parsePackageBody(self, subprogramParseObject):
        pos = subprogramParseObject.startPos
        matches = self._getPattern("variableTypePattern").finditer(self._text, pos, subprogramParseObject.endPos)
        for match in matches:
            isConstant = False
            isParameter = False
            datatype = ""
            nrGroups = len(match.groups())
            if nrGroups == 3: # if have optional CONSTANT|PARAMETER
                option = match[1]
                if option:
                    option = option.strip().upper()
                    if option == "CONSTANT":
                        isConstant = True
                    elif option == "PARAMETER":
                        isParameter = True
                datatype = match.group(2)
            else:
                datatype = match.group(1)
            colonGroup = match.group(nrGroups)  # 2 for typePattern or 3 for allowConstantHeadPattern
            if colonGroup.find(":") != -1:
                if datatype:
                    pos = match.end()
                    pos = self._parsePackageVariables(subprogramParseObject, pos, datatype, isConstant, isParameter)
                else:
                    self._addMessage("no package variable type{position}{subprogram}", pos, subprogramParseObject)
                    pos = -1
                    break
            else:
                self._addMessage("no colon found after package variable type \"" + datatype + "\"{position}{subprogram}",
                                 pos, subprogramParseObject)
                pos = -1
                break

        if pos >= 0:
            pos = subprogramParseObject.startPos
            matches = self._getPattern("filePattern").finditer(self._text, pos, subprogramParseObject.endPos)
            for match in matches:
                datatype = match.group(1)
                colonGroup = match.group(2)  # 2 for filePattern
                if colonGroup.find(":") != -1:
                    pos = match.end()
                    pos = self._parsePackageFileSpecifiers(subprogramParseObject, pos, datatype)
                else:
                    self._addMessage("no colon found after \"" + datatype + "\"{position}{subprogram}",
                                     pos, subprogramParseObject)
                    pos = -1
                    break

    def _parsePackageVariables(self, subprogramParseObject, pos, datatype, isConstant, isParameter):
        # Parse a set of package variable declarations with the same type (comma separated).
        while True:
            match = self._getPattern("identifierPattern").match(self._text, pos)
            if match:
                pos = match.end()
                name = match[1]
                validNameErr = esl.ValidateName(name, silent=True)
                if validNameErr:
                    self._addMessage("package variable name "+validNameErr+"{position}{subprogram}", pos, subprogramParseObject)
                    pos = -1
                    break
                dimensionality = None
                match = self._getPattern("openBracketPattern").match(self._text, pos)
                if match:
                    # Got an array dimension start
                    pos = match.end()
                    pos, dimensionality = self.parseDimensions(self._text, pos, subprogramParseObject, checkNothingLeft=False, allowStar=True)
                    if pos >= 0:
                        match = self._getPattern("closeBracketPattern").match(self._text, pos)
                        if match:
                            pos = match.end()  # Where the dimensions bracket closed
                        else:
                            self._addMessage("no package variable dimensions closing bracket{position}{subprogram}", pos, subprogramParseObject)
                            pos = -1
                            break
                    else:  # problem parsing dimensions
                        break
                initialValue = None
                match = self._getPattern("initialValuePattern").match(self._fullText, pos)
                if match:
                    pos = match.end()
                    initialValue = match[0].strip()
                    initialValue = initialValue.replace('\n', ' ')

                # Setup this variable
                variableParseObject = VariableParseObject(subprogramParseObject, datatype, name, isConstant, isParameter, dimensionality, initialValue)
                subprogramParseObject.packageVariables.append(variableParseObject)

                match = self._getPattern("separatingCommaPattern").match(self._text, pos)
                if not match:
                    break # exit this function so as to check for next thing in the signature.
                else: # Continue loop and get next argument for this datatype
                    pos = match.end()
            else:
                self._addMessage("no package variable identifier{position}{subprogram}", pos, subprogramParseObject)
                pos = -1  # stop parsing signature
                break
        return pos

    def _parsePackageFileSpecifiers(self, subprogramParseObject, pos, datatype):
        while True:
            match = self._getPattern("identifierPattern").match(self._text, pos)
            if match:
                pos = match.end()
                name = match[1]
                validNameErr = esl.ValidateName(name, silent=True)
                if validNameErr:
                    self._addMessage("package file specifier "+validNameErr+"{position}{subprogram}", pos, subprogramParseObject)
                    pos = -1
                    break

                # Setup this argument
                variableParseObject = VariableParseObject(subprogramParseObject, datatype, name, isConstant=False, isParameter=False, dimensionality=None, initialValue=None)
                subprogramParseObject.packageVariables.append(variableParseObject)

                match = self._getPattern("separatingCommaPattern").match(self._text, pos)
                if not match:
                    break  # exit this function so as to check for next thing in the subprogram (package).
                else:  # Continue loop and get next argument for this datatype
                    pos = match.end()

            else:
                self._addMessage("no package file specifier{position}{subprogram}", pos, subprogramParseObject)
                pos = -1  # stop parsing subprogram
                break

        return pos

    # For dimensionality handling
    _instance = None

    @staticmethod
    def get_dimensionality(dimensions:str, checkNothingLeft:bool=True, allowStar:bool=False, parseReference:bool=False) -> DimensionalityParseObject:
        if ParseEsl._instance is None:
            ParseEsl._instance = ParseEsl()
        pos, dimensionality = ParseEsl._instance.parseDimensions(dimensions, checkNothingLeft=checkNothingLeft, allowStar=allowStar, parseReference=parseReference)
        return dimensionality

    @staticmethod
    def is_keyword(match:re.Match):
        result = True
        start = match.start(1) # pos of first char of first inner pattern match
        if start > 0:
            prevCh = match.string[start-1]
            if prevCh.isalpha() or prevCh == "_":
                result = False
        if result:
            end = match.end(1) # pos *after* last char of first inner pattern match
            if end < len(match.string):
                nextCh = match.string[end]
                if nextCh.isalpha() or nextCh == "_":
                    result = False
        return result
