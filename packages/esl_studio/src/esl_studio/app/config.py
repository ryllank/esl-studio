#! /usr/bin/python

import os, os.path
import re
import sys
import shutil
from collections import OrderedDict
import configparser as IniParser

import wx

from . import utils as Utils

class ConfigSettingsInfo():
    def __init__(self, type:str, default:any, show:bool, description:str):
        self.type:str = type    # one of "Bool"|"Int"|"String"
        self.default:any = default
        self.show:bool = show
        self.description:str = description

class Config(object):

    ROOT = "/"

    configUsesTypedValues = True    # If true system configuration methods can distinguish Int and String, but not Bool. If not all are String types
    if sys.platform == 'win32':
        configUsesTypedValues = True
        TEXT_EDITOR_DEFAULT = 'notepad'
        TEXT_EDITOR = TEXT_EDITOR_DEFAULT
    else:
        configUsesTypedValues = False
        TEXT_EDITOR_DEFAULT = 'gedit'
        TEXT_EDITOR = TEXT_EDITOR_DEFAULT
        TEXT_EDITOR_ALT = 'xed'
        TEXT_EDITOR_ALT2 = 'kate'
        if shutil.which(TEXT_EDITOR) == None:
            TEXT_EDITOR = TEXT_EDITOR_ALT
            if shutil.which(TEXT_EDITOR) == None:
                TEXT_EDITOR = TEXT_EDITOR_ALT2
                if shutil.which(TEXT_EDITOR) == None: # last alt fails - back to first choice
                    TEXT_EDITOR = TEXT_EDITOR_DEFAULT

    PATH_SEPARATOR = Utils.PATH_SEPARATOR

    # The set of block diagram properties which can be overridden by config options
    # values as set in the theme.
    BlockDiagramThemePropertyOptions = [
        True,               # Show Grid
        0,                  # Grid Snap
        "smart2segments"    # Smart Link
                            # put others below
    ]

    # Configuration settings - for OptionsDlg
    if sys.platform == 'win32':
        _bleepSoundDefault = "Error sound"
    else:
        _bleepSoundDefault = "Beep sound"

    Settings = OrderedDict(
        [   #key: path [ type(=Bool|Int|String'), default, show, description ]
            ('Settings/version', ConfigSettingsInfo('String', "", False, 'Version of application for this configuration data')),
            ('Settings/perspective', ConfigSettingsInfo('String', '', False, 'Layout (perspective) of AUI window (agw)')),
            ('Settings/wxperspective', ConfigSettingsInfo('String', '', False, 'Layout (perspective) of AUI window (wx)')),
            ('Settings/x', ConfigSettingsInfo('Int', -1, False, 'X coord of window')),
            ('Settings/y', ConfigSettingsInfo('Int', -1, False, 'Y coord of window')),
            ('Settings/width', ConfigSettingsInfo('Int', 600, False, 'Width of window')),
            ('Settings/height', ConfigSettingsInfo('Int', 400, False, 'Height of window')),
            ('Settings/maximised', ConfigSettingsInfo('Bool', False, False, 'Window is maximised')),
            ('Settings/cwd', ConfigSettingsInfo('String', '', False, 'Current working directory')),
            ('Settings/history', ConfigSettingsInfo('String', '', False, 'Recent applications history')),
            ('Settings/application', ConfigSettingsInfo('String', '', False, 'Last application')),

            ('Profile/Profile Files', ConfigSettingsInfo('String', '', False, 'Profile files to be used')),

            ('General/Splash', ConfigSettingsInfo('Bool', True, True, 'Show splash screen at start')),
            ('General/Open Last Application', ConfigSettingsInfo('Bool', True, True, 'Open the last application (if any) when start up')),
            ('General/Show Full Application Path', ConfigSettingsInfo('Bool', True, True, 'Show the full path in the window title when load an application')),
            ('General/Text Editor', ConfigSettingsInfo('String', TEXT_EDITOR, True, 'External text editor command (use %s) for file if not at end)')),

            ('Application/Open Simulation Parameters', ConfigSettingsInfo('Bool', False, True, 'Open the simulations parameters view when load an application')),
            ('Application/Open Subprograms', ConfigSettingsInfo('Bool', True, True, 'Open subprogram diagram pages when load an application')),
            ('Application/Open Packages', ConfigSettingsInfo('Bool', True, True, 'Open package pages when load an application')),
            ('Application/Open Code Pages', ConfigSettingsInfo('Bool', True, True, 'Open code pages when load an application')),
            ('Application/Open Setup View', ConfigSettingsInfo('Bool', False, True, 'Open the setup view when load an application')),

            ('Diagrams/Show Grid', ConfigSettingsInfo('Bool', True, True, 'Show the grid as set by the block diagram theme')),
            ('Diagrams/Grid Snap', ConfigSettingsInfo('Int', 0, True, 'Snap objects to a grid of this size')),
            ('Diagrams/Smart Links', ConfigSettingsInfo('String', 'smart2segments', True, 'Mode for drawing smart links')),

            ('Views/Package/Help', ConfigSettingsInfo('Bool', True, True, 'Show/hide package view help/description box (initial setting)')),
            ('Views/Simulation Parameters/Help', ConfigSettingsInfo('Bool', True, True, 'Show/hide simulation parameters view help/description box (initial setting)')),
            ('Views/Properties/Help', ConfigSettingsInfo('Bool', True, True, 'Show/hide properties panel help/description box (initial setting)')),
            ('Views/Properties/Expand Property', ConfigSettingsInfo('Bool', True, True, 'Automatically expand property to show its components when click in edit cell')),
            ('Views/Reset Layout', ConfigSettingsInfo('Bool', False, True, 'Reset the view windows layout to default (just when next start)')),
            #('Views/Package/HelpSize', [50, 'Size of package view help/description box'))

            ('Advanced/Diagnostics', ConfigSettingsInfo('Bool', False, True, 'Show/hide diagnostic messages')),
            ('Advanced/Bleep Sound', ConfigSettingsInfo('String', _bleepSoundDefault, True, '"Bleep" sound to make with important messages')),
            ('Advanced/AGWAUI', ConfigSettingsInfo('Bool', True, True, 'Use full (AGW) Advanced User Interface when next start')),
            ('Advanced/WXAUI', ConfigSettingsInfo('Bool', False, True, 'Use basic (WX) Advanced User Interface when next start')),
            ('Advanced/AUIAeroStyle', ConfigSettingsInfo('Bool', False, True, 'Use alternate (Aero-style) docking guides with full (AGW) AUI (when next start)')),
        ]
    )

    retainedSettings = []

    @staticmethod
    def getSystemConfig():
        systemConfig = wx.ConfigBase.Get()
        return systemConfig

    @staticmethod
    def setup():
        Config.getSystemConfig().SetExpandEnvVars(False)

    @staticmethod
    def getSettings(frame):
        # frame settings
        x = Config.getValue("Settings/x")
        y = Config.getValue("Settings/y")
        width = Config.getValue("Settings/width")
        height = Config.getValue("Settings/height")
        maximised = Config.getValue("Settings/maximised")
        return x, y, width, height, maximised

    @staticmethod
    def sanitisePerspective(perspective):
        new_perspective = perspective
        main_view_match = re.search(r'\|(name=MainView;.*)\|name=', new_perspective)
        if main_view_match:
            main_view_str = main_view_match.group(1)
            new_main_view_str = main_view_str
            new_main_view_str = main_view_str.replace("minimode=1;", "")
            new_main_view_str = new_main_view_str.replace("state=258;", "state=256;")
            if new_main_view_str != main_view_str:
                new_perspective = new_perspective.replace(main_view_str, new_main_view_str, 1)
        return new_perspective

    @staticmethod
    def getPerspective(frame, using_AGW_AUI):
        perspective = ""
        if using_AGW_AUI:
            perspective = Config.getValue("Settings/perspective")
        else:
            perspective = Config.getValue("Settings/wxperspective")
        perspective = Config.sanitisePerspective(perspective)
        return perspective

    @staticmethod
    def setSettings(frame):
        # frame settings
        pos = frame.GetPosition()
        size = frame.GetSize()
        isIconised = frame.IsIconized()
        maximised = frame.IsMaximized()
        # other settings (saved here)
        cwd = os.getcwd()
        history = frame.applicationHistory().getHistory()
        historyStr = Config.PATH_SEPARATOR.join(history)
        application = frame.application().filepath()
        if not isIconised and not maximised:
            Config.setValue("Settings/x", pos.x)
            Config.setValue("Settings/y", pos.y)
            Config.setValue("Settings/width", size.width)
            Config.setValue("Settings/height", size.height)
        Config.setValue("Settings/maximised", maximised)
        Config.setValue("Settings/cwd", cwd)
        Config.setValue("Settings/history", historyStr)
        Config.setValue("Settings/application", application)

    @staticmethod
    def setPerspective(frame, using_AGW_AUI):
        perspective = frame.auiManager().SavePerspective()
        if using_AGW_AUI:
            Config.setValue("Settings/perspective", perspective)
        else:
            Config.setValue("Settings/wxperspective", perspective)

    @staticmethod
    def setupBlockDiagramThemePropertyOptions(options):
        Config.BlockDiagramThemePropertyOptions[0] = options[0]
        Config.BlockDiagramThemePropertyOptions[1] = options[1]
        smartLinksDraw = options[2]
        # set as default values in Settings
        Config.Settings['Diagrams/Show Grid'].default = Config.BlockDiagramThemePropertyOptions[0]
        Config.Settings['Diagrams/Grid Snap'].default = Config.BlockDiagramThemePropertyOptions[1]
        Config.Settings['Diagrams/Smart Links'].default = smartLinksDraw

    @staticmethod
    def getBlockDiagramThemePropertyOptions():
        return Config.BlockDiagramThemePropertyOptions

    @staticmethod
    def getBlockDiagramPropertyOptions():
        options = [
            Config.getValue('Diagrams/Show Grid'),
            Config.getValue('Diagrams/Grid Snap'),
            Config.getValue('Diagrams/Smart Links')
        ]
        return options

    @staticmethod
    def getSetTypeFromValue(value: bool|int|str) -> str:
        setType = ""
        if isinstance(value, bool):
            setType = 'Bool'
        elif isinstance(value, int):
            setType = 'Int'
        elif isinstance(value, str):
            setType = 'String'
        return setType

    @staticmethod
    def getValueFromTypedString(valueStr:str) -> (bool|int|str, str):
        if valueStr.startswith("bool:"):
            valueType = "Bool"
            if valueStr == "bool:True": value = True
            elif valueStr == "bool:False": value = False
            else: value = bool(valueStr[len("bool:"):])
        elif valueStr.startswith("int:"):
            valueType = "Int"
            value = int(valueStr[len("int:"):]) # will raise exception itself if this is not actually an int
        else: # a string
            valueType = "String"
            value = valueStr
        return value, valueType

    @staticmethod
    def makeTypedStringForValue(value:bool|int|str, setType:str) -> str:
        if setType == "Bool":
            if value == True: value = "bool:True"
            elif value == False: value = "bool:False"
            else: value = "bool:" + str(value)
        elif setType == "Int":
            value = "int:" + str(value)
        elif setType == "String":
            pass # value unchanged
        else:
            value = None
        return value

    @staticmethod
    def getValueForType(path:str, setType:str) -> bool|int|str:
        config = Config.getSystemConfig()
        value = None
        if path[0] != Config.ROOT:
            path = Config.ROOT + path
        if config.HasEntry(path):
            if Config.configUsesTypedValues and setType == 'Int':
                value = config.ReadInt(path)
            else:
                valueStr = config.Read(path)
                value, valueType = Config.getValueFromTypedString(valueStr)
                if valueType != setType:
                    raise Exception("Config.getValueForType got invalid type - value=" + str(value) + " valType=" + valueType+" not setType=" + setType)
        return value

    @staticmethod
    def setValueForType(path:str, value:bool|int|str, setType:str):
        valueSetType = Config.getSetTypeFromValue(value)
        validValue = False
        if valueSetType == setType:
            config = Config.getSystemConfig()
            ok = False
            if path[0] != Config.ROOT:
                path = Config.ROOT + path
            if Config.configUsesTypedValues and setType == 'Int':
                ok = config.WriteInt(path, value)
            else:
                valueStr = Config.makeTypedStringForValue(value, setType)
                ok = config.Write(path, valueStr)
        else:
            raise Exception("Config.setValue inappropriate type - path="+str(path)+"("+str(setType)+") value="+str(value)+"("+str(valueSetType)+")")
        return ok

    @staticmethod
    def getValue(path:str) -> bool|int|str:
        value = None
        settingsInfo = Config.Settings.get(path)
        if settingsInfo:
            value = Config.getValueForType(path, settingsInfo.type)
            if value is None:
                value = settingsInfo.default
        return value

    @staticmethod
    def setValue(path:str, value:bool|int|str):
        ok = False
        settingsInfo = Config.Settings.get(path)
        if settingsInfo:
            ok = Config.setValueForType(path, value, settingsInfo.type)
        else:
            raise Exception("Config.setValue no setting info for path="+path)
        return ok

    @staticmethod
    def getBool(path:str) -> bool:
        value = Config.getValueForType(path, "Bool")
        if value is None:
            settingsInfo = Config.Settings.get(path)
            if settingsInfo:
                value = settingsInfo.default
        return value

    @staticmethod
    def setBool(path:str, value:bool):
        if type(value) == int:
            value = bool(value)
        ok = Config.setValueForType(path, value, "Bool")
        return ok

    @staticmethod
    def getInt(path:str) -> int:
        value = Config.getValueForType(path, "Int")
        if value is None:
            settingsInfo = Config.Settings.get(path)
            if settingsInfo:
                value = settingsInfo.default
        return value

    @staticmethod
    def setInt(path:str, value:int):
        ok = Config.setValueForType(path, value, "Int")
        return ok

    @staticmethod
    def getString(path:str) -> str:
        value = Config.getValueForType(path, "String")
        if value is None:
            settingsInfo = Config.Settings.get(path)
            if settingsInfo:
                value = settingsInfo.default
        return value

    @staticmethod
    def setString(path:str, value:str):
        ok = Config.setValueForType(path, value, "String")
        return ok

    @staticmethod
    def readRawConfigFilePathValues(configFile) -> OrderedDict:
        configPathValues = OrderedDict()
        if sys.version_info.minor >= 13:
            iniParser = IniParser.ConfigParser(allow_unnamed_section=True)
        else:
            iniParser = IniParser.ConfigParser()
        iniParser.optionxform = str
        iniParser.read(configFile)
        if iniParser.has_section(IniParser.UNNAMED_SECTION):
            for option, valueStr in iniParser.items(IniParser.UNNAMED_SECTION):
                value, valueType = Config.getValueFromTypedString(valueStr)
                configPathValues[option] = value
        items = iniParser.items()
        for section in iniParser.sections():
            if section != IniParser.UNNAMED_SECTION:
                for option, valueStr in iniParser.items(section):
                    key = section + "/" + option
                    value, valueType = Config.getValueFromTypedString(valueStr)
                    configPathValues[key] = value
        return configPathValues

    @staticmethod
    def loadConfigFile(configFile):
        from .configupdate import ConfigUpdate
        rawConfigPathValues = Config.readRawConfigFilePathValues(configFile)
        if rawConfigPathValues:
            version = rawConfigPathValues.get("Settings/version")
            updateLevel = ConfigUpdate.checkForConfigUpdateLevel(version)
            updatedConfigPathValues = ConfigUpdate.checkForUpdatedConfig(updateLevel, rawConfigPathValues)
            for path, value in updatedConfigPathValues.items():
                settingsInfo = Config.Settings.get(path)
                if settingsInfo.type == "String":
                    value = value.replace("<NL>", "\n")
                Config.setValue(path, value)

    @staticmethod
    def saveConfigFile(configFile, configPathValues):
        if sys.version_info.minor >= 13:
            iniParser = IniParser.ConfigParser(allow_unnamed_section=True)
        else:
            iniParser = IniParser.ConfigParser()
        iniParser.optionxform = str
        for path, value in configPathValues.items():
            settingsInfo = Config.Settings.get(path)
            if settingsInfo:
                valueStr = Config.makeTypedStringForValue(value, settingsInfo.type)
                if settingsInfo.type == "String":
                    valueStr = valueStr.replace("\n", "<NL>")
                sectionEndPos = path.rfind("/")
                section = path[:sectionEndPos]
                option = path[sectionEndPos+1:]
                if not iniParser.has_section(section):
                    iniParser.add_section(section)
                iniParser.set(section, option, valueStr)
        iniParser.write(open(configFile, "w"))

    @staticmethod
    def retainSettings():
        Config.retainedSettings = []
        for path in Config.Settings.keys():
            value = Config.getValue(path)
            Config.retainedSettings.append(value)

    @staticmethod
    def restoreRetainedSettings():
        i = 0
        for path in Config.Settings.keys():
            value = Config.retainedSettings[i]
            i += 1
            Config.setValue(path, value)

    @staticmethod
    def closeDown(saveSettings, frame, using_AGW_AUI):
        if not saveSettings:
            Config.restoreRetainedSettings()
        else:
            Config.setSettings(frame)
            Config.setPerspective(frame, using_AGW_AUI)
        Config.getSystemConfig().Flush()
