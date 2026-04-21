#! /usr/bin/python

class Subprogram():

    def __init__(self, subprogramBaseType):
        self._subprogramBaseType = subprogramBaseType
        self._valid = True

    def subprogramBaseType(self):
        return self._subprogramBaseType

    def valid(self):
        return self._valid

    def set_valid(self, valid):
        self._valid = valid
