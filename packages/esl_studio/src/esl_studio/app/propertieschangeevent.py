#! /usr/bin/python

import wx

PROPERTIES_CHANGE_EVENT = wx.NewEventType()
EVT_PROPERTIES_CHANGE = wx.PyEventBinder(PROPERTIES_CHANGE_EVENT, 0)

#class MyNotifyEvent(wx.PyEvent): 
class PropertiesChangeEvent(wx.PyCommandEvent): # in python cant use wx.NotifyEvent (as would in C++) so emulate
    def __init__(self, category, propertyId, propertyTag, newValue, oldValue):
        #wx.PyEvent.__init__(self, -1, MY_NOTIFY_EVENT)
        wx.PyCommandEvent.__init__(self, PROPERTIES_CHANGE_EVENT)
        self.category = category            # 'model' 'submodel' 'entity' & 'simulationparameter'
                                            # + basic graphical objects (see ise.propertiescontrol.PropertiesKnownElements)
                                            # + TODO 'package-variable' 'parameter'
        self.propertyId = propertyId        # something to identify the item - e.g. canvasId at present/canvasId:objectId
        self.propertyTag = propertyTag      # property tag/name to for the property of the item (?all)
        self.newValue = newValue
        self.oldValue = oldValue
        self._vetoed = False

    def __str__(self):
        s = '<PropertiesChangeEvent type=' + str(self.GetEventType())
        s += ' allowed='+str(self.IsAllowed())
        s += ' category=' + str(self.category)
        s += ' propertyId=' + str(self.propertyId)
        s += ' propertyTag=' + str(self.propertyTag)
        s += ' newValue=' + str(self.newValue)
        s += ' oldValue=' + str(self.oldValue)
        s += '>'
        return s

    def IsAllowed(self):
        return not self._vetoed

    def Veto(self):
        self._vetoed = True
