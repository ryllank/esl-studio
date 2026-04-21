; EslNsisUtils

!ifndef ___ESL_NSIS_UTILS___
!define ___ESL_NSIS_UTILS___

!include LogicLib.nsh

# Macro ${EslNsisExplode} nrElements(out) separatorStr(in) inputStr(in)
# Pushes nrElements string elements on the stack after splitting the inputStr
# with the separatorStr. There will always be at least one (which may be empty, 
# as may any of them).
# After invoking you should pop off the nrElements elements and handle one by one
# in a loop.
; Obtained, as Explode, from https://nsis.sourceforge.io/Explode

# Have to use variables (which in NSIS are global) for work variables as
# returning arbitrary number of elements on stack makes it 
# impossible (as I see it) to save "register" variables to use for this
# and restore them from stack and leave the elements suitably stacked.
Var /GLOBAL EslNsisExplInputStr
Var /GLOBAL EslNsisExplSeparatorStr
Var /GLOBAL EslNsisExplStrLen
Var /GLOBAL EslNsisExplSepLen
Var /GLOBAL EslNsisExplOffset
Var /GLOBAL EslNsisExplTmp
Var /GLOBAL EslNsisExplTmp2
Var /GLOBAL EslNsisExplTmp3
Var /GLOBAL EslNsisExplNrElements

# Macro EslNsisExplode
!define EslNsisExplode "!insertmacro EslNsisExplode"
!macro EslNsisExplode nrElements separatorStr inputStr
	Push `${separatorStr}`
	Push `${inputStr}`
	Call EslNsisExplode
	Pop  `${nrElements}`
!macroend
!define un.EslNsisExplode "!insertmacro un.EslNsisExplode"
!macro un.EslNsisExplode nrElements separatorStr inputStr
	Push `${separatorStr}`
	Push `${inputStr}`
	Call un.EslNsisExplode
	Pop  `${nrElements}`
!macroend

# Function EslNsisExplode
!macro mkEslNsisExplode UN
Function ${UN}EslNsisExplode
 
  ; Get input from user
  Pop $EslNsisExplInputStr
  Pop $EslNsisExplSeparatorStr
 
  ; Calculates initial values
  StrLen $EslNsisExplStrLen $EslNsisExplInputStr
  StrLen $EslNsisExplSepLen $EslNsisExplSeparatorStr
  StrCpy $EslNsisExplNrElements 1
 
  ${If}   $EslNsisExplStrLen <= 1 ; If we got a single character
  ${OrIf} $EslNsisExplSepLen > $EslNsisExplStrLen ; or separator is larger than the string,
    Push    $EslNsisExplInputStr  ; then we return initial string with no change
    Push    1                     ; and set array's length to 1
    Return
  ${EndIf}
 
  ; Set offset to the last symbol of the string
  StrCpy $EslNsisExplOffset $EslNsisExplStrLen
  IntOp  $EslNsisExplOffset $EslNsisExplOffset - 1
 
  ; Clear temp string to exclude the possibility of appearance of occasional data
  StrCpy $EslNsisExplTmp   ""
  StrCpy $EslNsisExplTmp2  ""
  StrCpy $EslNsisExplTmp3  ""
 
  ; Loop until the offset becomes negative
  ${Do}
    ;   If offset becomes negative, it is time to leave the function
    ${IfThen} $EslNsisExplOffset == -1 ${|} ${ExitDo} ${|}
 
    ;   Remove everything before and after the searched part ("TempStr")
    StrCpy $EslNsisExplTmp $EslNsisExplInputStr $EslNsisExplSepLen $EslNsisExplOffset
 
    ${If} $EslNsisExplTmp == $EslNsisExplSeparatorStr
        ;   Calculating offset to start copy from
        IntOp   $EslNsisExplTmp2 $EslNsisExplOffset + $EslNsisExplSepLen ; Offset equals to the current offset plus length of separator
        StrCpy  $EslNsisExplTmp3 $EslNsisExplInputStr "" $EslNsisExplTmp2
 
        Push    $EslNsisExplTmp3                           ; Throwing array item to the stack
        IntOp   $EslNsisExplNrElements $EslNsisExplNrElements + 1 ; Increasing array's counter
 
        StrCpy  $EslNsisExplInputStr $EslNsisExplInputStr $EslNsisExplOffset 0 ; Cutting all characters beginning with the separator entry
        StrLen  $EslNsisExplStrLen $EslNsisExplInputStr
    ${EndIf}
 
    ${If} $EslNsisExplOffset = 0 ; If the beginning of the line met and there is no separator,
                                 ; copying the rest of the string
        ${If} $EslNsisExplSeparatorStr == ""    ; Fix for the empty separator
            IntOp   $EslNsisExplNrElements   $EslNsisExplNrElements - 1
        ${Else}
            Push    $EslNsisExplInputStr
        ${EndIf}
    ${EndIf}
 
    IntOp   $EslNsisExplOffset $EslNsisExplOffset - 1
  ${Loop}

  Push $EslNsisExplNrElements
FunctionEnd
!macroend   # mkEslNsisExplode UN
!insertmacro mkEslNsisExplode ""
!insertmacro mkEslNsisExplode "un."

# Macro ${EslNsisCompareValidVersions} resultStr(out) formerVersionStr(in) currentVersionStr(out)
# Compares the currentVersionStr with a formerVersionStr and returns a resultStr 
# (for valid versions) to say if former version was lower, higher or the same as current.
!define EslNsisCompareValidVersions "!insertmacro EslNsisCompareValidVersions"
!macro  EslNsisCompareValidVersions resultStr formerVersionStr currentVersionStr
	Push `${formerVersionStr}`
	Push `${currentVersionStr}`
	Call EslNsisCompareValidVersions
	Pop  `${resultStr}`
!macroend
!define un.EslNsisCompareValidVersions "!insertmacro un.EslNsisCompareValidVersions"
!macro  un.EslNsisCompareValidVersions resultStr formerVersionStr currentVersionStr
	Push `${formerVersionStr}`
	Push `${currentVersionStr}`
	Call un.EslNsisCompareValidVersions
	Pop  `${resultStr}`
!macroend

# Function EslNsisCompareValidVersions
!macro mkEslNsisCompareValidVersions UN
Function ${UN}EslNsisCompareValidVersions
	# Retrieve arguments and stack up work variables to restore values at end.
	; stack		; formerVersionStr currentVersionStr
	Push $0		; $0 formerVersionStr currentVersionStr			| $0 used to return the comparison resultStr
	Exch 2		; formerVersionStr currentVersionStr $0
	Exch $R1	; $R1 currentVersionStr $0						| $R1<-formerVersionStr
	Exch 1		; currentVersionStr $R1 $0 
	Exch $R2	; $R2 $R1 $0 									| $R2<-pathElementToRemove
	Push $1		; $1 $R2 $R1 $0 								| $1 used for exploded version elements
	Push $2		; $2 $1 $R2 $R1 $0 								| $2 used for major version element of formerVersionStr
	Push $3		; $3 $2 $1 $R2 $R1 $0 							| $3 used for minor version element of formerVersionStr
	Push $4		; $4 $3 $2 $1 $R2 $R1 $0 						| $4 used for revsn version element of formerVersionStr
	Push $5		; $5 $4 $3 $2 $1 $R2 $R1 $0 					| $5 used for build version element of formerVersionStr
	Push $6		; $6 $5 $4 $3 $2 $1 $R2 $R1 $0 					| $6 used for major version element of currentVersionStr
	Push $7		; $7 $6 $5 $4 $3 $3 $2 $1 $R2 $R1 $0 			| $7 used for minor version element of currentVersionStr
	Push $8		; $8 $7 $6 $5 $4 $3 $4 $3 $2 $1 $R2 $R1 $0 		| $8 used for revsn version element of currentVersionStr
	Push $9		; $9 $8 $7 $6 $5 $4 $3 $5 $4 $3 $2$1 $R2 $R1 $0	| $9 used for build version element of currentVersionStr
# MessageBox MB_OK ">${UN}EslNsisCompareValidVersions formerVersionStr=$R1 with currentVersionStr=$R2"
# DetailPrint ">${UN}EslNsisCompareValidVersions formerVersionStr=$R1 with currentVersionStr=$R2"
	${${UN}EslNsisExplode} $1 "." $R1 # formerVersionStr
	${If} $1 != 4
		StrCpy $0 "invalid"
		# Pop off $1 values (to $2)
		loop1:
			IntCmp $1 0 end_loop1 end_loop1 0
			Pop $2
			IntOp $1 $1 - 1
			goto loop1
		end_loop1:
	${Else}
		Pop $2
		Pop $3
		Pop $4
		Pop $5
# MessageBox MB_OK "*${UN}EslNsisCompareValidVersions formerVersion got $2 $3 $4 $5"
# DetailPrint "*${UN}EslNsisCompareValidVersions formerVersion got $2 $3 $4 $5"
		${${UN}EslNsisExplode} $1 "." $R2 # currentVersionStr
		${If} $1 != 4
			StrCpy $0 "invalid"
			# Pop off $1 values (to $2)
			loop2:
				IntCmp $1 0 end_loop2 end_loop2 0
				Pop $2
				IntOp $1 $1 - 1
				goto loop2
			end_loop2:
		${Else}
			Pop $6
			Pop $7
			Pop $8
			Pop $9
# MessageBox MB_OK "*${UN}EslNsisCompareValidVersions cf currentVersion $6 $7 $8 $9"
# DetailPrint "*${UN}EslNsisCompareValidVersions cf currentVersion $6 $7 $8 $9"
			${If} $2 < $6
				StrCpy $0 "lower"
			${ElseIf} $2 > $6
				StrCpy $0 "higher"
			${Else}
				${If} $3 < $7
					StrCpy $0 "lower"
				${ElseIf} $3 > $7
					StrCpy $0 "higher"
				${Else}
					${If} $4 < $8
						StrCpy $0 "lower"
					${ElseIf} $4 > $8
						StrCpy $0 "higher"
					${Else}
						${If} $5 < $9
							StrCpy $0 "lower"
						${ElseIf} $5 > $9
							StrCpy $0 "higher"
						${Else}
							StrCpy $0 "same"
						${Endif}
					${Endif}
				${Endif}
			${Endif}
		${Endif}
	${Endif}
# MessageBox MB_OK "<${UN}EslNsisCompareValidVersions result=$0"
# DetailPrint "<${UN}EslNsisCompareValidVersions result=$0"
	# Restore values of work variables from stack.
	Pop $9
	Pop $8
	Pop $7
	Pop $6
	Pop $5
	Pop $4
	Pop $3
	Pop $2
	Pop $1
	Pop $R2
	Pop $R1		; stack: $0
	# Push work $0=resultStr onto stack
	Push $0		; resultStr $0
	Exch		; $0 resultStr
	# Restore orig value into $0
	Pop $0		; resultStr result left on stack - is popped by macro
FunctionEnd
!macroend   # mkEslNsisCompareValidVersions UN
!insertmacro mkEslNsisCompareValidVersions ""
!insertmacro mkEslNsisCompareValidVersions "un."

# Macro ${EslNsisRemoveFromPath} finalPath(out) pathStr(in) pathElementToRemove(in)
# Removes pathElementToRemove (an element) which may be in pathStr, a path separated 
# by semi-colons (;), and returns the finalPath - without the element if it 
# was in there, or the original path if it wasn't.
!define EslNsisRemoveFromPath "!insertmacro EslNsisRemoveFromPath"
!macro  EslNsisRemoveFromPath finalPath pathStr pathElementToRemove
	Push `${pathStr}`
	Push `${pathElementToRemove}`
	Call EslNsisRemoveFromPath
	Pop  `${finalPath}`
!macroend
!define un.EslNsisRemoveFromPath "!insertmacro un.EslNsisRemoveFromPath"
!macro  un.EslNsisRemoveFromPath finalPath pathStr pathElementToRemove
	Push `${pathStr}`
	Push `${pathElementToRemove}`
	Call un.EslNsisRemoveFromPath
	Pop  `${finalPath}`
!macroend

# Function EslNsisRemoveFromPath
!macro mkEslNsisRemoveFromPath UN
Function ${UN}EslNsisRemoveFromPath
	# Retrieve arguments and stack up work variables to restore values at end.
	; stack		; pathElementToRemove pathStr
	Push $0		; $0 pathElementToRemove pathStr	| $0 used to build and return finalPath
	Exch 2		; pathStr pathElementToRemove $0
	Exch $1		; $1 pathElementToRemove $0			| $1<-pathStr
	Exch 1		; pathElementToRemove $1 $0 
	Exch $2		; $2 $1 $0 							| $2<-pathElementToRemove
	Push $3		; $3 $2 $1 $0 						| $3 used for number of path elements
	Push $4		; $4 $3 $2 $1 $0					| $4 used for ongoing count of processed path elements
	Push $5		; $5 $4 $3 $2 $1 $0					| $5 used for current path element
	StrCpy $0 "" # use $0 to build the final path
# MessageBox MB_OK ">${UN}EslNsisRemoveFromPath pathElementToRemove=$2 pathStr=$1"
# DetailPrint ">${UN}EslNsisRemoveFromPath pathElementToRemove=$2 pathStr=$1"
	${${UN}EslNsisExplode} $3 ";" $1
# MessageBox MB_OK "-${UN}EslNsisRemoveFromPath nr elements=$3"
# DetailPrint "-${UN}EslNsisRemoveFromPath nr elements=$3"
	loop:
		IntCmp $4 $3 end_loop
		Pop $5
		IntOp $4 $4 + 1
# MessageBox MB_OK "-${UN}EslNsisRemoveFromPath elements=$4 =$5"
# DetailPrint "-${UN}EslNsisRemoveFromPath elements=$4 =$5"
		StrCmp $5 "" after_add_element # dont accrete if blank
		StrCmp $5 $2 after_add_element
			StrCpy $0 "$0$5;" # have trailing separator
		after_add_element:
		goto loop
	end_loop:
	StrCpy $0 $0 -1 # remove final trailing ;
# MessageBox MB_OK "-${UN}EslNsisRemoveFromPath $0 $1 $2 $3 $4 $5"
	# Restore values of work variables from stack.
	Pop $5
	Pop $4
	Pop $3
	Pop $2
	Pop $1		; stack: $0
	# Push work $0=finalPath onto stack
	Push $0		; finalPath $0
	Exch		; $0 finalPath
	# Restore orig value into $0
	Pop $0		; finalPath result left on stack - is popped by macro
FunctionEnd
!macroend   # mkEslNsisRemoveFromPath UN
!insertmacro mkEslNsisRemoveFromPath ""
!insertmacro mkEslNsisRemoveFromPath "un."

# Macro ${EslNsisRemoveFromPathEnvVar} regLoc(in) regPath(in) pathKey(in) pathElementToRemove(in)
# Invokes the ${EslNsisRemoveFromPath} macro on a regPath/pathKey in the registry.
# regLoc can be HKLM or HKCU.
!define EslNsisRemoveFromPathEnvVar "!insertmacro EslNsisRemoveFromPathEnvVar"
!macro  EslNsisRemoveFromPathEnvVar regLoc regPath pathKey pathElementToRemove
	Push `${regLoc}`
	Push `${regPath}`
	Push `${pathKey}`
	Push `${pathElementToRemove}`
	Call EslNsisRemoveFromPathEnvVar
!macroend
!define un.EslNsisRemoveFromPathEnvVar "!insertmacro un.EslNsisRemoveFromPathEnvVar"
!macro  un.EslNsisRemoveFromPathEnvVar regLoc regPath pathKey pathElementToRemove
	Push `${regLoc}`
	Push `${regPath}`
	Push `${pathKey}`
	Push `${pathElementToRemove}`
	Call un.EslNsisRemoveFromPathEnvVar
!macroend

# Function EslNsisRemoveFromPathEnvVar
!macro mkEslNsisRemoveFromPathEnvVar UN
Function ${UN}EslNsisRemoveFromPathEnvVar
	# Retrieve arguments and stack up work variables to restore values at end.
	; stack		; pathElementToRemove pathKey regPath regLoc
	Push $R0	; $R0 pathElementToRemove pathKey regPath regLoc	| $R0 used for the string with removal
	Exch 4		; regLoc pathElementToRemove pathKey regPath $R0
	Exch $R1	; $R1 pathElementToRemove pathKey regPath $R0		| $R1<-regLoc
	Exch 3		; regPath pathElementToRemove pathKey $R1 $R0 
	Exch $R2	; $R2 pathElementToRemove pathKey $R1 $R0 			| $R2<-regPath
	Exch 2		; pathKey pathElementToRemove $R2 $R1 $R0 
	Exch $R3	; $R3 pathElementToRemove $R2 $R1 $R0 				| $R3<-pathKey
	Exch 1		; pathElementToRemove $R3 $R2 $R1 $R0
	Exch $R4	; $R4 $R2 $R1 $R0 									| $R4<-pathElementToRemove
	Push $R5	; $R5 $R4 $R2 $R1 $R0 								| $R5 used for pathKey's value
	${If} $R1 == HKLM
		ReadRegStr $R5 HKLM $R2 $R3 # get the pathKey's value in R5
	${ElseIf} $R1 == HKCU
		ReadRegStr $R5 HKCU $R2 $R3 # get the pathKey's value in R5
	${Else}
		Return # without doing anything
	${EndIf}
	${${UN}EslNsisRemoveFromPath} $R0 $R5 $R4 # get the updated value in R0
	${If} $R1 == HKLM
		WriteRegStr HKLM $R2 $R3 $R0 # write it back
	${ElseIf} $R1 == HKCU
		WriteRegStr HKCU $R2 $R3 $R0 # write it back
	${EndIf}
# MessageBox MB_OK "-${UN}EslNsisRemoveFromPathEnvVar $R0 $R1 $R2 $R3 $R4 $R5"
	# Restore values of work variables from stack.
	Pop $R5
	Pop $R4
	Pop $R3
	Pop $R2
	Pop $R1
	Pop $R0
FunctionEnd
!macroend   # mkEslNsisRemoveFromPathEnvVar UN
!insertmacro mkEslNsisRemoveFromPathEnvVar ""
!insertmacro mkEslNsisRemoveFromPathEnvVar "un."

# Macro ${EslNsisAddToPath} finalPath(out) pathStr(in) pathElementToAdd(in) appendPrepend(in)
# Adds pathElementToAdd (a path element) to a pathStr, a path separated 
# by semi-colons (;), and returns the finalPath.
# If appendPrepend = "P" it prepends, anything else (such as "A") it appends the element.
# But it first checks if the NSIS can handle the new string length, assuming that the 
# EslNsisMaxStrLen has been set, and if it can't do the add the finalPath will be empty.
!define EslNsisAddToPath "!insertmacro EslNsisAddToPath"
!macro  EslNsisAddToPath finalPath pathStr pathElementToAdd appendPrepend
	Push `${pathStr}`
	Push `${pathElementToAdd}`
	Push `${appendPrepend}`
	Call EslNsisAddToPath
	Pop  `${finalPath}`
!macroend
!define un.EslNsisAddToPath "!insertmacro un.EslNsisAddToPath"
!macro  un.EslNsisAddToPath finalPath pathStr pathElementToAdd appendPrepend
	Push `${pathStr}`
	Push `${pathElementToAdd}`
	Push `${appendPrepend}`
	Call un.EslNsisAddToPath
	Pop  `${finalPath}`
!macroend

# Function EslNsisAddToPath
!macro mkEslNsisAddToPath UN
Function ${UN}EslNsisAddToPath
	# Retrieve arguments and stack up work variables to restore values at end.
	; stack		; appendPrepend pathElementToAdd pathStr
	Push $0		; $0 appendPrepend pathElementToAdd pathStr	| $0 used to build and return finalPath
	Exch 3		; pathStr appendPrepend pathElementToAdd $0
	Exch $1		; $1 appendPrepend pathElementToAdd $0		| $1<-pathStr
	Exch 2		; pathElementToAdd appendPrepend $1 $0 
	Exch $2		; $2 appendPrepend $1 $0 					| $2<-pathElementToAdd
	Exch 1		; appendPrepend $2 $1 $0
	Exch $3		; $3 $2 $1 $0 								| $3<-appendPrepend
	Push $4		; $4 $3 $2 $1 $0							| $4 used in getting EslNsisMaxStrLen set and then for last char in value
	Push $5		; $5 $4 $3 $2 $1 $0							| $5 used for length of value
	Push $6		; $6 $5 $4 $3 $2 $1 $0						| $6 used for length to be added
	Push $7		; $7 $6 $5 $4 $3 $2 $1 $0					| $7 used for total length
	StrCpy $0 "" # use $0 to build the final path
	# Check lengths can be handled.
	StrLen $5 $1 # length of value
	StrLen $6 $2 # length to be added (without ;)
	IntOp $7 $5 + $6 # use $7 for total length
	IntOp $7 $7 + 2 # for ; and one more for luck
	###${${UN}EslNsisGetMaxStrLen} $4 # ensure EslNsisMaxStrLen set
	${If} $7 < ${NSIS_MAX_STRLEN}
		${If} $1 == ""
			StrCpy $0 $2 # no previous (content in) pathStr - so set to pathElementToAdd
		${ElseIf} $3 == "P"
			StrCpy $0 "$2;$1" # prepend into $0
		${Else}
			StrCpy $4 $1 "" -1 # last char in value
			${If} $4 != ";" # value doesn't ends in ;
				StrCpy $1 "$1;" # so append one
			${EndIf}
			StrCpy $0 "$1$2" # append into $0
		${EndIf}
	${EndIf}
# MessageBox MB_OK "-${UN}EslNsisAddToPath $0 $1 $2 $3 $4 $5 $6 $7"
	# Restore values of work variables from stack.
	Pop $7
	Pop $6
	Pop $5
	Pop $4
	Pop $3
	Pop $2
	Pop $1		; stack: $0
	# Push work $0=finalPath onto stack
	Push $0		; finalPath $0
	Exch		; $0 finalPath
	# Restore orig value into $0
	Pop $0		; finalPath result left on stack - is popped by macro
FunctionEnd
!macroend   # mkEslNsisAddToPath UN
!insertmacro mkEslNsisAddToPath ""
!insertmacro mkEslNsisAddToPath "un."

# Macro ${EslNsisAddToPathEnvVar} regLoc(in) regPath(in) pathEnvVar(in) pathElementToAdd(in) appendPrepend(in)
# Invokes the ${EslNsisAddToPath} macro on a regPath/pathKey in the registry.
# Shows a MessageBox if it can't be done.
# regLoc can be HKLM or HKCU.
!define EslNsisAddToPathEnvVar "!insertmacro EslNsisAddToPathEnvVar"
!macro  EslNsisAddToPathEnvVar regLoc regPath pathKey pathElementToAdd appendPrepend
	Push `${regLoc}`
	Push `${regPath}`
	Push `${pathKey}`
	Push `${pathElementToAdd}`
	Push `${appendPrepend}`
	Call EslNsisAddToPathEnvVar
!macroend
!define un.EslNsisAddToPathEnvVar "!insertmacro un.EslNsisAddToPathEnvVar"
!macro  un.EslNsisAddToPathEnvVar regLoc regPath pathKey pathElementToAdd appendPrepend
	Push `${regLoc}`
	Push `${regPath}`
	Push `${pathKey}`
	Push `${pathElementToAdd}`
	Push `${appendPrepend}`
	Call un.EslNsisAddToPathEnvVar
!macroend

# Function EslNsisAddToPathEnvVar
!macro mkEslNsisAddToPathEnvVar UN
Function ${UN}EslNsisAddToPathEnvVar
	# Retrieve arguments and stack up work variables to restore values at end.
	; stack		; appendPrepend pathElementToAdd pathKey regPath regLoc
	Push $R0	; $R0 appendPrepend pathElementToAdd pathKey regPath regLoc	| $R0 used for the string with addition
	Exch 5		; regLoc appendPrepend pathElementToAdd pathKey regPath $R0
	Exch $R1	; $R1 appendPrepend pathElementToAdd pathKey regPath $R0	| $R1<-regLoc
	Exch 4		; regPath appendPrepend pathElementToAdd pathKey $R1 $R0 
	Exch $R2	; $R2 appendPrepend pathElementToAdd pathKey $R1 $R0 		| $R2<-regPath
	Exch 3		; pathKey appendPrepend pathElementToAdd $R2 $R1 $R0 
	Exch $R3	; $R3 appendPrepend pathElementToAdd $R2 $R1 $R0 			| $R3<-pathKey
	Exch 2		; pathElementToAdd appendPrepend $R3 $R2 $R1 $R0
	Exch $R4	; $R4 appendPrepend $R2 $R1 $R0 							| $R4<-pathElementToAdd
	Exch 1		; appendPrepend $R4 $R3 $R2 $R1 $R0
	Exch $R5	; $R5 R4 $R2 $R1 $R0 										| $R5<-appendPrepend
	Push $R6	; $R6 $R5 $R4 $R2 $R1 $R0 									| $R6 used for pathKey's value
	Push $0		; $0 $R6 $R5 R4 $R2 $R1 $R0									| $0 used to say append or prepend if have to do message
	${If} $R1 == HKLM
		ReadRegStr $R6 HKLM $R2 $R3 # get the pathKey's value in R6
	${ElseIf} $R1 == HKCU
		ReadRegStr $R6 HKCU $R2 $R3 # get the pathKey's value in R6
	${Else}
		Return # without doing anything
	${EndIf}
	${${UN}EslNsisAddToPath} $R0 $R6 $R4 $R5 # get the updated value in R0 (which may be empty if couldn't do it)
	${If} $R0 != ""
		${If} $R1 == HKLM
			WriteRegStr HKLM $R2 $R3 $R0 # write it back
		${ElseIf} $R1 == HKCU
			WriteRegStr HKCU $R2 $R3 $R0 # write it back
		${EndIf}
	${Else}
		StrCpy $0 append
		${If} $R5 == "P"
			StrCpy $0 prepend
		${EndIf}
		MessageBox MB_OK 'Insufficient installer memory to $0 "$R4" into "$R3"$\r$\nWe recommend you add it manually after the installation'
	${EndIf}
# MessageBox MB_OK "-${UN}EslNsisAddToPathEnvVar $0 $R0 $R1 $R2 $R3 $R4 $R5 $R6"
	# Restore values of work variables from stack.
	Pop $0
	Pop $R6
	Pop $R5
	Pop $R4
	Pop $R3
	Pop $R2
	Pop $R1
	Pop $R0
FunctionEnd
!macroend   # mkEslNsisAddToPathEnvVar UN
!insertmacro mkEslNsisAddToPathEnvVar ""
!insertmacro mkEslNsisAddToPathEnvVar "un."

!endif # !___ESL_NSIS_UTILS___
