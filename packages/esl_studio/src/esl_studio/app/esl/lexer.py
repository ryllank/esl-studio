from enum import IntEnum
import re
from typing import Tuple

eolPattern = r'\r\n|\n'
whiteSpacePattern = r'[ \t\f\v]+' # not \s as this includes \n \r
commentStartString = r"--"
inclusionStartString = r"<<"
inclusionEndString = r">>"
encryptPattern = r"\s*ENCRYPT[^\r\n]*" # match case-insensitive
endEncryptPattern = r"\s*END_ENCRYPT[^\r\n]*" # match case-insensitive
numberPattern = r"\d+(\.\d+)?([EeDd][+-]?\d+)?" # real and int - should we discriminate - no: if need just check text value
stringQuoteChar =  r'"' # quote in string is doubled "hi ""there"""
percentStringQuoteChar =  r"%" # quote in string is doubled %is %%one%% string%
specialPattern = r"\*\*|/=|<=|>=|[()*+-./:;<=>_[\]]" # explicit check for 2 special character operators
identifierPattern = r"[A-Za-z][A-Za-z0-9_]*" # then check if is any kind of keyword - note not supporting $ (even initial)
transferIdentifier = "TRANSFER"
transferMatrixIdentifier = "TRANSFER_MATRIX"
preTfPattern = r'\s*\(\s*'
otherPattern = r"[^\"()*+-./:;<=>_[\]\n\s\w]"

class EslTokenType(IntEnum):
    OTHER = 0
    EOL = 1
    WHITESPACE = 2
    COMMENT = 3
    NUMBER = 4
    STRING = 5
    PERCENT_STRING = 6
    UNTERMINATED_STRING = 7
    SPECIAL = 8
    IDENTIFIER = 9
    TRANSFER_FN = 10
    TRANSFER_MATRIX = 11
    UNTERMINATED_TRANSFER = 12
    INCLUSION = 13
    ENCRYPT = 14
    END_ENCRYPT = 15
    # poss more later
    KEYWORDS = 20 # last (highest number)

EslMultilineTokens = [
    EslTokenType.INCLUSION,
    EslTokenType.TRANSFER_FN,
    EslTokenType.TRANSFER_MATRIX,
    EslTokenType.UNTERMINATED_TRANSFER,
]

class EslToken():
    def __init__(self, start:int=0, length:int=0, type:EslTokenType=EslTokenType.OTHER, text:str=""):
        self.start:int = start
        self.length:int = length
        self.type:EslTokenType = type
        self.text:str = text

    def __str__(self):
        text = self.text
        if self.type == EslTokenType.EOL or self.type in EslMultilineTokens:
            text = text.replace('\r', '\\r')
            text = text.replace('\n', '\\n')
        elif self.type == EslTokenType.WHITESPACE:
            text = text.replace('\t', '\\t')
            text = text.replace('\f', '\\f')
            text = text.replace('\v', '\\v')
        type = str(self.type).replace('EslTokenType.', '')
        result = "@"+str(self.start)+"#"+str(type)+"|"+text+"|"
        return result

class EslLexer():
    def __init__(self):
        pass

    def _getComment(self, text:str) -> int:
        length = 0
        maxLength = len(text)
        while length < maxLength:
            ch = text[length]
            if ch == "\n" or ch == "\r":
                break
            else: # matched quote
                length += 1
        return length

    def _getInclusion(self, text:str) -> int:
        length = 0
        end = text.find(inclusionEndString)
        if end == -1:
            length = len(text)
        else:
            length = end + len(inclusionEndString)
        return length

    def _getString(self, quote:str, text:str) -> Tuple[int, EslTokenType, str]:
        length = 0
        type = EslTokenType.UNTERMINATED_STRING
        maxLength = len(text)
        if text[0] == quote:
            length += 1
        while length < maxLength:
            ch = text[length]
            if ch == "\n" or ch == "\r":
                break
            elif ch != quote:
                length += 1
            else:
                if length+1 < maxLength and text[length+1] == quote:
                    length += 2
                else: # matched quote
                    length += 1
                    type = EslTokenType.STRING
                    if quote == percentStringQuoteChar:
                        type = EslTokenType.PERCENT_STRING
                    break
        string = text[0:length]
        return length, type, string

    def _getTransferFunction(self, text:str) -> Tuple[int, bool]:
        length = 0
        terminated = False
        maxLength = len(text)
        brackets = 0
        while length < maxLength:
            ch = text[length]
            if ch == "(":
                brackets += 1
                length += 1
            elif ch == ")":
                if brackets == 0: # valid termination
                    terminated = True
                    break
                else:
                    brackets -= 1
                    length += 1
            elif ch == ",":
                if brackets == 0: # valid termination
                    terminated = True
                #else: # invalid termination
                break
            else: # may include \r \n
                length += 1
        return length, terminated

    def _tokeniseTransferFunction(self, transferToken:EslToken, text:str, tokens:list[EslToken]) -> Tuple[EslToken, str]:
        # we can push this transferToken identifier and carry on looking
        transferType = EslTokenType.TRANSFER_FN
        if transferToken.text.upper() == transferMatrixIdentifier:
            transferType = EslTokenType.TRANSFER_MATRIX
        startTextPos = transferToken.start
        tokens.append(transferToken)
        startTextPos += transferToken.length
        text = text[transferToken.length:]
        resultToken = None
        terminated = False
        # look for poss multiline tf in function
        preTfMatch = re.match(preTfPattern, text)
        if preTfMatch:
            preTfText = preTfMatch.group(0)
            tfStart = len(preTfText)
            self.Tokenise(startTextPos, preTfText, tokens)
            startTextPos += tfStart
            text = text[tfStart:]
            tfLength, terminated = self._getTransferFunction(text)
            if terminated:
                tfString = text[:tfLength]
                # Find the end whitespace and shorten the actual TF token
                endSpaces = 0
                for i in range(tfLength):
                    ch = tfString[tfLength - 1 - i]
                    if not ch.isspace():
                        endSpaces = i
                        break
                tfLength -= endSpaces
                resultToken = EslToken(startTextPos, tfLength, transferType, text[:tfLength])
        if not terminated:
            # Make an UNTERMINATED_TRANSFER current token all the way to end of text being processed.
            resultToken = EslToken(startTextPos, len(text), EslTokenType.UNTERMINATED_TRANSFER, text)
        pass
        return resultToken, text

    def Tokenise(self, startTextPos:int, text:str, tokens:list[EslToken]):
        while len(text) > 0:
            token, text = self._doTokenise(startTextPos, text, tokens)
            if token is not None:
                tokens.append(token)
                startTextPos = token.start + token.length
                text = text[token.length:]
        pass

    def _doTokenise(self, startTextPos:int, text:str, tokens:list[EslToken]) -> Tuple[EslToken, str]:
        token = None
        match = re.match(eolPattern, text)
        if match:
            token = EslToken(startTextPos, match.end(), EslTokenType.EOL, text[:match.end()])
        if token is None:
            match = re.match(whiteSpacePattern, text)
            if match:
                token = EslToken(startTextPos, match.end(), EslTokenType.WHITESPACE, text[:match.end()])
        if token is None:
            if text.startswith(commentStartString):
                length = self._getComment(text)
                token = EslToken(startTextPos, length, EslTokenType.COMMENT, text[:length])
        if token is None:
            if text.startswith(inclusionStartString):
                length = self._getInclusion(text)
                token = EslToken(startTextPos, length, EslTokenType.INCLUSION, text[:length])
        if token is None:
            match = re.match(encryptPattern, text, re.IGNORECASE)
            if match:
                token = EslToken(startTextPos, match.end(), EslTokenType.ENCRYPT, text[:match.end()])
        if token is None:
            match = re.match(endEncryptPattern, text, re.IGNORECASE)
            if match:
                token = EslToken(startTextPos, match.end(), EslTokenType.END_ENCRYPT, text[:match.end()])
        if token is None:
            match = re.match(numberPattern, text)
            if match:
                token = EslToken(startTextPos, match.end(), EslTokenType.NUMBER, text[:match.end()])
        if token is None:
            ch = text[0]
            if ch == stringQuoteChar or ch == percentStringQuoteChar:
                length, type, string = self._getString(ch, text)
                token = EslToken(startTextPos, length, type, text[:length])
        if token is None:
            match = re.match(specialPattern, text)
            if match:
                token = EslToken(startTextPos, match.end(), EslTokenType.SPECIAL, text[:match.end()])
        if token is None:
            match = re.match(identifierPattern, text)
            if match:
                token = EslToken(startTextPos, match.end(), EslTokenType.IDENTIFIER, text[:match.end()])
                if token.text.upper() == transferIdentifier or token.text.upper() == transferMatrixIdentifier:
                    token, text = self._tokeniseTransferFunction(token, text, tokens)
        if token is None:
            match = re.match(otherPattern, text)
            if match:
                token = EslToken(startTextPos, match.end(), EslTokenType.OTHER, text[:match.end()])
        return token, text
