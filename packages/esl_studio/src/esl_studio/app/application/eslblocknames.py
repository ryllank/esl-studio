#! /usr/bin/python

from ..esl import esl

class EslBlockNames(object):
    def __init__(self):
        self._blockNames = {}
    def get(self, name):
        return self._blockNames.get(name.upper())
    def isin(self, name):
        result = (name.upper()[0:esl.EslNameMaxChars] in self._blockNames)
        return result
    def add(self, name, block):
        result = ''
        errTxt = esl.ValidateName(name, silent=False)
        if not errTxt:
            upname = name.upper()[0:esl.EslNameMaxChars]
            if not upname in self._blockNames:
                self._blockNames[upname] = block
                result = upname
            else:
                exceptionMsg = 'Name "' + name + '" '
                if len(name) > esl.EslNameMaxChars:
                    exceptionMsg += '(truncated) '
                exceptionMsg += 'is already in the block'
                raise Exception(exceptionMsg)
        return result

    def delete(self, name):
        upname = name.upper()
        if upname in self._blockNames:
            del self._blockNames[upname]

    def getUnusedName(self, stem):
        name = ''
        count = 0
        errTxt = esl.ValidateName(stem, silent=True)
        if not errTxt:
            name = stem
        else:
            count += 1
            name = stem + "_" + str(count)
        while True:
            upname = name.upper()
            if self._blockNames.get(upname) is None:
                break
            else:
                count += 1
                name = stem + "_" + str(count)
                if len(name) > esl.EslNameMaxChars:
                    name = ''
                    raise Exception('Cannot get an unused name based on "' + stem + '"')
                    #break
        return name

    def isUniqueToLength(self, name, length):
        result = True
        if length < 1 or length > esl.EslNameMaxChars:
            length = esl.EslNameMaxChars
        upTruncName = name.upper()[0:length]
        for entry in self._blockNames.keys():
            if upTruncName == entry[0:length]:
                result = False
                break
        return result
