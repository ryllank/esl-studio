#! /usr/bin/python

# printsavediagramdlg.py

import wx
from wx import xrc

from .. import utils as Utils

class PrintSaveDiagramDlg(wx.Dialog):

    _instance = None

    choiceTexts = [
        "Diagram view",
        "All objects",
        "Encompass selected objects",
        "Use coordinates",
        "Full diagram (1 page)",
        "Full diagram (4 pages)",
        "Full diagram (16 pages)"
    ]
    # Convenience lookup maps
    choiceTextsToDiagramAreaOption = {}
    diagramAreaOptionToChoiceTexts = {}
    multiPageOptions = []

    @classmethod
    def Instance(cls, parent, canvas):
        if cls._instance is None:
            cls._instance = cls(parent)
        cls._instance.setupForCanvas(canvas)
        return cls._instance

    def __init__(self, parent):
        wx.Dialog.__init__(self)
        self._parent = parent # frame
        self._printing = self._parent.printing()
        self._commands = self._parent.commands()
        self._canvas = None
        resfile = Utils.resourceFile("printsavediagramdlg.xrc")
        if resfile:
            res = xrc.XmlResource(resfile)
            if res:
                res.LoadDialog(self, parent, "PrintSaveDiagramDlg")
                self.setup()

    def setup(self):
        #self._sttArea = xrc.XRCCTRL(self, "sttArea")
        self._chcArea = xrc.XRCCTRL(self, "chcArea")
        self._chkCoordinates = xrc.XRCCTRL(self, "chkCoordinates")
        #self._sttLeftTop = xrc.XRCCTRL(self, "sttLeftTop")
        self._spnLeft = xrc.XRCCTRL(self, "spnLeft")
        self._spnTop = xrc.XRCCTRL(self, "spnTop")
        #self._sttWidthHeight = xrc.XRCCTRL(self, "sttWidthHeight")
        self._spnWidth = xrc.XRCCTRL(self, "spnWidth")
        self._spnHeight = xrc.XRCCTRL(self, "spnHeight")
        self._btnPageSetup = xrc.XRCCTRL(self, "btnPageSetup")
        self._btnPrintPreview = xrc.XRCCTRL(self, "btnPrintPreview")
        self._btnPrintDiagram = xrc.XRCCTRL(self, "btnPrintDiagram")
        self._btnSaveAsImage = xrc.XRCCTRL(self, "btnSaveAsImage")

        self.Bind(wx.EVT_CHOICE, self.onAreaChanged, self._chcArea)
        self.Bind(wx.EVT_CHECKBOX, self.onCoordinatesChanged, self._chkCoordinates)
        #
        self.Bind(wx.EVT_BUTTON, self.onPageSetupClicked, self._btnPageSetup)
        self.Bind(wx.EVT_BUTTON, self.onPrintPreviewClicked, self._btnPrintPreview)
        self.Bind(wx.EVT_BUTTON, self.onPrintDiagramClicked, self._btnPrintDiagram)
        self.Bind(wx.EVT_BUTTON, self.onSaveAsImageClicked, self._btnSaveAsImage)

        for i in range(len(PrintSaveDiagramDlg.choiceTexts)):
            PrintSaveDiagramDlg.choiceTextsToDiagramAreaOption[PrintSaveDiagramDlg.choiceTexts[i]] = i + 1
            PrintSaveDiagramDlg.diagramAreaOptionToChoiceTexts[i + 1] = PrintSaveDiagramDlg.choiceTexts[i]
        PrintSaveDiagramDlg.multiPageOptions = [self._printing.diagramArea.Option.FULL_DIAGRAM_4, self._printing.diagramArea.Option.FULL_DIAGRAM_16]

        self._canvasWidth = 0; self._canvasHeight = 0
        self._visibleRect = None
        self._objectsRect = None
        self._selectedRect = None
        self._preCoordsAreaSelection = 0
        self._objectsMargin = 10

    def setupForCanvas(self, canvas):
        self._canvasWidth, self._canvasHeight = canvas.GetDiagramSize()
        self._visibleRect = canvas.GetVisibleDiagramArea()
        self._objectsRect = canvas.GetFullExtent()
        self._selectedRect = canvas.GetSelectedExtent()
        option, drawRect = self._printing.getDiagramArea()

        doResetDiagramArea = False
        if canvas != self._canvas:
            doResetDiagramArea = True
        elif option == self._printing.diagramArea.Option.ALL_OBJECTS and self._objectsRect is None:
            doResetDiagramArea = True
        elif option == self._printing.diagramArea.Option.SELECTED_OBJECTS and self._selectedRect is None:
            doResetDiagramArea = True
        if doResetDiagramArea:
            # reset the area info in printing
            self._printing.resetDiagramArea()
        self._canvas = canvas
        # Setup cmbArea options
        self._chcArea.Clear()
        for i in range(len(PrintSaveDiagramDlg.choiceTexts)):
            doAppend = True
            if i == 1 and self._objectsRect is None: # no objects
                doAppend = False
            elif i == 2 and self._selectedRect is None: # no selected objects
                doAppend = False
            if doAppend:
                self._chcArea.Append(PrintSaveDiagramDlg.choiceTexts[i])
        #
        self.setWidgetsForDiagramArea()

    def setWidgetsForDiagramArea(self):
        option, drawRect = self._printing.getDiagramArea()
        selection = wx.NOT_FOUND
        choiceText = PrintSaveDiagramDlg.diagramAreaOptionToChoiceTexts.get(option)
        if choiceText:
            selection = self._chcArea.FindString(choiceText)
        self._chcArea.SetSelection(selection)
        self._spnLeft.SetRange(0, self._canvasWidth)
        self._spnTop.SetRange(0, self._canvasHeight)
        self._spnWidth.SetRange(1, self._canvasWidth)
        self._spnHeight.SetRange(1, self._canvasHeight)
        self.onAreaChanged(None)

    def setDiagramAreaForWidgets(self):
        selection = self._chcArea.GetSelection()
        choiceText = self._chcArea.GetString(selection)
        option = PrintSaveDiagramDlg.choiceTextsToDiagramAreaOption[choiceText]
        drawRect = self.getDrawRectFromWidgets()
        self._printing.setDiagramArea(option, drawRect)

    def onAreaChanged(self, event):
        selection = self._chcArea.GetSelection()
        choiceText = self._chcArea.GetString(selection)
        diagramAreaOption = PrintSaveDiagramDlg.choiceTextsToDiagramAreaOption[choiceText]
        coordinates = False
        if diagramAreaOption == self._printing.diagramArea.Option.COORDINATES:
            coordinates = True
        self.enableCoordinatesWidgets(coordinates)
        if not coordinates:
            drawRect = self.getDrawRectFromWidgets()
            self.setCoordinatesSpinners(drawRect)
        multipage = diagramAreaOption in PrintSaveDiagramDlg.multiPageOptions
        self._btnSaveAsImage.Enable(not multipage)

    def getDrawRectFromWidgets(self):
        drawRect = None
        selection = self._chcArea.GetSelection()
        choiceText = self._chcArea.GetString(selection)
        if PrintSaveDiagramDlg.choiceTextsToDiagramAreaOption[choiceText] == self._printing.diagramArea.Option.COORDINATES:
            drawRect = wx.Rect(self._spnLeft.GetValue(), self._spnTop.GetValue(), self._spnWidth.GetValue(), self._spnHeight.GetValue())
        else:
            if PrintSaveDiagramDlg.choiceTextsToDiagramAreaOption[choiceText] == self._printing.diagramArea.Option.DIAGRAM_VIEW:
                drawRect = wx.Rect(self._visibleRect)
            elif PrintSaveDiagramDlg.choiceTextsToDiagramAreaOption[choiceText] == self._printing.diagramArea.Option.ALL_OBJECTS:
                drawRect = wx.Rect(self._objectsRect)
                if drawRect:
                    drawRect.Inflate(self._objectsMargin, self._objectsMargin)
            elif PrintSaveDiagramDlg.choiceTextsToDiagramAreaOption[choiceText] == self._printing.diagramArea.Option.SELECTED_OBJECTS:
                drawRect = wx.Rect(self._selectedRect)
                if drawRect:
                    drawRect.Inflate(self._objectsMargin, self._objectsMargin)
            elif PrintSaveDiagramDlg.choiceTextsToDiagramAreaOption[choiceText] == self._printing.diagramArea.Option.FULL_DIAGRAM_1:
                drawRect = wx.Rect(0, 0, self._canvasWidth, self._canvasHeight)
            elif PrintSaveDiagramDlg.choiceTextsToDiagramAreaOption[choiceText] == self._printing.diagramArea.Option.FULL_DIAGRAM_4:
                drawRect = wx.Rect(0, 0, self._canvasWidth//2, self._canvasHeight//2)
            elif PrintSaveDiagramDlg.choiceTextsToDiagramAreaOption[choiceText] == self._printing.diagramArea.Option.FULL_DIAGRAM_16:
                drawRect = wx.Rect(0, 0, self._canvasWidth//4, self._canvasHeight//4)
        return drawRect

    def onCoordinatesChanged(self, event):
        coordinates = self._chkCoordinates.IsChecked()
        if coordinates:
            selection = self._chcArea.GetSelection()
            self._preCoordsAreaSelection = selection
            choiceText = PrintSaveDiagramDlg.diagramAreaOptionToChoiceTexts[self._printing.diagramArea.Option.COORDINATES]
            selection = self._chcArea.FindString(choiceText)
            self._chcArea.SetSelection(selection)
        else:
            self._chcArea.SetSelection(self._preCoordsAreaSelection)
        self.onAreaChanged(None)

    def setCoordinatesSpinners(self, drawRect):
        self._spnLeft.SetValue(drawRect.x)
        self._spnTop.SetValue(drawRect.y)
        self._spnWidth.SetValue(drawRect.width)
        self._spnHeight.SetValue(drawRect.height)

    def enableCoordinatesWidgets(self, coordinates):
        self._chkCoordinates.SetValue(coordinates)
        self._spnLeft.Enable(coordinates)
        self._spnTop.Enable(coordinates)
        self._spnWidth.Enable(coordinates)
        self._spnHeight.Enable(coordinates)

    def onPageSetupClicked(self, event):
        result = self._printing.PageSetup()
        #if result == wx.ID_OK: # don't close this after this
        #    self.EndModal(wx.ID_OK)

    def onPrintPreviewClicked(self, event):
        self.setDiagramAreaForWidgets()
        result = self._printing.PrintPreview(self._canvas, useDiagramArea=True)
        #if result == wx.ID_OK: # don't close this after this
        #    self.EndModal(wx.ID_OK)

    def onPrintDiagramClicked(self, event):
        self.setDiagramAreaForWidgets()
        result = self._printing.PrintDiagram(self._canvas, useDiagramArea=True)
        if result == wx.ID_OK:      # do close this if printed
            self.EndModal(wx.ID_OK)

    def onSaveAsImageClicked(self, event):
        self.setDiagramAreaForWidgets()
        result = self._printing.SaveDiagram(self._canvas, useDiagramArea=True)
        if result == wx.ID_OK:      # do close this if saved
            self.EndModal(wx.ID_OK)
