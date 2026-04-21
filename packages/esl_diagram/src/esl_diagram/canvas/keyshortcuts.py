#! /usr/bin/python

import wx

#from interactions import Interactions
from .selection import Selection
from .actions import ActionContext
from .object import Object

keycodes = {
  #wx.WXK_NONE = 0,
  wx.WXK_BACK:'Back',
  wx.WXK_TAB:'Tab',
  wx.WXK_RETURN:'Return',
  wx.WXK_ESCAPE:'Escape',
  wx.WXK_SPACE:'Space',
  wx.WXK_DELETE:'Delete',
  wx.WXK_START:'Start',
  wx.WXK_LBUTTON:'LButton',
  wx.WXK_RBUTTON:'RButton',
  wx.WXK_CANCEL:'Cancel',
  wx.WXK_MBUTTON:'MButton',
  wx.WXK_CLEAR:'Clear',
  wx.WXK_SHIFT:'Shift',
  wx.WXK_ALT:'Alt',
  wx.WXK_CONTROL:'Control',
  #wx.WXK_RAW_CONTROL:'RawControl',
  wx.WXK_MENU:'Menu',
  wx.WXK_PAUSE:'Pause',
  wx.WXK_CAPITAL:'Capital',
  wx.WXK_END:'End',
  wx.WXK_HOME:'Home',
  wx.WXK_LEFT:'Left',
  wx.WXK_UP:'Up',
  wx.WXK_RIGHT:'Right',
  wx.WXK_DOWN:'Down',
  wx.WXK_SELECT:'Select',
  wx.WXK_PRINT:'Print',
  wx.WXK_EXECUTE:'Execute',
  wx.WXK_SNAPSHOT:'Snapshot',
  wx.WXK_INSERT:'Insert',
  wx.WXK_HELP:'Help',
  wx.WXK_NUMPAD0:'Numpad_0',
  wx.WXK_NUMPAD1:'Numpad_1',
  wx.WXK_NUMPAD2:'Numpad_2',
  wx.WXK_NUMPAD3:'Numpad_3',
  wx.WXK_NUMPAD4:'Numpad_4',
  wx.WXK_NUMPAD5:'Numpad_5',
  wx.WXK_NUMPAD6:'Numpad_6',
  wx.WXK_NUMPAD7:'Numpad_7',
  wx.WXK_NUMPAD8:'Numpad_8',
  wx.WXK_NUMPAD9:'Numpad_9',
  wx.WXK_MULTIPLY:'Multiply',
  wx.WXK_ADD:'Add',
  wx.WXK_SEPARATOR:'Separator', #?
  wx.WXK_SUBTRACT:'Subtract',
  wx.WXK_DECIMAL:'Decimal',
  wx.WXK_DIVIDE:'Divide',
  wx.WXK_F1:'F1',
  wx.WXK_F2:'F2',
  wx.WXK_F3:'F3',
  wx.WXK_F4:'F4',
  wx.WXK_F5:'F5',
  wx.WXK_F6:'F6',
  wx.WXK_F7:'F7',
  wx.WXK_F8:'F8',
  wx.WXK_F9:'F9',
  wx.WXK_F10:'F10',
  wx.WXK_F11:'F11',
  wx.WXK_F12:'F12',
  wx.WXK_F13:'F13',
  wx.WXK_F14:'F14',
  wx.WXK_F15:'F15',
  wx.WXK_F16:'F16',
  wx.WXK_F17:'F17',
  wx.WXK_F18:'F18',
  wx.WXK_F19:'F19',
  wx.WXK_F20:'F20',
  wx.WXK_F21:'F21',
  wx.WXK_F22:'F22',
  wx.WXK_F23:'F23',
  wx.WXK_F24:'F23',
  wx.WXK_NUMLOCK:'Numlock',
  wx.WXK_SCROLL:'Scroll',
  wx.WXK_PAGEUP:'PageUp',
  wx.WXK_PAGEDOWN:'PageDown',
  wx.WXK_NUMPAD_SPACE:'Numpad_Space',
  wx.WXK_NUMPAD_TAB:'Numpad_Tab',
  wx.WXK_NUMPAD_ENTER:'Numpad_Enter',
  wx.WXK_NUMPAD_F1:'Numpad_F1',
  wx.WXK_NUMPAD_F2:'Numpad_F2',
  wx.WXK_NUMPAD_F3:'Numpad_F3',
  wx.WXK_NUMPAD_F4:'Numpad_F4',
  wx.WXK_NUMPAD_HOME:'Numpad_Home',
  wx.WXK_NUMPAD_LEFT:'Numpad_Left',
  wx.WXK_NUMPAD_UP:'Numpad_Up',
  wx.WXK_NUMPAD_RIGHT:'Numpad_Right',
  wx.WXK_NUMPAD_DOWN:'Numpad_Down',
  wx.WXK_NUMPAD_PAGEUP:'Numpad_PageUp',
  wx.WXK_NUMPAD_PAGEDOWN:'Numpad_PageDown',
  wx.WXK_NUMPAD_END:'Numpad_End',
  wx.WXK_NUMPAD_BEGIN:'Numpad_Begin',
  wx.WXK_NUMPAD_INSERT:'Numpad_Insert',
  wx.WXK_NUMPAD_DELETE:'Numpad_Delete',
  wx.WXK_NUMPAD_EQUAL:'Numpad_Equal',
  wx.WXK_NUMPAD_MULTIPLY:'Numpad_F1',
  wx.WXK_NUMPAD_ADD:'Numpad_Add',
  wx.WXK_NUMPAD_SEPARATOR:'Numpad_Separator',
  wx.WXK_NUMPAD_SUBTRACT:'Numpad_Subtract',
  wx.WXK_NUMPAD_DECIMAL:'Numpad_Decimal',
  wx.WXK_NUMPAD_DIVIDE:'Numpad_Divide',
  wx.WXK_WINDOWS_LEFT:'Windows_Left',
  wx.WXK_WINDOWS_RIGHT:'Windows_Right',
  wx.WXK_WINDOWS_MENU:'Windows_Menu',
  wx.WXK_COMMAND:'Command',
  wx.WXK_SPECIAL1:'Special_1',
  wx.WXK_SPECIAL2:'Special_2',
  wx.WXK_SPECIAL3:'Special_3',
  wx.WXK_SPECIAL4:'Special_4',
  wx.WXK_SPECIAL5:'Special_5',
  wx.WXK_SPECIAL6:'Special_6',
  wx.WXK_SPECIAL7:'Special_7',
  wx.WXK_SPECIAL8:'Special_8',
  wx.WXK_SPECIAL9:'Special_9',
  wx.WXK_SPECIAL10:'Special_10',
  wx.WXK_SPECIAL11:'Special_11',
  wx.WXK_SPECIAL12:'Special_12',
  wx.WXK_SPECIAL13:'Special_13',
  wx.WXK_SPECIAL14:'Special_14',
  wx.WXK_SPECIAL15:'Special_15',
  wx.WXK_SPECIAL16:'Special_16',
  wx.WXK_SPECIAL17:'Special_17',
  wx.WXK_SPECIAL18:'Special_18',
  wx.WXK_SPECIAL19:'Special_19',
  wx.WXK_SPECIAL20:'Special_20'
}

class Keyshortcuts(object):

    def __init__(self, interactions):
        self._interactions = interactions
        self._keys = {}

    def clearKeyshortcutDefinitions(self):
        self._keys = {}

    def setKeyshortcutDefinitions(self, canvasDefinitions):
        self.loadKeysFromXml(canvasDefinitions)

    def loadKeysFromXml(self, xmlElement):
        if xmlElement:
            if xmlElement.name() == "keys": keysElements = [xmlElement]
            else: keysElements = xmlElement.getXmlElementListByName("keys", True)
            if keysElements:
                for keysElement in keysElements:
                    keyElements = keysElement.getXmlElementListByName("key", False)
                    for keyElement in keyElements:
                        bindStr = keyElement.getAttribute("bind")
                        if bindStr not in self._keys: self._keys[bindStr] = [ keyElement ] # or just the action (if any)
                        else: self._keys[bindStr].append(keyElement)

    def onKeyDown(self, evt, dc):
        handledkey = False
        action = ''
        # what key bind string is it
        bindStr = ''
        modifiers = evt.GetModifiers()
        #if modifiers
        if modifiers & wx.MOD_CONTROL: bindStr += "Ctrl+"
        if modifiers & wx.MOD_ALT: bindStr += "Alt+"
        if modifiers & wx.MOD_SHIFT: bindStr += "Shift+"
        if modifiers & wx.MOD_META: bindStr += "Meta+"
        if modifiers & wx.MOD_WIN: bindStr += "Win+"
        keyCode = evt.GetKeyCode() # book says check Uni first but its not working as I want
        keyCodeText = keycodes.get(keyCode)
        if keyCodeText:
            bindStr += keyCodeText
        else:
            uniKey = evt.GetUnicodeKey()
            if uniKey != 0: #None: #!= wx.WXK:   .WXK_NONE:
                strg = chr(uniKey) #wx.String(uniKey)
                bindStr += strg.upper() #strg.Upper()
            else:
                bindStr += 'Unrecognised:' + str(keyCode)

        xmlElementList = self._keys.get(bindStr)
        effectElement = None
        if xmlElementList:
            for keyBindElement in xmlElementList:
                conditionElement = keyBindElement.getXmlElementByName("condition", False)
                condition = True
                if conditionElement:
                    condition, actionTarget = self._interactions.matchCondition(conditionElement, None, None)
                if condition:
                    effectElement = keyBindElement.getXmlElementByName("effect", False)
                    if effectElement:
                        action = effectElement.getAttribute('action')
                    if not action:
                        handledkey = True
                    break
        if handledkey or action:
            self._interactions.cleanUpCurrentOperation(dc, operation=None, target=None)
            self._interactions.clearState(keepSelection=True)  # ? keepSelection = True ?
        if action and action != "default":
            actionXmlElement = None
            if effectElement: actionXmlElement = effectElement.getXmlElementByName("action")
            actionContext = ActionContext()
            actionContext.dc = dc
            actionContext.ptr = None #self._thisPtr
            actionContext.type = 'keyshortcut'
            actionContext.targets = self._interactions.selection().selection()
            actionContext.initSelectionSaved = self._interactions.canvas().diagram().saveObjectList(
                self._interactions.selection().selection(),
                indent=None, level=0, saveDefaults=True)
            resultStr = self._interactions.canvas().actions().InvokeAction(action, actionContext, actionXmlElement)
            handledkey = True
        if not handledkey:
            evt.Skip()
