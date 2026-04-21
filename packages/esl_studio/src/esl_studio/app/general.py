#! /usr/bin/python

from .. import * # imports package's __init__.py exports (specifically version and build_time)

APPLICATION_VERSION_STRING =  version # "1.3.1"
APPLICATION_BUILD_DATE = build_time

COMPATIBILITY_1_VERSION_STRING = "1.2.0.30"     # as for ESL v8.3.0.1

APP_NAME = 'ESL-Studio'
APP_TITLE = 'ESL-Studio'
APP_VENDOR = 'ESL Software'

APP_COPYRIGHT = "Copyright (c) 2026 Ryllan J E Kraft"       # See also (as text in) ./LICENSE, ./README.md and./src/__init__.py

# Environment variables for the URLs.
ESL_SOFTWARE_URL_ENV = 'ESL_SOFTWARE_URL'
ESL_STUDIO_URL_ENV = 'ESL_STUDIO_URL'
ESL_STUDIO_PAGES_ENV = 'ESL_STUDIO_PAGES'

# Defaults for the URLs
ESL_SOFTWARE_URL = 'https://www.isimsimulation.com'
ESL_STUDIO_URL = 'https://ryllank.github.io/esl-studio'     # See also  ./pyproject.toml (Homepage)
ESL_STUDIO_PAGES = ESL_STUDIO_URL + "/guides"
if APPLICATION_VERSION_STRING.startswith("1."):             # To cater for before the v2 documentation is in place
    ESL_STUDIO_URL = ESL_SOFTWARE_URL + "/help_pages/esl-studio"
    ESL_STUDIO_PAGES = ESL_SOFTWARE_URL + "/help_pages/esl-studio"

APP_WEBSITE = ESL_SOFTWARE_URL

APP_URL = ESL_STUDIO_URL
APP_DESCR = "Integrated development environment used primarily for creating ESL simulations."
APP_DESCRIPTION = 'An integrated development environment used primarily for creating\n\
ESL simulations using block diagrams and ESL code.'

APP_AUTHOR = "Ryllan J E Kraft"
APP_AUTHOR_EMAIL = "Ryllan.Kraft@gmail.com>"

APP_LICENSE = "MIT License (SPDX-License-Identifier: MIT)"

APP_BASEDIR_ENV = 'ESLSTUDIODIR'

# Application files default extension
APP_FILE_EXT = '.eslstudio'
# Profile files are looked for on an environment variable path (else local profile directory)
PROFILE_PATHS_ENV = 'ESLSTUDIOPROFILE'
# Default profile directory
PROFILE_DEFAULT_DIR = 'profile'
# Profile files extension
PROFILE_FILE_EXT = '.eslprofile'
# Default resources directory
RESOURCES_DEFAULT_DIR = 'resources'
