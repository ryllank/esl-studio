
import re
from typing import Tuple

nl = '\n'

class Pole():
    def __init__(self, order: int):
        self.order: int = order

    def __str__(self):
        result = "S"
        if self.order and self.order > 1: result += "^"+str(self.order)
        return result

class Sign():
    def __init__(self, sign: str = "+"):
        self.sign: str = sign  # + or - only

    def __str__(self):
        result = str(self.sign)
        return result

class Coeft():  # identifier or real number
    def __init__(self, identifier: bool, value: str):
        self.identifier: bool = identifier  # if true value is identifier, else is a real number
        self.value: str = value

    def __str__(self):
        result = str(self.value)
        return result

class Term():  # require coeft or pole, allow both (e.g. -2.0s**3)
    def __init__(self, sign:Sign=None, coeft:Coeft=None, pole:Pole=None):
        self._sign: Sign = sign
        self.coeft: Coeft = coeft
        self.pole: Pole = pole

    def sign(self) -> str:
        return "+" if not self._sign else self._sign.sign

    def value(self) -> str:
        return "1" if not self.coeft else self.coeft.value

    def order(self) -> int:
        return 0 if not self.pole else self.pole.order

    def __str__(self):
        result = ""
        if self._sign: result += str(self._sign)
        if self.coeft and self.coeft.value != "1":
            result += str(self.coeft)
            if self.pole: result += "*"
        if self.pole:  result += str(self.pole)
        return result

class Factor():
    def __init__(self, terms:list[Term]=[]):
        self.terms: list[Term] = terms

    def add(self, term:Term):
        self.terms.append(term)

    def __str__(self):
        result = ""
        n = len(self.terms)
        if n: result = "("
        for term in self.terms:
            result += str(term)
        if n: result += ")"
        return result

class Gain():
    def __init__(self, sign: Sign = None, coeft: Coeft = None):
        self.sign: Sign = sign
        self.coeft: Coeft = coeft

    def __str__(self):
        result = ""
        if self.sign: result = str(self.sign)
        result += str(self.coeft)
        return result

class Numerator():
    def __init__(self, gain: Gain = None, factors: list[Factor] = []):
        self.gain: Gain = gain
        self.factors: list[Factor] = factors

    def __str__(self):
        result = ""
        if self.gain: result = "Gain: "+str(self.gain)+", "
        result += "Factors: "
        for factor in self.factors:
            result += str(factor)
        return result

class Denominator():
    def __init__(self, pole:Pole=None, factors: list[Factor]=[]):
        self.origin: Pole = pole
        self.factors: list[Factor] = factors

    def add(self, term:Term):
        self.terms.append(term)

    def __str__(self):
        result = ""
        if self.origin: result = "Origin: "+str(self.origin)+", "
        result += "Factors: "
        for factor in self.factors:
            result += str(factor)
        return result

class ParseTF():

    tfPattern = r"([^/]+)/([^/]+$)"
    signPattern = r"([+-])"
    identifierPattern = r"[A-Za-z][A-Za-z0-9_]*"
    realPattern = r"(\d*)(\.\d*)?([EeDd][+-]?\d*)?" # was r"\d+(\.\d+)?([EeDd][+-]?\d+)?" - now check digit(s) before and after . and after exponent
    intPattern = r"\d+"
    polePattern = r"[s|S]\*\*(\d+)?"

    def __init__(self):
        self._tf : str = ""
        self._initialisations = ""
        self._reverseOrder = False
        self.clear()

    def clear(self):
        self._numerator_str : str = ""
        self._denominator_str : str = ""
        self.numerator : Numerator = None
        self.denominator : Denominator = None
        self.identifiers : list[str] = []
        # poss temp
        self.numerator_intermediate_factor : Factor = None
        self.denominator_intermediate_factor : Factor = None
        self.numerator_factor : Factor = None
        self.denominator_factor : Factor = None
        self.n : int = 0
        self.m : int = 0
        self.k : int = 0
        pass

    def setTF(self, tf:str) -> str:
        self._tf = tf
        self._initialisations = ""
        self.clear()
        err = self.getNumeratorAndDenominator()
        return err

    def setNumeratorAndDenominator(self, numerator: str, denominator : str) -> str :
        self._numerator_str = numerator
        self._denominator_str = denominator
        self._tf = self._numerator + "/" + self._denominator
        err = ""
        return err

    def setInitialisations(self, initialisations : str) -> str: # comma separated initialisations
        info = ""
        self._initialisations = list(map(lambda item: item.strip(), initialisations.split(",")))
        if self.denominator:
            if len(self._initialisations) > self.m:
                info = "more than "+str(self.m)+" initial values - excess ones will be ignored"
            elif len(self._initialisations) < self.m:
                info = "less than " + str(self.m) + " initial values - 0.0 will be used for the rest"
        return info

    def getNumeratorAndDenominator(self) -> str :
        err = ""
        match = re.match(ParseTF.tfPattern, self._tf)
        if not match:
            err = "failed to split numerator and denominator"
        else:
            self._numerator_str = match.group(1)
            self._denominator_str = match.group(2)
        return err

    def addIdentifier(self, value:str):
        if value not in self.identifiers:
            self.identifiers.append(value)

    def parse(self) -> str :
        err = self.parseNumerator()
        if not err:
            err = self.parseDenominator()
        return err

    def parseNumerator(self) -> str:
        err = ""
        gain = None
        factors = []

        text = self._numerator_str.strip()
        sign = None
        if text and (text[0] == "+" or text[0] == "-"):
            sign = Sign(text[0])
            text = text[1:].lstrip()
            # make gain of +|- one for the sign
            gain = Gain(sign, Coeft(False, "1"))
        if text and text[0] == "(": # do not advance text

            err, newFactors, text = self.parseFactors(text, factors)
            if err:
                err += " parsing numerator factors"
            if not err and (len(newFactors) == 0 or text != ""):
                err = "failed to complete parsing numerator factors"

        else:
            # look for naked pole
            err, pole, text = self.parsePole(text)
            if not err and pole:
                factors.append(Factor([ Term(None, None, pole)])) # factor of one term - the pole

                if text:
                    if text[0] == "(":  # do not advance text
                        err, newFactors, text = self.parseFactors(text, factors)
                        if err:
                            err += " parsing numerator factors after pole"
                        if not err and (len(newFactors) == 0 or text != ""):
                            err = "failed to complete parsing numerator factors after pole"
                    else:
                        err = "unexpected text parsing numerator after pole: \""+text+"\" - expecting ("

            elif not err:
                #match identifier or real (=coeft)
                err, coeft, text = self.parseCoeft(text)
                if not err:
                    if coeft.identifier:
                        self.addIdentifier(coeft.value)
                    gain = Gain(sign, coeft)
                    if text:
                        if text[0] == "*" or text[0] == "(":
                            # look for * and parse pole and factors
                            if text[0] == "*":
                                text = text[1:].lstrip()
                                err, pole, text = self.parsePole(text)
                                if not err and pole:
                                    factors.append(Factor([Term(None, None, pole)]))  # factor of one term - the pole
                                elif not err:
                                    err = "failed to parse pole after gain"
                                if not err and text:
                                    if text[0] == "(":  # do not advance text
                                        err, newFactors, text = self.parseFactors(text, factors)
                                        if err:
                                            err += " parsing numerator factors after gain and pole"
                                        if not err and (len(newFactors) == 0 or text != ""):
                                            err = "failed to complete parsing numerator factors after gain and pole"
                                    else:
                                        err = "unexpected text parsing numerator: \""+text+"\" - expecting ("
                            else: # "("
                                err, newFactors, text = self.parseFactors(text, factors)
                                if err:
                                    err += " parsing numerator factors after gain"
                                if not err and (len(newFactors) == 0 or text != ""):
                                    err = "failed to complete parsing numerator factors after gain"
                        else:
                            err = "unexpected text parsing numerator: \""+text+"\" - expecting * or ("
                    else:
                        factors.append(Factor([Term(None, Coeft(False, "1"), None)]))  # factor of one term - "1"

        if not err:
            self.numerator = Numerator(gain, factors)

        return err

    def parseDenominator(self) -> str:
        err = ""
        text = self._denominator_str.strip()
        origin = None
        factors = []

        # look for plain (not even a sigh) pole - for the origin
        err, pole, text = self.parsePole(text)
        if not err and pole:
            factors.append(Factor([Term(None, None, pole)]))  # factor of one term - the pole
            origin = pole

        if not err and text:
            if text[0] == "(":  # do not advance text
                err, newFactors, text = self.parseFactors(text, factors)
                if err:
                    err += " parsing denominator factors"
                if not err and (len(newFactors) == 0 or text != ""):
                    err = "failed to complete parsing denominator factors"
            else:
                err = "unexpected text parsing denominator: \""+text+"\" - expecting ("

        if not err:
            self.denominator = Denominator(origin, factors)

        return err

    def parseFactors(self, text:str, priorFactors:list[Factor]) -> Tuple[str,list[Factor],str]: # text includes the first "(", this checks for more factors, text is updated
        err = ""
        newFactors = priorFactors
        if text[0] != "(":
            err = "no ("
        else:
            text = text[1:].lstrip()
            factor = Factor([])
            sign = None
            if text and (text[0] == "+" or text[0] == "-"): # opt unary
                sign = Sign(text[0])
                text = text[1:].lstrip()
            while not err and text:
                term = None
                # look for bare pole
                err, pole, text = self.parsePole(text)
                if not err and pole:
                    term = Term(sign, None, pole)
                elif not err:
                    # match identifier or real (=coeft)
                    err, coeft, text = self.parseCoeft(text)
                    if not err:
                        if coeft.identifier:
                            self.addIdentifier(coeft.value)
                        pole = None
                        if text and text[0] == "*":
                            text = text[1:].lstrip()
                            err, pole, text = self.parsePole(text)
                        else:
                            # see if a pole follows
                            if text:
                                match = re.match(ParseTF.identifierPattern, text)
                                if match and (match.group(0) == "s" or match.group(0) == "S"):
                                    err = "unexpected text: \""+text+"\" - expecting * before pole"
                        if not err:
                            term = Term(sign, coeft, pole)
                if not err:
                    factor.add(term)

                    if text:
                        if text[0] == "+" or text[0] == "-": # binary
                            sign = Sign(text[0])
                            text = text[1:].lstrip()
                            pass # round the while loop for the next term in this factor
                        elif text[0] == ")":
                            text = text[1:].lstrip()
                            break # out of the while for terms and finish the factor
                        else:
                            err = "unexpected text: \""+text+"\" - expecting + - or )"
                    else:
                        err = "unexpected end of text"
            pass # end of while terms
            if not err:
                newFactors.append(factor)
                if text:
                    if text[0] == "(": # dont advance text
                        err, newFactors, text = self.parseFactors(text, newFactors) #another factor
                    else:
                        err = "unexpected text: \""+text+"\" - expecting ("

        return err, newFactors, text

    def parseCoeft(self, text:str) -> Tuple[str,Coeft,str]:
        err = ""
        coeft = None
        match = re.match(ParseTF.identifierPattern, text)
        if match:
            if match.group(0) == "s" or match.group(0) == "S":
                err = "unexpected pole (S) parsing coefficient"
            else:
                coeft = Coeft(True, match.group(0))
                text = text[match.end():].lstrip()
        else:
            match = re.match(ParseTF.realPattern, text)
            if match:
                if not match.group(1) and match.group(2):
                    if err: err += ", "
                    err += "no digits before decimal point"
                if match.group(2) == ".":
                    if err: err += " + "
                    err += "no digits after decimal point"
                if match.group(3) and not match.group(3)[-1].isdigit():
                    if err: err += " + "
                    err += "no digits after exponent"
                if not err:
                    coeft = Coeft(False, match.group(0))
                    text = text[match.end():].lstrip()
                else:
                    err += " parsing coefficient"
            else:
                err = "failed to parse coefficient"
        return err, coeft, text

    def parsePole(self, text) -> Tuple[str,Pole,str]:
        err = ""
        pole = None
        match = re.match(ParseTF.identifierPattern, text)
        if match and (match.group(0) == "s" or match.group(0) == "S"):
            text = text[1:] # no spaces allowed before **
            if len(text) >= 2 and text[0] == "*" and text[1] == "*":
                text = text[2:] # no spaces allowed after **
                match = re.match(ParseTF.intPattern, text)
                if match:
                    order = int(match.group(0))
                    pole = Pole(order)
                    text = text[match.end():].lstrip()
                else:
                    err = "failed to parse pole order"
            else:
                pole = Pole(1)
            if not err:
                text = text.lstrip()
        return err, pole, text

    def derive(self) -> str:
        err = ""
        self.numerator_intermediate_factor = self.expandFactors(self.numerator.factors)
        self.denominator_intermediate_factor = self.expandFactors(self.denominator.factors)
        self.numerator_factor = self.condenseFactor(self.numerator_intermediate_factor)
        self.denominator_factor = self.condenseFactor(self.denominator_intermediate_factor)

        if len(self.numerator_factor.terms) > 0: self.n = self.numerator_factor.terms[0].order()
        if len(self.denominator_factor.terms) > 0: self.m = self.denominator_factor.terms[0].order()
        if self.denominator.origin and self.denominator.origin.order: self.k = self.denominator.origin.order

        if self.m == 0:
            err = "denominator is of order 0"
        elif self.n > self.m:
            err = "numerator is of higher order than denominator"
        return err

    def expandFactors(self, factors_:list[Factor]) -> Factor:
        newFactor = Factor([])
        if len(factors_) > 0:
            factors = factors_.copy()
            while len(factors) > 1:
                merged = []
                first = factors.pop(0)
                second = factors.pop(0)
                for term1 in first.terms:
                    for term2 in second.terms:
                        newTerm = self.multiplyTerms(term1, term2)
                        merged.append(newTerm)
                factors.insert(0, Factor(merged))
            pass
            newFactor = factors[0]
        return newFactor

    def multiplyTerms(self, term1:Term, term2:Term) -> Term:
        sign1 = term1.sign()
        sign2 = term2.sign()
        sign = Sign("+")
        if sign1 != sign2:
            sign = Sign("-")
        value = "1"
        if term1.value() != "1": value = term1.value()
        if term2.value() != "1":
            if value != "1":
                value += "*" + term2.value()
            else:
                value = term2.value()
        coeft = Coeft(False, value)
        pole = None
        order = term1.order() + term2.order()
        if order > 0:
            pole = Pole(order)
        newTerm = Term(sign, coeft, pole)
        return newTerm

    def condenseFactor(self, factor:Factor) -> Factor:
        newFactor = Factor([])
        if len(factor.terms) > 0:
            terms = factor.terms.copy()
            terms.sort(key=lambda term: term.order(), reverse=True)

            highestOrder = terms[0].order()

            newTerms = []
            for order in range(highestOrder, -1, -1):
                orderTerms = list(filter(lambda term: term.order() == order, terms))
                n = len(orderTerms)
                if n > 1:
                    termValue = "("
                    for term in orderTerms:
                        termValue += term.sign()+term.value()
                    termValue += ")"
                    pole = None if order == 0 else Pole(order)
                    newTerm = Term(Sign("+"), Coeft(False, termValue), pole)
                    newTerms.append(newTerm)
                elif n == 1:
                    newTerms.append(orderTerms[0])
                pass
            pass
            newFactor = Factor(newTerms)
        return newFactor

    def generateEsl(self, genTransferFunction, coderegion:str): # coderegion : "declarations" "initial" "dynamic" ["step" "communication" "include" not used]
        result = ""
        nAuxilaryVariables = self.m
        if nAuxilaryVariables > 0:
            if coderegion == "declarations":
                if nAuxilaryVariables > 0:
                    if nAuxilaryVariables == 1:
                        result += "-- State variable for "
                    else:
                        result += "-- State variables ("+str(nAuxilaryVariables)+") for "
                    result += "Transfer Function-"+str(genTransferFunction.objectId())
                    result += nl
                    result += "REAL: "
                    for i in range(nAuxilaryVariables):
                        result += genTransferFunction.makeEslName("Z" + str(i))
                        if i < nAuxilaryVariables - 1:
                            result += ", "
                    result += ";" + nl

            elif coderegion == "initial":
                # get the initial values from the ICS attribute value (string - comma separated values - where not supplied use 0)
                if nAuxilaryVariables > 0:
                    if nAuxilaryVariables == 1:
                        result += "-- Initialisation for "
                    else:
                        result += "-- Initialisations ("+str(nAuxilaryVariables)+") for "
                    result += "Transfer Function-"+str(genTransferFunction.objectId())
                    result += nl
                    for i in range(nAuxilaryVariables):
                        value = "0.0"
                        if i < len(self._initialisations):
                            value = self._initialisations[i]
                        result += genTransferFunction.makeEslName("Z"+str(i)) + " := " + value + ";" + nl
                    if nAuxilaryVariables > 1:
                        result += "--\n"

            elif coderegion == "dynamic":
                if nAuxilaryVariables > 1:
                    if nAuxilaryVariables == 2:
                        result += "-- Auxiliary equation for "
                    else:
                        result += "-- Auxiliary equations ("+str(nAuxilaryVariables - 1)+") for "
                    result += "Transfer Function-"+str(genTransferFunction.objectId())
                    result += nl
                    for i in range(nAuxilaryVariables - 1):
                        result += genTransferFunction.makeEslName("Z"+str(i)+"'") + " := " + genTransferFunction.makeEslName("Z"+str(i+1)) + ";" + nl
                    if nAuxilaryVariables > 2:
                        result += "--\n"

                result += "-- State equation for "
                result += "Transfer Function-"+str(genTransferFunction.objectId())
                result += nl
                # Template for the ESL name for the "x" variable (?or expression) that is the product for the TF
                # i.e. the name for the output that is linked to the input (x) of the TF
                xVariable = "{I:x}"
                result += self.generateStateEquation(genTransferFunction, xVariable)

                result += "-- Output equation for "
                result += "Transfer Function-"+str(genTransferFunction.objectId())
                result += nl

                # Template for the ESL name for the output variable "y"
                yVariable = "{O:y}"
                result += self.generateOutputEquation(genTransferFunction, yVariable)
                result += "--\n"

        return result

    def generateStateEquation(self, genTransferFunction, xVariable:str):
        # from code6.f
        # * State equation      Z'm-1 = (X - bm-1.Zm-1 - .... - bk.zk)/bm
        # * -------------                                          if m>k
        # *                     Z'm-1 = X/bm                       if m=k
        if self.n > self.m or self.m == 0:
            result = "invalid state equation"
        else:
            result = genTransferFunction.makeEslName("Z" + str(self.m - 1) + "'") + " := "
            if self.denominator_factor.terms[0].sign() == "-":
                result += "-"
            if self.m > self.k:
                result += "("+xVariable
                terms = self.denominator_factor.terms[1:]
                if self._reverseOrder:
                    terms.reverse()
                for i in range(len(terms)):
                    term = terms[i]
                    multiplier = term.value()
                    if multiplier != "1":
                        multiplier += "*"
                    else:
                        multiplier = ""
                    sign = " - "
                    if term.sign() == "-":
                        sign = " + "
                    result += sign + multiplier + genTransferFunction.makeEslName("Z"+str(term.order()))
                result += ")"
            else: # self.m == self.k:
                result += xVariable
            term = self.denominator_factor.terms[0]
            divisor = term.value()
            if divisor != "1":
                result += "/" + divisor
            result += ";"
        result += nl
        return result

    def generateOutputEquation(self, genTransferFunction, yVariable:str):
        # from code6.f
        # * Output equation     Y = K(an.Zn + an-1.Zn-1 + .... +a0.Z0)
        # * ---------------                                        if m>n
        # *                     Y = K(an.Z'n-1 + an-1.Zn-1 ....    if m=n
        if self.n > self.m or self.m == 0:
            result = "invalid output equation"
        else:
            result = yVariable + " := "
            terms = self.numerator_factor.terms.copy()
            if self._reverseOrder:
                terms.reverse()
            nTerms = len(terms)
            if self.numerator.gain and str(self.numerator.gain) != "1":
                result += str(self.numerator.gain)
                if nTerms > 0:
                    result += "*"
            sign = " + "
            if nTerms > 0:
                if nTerms > 1:
                    result += "("
                start = 0
                end = nTerms
                if self.m == self.n:
                    if not self._reverseOrder:
                        start = 1
                    else:
                        end = nTerms - 1
                if self.m == self.n and not self._reverseOrder:
                    term = self.numerator_factor.terms[0]
                    multiplier = term.value()
                    if multiplier != "1":
                        multiplier += "*"
                    else:
                        multiplier = ""
                    sign = ""
                    if term.sign() == "-":
                        sign = "-"
                    result += sign + multiplier + genTransferFunction.makeEslName("Z"+str(term.order()-1)+"'")
                for i in range(start, end):
                    term = terms[i]
                    multiplier = term.value()
                    if multiplier != "1":
                        multiplier += "*"
                    else:
                        multiplier = ""
                    sign = " + "
                    if term.sign() == "-":
                        sign = " - "
                    if i == start and (self.m != self.n or self._reverseOrder):
                        if sign == " + ":
                            sign = ""
                        else:
                            sign = "-"
                    result += sign + multiplier + genTransferFunction.makeEslName("Z"+str(term.order()))
                    if i < end - 1:
                        sign = " + "
                if self.m == self.n and self._reverseOrder:
                    term = self.numerator_factor.terms[0]
                    multiplier = term.value()
                    if multiplier != "1":
                        multiplier += "*"
                    else:
                        multiplier = ""
                    sign = " + "
                    if term.sign() == "-":
                        sign = " - "
                    if nTerms == 1:
                        if sign == " + ":
                            sign = ""
                        else:
                            sign = "-"
                    result += sign + multiplier + genTransferFunction.makeEslName("Z"+str(term.order()-1)+"'")
                if nTerms > 1:
                    result += ")"
            elif str(self.numerator.gain) == "1":
                result += "1"
            result += ";"
        result += nl

        return result

    @property
    def tf(self) -> str :
        return self._tf

    @property
    def reverseOrder(self):
        return self._reverseOrder

    @reverseOrder.setter
    def reverseOrder(self, value:bool):
        self._reverseOrder = value
