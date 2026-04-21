#! /usr/bin/python

def entitise(strng):
    result = strng
    result = result.replace('&', '%%amp%%')
    result = result.replace('"', '&quot;')
    result = result.replace('<', '&lt;')
    result = result.replace('>', '&gt;')
    result = result.replace('%%amp%%', '&amp;')
    return result
