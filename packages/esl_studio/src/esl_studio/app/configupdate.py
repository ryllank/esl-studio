#! /usr/bin/python

import sys
from collections import OrderedDict
if sys.platform == 'win32':
    import winreg

import wx

from . import utils as Utils
from .general import APPLICATION_VERSION_STRING, COMPATIBILITY_1_VERSION_STRING
from .general import APP_NAME, APP_VENDOR
from .config import Config
from .profile import Profile

class ConfigUpdate(object):

    Update1Methods = {} # As this is in ConfigUpdate and will contain ConfigUpdate static methods, must be assigned after the class has been defined (at the bottom)

    @staticmethod
    def setUpdate1Methods():
        ConfigUpdate.Update1Methods = {
        'Settings/history': ConfigUpdate.update1History,
        'Application/Open Submodels': 'Application/Open Subprograms',
        'Diagrams/SmartLink2Segments': ConfigUpdate.update1SmartLinks,
        'Diagrams/SmartLink3Segments': ConfigUpdate.update1SmartLinks,
        'Diagrams/SmartLinkStraight': ConfigUpdate.update1SmartLinks,
        'Advanced/BleepBeep': ConfigUpdate.update1BleepSound,
        'Advanced/BleepErrorSound': ConfigUpdate.update1BleepSound,
        'Advanced/BleepOff': ConfigUpdate.update1BleepSound,
        'Views/SimulationParameters/Help': 'Views/Simulation Parameters/Help',
        'Views/Properties/ExpandChildren': 'Views/Properties/Expand Property',
        'Profile/Profile Files': Profile.update1Profiles,
    }

    @staticmethod
    def getSystemConfigCurrentGroupEntries(systemConfig, configGroupPath, configPathValues):
        #print(">ConfigUpdate.getSystemConfigCurrentGroupEntries configGroupPath=" + configGroupPath +" systemPath=" + systemConfig.GetPath())
        gotEntry, itemEntry, indexEntries = systemConfig.GetFirstEntry()
        #print("-ConfigUpdate.getSystemConfigCurrentGroupEntries configGroupPath=" + configGroupPath + " first gotEntry="+str(gotEntry) +
        #      " itemEntry=" + itemEntry+" indexEntries="+str(indexEntries))
        while gotEntry:  # entries
            if Config.configUsesTypedValues and systemConfig.GetEntryType(itemEntry) == wx.ConfigBase.Type_Integer:
                value = systemConfig.ReadInt(itemEntry)
                valueType = "Int"
            else:
                valueStr = systemConfig.Read(itemEntry)
                value, valueType = Config.getValueFromTypedString(valueStr)
            if configGroupPath:
                path = configGroupPath + "/" + itemEntry
            else:
                path = itemEntry
            #print("*ConfigUpdate.getSystemConfigCurrentGroupEntries path="+path+": "+str(value)+" ["+valueType+"]")
            configPathValues[path] = value
            gotEntry, itemEntry, indexEntries = systemConfig.GetNextEntry(indexEntries)
        #print("-ConfigUpdate.getSystemConfigCurrentGroupEntries next gotEntry="+str(gotEntry) + " itemEntry=" + itemEntry+" indexEntries="+str(indexEntries))
        pass  # entries

    @staticmethod
    def getSystemConfigCurrentGroupEntitiesAndSubGroups(systemConfig, configPath, configPathValues):
        systemConfig.SetPath(Config.ROOT+configPath)  # set the current config (its "path" = current location) absolutely to the group
        #print(">ConfigUpdate.getSystemConfigCurrentGroupEntitiesAndSubGroups configPath="+configPath+" systemPath=" + systemConfig.GetPath())
        #if sys.platform != 'win32' or configPath != "": # skip toplevel entries for windows registry config
        ConfigUpdate.getSystemConfigCurrentGroupEntries(systemConfig, configPath, configPathValues)
        subGroupPaths = ConfigUpdate.getSystemConfigCurrentGroupSubGroups(systemConfig)
        #print("*ConfigUpdate.getSystemConfigCurrentGroupEntitiesAndSubGroups subGroupPaths="+str(subGroupPaths))
        for subGroupPath in subGroupPaths:
            if configPath:
                fullSubGroupPath = configPath + "/" + subGroupPath
            else:
                fullSubGroupPath = subGroupPath
            ConfigUpdate.getSystemConfigCurrentGroupEntitiesAndSubGroups(systemConfig, fullSubGroupPath, configPathValues)

    @staticmethod
    def getSystemConfigCurrentGroupSubGroups(systemConfig) -> list[str]:
        subGroupPaths = []
        gotGroup, itemGroup, indexGroups = systemConfig.GetFirstGroup()
        while gotGroup:
            subGroupPaths.append(itemGroup)
            gotGroup, itemGroup, indexGroups = systemConfig.GetNextGroup(indexGroups)
        return subGroupPaths

    @staticmethod
    def getCurrentSystemConfigAsPathValues() -> OrderedDict:
        configPathValues = OrderedDict()
        systemConfig = Config.getSystemConfig()
        #print(">ConfigUpdate.getCurrentSystemConfigAsPathValues initial systemPath=" + systemConfig.GetPath())
        configPath = ""
        if sys.platform == 'win32':
            #groups = ["Views", "Settings"]#, "Profile", "General", "Diagrams", "Application", "Advanced"]
            valueTuples, groups = ConfigUpdate.openRegConfig()
            for valueTuple in valueTuples:
                configPathValues[valueTuple[0]] = valueTuple[1]
        else:
            groups = [""]
        for group in groups:
            configPath = group
            ConfigUpdate.getSystemConfigCurrentGroupEntitiesAndSubGroups(systemConfig, configPath, configPathValues)
        #print("-ConfigUpdate.getCurrentSystemConfigAsPathValues after got all entries systemPath=" + systemConfig.GetPath())
        systemConfig.SetPath(Config.ROOT)
        #print("-ConfigUpdate.getCurrentSystemConfigAsPathValues after final set root systemPath=" + systemConfig.GetPath())
        return configPathValues

    @staticmethod
    def standardUpdate1Method(path, value):
        newPath = path
        newValue = value
        settingsInfo = Config.Settings.get(path)
        if settingsInfo:
            if settingsInfo.type == "Bool" and type(value) != bool:
                if value == 0 or value == '0':
                    newValue = False
                elif value == 1 or value == '1':
                    newValue = True
                else:
                    newValue = bool(value)
            elif settingsInfo.type == "Int" and type(value) != int:
                newValue = int(value)
        return newPath, newValue

    @staticmethod
    def update1History(path, value):
        newPath = path
        newValue = value.replace("|", Config.PATH_SEPARATOR)
        return newPath, newValue

    @staticmethod
    def update1SmartLinks(path, value):
        newPath = 'Diagrams/Smart Links'
        newValue = None
        if path == 'Diagrams/SmartLink2Segments' and value == True:
            newValue = 'smart2segments'
        elif path == 'Diagrams/SmartLink3Segments' and value == True:
            newValue = 'smart3segments'
        elif path == 'Diagrams/SmartLinkStraight' and value == True:
            newValue = 'straight'
        return newPath, newValue

    @staticmethod
    def update1BleepSound(path, value):
        newPath = 'Advanced/Bleep Sound'
        newValue = None
        if path == 'Advanced/BleepBeep' and value == True:
            newValue = 'Beep sound'
        elif path == 'Advanced/BleepErrorSound' and value == True:
            newValue = 'Error sound'
        elif path == 'Advanced/BleepOff' and value == True:
            newValue = 'Off'
        return newPath, newValue

    @staticmethod
    def updateConfigPathValues(updateLevel, preUpdateConfigPathValues) -> OrderedDict:
        resultUpdateConfigPathValues = OrderedDict()
        if updateLevel == 0:
            resultUpdateConfigPathValues = preUpdateConfigPathValues
        elif updateLevel == 1:
            for path, value in preUpdateConfigPathValues.items():
                updateMethod:any = ConfigUpdate.Update1Methods.get(path)
                if updateMethod:
                    if type(updateMethod) == str:  # just name to a newPath - value standard update
                        path = updateMethod
                        path, value = ConfigUpdate.standardUpdate1Method(path, value)
                    elif callable(updateMethod):
                        path, value = updateMethod(path, value) # update to newPath (if not None) and newValue (if not None)
                else:
                    path, value = ConfigUpdate.standardUpdate1Method(path, value)
                if path and value is not None:
                    resultUpdateConfigPathValues[path] = value
        return resultUpdateConfigPathValues

    @staticmethod
    def checkForConfigUpdateLevel(version:str) -> int:
        updateLevel = 0
        if not version:
            version = COMPATIBILITY_1_VERSION_STRING
        # Update from COMPATIBILITY_1 (1.2.0.30) version to present version
        versionComparison = Utils.compareVersions(version, APPLICATION_VERSION_STRING)
        msg = ""
        if versionComparison != "invalid" and versionComparison != "same":
            msg = "Loading configuration version " + version + " is " + versionComparison + " than this version of ESL-Studio (" + APPLICATION_VERSION_STRING + ")\n"
        if versionComparison in ["older", "(development) possibly older"]:
            updateLevel = 1
            msg += "- configuration will be updated\n"
        if msg:
            frame = wx.GetApp().frame()
            if frame:
                frame.control().appendMessage(msg)
            else:
                print(str(msg))
        return updateLevel

    @staticmethod
    def checkForUpdatedConfig(updateLevel, preUpdateConfigPathValues) -> OrderedDict:
        updatedConfigPathValues = OrderedDict()
        preUpdateConfigPathValues = ConfigUpdate.updateConfigPathValues(updateLevel, preUpdateConfigPathValues)
        for path in Config.Settings.keys():
            value = preUpdateConfigPathValues.get(path)
            if not value is None:
                updatedConfigPathValues[path] = value
        version = APPLICATION_VERSION_STRING
        updatedConfigPathValues["Settings/version"] = version # overwrite whatever may have been in
        return updatedConfigPathValues

    @staticmethod
    def removeOldSystemConfigEntries(currentSystemConfigPathValues, updatedConfigPathValues):
        systemConfig = Config.getSystemConfig()
        for path in currentSystemConfigPathValues:
            if path in Config.Settings:
                remove = False
            else:
                remove = True
            if remove:
                if path[0] != Config.ROOT:
                    path = Config.ROOT + path
                systemConfig.DeleteEntry(path)
                #print("*ConfigUpdate.removeOldSystemConfigEntries path=" + path)

    @staticmethod
    def checkForUpdatedSystemConfig():
        systemConfig = Config.getSystemConfig()
        version = systemConfig.Read("Settings/version")
        updateLevel = ConfigUpdate.checkForConfigUpdateLevel(version)
        if updateLevel > 0:
            currentSystemConfigPathValues = ConfigUpdate.getCurrentSystemConfigAsPathValues()
            updatedConfigPathValues = ConfigUpdate.checkForUpdatedConfig(updateLevel, currentSystemConfigPathValues)
            ConfigUpdate.removeOldSystemConfigEntries(currentSystemConfigPathValues, updatedConfigPathValues)
            for path, value in updatedConfigPathValues.items():
                settingsInfo = Config.Settings.get(path)
                if Config.configUsesTypedValues and settingsInfo.type == "Bool" and isinstance(value, int):
                    value = bool(value)
                Config.setValueForType(path, value, settingsInfo.type)

    @staticmethod
    def openRegConfig():
        ok  = True
        valueTuples = []
        subKeys = []

        hKey = 0
        try:
            hKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\"+APP_VENDOR+"\\"+APP_NAME)
        except:
            ok = False
        #print("-ConfigUpdate.openReg ok=" + str(ok)+" hKey=" + str(hKey))
        if ok:
            indx = 0
            while True:
                try:
                    valueName, value, valueType = winreg.EnumValue(hKey, indx)
                    #print("*ConfigUpdate.openReg valueName=" + valueName+" value="+str(value)+" valueType=" + str(valueType))
                    valueTuples.append((valueName, value, valueType))
                    indx += 1
                except:
                    break
            indx = 0
            while True:
                try:
                    subKeyName = winreg.EnumKey(hKey, indx)
                    #print("*ConfigUpdate.openReg subKeyName=" + subKeyName)
                    subKeys.append(subKeyName)
                    indx += 1
                except:
                    break
        winreg.CloseKey(hKey)
        #print("<ConfigUpdate.openReg valueTuples="+str(valueTuples)+" subKeys=" + str(subKeys)+">")
        return valueTuples, subKeys

ConfigUpdate.setUpdate1Methods()
