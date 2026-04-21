#! /usr/bin/python

import wx

MODULES_CHANGE_EVENT = wx.NewEventType()
EVT_MODULES_CHANGE = wx.PyEventBinder(MODULES_CHANGE_EVENT, 0)

class ModulesChangeEvent(wx.PyCommandEvent): # in python cant use wx.NotifyEvent (as would in C++) so emulate
    def __init__(self, category, moduleId, subType='', variableId=0, data=''):
        #wx.PyEvent.__init__(self, -1, MY_NOTIFY_EVENT)
        wx.PyCommandEvent.__init__(self, MODULES_CHANGE_EVENT)
        self.category = category            # 'add-submodel' 'remove-submodel' 'add-package' 'remove-package'
                                            # ? add-parameter' remove-parameter' 'add-package-variable' 'remove-package-variable'
        self.moduleId = moduleId            # use 0 to add, actual moduleId to remove (redo will make a new moduleId)
        self.subType = subType              # when add the module the subType (depends on the module-type)
        self.variableId = variableId        # when remove the id of the variable in the module
        self.data = data                    # when remove, data to enable undo to recreate module (with a new moduleId)
        self._vetoed = False                # wont allow remove if submodel/package(variable) in use

    def IsAllowed(self):
        return not self._vetoed

    def Veto(self):
        self._vetoed = True

    def __str__(self):
        s = '<ModulesChangeEvent type=' + str(self.GetEventType())
        s += ' allowed='+str(self.IsAllowed())
        s += ' category=' + str(self.category)
        s += ' moduleId=' + str(self.moduleId)
        s += ' subType=' + str(self.subType)
        s += ' variableId=' + str(self.variableId)
        s += ' data=' + str(self.data)
        s += '>'
        return s
