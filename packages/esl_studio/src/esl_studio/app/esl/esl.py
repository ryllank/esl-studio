#! /usr/bin/python

import string

EslNameMaxChars = 28

EslNameFirstChar = string.ascii_letters

EslNameChars = string.ascii_letters + string.digits + '_$'

EslLogicalValues = ['TRUE', 'FALSE']
EslKeywords = ['IF', 'OR', 'AND', 'END', 'FOR', 'NOT', 'USE', 'ELSE',   # includes the EslLogicalValues
               'LOOP', 'OPEN', 'PLOT', 'READ', 'STEP', 'STOP', 'THEN', 'TRIM', 
               'TRUE', 'WHEN', 'CLOSE', 'FALSE', 'MODEL', 'PRINT', 'STUDY', 
               'WHILE', 'CREATE', 'DELETE', 'END_IF', 'IOSTAT', 'NOSORT', 
               'READEL', 'REMOTE', 'RETURN', 'RESUME', 'DYNAMIC', 'ELSE_IF', 
               'INCLUDE', 'INITIAL', 'PACKAGE', 'PREPARE', 'SEGMENT', 'REWRITE', 
               'RESTART', 'ANALYSIS', 'CONSTANT', 'EMBEDDED',
               'END_LOOP', 'END_WHEN', 'EXTERNAL', 'INTERACT', 'SNAPSHOT', 
               'SUBMODEL', 'TABULATE', 'TERMINAL', 'TRANSFER', 'OPTIMIZE', 
               'END_STUDY', 'LINEARIZE', 'PARAMETER', 'PROCEDURE', 'TERMINATE', 
               'PROCEDURAL', 'EIGENVALUE', 'CLEAR_SCREEN',
               'COMMUNICATION', 'END_PROCEDURAL', 'TRANSFER_MATRIX', 'LIBRARY']
EslBaseTypeNames = ['REAL', 'INTEGER', 'LOGICAL']
EslTypeNames = EslBaseTypeNames + ['CHARACTER', 'FILE']
EslReservedVariables = ['T', 'TSTART', 'TFIN', 'CINT', 'DISERR', 'INTERR', 
                        'OP_STP', 'ALGO', 'NSTEP', 'GE_EUL', 'IEX_CM', 'DIS_ST']
EslAlgoNames = ['RK5', 'RK4', 'RK2', 'STIFF2', 'GEAR1', 'GEAR2', 'ADAMS', 
                'RK1', 'LIN1', 'LIN2']

EslStandardFunctions = ['SIN', 'ASIN', 'COS', 'ACOS', 'ATAN', 'ATAN2', 'LOG', 'ALOG', 'EXP',
                        'ABS', 'SQRT', 'RAND', 'INT', 'LEN', 'LEN_1', 'LEN_2', 'LEN_3',
                        'ACHAR', 'IACHAR', 'INV', 'DET', 'TRNSP', 'SUB_STRING']

EslReservedNames = EslKeywords + EslTypeNames + EslReservedVariables + EslAlgoNames + EslStandardFunctions

EslSubmodelText = "SUBMODEL {0}();\nDYNAMIC\nEND;"

EslFoldLevelPlusKeywords = {
    "STUDY" : 0,
    "MODEL": 1,
    "SUBMODEL": 1,
    "SEGMENT": 1,
    "PROCEDURE": 1,
    "PACKAGE": 1,
    "INITIAL": 2,
    "DYNAMIC": 2,
    "STEP": 2,
    "COMMUNICATION": 2,
    "TERMINAL": 2,
    "ANALYSIS": 2,
}
EslFoldLevelMinusKeywords = {
    "END_STUDY": 0,
    "END": 1,
}
"""EslFoldLevelPlusKeywords = {
    "STUDY" : 1,
    "MODEL": 2,
    "SUBMODEL": 2,
    "SEGMENT": 2,
    "PROCEDURE": 2,
    "PACKAGE": 2,
    "INITIAL": 3,
    "DYNAMIC": 3,
    "STEP": 3,
    "COMMUNICATION": 3,
    "TERMINAL": 3,
    "ANALYSIS": 3,
}
EslFoldLevelMinusKeywords = {
    "END_STUDY": 1,
    "END": 2,
}"""

def ValidateName(name, silent):
    errTxt = ''
    if not name:
        errTxt = 'no name given'
        if not silent:
            raise Exception(errTxt)
    else:
        uname = name.upper()
        if uname not in EslReservedNames:
            if validChars(name):
                result = True
            else:
                errTxt = '"' + name + '" contains invalid characters'
                if not silent:
                    raise Exception(errTxt)
        else:
            #errTxt = '"' + name + '" is reserved'
            if uname in EslKeywords:
                errTxt = '"' + name + '" is an ESL keyword'
            elif uname in EslTypeNames:
                errTxt = '"' + name + '" is an ESL type name'
            elif uname in EslReservedVariables:
                errTxt = '"' + name + '" is an ESL reserved variable'
            elif uname in EslAlgoNames:
                errTxt = '"' + name + '" is an ESL ALGO name'
            elif uname in EslStandardFunctions:
                errTxt = '"' + name + '" is an ESL standard function'
            if not silent:
                raise Exception(errTxt)
    return errTxt

def validChars(name):
    result = False
    if name[0] in EslNameFirstChar:
        result = True
        for ch in name:
            if ch not in EslNameChars:
                result = False
                break
    return result
