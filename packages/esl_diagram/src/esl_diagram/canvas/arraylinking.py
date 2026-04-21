#! /usr/bin/python

import re

LINKABLES = ["link", "port", "node"] # linkable object categories

class DimensionsInfo():         # Based on DimensionalityParseObject in esl_studio app/esl/parseesl
    UniversalToken = "..."      # Denotes universal dimensionality - generic and of any dimensionality.number - same as in esl_studio for parseesl DimensionalityParseObject
    StarDimension: int = -9999  # An integer that is not likely to be an actual dimension range element

    def __init__(self, dimensionsText:str, bounds:list[tuple[int,int]]):
        self._dimensionsText:str = dimensionsText
        self._bounds:list[tuple[int,int]] = bounds
        self.universal = False
        if dimensionsText == DimensionsInfo.UniversalToken:
            self.universal = True

    def bounds(self) -> list[tuple[int,int]]:
        return self._bounds

    def add_bounds(self, lowerBound:int, upperBound:int):
        self._bounds.append((lowerBound, upperBound))

    def number(self) -> int:
        return len(self._bounds)

    def sizes(self) -> list[int]:
        sizes = []
        number = len(self._bounds)
        if number > 0 and number <= 3:
            for ix in range(number):
                if self._bounds[ix][1] == DimensionsInfo.StarDimension:
                    sizes.append(DimensionsInfo.StarDimension)
                else:
                    sizes.append(self._bounds[ix][1] - self._bounds[ix][0] + 1)
        return sizes

    def size(self) -> int:
        sizes = self.sizes()
        size = 1
        for nr in sizes:
            if nr == DimensionsInfo.StarDimension:
                size = DimensionsInfo.StarDimension
                break
            size = size * nr
        return size

    def str_sizes(self) -> str:
        result = "("
        result += ",".join(map(lambda it: "*" if it == DimensionsInfo.StarDimension else str(it), self.sizes()))
        result += ")"
        return result

    def dimensionsList(self) -> list[str]: # std form
        result = []
        number = len(self._bounds)
        if number > 0 and number <= 3:
            for ix in range(number):
                if self._bounds[ix][1] == DimensionsInfo.StarDimension:
                    result.append("*")
                else:
                    boundStr = ""
                    if self._bounds[ix][0] != 1:
                        boundStr += str(self._bounds[ix][0]) + ".."
                    boundStr += str(self._bounds[ix][1])
                    result.append(boundStr)
        return result

    def dimensions(self) -> str: # print std form - no brackets|spaces
        if self.universal:
            result = DimensionsInfo.UniversalToken
        else:
            result = ",".join(self.dimensionsList())
        return result

    def __str__(self):
        result = ""
        result += self.dimensions()
        return result

_DatatypeBracketsRegex  = re.compile(r"\s*([^\(]+)\(([^\)]+)\)\s*$")
_DimensionRegex         = re.compile(r"\s*([-]?\d+\s*\.\.)?\s*([-]?\d+)")
_StarRegex              = re.compile(r"\s*\*")
_SeparatingCommaRegex   = re.compile(r"\s*,")

def parseDatatype(datatype:str) -> (str, DimensionsInfo):     # Based on parseDimensions in esl_studio app/esl/parseesl

    baseType = ""
    dimensionsInfo = None
    match = _DatatypeBracketsRegex.match(datatype)
    if match:
        baseTypeStr = match[1].strip()
        dimensionsText = match[2].strip()
        ok = False
        bounds = []
        pos = 0
        if dimensionsText:
            # Look for universal dimensionality token
            if dimensionsText == DimensionsInfo.UniversalToken:
                ok = True
            else:
                ok = True
                for count in range(3):
                    if ok:
                        # Look for dimension bounds
                        match = _DimensionRegex.match(dimensionsText, pos)
                        if match:
                            lowerBound = 1
                            if match[1]:
                                lowBound = match[1].replace("..", "")
                                lowerBound = int(lowBound)
                            upperBound = int(match[2])
                            if upperBound >= lowerBound:
                                bounds.append((lowerBound, upperBound))
                            else:
                                ok = False
                        else:
                            match = _StarRegex.match(dimensionsText, pos)
                            if match:
                                bounds.append((1, DimensionsInfo.StarDimension))
                            else:
                                ok = False
                        if not ok:
                            break
                        pos = match.end()
                        whatsLeft = dimensionsText[pos:]
                        if not whatsLeft or whatsLeft.isspace():
                            break # finished ok
                        elif count == 2:
                            ok = False # something left after 3rd bounds
                            break
                        # Look for separating comma (before next bounds)
                        match = _SeparatingCommaRegex.match(dimensionsText, pos)
                        if match:
                            pos = match.end()
                        else:
                            ok = False
                            break
                    pass # end for loop
        if ok:
            baseType = baseTypeStr
            dimensionsInfo = DimensionsInfo(dimensionsText, bounds)
    return baseType, dimensionsInfo

def compatibleTypes(type1, baseType1, dimensionsInfo1, type2, baseType2, dimensionsInfo2, allowGeneric="either"):
    # See if the second baseType2, dimensionsInfo2 is compatible with the primary baseType1, dimensionsInfo1
    # by seeing if baseTypes match exactly
    # and dimensionsInfos's dimensions (strs) match exactly
    # if not then if dimensionsInfos's numbers match exactly,
    # if not then, if second dimensionsInfo has the same sizes (all elements)
    # or check each element for generic match
    # for allowGeneric="second" - to match first type against any compatible generic second type
    # or allowGeneric="either"  - to match generically both ways
    # or if not then by seeing if either is of universal dimensionality and matching its baseType against the other's or its (full) type if scalar
    compatibility = False
    # Both are arrays (have baseType and dimensionsInfo) (or possibly both universal)
    if baseType1 and baseType2 and baseType1 == baseType2: # baseTypes must match exactly
        if dimensionsInfo1.dimensions() == dimensionsInfo2.dimensions(): # std format str match exactly
            compatibility = True
        elif dimensionsInfo1.number() == dimensionsInfo2.number(): # dimensionality.numbers must match exactly
            #### TODO check the dimensionsInfos' dimensionsLists before sizes to assess specificity (i.e same dimensionsList[ix]s more specific than just sizes[ix] same)
            sizes1 = dimensionsInfo1.sizes()
            sizes2 = dimensionsInfo2.sizes()
            compatibility = True # see if all dimensionality.number sizes are the same or compatible
            for ix in range(len(sizes1)):
                if sizes1[ix] != sizes2[ix]: # sizes[ix] not same here
                    compatibility = False # not compatible - unless there is a generic match here
                    if allowGeneric == "either":
                        if sizes1[ix] == DimensionsInfo.StarDimension: # if type1 is generic here - matches any size in type2 here
                            compatibility = True
                    if not compatibility and (allowGeneric == "second" or allowGeneric == "either"):
                        if sizes2[ix] == DimensionsInfo.StarDimension:  # if type2 is generic here - matches any size in type1 here
                            compatibility = True
                if not compatibility: # not compatible here - so not at all
                    break
    if not compatibility:
        # Check if first has universal dimensionality
        if dimensionsInfo1 and dimensionsInfo1.universal:
            if allowGeneric == "either":
                compatibility = (baseType2 == baseType1) or (type2 == baseType1)
    if not compatibility:
        # Check if second has universal dimensionality
        if dimensionsInfo2 and dimensionsInfo2.universal:
            if allowGeneric == "second" or allowGeneric == "either":
                compatibility = (baseType1 == baseType2) or (type1 == baseType2)
    return compatibility

#def findLinkableDefn(diagram, category, type):
#    defn = diagram.registry().get(category, type) # exact type matches (base and dimensions)
#    if defn is None:
#        baseType1, dimensionsInfo1 = parseDatatype(type)

def findCompatibleDefn(diagram, category, type1, baseType1, dimensionsInfo1):
    defn = None
    defnList = diagram.registry().getCategoryValues(category)
    for definition in defnList:
        exactType = definition.getAttribute("exact-type") # a definition may enforce exact-match (already checked)
        if not exactType or exactType.lower() != "true":
            defnType = definition.getAttribute("type")
            baseType2, dimensionsInfo2 = parseDatatype(defnType)
            if defn is None:
                compatibility = compatibleTypes(type1, baseType1, dimensionsInfo1, defnType, baseType2, dimensionsInfo2, allowGeneric="second")
                if compatibility:
                    defn = definition
                    break
                equivalentTypes = definition.getAttribute("equivalent-types") # see if definition has any equivalents
                if equivalentTypes:
                    equivalentTypesList = equivalentTypes.split("|")
                    for equivalentType in equivalentTypesList:
                        equivalentType = equivalentType.strip()
                        baseType2, dimensionsInfo2 = parseDatatype(equivalentType)
                        if compatibleTypes("", baseType1, dimensionsInfo1, equivalentType, baseType2, dimensionsInfo2, allowGeneric="second"):
                            defn = definition
                            break
                    if defn:
                        break
    pass #end for
    return defn

def arrayTypesCompatible(link, connectable):
    compatible = False
    errorMsg = "" # will use default join failure msg
    link_exactType = False
    exactType = link.defn().getAttribute("exact-type")
    if exactType and exactType.lower() == "true":
        link_exactType = True
    connectable_exactType = False
    exactType = connectable.defn().getAttribute("exact-type")
    if exactType and exactType.lower() == "true":
        connectable_exactType = True

    if link_exactType or connectable_exactType:  # if either require exact-type - that's that
        compatible = link.type() == connectable.type()
    else:
        link_type = link.type()
        link_baseType = link.baseType()
        connectable_type = connectable.type()
        connectable_baseType = connectable._baseType

        link_dimensionsInfo = link.dimensionsInfo()
        connectable_dimensionsInfo = connectable.dimensionsInfo()

        # Get any equivalent-types
        link_typePairs = []
        equivalent_types = link.defn().getAttribute("equivalent-types")  # see if definition has any equivalents
        if equivalent_types:
            equivalent_types = list(map(lambda item: item.strip(), equivalent_types.split("|")))
            for equivalent_type in equivalent_types:
                baseType, dimensionsInfo = parseDatatype(equivalent_type)
                if baseType:
                    link_typePairs.append((baseType, dimensionsInfo))
        connectable_typePairs = []
        equivalent_types = connectable.defn().getAttribute("equivalent-types")  # see if definition has any equivalents
        if equivalent_types:
            equivalent_types = list(map(lambda item: item.strip(), equivalent_types.split("|")))
            for equivalent_type in equivalent_types:
                baseType, dimensionsInfo = parseDatatype(equivalent_type)
                if baseType:
                    connectable_typePairs.append((baseType, dimensionsInfo))
        # Put the primary-types first and cross-check for compatibilty together with each link's equivalent-type (if any) against the connectable's set
        link_typePairs.insert(0, (link_baseType, link_dimensionsInfo))
        connectable_typePairs.insert(0, (connectable_baseType, connectable_dimensionsInfo))
        for link_typePair in link_typePairs:
            for connectable_typePair in connectable_typePairs:
                compatibility = compatibleTypes(link_type, link_typePair[0], link_typePair[1], connectable_type,
                                                connectable_typePair[0], connectable_typePair[1], allowGeneric="either")
                if compatibility:
                    compatible = True
                    break
    return compatible, errorMsg
