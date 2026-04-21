#! /usr/bin/python

import os
import sys

import wx
from enum import IntEnum

import esl_diagram.canvas as canv

from .views.stc import Stc
from .dlg.printsavediagramdlg import PrintSaveDiagramDlg

MM_PER_IN = 25.4

class DiagramArea(object):
    class Option(IntEnum):
        DIAGRAM_VIEW = 1
        ALL_OBJECTS = 2
        SELECTED_OBJECTS = 3
        COORDINATES = 4
        FULL_DIAGRAM_1 = 5
        FULL_DIAGRAM_4 = 6
        FULL_DIAGRAM_16 = 7

    def __init__(self):
        self.option = DiagramArea.Option.DIAGRAM_VIEW       # Diagram view, All objects, Encompass selected objects, Full diagram (1 page), Full diagram (4 pages), Full diagram (16 pages), Specified coordinates
        self.drawRect = None

class PrintoutCanvas(wx.Printout):
    def __init__(self, printing, canvas, title):
        wx.Printout.__init__(self)
        self._printing = printing
        self._canvas = canvas
        self._title = title

    def nrPages(self):
        nrPages = 1
        if self._printing.diagramArea.option == DiagramArea.Option.FULL_DIAGRAM_4:
            nrPages = 4
        elif self._printing.diagramArea.option == DiagramArea.Option.FULL_DIAGRAM_16:
            nrPages = 16
        return nrPages

    def HasPage(self, page): # pages start at 1
        nrPages = self.nrPages()
        return page <= nrPages

    def GetPageInfo(self):
        nrPages = self.nrPages()
        return (1, nrPages, 1, nrPages)

    def OnPrintPage(self, page):
        if not self.HasPage(page): # this probably already checked by framework
            raise Exception("Attempt to print invalid page "+str(page))

        dc = self.GetDC()
        doMemoryBlit = False
        if isinstance(dc, wx.PrinterDC) and sys.platform == "win32":
            doMemoryBlit = True

        if page > 1:
            drawRect = self._printing.getPrintingPageArea(page)
        else:
            drawRect = self._printing.diagramArea.drawRect
        if drawRect is None:
            drawRect = self._canvas.GetVisibleDiagramArea()  # Current view

        maxX = drawRect.GetWidth()
        maxY = drawRect.GetHeight()

        # Get the size of the DC in pixels
        (w, h) = dc.GetSize()

        # Calculate a suitable scaling factor - margins are mms
        ppiPrt = self.GetPPIPrinter() # pixels per inch
        margins = (self._printing.marginTopLeft.x + self._printing.marginBottomRight.x) * (ppiPrt[0] / MM_PER_IN)
        scaleX = float(w - margins) / maxX
        margins = (self._printing.marginTopLeft.y + self._printing.marginBottomRight.y) * (ppiPrt[1] / MM_PER_IN)
        scaleY = float(h - margins) / maxY

        # Use x or y scaling factor, whichever fits on the DC
        actualScale = min(scaleX, scaleY)

        # Calculate the position on the DC for centering the graphic
        posX = (w - (drawRect.GetWidth() * actualScale)) / 2.0
        posY = (h - (drawRect.GetHeight() * actualScale)) / 2.0
        posX -= drawRect.GetLeft() * actualScale
        posY -= drawRect.GetTop() * actualScale
        posX += (self._printing.marginTopLeft.x/2 - self._printing.marginBottomRight.x/2) * (ppiPrt[0] / MM_PER_IN) # * actualScale
        posY += (self._printing.marginTopLeft.y/2 - self._printing.marginBottomRight.y/2) * (ppiPrt[1] / MM_PER_IN) # * actualScale

        # Set the scale and origin
        printDC = None
        memoryDC = None
        if doMemoryBlit:
            memoryDC = wx.MemoryDC()
            printDC = dc
            bitmap = wx.Bitmap(w, h)
            dc = memoryDC           # draw to memory DC
            dc.SelectObject(bitmap)

        dc.SetUserScale(actualScale, actualScale)
        dc.SetDeviceOrigin(int(posX), int(posY))

        if doMemoryBlit and memoryDC:
            memoryDC.SetBackground(wx.WHITE_BRUSH)
            memoryDC.Clear()
        dc.DestroyClippingRegion()
        dc.SetClippingRegion(drawRect)
        self._canvas.DoDrawing(dc, drawRect)

        if doMemoryBlit and printDC:
            # Copy (blit) from memory DC to printer DC
            if sys.platform == "win32":
                # This works in Window but not Linux
                printDC.Blit(
                        0,  # xdest (int) – Destination device context x position.
                        0,  # ydest (int) – Destination device context y position
                        w,  # width (int) – Width of source area to be copied
                        h,  # height (int) – Height of source area to be copied.
                        memoryDC,  # source (wx.DC) – Source device context.
                        0, #drawRect.x,  # xsrc (int) – Source device context x position.
                        0, #drawRect.y,  # ysrc (int) – Source device context y position.
                        wx.COPY, # logicalFunc (RasterOperationMode) – Logical function to use, see SetLogicalFunction .
                        False # useMask (bool) – If True, Blit does a transparent blit using the mask that is associated with the bitmap selected into the source device context.
                        )
            else:
                # This (experimental path) still not working properly in Linux - but doesn't get used.
                printDC.Blit(
                        0,  # xdest (int) – Destination device context x position.
                        0,  # ydest (int) – Destination device context y position
                        drawRect.width,  # width (int) – Width of source area to be copied
                        drawRect.height,  # height (int) – Height of source area to be copied.
                        memoryDC,  # source (wx.DC) – Source device context.
                        drawRect.x, # xsrc (int) – Source device context x position.
                        drawRect.y, # ysrc (int) – Source device context y position.
                        wx.COPY, # logicalFunc (RasterOperationMode) – Logical function to use, see SetLogicalFunction .
                        False # useMask (bool) – If True, Blit does a transparent blit using the mask that is associated with the bitmap selected into the source device context.
                        )
            memoryDC.SelectObject(wx.NullBitmap)

        return True

class PrintoutStc(wx.Printout):
    def __init__(self, printing, stc, title):
        wx.Printout.__init__(self)
        self._printing = printing
        self._stc = stc
        self._title = title
        self._pageRect = None
        self._printRect = None
        self._pageEnds = []

    def HasPage(self, page): # pages start at 1
        return page <= len(self._pageEnds)

    def GetPageInfo (self):
        # initialize values
        minPage = 0
        maxPage = 0
        selPageFrom = 0
        selPageTo = 0
        # scale DC if possible
        dc = self.GetDC()
        if not dc:
            #print("PrintoutStc.GetPageInfo no DC")
            return minPage, maxPage, selPageFrom, selPageTo
        self.printScaling(dc)
        # get print page informations and convert to printer pixels
        ppiScr = self.GetPPIScreen()
        w,h = self.GetPageSizeMM()
        w = int(w * ppiScr[0] / MM_PER_IN)
        h = int(h * ppiScr[1] / MM_PER_IN)

        self._pageRect = wx.Rect(0, 0, w, h)
        # get margins informations and convert to printer pixels
        pt = self._printing.marginTopLeft
        left = pt.x
        top = pt.y
        pt = self._printing.marginBottomRight
        right = pt.x
        bottom = pt.y
        top = int(top * ppiScr[1] / MM_PER_IN)
        bottom = int(bottom * ppiScr[1] / MM_PER_IN)
        left = int(left * ppiScr[0] / MM_PER_IN)
        right = int(right * ppiScr[0] / MM_PER_IN)
        self._printRect = wx.Rect (left, top, w - (left + right), h - (top + bottom))
        # count pages
        self._pageEnds = []
        len = self._stc.GetLength()
        printed = 0
        while printed < len:
            printed = self._stc.FormatRange(False, printed, len,
                                          dc, dc, self._printRect, self._pageRect)
            self._pageEnds.append(printed)
            maxPage += 1
        if maxPage > 0: minPage = 1
        selPageFrom = minPage
        selPageTo = maxPage
        #print("PrintoutStc.GetPageInfo minPage=%d maxPage=%d selPageFrom=%d selPageTo=%d" % (minPage, maxPage, selPageFrom, selPageTo))
        return minPage, maxPage, selPageFrom, selPageTo

    def OnPrintPage(self, page):
        dc = self.GetDC()
        self.printScaling(dc)
        start = 0
        if page != 1:
            start = self._pageEnds[page - 2]
        end = self._pageEnds[page - 1]
        self._stc.FormatRange(
            True, #doDraw (bool) –
            start, #startPos (int) –
            end, #endPos (int) –
            dc, #draw (wx.DC) –
            dc, #target (wx.DC) –
            self._printRect, #renderRect (wx.Rect) –
            self._pageRect, #pageRect (wx.Rect) –
        )
        return True

    def printScaling(self, dc):
        # get printer and screen sizing values
        ppiScr = self.GetPPIScreen()
        if not ppiScr: # most possible guess 96 dpi
            ppiScr = (96, 96)
        ppiPrt = self.GetPPIPrinter()
        if not ppiPrt: # scaling factor to 1
            ppiPrt = ppiScr
        dcSize = dc.GetSize()
        pageSize = self.GetPageSizePixels()

        # set user scale
        scale_x = (ppiPrt[0] * dcSize.x) / (ppiScr[0] * pageSize[0])
        scale_y = (ppiPrt[1] * dcSize.y) / (ppiScr[1] * pageSize[1])
        dc.SetUserScale(scale_x, scale_y)

class Printing(object):
    def __init__(self, frame):
        self._frame = frame
        self.diagramArea = DiagramArea()
        self.printData = wx.PrintData()
        self.marginTopLeft = wx.Point(0,0)
        self.marginBottomRight = wx.Point(0,0)

    def setup(self):
        pass

    def resetDiagramArea(self):
        self.diagramArea.option = DiagramArea.Option.DIAGRAM_VIEW
        self.diagramArea.drawRect = None

    def setDiagramArea(self, option, drawRect):
        self.diagramArea.option = option
        self.diagramArea.drawRect = drawRect

    def getDiagramArea(self):
        return self.diagramArea.option, self.diagramArea.drawRect

    def getPrintingPageArea(self, page): # pages start at 1
        n = 0
        if self.diagramArea.option == DiagramArea.Option.FULL_DIAGRAM_4:
            n = 2
        elif self.diagramArea.option == DiagramArea.Option.FULL_DIAGRAM_16:
            n = 4
        w = self.diagramArea.drawRect.width
        h = self.diagramArea.drawRect.height
        col = (page - 1) % n
        row = (page - 1) // n
        drawRect = wx.Rect(col*w, row*h, w, h)
        return drawRect

    def PrintSaveDiagram(self):
        result = wx.ID_CANCEL
        canvas = self._frame.control().currentCanvas()
        if canvas: # currently only support diagrams
            dlg = PrintSaveDiagramDlg.Instance(self._frame, canvas)
            result = dlg.ShowModal()
        return result

    def PageSetup(self):
        psdd = wx.PageSetupDialogData(self.printData)
        psdd.SetMarginTopLeft(self.marginTopLeft)
        psdd.SetMarginBottomRight(self.marginBottomRight)
        dlg = wx.PageSetupDialog(self._frame, psdd)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            # this makes a copy of the wx.PrintData instead of just saving
            # a reference to the one inside the PrintDialogData that will
            # be destroyed when the dialog is destroyed
            psdd = dlg.GetPageSetupData()
            pd = psdd.GetPrintData()
            self.printData = wx.PrintData(pd)
            self.marginTopLeft = psdd.GetMarginTopLeft()
            self.marginBottomRight = psdd.GetMarginBottomRight()
        dlg.Destroy()
        return result

    def PrintPreview(self, canvas=None, useDiagramArea=False):
        result = wx.ID_CANCEL
        data = wx.PrintDialogData(self.printData)
        textView = None
        printout = None
        printout2 = None
        title = ""
        caption = ""
        if not canvas:
            canvas = self._frame.control().currentCanvas()
        if not canvas:
            page = self._frame.control().currentPage()
            if isinstance(page, Stc):
                textView = page
        if canvas:
            if not useDiagramArea:
                self.resetDiagramArea()
            title = self.pageCanvasTitle(canvas)
            caption = "ESL Studio Diagram Print Preview"
        elif textView:
            title = self.pageTextTitle(textView)
            caption = "ESL Studio Text Print Preview"

        if canvas:
            printout = PrintoutCanvas(self, canvas, title)
            printout2 = PrintoutCanvas(self, canvas, title)
        elif textView:
            printout = PrintoutStc(self, textView, title)
            printout2 = PrintoutStc(self, textView, title)

        if printout:
            printPreview = wx.PrintPreview(printout, printout2, data)
            if printPreview.IsOk():
                pfrm = wx.PreviewFrame(printPreview, self._frame, caption)
                pfrm.Initialize()
                pfrm.SetPosition(self._frame.GetPosition())
                pfrm.SetSize(self._frame.GetSize())
                pfrm.Show(True)
                result = wx.ID_OK
        return result

    def PrintView(self):
        result = wx.ID_CANCEL
        page = self._frame.control().currentPage()
        if isinstance(page, canv.Canvas):
            result = self.PrintDiagram()
        elif isinstance(page, Stc):
            result = self.PrintText()
        return result

    def PrintDiagram(self, canvas=None, useDiagramArea=False):
        result = wx.ID_CANCEL
        if not canvas:
            canvas = self._frame.control().currentCanvas()
        if canvas:
            if not useDiagramArea:
                self.resetDiagramArea()
            title = self.pageCanvasTitle(canvas)
            pdd = wx.PrintDialogData(self.printData)
            pdd.SetToPage(1)
            printer = wx.Printer(pdd)
            printout = PrintoutCanvas(self, canvas, title)
            if not printer.Print(self._frame, printout, True):
                if printer.GetLastError() == wx.PRINTER_ERROR:
                    wx.MessageBox("There was a problem printing diagram.\nPerhaps your current printer is not set correctly?", "Printing", wx.OK)
            else:
                self.printData = wx.PrintData(printer.GetPrintDialogData().GetPrintData())
                result = wx.ID_OK
            printout.Destroy()
        return result

    def SaveDiagram(self, canvas=None, useDiagramArea=False):
        result = wx.ID_CANCEL
        if not canvas:
            canvas = self._frame.control().currentCanvas()
        if canvas:
            if not useDiagramArea:
                self.resetDiagramArea()
            option, drawRect = self.getDiagramArea()
            if drawRect is None:
                drawRect = canvas.GetVisibleDiagramArea()  # Current view
            drawScale = 1
            if option == DiagramArea.Option.DIAGRAM_VIEW:
                drawScale = canvas.GetScale()               # for current view use scale view in diagram

            dc = wx.MemoryDC()
            crop = False                # if set draw from origin and later crop off the margin - necessary in Windows as dc.SetDeviceOrigin causes drawing failures
            dontScale = False           # for diagram view (if zoomed big) don't scale the drawing to same scale as in view - necessary in Windows as dc.SetUserScale causes drawing failures
            rescaleImage = False        # for use (in Windows) when dontScale and zoomed big to try to rescale up the unscaled image after generation - but is fuzzy
            clearAlpha = False          # clear the image alpha channel (if has) - for use (in Windows) prior to saving image
            if sys.platform == "win32":
                ##crop = True
                ##dontScale = True
                ##rescaleImage = False    # not in use because looks too fuzzy
                clearAlpha = True
            x = drawRect.x; y = drawRect.y; w = drawRect.width; h = drawRect.height
            if drawScale > 1 and not dontScale:
                x = int(x*drawScale); y = int(y*drawScale); w = int(w*drawScale); h = int(h*drawScale)
                dc.SetUserScale(drawScale, drawScale) # this fine in Linux but fails to draw properly in Windows
            if x != 0 or y != 0:
                if not crop:
                    dc.SetDeviceOrigin(-x, -y) # this fine in Linux but fails to draw properly in Windows
                else:
                    w += x; h += y # alt extend with a black area and later will have to crop
            bitmap = wx.Bitmap(w, h)
            dc.SelectObject(bitmap)
            ok = dc.IsOk()

            dc.DestroyClippingRegion()
            dc.SetClippingRegion(drawRect)
            canvas.DoDrawing(dc, drawRect)

            if crop and (x != 0 or y != 0):
                bitmap = dc.GetAsBitmap(wx.Rect(x, y, w - x, h - y))
                ok = bitmap.IsOk()

            dc.SelectObject(wx.NullBitmap)
            image = bitmap.ConvertToImage()
            if rescaleImage and drawScale > 1:
                image.Rescale(int(w*drawScale), int(h*drawScale), wx.IMAGE_QUALITY_HIGH)
            if image and image.IsOk():
                wildcard = "Portable Network Graphics files (*.png)|*.png|Bitmap files (*.bmp)|*.bmp|JPEG files (*.jpg)|*.jpg|All files (*.*)|*.*"
                dlg = wx.FileDialog(self._frame, "Save diagram as image file",
                                    os.getcwd(), "", wildcard,
                                    style=wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT)
                result = dlg.ShowModal()
                if result == wx.ID_OK:
                    if clearAlpha and image.HasAlpha(): #?do only for png?
                        image.ClearAlpha()
                    image.SaveFile(dlg.GetPath())
        return result

    def PrintText(self, view=None):
        result = wx.ID_CANCEL
        textView = None
        page = self._frame.control().currentPage()
        if isinstance(page, Stc):
            textView = page
            title = self.pageTextTitle(textView)
            pdd = wx.PrintDialogData(self.printData)
            pdd.SetToPage(1)
            printer = wx.Printer(pdd)
            printout = PrintoutStc(self, textView, title)
            if not printer.Print(self._frame, printout, True):
                if printer.GetLastError() == wx.PRINTER_ERROR:
                    wx.MessageBox("There was a problem printing text.\nPerhaps your current printer is not set correctly?",
                                  "Printing", wx.OK)
            else:
                self.printData = wx.PrintData(printer.GetPrintDialogData().GetPrintData())
                result = wx.ID_OK
            printout.Destroy()
        return result

    def pageCanvasTitle(self, canvas):
        title = ''
        application = self._frame.application()
        filepath = application.filepath()
        if filepath:
            title += 'Application '+str(filepath)+' '
        info = self._frame.application().getCanvasInfo(canvas) #[canvasId, moduleType, name]
        if info:
            if info[1] == 'model':
                if application.program().model() and application.program().moduleId() == canvas.moduleId():
                    title += 'Program/Model '+str(info[2])+' '
                else:
                    title += 'Model '+str(info[2])+' '
            elif info[1] == 'submodel':
                title += 'Submodel '+str(info[2])+' '
            elif info[1] == 'segment':
                title += 'Segment '+str(info[2])+' '
        else:
            if canvas.moduleId() == application.program().moduleId(): # Program
                title += 'Program'
                if application.program().name():
                    title += " " + application.program().name()
        return title

    def pageTextTitle(self, textView):
        title = ""
        filepath = textView.filepath()
        if filepath:
            title = "File "+str(filepath)
        return title
