import re
import sys
from enum import Enum
import os.path
import wx
import wx.stc as stc
from .. import utils as Utils
from ..esl.lexer import EslLexer, EslTokenType, EslMultilineTokens
from ..esl.esl import EslKeywords, EslTypeNames, EslReservedVariables, EslAlgoNames, EslStandardFunctions
from ..esl.esl import EslFoldLevelPlusKeywords, EslFoldLevelMinusKeywords
from .view import View
from ..esl.parseesl import ParseEsl

class Stc(stc.StyledTextCtrl):

    # copied essentially from StyledTextCtrl_2 (setup for Python)
    if wx.Platform == '__WXMSW__':
        Faces = {'times': 'Times New Roman',
                 'mono': 'Courier New',
                 'helv': 'Arial',
                 'other': 'Comic Sans MS',
                 'size': 10,
                 'size2': 8,
                 }
    elif wx.Platform == '__WXMAC__':
        Faces = {'times': 'Times New Roman',
                 'mono': 'Monaco',
                 'helv': 'Arial',
                 'other': 'Comic Sans MS',
                 'size': 12,
                 'size2': 10,
                 }
    else:
        Faces = {'times': 'Times',
                 'mono': 'Monospace',
                 'helv': 'Helvetica',
                 'other': 'new century schoolbook',
                 'size': 12,
                 'size2': 10,
                 }

    class Style(Enum):
        Unknown = 0
        ESL = 1
        Text = 2
        XML = 3
        CPP = 4
        Fortran = 5
        Python = 6

    Lexers = {
        Style.ESL: stc.STC_LEX_CONTAINER,
        Style.Text: stc.STC_LEX_NULL,
        Style.XML: stc.STC_LEX_XML,
        Style.CPP: stc.STC_LEX_CPP,
        Style.Fortran: stc.STC_LEX_FORTRAN,
        Style.Python: stc.STC_LEX_PYTHON
    }

    EncryptFoldOffset = 5

    def __init__(self, parent):
        stc.StyledTextCtrl.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize)
        self._parent = parent
        self._frame = wx.GetApp().frame()
        self._control = None
        if self._frame:
            self._control = self._frame.control()
        self._filepath = ""
        self.readOnly = True
        self.inModalDlg = False
        self.SetReadOnly(self.readOnly)
        self._eslLexer = EslLexer()
        self.registerEvents()
        self.setup()
        self._style = Stc.Style.Text
        self.setStyle(self._style)

        self._parseEsl = None

        self._find_text = ""
        self._find_pos = 0
        self._find_end = 0
        self._find_in_whole_file = True # Do the find (or find next) over whole file, else from current caret position.

        self.UsePopUp(stc.STC_POPUP_NEVER)
        self.Bind(wx.EVT_CONTEXT_MENU, self.showContextMenu)
        self.Bind(wx.EVT_MENU_RANGE, self.onContextMenuItem)
        self._allowToggleEdit = False
        self._allowSave = False
        self._allowCommitESL = False
        self._allowRunESLDirect = False
        id = wx.ID_HIGHEST + 101
        self._id_edit = id; id += 1
        self._id_save = id; id += 1
        self._id_saveas = id; id += 1
        self._id_commitesl = id; id += 1
        self._id_run_esl_direct = id; id += 1
        self._id_code_checks = id; id += 1
        self._id_run_compiler = id; id += 1
        self._id_undo = id; id += 1
        self._id_redo = id; id += 1
        self._id_cut = id; id += 1
        self._id_copy = id; id += 1
        self._id_paste = id; id += 1
        self._id_delete = id; id += 1
        self._id_wrap = id; id += 1
        self._id_folding = id; id += 1
        self._id_linenrs = id; id += 1
        self._id_whitespace = id; id += 1
        self._id_selectall = id; id += 1
        self._id_goto = id; id += 1
        self._id_find = id; id += 1
        self._id_find_next = id; id += 1
        self._id_find_prev = id; id += 1

    def style(self):
        return self._style

    def filepath(self):
        return self._filepath

    def setReadOnly(self, readOnly):
        self.readOnly = readOnly
        self.SetReadOnly(self.readOnly)

    def setAllowToggleEdit(self, allowToggleEdit):
        self._allowToggleEdit = allowToggleEdit

    def setAllowSave(self, allowSave):
        self._allowSave = allowSave

    def setAllowCommitESL(self, allowCommitESL):
        self._allowCommitESL = allowCommitESL

    def setAllowRunESLDirect(self, allowRunESLDirect):
        self._allowRunESLDirect = allowRunESLDirect

    def LoadFile(self, filepath, readOnly=True):
        ok = True
        text = ""
        extn = ".esl"
        if filepath:
            useFilepath = filepath
            if not os.path.exists(filepath):
                useFilepath = Utils.eslFile(filepath)
            root, extn = os.path.splitext(useFilepath)
            file = None
            try:
                file = open(useFilepath, 'r')
            except Exception:
                ok = False
                msg = 'Failed to open file "' + filepath + '"\n'
                if self._control:
                    self._control.appendMessage(msg)
                else:
                    wx.MessageBox(msg)
            if ok and file and not file.closed:
                try:
                    text = file.read()
                except Exception:
                    ok = False
                    msg = 'Failed to read file "' + filepath + '"\n'
                    if self._control:
                        self._control.appendMessage(msg)
                    else:
                        wx.MessageBox(msg)
            if file and not file.closed:
                file.close()
        if ok:
            self._filepath = filepath
            self.setReadOnly(readOnly)
            self.setStcText(text, extn)
        return ok

    def setup(self):
        # Use Ctrl + - to zoom
        self.CmdKeyAssign(ord('+'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('='), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('-'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)
        self.CmdKeyAssign(ord('_'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)
        # Enable folding
        self.SetProperty("fold", "1")
        self.SetProperty("fold.compact", "1")
        self.SetProperty("fold.comment", "1")
        self.SetProperty("fold.preprocessor", "1")
        self.SetProperty("fold.html", "1")
        self.SetProperty("fold.html.preprocessor", "1")
        # Highlight tab/space mixing (shouldn't be any)
        self.SetProperty("tab.timmy.whinge.level", "1")
        # Set left and right margins
        self.SetMargins(0, 0)
        # Set up the numbers in the margin for margin #1
        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        # Reasonable value for, say, 4-5 digits using a mono font (40 pix)
        self.SetMarginWidth(1, 40)
        # Indentation and tab stuff
        self.SetIndent(4)  # Proscribed indent size for wx
        #self.SetIndentationGuides(True)  # Show indent guides
        self.SetBackSpaceUnIndents(True)  # Backspace unindents rather than delete 1 space
        self.SetTabIndents(True)  # Tab key indents
        self.SetTabWidth(4)  # Proscribed tab size for wx
        self.SetUseTabs(False)  # Use spaces rather than tabs, or
        # TabTimmy will complain!
        # White space
        self.SetViewWhiteSpace(False)  # Don't view white space
        # EOL: Since we are loading/saving ourselves, and the
        # strings will always have \n's in them, set the STC to
        # edit them that way.
        self.SetEOLMode(wx.stc.STC_EOL_LF)
        self.SetViewEOL(False)
        # No right-edge mode indicator
        self.SetEdgeMode(stc.STC_EDGE_NONE)
        # self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
        # Setup a margin to hold fold markers
        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)
        # self.SetBufferedDraw(False)
        # self.SetEOLMode(stc.STC_EOL_CRLF)
        # self.SetUseAntiAliasing(True)
        self.SetEdgeColumn(78)

        self.SetWrapMode(stc.STC_WRAP_WORD)

        # and now set up the fold markers
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, "white", "black")

        # Caret color
        self.SetCaretForeground("BLUE")
        # Selection background
        #self.SetSelBackground(1, '#66CCFF')
        #self.SetSelBackground(True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        #self.SetSelForeground(True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))

        self._DimGrey = "#696969"
        self._Navy = "#000080"
        self._Blue = "#0000FF"
        self._SlateBlue = "#6A5ACD"
        self._DarkCyan = "#008B8B"
        self._Green = "#008000" # wx seems to do #00ff00 on windows
        self._DarkGreen = "#006400"
        self._Olive = "#808000"
        self._DarkMagenta = "#8B008B"
        self._DarkRed = "#8B0000"
        self._Red = "#FF0000"
        self._Sienna = "#A0522D"
        self._Yellow = "#FFFF00"
        self._Wheat = "#F5DEB3"

        # Global default styles for all languages
        self._fixed = "fore:Black,face:%(mono)s,size:%(size)d" % Stc.Faces
        self._proportional    = "fore:Black,face:%(helv)s,size:%(size)d" % Stc.Faces
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     self._proportional)
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % Stc.Faces)
        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % Stc.Faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")

        # Code style specifications
        self._codeDefault   = self._fixed
        self._identifier    = "fore:Black,face:%(mono)s,size:%(size)d" % Stc.Faces
        self._number        = "fore:"+self._Navy+",face:%(mono)s,size:%(size)d" % Stc.Faces    # #007F7F dark cyan - closest CYAN4 #008B8B [html has teal #008080
        self._string        = "fore:"+self._DarkRed+",face:%(mono)s,size:%(size)d" % Stc.Faces    # #7F007F dark magenta - looks like PURPLE #A020F0 or DARK VIOLET #9400D3 (or PURPLE3)
        self._string2       = "fore:"+self._Sienna+",face:%(mono)s,size:%(size)d" % Stc.Faces
        self._highlight     = "fore:"+self._Red+",back:"+self._Yellow+",face:%(mono)s,size:%(size)d" % Stc.Faces    # eg. unterminated string
        self._highlight2    = "fore:"+self._DarkMagenta+",back:"+self._Wheat+",face:%(mono)s,size:%(size)d" % Stc.Faces    # eg. unterminated string
        self._operator      = "fore:Black,face:%(mono)s,size:%(size)d,bold" % Stc.Faces
        self._comment       = "fore:"+self._Green+",face:%(mono)s,size:%(size)d" % Stc.Faces # #007F00 dark green - not really DARK GREEN #006400 - like GREEN4 , #008B00 [visually GREEN isnt
        self._comment2      = "fore:"+self._DarkGreen+",face:%(mono)s,size:%(size)d" % Stc.Faces # #007F00 dark green - not really DARK GREEN #006400 - like GREEN4 , #008B00 [visually GREEN isnt
        self._className     = "fore:"+self._DarkCyan+",face:%(mono)s,size:%(size)d,bold" % Stc.Faces
        self._other         = "fore:"+self._Olive+",face:%(mono)s,size:%(size)d" % Stc.Faces
        self._other2        = "fore:"+self._DarkMagenta+",face:%(mono)s,size:%(size)d" % Stc.Faces
        self._keyword1      = "fore:"+self._Blue+",face:%(mono)s,size:%(size)d,bold" % Stc.Faces # #00007F dork blue closest NAVY BLUE #000080
        self._keyword2      = "fore:"+self._SlateBlue+",face:%(mono)s,size:%(size)d,bold" % Stc.Faces
        self._keyword3      = "fore:"+self._DimGrey+",face:%(mono)s,size:%(size)d,bold" % Stc.Faces # #003F7F closest DEEPSKYBLUE4 #00688B or DarkCyan

        # ESL
        self._eslStyles = {
            EslTokenType.OTHER: self._other, #OTHER = 0
            #EslTokenType.EOL: "fore:Black,back:GOLD,face:%(mono)s,size:%(size)d" % Stc.Faces, #EOL = 1
            EslTokenType.WHITESPACE: self._codeDefault, #"fore:Black,back:RED,face:%(mono)s,size:%(size)d" % Stc.Faces, #WHITESPACE = 2
            EslTokenType.COMMENT: self._comment, #COMMENT = 3
            EslTokenType.NUMBER: self._number, #NUMBER = 4
            EslTokenType.STRING: self._string, #STRING = 5
            EslTokenType.PERCENT_STRING: self._string2, #PERCENT_STRING = 6
            EslTokenType.UNTERMINATED_STRING: self._highlight, #UNTERMINATED_STRING = 7
            EslTokenType.SPECIAL: self._operator, #SPECIAL = 8 - e.g. operators
            EslTokenType.IDENTIFIER: self._identifier, #IDENTIFIER = 9
            EslTokenType.TRANSFER_FN: self._other, #TRANSFER_FN = 10
            EslTokenType.TRANSFER_MATRIX: self._other2, #TRANSFER_MAXTRIX = 11
            EslTokenType.UNTERMINATED_TRANSFER: self._highlight, #UNTERMINATED_TRANSFER = 12
            EslTokenType.INCLUSION: self._highlight, #INCLUSION = 13
            EslTokenType.ENCRYPT: self._highlight2,  # ENCRYPT = 14
            EslTokenType.END_ENCRYPT: self._highlight2,  # END_ENCRYPT = 15
            # keywords of different categories (3)
            EslTokenType.KEYWORDS: self._keyword1,
            EslTokenType.KEYWORDS + 1: self._keyword2,
            EslTokenType.KEYWORDS + 2: self._keyword3,
        }
        self._eslKeywords1 = EslKeywords
        self._eslKeywords2 = EslTypeNames
        self._eslKeywords3 = EslReservedVariables + EslAlgoNames + EslStandardFunctions

        # XML/HTML
        self._xmlStyles = {
            stc.STC_H_DEFAULT: self._codeDefault, # = 0
            stc.STC_H_TAG: self._keyword1, # = 1
            stc.STC_H_TAGUNKNOWN: self._keyword1, # = 2
            stc.STC_H_ATTRIBUTE: self._className, # = 3
            stc.STC_H_ATTRIBUTEUNKNOWN: self._className, # = 4
            stc.STC_H_NUMBER: self._number, # = 5
            stc.STC_H_DOUBLESTRING: self._string, # = 6
            stc.STC_H_SINGLESTRING: self._string2, # = 7
            stc.STC_H_OTHER: self._other, # = 8
            stc.STC_H_COMMENT: self._comment, # = 9
            stc.STC_H_ENTITY: self._keyword3, # = 10
            stc.STC_H_TAGEND: self._keyword1, # = 11
            stc.STC_H_XMLSTART: self._highlight, # = 12
            stc.STC_H_XMLEND: self._highlight, # = 13
            stc.STC_H_SCRIPT: self._codeDefault + ",italic", # = 14 - this is not the script - which is proportional
            stc.STC_H_ASP: self._codeDefault, # = 15
            stc.STC_H_ASPAT: self._codeDefault, # = 16
            stc.STC_H_CDATA: self._other2, # = 17
            stc.STC_H_QUESTION: self._keyword3, # = 18
            stc.STC_H_VALUE: self._number, # = 19
            stc.STC_H_XCCOMMENT: self._comment2, # = 20
            stc.STC_H_SGML_DEFAULT: self._codeDefault,  # = 21
            stc.STC_H_SGML_COMMAND: self._codeDefault,  # = 22
            stc.STC_H_SGML_1ST_PARAM: self._codeDefault,  # = 23
            stc.STC_H_SGML_DOUBLESTRING: self._codeDefault,  # = 24
            stc.STC_H_SGML_SIMPLESTRING: self._codeDefault,  # = 25
            stc.STC_H_SGML_ERROR: self._codeDefault,  # = 26
            stc.STC_H_SGML_SPECIAL: self._codeDefault,  # = 27
            stc.STC_H_SGML_ENTITY: self._codeDefault,  # = 28
            stc.STC_H_SGML_COMMENT: self._codeDefault,  # = 29
            stc.STC_H_SGML_1ST_PARAM_COMMENT: self._codeDefault,  # = 30
            stc.STC_H_SGML_BLOCK_DEFAULT: self._codeDefault,  # = 31
            # There something unlisted for script - but as defaults to proportional which looks ok, leave it be
        }
        # no keywords

        # C/CPP
        self._cppStyles = {
            stc.STC_C_DEFAULT: self._codeDefault,  # = 0
            stc.STC_C_COMMENT: self._comment,  # = 1
            stc.STC_C_COMMENTLINE: self._comment,  # = 2
            stc.STC_C_COMMENTDOC: self._comment2,  # = 3
            stc.STC_C_NUMBER: self._number,  # = 4
            stc.STC_C_WORD: self._keyword1,  # = 5
            stc.STC_C_STRING: self._string,  # = 6
            stc.STC_C_CHARACTER: self._string2,  # = 7
            stc.STC_C_UUID: self._highlight,  # = 8
            stc.STC_C_PREPROCESSOR: self._other2,  # = 9
            stc.STC_C_OPERATOR: self._operator,  # = 10
            stc.STC_C_IDENTIFIER: self._identifier,  # = 11
            stc.STC_C_STRINGEOL: self._highlight,  # = 12
            stc.STC_C_VERBATIM: self._other,  # = 13
            stc.STC_C_REGEX: self._codeDefault,  # = 14
            stc.STC_C_COMMENTLINEDOC: self._comment2,  # = 15
            stc.STC_C_WORD2: self._keyword2,  # = 16
            stc.STC_C_COMMENTDOCKEYWORD: self._codeDefault,  # = 17
            stc.STC_C_COMMENTDOCKEYWORDERROR: self._codeDefault,  # = 18
            stc.STC_C_GLOBALCLASS: self._className,  # = 19
            stc.STC_C_STRINGRAW: self._string2,  # = 20
            stc.STC_C_TRIPLEVERBATIM: self._other,  # = 21
            stc.STC_C_HASHQUOTEDSTRING: self._codeDefault,  # = 22
            stc.STC_C_PREPROCESSORCOMMENT: self._other2,  # = 23
            stc.STC_C_PREPROCESSORCOMMENTDOC: self._other2,  # = 24
            stc.STC_C_USERLITERAL: self._codeDefault,  # = 25
            stc.STC_C_TASKMARKER: self._codeDefault,  # = 26
            stc.STC_C_ESCAPESEQUENCE: self._codeDefault,  # = 27
            # There are also unlisted specs (show as proportional) - see in setStyle.
        }
        # From the wxwidgets sample
        #self._cppKeywords1 = "asm auto bool break case catch char class const const_cast continue default delete do double dynamic_cast else enum explicit export extern false float for friend goto if inline int long mutable namespace new operator private protected public register reinterpret_cast return short signed sizeof static static_cast struct switch template this throw true try typedef typeid typename union unsigned using virtual void volatile wchar_t while"
        # From Geany
        self._cppKeywords1 = "alignas alignof and and_eq asm auto bitand bitor bool break case catch char char16_t char32_t class compl const const_cast constexpr continue decltype default delete do double dynamic_cast else enum explicit export extern false final float for friend goto if inline int long mutable namespace new noexcept not not_eq nullptr operator or or_eq override private protected public register reinterpret_cast return short signed sizeof static static_assert static_cast struct switch template this thread_local throw true try typedef typeid typename union unsigned using virtual void volatile wchar_t while xor xor_eq"
        # +plus keep
        self._cppKeywords2 = "file"

        # Fortran
        self._fortranStyles = {
            stc.STC_F_DEFAULT: self._codeDefault, # = 0
            stc.STC_F_COMMENT: self._comment, # = 1
            stc.STC_F_NUMBER: self._number, # = 2
            stc.STC_F_STRING1: self._string, # = 3
            stc.STC_F_STRING2: self._string2, # = 4
            stc.STC_F_STRINGEOL: self._highlight, # = 5
            stc.STC_F_OPERATOR: self._operator, # = 6
            stc.STC_F_IDENTIFIER: self._identifier, # = 7
            stc.STC_F_WORD: self._keyword1, # = 8
            stc.STC_F_WORD2: self._keyword2, # = 9
            stc.STC_F_WORD3: self._keyword3, # = 10
            stc.STC_F_PREPROCESSOR: self._other2, # = 11
            stc.STC_F_OPERATOR2: self._operator, # = 12
            stc.STC_F_LABEL: self._other, # = 13
            stc.STC_F_CONTINUATION: self._highlight, # = 14
        }
        # My inference based on Fortran 95/2003/2008 Keywords https://eng.libretexts.org/Bookshelves/Computer_Science/Programming_Languages/Introduction_to_Programming_using_Fortran_95_2003_2008_(Jorgensen)/27%3A_Appendix_7_-_Fortran_95_2003_2008_Keywords/27.01%3A_Fortran_95_2003_2008_Keywords
        #self._fortranKeywords1 = "allocate backspace call case character close complex contains cycle deallocate default do else elseif elsewhere end enddo endfile endfunction endif endinterface endmodule endprogram endselect endsubroutine endtype endwhere exit format function if implicit inquire integer interface intrinsic logical module module namelist nullify open print private program public read real return rewind select selectcase stop subroutine then type use where while write"
        #self._fortranKeywords2 = "allocatable assignment intent kind len only operator optional pointer recursive result target"
        #self._fortranKeywords3 = "in inout out"
        # From Geany
        self._fortranKeywords1 = "abstract access action advance all allstop allocatable allocate apostrophe assign assignment associate asynchronous backspace bind blank block blockdata call case character class close codimension common complex concurrent contains contiguous continue critical cycle data deallocate decimal delim default dimension direct do dowhile double doubleprecision elemental else elseif elsewhere encoding end endassociate endblock endblockdata endcritical enddo endfile endforall endfunction endif endinterface endmodule endprocedure endprogram endselect endsubmodule endsubroutine endtype endwhere entry enum enumerator eor equivalence err errmsg exist exit extends external file final flush fmt forall form format formatted function generic go goto id if images implicit import impure in include inout integer inquire intent interface intrinsic iomsg iolength iostat is kind len lock logical memory module name named namelist nextrec nml non_intrinsic non_overridable none nopass nullify number only open opened operator optional out pad parameter pass pause pending pointer pos position precision print private procedure program protected public quote pure read readwrite real rec recl recursive result return rewind save select selectcase selecttype sequential sign size stat status stop stream submodule subroutine sync syncall syncimages syncmemory target then to type unformatted unit unlock use value volatile wait where while write"
        self._fortranKeywords2 = "abs achar acos acosd acosh adjustl adjustr aimag aimax0 aimin0 aint ajmax0 ajmin0 akmax0 akmin0 all allocated alog alog10 amax0 amax1 amin0 amin1 amod anint any asin asind asinh associated atan atan2 atan2d atand atanh atomic_define atomic_ref bessel_j0 bessel_j1 bessel_jn bessel_y0 bessel_y1 bessel_yn bge bgt bit_size bitest bitl bitlr bitrl bjtest bktest ble blt break btest c_associated c_f_pointer c_f_procpointer c_funloc c_loc c_sizeof cabs ccos cdabs cdcos cdexp cdlog cdsin cdsqrt ceiling cexp char clog cmplx command_argument_count conjg cos cosd cosh count cpu_time cshift csin csqrt dabs dacos dacosd dasin dasind datan datan2 datan2d datand date date_and_time dble dcmplx dconjg dcos dcosd dcosh dcotan ddim dexp dfloat dfloti dflotj dflotk digits dim dimag dint dlog dlog10 dmax1 dmin1 dmod dnint dot_product dprod dreal dshiftl dshiftr dsign dsin dsind dsinh dsqrt dtan dtand dtanh eoshift epsilon erf erfc erfc_scaled errsns execute_command_line exp exponent extends_type_of findloc float floati floatj floatk floor fraction free gamma get_command get_command_argument get_environment_variable huge hypot iabs iachar iall iand iany ibclr ibits ibset ichar idate idim idint idnint ieor ifix iiabs iiand iibclr iibits iibset iidim iidint iidnnt iieor iifix iint iior iiqint iiqnnt iishft iishftc iisign ilen image_index imax0 imax1 imin0 imin1 imod index inint inot int int1 int2 int4 int8 ior iparity iqint iqnint is_contiguous is_isostat_end is_isostat_eor ishft ishftc isign isnan izext jiand jibclr jibits jibset jidim jidint jidnnt jieor jifix jint jior jiqint jiqnnt jishft jishftc jisign jmax0 jmax1 jmin0 jmin1 jmod jnint jnot jzext kiabs kiand kibclr kibits kibset kidim kidint kidnnt kieor kifix kind kint kior kishft kishftc kisign kmax0 kmax1 kmin0 kmin1 kmod knint knot kzext lbound lcobound leadz len len_trim lge lgt lle llt log log10 log_gamma logical lshift malloc maskl maskr matmul max max0 max1 maxexponent maxloc maxval merge merge_bits min min0 min1 minexponent minloc minval mod modulo move_alloc mvbits nearest new_line nint norm2 not null num_images number_of_processors nworkers pack parity popcnt poppar precision present product radix random random_number random_seed range real repeat reshape rrspacing rshift same_type_as scale scan secnds selected_char_kind selected_int_kind selected_real_kind set_exponent shape shifta shiftl shiftr sign sin sind sinh size sizeof sngl snglq spacing spread sqrt storage_size sum system_clock tan tand tanh this_image tiny trailz transfer transpose trim ubound ucobound unpack verify"
        self._fortranKeywords3 = "cdabs cdcos cdexp cdlog cdsin cdsqrt cotan cotand dcmplx dconjg dcotan dcotand decode dimag dll_export dll_import doublecomplex dreal dvchk encode find flen flush getarg getcharqq getcl getdat getenv gettim hfix ibchng identifier imag int1 int2 int4 intc intrup invalop iostat_msg isha ishc ishl jfix lacfar locking locnear map nargs nbreak ndperr ndpexc offset ovefl peekcharqq precfill prompt qabs qacos qacosd qasin qasind qatan qatand qatan2 qcmplx qconjg qcos qcosd qcosh qdim qexp qext qextd qfloat qimag qlog qlog10 qmax1 qmin1 qmod qreal qsign qsin qsind qsinh qsqrt qtan qtand qtanh ran rand randu rewrite segment setdat settim system timer undfl unlock union val virtual volatile zabs zcos zexp zlog zsin zsqrt"

        # Python
        self._pythonStyles = {
            stc.STC_P_DEFAULT: self._codeDefault,  # = 0
            stc.STC_P_COMMENTLINE: self._comment,  # = 1
            stc.STC_P_NUMBER: self._number,  # = 2
            stc.STC_P_STRING: self._string,  # = 3
            stc.STC_P_CHARACTER: self._string2,  # = 4 #7F007F
            stc.STC_P_WORD: self._keyword1,  # = 5
            stc.STC_P_TRIPLE: self._string2,  # = 6 #7F0000        # triple single quoted doc string
            stc.STC_P_TRIPLEDOUBLE: self._string,  # = 7 #7F0000  # triple double quoted doc string
            stc.STC_P_CLASSNAME: self._className,  # = 8 #0000FF
            stc.STC_P_DEFNAME: self._other,  # = 9 #007F7F
            stc.STC_P_OPERATOR: self._operator,  # = 10
            stc.STC_P_IDENTIFIER: self._identifier,  # = 11
            stc.STC_P_COMMENTBLOCK: self._comment2, # = 12 #7F7F7F  # double hashed comment
            stc.STC_P_STRINGEOL: self._highlight, # = 13   # ? when a string hits EOL - i.e. unterminated?
            stc.STC_P_WORD2: self._keyword2,  # = 14
            stc.STC_P_DECORATOR: self._other2, # = 15 #003F7F
        }
        # From the wxpython demo + my self
        #self._pythonKeywords1 = " ".join(keyword.kwlist)
        #self._pythonKeywords2 = "self"
        # From Geany + my self & cls
        self._pythonKeywords1 = "False None True and as assert async await break class continue def del elif else except exec finally for from global if import in is lambda nonlocal not or pass print raise return try while with yield"
        self._pythonKeywords2 = "ArithmeticError AssertionError AttributeError BaseException BlockingIOError BrokenPipeError BufferError BytesWarning ChildProcessError ConnectionAbortedError ConnectionError ConnectionRefusedError ConnectionResetError DeprecationWarning EOFError Ellipsis EnvironmentError Exception FileExistsError FileNotFoundError FloatingPointError FutureWarning GeneratorExit IOError ImportError ImportWarning IndentationError IndexError InterruptedError IsADirectoryError KeyError KeyboardInterrupt LookupError MemoryError ModuleNotFoundError NameError NotADirectoryError NotImplemented NotImplementedError OSError OverflowError PendingDeprecationWarning PermissionError ProcessLookupError RecursionError ReferenceError ResourceWarning RuntimeError RuntimeWarning StandardError StopAsyncIteration StopIteration SyntaxError SyntaxWarning SystemError SystemExit TabError TimeoutError TypeError UnboundLocalError UnicodeDecodeError UnicodeEncodeError UnicodeError UnicodeTranslateError UnicodeWarning UserWarning ValueError Warning ZeroDivisionError __build_class__ __debug__ __doc__ __import__ __loader__ __name__ __package__ __spec__ abs all any apply ascii basestring bin bool breakpoint buffer bytearray bytes callable chr classmethod cmp coerce compile complex copyright credits delattr dict dir divmod enumerate eval execfile exit file filter float format frozenset getattr globals hasattr hash help hex id input int intern isinstance issubclass iter len license list locals long map max memoryview min next object oct open ord pow property quit range raw_input reduce reload repr reversed round set setattr slice sorted staticmethod str sum super tuple type unichr unicode vars xrange zip"
        self._pythonKeywords2 = self._pythonKeywords2 + " self cls"

    def registerEvents(self):
        #self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
        self.Bind(stc.EVT_STC_STYLENEEDED, self.OnStyleNeeded)
        #self.Bind(stc.EVT_STC_MODIFIED, self.OnModified)
        #self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)

    def setStyle(self, style):
        self._style = style
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, self._proportional)
        self.StyleClearAll()
        self.SetIndentationGuides(False)
        lexer = Stc.Lexers.get(style, stc.STC_LEX_NULL)
        self.SetLexer(lexer)
        if style == Stc.Style.ESL:
            for index, styleSpec in self._eslStyles.items():
                self.StyleSetSpec(index, styleSpec)
            pass
        elif style == Stc.Style.Text:
            pass
        elif style == Stc.Style.XML:
            for index, styleSpec in self._xmlStyles.items():
                self.StyleSetSpec(index, styleSpec)
            pass
        elif style == Stc.Style.CPP:
            self.SetKeyWords(0, self._cppKeywords1)
            self.SetKeyWords(1, self._cppKeywords2)
            for index, styleSpec in self._cppStyles.items():
                self.StyleSetSpec(index, styleSpec)
            pass
            # Unlisted specs show as proportional - so clobber with codeDefault
            #for i in range(stc.STC_C_ESCAPESEQUENCE+1, 76): #needs 73,75 - and who knows what else
            for i in range(64, 80):
                self.StyleSetSpec(i, self._codeDefault)
        elif style == Stc.Style.Fortran:
            self.SetKeyWords(0, self._fortranKeywords1)
            self.SetKeyWords(1, self._fortranKeywords2)
            self.SetKeyWords(2, self._fortranKeywords3)
            for index, styleSpec in self._fortranStyles.items():
                self.StyleSetSpec(index, styleSpec)
            pass
        elif style == Stc.Style.Python:
            self.SetKeyWords(0, self._pythonKeywords1)
            self.SetKeyWords(1, self._pythonKeywords2)
            for index, styleSpec in self._pythonStyles.items():
                self.StyleSetSpec(index, styleSpec)
            pass
            #self.SetIndentationGuides(True)  # Show indent guides - cant get these to display at 4 fixed chars
            #self.SetIndent(4)
            #self.SetTabWidth(4)
        else:
            pass
        # Enable folding - has to be redone after setting the lexer
        self.SetProperty("fold", "1")
        self.SetProperty("fold.compact", "1")
        self.SetProperty("fold.comment", "1")
        self.SetProperty("fold.preprocessor", "1")
        self.SetProperty("fold.html", "1")
        self.SetProperty("fold.html.preprocessor", "1")

    def setStyleForExtn(self, extn): # extn has a dot
        style = None
        if extn == ".esl": style = Stc.Style.ESL
        elif extn == ".txt": style = Stc.Style.Text
        elif extn in [".h", ".c", ".cpp"] : style = Stc.Style.CPP
        elif extn in [".f", ".for"] : style = Stc.Style.Fortran
        elif extn in [".py", ".pyw"] : style = Stc.Style.Python
        elif extn in [".xml", ".eslstudio", ".eslprofile", ".sec", ".dis"] : style = Stc.Style.XML
        elif extn in [".htm", ".html"]: style = Stc.Style.XML # treat HTML as XML
        if style is not None:
            self.setStyle(style)
        return style

    def setStcText(self, text, extn=None):
        style = None
        if extn:
            style = self.setStyleForExtn(extn)
        if not style:
            # look for <?xml in text
            if len(text) > 5 and text.startswith("<?xml"):
                self.setStyle(Stc.Style.XML)
            else:
                self.setStyle(Stc.Style.Text)
        wasReadOnly = self.GetReadOnly()
        if wasReadOnly: self.SetReadOnly(False)
        self.SetValue(text)
        if wasReadOnly: self.SetReadOnly(True)
        if style == Stc.Style.ESL:
            self.doStyling(0, 0, text)
        self.EmptyUndoBuffer()

    def OnStyleNeeded(self, styledTextEvent):
        startPos = self.GetEndStyled() # where last styled
        posn = styledTextEvent.GetPosition()
        lineNumber = self.LineFromPosition(startPos)
        startLinePos = self.PositionFromLine(lineNumber)
        #print("OnStyleNeeded startPos="+str(startPos)+" lineNumber="+str(lineNumber)+" startLinePos="+str(startLinePos)+
        #      " posn="+str(posn)+"("+str(posn-startLinePos)+") raw="+str(self.GetFoldLevel(lineNumber)))
        text = self.GetTextRange(startLinePos, posn)
        self.doStyling(lineNumber, startLinePos, text)

    def doStyling(self, lineNumber, startLinePos, text):
        #print("doStyling lineNumber="+str(lineNumber)+" startLinePos="+str(startLinePos)+" len(text)="+str(len(text)))
        tokens = []
        self._eslLexer.Tokenise(startLinePos, text, tokens)
        self.StartStyling(startLinePos)
        for token in tokens:
            styleIndex = token.type
            if styleIndex == EslTokenType.IDENTIFIER:
                upperToken = token.text.upper()
                if upperToken in self._eslKeywords1:
                    styleIndex = EslTokenType.KEYWORDS
                elif upperToken in self._eslKeywords2:
                    styleIndex = EslTokenType.KEYWORDS + 1
                elif upperToken in self._eslKeywords3:
                    styleIndex = EslTokenType.KEYWORDS + 2
            # Style the token
            self.SetStyling(token.length, styleIndex)
        pass # for tokens
        self.doFolding(lineNumber, tokens)

    def doFolding(self, lineNumber, tokens):
        foldLevelNr = (self.GetFoldLevel(lineNumber) & stc.STC_FOLDLEVELNUMBERMASK) - stc.STC_FOLDLEVELBASE
        if foldLevelNr == 0 and lineNumber > 0:
            foldLevelNr = (self.GetFoldLevel(lineNumber - 1) & stc.STC_FOLDLEVELNUMBERMASK) - stc.STC_FOLDLEVELBASE
        currentLine = lineNumber
        isFoldHeader = False
        showWhiteFlag = True
        nrNewLines = 0
        nextFoldLevelNr = foldLevelNr
        inEncryptBlock = False
        encryptEslLevel = 0
        eslLevel = foldLevelNr
        if eslLevel >= Stc.EncryptFoldOffset:
            eslLevel -= Stc.EncryptFoldOffset
            encryptEslLevel = eslLevel
            inEncryptBlock = True
        doSetFoldLevel = False
        nTokens = len(tokens)
        iToken = 0
        while True:
            if iToken == nTokens:
                doSetFoldLevel = True
            else:
                token = tokens[iToken]
                iToken += 1
                tokenLine = self.LineFromPosition(token.start)
                if tokenLine > currentLine:
                    doSetFoldLevel = True
                    iToken -= 1 # repeat this token next loop
            if doSetFoldLevel:
                foldLevel = foldLevelNr + stc.STC_FOLDLEVELBASE
                if isFoldHeader:
                    foldLevel |= stc.STC_FOLDLEVELHEADERFLAG
                if showWhiteFlag:
                    foldLevel |= stc.STC_FOLDLEVELWHITEFLAG
                for line in range(currentLine, currentLine + nrNewLines + 1):
                    self.SetFoldLevel(line, foldLevel)
                    #print("doFolding set line=" + str(line)+" foldLevelNr=" + str(foldLevelNr)+" foldLevel="+str(foldLevel))
                if iToken == nTokens:
                    break
                # Reset for next line of tokens
                foldLevelNr = nextFoldLevelNr
                currentLine = tokenLine
                isFoldHeader = False
                showWhiteFlag = True
                nrNewLines = 0
                doSetFoldLevel = False
            else:
                styleIndex = token.type
                if styleIndex in EslMultilineTokens:
                    nrNewLines = token.text.count('\n')
                if showWhiteFlag and styleIndex != EslTokenType.WHITESPACE and styleIndex != EslTokenType.EOL:
                   showWhiteFlag = False
                eslLevelUp = 0
                eslLevelDown = 0
                if token.type == EslTokenType.ENCRYPT:
                    #foldLevelNr stays same
                    inEncryptBlock = True
                    encryptEslLevel = eslLevel
                    nextFoldLevelNr = eslLevel + Stc.EncryptFoldOffset
                    #print("--- ENCR:"+str(eslLevel)+" line="+str(tokenLine+1)+
                    #      " foldLevelNr="+str(foldLevelNr) +
                    #      " nextFoldLevelNr="+str(nextFoldLevelNr))
                    isFoldHeader = True
                elif token.type == EslTokenType.END_ENCRYPT:
                    # foldLevelNr stays same
                    inEncryptBlock = False
                    eslLevel = encryptEslLevel
                    foldLevelNr = eslLevel + Stc.EncryptFoldOffset
                    nextFoldLevelNr = eslLevel
                    #print("--- END :"+str(eslLevel)+" line="+str(tokenLine+1)+
                    #      " foldLevelNr=" + str(foldLevelNr) +
                    #      " nextFoldLevelNr=" + str(nextFoldLevelNr))
                elif styleIndex == EslTokenType.IDENTIFIER:
                    # Check fold level at identifier token
                    upperToken = token.text.upper()
                    eslLevelDown = EslFoldLevelMinusKeywords.get(upperToken, -1)
                    eslLevelUp = EslFoldLevelPlusKeywords.get(upperToken, -1)
                    if eslLevelUp > 0: # DO [#>= 0:  # DONT] treat 0 (STUDY) as no fold
                        if not isFoldHeader: # ignore a second Up on the same line
                            #foldLevelNr stays same normally
                            if eslLevelUp == eslLevel:
                                foldLevelNr -= 1 # this make a fold point at the same eslLevel
                            eslLevel = eslLevelUp
                            nextFoldLevelNr = eslLevel
                            if inEncryptBlock: nextFoldLevelNr += Stc.EncryptFoldOffset
                            isFoldHeader = True
                            #print("--- Up  :"+str(eslLevel)+" line="+str(tokenLine+1)+
                            #      " foldLevelNr=" + str(foldLevelNr) +
                            #      " nextFoldLevelNr="+str(nextFoldLevelNr))
                    if eslLevelDown > 0: # DO [#>= 0: # DONT treat 0 (END_STUDY) as no fold
                        eslLevel = eslLevelDown
                        foldLevelNr = eslLevel
                        if inEncryptBlock: foldLevelNr += Stc.EncryptFoldOffset
                        nextFoldLevelNr = foldLevelNr - 1
                        #print("--- Down:"+str(eslLevel)+" line="+str(tokenLine+1)+
                        #      " foldLevelNr=" + str(foldLevelNr) +
                        #      " nextFoldLevelNr="+str(nextFoldLevelNr))
                        eslLevel -= 1

        pass # for tokens

    def OnMarginClick(self, evt):
        # fold and unfold as needed
        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.exFoldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())
                #print("OnMarginClick line="+str(lineClicked+1)+" raw="+str(self.GetFoldLevel(lineClicked))+
                #      " level="+str((self.GetFoldLevel(lineClicked) & stc.STC_FOLDLEVELNUMBERMASK) - stc.STC_FOLDLEVELBASE))
                if self.GetFoldLevel(lineClicked) & stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, True)
                        self.Expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, False)
                            self.Expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, True)
                            self.Expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)

    def exFoldAll(self): # taken from example but changed from FoldAll
        lineCount = self.GetLineCount()
        expanding = True
        # find out if we are folding or unfolding
        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) & stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lineNum)
                break
        lineNum = 0
        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & stc.STC_FOLDLEVELHEADERFLAG and \
               (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:
                if expanding:
                    self.SetFoldExpanded(lineNum, True)
                    lineNum = self.Expand(lineNum, True)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldExpanded(lineNum, False)
                    if lastChild > lineNum:
                        self.HideLines(lineNum+1, lastChild)
            lineNum = lineNum + 1

    def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
        lastChild = self.GetLastChild(line, level)
        line = line + 1
        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)
            if level == -1:
                level = self.GetFoldLevel(line)
            if level & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)
                    line = self.Expand(line, doExpand, force, visLevels-1)
                else:
                    if doExpand and self.GetFoldExpanded(line):
                        line = self.Expand(line, True, force, visLevels-1)
                    else:
                        line = self.Expand(line, False, force, visLevels-1)
            else:
                line = line + 1
        return line

    def OnKeyDown(self, evt):
        keyCode = evt.GetKeyCode()
        uniKey = evt.GetUnicodeKey()
        char = ""
        if uniKey != 0:
            char = chr(uniKey)
        modifiers = evt.GetModifiers()
        # Built-in behaviours for Ctrl-X/C/V, Ctrl-Z/Y DEL & BS
        if keyCode == wx.WXK_F5:
            #self.Refresh()
            if self._style == Stc.Style.ESL and not self.readOnly:
                text = self.GetText()
                self.doStyling(0, 0, text)
        elif char == "G" and modifiers & wx.MOD_CONTROL:
            self.doGoto()
        elif char == "F" and modifiers & wx.MOD_CONTROL:
            self.doFind()
        elif keyCode == wx.WXK_F3 and not modifiers:
            self.doFindNext()
        elif keyCode == wx.WXK_F3 and modifiers & wx.MOD_SHIFT:
            self.doFindPrev()
        else:
            evt.Skip(True)

    def OnSetFocus(self, focusEvent):
        mainView = self._parent
        if mainView:
            if isinstance(self, View):
                self.checkSelectedInMainView()
        focusEvent.Skip()

    def showContextMenu(self, event):
        editable = not self.readOnly
        menu = wx.Menu()
        if self._allowToggleEdit:
            menu.Append(self._id_edit, "Edit", "", wx.ITEM_CHECK)
            menu.Check(self._id_edit, editable)
            menu.AppendSeparator()
        if editable and self._allowSave:
            if self._filepath:
                menu.Append(self._id_save, "Save")
                menu.Enable(self._id_save, self.IsModified())
            menu.Append(self._id_saveas, "Save As")
            menu.AppendSeparator()
        if editable and self._allowCommitESL:
            menu.Append(self._id_commitesl, "Commit ESL")
            menu.Enable(self._id_commitesl, self.IsModified())
            menu.AppendSeparator()
        if self._allowRunESLDirect:
            menu.Append(self._id_run_esl_direct, "Run ESL Direct")
            menu.AppendSeparator()
        if hasattr(self, "getModule"): # in EslView
            module = self.getModule()
            if module and module.moduleType() == "code":
                menu.Append(self._id_code_checks, "Show code checks")
                menu.Append(self._id_run_compiler, "Run ESL Compiler")
                menu.AppendSeparator()
        if editable:
            menu.Append(self._id_undo, "Undo Edit\tCtrl+Z")
            menu.Enable(self._id_undo, self.CanUndo())
            menu.Append(self._id_redo, "Redo Edit\tCtrl+Y")
            menu.Enable(self._id_redo, self.CanRedo())
            menu.AppendSeparator()
        if editable:
            menu.Append(self._id_cut, "Cut\tCtrl+X")
            menu.Enable(self._id_cut, self.CanCopy())
        menu.Append(self._id_copy, "Copy\tCtrl+C")
        menu.Enable(self._id_copy, self.CanCopy())
        if editable:
            menu.Append(self._id_paste, "Paste\tCtrl+V")
            menu.Enable(self._id_paste, self.CanPaste())
            menu.Append(self._id_delete, "Delete")
        menu.AppendSeparator()
        menu.Append(self._id_wrap, "Wrap", "", wx.ITEM_CHECK)
        menu.Check(self._id_wrap, self.GetWrapMode() != stc.STC_WRAP_NONE)
        menu.Append(self._id_folding, "Folding", "", wx.ITEM_CHECK)
        menu.Check(self._id_folding, self.GetMarginWidth(2) == 12)
        menu.Append(self._id_linenrs, "Line Numbers", "", wx.ITEM_CHECK)
        menu.Check(self._id_linenrs, self.GetMarginWidth(1) == 40)
        menu.Append(self._id_whitespace, "White Space", "", wx.ITEM_CHECK)
        menu.Check(self._id_whitespace, self.GetViewWhiteSpace() == stc.STC_WS_VISIBLEALWAYS)
        menu.AppendSeparator()
        menu.Append(self._id_selectall, "Select All\tCtrl+A")
        menu.AppendSeparator()
        menu.Append(self._id_goto, "Goto Line Number...\tCtrl+G")
        menu.Append(self._id_find, "Find Text...\tCtrl+F")
        menu.Append(self._id_find_next, "Find Next...\tF3")
        menu.Append(self._id_find_prev, "Find Previous...\tShift+F3")
        self.PopupMenu(menu)

    def onContextMenuItem(self, event):
        id = event.GetId()
        #print("event id", id)
        if id == self._id_edit:
            self.setReadOnly(not self.readOnly)
        elif id == self._id_save:
            if self._filepath:
                self.SaveFile(self._filepath)
                self.EmptyUndoBuffer()
        elif id == self._id_saveas:
            self.doSaveAs()
        elif id == self._id_commitesl:
            self.doCommitESL()
        elif id == self._id_run_esl_direct:
            self.runESLDirect()
        elif id == self._id_code_checks:
            self.doShowCodeChecks() # in EslView
        elif id == self._id_run_compiler:
            self.runESLCompiler()  # in EslView
        elif id == self._id_undo:
            self.Undo()
        elif id == self._id_redo:
            self.Redo()
        elif id == self._id_cut:
            self.Cut()
        elif id == self._id_copy:
            self.Copy()
        elif id == self._id_paste:
            self.Paste()
        elif id == self._id_delete:
            self.Clear()
        elif id == self._id_wrap:
            if self.GetWrapMode() == stc.STC_WRAP_NONE:
                self.SetWrapMode(stc.STC_WRAP_WORD)
            else:
                self.SetWrapMode(stc.STC_WRAP_NONE)
        elif id == self._id_folding:
            if self.GetMarginWidth(2) == 12:
                self.SetMarginWidth(2, 0)
                self.FoldAll(stc.STC_FOLDACTION_EXPAND)
            else:
                self.SetMarginWidth(2, 12)
        elif id == self._id_linenrs:
            if self.GetMarginWidth(1) == 40:
                self.SetMarginWidth(1, 0)
            else:
                self.SetMarginWidth(1, 40)
        elif id == self._id_whitespace:
            if self.GetViewWhiteSpace() == stc.STC_WS_VISIBLEALWAYS:
                self.SetViewWhiteSpace(stc.STC_WS_INVISIBLE)
            else:
                self.SetViewWhiteSpace(stc.STC_WS_VISIBLEALWAYS)
        elif id == self._id_selectall:
            self.SelectAll()
        elif id == self._id_goto:
            self.doGoto()
        elif id == self._id_find:
            self.doFind()
        elif id == self._id_find_next:
            self.doFindNext()
        elif id == self._id_find_prev:
            self.doFindPrev()

    def doSaveAs(self):
        extn = ".txt"
        if self._filepath:
            root, extn = os.path.splitext(self._filepath)
        wildcard = ""
        fileType = ""
        if extn:
            fileType = extn[1:].upper()
            wildcard = fileType+" files (*"+extn+")|*"+extn+"|"
        wildcard += "All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Save file",
                            os.getcwd(), "", wildcard,
                            style=wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT)
        result = self.showModalDlg(dlg)
        if result == wx.ID_OK:
            filepath = dlg.GetPath()
            if filepath:
                self.SaveFile(filepath)
                self.LoadFile(filepath)
                self.setAllowToggleEdit(True)
                self.setAllowSave(True)
                self.setReadOnly(False)
                self.setAllowRunESLDirect(self._style == Stc.Style.ESL)
                if self._control:
                    mainview = self._frame.viewManager().mainView()
                    pageindex = mainview.GetPageIndex(self)
                    if pageindex != wx.NOT_FOUND:
                        tabname = os.path.basename(filepath)
                        mainview.SetPageText(pageindex, tabname)

    def doCommitESL(self):
        if hasattr(self, "updateEsl"): # in EslView
            self.updateEsl()

    def runESLDirect(self):
        msg = ""
        if self._control and not self.inModalDlg:
            eslText = self.GetText()
            if eslText:
                if not self._parseEsl:
                    self._parseEsl = ParseEsl()
                hasReadIn = self._parseEsl.hasReadStatement(eslText)
                if hasReadIn:
                    msg = "ESL text contains direct input - cannot run directly from ESL-Studio.\n"
                    msg += "Run saved file from command line or specify to run with ESL-SEC (Simulation/Setup).\n"
                else:
                    filebase = "run_esl_direct_" + str(os.getpid())
                    eslfile = filebase + ".esl"
                    f = None
                    try:
                        f = open(eslfile, "w")
                    except Exception:
                        msg = "Cannot write ESL file \"" + eslfile + "\" on directory \"" + os.getcwd() + "\"\n"
                    if f and not f.closed:
                        f.write(eslText)
                        f.close()
                        cmd = "esl"
                        if sys.platform == "win32":
                            cmd += ".bat"
                        cmd += " " + filebase + " -noprompt"
                        input = "Quit\n" # input is there to exit from Interact if esl_run has a runtime error - the newline is needed in Windows
                        retcode, lines = self._frame.commands().execute(cmd, getoutput=True, synchronise=False,
                                                                        callback=self.runESLDirectCallback, input=input)
        if msg:
            self._control.appendMessage(msg)
        pass

    def runESLDirectCallback(self, process):
        if process:
            msg = self._frame.commands().getCommandOutput()
            self._control.appendMessage(msg)
        filebase = "run_esl_direct_" + str(os.getpid())
        if os.path.exists(filebase + ".esl"):
            os.remove(filebase + ".esl")
        if os.path.exists(filebase + ".hcd"):
            os.remove(filebase + ".hcd")

    def showModalDlg(self, dlg):
        self.inModalDlg = True
        ans = dlg.ShowModal()
        self.inModalDlg = False
        return ans

    def gotoLineCol(self, lineColStr):
        line = -1
        char = -1
        try:
            # line = int(text)
            match = re.match(r"\s*(\d+)(\:\d*)?", lineColStr)
            if match:
                line = int(match[1])
                if match[2]:
                    char = int(match[2][1:])
                else:
                    char = 1
        except:
            pass
        if line < 0 or line > self.GetNumberOfLines() or char - 1 > self.GetLineLength(line - 1):
            Utils.bleep()
        else:
            # self.GotoLine(line - 1)
            pos = self.XYToPosition(char - 1, line - 1)
            if pos >= 0:
                self.GotoPos(pos)

    def doGoto(self):
        #text = wx.GetTextFromUser("Give line number to goto", "Goto Line Number", "", self)
        text = ""
        pos = self.GetCurrentPos()
        if pos >= 0:
            ok, char, line = self.PositionToXY(pos) # zero based
            if ok:
                text = str(line+1)+":"+str(char+1)
        dlg = wx.TextEntryDialog(self, "Give line number [:character number] to goto",
                                 "Goto Line Number", text)
        ans = self.showModalDlg(dlg)
        text = dlg.GetValue()
        if ans == wx.ID_OK and text: # else was cancelled (or blank)
            self.gotoLineCol(text)

    def askFindText(self):
        defaultText = self.GetSelectedText()
        #text = wx.GetTextFromUser("Give text to search for", "Find Text", defaultText, self)
        dlg = wx.TextEntryDialog(self, "Give text to search for", "Find Text", defaultText)
        ans = self.showModalDlg(dlg)
        text = dlg.GetValue()
        if ans == wx.ID_OK and text: # else was cancelled (or blank)
            self._find_text = text

    def doFind(self):
        self.askFindText()
        if self._find_text:
            self.doFindNext()

    def doFindNext(self):
        if not self._find_text:
            self.askFindText()
        if self._find_text:
            if self._find_in_whole_file:
                pos = 0
            else:
                pos = self.GetCurrentPos()
            if pos < 0: pos = 0
            maxPos = self.GetTextLength()
            minPos = pos
            flags = 0 # stc.STC_FIND_POSIX ^ stc.STC_FIND_REGEXP ^ stc.STC_FIND_MATCHCASE ^ stc.STC_FIND_WHOLEWORD ^ stc.STC_FIND_WORDSTART
            pos, end = self.FindText(minPos, maxPos, self._find_text, flags)
            if pos == stc.STC_INVALID_POSITION:
                Utils.bleep()
                self._find_in_whole_file = True
            else:
                self.SetSelectionStart(pos)
                self.SetSelectionEnd(end)
                self.EnsureCaretVisible()
                self._find_pos = pos
                self._find_end = end
                self._find_in_whole_file = False

    def doFindPrev(self):
        if not self._find_text:
            self.askFindText()
        if self._find_text:
            if self._find_in_whole_file:
                pos = self.GetTextLength()
            else:
                pos = self.GetCurrentPos()
            if pos < 0: pos = 0
            if pos <= self._find_end and pos > self._find_pos:
                pos = self._find_pos
            maxPos = 0
            minPos = pos
            flags = 0 # stc.STC_FIND_POSIX ^ stc.STC_FIND_REGEXP ^ stc.STC_FIND_MATCHCASE ^ stc.STC_FIND_WHOLEWORD ^ stc.STC_FIND_WORDSTART
            pos, end = self.FindText(minPos, maxPos, self._find_text, flags)
            if pos == stc.STC_INVALID_POSITION:
                Utils.bleep()
                self._find_in_whole_file = True
            else:
                self.SetSelectionStart(pos)
                self.SetSelectionEnd(end)
                self.EnsureCaretVisible()
                self._find_pos = pos
                self._find_end = end
                self._find_in_whole_file = False
