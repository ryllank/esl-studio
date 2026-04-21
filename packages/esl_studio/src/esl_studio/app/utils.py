#! /usr/bin/python

import os, os.path, sys
import importlib.metadata
import importlib.resources
import re
from typing import Callable

import wx
from wx.lib.newevent import NewCommandEvent
if sys.platform == "win32":
    import winsound

from .general import APP_BASEDIR_ENV, PROFILE_DEFAULT_DIR, RESOURCES_DEFAULT_DIR
from .general import (ESL_SOFTWARE_URL_ENV, ESL_STUDIO_URL_ENV, ESL_STUDIO_PAGES_ENV,
                      ESL_SOFTWARE_URL, ESL_STUDIO_URL, ESL_STUDIO_PAGES)

# Application base path (global) (typically up one from launch path - for when files are located in the distribution directory tree)
BASEDIR = ''
EXECUTION_DIR = ''
INTERNAL_DATA = ''

PATH_SEPARATOR = os.pathsep

Development_options = "" # May be used to specify options
    # "use_dev_website" (to convert websitev1 urls to websitev2)
    # "use_localhost8080" for localhost:8080
    # "use_extra_help_pages" to replace help_pages with extra/help_pages

# For queueFunctionCall
QueueFunctionCommandEvent, EVT_QUEUE_FUNCTION_COMMAND_EVENT = NewCommandEvent()
QueueFunctionIdCount = 0
QueueFunctionEventIdDict = {}

def isDistributionPackage():
    result = False
    try:
        package_version = importlib.metadata.version("esl_studio")
        if package_version:
            result = package_version
    except: pass
    return result

def isFrozen():
    result = getattr(sys, 'frozen', False)
    return result

def setEnvironment():
    global BASEDIR
    global EXECUTION_DIR
    global INTERNAL_DATA

    BASEDIR = os.getenv(APP_BASEDIR_ENV) # can impose a base directory - which may have profile/resources for "internal data".
    ##print("setEnvironment BASEDIR", BASEDIR)

    EXECUTION_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    ##print("setEnvironment EXECUTION_DIR", EXECUTION_DIR)

    if not INTERNAL_DATA:
        # See if INTERNAL_DATA has been provided via a specified BASEDIR - need both resources and profile at that level
        if BASEDIR:
            if os.path.isdir(os.path.join(BASEDIR, RESOURCES_DEFAULT_DIR)) and os.path.isdir(os.path.join(BASEDIR, PROFILE_DEFAULT_DIR)):
                INTERNAL_DATA = BASEDIR
                ##print("setEnvironment using 'ESLSTUDIODIR' BASEDIR "+BASEDIR+" for INTERNAL_DATA")

    if not INTERNAL_DATA:
        # See if installed distribution package data
        frozen = isFrozen()
        ##print("setEnvironment frozen="+str(frozen))
        if frozen: # Have frozen with PyInstaller
            if hasattr(sys, '_MEIPASS'):
                ##print("setEnvironment sys._MEIPASS", sys._MEIPASS)
                INTERNAL_DATA = sys._MEIPASS
                ##print("setEnvironment using PyInstaller path for INTERNAL_DATA")
            else:
                raise Exception("setEnvironment failed to find sys._MEIPASS (set by PyInstaller) when sys marked frozen")

    if not INTERNAL_DATA:
        distribution_package_version = isDistributionPackage()
        ##print("setEnvironment distribution_package_version=" + str(distribution_package_version))
        if distribution_package_version:
            package_data = importlib.resources.files("esl_studio")
            if package_data and os.path.isdir(os.path.join(package_data, RESOURCES_DEFAULT_DIR)):  # look for a resources directory by that name
                INTERNAL_DATA = package_data
                ##print("setEnvironment using package data for INTERNAL_DATA")

    if not INTERNAL_DATA:
        if EXECUTION_DIR: # must be launched directly in Python - look for resources directory under and at same level as execution dir
            ##print("setEnvironment trying to use EXECUTION_DIR "+EXECUTION_DIR+" for INTERNAL_DATA")
            if os.path.isdir(os.path.join(EXECUTION_DIR, RESOURCES_DEFAULT_DIR)):
                INTERNAL_DATA = EXECUTION_DIR
                ##print("setEnvironment using EXECUTION_DIR " + INTERNAL_DATA + " for INTERNAL_DATA")
            elif os.path.isdir(os.path.join(os.path.dirname(EXECUTION_DIR), RESOURCES_DEFAULT_DIR)):
                INTERNAL_DATA = os.path.dirname(EXECUTION_DIR)
                ##print("setEnvironment using up one from EXECUTION_DIR " + INTERNAL_DATA + " for INTERNAL_DATA")

    if not INTERNAL_DATA:
        ##print("setEnvironment trying to use module file path " + __file__ + " for INTERNAL_DATA")
        if os.path.isdir(os.path.join(os.path.dirname(os.path.dirname(__file__)), RESOURCES_DEFAULT_DIR)):
            INTERNAL_DATA = os.path.dirname(os.path.dirname(__file__))
            ##print("setEnvironment using up one from module file's dir " + INTERNAL_DATA + " for INTERNAL_DATA")

    if not BASEDIR: # assume we launched from a bin or some directory below the installation base directory
        BASEDIR = os.path.dirname(EXECUTION_DIR)
        # put into the internal environment
        os.environ[APP_BASEDIR_ENV] = BASEDIR

    ##print("setEnvironment INTERNAL_DATA", INTERNAL_DATA)
    return INTERNAL_DATA != ""

# Locate an ESL-Studio setup/profile file
# - looks as given (e.g. current dir wherever that may be), then basedir/profile, then basedir/ise/profile
def profileFile(filename, extn=''):
    filePath = ''
    if extn:
        filename = checkExt(filename, extn)
    filename = disEnvVarPath(filename)
    if os.path.isabs(filename):
        file = os.path.abspath(filename)
    else:
        file = os.path.join(defaultProfileDir(), filename)
    if os.path.isfile(file):
        filePath = file
    return filePath

# Looks under basedir/profile
def defaultProfileDir():
    global BASEDIR
    global INTERNAL_DATA
    dirPath = ''
    root = BASEDIR
    if INTERNAL_DATA:
        root = INTERNAL_DATA
    dir = os.path.join(root, PROFILE_DEFAULT_DIR)
    if os.path.isdir(dir):
        dirPath = os.path.abspath(dir)
    return dirPath

# Looks as given, then under basedir/elementicons
def elementIconFile(filename):
    filepath = profileFile(filename, extn='.png')
    if not filepath:
        filepath = profileFile("elementicons/"+filename, extn='.png')
    return filepath

# Looks as given, then under basedir/toolbaricons
def toolbarIconFile(filename):
    filepath = profileFile(filename, extn='.png')
    if not filepath:
        filepath = profileFile("toolbaricons/"+filename, extn='.png')
    return filepath

def getButtonBitmap(file):
    bitmap = None
    imagefile = toolbarIconFile(file)
    if imagefile:
        image = wx.Image(imagefile)
        bitmap = wx.Bitmap(image)
    return bitmap

# Looks as given, then under basedir/buttonicons
def buttonIconFile(filename):
    filepath = profileFile(filename, extn='.png')
    if not filepath:
        filepath = profileFile("buttonicons/"+filename, extn='.png')
    return filepath

# Looks under basedir/resources
def defaultResourceDir():
    global BASEDIR
    global INTERNAL_DATA
    dirPath = ''
    root = BASEDIR
    if INTERNAL_DATA:
        root = INTERNAL_DATA
    dir = os.path.join(root, RESOURCES_DEFAULT_DIR)
    if os.path.isdir(dir):
        dirPath = os.path.abspath(dir)
    return dirPath

def resourceFile(filename):
    global BASEDIR
    filePath = ''
    fileName = disEnvVarPath(filename)
    if os.path.isabs(fileName):
        file = os.path.abspath(filename)
    else:
        file = os.path.join(defaultResourceDir(), filename)
    if os.path.isfile(file):
        filePath = file
    return filePath

def docFile(filename):
    global EXECUTION_DIR
    global BASEDIR
    ##print("docFile BASEDIR", BASEDIR)
    ##print("docFile EXECUTION_DIR", EXECUTION_DIR)
    filePath = ''
    fileName = disEnvVarPath(filename)
    if os.path.isabs(fileName):
        file = os.path.abspath(filename)
        if os.path.isfile(file): filePath = file
    # Check in subdirectory docs (docs/install if running python direct) or legacy doc.
    docs_dir = "docs"
    if not isFrozen() and not isDistributionPackage():
        docs_dir = os.path.join(docs_dir, "install")
    if not filePath:  # look in  same level as execution directory
        file = os.path.join(os.path.join(os.path.dirname(EXECUTION_DIR), docs_dir), filename)
        ##print("docFile EXECUTION_DIR file", file)
        if os.path.isfile(file): filePath = file
    if not filePath:
        file = os.path.join(os.path.join(os.path.dirname(EXECUTION_DIR), "doc"), filename)
        if os.path.isfile(file): filePath = file
    if not filePath: # look under base directory
        file = os.path.join(os.path.join(BASEDIR, docs_dir), filename)
        if os.path.isfile(file): filePath = file
    if not filePath:
        file = os.path.join(os.path.join(BASEDIR, "doc"), filename)
        if os.path.isfile(file): filePath = file
    return filePath

# Checks if filepath has extension if not sets it (extn must have .).
def checkExt(filepath, extn):
    root_ext = os.path.splitext(filepath)
    if not root_ext[1]:
        filepath += extn
    return filepath

def relativise(filename, allowUp=0):
    result = filename
    cwd = os.getcwd()
    if filename == cwd or filename == cwd+'/' or filename == cwd+'\\':
        result = ""
    else:
        path = cwd
        if result.startswith(path) and len(result) - len(path) > 1:
            result = result[len(path) + 1:]
        elif allowUp == 1: # as far as we will go
            path, cwddir = os.path.split(cwd)
            if path and result.startswith(path) and len(result) - len(path) > 1:
                result = result[len(path) + 1:]
                result = os.pardir + os.sep + result
    return result

# Looks for a the expansion of the environment variable enVar (default ESLDIR) in front
# of a path, and if found replaces it with the use of the environment
# variable.
def environmentalise(filepath, envVar=APP_BASEDIR_ENV):
    newFilepath = filepath
    envDir = os.getenv(envVar)
    if envDir:
        substitute = False
        substitution = ''
        if sys.platform == 'win32':
            substitute = filepath.lower().startswith(envDir.lower())
            substitution = '%'+envVar+'%'
        else:
            substitute = filepath.startswith(envDir)
            substitution = '${'+envVar+'}'
        if substitute:
            newFilepath = substitution + filepath[len(envDir):]
    return newFilepath

def internalEnvvarSubstition(envvar):
    envvar_value = None
    if envvar == ESL_SOFTWARE_URL_ENV:
        envvar_value = ESL_SOFTWARE_URL
    elif envvar == ESL_STUDIO_URL_ENV:
        envvar_value = ESL_STUDIO_URL
    elif envvar == ESL_STUDIO_PAGES_ENV:
        envvar_value = ESL_STUDIO_PAGES
    elif envvar == 'ESLISEHOME': # legacy from old-ISE
        envvar_value = os.getenv('ESLDIR')
    return envvar_value

# Looks for a single environment variable at the beginning of a path,
# i.e. for a directory path, and if it finds one it expands the environment
# variable to give a full path and also converts \ to / or / to \ to suit
# the current operating system.
# It accepts the $... or $.../ or $...\ and $(...), and the %...% formats.
# And also ${...}
def disEnvVarPath(filepath, suppressDirChange=False):
    global BASEDIR
    newFilepath = filepath
    envstart = 0
    envend = -1
    keepend = False
    quoted = False
    if filepath.startswith('"') and filepath.endswith('"'):
        quoted = True
        filepath = filepath[1:-1]
        newFilepath = filepath
    if filepath.startswith('$('):
        envstart = 2
        envend = filepath.find(')')
    elif filepath.startswith('${'):
        envstart = 2
        envend = filepath.find('}')
    elif filepath.startswith('$'):
        envstart = 1
        envend = filepath.find('/')
        envend2 = filepath.find('\\')
        if envend > 0 and envend2 > 0:
            envend = min(envend, envend2)
            keepend = True
        elif envend < 0 and envend2 < 0:
            envend = len(filepath)
        else:
            envend = max(envend, envend2)
            keepend = True
    elif filepath.startswith('%'):
        envstart = 1
        envend = filepath.find('%', envstart)
    if envend > 0:
        envvar = filepath[envstart:envend]
        envvar_value = os.getenv(envvar)
        if not envvar_value:
            envvar_value = internalEnvvarSubstition(envvar)
        if not envvar_value and (envvar.upper() == APP_BASEDIR_ENV or envvar == '0'):
            envvar_value = BASEDIR
        if envvar_value:
            if not keepend:
                envend += 1
            newFilepath = envvar_value + filepath[envend:]
    if quoted:
        newFilepath = '"' + newFilepath + '"'
    if not suppressDirChange:
        if sys.platform == 'win32':
            newFilepath = newFilepath.replace('/', '\\')
        else:
            newFilepath = newFilepath.replace('\\', '/')
    return newFilepath

# Given an ESL file name it returns the full path reference for the file.
def eslFile(filepath):
    newFilepath = ''
    filepath = disEnvVarPath(filepath)
    filepath = checkExt(filepath, '.esl')
    if os.path.isfile(filepath):
        newFilepath = filepath
    else:
        esllib = os.getenv("ESLLIB")
        if esllib:
            esllibpaths = esllib.split(PATH_SEPARATOR)
            filebase = filepath
            for esllibpath in esllibpaths:
                filepath = os.path.join(esllibpath, filebase)
                if os.path.isfile(filepath):
                    newFilepath = filepath
                    break
    return newFilepath

# Remove ESLLIB path prefix on filepath (first found)
def deEslLibFile(filepath):
    newFilePath = filepath
    theEslLibPath = os.getenv('ESLLIB')
    if theEslLibPath:
        eslLibPaths = theEslLibPath.split(PATH_SEPARATOR)
        for eslLibPath in eslLibPaths:
            if eslLibPath:
                match = False
                eslExt = False
                if sys.platform == 'win32':
                    match = filepath.lower().startswith(eslLibPath.lower())
                    eslExt = filepath.lower().endswith('.esl')
                else:
                    match = filepath.startswith(eslLibPath)
                    eslExt = filepath.endswith('.esl')
                if match:
                    newFilePath = filepath[len(eslLibPath)+1:]
                    if eslExt:
                        newFilePath = newFilePath[:-4]
    return newFilePath

def indentation(indent, level):
    nl = '\n'
    ind = ''
    if indent is not None:
        for i in range(level): ind += indent
        ind2 = ind + indent
    else:
        nl = ''
        ind2 = ''
    return nl, ind, ind2

def checkDevelopmentUrl(url):
    new_url = url
    if Development_options:
        if Development_options.find("use_dev_website") != -1:
            new_url = new_url.replace("https://www.isimsimulation.com/", "http://dev.isimsimulation.com/", 1)
        if Development_options.find("use_localhost8080") != -1:
            new_url = new_url.replace("https://www.isimsimulation.com/", "http://localhost:8080/", 1)
        if Development_options.find("use_extra_help_pages") != -1:
            if new_url.find("/extra/help_pages/") == -1:
                new_url = new_url.replace("/help_pages/", "/extra/help_pages/", 1)
    return new_url

def openUrl(url):
    url = disEnvVarPath(url, suppressDirChange=True)
    url = checkDevelopmentUrl(url)
    wx.LaunchDefaultApplication(url)
    pass

def hardenPaths(designElementXml):
    # harden paths for images (src)
    imageXmlList = designElementXml.getXmlElementListByName("image", True)
    for imageXml in imageXmlList:
        src = imageXml.getAttribute("src")
        if src:
            # harden the path as if is an element icon
            newSrc = elementIconFile(src)
            if newSrc != src:
                imageXml.setAttribute("src", newSrc)

def libraryBaseName(lib):
    name = os.path.basename(lib)
    name = os.path.splitext(name)[0]
    name = name.upper()
    return name

def escapeText(text):
    result = text
    result = result.replace('\\', '#back/slash#')
    result = result.replace('\n', '\\n')
    result = result.replace('\r', '\\r')
    result = result.replace('\t', '\\t')
    result = result.replace('#back/slash#', '\\\\')
    return result

def unescapeText(text):
    result = text
    result = re.sub(r"\\\\",  '#back/slash#', result)
    result = re.sub(r'\\n', '\n', result)
    result = re.sub(r"\\r", '\r', result)
    result = re.sub(r"\\t", '\t', result)
    result = result.replace('#back/slash#', '\\')
    return result

def sanitiseFilename(filename, noSpaces=False):
    result = filename
    result = re.sub(r"[\\/:*\"?<>|'&]", "_", result)
    if noSpaces:
        result = result.replace(" ", "_")
    return result

def extendNew(thisList, newListOrThing):
    if isinstance(newListOrThing, list):
        if len(newListOrThing):
            newThings = filter(lambda thing: thing not in thisList, newListOrThing)
            thisList.extend(newThings)
    elif newListOrThing not in thisList:
        thisList.append(newListOrThing)

def getCaseInsensitive(orderedDict, name):
    result = None
    for key in orderedDict:
        if key.upper() == name.upper():
            result = orderedDict[key]
            break
    return result

def bleep():
    from .config import Config # cant import config at top due to dependency recursion
    configBleepSound = Config.getString("Advanced/Bleep Sound")
    if configBleepSound and configBleepSound != "Off":
        errCode = 0
        if configBleepSound == "Beep sound":
            if sys.platform == "linux":
                # Try emulating a beep with speaker-test.
                try:
                    errCode = os.system("( speaker-test -t sine -f 330 > /dev/null )& pid=$! ; sleep 0.5s ; kill -9 $pid")
                except:
                    errCode = 256
            elif sys.platform == "win32":
                # Try emulating a beep with winsound
                try:
                    winsound.Beep(330, 600)
                except:
                    errCode = 256
        if configBleepSound == "Error sound" or errCode != 0:
            if sys.platform == "linux": # it seems wx.Bell doesnt work in Linux
                # Try emulating a (slightly different) beep with speaker-test.
                try:
                    errCode = os.system("( speaker-test -t sine -f 380 > /dev/null )& pid=$! ; sleep 0.8s ; kill -9 $pid")
                except:
                    errCode = 256
            if sys.platform == "win32" or errCode != 0:
                wx.Bell()

def compareVersions(thisVersionStr, otherVersionStr):
    result = "invalid"
    versionPattern = r"(\d+)\.(\d+)\.(\d+)(\.(\d+))?"
    thisMatch = re.match(versionPattern, thisVersionStr)
    if thisMatch:
        otherMatch = re.match(versionPattern, otherVersionStr)
        if otherMatch:
            thisMajor = int(thisMatch.group(1))
            thisMinor = int(thisMatch.group(2))
            thisRevn = int(thisMatch.group(3))
            if thisMatch.group(5):
                thisBuild = int(thisMatch.group(5))
            else:
                thisBuild = 0 # this (application) must have been created by a development ESL-Studio - deemed old
            otherMajor = int(otherMatch.group(1))
            otherMinor = int(otherMatch.group(2))
            otherRevn = int(otherMatch.group(3))
            if otherMatch.group(5):
                otherBuild = int(otherMatch.group(5))
            else:
                otherBuild = 9999 # other (ESL-Studio) must be a development ESL-Studio - deemed new
            if (thisMajor == otherMajor and
                thisMinor == otherMinor and
                thisRevn == otherRevn):
                if thisBuild == otherBuild:
                    result = "same"
                elif thisBuild < otherBuild:
                    result = "older"
                    if thisBuild == 0: # application has a development version
                        if otherBuild == 9999: # ESL-Studio has a development version
                            result = "(development) possibly older" # wording for loading development application into development ESL-Studio
                        else:
                            result = "(development) possibly later"  # wording for loading development application into non-development ESL-Studio
                else:
                    result = "later"
            else:
                result = "later"
                if thisMajor != otherMajor:
                    result = "older" if thisMajor < otherMajor else "later"
                elif thisMinor != otherMinor:
                    result = "older" if thisMinor < otherMinor else "later"
                elif thisRevn != otherRevn:
                    result = "older" if thisRevn < otherRevn else "later"
    return result

def queueFunctionCall(function:Callable, argument=None):
    global QueueFunctionCommandEvent, EVT_QUEUE_FUNCTION_COMMAND_EVENT, QueueFunctionEventIdDict, QueueFunctionIdCount
    if function:
        #print("function="+str(function)+" type="+str(type(function)))
        eventId = QueueFunctionEventIdDict.get(function)
        if not eventId:
            QueueFunctionIdCount += 1
            eventId = QueueFunctionIdCount
            QueueFunctionEventIdDict[function] = eventId
        event = QueueFunctionCommandEvent(id=eventId)
        if argument is not None:
            event.SetClientObject(argument)
        def localHandler(evt):
            arg = evt.GetClientObject()
            if arg:
                if isinstance(arg, tuple):
                    function(*arg)
                else:
                    function(arg)
            else:
                function()
            pass
        app = wx.GetApp()
        app.Bind(EVT_QUEUE_FUNCTION_COMMAND_EVENT, localHandler, id=eventId)
        wx.QueueEvent(app, event)
