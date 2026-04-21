#! /usr/bin/python

PROGRAMTYPES = ['study', 'remote-program', 'embedded-program']
MODULETYPES = ['program', 'model', 'submodel', 'segment', 'package', 'code', 'setup-info']
SUBPROGRAMBASETYPES = ['diagram', 'code']
CALLABLEMODULETYPES = ['submodel', 'segment', 'function']
MODELTYPES = ['model', 'embedded-segment', 'remote-segment']
SEGMENTTYPES = ['segment', 'external-segment']
CODETYPES = ['ESL', 'file']
CODESUBPROGRAMTYPES = ['submodel', 'segment', 'external-segment', 'model', 'procedure', 'function', 'external-function'] #### TODO extend with ?(+remote-segment, embedded-segment)
CALLABLECODESUBPROGRAMTYPES = ['submodel', 'segment', 'external-segment', 'function', 'external-function']
