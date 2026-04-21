; ESL-Studio installation script

;--------------------------------
; Build environment
;--------------------------------

!define PRODUCT_NAME ESL-Studio
!define PRODUCT_PUBLISHER "ESL Software"
!define ISIM_PRODUCT_PUBLISHER "ISIM International Simulation Limited"
!define PRODUCT_DESCRIPTION "ESL-Studio installation package"
!define PRODUCT_ROOT "ESL Software"
!define PRODUCT_WEB_SITE "https://www.isimsimulation.com"
!define PRODUCT_CONTACT "e-mail: support@isimsimulation.com"
!define PRODUCT_VERSION $%PRODUCT_VERSION%
!define PRODUCT_VERSION_MAJOR $%PRODUCT_VERSION_MAJOR%
!define PRODUCT_VERSION_MINOR $%PRODUCT_VERSION_MINOR%
!define TARGET $%_target%
!define SRC $%_SRC%
!define NAME ${PRODUCT_NAME}-${PRODUCT_VERSION}
!define DEFAULT_INSTDIR_BASE "${PRODUCT_ROOT}\esl-studio"
!define PRODUCT_UNINST_BASE "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
!define PRODUCT_UNINST_KEY "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define ENVIRONMENT_KEY "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
!define ESLSTUDIO_INSTALLED_KEY "SOFTWARE\${PRODUCT_PUBLISHER}\ESL-Studio" ; No need to say solo
!define ISIM_ESLSTUDIO_INSTALLED_KEY "SOFTWARE\${ISIM_PRODUCT_PUBLISHER}\ESL-Studio" ; No need to say solo
!define ESLPRO_INSTALLED_KEY "SOFTWARE\${PRODUCT_PUBLISHER}\ESL-Pro"
!define ISIM_ESLPRO_INSTALLED_KEY "SOFTWARE\${ISIM_PRODUCT_PUBLISHER}\ESL-Pro"
!define ESLLITE_INSTALLED_KEY "SOFTWARE\${PRODUCT_PUBLISHER}\ESL-Lite"
!define ISIM_ESLLITE_INSTALLED_KEY "SOFTWARE\${ISIM_PRODUCT_PUBLISHER}\ESL-Lite"
!define README_FILE "$INSTDIR\docs\readme.txt"
!define ESLSTUDIO_SOLO_FILE_ASSOCIATION "ESL-Studio (solo) application file" ; Must be same in all installers using it
!define ESL_ESLSTUDIO_FILE_ASSOCIATION "$Got_ESL ESL-Studio application file"
!define ESLSTUDIO_SOLO_LINK_NAME "ESL-Studio (solo)"
!define ESL_ESLSTUDIO_LINK_NAME "$Got_ESL ESL-Studio"
!define UNINSTALL_LINK_NAME "Uninstall ESL-Studio" ; No need to say solo
!define UNINSTALL_LINK_EXE "Uninstall-ESL-Studio"

; Texts for MUI
!define NL "$\r$\n"
; for Welcome Page
!define EXITBUTTONTEXT "Exit"
!define WELCOMEPAGE_GUIDANCE_TEXT_DEFAULT \
"This will guide you through the installation of ${NAME}."
!define WELCOMEPAGE_GUIDANCE_TEXT_CANNOT_INSTALL \
"Cannot do the installation of ${NAME} at this time."
!define WELCOMEPAGE_RECOMMENDATION_TEXT_DEFAULT \
"${NL}${NL}It is recommended that you close all other applications before installing. This will make it possible to update relevant system files without having to reboot your computer."
!define AND_FOUND_TEXT " and found "
!define ESLSTUDIO_COMPONENT_TEXT_CAN_HAVE \
"which can have an ESL-Studio component"
!define ESLSTUDIO_COMPONENT_TEXT_HAS \
"which has an ESL-Studio-$Got_ESL_ESLStudio_Version component"
!define CAN_INSTALL_IN_ESL_TEXT \
"$Got_ESL-$Got_ESL_Version $InESL_ESLStudioComponentText"
!define CANNOT_INSTALL_IN_ESL_TEXT \
"$Got_ESL-$Got_ESL_Version which cannot have an ESL-Studio component"
!define PREVIOUS_SOLO_NOT_REPLACEABLE_HIGHER_VERSION_TEXT \
" (higher version than this - will need to uninstall to replace)"
!define PREVIOUS_SOLO_NOT_REPLACEABLE_INVALID_VERSION_TEXT \
" (an invalid version - will need to uninstall to replace)"
!define PREVIOUS_SOLO_TEXT \
"a previous installation of ${PRODUCT_NAME} (solo) $GotESLStudio_Version$PreviousSoloNotReplaceableText"
!define CANNOT_INSTALL_SOLO_TEXT_HIGHER_VERSION \
"${NL}${NL}The previously installed ${NAME} has a higher version, so this installation cannot continue.${NL}${NL}You should explicitly uninstall it before re-running this installer."
!define CANNOT_INSTALL_SOLO_TEXT_INVALID_VERSION \
"${NL}${NL}The previously installed ${NAME} has an invalid version, so this installation cannot continue.${NL}${NL}You should explicitly uninstall it before re-running this installer."
!define WELCOMEPAGE_TEXT_ADDITIONAL_TEXT \
"${NL}${NL}Found $CanInstallInESLText$CannotInstallInESLText$AndFound$PreviousSoloText.$CannotInstallSoloText"
!define WELCOMEPAGE_CLICK_TEXT_DEFAULT \
"Click Next to continue"
!define WELCOMEPAGE_CLICK_TEXT_TO_EXIT \
"Click Exit to quit the installation"
; for AskIfDoInstallInESL MessageBox
!define ESLSTUDIO_REPLACEMENT_TEXT \
" to replace its current ESL-Studio-$Got_ESL_ESLStudio_Version component"
!define ASK_SELECTION_TEXT_CAN_SOLO \
"${NL}${NL}Select Yes to install in ESL, No to install ESL-Studio solo (independent from ESL installation) or Cancel to exit the installation."
!define ASK_SELECTION_TEXT_CANNOT_SOLO \
"${NL}${NL}Note: To install ESL-Studio solo you need to Cancel and uninstall the previous ESL-Studio solo explicitly.${NL}${NL}Select OK to install in ESL or Cancel to exit the installation."
!define ASK_ESL_TEXT \
"Found $CanInstallInESLText.${NL}${NL}Do you want to install this ${NAME} in the $Got_ESL-$Got_ESL_Version installation$ESLStudioReplacementText?$AskSelectionText"
!define ASK_QUIT_TEXT \
"Are you sure you want to quit ${NAME} Setup"
; for Components Page
!define INSTALLBUTTONTEXT "&INSTALL"
!define COMPONENTSPAGE_TEXT_TOP_ADDITIONAL_SOLO \
" for ESL-Studio (solo)."
!define COMPONENTSPAGE_TEXT_TOP_ADDITIONAL_IN_ESL \
" into ESL."
!define COMPONENTSPAGE_CLICK_TEXT_DEFAULT \
"${NL}Click Next to continue"
!define COMPONENTSPAGE_CLICK_TEXT_INSTALL \
"${NL}Click INSTALL to start the installation" #works - on new line (but not spaced out as well as I'd like)
; for Directory Page (via DirText)
!define DIRTEXT_TEXT \
"Installing ${NAME} in the destination folder below. To install in a different folder, click Browse and select another folder.$DirTextAdditionalText$_CLICK"
!define DIRTEXT_ADDITIONAL_TEXT_DEFAULT \
"${NL}${NL}" ; Have blank line before standard Click text
!define DIRTEXT_ADDITIONAL_TEXT_LOCATION \
"${NL}Note: This has been initially set to the same location $\"$GotESLStudio_InstallLocation$\" as the previous installation ($PreviousVersionStatus version $GotESLStudio_Version) which it will replace.${NL}${NL}" ; Tried having a blank line before this, but wouldn't fit on dialog

;--------------------------------
; General
;--------------------------------

Name ${NAME}
OutFile ${TARGET}
;;; SetCompressor /SOLID LZMA

RequestExecutionLevel admin	# if not granted installation just doesn't go ahead

BrandingText " " # remove Nullsoft watermark

DirText \
"${DIRTEXT_TEXT}" \
	"" "" ""

InstallButtonText ${INSTALLBUTTONTEXT} # Want it to look more important than just Install (but can't be bigger)

;--------------------------------
; Includes
;--------------------------------

!include "LogicLib.nsh"
!include "x64.nsh"
!include "FileFunc.nsh"
!include "MUI2.nsh"
!include "EslNsisUtils.nsh"

;--------------------------------
; Variables
;--------------------------------

Var StartMenuFolder
Var DateTime
Var ISIM_ESLSTUDIO
Var ISIM_ESL
Var GotESLStudio_Installed
Var GotESLStudio_InstallLocation
Var GotESLStudio_Version
Var GotESLPro_Installed
Var GotESLLite_Installed
Var Got_ESL_ESLStudio_Version
Var Got_ESL
Var Got_ESL_Version
Var Got_ESL_StartMenuFolder
Var Got_ESLDIR
Var CanInstallInESLText
Var CannotInstallInESLText
Var InESL_ESLStudioComponentText
Var PreviousSoloText
Var PreviousSoloNotReplaceableText
Var CannotInstallSoloText
Var AndFound
Var DoInstallInESL
Var PreviousVersionStatus
Var UninstallCmd
Var WelcomePageGuidanceText
Var WelcomePageRecommendationText
Var WelcomePageTextAdditionalText
Var WelcomePageClickText
Var AskESLText
Var ESLStudioReplacementText
Var AskSelectionText
Var ComponentsPageTextTopAdditionalText
Var ComponentsPageClickText
Var DirTextAdditionalText

;--------------------------------
; MUI Settings
;--------------------------------

!define MUI_COMPONENTSPAGE_SMALLDESC
!define MUI_ABORTWARNING
!define MUI_ICON "esl.ico"
!define MUI_UNICON "esl.ico"

!define MUI_FINISHPAGE_SHOWREADME "${README_FILE}"
!define MUI_FINISHPAGE_NOAUTOCLOSE
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION "OpenReadMe"

!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_RIGHT
!define MUI_HEADERIMAGE_BITMAP "header.bmp"

!define MUI_WELCOMEFINISHPAGE_BITMAP "sidebar.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "sidebar.bmp"

!define MUI_UNFINISHPAGE_NOAUTOCLOSE

;--------------------------------
; Pages
;--------------------------------

; Welcome Page
!define MUI_WELCOMEPAGE_TEXT \
"$WelcomePageGuidanceText$WelcomePageRecommendationText$WelcomePageTextAdditionalText${NL}${NL}$WelcomePageClickText"
!define MUI_PAGE_CUSTOMFUNCTION_PRE WelcomePagePreCallback
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE WelcomePageLeaveCallback
!insertmacro MUI_PAGE_WELCOME

; License Page
!insertmacro MUI_PAGE_LICENSE "ESLStudio-Licence.rtf"

; Components Page
!define MUI_COMPONENTSPAGE_TEXT_TOP "Check the components you want to install and uncheck the components you don't want to install$ComponentsPageTextTopAdditionalText$ComponentsPageClickText"
!define MUI_PAGE_CUSTOMFUNCTION_PRE ComponentsPagePreCallback
!insertmacro MUI_PAGE_COMPONENTS

; Directory Page
!define MUI_PAGE_CUSTOMFUNCTION_PRE DirectoryPagePreCallback
!insertmacro MUI_PAGE_DIRECTORY

; Start Menu Page
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKLM"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "SOFTWARE\${PRODUCT_PUBLISHER}\${PRODUCT_NAME}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "${PRODUCT_NAME}"
!define MUI_PAGE_CUSTOMFUNCTION_PRE StartMenuPagePreCallback
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE UninstallPreviousInstallation ; StartMenuPageLeaveCallback
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

; Install Files Page
##!define MUI_PAGE_CUSTOMFUNCTION_PRE InstFilesPagePreCallback
!insertmacro MUI_PAGE_INSTFILES

; Finish Page
##!define MUI_PAGE_CUSTOMFUNCTION_PRE FinishPagePreCallback
!insertmacro MUI_PAGE_FINISH

; Uninstall pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages
;--------------------------------

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Functions
;--------------------------------

Function .onInit
#	# Try a splash
#	InitPluginsDir
#	File "/oname=$PluginsDir\spltmp.bmp" "splash.bmp"
#	advsplash::show 2000 500 200 -1 $PluginsDir\spltmp
#	# Delay, FadeIn, FadeOut, KeyColor
#	Pop $0 ; $0 has '1' if the user closed the splash screen early,
#	; '0' if everything closed normally, and '-1' if some error occurred.

	SetShellVarContext all
	${If} ${RunningX64}
		StrCpy $INSTDIR "$PROGRAMFILES64\${DEFAULT_INSTDIR_BASE}"
		SetRegView 64
	${Else}
		StrCpy $INSTDIR "$PROGRAMFILES\${DEFAULT_INSTDIR_BASE}"
	${EndIf}

	Call CheckInstallations

	Call SeeIfCanInstallInESL

	Call SetupForWelcomePage

##	MessageBox MB_OK "<.onInit:$\n\
##WelcomePageTextAdditionalText=$WelcomePageTextAdditionalText"
FunctionEnd

Function un.onInit ; Doing solo (standalone) uninstall
	SetShellVarContext all
	${If} ${RunningX64}
		SetRegView 64
	${EndIf}
	Call un.CheckInstallations
FunctionEnd

Function CheckInstallations
	StrCpy $ISIM_ESLSTUDIO ""
	ReadRegStr $GotESLStudio_Installed HKLM "${ESLSTUDIO_INSTALLED_KEY}" "Installed"
	${If} $GotESLStudio_Installed == ""
		ReadRegStr $GotESLStudio_Installed HKLM "${ISIM_ESLSTUDIO_INSTALLED_KEY}" "Installed"
		StrCpy $ISIM_ESLSTUDIO "TRUE"
	${EndIf}
	${If} $GotESLStudio_Installed != ""
		${If} $ISIM_ESLSTUDIO == ""
	        ReadRegStr $GotESLStudio_Version HKLM "${ESLSTUDIO_INSTALLED_KEY}" "Version"
		${Else}
	        ReadRegStr $GotESLStudio_Version HKLM "${ISIM_ESLSTUDIO_INSTALLED_KEY}" "Version"
		${EndIf}
	    ReadRegStr $GotESLStudio_InstallLocation HKLM "${PRODUCT_UNINST_KEY}" "InstallLocation"
    ${EndIf}

	StrCpy $ISIM_ESL ""
	ReadRegStr $GotESLPro_Installed HKLM "${ESLPRO_INSTALLED_KEY}" "Installed"
	${If} $GotESLPro_Installed == ""
		ReadRegStr $GotESLPro_Installed HKLM "${ISIM_ESLPRO_INSTALLED_KEY}" "Installed"
		StrCpy $ISIM_ESL "TRUE"
	${EndIf}
	ReadRegStr $GotESLLite_Installed HKLM "${ESLLITE_INSTALLED_KEY}" "Installed"
	${If} $GotESLLite_Installed == ""
		ReadRegStr $GotESLLite_Installed HKLM "${ISIM_ESLLITE_INSTALLED_KEY}" "Installed"
		StrCpy $ISIM_ESL "TRUE"
	${EndIf}
	ReadRegStr $Got_ESLDIR HKLM "${ENVIRONMENT_KEY}" "ESLDIR"
	${If} $GotESLPro_Installed != ""
		StrCpy $Got_ESL "ESL-Pro"
		${If} $ISIM_ESL == ""
			ReadRegStr $Got_ESL_Version HKLM "${ESLPRO_INSTALLED_KEY}" "Version"
			ReadRegStr $Got_ESL_StartMenuFolder HKLM "${ESLPRO_INSTALLED_KEY}" "Start Menu Folder"
			ReadRegStr $Got_ESL_ESLStudio_Version HKLM "SOFTWARE\${PRODUCT_PUBLISHER}\ESL-Pro" "ESL-Studio-Version"
        ${Else}
			ReadRegStr $Got_ESL_Version HKLM "${ISIM_ESLPRO_INSTALLED_KEY}" "Version"
			ReadRegStr $Got_ESL_StartMenuFolder HKLM "${ISIM_ESLPRO_INSTALLED_KEY}" "Start Menu Folder"
			ReadRegStr $Got_ESL_ESLStudio_Version HKLM "SOFTWARE\${ISIM_PRODUCT_PUBLISHER}\ESL-Pro" "ESL-Studio-Version"
		${EndIf}
	${ElseIf} $GotESLLite_Installed != ""
		StrCpy $Got_ESL "ESL-Lite"
		${If} $ISIM_ESL == ""
			ReadRegStr $Got_ESL_Version HKLM "${ESLLITE_INSTALLED_KEY}" "Version"
			ReadRegStr $Got_ESL_StartMenuFolder HKLM "${ESLLITE_INSTALLED_KEY}" "Start Menu Folder"
			ReadRegStr $Got_ESL_ESLStudio_Version HKLM "SOFTWARE\${PRODUCT_PUBLISHER}\ESL-Lite" "ESL-Studio-Version"
		${Else}
			ReadRegStr $Got_ESL_Version HKLM "${ISIM_ESLLITE_INSTALLED_KEY}" "Version"
			ReadRegStr $Got_ESL_StartMenuFolder HKLM "${ISIM_ESLLITE_INSTALLED_KEY}" "Start Menu Folder"
			ReadRegStr $Got_ESL_ESLStudio_Version HKLM "SOFTWARE\${ISIM_PRODUCT_PUBLISHER}\ESL-Lite" "ESL-Studio-Version"
		${EndIf}
	${EndIf}
	${If} $Got_ESL_ESLStudio_Version == ""
		${If} $Got_ESLDIR != ""
			${If} ${FileExists} "$Got_ESLDIR\esl-studio\bin"
				# Must be on the original ESL v8.3.0.1 which originally contained 1.2.0.30
				## Note to self: when install in ESL have to set ESL-Studio-Version etc
				StrCpy $Got_ESL_ESLStudio_Version "1.2.0.30"
			${EndIf}
		${EndIf}
	${EndIf}
##	MessageBox MB_OK "<CheckInstallations:$\n\
##GotESLStudio_Installed=$GotESLStudio_Installed$\n\
##GotESLStudio_Version=$GotESLStudio_Version$\n\
##GotESLStudio_InstallLocation=$GotESLStudio_InstallLocation$\n\
##ISIM_ESLSTUDIO=$ISIM_ESLSTUDIO$\n\
##Got_ESL=$Got_ESL$\n\
##Got_ESL_Version=$Got_ESL_Version$\n\
##Got_ESL_StartMenuFolder=$Got_ESL_StartMenuFolder$\n\
##Got_ESL_ESLStudio_Version=$Got_ESL_ESLStudio_Version$\n\
##Got_ESLDIR=$Got_ESLDIR$\n\
##ISIM_ESL=$ISIM_ESL"
FunctionEnd

Function un.CheckInstallations ; subset of CheckInstallations ; Doing solo (standalone) uninstall
#	ReadRegStr $GotESLStudio_Installed HKLM "${ESLSTUDIO_INSTALLED_KEY}" "Installed"
#	ReadRegStr $GotESLStudio_Version HKLM "${ESLSTUDIO_INSTALLED_KEY}" "Version"
#	ReadRegStr $GotESLStudio_InstallLocation HKLM "${PRODUCT_UNINST_KEY}" "InstallLocation"
	${If} $ISIM_ESL == ""
		ReadRegStr $GotESLPro_Installed HKLM "${ESLPRO_INSTALLED_KEY}" "Installed"
		ReadRegStr $GotESLLite_Installed HKLM "${ESLLITE_INSTALLED_KEY}" "Installed"
	${Else}
		ReadRegStr $GotESLPro_Installed HKLM "${ISIM_ESLPRO_INSTALLED_KEY}" "Installed"
		ReadRegStr $GotESLLite_Installed HKLM "${ISIM_ESLLITE_INSTALLED_KEY}" "Installed"
	${EndIf}
	ReadRegStr $Got_ESLDIR HKLM "${ENVIRONMENT_KEY}" "ESLDIR"
	${If} $GotESLPro_Installed != ""
		StrCpy $Got_ESL "ESL-Pro"
#		ReadRegStr $Got_ESL_Version HKLM "${ESLPRO_INSTALLED_KEY}" "Version"
#		ReadRegStr $Got_ESL_StartMenuFolder HKLM "${ESLPRO_INSTALLED_KEY}" "Start Menu Folder"
		${If} $ISIM_ESL == ""
			ReadRegStr $Got_ESL_ESLStudio_Version HKLM "SOFTWARE\${PRODUCT_PUBLISHER}\ESL-Pro" "ESL-Studio-Version"
		${Else}
			ReadRegStr $Got_ESL_ESLStudio_Version HKLM "SOFTWARE\${ISIM_PRODUCT_PUBLISHER}\ESL-Pro" "ESL-Studio-Version"
		${EndIf}
	${ElseIf} $GotESLLite_Installed != ""
		StrCpy $Got_ESL "ESL-Lite"
#		ReadRegStr $Got_ESL_Version HKLM "${ESLLITE_INSTALLED_KEY}" "Version"
#		ReadRegStr $Got_ESL_StartMenuFolder HKLM "${ESLLITE_INSTALLED_KEY}" "Start Menu Folder"
		${If} $ISIM_ESL == ""
			ReadRegStr $Got_ESL_ESLStudio_Version HKLM "SOFTWARE\${PRODUCT_PUBLISHER}\ESL-Lite" "ESL-Studio-Version"
		${Else}
			ReadRegStr $Got_ESL_ESLStudio_Version HKLM "SOFTWARE\${ISIM_PRODUCT_PUBLISHER}\ESL-Lite" "ESL-Studio-Version"
		${EndIf}
	${EndIf}
	${If} $Got_ESL_ESLStudio_Version == ""
		${If} $Got_ESLDIR != ""
			${If} ${FileExists} "$Got_ESLDIR\esl-studio\bin"
				# Must be on the original ESL v8.3.0.1 which originally contained 1.2.0.30
				## Note to self: when install in ESL have to set ESL-Studio-Version etc
				StrCpy $Got_ESL_ESLStudio_Version "1.2.0.30"
			${EndIf}
		${EndIf}
	${EndIf}
# Cant have this active when uninstall (even with ExecWait) because may be installing on same directory (and wont wait for this)
#	MessageBox MB_OK "<un.CheckInstallations:$\n\
#Got_ESL=$Got_ESL$\n\
#Got_ESL_ESLStudio_Version=$Got_ESL_ESLStudio_Version$\n\
#Got_ESLDIR=$Got_ESLDIR"
FunctionEnd

Function SeeIfCanInstallInESL
##	MessageBox MB_OK ">SeeIfDoInstallInESL Got_ESL_Version=$Got_ESL_Version"
	StrCpy $CanInstallInESLText ""
	StrCpy $CannotInstallInESLText ""
	StrCpy $InESL_ESLStudioComponentText ""
	${If} $Got_ESL_Version != ""
		${EslNsisCompareValidVersions} $0 $Got_ESL_Version "8.3.0.1" # min ESL version that we allow for InstallInESL
		${If} $0 == "higher"
		${OrIf} $0 == "same"
			StrCpy $InESL_ESLStudioComponentText "${ESLSTUDIO_COMPONENT_TEXT_CAN_HAVE}"
			${If} $Got_ESL_ESLStudio_Version != ""
				StrCpy $InESL_ESLStudioComponentText "${ESLSTUDIO_COMPONENT_TEXT_HAS}"
			${EndIf}
			StrCpy $CanInstallInESLText "${CAN_INSTALL_IN_ESL_TEXT}"
		${Else}
			StrCpy $CannotInstallInESLText "${CANNOT_INSTALL_IN_ESL_TEXT}"
		${EndIf}
	${EndIf}
##	MessageBox MB_OK "<SeeIfDoInstallInESL CanInstallInESLText=$CanInstallInESLText CannotInstallInESLText=$CannotInstallInESLText"
FunctionEnd

Function SetupForWelcomePage
	StrCpy $WelcomePageGuidanceText "${WELCOMEPAGE_GUIDANCE_TEXT_DEFAULT}"
	StrCpy $WelcomePageRecommendationText "${WELCOMEPAGE_RECOMMENDATION_TEXT_DEFAULT}"
	StrCpy $CannotInstallSoloText ""
	StrCpy $AndFound ""
	StrCpy $PreviousSoloText ""
	StrCpy $PreviousSoloNotReplaceableText ""
	${If} $CanInstallInESLText != ""
	${OrIf} $CannotInstallInESLText != ""
	${OrIf} $GotESLStudio_Installed != ""
		${If} $CanInstallInESLText != ""
		${OrIf} $CannotInstallInESLText != ""
			${If} $GotESLStudio_Installed != ""
				StrCpy $AndFound "${AND_FOUND_TEXT}"
			${EndIf}
		${EndIf}
	${EndIf}
	${If} $GotESLStudio_Installed != ""
		${EslNsisCompareValidVersions} $PreviousVersionStatus $GotESLStudio_Version ${PRODUCT_VERSION}
##		MessageBox MB_OK "-SetupForWelcomePage GotESLStudio_Installed=$GotESLStudio_Installed $\n\
##GotESLStudio_Version=$GotESLStudio_Version $\n\
##PRODUCT_VERSION=${PRODUCT_VERSION} $\n\
##PreviousVersionStatus=$PreviousVersionStatus"
		${If}  $PreviousVersionStatus == "lower" ; Change "lower" to "older" for display clarification later in DIRTEXT_ADDITIONAL_TEXT_LOCATION
			StrCpy $PreviousVersionStatus "older"
		${EndIf}
		${If} $PreviousVersionStatus == "higher"
			StrCpy $PreviousSoloNotReplaceableText "${PREVIOUS_SOLO_NOT_REPLACEABLE_HIGHER_VERSION_TEXT}"
			${If} $CanInstallInESLText == ""
				StrCpy $CannotInstallSoloText "${CANNOT_INSTALL_SOLO_TEXT_HIGHER_VERSION}"
			${EndIf}
		${ElseIf} $PreviousVersionStatus == "invalid"
			StrCpy $PreviousSoloNotReplaceableText "${PREVIOUS_SOLO_NOT_REPLACEABLE_INVALID_VERSION_TEXT}"
			${If} $CanInstallInESLText == ""
				StrCpy $CannotInstallSoloText "${CANNOT_INSTALL_SOLO_TEXT_INVALID_VERSION}"
			${EndIf}
		${EndIf}
		StrCpy $PreviousSoloText "${PREVIOUS_SOLO_TEXT}"
	${EndIf}
	${If} $CanInstallInESLText != ""
	${OrIf} $CannotInstallInESLText != ""
	${OrIf} $GotESLStudio_Installed != ""
		StrCpy $WelcomePageTextAdditionalText "${WELCOMEPAGE_TEXT_ADDITIONAL_TEXT}"
	${EndIf}
##	MessageBox MB_OK "<SetupWelcomePage CanInstallInESLText=$CanInstallInESLText"
FunctionEnd

Function WelcomePagePreCallback
	StrCpy $WelcomePageClickText "${WELCOMEPAGE_CLICK_TEXT_DEFAULT}"
	${If} $CanInstallInESLText == ""
	${AndIf} $PreviousSoloNotReplaceableText != ""
		SendMessage $mui.Button.Next ${WM_SETTEXT} 0 "STR:${EXITBUTTONTEXT}"

		StrCpy $WelcomePageGuidanceText "${WELCOMEPAGE_GUIDANCE_TEXT_CANNOT_INSTALL}"
		StrCpy $WelcomePageRecommendationText ""
		StrCpy $WelcomePageClickText "${WELCOMEPAGE_CLICK_TEXT_TO_EXIT}"
	${Endif}
FunctionEnd

Function WelcomePageLeaveCallback
	${If} $CanInstallInESLText == ""
	${AndIf} $PreviousSoloNotReplaceableText != ""
		Quit
	${Endif}
FunctionEnd

Function AskIfDoInstallInESL
##	MessageBox MB_OK ">AskIfDoInstallInESL Got_ESL_Version=$Got_ESL_Version CannotInstallSoloText=$CannotInstallSoloText"
	ask:
	StrCpy $DoInstallInESL ""
	StrCpy $ESLStudioReplacementText ""
	${If} $CanInstallInESLText != ""
		${If} $Got_ESL_ESLStudio_Version != ""
			StrCpy $ESLStudioReplacementText "${ESLSTUDIO_REPLACEMENT_TEXT}"
		${EndIf}
		${If} $PreviousSoloNotReplaceableText == "" ; you can install solo
			StrCpy $AskSelectionText "${ASK_SELECTION_TEXT_CAN_SOLO}"
			StrCpy $AskESLText "${ASK_ESL_TEXT}"
			MessageBox MB_YESNOCANCEL|MB_ICONQUESTION $AskESLText IDNO no IDCANCEL ask_quit
			StrCpy $DoInstallInESL "DoInstallInESL" ; yes
			no: ; no
		${Else} ; you can't install solo
			StrCpy $AskSelectionText "${ASK_SELECTION_TEXT_CANNOT_SOLO}"
			StrCpy $AskESLText "${ASK_ESL_TEXT}"
			MessageBox MB_OKCANCEL|MB_ICONQUESTION $AskESLText IDCANCEL ask_quit
			StrCpy $DoInstallInESL "DoInstallInESL"
		${EndIf}
	${EndIf}
##	MessageBox MB_OK "<AskIfDoInstallInESL DoInstallInESL=$DoInstallInESL"
	Return
	ask_quit:
	MessageBox MB_YESNO|MB_ICONEXCLAMATION "${ASK_QUIT_TEXT}" IDNO ask
	Quit ; Cancel button - exits the installation
FunctionEnd

Function ComponentsPagePreCallback
##	MessageBox MB_OKCANCEL|MB_ICONQUESTION ">ComponentsPagePreCallback $DoInstallInESL : $INSTDIR$\nOK to continue - Cancel to Abort" IDOK continue
##		Abort
##	continue:
	Call AskIfDoInstallInESL

	StrCpy $ComponentsPageTextTopAdditionalText "${COMPONENTSPAGE_TEXT_TOP_ADDITIONAL_SOLO}"
	StrCpy $ComponentsPageClickText "${COMPONENTSPAGE_CLICK_TEXT_DEFAULT}"
	${If} $DoInstallInESL != "" ; Doing InstallInESL so  to set Next button to INSTALL
		;Set text on this page's Next button for INSTALL
		SendMessage $mui.Button.Next ${WM_SETTEXT} 0 "STR:${INSTALLBUTTONTEXT}"

		StrCpy $ComponentsPageTextTopAdditionalText "${COMPONENTSPAGE_TEXT_TOP_ADDITIONAL_IN_ESL}"
		StrCpy $ComponentsPageClickText "${COMPONENTSPAGE_CLICK_TEXT_INSTALL}"

	${EndIf}
##	MessageBox MB_OK "ComponentsPagePreCallback continuing ComponentsPageClickText=$ComponentsPageClickText"
FunctionEnd

Function DirectoryPagePreCallback
##	MessageBox MB_OK ">DirectoryPagePreCallback DoInstallInESL=$DoInstallInESL GotESLStudio_InstallLocation=$GotESLStudio_InstallLocation PreviousVersionStatus=$PreviousVersionStatus INSTDIR=$INSTDIR"
	${If} $DoInstallInESL != "" ; Doing InstallInESL so don't select an installation directory
		Abort
	${Else}
		StrCpy $DirTextAdditionalText "${DIRTEXT_ADDITIONAL_TEXT_DEFAULT}"
		StrCpy $1 ""
		${If} $GotESLStudio_InstallLocation != ""
			StrCpy $DirTextAdditionalText "${DIRTEXT_ADDITIONAL_TEXT_LOCATION}"
			StrCpy $INSTDIR $GotESLStudio_InstallLocation
		${EndIf}
	${EndIf}
##	MessageBox MB_OK "<DirectoryPagePreCallback DirTextAdditionalText=$DirTextAdditionalText INSTDIR=$INSTDIR"
FunctionEnd

Function StartMenuPagePreCallback
##	MessageBox MB_OKCANCEL|MB_ICONQUESTION ">StartMenuPagePreCallback $DoInstallInESL$\nOK to continue - Cancel to Abort" IDOK continue
##		Abort
##	continue:
	${If} $DoInstallInESL != "" ; Doing InstallInESL so don't set short-cuts in start menu
		Abort
	${EndIf}
##	MessageBox MB_OK "StartMenuPagePreCallback continuing"
FunctionEnd

Function UninstallPreviousInstallation ; StartMenuPageLeaveCallback
##	MessageBox MB_OK ">UninstallPreviousInstallation (= StartMenuPageLeaveCallback) $DoInstallInESL"
	${If} $DoInstallInESL == "" ; Doing solo (standalone)
		${If} $GotESLStudio_Installed != ""
    	    ReadRegStr $UninstallCmd HKLM "${PRODUCT_UNINST_KEY}" "UninstallString"
			${If} $UninstallCmd != ""
				StrCpy $UninstallCmd "$UninstallCmd /S"
			${EndIf}

##			MessageBox MB_OK "UninstallCmd=$UninstallCmd"

			ClearErrors
			${If} $UninstallCmd != ""
##				MessageBox MB_OK "Uninstalling ${PRODUCT_NAME}-$GotESLStudio_Version from $GotESLStudio_InstallLocation ..."
				ExecWait $UninstallCmd
				Sleep 200					# Needs a bit of Sleep if use same directory (else may skip files).
			${EndIf}
			; If uninstall was not successful, do not continue.
			; This happens for example if the user cancels the uninstaller.
			${If} ${Errors}
				MessageBox MB_OK|MB_ICONSTOP "Problem uninstalling previous version"
				Abort
			${EndIf}
			${If} $UninstallCmd != ""
				${If} $GotESLStudio_InstallLocation == $INSTDIR
##					MessageBox MB_OK "Installing on same directory as uninstalling"
					Sleep 700				# Needs a bit more Sleep.
				${EndIf}
##				MessageBox MB_OK "Uninstalled ${PRODUCT_NAME}-$GotESLStudio_Version - continuing installation"
			${EndIf}
		${EndIf}
	${EndIf}
FunctionEnd

Function OpenReadMe
	# The MUI2 FinishPage.ShowReadme (Finish.nsh) does ExecShell open "${MUI_FINISHPAGE_SHOWREADME}"
	# But on Windows 11 this does not work if the user does not have admin privileges.
	# Instead we explicitly invoke Notepad.
	# Note: It seems we can't use MUI_FINISHPAGE_SHOWREADME directly so use our own README_FILE.
	StrCpy $0 ${README_FILE}
	${If} $DoInstallInESL != ""
		StrCpy $0 "$Got_ESLDIR\esl-studio\docs\readme.txt"
	${EndIf}
	Exec '"$SYSDIR\notepad.exe" $0'
FunctionEnd

;--------------------------------
; Sections
;--------------------------------

Section "${PRODUCT_NAME} files" InstallFiles
#	DetailPrint ">InstallFiles"
##	MessageBox MB_OK ">InstallFiles $DoInstallInESL"
	SectionIn RO	# required component
	${If} $DoInstallInESL != ""
		RMDir /r "$Got_ESLDIR\esl-studio"
		; Sleep 200					# Do we need this?.
		SetOutPath "$Got_ESLDIR\esl-studio"
	${Else}
		SetOutPath "$INSTDIR"
	${EndIf}
	File /r "${SRC}\bin"
	File /r "${SRC}\docs"
#	DetailPrint "<InstallFiles"
SectionEnd

Section "ESL-Studio examples files" InstallESLStudioExamplesFiles
#	DetailPrint ">InstallESLStudioExamplesFiles"
##	MessageBox MB_OK ">InstallESLStudioExamplesFiles $DoInstallInESL"
	${If} $DoInstallInESL != ""
		SetOutPath "$Got_ESLDIR\esl-studio"
	${Else}
		SetOutPath "$INSTDIR"
	${EndIf}
	File /r "${SRC}\examples"
#	DetailPrint "<InstallESLStudioExamplesFiles"
SectionEnd

Section un.InstallFiles ; Doing solo (standalone) uninstall
#	DetailPrint ">un.InstallFiles"
	RMDir /r "$INSTDIR\bin"
	RMDir /r "$INSTDIR\docs"
	RMDir /r "$INSTDIR\examples"
#	DetailPrint "<un.InstallFiles"
SectionEnd

Section -SetFileAssociations
#	DetailPrint ">SetFileAssociations"
##	MessageBox MB_OK ">SetFileAssociations $DoInstallInESL"
	WriteRegStr HKCR ".eslstudio" "" "ESL.eslstudiofile"
	${If} $DoInstallInESL == "" ; Doing solo (standalone)
		WriteRegStr HKCR "ESL.eslstudiofile" "" "${ESLSTUDIO_SOLO_FILE_ASSOCIATION}"
		WriteRegStr HKCR "ESL.eslstudiofile\DefaultIcon" "" "$INSTDIR\bin\esl_studio.exe,0" # have to use icon 0
		WriteRegStr HKCR "ESL.eslstudiofile\shell\open\command" "" '"$INSTDIR\bin\esl_studio.exe" "%1"'
	${Else} ; Doing InstallInESL - set these (in case had not had a previous ESL-Studio component)
		WriteRegStr HKCR "ESL.eslstudiofile" "" "${ESL_ESLSTUDIO_FILE_ASSOCIATION}"
		WriteRegStr HKCR "ESL.eslstudiofile\DefaultIcon" "" "$Got_ESLDIR\esl-studio\bin\esl_studio.exe,0" # have to use icon 0
		WriteRegStr HKCR "ESL.eslstudiofile\shell\open\command" "" '"$Got_ESLDIR\esl-studio\bin\esl_studio.exe" "%1"'
	${EndIf}
#	DetailPrint "<SetFileAssociations"
SectionEnd

Section un.SetFileAssociations ; Doing solo (standalone) uninstall
#	DetailPrint ">un.SetFileAssociations"
	ReadRegStr $0 HKCR "ESL.eslstudiofile" ""
	${If} $0 == "${ESLSTUDIO_SOLO_FILE_ASSOCIATION}" ; Last ESL-Studio install was for this (solo) - not ESL component
		# See if should reassign .eslstudio file association to an ESL ESL-Studio component
		${If} $Got_ESL != ""
		${AndIf} $Got_ESL_ESLStudio_Version != "" ; Reinstate the file association to the ESL's ESL-Studio
			WriteRegStr HKCR "ESL.eslstudiofile" "" "${ESL_ESLSTUDIO_FILE_ASSOCIATION}"
			WriteRegStr HKCR "ESL.eslstudiofile\DefaultIcon" "" "$Got_ESLDIR\esl-studio\bin\esl_studio.exe,0" # have to use icon 0
			WriteRegStr HKCR "ESL.eslstudiofile\shell\open\command" "" '"$Got_ESLDIR\esl-studio\bin\esl_studio.exe" "%1"'
		${Else} ; Remove the file association
			DeleteRegKey HKCR "ESL.eslstudiofile"
			DeleteRegKey HKCR ".eslstudio"
		${EndIf}
	# Else was not last installed (and associated) by this installer - so leave it be.
	${EndIf}
#	DetailPrint "<un.SetFileAssociations"
SectionEnd

Section -SetStartMenu		# After Install
#	DetailPrint ">SetStartMenu"
##	MessageBox MB_OK ">SetStartMenu $DoInstallInESL"
	${If} $DoInstallInESL == "" ; Doing solo (standalone)
		!insertmacro MUI_STARTMENU_WRITE_BEGIN Application
			CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
			CreateShortCut "$SMPROGRAMS\$StartMenuFolder\${ESLSTUDIO_SOLO_LINK_NAME}.lnk" "$INSTDIR\bin\esl_studio.exe"
			CreateShortCut "$SMPROGRAMS\$StartMenuFolder\${UNINSTALL_LINK_NAME}.lnk" "$INSTDIR\${UNINSTALL_LINK_EXE}.exe"
		!insertmacro MUI_STARTMENU_WRITE_END
	${Else} ; Doing InstallInESL
		!define MUI_STARTMENUPAGE_DEFAULTFOLDER "$Got_ESL_StartMenuFolder"
		!define MUI_STARTMENUPAGE_NODISABLE
		## Would like to keep set to disable the short-cuts and then remove the checkbox MUI_STARTMENUPAGE_NODISABLE
		CreateShortCut "$SMPROGRAMS\$Got_ESL_StartMenuFolder\${ESL_ESLSTUDIO_LINK_NAME}.lnk" "$Got_ESLDIR\esl-studio\bin\esl_studio.exe"
	${EndIf}
#	DetailPrint "<SetStartMenu"
SectionEnd

Section un.SetStartMenu ; Doing solo (standalone) uninstall
#	DetailPrint ">un.SetStartMenu"
	!insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
	Delete "$SMPROGRAMS\$StartMenuFolder\${UNINSTALL_LINK_NAME}.lnk"
	Delete "$SMPROGRAMS\$StartMenuFolder\${ESLSTUDIO_SOLO_LINK_NAME}.lnk"
	RMDir "$SMPROGRAMS\$StartMenuFolder"
	#DeleteRegKey /ifempty HKLM "SOFTWARE\${PRODUCT_PUBLISHER}\${PRODUCT_NAME}" # this will happen later due to Installed mark
#	DetailPrint "<un.SetStartMenu"
SectionEnd

Section -SetInstaller
#	DetailPrint ">-SetInstaller"
##	MessageBox MB_OK ">SetInstaller $DoInstallInESL"
	${If} $DoInstallInESL == "" ; Doing solo (standalone)
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "${NAME}"
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$\"$INSTDIR\${UNINSTALL_LINK_EXE}.exe$\""
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "InstallLocation" "$INSTDIR"
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\${UNINSTALL_LINK_EXE}.exe"
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "HelpLink" "${PRODUCT_WEB_SITE}"
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Comments" "${PRODUCT_DESCRIPTION}"
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Contact" "${PRODUCT_CONTACT}"
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "InstallSource" "$EXEDIR\"
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "VersionMajor"  "${PRODUCT_VERSION_MAJOR}"
		WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "VersionMinor" "${PRODUCT_VERSION_MINOR}"
		WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "NoModify" "1"
		WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "NoRepair" "1"

		${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
		IntFmt $0 "0x%08X" $0
		WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "EstimatedSize" "$0"
	${EndIf}
#	DetailPrint "<-SetInstaller"
SectionEnd

Section un.SetInstaller ; Doing solo (standalone) uninstall
#	DetailPrint ">un.SetInstaller"
	DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
#	DetailPrint "<un.SetInstaller"
SectionEnd

Section -FinaliseInstallation
#	DetailPrint ">-FinaliseInstallation"
##	MessageBox MB_OK ">FinaliseInstallation $DoInstallInESL"
	${GetTime} "" "L" $0 $1 $2 $3 $4 $5 $6
	#StrCpy $DateTime "$0/$1/$2 $4:$5:$6"	# UK style
	StrCpy $DateTime "$2-$1-$0 $4:$5:$6"	# ISO date style
	${If} $DoInstallInESL == "" ; Doing solo (standalone)
		WriteRegStr HKLM "SOFTWARE\${PRODUCT_PUBLISHER}\${PRODUCT_NAME}" "Installed" "$DateTime"
		WriteRegStr HKLM "SOFTWARE\${PRODUCT_PUBLISHER}\${PRODUCT_NAME}" "Version" "${PRODUCT_VERSION}"
		WriteUninstaller "$INSTDIR\${UNINSTALL_LINK_EXE}.exe"
	${Else} ; Update the ESL-Studio installation info in the ESL
		${If} $ISIM_ESL == ""
			WriteRegStr HKLM "SOFTWARE\${PRODUCT_PUBLISHER}\$Got_ESL" "ESL-Studio-Installed" "$DateTime"
			WriteRegStr HKLM "SOFTWARE\${PRODUCT_PUBLISHER}\$Got_ESL" "ESL-Studio-Version" "${PRODUCT_VERSION}"
		${Else}
			WriteRegStr HKLM "SOFTWARE\${ISIM_PRODUCT_PUBLISHER}\$Got_ESL" "ESL-Studio-Installed" "$DateTime"
			WriteRegStr HKLM "SOFTWARE\${ISIM_PRODUCT_PUBLISHER}\$Got_ESL" "ESL-Studio-Version" "${PRODUCT_VERSION}"
		${EndIf}
	${EndIf}
#	DetailPrint "<-FinaliseInstallation"
SectionEnd

Section Uninstall ; Doing solo (standalone) uninstall
#	DetailPrint ">Uninstall"
	Delete $INSTDIR\${UNINSTALL_LINK_EXE}.exe
	RMDir "$INSTDIR" # if empty
	# Could we check if $INSTDIR is of form [Program Files?]\ESL\x and only then do line below
	RMDir "$INSTDIR\..\..\${PRODUCT_ROOT}" # if empty
	DeleteRegKey HKLM "SOFTWARE\${PRODUCT_PUBLISHER}\${PRODUCT_NAME}"
	DeleteRegKey /ifempty HKLM "SOFTWARE\${PRODUCT_PUBLISHER}"
#	DetailPrint "<Uninstall"
SectionEnd

;--------------------------------
; Descriptions (after sections)
;--------------------------------

LangString DESC_InstallFiles ${LANG_ENGLISH} "Required program files."
LangString DESC_InstallESLStudioExamplesFiles ${LANG_ENGLISH} "Install the ESL-Studio Examples files."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${InstallFiles} $(DESC_InstallFiles)
!insertmacro MUI_DESCRIPTION_TEXT ${InstallESLStudioExamplesFiles} $(DESC_InstallESLStudioExamplesFiles)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
