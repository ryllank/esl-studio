#! /usr/bin/python

import os.path
from collections import OrderedDict

from . import utils as Utils
from .general import PROFILE_PATHS_ENV, PROFILE_DEFAULT_DIR, PROFILE_FILE_EXT
from .config import Config

PROFILE_STEM = PROFILE_DEFAULT_DIR + os.sep

class Profile(object):

    StandardProfiles = OrderedDict({        # value list 0 is crude level of (un)importance - 1 most, 2 less so, 3 even less so
        PROFILE_STEM+'diagram-std-actions.eslprofile': [1],
        PROFILE_STEM+'diagram-std-interactions.eslprofile': [1],
        PROFILE_STEM+'diagram-std-keys.eslprofile': [1],
        PROFILE_STEM+'diagram-std-menus.eslprofile': [1],
        PROFILE_STEM+'diagram-theme-std.eslprofile': [1],
        PROFILE_STEM+'diagram-theme-std-generic-arrays.eslprofile': [2],
        PROFILE_STEM+'diagram-theme-xtra1-vectors.eslprofile': [3],
        PROFILE_STEM+'diagram-xtra1-drawing.eslprofile': [2],
        PROFILE_STEM+'esl-entities-std-definitions.eslprofile': [1],
        PROFILE_STEM+'esl-entities-std-elements.eslprofile': [1],
        PROFILE_STEM+'esl-entities-xtra1-arrays-matrices-vectors.eslprofile': [3],
        PROFILE_STEM+'esl-studio-std-commands.eslprofile': [1],
        PROFILE_STEM+'esl-studio-std-menubar.eslprofile': [1],
        PROFILE_STEM+'esl-studio-std-toolbar.eslprofile': [1],
    })

    Update1ProfileMapping = {
        PROFILE_STEM+'diagram-actions.eslprofile': PROFILE_STEM+'diagram-std-actions.eslprofile',
        PROFILE_STEM+'diagram-drawing.eslprofile': PROFILE_STEM+'diagram-xtra1-drawing.eslprofile',
        PROFILE_STEM+'diagram-interactions.eslprofile': PROFILE_STEM+'diagram-std-interactions.eslprofile',
        PROFILE_STEM+'diagram-keys.eslprofile': PROFILE_STEM+'diagram-std-keys.eslprofile',
        PROFILE_STEM+'diagram-menus.eslprofile': PROFILE_STEM+'diagram-std-menus.eslprofile',
        PROFILE_STEM+'diagram-theme-generic-arrays.eslprofile': [PROFILE_STEM+'diagram-theme-std-generic-arrays.eslprofile',  # since 1.2.0.30 - came in in 1.3.1.40
                                                            PROFILE_STEM+'diagram-theme-xtra1-vectors.eslprofile'],
        PROFILE_STEM+'diagram-theme.eslprofile': PROFILE_STEM+'diagram-theme-std.eslprofile',
        PROFILE_STEM+'esl-entities-definitions.eslprofile': PROFILE_STEM+'esl-entities-std-definitions.eslprofile',
        PROFILE_STEM+'esl-entities-elements.eslprofile': PROFILE_STEM+'esl-entities-std-elements.eslprofile',
        PROFILE_STEM+'esl-studio-commands.eslprofile': PROFILE_STEM+'esl-studio-std-commands.eslprofile',
        PROFILE_STEM+'esl-studio-menubar.eslprofile': PROFILE_STEM+'esl-studio-std-menubar.eslprofile',
        PROFILE_STEM+'esl-studio-toolbar.eslprofile': PROFILE_STEM+'esl-studio-std-toolbar.eslprofile',
        'if-diagram-theme-xtra1-vectors': [PROFILE_STEM+'esl-entities-xtra1-arrays-matrices-vectors.eslprofile'],
        'new-profiles': [PROFILE_STEM+'diagram-theme-std-generic-arrays.eslprofile',
                         PROFILE_STEM+'diagram-theme-xtra1-vectors.eslprofile',
                         PROFILE_STEM+'esl-entities-xtra1-arrays-matrices-vectors.eslprofile'],
    }

    # Get list of available profile files
    @staticmethod
    def availableProfileFiles():
        #print(">Profile.availableProfileFiles")
        profilePath = os.getenv(PROFILE_PATHS_ENV)
        profileDirs = []
        if profilePath:
            profileDirs = profilePath.split(Config.PATH_SEPARATOR)
        if PROFILE_DEFAULT_DIR not in profileDirs:
            profileDirs.insert(0, PROFILE_DEFAULT_DIR)
        profileFiles = []
        missingProfileDirs = []
        for profileDir in profileDirs:
            if profileDir != PROFILE_DEFAULT_DIR and not os.path.isdir(profileDir):
                missingProfileDirs.append(profileDir)
            else:
                scanProfileDir = profileDir
                if profileDir == PROFILE_DEFAULT_DIR:
                    scanProfileDir = Utils.defaultProfileDir()
                fileList = os.listdir(scanProfileDir)
                fileList.sort()
                for filename in fileList:
                    if filename.lower().endswith(PROFILE_FILE_EXT):
                        filePath = os.path.join(profileDir, filename)
                        if profileDir != PROFILE_DEFAULT_DIR:
                            filePath = os.path.abspath(filePath)
                            filePath = Utils.environmentalise(filePath)
                        profileFiles.append(filePath)
        #print("<Profile.update1Profiles profileFiles=" + str(profileFiles)+ " missingProfileDirs=" + str(missingProfileDirs))
        return profileFiles, missingProfileDirs

    @staticmethod
    def resetProfiles(currentProfileFiles):
        gotFiles = []
        profilePath = os.getenv(PROFILE_PATHS_ENV)
        profileDirs = []
        if profilePath:
            profileDirs = profilePath.split(Config.PATH_SEPARATOR)
        for profileFile in currentProfileFiles:
            dir = os.path.dirname(profileFile)
            if dir not in profileDirs and dir != PROFILE_DEFAULT_DIR:
                gotFiles.append(profileFile)
        resetProfileFiles, missingProfileDirs = Profile.availableProfileFiles()
        resetProfileFiles += gotFiles
        return resetProfileFiles

    @staticmethod
    def addSubstitution(substitution, newProfile):
        if substitution is not None:
            if isinstance(substitution, str):
                newProfile.append(substitution)
            elif isinstance(substitution, list):
                newProfile += substitution

    @staticmethod
    def update1Profiles(path, value):
        #print(">Profile.update1Profiles path=" + path + " value=" + value)
        newPath = path
        if not value:
            newProfile, missingProfileDirs = Profile.availableProfileFiles()
        else:
            configProfile1Files = value.split(Config.PATH_SEPARATOR)
            mapping = Profile.Update1ProfileMapping.copy()
            # remove from mapping those std profiles found to be removed in orig config
            for profile1File in Profile.Update1ProfileMapping:
                if profile1File not in configProfile1Files:
                    del mapping[profile1File]
            nrSubstitutions = len(mapping)
            # apply substitutions in orig config order
            newProfile = []
            nrSubstituted = 0
            for profile1File in configProfile1Files:
                substitution = mapping.get(profile1File)
                if substitution is not None:
                    Profile.addSubstitution(substitution, newProfile)
                    nrSubstituted += 1
                    if nrSubstituted >= nrSubstitutions:
                        if PROFILE_STEM+'diagram-theme-xtra1-vectors.eslprofile' in newProfile: # special case
                            substitution = Profile.Update1ProfileMapping.get(PROFILE_STEM+'diagram-theme-xtra1-vectors.eslprofile')
                            if substitution is not None:
                                Profile.addSubstitution(substitution, newProfile)
                        substitution = Profile.Update1ProfileMapping.get('new-profiles')
                        if substitution is not None:
                            for newProfileFile in substitution:
                                if newProfileFile not in newProfile:
                                    Profile.addSubstitution(newProfileFile, newProfile)
                else:
                    newProfile.append(profile1File)
        newValue = Config.PATH_SEPARATOR.join(newProfile)
        #print("<Profile.update1Profiles newPath=" + newPath + " newValue=" + newValue)
        return newPath, newValue
