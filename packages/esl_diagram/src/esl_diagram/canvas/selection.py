#! /usr/bin/python

import wx

class Selection(object):
    """ Handles the selected objects for the canvas.
    """
    def __init__(self, interactions):
        self._interactions = interactions
        self.clear()

    def selection(self): return self._selection

    def clear(self):
        self._selection = []
        self._extent = None

    def add(self, object):
        self._selection.append(object)
            
    def remove(self, object):
        try:
            self._selection.remove(object)
        except Exception:
            pass

    def len(self):
        return len(self._selection)

    def get(self, index):
        return self._selection[index]
    
    def extent(self):
        ext = None
        for obj in self._selection:
            if ext is None: ext = obj.extent()
            else: ext = ext.Union(obj.extent())
        return ext

    def dragByPolymorphic(self, obj, dc, displacement, refreshCache=None):
        obj.dragBy(dc, displacement, refreshCache)

    def gatherDeleteListPolymorphic(self, obj, deleteList):
        obj.gatherDeleteList(deleteList)

    def map(self, func, *args):
        #results = map(func, self._selection, args)
        for obj in self._selection: func(obj, *args)
        #return results
    def mapTillTrue(self, func, *args):
        result = False
        for obj in self._selection: 
            result = func(obj, *args)
            if result: break
        return result
