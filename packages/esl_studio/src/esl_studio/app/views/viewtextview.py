#! /usr/bin/python

import wx

from .view import View
from .stc import Stc

class ViewTextView(View, Stc):
    def __init__(self, parent):
        Stc.__init__(self, parent)
        View.__init__(self, parent, 'page')
