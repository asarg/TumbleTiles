from __future__ import absolute_import
from __future__ import print_function
import copy
from tkinter import *
import tkinter.font
from scrollableFrame import VerticalScrolledFrame
import tkinter.filedialog
import tkinter.messagebox
import tkinter.colorchooser
import xml.etree.ElementTree as ET
import tumbletiles as TT
import main as TG
from boardgui import redrawCanvas, drawGrid
import random
import time
import os
import sys
import math
from tkinter.colorchooser import askcolor
import numpy as np
from dataclasses import dataclass

# the x and y coordinate that the preview tiles will begin to be drawn on

def debug_print(*print_args):
    if TT.DEBUGGING:
        for arg in print_args:
            print(f"[DEBUG]: {arg}\n") 

TILESIZE = 15

PREVTILESTARTX = 20
PREVTILESTARTY = 21
PREVTILESIZE = 50

NEWTILEWINDOW_W = 250
NEWTILEWINDOW_H = 180

CURRENTNEWTILECOLOR = '#ffff00'

# Used to know where to paste a selection that was made
CURRENTSELECTION = 0

# Defines the current state of selecting an area
SELECTIONSTARTED = False
SELECTIONMADE = False
COPYMADE = False
SHIFTSELECTIONSTARTED = False

@dataclass
class ICoordPair2D:
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0

COPIED_SELECTION = []
COPIED_SELECTION_COORDS = ICoordPair2D(0, 0, 0, 0)

MODS = {
    0x0001: 'Shift',
    0x0002: 'Caps Lock',
    0x0004: 'Control',
    0x0008: 'Left-hand Alt',
    0x0010: 'Num Lock',
    0x0080: 'Right-hand Alt',
    0x0100: 'Mouse button 1',
    0x0200: 'Mouse button 2',
    0x0400: 'Mouse button 3'
}


class TileEditorGUI:
    def __init__(self, parent, tumbleGUI, board, glue_data, previewTileList):

        # open two windows
        # `w1` will be the tile editor
        # `w2` will be a tile config previewer


        self.parent = parent
        self.board = board
        self.board_w = board.Cols
        self.board_h = board.Rows

        # instance of tumbleGUI that created it so methods from that class can be
        # called
        self.tumbleGUI = tumbleGUI

        # self.rows = self.board.Rows
        # self.columns = self.board.Cols

        self.tile_size = TILESIZE
        self.width = self.board_w * self.tile_size
        self.height = self.board_h * self.tile_size

        self.prevTileList = previewTileList

        self.selectedTileIndex = -1

        # States for the tile editor
        self.remove_state = False
        self.add_state = False

        # Variable to hold on to the specifications of the tile to add
        self.tile_to_add = None

        self.glue_label_list = []

        self.glue_data = glue_data

        # A two-dimensional array
        self.coord2tile = [[None for x in range(
            self.board_h)] for y in range(self.board_w)]

        # outline of a preview tile when it is selected
        self.outline = None

        # boolean for whether or not to randomize the color of a placed tile
        self.randomizeColor = False

        # the variable associated with the entry in the create new tile window
        self.newTileN = StringVar()
        self.newTileE = StringVar()
        self.newTileS = StringVar()
        self.newTileW = StringVar()

        self.editTileN = StringVar()
        self.editTileE = StringVar()
        self.editTileS = StringVar()
        self.editTileW = StringVar()

        self.concreteChecked = IntVar()

        # populate the array
        self.populateArray()

        # //////////////////
        #   Window Config
        # /////////////////
        self.newWindow = Toplevel(self.parent)
        self.newWindow.wm_title(f"Editor - {self.parent.title()}")
        self.newWindow.resizable(True, True)
        self.newWindow.protocol("WM_DELETE_WINDOW", lambda: self.closeGUI())

        # TODO: Refactor binds to modular callbacks instead of a central "double-event-handler". This is a weird pattern.
        self.newWindow.bind("<Key>", self.keyPressed)
        self.newWindow.bind("<Up>", self.keyPressed)
        self.newWindow.bind("<Right>", self.keyPressed)
        self.newWindow.bind("<Down>", self.keyPressed)
        self.newWindow.bind("<Left>", self.keyPressed)

        # Add Menu Bar
        self.menuBar = Menu(self.newWindow, relief=RAISED, borderwidth=1)
        self.tkSHOWLOC = BooleanVar()
        self.tkSHOWLOC.set(False)
        optionsMenu = Menu(self.menuBar, tearoff=0)
        optionsMenu.add_command(label="New Board", command=lambda: self.newBoard())
        optionsMenu.add_checkbutton(
        label="Show Location",
        onvalue=True,
        offvalue=False,
        variable=self.tkSHOWLOC,
         command=lambda: self.redrawPrev())
        optionsMenu.add_command(label="Export", command=lambda: self.exportTiles())
        optionsMenu.add_command(
        label="Resize Board",
         command=lambda: self.boardResizeDial())
        optionsMenu.add_command(
        label="Save Configuration",
         command=lambda: self.saveTileConfig())

        # add the options menu to the menu bar
        self.menuBar.add_cascade(label="Option", menu=optionsMenu)
        self.newWindow.config(menu=self.menuBar)

        

        # Create two frames, one to hold the board and the buttons, and one to
        # hold the tiles to be placed
        self.tileEditorFrame = Frame(
        self.newWindow,
        width=200,
        height=500,
        relief=SUNKEN,
        borderwidth=1)
        self.tileEditorFrame.pack(side=RIGHT, expand=True)

        self.BoardFrame = Frame(
        self.newWindow,
        borderwidth=1,
        relief=FLAT,
        width=500,
        height=500)

        self.BoardFrame.pack(side=LEFT, expand=True)

        # The button thats toggles randomizing the color of a placed tile
        self.randomColorButton = Button(
        self.tileEditorFrame,
        text="Random Color",
        width=10,
        command=self.randomColorToggle)
        self.randomColorButton.pack(side=TOP)

        # Button that will allow user to add a new preview tile
        self.addNewPrevTileButton = Button(
        self.tileEditorFrame,
        text="New Tile",
        width=10,
        command=self.addNewPrevTile)
        self.addNewPrevTileButton.pack(side=TOP)

        self.addTileWindow = None # null default init for instance check 

        self.controlsInstructionFrame = Frame(
        self.tileEditorFrame,
        width=20,
        height=20,
        relief=SUNKEN,
        borderwidth=1)

        self.T = Text(self.controlsInstructionFrame, height=20, width=20, wrap=NONE)

        quote = """Controls [Num-Lock MUST BE OFF!!]

Left-Click:
        - Delesect Selection
        - Select Single Square
        - Place Selected Tile

Right-Click:
        - Delete Single Tile

AREA SELECTION TOOL
Ctrl + Left-Click:
        - First sqaure clicked will be highlighted green.
        - Second square will highlight the area between both clicks blue.

        Ctrl + C, copy selection
        Ctrl + V, Select Single Square First
                  If something has been copied then its will paste
        Ctrl + F, Fill Selection with Selected Tile
        Ctrl + D, Deletes the Selection
        Ctrl + T, Flip Vertically
        Ctrl + Y, Flip Horizontally

SPECIAL SELECTION TOOL [Incomplete]
Shift + Left-Click:
        - While holding Left Shift, you can click and highlight a square
          and outline in yellow. The current clicked tile is outline in yellow.
          When clicking on other squares it will start highlighting the area
          between previous clicked and currently clicked square.

Shift + Right-Click:
        - Same as Shift + Left-Click, but deletes the highlight. To use properly
          use a combination of the Shift + Left-Click and Shift + Right-Click.

        Ctrl + F, Fill Selection with Selected Tile
        Ctrl + D, Deletes the Selection

                """
        self.T.insert(END, quote)
        myFont = tkinter.font.Font(
        family='Helvetica', size=12, weight='bold')
        self.T.config(state=DISABLED, font=myFont)

        self.scrollbarTextV = Scrollbar(self.controlsInstructionFrame)
        self.scrollbarTextV.pack(side=RIGHT, fill=Y)
        self.T.config(yscrollcommand=self.scrollbarTextV.set)
        self.scrollbarTextV.config(command=self.T.yview)

        self.scrollbarTextH = Scrollbar(
        self.controlsInstructionFrame, orient=HORIZONTAL)
        self.scrollbarTextH.pack(side=BOTTOM, fill=X)
        self.T.config(xscrollcommand=self.scrollbarTextH.set)
        self.scrollbarTextH.config(command=self.T.xview)

        self.T.pack()
        self.controlsInstructionFrame.pack(side=BOTTOM)

        # Canvas that tile and grid is drawn on
        self.BoardCanvas = Canvas(
        self.BoardFrame,
        width=self.width,
        height=self.height,
        scrollregion=(
        0,
        0,
        self.width,
        self.height))

        self.scrollbarV = Scrollbar(self.BoardFrame)
        self.scrollbarV.pack(side=RIGHT, fill=Y)
        self.BoardCanvas.config(yscrollcommand=self.scrollbarV.set)
        self.scrollbarV.config(command=self.BoardCanvas.yview)

        self.scrollbarH = Scrollbar(self.BoardFrame, orient=HORIZONTAL)
        self.scrollbarH.pack(side=BOTTOM, fill=X)
        self.BoardCanvas.config(xscrollcommand=self.scrollbarH.set)
        self.scrollbarH.config(command=self.BoardCanvas.xview)
        self.BoardCanvas.pack(side=TOP)
        
        

        # Used to tell when a tile is trying to be placed, will send the event to
        # onBoardClick to determine the location
        self.BoardCanvas.bind(
    "<Button-1>",
     lambda event: self.onBoardClick(event))  # -- LEFT CLICK
        self.BoardCanvas.bind(
    "<Button-3>",
     lambda event: self.onBoardClick(event))  # -- RIGHT CLICK
        self.BoardCanvas.bind("<Button-2>", lambda event: self.onBoardClick(event))

        # Location of last square clicked
        self.CURRENTCLICKX = 0
        self.CURRENTCLICKY = 0

        # Defines the area of a selection
        self.SELECTIONX1 = 0
        self.SELECTIONY1 = 0
        self.SELECTIONX2 = 0
        self.SELECTIONY2 = 0

        # Selection box that appears when ctrl clicking
        self.selection = self.BoardCanvas.create_rectangle(
            0, 0, 0, 0, fill="#0000FF", stipple="gray50")
        self.squareSelection = self.BoardCanvas.create_rectangle(
            0, 0, 0, 0, fill="#0000FF", stipple="gray50")

        self.ShiftSelectionMatrix = [[None for y in range(
        self.board.Rows)] for x in range(self.board.Cols)]

        # TODO: Deselect
        self.tilesFrame = Frame(
        self.tileEditorFrame,
        width=200,
        height=200,
        relief=SUNKEN,
        borderwidth=1)
        self.tilePrevCanvas = Canvas(
        self.tilesFrame,
        width=200,
        height=300,
        scrollregion=(
            0,
            0,
            200,
             2000))
        
        
        self.location_text = Label(
            self.tileEditorFrame,
            text="(0, 0)",
        )
        self.location_text.pack()

        self.scrollbarCanvasV = Scrollbar(self.tilesFrame)
        self.scrollbarCanvasV.pack(side=RIGHT, fill=Y)
        self.tilePrevCanvas.config(
        yscrollcommand=self.scrollbarCanvasV.set)
        self.scrollbarCanvasV.config(command=self.tilePrevCanvas.yview)

        self.scrollbarCanvasH = Scrollbar(
            self.tilesFrame, orient=HORIZONTAL)
        self.scrollbarCanvasH.pack(side=BOTTOM, fill=X)
        self.tilePrevCanvas.config(
        xscrollcommand=self.scrollbarCanvasH.set)
        self.scrollbarCanvasH.config(command=self.tilePrevCanvas.xview)

        self.tilePrevCanvas.pack()
        self.tilesFrame.pack(side=TOP)
        self.tilePrevCanvas.pack()

        # draw the board on the canvas os
        self.popWinTiles()
        self.redrawPrev()

        self.highlighted_cross = (None, None)

    # populates the array of tiles

    def populateArray(self):
        self.coord2tile = [[None for x in range(
            self.board.Rows)] for y in range(self.board.Cols)]
        for p in self.board.Polyominoes:
            for tile in p.Tiles:
                self.coord2tile[tile.x][tile.y] = tile
        for conc in self.board.ConcreteTiles:
            self.coord2tile[conc.x][conc.y] = conc

    # ***********************************************************************************************

            # PREVIEW TILE CODE

    # ***********************************************************************************************

    # Called when you click to add a new tile. Will create a small window where you can insert the 4 glues, then add that tile to the
    # preview tile window

    def addNewPrevTile(self):
        global CURRENTNEWTILECOLOR

        if self.addTileWindow: return 
        self.addTileWindow = Toplevel(self.newWindow)
        self.addTileWindow.lift(aboveThis=self.newWindow)

        self.addTileWindow.wm_title("Create Tile")
        self.addTileWindow.resizable(False, False)
        self.addTileWindow.protocol(
    "WM_DELETE_WINDOW",
     lambda: self.closeNewTileWindow())

        self.prevFrame = Frame(
        self.addTileWindow,
        borderwidth=1,
        relief=FLAT,
        width=200,
        height=NEWTILEWINDOW_H - 40)

        # Frame that will hold the text boxes that the glues will be entered it
        self.tileFrame = Frame(
        self.prevFrame,
        borderwidth=1,
        relief=FLAT,
        width=50,
        height=NEWTILEWINDOW_H - 40)
        self.colorFrame = Frame(
        self.prevFrame,
        borderwidth=1,
        relief=FLAT,
        width=100,
         height=NEWTILEWINDOW_H - 40)

        # Canvas that will draw color preview
        self.colorPrevCanvas = Canvas(self.colorFrame, width=100, height=100)

        self.drawColorPreview()

        self.colorPrevCanvas.pack()

        # Frames that hold a label and an entry next to each other
        self.nFrame = Frame(
        self.tileFrame,
        borderwidth=1,
        relief=FLAT,
        width=self.tile_size * 3,
        height=20)
        self.eFrame = Frame(
        self.tileFrame,
        borderwidth=1,
        relief=FLAT,
        width=self.tile_size * 3,
        height=20)
        self.sFrame = Frame(
        self.tileFrame,
        borderwidth=1,
        relief=FLAT,
        width=self.tile_size * 3,
        height=20)
        self.wFrame = Frame(
        self.tileFrame,
        borderwidth=1,
        relief=FLAT,
        width=self.tile_size * 3,
        height=20)

        # Labels and entrys that user will enter the new glue configuration into
        self.glueN = Entry(self.nFrame, textvariable=self.newTileN, width=5)
        self.glueE = Entry(self.eFrame, textvariable=self.newTileE, width=5)
        self.glueS = Entry(self.sFrame, textvariable=self.newTileS, width=5)
        self.glueW = Entry(self.wFrame, textvariable=self.newTileW, width=5)
        self.concreteCheck = Checkbutton(
        self.tileFrame,
        text="Concrete",
        variable=self.concreteChecked)

        self.labelN = Label(self.nFrame, text="N:")
        self.labelE = Label(self.eFrame, text="E:")
        self.labelS = Label(self.sFrame, text="S:")
        self.labelW = Label(self.wFrame, text="W:")

        self.labelN.pack(fill=None, side=LEFT)
        self.labelE.pack(fill=None, side=LEFT)
        self.labelS.pack(fill=None, side=LEFT)
        self.labelW.pack(fill=None, side=LEFT)
        self.concreteCheck.pack(side=BOTTOM)
        self.glueN.pack(fill=None, side=RIGHT)
        self.glueE.pack(fill=None, side=RIGHT)
        self.glueS.pack(fill=None, side=RIGHT)
        self.glueW.pack(fill=None, side=RIGHT)

        self.nFrame.pack(side=TOP)
        self.eFrame.pack(side=TOP)
        self.sFrame.pack(side=TOP)
        self.wFrame.pack(side=TOP)

        self.tileFrame.pack(side=LEFT)
        self.colorFrame.pack(side=RIGHT)

        self.prevFrame.pack(side=TOP)

        # Frame that till hold the two buttons cancel / create
        self.buttonFrame = Frame(
        self.addTileWindow,
        borderwidth=1,
        background="#000",
        relief=FLAT,
        width=300,
        height=200)
        self.buttonFrame.pack(side=BOTTOM)

        self.createButton = Button(
        self.buttonFrame,
        text="Create Tile",
        width=8,
        command=self.createTile)
       
        self.cancelButton = Button(
        self.buttonFrame,
        text="Cancel",
        width=5,
        command=self.cancelTileCreation)
     
        self.setColorButton = Button(
        self.buttonFrame,
        text="Set Color",
        width=8,
        command=self.getColor)

        self.createButton.pack(side=LEFT)
        self.cancelButton.pack(side=RIGHT)
        self.setColorButton.pack(side=LEFT)

        # Makes the new window open over the current editor window
        self.addTileWindow.geometry('%dx%d+%d+%d' % (NEWTILEWINDOW_W, NEWTILEWINDOW_H,
        self.newWindow.winfo_x() + self.newWindow.winfo_width() / 2 - NEWTILEWINDOW_W / 2,
        self.newWindow.winfo_y() + self.newWindow.winfo_height() / 2 - NEWTILEWINDOW_H / 2))

    def editTilePrevTile(self):
        global CURRENTNEWTILECOLOR
        i = self.selectedTileIndex
        tile = self.prevTileList[i]

        if self.addTileWindow is not None:
            return 

        self.addTileWindow = Toplevel(self.newWindow)
        self.addTileWindow.lift(aboveThis=self.newWindow)

        self.addTileWindow.wm_title("Edit Tile")
        self.addTileWindow.resizable(False, False)
        self.addTileWindow.protocol(
        "WM_DELETE_WINDOW",
        lambda: self.closeNewTileWindow())

        self.prevFrame = Frame(
        self.addTileWindow,
        borderwidth=1,
        relief=FLAT,
        width=200,
        height=NEWTILEWINDOW_H - 40)

            # Frame that will hold the text boxes that the glues will be entered it
        self.tileFrame = Frame(
        self.prevFrame,
        borderwidth=1,
        relief=FLAT,
        width=50,
         height=NEWTILEWINDOW_H - 40)
        self.colorFrame = Frame(
        self.prevFrame,
        borderwidth=1,
        relief=FLAT,
        width=100,
        height=NEWTILEWINDOW_H - 40)

        # Canvas that will draw color preview
        self.colorPrevCanvas = Canvas(self.colorFrame, width=100, height=100)

        self.drawColorPreviewEdit(tile.color)
        CURRENTNEWTILECOLOR = tile.color
        self.colorPrevCanvas.pack()

        # Frames that hold a label and an entry next to each other
        self.nFrame = Frame(
        self.tileFrame,
        borderwidth=1,
        relief=FLAT,
        width=self.tile_size * 3,
         height=20)
        self.eFrame = Frame(
        self.tileFrame,
        borderwidth=1,
        relief=FLAT,
        width=self.tile_size * 3,
         height=20)
        self.sFrame = Frame(
        self.tileFrame,
        borderwidth=1,
        relief=FLAT,
        width=self.tile_size * 3,
         height=20)
        self.wFrame = Frame(
        self.tileFrame,
        borderwidth=1,
        relief=FLAT,
        width=self.tile_size * 3,
         height=20)

        # Labels and entrys that user will enter the new glue configuration into
        self.glueN = Entry(self.nFrame, textvariable=self.editTileN, width=5)
        self.glueE = Entry(self.eFrame, textvariable=self.editTileE, width=5)
        self.glueS = Entry(self.sFrame, textvariable=self.editTileS, width=5)
        self.glueW = Entry(self.wFrame, textvariable=self.editTileW, width=5)

        self.editTileN.set(tile.glues[0])
        self.editTileE.set(tile.glues[1])
        self.editTileS.set(tile.glues[2])
        self.editTileW.set(tile.glues[3])

        self.labelN = Label(self.nFrame, text="N:")
        self.labelE = Label(self.eFrame, text="E:")
        self.labelS = Label(self.sFrame, text="S:")
        self.labelW = Label(self.wFrame, text="W:")

        self.labelN.pack(fill=None, side=LEFT)
        self.labelE.pack(fill=None, side=LEFT)
        self.labelS.pack(fill=None, side=LEFT)
        self.labelW.pack(fill=None, side=LEFT)

        self.glueN.pack(fill=None, side=RIGHT)
        self.glueE.pack(fill=None, side=RIGHT)
        self.glueS.pack(fill=None, side=RIGHT)
        self.glueW.pack(fill=None, side=RIGHT)

        self.nFrame.pack(side=TOP)
        self.eFrame.pack(side=TOP)
        self.sFrame.pack(side=TOP)
        self.wFrame.pack(side=TOP)

        self.tileFrame.pack(side=LEFT)
        self.colorFrame.pack(side=RIGHT)

        self.prevFrame.pack(side=TOP)

        # Frame that till hold the two buttons cancel / create
        self.buttonFrame = Frame(
        self.addTileWindow,
        borderwidth=1,
        background="#000",
        relief=FLAT,
        width=300,
         height=200)
        self.buttonFrame.pack(side=BOTTOM)

        self.ApplyButton = Button(
        self.buttonFrame,
        text="Apply",
        width=8,
         command=self.editTile)
        self.DeleteButton = Button(
        self.buttonFrame,
        text="Delete",
        width=8,
         command=self.deleteTile)
        self.cancelButton = Button(
        self.buttonFrame,
        text="Cancel",
        width=5,
         command=self.cancelTileCreation)
        self.setColorButton = Button(
        self.buttonFrame,
        text="Set Color",
        width=8,
         command=self.getColor)

        self.ApplyButton.pack(side=LEFT)
        self.setColorButton.pack(side=LEFT)
        self.DeleteButton.pack(side=LEFT)
        self.cancelButton.pack(side=RIGHT)

        # Makes the new window open over the current editor window
        self.addTileWindow.geometry('%dx%d+%d+%d' % (NEWTILEWINDOW_W, NEWTILEWINDOW_H,
        self.newWindow.winfo_x() + self.newWindow.winfo_width() / 2 - NEWTILEWINDOW_W / 2,
        self.newWindow.winfo_y() + self.newWindow.winfo_height() / 2 - NEWTILEWINDOW_H / 2))

    def getColor(self):
        global CURRENTNEWTILECOLOR
        color = askcolor()
        CURRENTNEWTILECOLOR = color[1]
        self.drawColorPreview()

        # lift editor and new tile above simulator
        self.newWindow.lift(aboveThis=self.parent)
        self.addTileWindow.lift(aboveThis=self.newWindow)

    def drawColorPreviewEdit(self, color):
        self.colorPrevCanvas.delete("all")
        self.colorPrevCanvas.create_rectangle(0, 0, 50, 50, fill=color)

    def drawColorPreview(self):
        global CURRENTNEWTILECOLOR
        self.colorPrevCanvas.delete("all")
        self.colorPrevCanvas.create_rectangle(0, 0, 50, 50, fill=CURRENTNEWTILECOLOR)

    def createTile(self):
        global CURRENTNEWTILECOLOR

        r = lambda: random.randint(100, 255)

        newPrevTile = {}
        # debug_print(newPrevTile)

        color = CURRENTNEWTILECOLOR
        northGlue = self.newTileN.get()
        eastGlue = self.newTileE.get()
        southGlue = self.newTileS.get()
        westGlue = self.newTileW.get()
        label = "x"
        if self.concreteChecked.get() == 1:
            # debug_print("adding concrete")
            isConcrete = "True"
            color = "#686868"
        else:
            isConcrete = "False"
        glues = [northGlue, eastGlue, southGlue, westGlue]
        newTile = TT.Tile(None, 0, 0, 0, glues, color, isConcrete)

        self.prevTileList.append(newTile)
        self.popWinTiles()

    def deleteTile(self):
            self.prevTileList.pop(self.selectedTileIndex)
            self.selectedTileIndex = -1
            self.popWinTiles()
            self.closeNewTileWindow()

    def editTile(self):
        color = CURRENTNEWTILECOLOR
        northGlue = self.editTileN.get()
        eastGlue = self.editTileE.get()
        southGlue = self.editTileS.get()
        westGlue = self.editTileW.get()

        glues = [northGlue, eastGlue, southGlue, westGlue]
        self.prevTileList[self.selectedTileIndex] = TT.Tile(
            None, 0, 0, 0, glues, color, False)

        self.popWinTiles()
        self.closeNewTileWindow()

    def cancelTileCreation(self):
        self.closeNewTileWindow()

    # changes whether a tile placed will have a random color assigned to it
    # also changes the relief of the button to show whether or not it is
    # currently selected
    def randomColorToggle(self):
        # debug_print(self.randomizeColor)
        if self.randomizeColor == True:
            # debug_print("raising")
            self.randomColorButton.config(relief=RAISED)
            self.randomizeColor = False
        else:
            # debug_print("sinking")
            self.randomColorButton.config(relief=SUNKEN)
            self.randomizeColor = True

    # fills the canvas with preview tiles

    def popWinTiles(self):
        global PREVTILESIZE
        global PREVTILESTARTX
        frame_size = 0

        self.tilePrevCanvas.delete("all")
        i = 0
        for prevTile in self.prevTileList:
            # PREVTILESIZE = TILESIZE * 2
            PREVTILESTARTX = (70 - PREVTILESIZE) / 2
            x = (70 - PREVTILESIZE) / 2
            y = PREVTILESTARTY + 80 * i
            size = PREVTILESIZE

            prevTileButton = self.tilePrevCanvas.create_rectangle(
                x, y, x + size, y + size, fill=prevTile.color)
            # tag_bing can bind an object in a canvas to an event, here the rectangle that bounds the
            # preview tile is bound to a mouse click, and it will call selected() with
            # its index as the argument
            self.tilePrevCanvas.tag_bind(
            prevTileButton,
            "<Button-1>",
            lambda event,
             a=i: self.selected(a))
            # buttonArray.append(prevTileButton)

            self.tilePrevCanvas.bind('<Button-1>', lambda event: self.deselect_if_empty(event))

            if prevTile.isConcrete == False:
                # Print Glues
                if prevTile.glues[0] != "None":
                    # north
                    self.tilePrevCanvas.create_text(
                    x + size // 2,
                    y + size // 5,
                    text=prevTile.glues[0],
                    fill="#000",
                    font=(
                        '',
                         size // 5))
                if prevTile.glues[1] != "None":
                    # east
                    self.tilePrevCanvas.create_text(
                    x + size - size // 5,
                    y + size // 2,
                    text=prevTile.glues[1],
                    fill="#000",
                    font=(
                        '',
                         size // 5))
                if prevTile.glues[2] != "None":
                    # south
                    self.tilePrevCanvas.create_text(
                    x + size // 2,
                    y + size - size // 5,
                    text=prevTile.glues[2],
                    fill="#000",
                    font=(
                        '',
                         size // 5))
                if prevTile.glues[3] != "None":
                    # west
                    self.tilePrevCanvas.create_text(
                    x + size // 5,
                    y + size // 2,
                    text=prevTile.glues[3],
                    fill="#000",
                    font=(
                        '',
                         size // 5))

            i += 1
            frame_size = y + size + 10

                # frame_size = (PREVTILESIZE)*len(self.prevTileList) + 20
        self.tilesFrame.config(width=100, height=500)
        self.tilePrevCanvas.config(
        width=100, height=frame_size, scrollregion=(
        0, 0, 200, frame_size))

        self.tilesFrame.pack(side=TOP)
        self.tilePrevCanvas.pack()

    # ***********************************************************************************************

            # **INPUT CODE

    # ***********************************************************************************************

    def onBoardClick(self, event):
        global SHIFTSELECTIONSTARTED
        global SELECTIONSTARTED
        global SELECTIONMADE
        self.BoardCanvas.delete(self.squareSelection)

        # sets right and left click depending on os
        leftClick = 1
        rightClick = 3


        if sys.platform == 'darwin':  # value for OSX
            rightClick = 2

        # print(event.num)
        # print " mods : ", MODS.get(event.state, None)
        # Determine the position on the board the player clicked

        # x = (event.x / self.tile_size)
        # y = (event.y / self.tile_size)

        x = int(self.BoardCanvas.canvasx(event.x)) // self.tile_size
        y = int(self.BoardCanvas.canvasy(event.y)) // self.tile_size

        # print( "EVENT: ",  event.state )

        #event.state == 4 means control is held
        #event.state == 6 means control is held and caps lock is on
        if event.state / 4 % 2 == 1:
            # TODO: DRY the below line 
            if self.highlighted_cross[0]: self.BoardCanvas.delete(*self.highlighted_cross)
            self.CtrlSelect(int(x), int(y))
            self.CURRENTSELECTIONX = int(x)
            self.CURRENTSELECTIONY = int(y)
            self.drawSquareSelectionGreen()
            

        # TODO: Draw axes from corners of selection ?

        #event.state == 1 when shift is held
        #event.state == 3 when shift is held and caps lock is on
        elif event.state % 2 == 1:
            if self.highlighted_cross[0]: self.BoardCanvas.delete(*self.highlighted_cross)
            if event.num == rightClick:
                    self.ShftSelect(x, y, False, False)
            else:
                    self.ShftSelect(x, y, True, False)
            self.CURRENTSELECTIONX = int(x)
            self.CURRENTSELECTIONY = int(y)

        elif self.remove_state or event.num == rightClick:
            self.removeTileAtPos(x, y, True)

        elif event.num == leftClick:

            self.CURRENTSELECTIONX = int(x)
            self.CURRENTSELECTIONY = int(y)
            self.clearSelection()
            self.clearShiftSelection()

            if self.highlighted_cross[0]: self.BoardCanvas.delete(self.highlighted_cross[0], self.highlighted_cross[1])
            self.drawSquareSelectionRed()
            self.HighlightCross(self.CURRENTSELECTIONX, self.CURRENTSELECTIONY)

            # print(self.add_state)
            if self.add_state:
                self.addTileAtPos(x, y)

        elif event.keysym == "r" and MODS.get(event.state, None) == 'Control':
            self.reloadFile() # TODO: No definition for self.reloadFile

    # Handles most key press events

    def keyPressed(self, event):
        global SELECTIONMADE
        
        # TODO: Change this
        if not SELECTIONMADE:
            # if event.keysym == "space":
            # self.tumbleGUI.setTilesFromEditor(self.board, self.glue_data, self.prevTileList, self.board.Cols, self.board.Rows)
            # self.glue_data = {'N':1, 'E':1, 'S':1, 'W':1,  'A': 1, 'B': 1, 'C': 1, 'D': 1, 'X': 1, 'Y': 1, 'Z': 1}
            

            if event.keysym == "Up":
                debug_print("Moving up")
                self.stepAllTiles("N")
            elif event.keysym == "Right":
                debug_print("Moving Right")
                self.stepAllTiles("E")
            elif event.keysym == "Down":
                debug_print("Moving Down")
                self.stepAllTiles("S")
            elif event.keysym == "Left":
                debug_print("Moving Left")
                self.stepAllTiles("W")
        elif SELECTIONMADE:
            if event.keysym == "Up":
                debug_print("Moving up")
                self.stepSelection("N")
            elif event.keysym == "Right":
                debug_print("Moving Right")
                self.stepSelection("E")
            elif event.keysym == "Down":
                debug_print("Moving Down")
                self.stepSelection("S")
            elif event.keysym == "Left":
                debug_print("Mving Left")
                self.stepSelection("W")
        if event.state / 4 % 2 == 1:
            if event.keysym.lower() == "f" and SHIFTSELECTIONSTARTED:
                self.fillInShiftSelection()
                self.clearShiftSelection()
            if event.keysym.lower() == "d" and SHIFTSELECTIONSTARTED:
                self.deleteTilesInShiftSelection()
                self.clearShiftSelection()
            if event.keysym.lower() == "d" and SELECTIONMADE:
                self.deleteTilesInSelection()
                self.clearSelection()
            if event.keysym.lower() == "c" and SELECTIONMADE:
                self.copySelection()
                self.clearSelection()
            if event.keysym.lower() == "v":
                self.pasteSelection()
            if event.keysym.lower() == "t" and SELECTIONMADE:
                self.selectionVerticallyFlipped()
                self.clearSelection()
            if event.keysym.lower() == "y" and SELECTIONMADE:
                self.selectionHorizontallyFlipped()
                self.clearSelection()
            if event.keysym.lower() == "f" and SELECTIONMADE:
                self.fillIn()
                self.clearSelection()
            if event.keysym.lower() == "q" and SELECTIONMADE:
                self.DisplaySelection()
        # if MODS.get( event.state, None ) == 'Shift':
                            
    # TODO: Add stepping seleciton funcitonality

    def stepSelection(self, dir):
        direction = dir
        # print "STEPPING", direction 
        dx = 0
        dy = 0

        if direction == "N":
            dy = -1
            if self.SELECTIONY1 == 0:
                return
        elif direction == "S":
            dy = 1
            if self.SELECTIONY2 == self.board.Rows - 1:
                return
        elif direction == "E":
            dx = 1
            if self.SELECTIONX2 == self.board.Cols - 1:
                return
        elif direction == "W":
            dx = -1
            if self.SELECTIONX1 == 0:
                return


        
        selection = []

        for x in range(self.SELECTIONX1, self.SELECTIONX2 + 1):
            for y in range(self.SELECTIONY1, self.SELECTIONY2 + 1):
                # print "Removing tile at ", x, ", ", y
                selection.append(self.board.coordToTile[x][y])
    
        for tile in selection:
            if tile == None:
                pass
            else:
                if tile.x + dx >= 0 and tile.x + dx < self.board.Cols:
                    tile.x = tile.x + dx
                if tile.y + dy >= 0 and tile.y + dy < self.board.Rows:          
                    tile.y = tile.y + dy
        
        self.redrawPrev()
        self.board.remapArray()
        
        self.SELECTIONX1 = self.SELECTIONX1 + dx
        self.SELECTIONX2 = self.SELECTIONX2 + dx
        self.SELECTIONY1 = self.SELECTIONY1 + dy
        self.SELECTIONY2 = self.SELECTIONY2 + dy
        self.drawSelection(self.SELECTIONX1, self.SELECTIONY1, self.SELECTIONX2, self.SELECTIONY2)

    # This function is called when Ctrl + left click are pressed at the same time. Handles 
    # The creation and deletion of a selection
    def CtrlSelect(self, x, y):
        
        global SELECTIONSTARTED
        global SELECTIONMADE


        if not SELECTIONSTARTED:
            self.clearShiftSelection()

            self.deleteSelection()
            SELECTIONSTARTED = True
            SELECTIONMADE = False
            self.SELECTIONX1 = x
            self.SELECTIONY1 = y

        elif SELECTIONSTARTED:
            # print ("selection made")
            
            SELECTIONMADE = True
            SELECTIONSTARTED = False
            self.SELECTIONX2 = x
            self.SELECTIONY2 = y

            # print "x1: ", self.SELECTIONX1, "y1: ", self.SELECTIONY1
            # print "x2: ", self.SELECTIONX2, "y2: ", self.SELECTIONY2


            if self.SELECTIONX2 < self.SELECTIONX1:
                temp = self.SELECTIONX2
                self.SELECTIONX2 = self.SELECTIONX1
                self.SELECTIONX1 = temp

            if self.SELECTIONY2 < self.SELECTIONY1:
                temp = self.SELECTIONY2
                self.SELECTIONY2 = self.SELECTIONY1
                self.SELECTIONY1 = temp

            self.drawSelection(self.SELECTIONX1, self.SELECTIONY1, self.SELECTIONX2, self.SELECTIONY2)
            self.location_text.config(text=f"Selection: ({self.SELECTIONX1}, {self.SELECTIONY1}), ({self.SELECTIONX2}, {self.SELECTIONY2})")



        # This function is called when Shft + left click are pressed at the same time. Handles 
    # The creation and deletion of a selection
                
    def ShftSelect(self, x, y, option, Left_Alt):
        global SHIFTSELECTIONSTARTED
        # global SELECTIONMADE
                
                
        # print("SHIFTSELECTIONMADE :", SHIFTSELECTIONSTARTED)
                
        if not SHIFTSELECTIONSTARTED:
            self.clearSelection()
            for x1 in range(0, self.board.Cols):
                for y1 in range(0, self.board.Rows):
                    if not self.ShiftSelectionMatrix[x1][y1]  == None:
                        self.BoardCanvas.delete(self.ShiftSelectionMatrix[x1][y1])
            self.ShiftSelectionMatrix = [[None for y2 in range(self.board.Rows)] for x2 in range(self.board.Cols)]
            # print(x,":  :", y)
            self.ShiftSelectionMatrix[x][y] = self.BoardCanvas.create_rectangle(self.tile_size*x, self.tile_size*y, self.tile_size*x + self.tile_size, self.tile_size*y + self.tile_size, fill = "#FFFF00", stipple="gray50")

            SHIFTSELECTIONSTARTED = True
            self.SELECTIONX1 = x
            self.SELECTIONY1 = y
        
        elif SHIFTSELECTIONSTARTED and Left_Alt:
            self.ShiftSelectionMatrix[x][y] = self.BoardCanvas.create_rectangle(self.tile_size*x, self.tile_size*y, self.tile_size*x + self.tile_size, self.tile_size*y + self.tile_size, fill = "#FFFF00", stipple="gray50")
            self.SELECTIONX1 = x
            self.SELECTIONY1 = y
                
        elif SHIFTSELECTIONSTARTED:
            # print ("selection made")
            
            self.SELECTIONX2 = x
            self.SELECTIONY2 = y

            # print "x1: ", self.SELECTIONX1, "y1: ", self.SELECTIONY1
            # print "x2: ", self.SELECTIONX2, "y2: ", self.SELECTIONY2


            if self.SELECTIONX2 < self.SELECTIONX1:
                temp = self.SELECTIONX2
                self.SELECTIONX2 = self.SELECTIONX1
                self.SELECTIONX1 = temp

            if self.SELECTIONY2 < self.SELECTIONY1:
                temp = self.SELECTIONY2
                self.SELECTIONY2 = self.SELECTIONY1
                self.SELECTIONY1 = temp

            
            for x3 in range(self.SELECTIONX1, self.SELECTIONX2+1):
                for y3 in range(self.SELECTIONY1, self.SELECTIONY2+1):
                    if option == True:
                        self.BoardCanvas.delete(self.ShiftSelectionMatrix[x3][y3])
                        self.ShiftSelectionMatrix[x3][y3] = self.BoardCanvas.create_rectangle(self.tile_size*x3, self.tile_size*y3, self.tile_size*x3 + self.tile_size, self.tile_size*y3 + self.tile_size, fill = "#FFFF00", stipple="gray50")
                    else:
                        self.BoardCanvas.delete(self.ShiftSelectionMatrix[x3][y3])
            self.SELECTIONX1 = x
            self.SELECTIONY1 = y
                
        if option == True:
            self.BoardCanvas.delete(self.ShiftSelectionMatrix[x][y])
            self.ShiftSelectionMatrix[x][y] = self.BoardCanvas.create_rectangle(self.tile_size*x, self.tile_size*y, self.tile_size*x + self.tile_size, self.tile_size*y + self.tile_size, fill = "#FFFF00", outline = "#FFFF00", stipple="gray50")

        else:
            self.BoardCanvas.delete(self.ShiftSelectionMatrix[x][y])
            self.ShiftSelectionMatrix[x][y] = self.BoardCanvas.create_rectangle(self.tile_size*x, self.tile_size*y, self.tile_size*x + self.tile_size, self.tile_size*y + self.tile_size, outline = "#FFFF00", stipple="gray50")


    # ***********************************************************************************************

            # SELECTION CODE

    # ***********************************************************************************************
    def clearShiftSelection(self):

        global SHIFTSELECTIONSTARTED


        if SHIFTSELECTIONSTARTED:


            for x in range(0, self.board.Cols):
                for y in range(0, self.board.Rows):
                    # print "clearShiftSelection: ", x,", ", y

                    if not self.ShiftSelectionMatrix[x][y]  == None:
                        self.BoardCanvas.delete(self.ShiftSelectionMatrix[x][y])

            self.ShiftSelectionMatrix = [[None for y in range(self.board.Rows)] for x in range(self.board.Cols)]

        SHIFTSELECTIONSTARTED = False

        
    def clearSelection(self):
        global SELECTIONSTARTED
        global SELECTIONMADE

        self.deleteSelection()
        SELECTIONSTARTED = False
        SELECTIONMADE = False
        
    # This method will outline a square that is clicked on with a red line
    def selected(self, i):
        if self.selectedTileIndex == i:
            if not self.prevTileList[self.selectedTileIndex].isConcrete:
               self.editTilePrevTile()
        else: # TODO: activate edit window via double-click instead of single click 
            self.add_state = True
            self.selectedTileIndex = i
    
            if self.outline is not None:
                self.tilePrevCanvas.delete(self.outline)

            self.outline = self.tilePrevCanvas.create_rectangle(PREVTILESTARTX, PREVTILESTARTY + 80 * i, 
                PREVTILESTARTX + PREVTILESIZE, PREVTILESTARTY + 80 * i + PREVTILESIZE, outline="#FF0000", width = 2)

    def deselect_if_empty(self, event: Event):
        if self.selectedTileIndex == -1: return 

        if not event.widget.find_overlapping(event.x, event.y, event.x, event.y):
            self.tilePrevCanvas.delete(self.outline)
            self.outline = None 

            self.selectedTileIndex = -1 
            self.add_state = False 
            

    def deleteTilesInShiftSelection(self):
        for x in range(0, self.board.Cols):
            for y in range(0, self.board.Rows):
                # print "deleteShiftSelection: ", x,", ", y
                if not self.ShiftSelectionMatrix[x][y]  == None:
                    self.removeTileAtPos(x,y, False)
        self.clearShiftSelection()
        self.redrawPrev()

        

    # Will delete all tile in a selection square.
    def deleteTilesInSelection(self):
        for x in range(self.SELECTIONX1, self.SELECTIONX2 + 1):
            for y in range(self.SELECTIONY1, self.SELECTIONY2 + 1):
                # print "Removing tile at ", x, ", ", y
                self.removeTileAtPos(x,y, False)
        self.redrawPrev()
        self.board.remapArray()


    def HighlightCross(self, x1, y1):
        x_axis = ((0, self.tile_size * y1), (self.tile_size * self.width, self.tile_size * (y1 + 1)))
        y_axis = ((self.tile_size * x1, 0), (self.tile_size * (x1 + 1), self.tile_size * self.height))
        
        # pls blend 
        self.highlighted_cross = (
            self.BoardCanvas.create_rectangle(x_axis[0][0], x_axis[0][1], x_axis[1][0], x_axis[1][1], fill="#2EB8B8", stipple="gray25"),
            self.BoardCanvas.create_rectangle(y_axis[0][0], y_axis[0][1], y_axis[1][0], y_axis[1][1], fill="#2EB8B8", stipple="gray25"),
        )
        self.location_text.config(text=f"({x1}, {y1})")


    # When you control click in two locations this method will draw the resulting rectangle
    def drawSelection(self, x1, y1, x2, y2):
        # print("x1: ", x1, "    y1: ", y1, "   x2: ", x2, "   y2: ", y2)

        self.selection = self.BoardCanvas.create_rectangle(self.tile_size*x1, self.tile_size*y1, self.tile_size*x2 + self.tile_size, self.tile_size*y2 + self.tile_size, fill = "#0000FF", stipple="gray50")


    # Deletes the selection drawing from the board
    def deleteSelection(self):
        self.BoardCanvas.delete(self.selection)

        # WIll store a copy of all the tiles in a seleciton so that it can be pasted

    # TODO: Cross-Editor Clipboard
    def copySelection(self):
        global COPYMADE
        global COPIED_SELECTION
        global COPIED_SELECTION_COORDS
        COPIED_SELECTION_COORDS = ICoordPair2D(self.SELECTIONX1, self.SELECTIONY1, self.SELECTIONX2, self.SELECTIONY2)
        # TODO: Clean up clipboarding code. It is messy because a hotfix was requested. 
        COPYMADE = True

        COPIED_SELECTION = [[None for x in range(abs(self.SELECTIONY2 - self.SELECTIONY1) + 1)] for y in range(abs(self.SELECTIONX2 - self.SELECTIONX1) + 1)]

        for x in range(self.SELECTIONX1, self.SELECTIONX2 + 1):
            # print "X index: ", x
            for y in range(self.SELECTIONY1, self.SELECTIONY2 + 1):
                # print "y index: ", y
                # print "Copying tile at ", x, ", ", y, " to ", x - self.SELECTIONX1, ", ", y - self.SELECTIONY1

                try:
                    COPIED_SELECTION[x - self.SELECTIONX1][y - self.SELECTIONY1] = copy.deepcopy(self.board.coordToTile[x][y])
                except IndexError:
                    # TODO: Replace this and others with error logging. 
                    print("Error: tried to access COPIED_SELECTION[", x - self.SELECTIONX1, "][", y - self.SELECTIONY1, "]")
                    print("Its size is ", len(COPIED_SELECTION), ", ", len(COPIED_SELECTION[0]))

                    print("Error: tried to access self.board.coordToTile[", x, "][", y, "]")
                    print("Its size is ", len(self.board.coordToTile[x]), ", ", len(self.board.coordToTile[x]))


    def selectionVerticallyFlipped(self):
        global CURRENTNEWTILECOLOR
        global COPIED_SELECTION
        color = CURRENTNEWTILECOLOR
        
        self.copySelection()

        self.CURRENTSELECTIONX = self.SELECTIONX1
        self.CURRENTSELECTIONY = self.SELECTIONY1
        # print("CURRENT SELECTION X : ", self.CURRENTSELECTIONX)
        # print("CURRENT SELECTION Y : ", self.CURRENTSELECTIONY)
        # print("SELECTION X1 : ", self.SELECTIONX1)
        # print("SELECTION X2 : ", self.SELECTIONX2)
        # print("SELECTION Y1 : ", self.SELECTIONY1)
        # print("SELECTION Y2 : ", self.SELECTIONY2)

        selectionWidth = self.SELECTIONX2 - self.SELECTIONX1 + 1
        selectionHeight = self.SELECTIONY2 - self.SELECTIONY1  + 1
        for x in range(0, selectionWidth):
                for y in range(0, selectionHeight):
                        # print "Removing tile at ", x + self.CURRENTSELECTIONX, ", ", y + self.CURRENTSELECTIONY
                        self.removeTileAtPos(self.CURRENTSELECTIONX + x,self.CURRENTSELECTIONY + y, False)
                        

        # print("pasting")

        selectionWidth = self.SELECTIONX2 - self.SELECTIONX1 + 1
        selectionHeight = self.SELECTIONY2 - self.SELECTIONY1  + 1

        # print "Width: ", selectionWidth
        # print "Height: ", selectionHeight

        for x in range(0, selectionWidth):
            for y in range(0, selectionHeight):

                try:    
                    if(COPIED_SELECTION[x][y] == None):
                        continue
                    else:
                        tile = COPIED_SELECTION[x][y]

                except IndexError:
                    print("Error: tried to access COPIED_SELECTION[", x, "][", y, "]")
                    print("Its size is ", len(COPIED_SELECTION), ", ", len(COPIED_SELECTION[0]))

                # print "x: ",x
                # print "y: ", y

                

                if tile == None:
                    continue

                newX = self.CURRENTSELECTIONX + x
                # print "NEWX: ", newX
                newY = self.CURRENTSELECTIONY + (selectionHeight - y) - 1
                # print "NEWY: ", newY

                if newX > self.board.Rows or newY > self.board.Cols:
                    continue

                p = TT.Polyomino(0, newX, newY, tile.glues, tile.color)

                northGlue = self.newTileN.get()
                eastGlue = self.newTileE.get()
                southGlue = self.newTileS.get()
                westGlue = self.newTileW.get()
                

                glues = [northGlue, eastGlue, southGlue, westGlue]
                color = "#686868"
        
            
                newConcTile = TT.Tile(None, 0, newX, newY, glues , color , True)

                # COPIED_SELECTION[x][y].x = newX
                # COPIED_SELECTION[x][y].y = newY

                if COPIED_SELECTION[x][y].isConcrete:
                    # print "is concrete"
                    self.board.AddConc(newConcTile)
                elif not COPIED_SELECTION[x][y].isConcrete:
                    self.board.Add(p)
        self.redrawPrev()
        self.board.remapArray()
            
    def selectionHorizontallyFlipped(self):
            global CURRENTNEWTILECOLOR
            global COPIED_SELECTION
            color = CURRENTNEWTILECOLOR
            self.copySelection()

            self.CURRENTSELECTIONX = self.SELECTIONX1
            self.CURRENTSELECTIONY = self.SELECTIONY1
            # print("CURRENT SELECTION X : ", self.CURRENTSELECTIONX)
            # print("CURRENT SELECTION Y : ", self.CURRENTSELECTIONY)
            # print("SELECTION X1 : ", self.SELECTIONX1)
            # print("SELECTION X2 : ", self.SELECTIONX2)
            # print("SELECTION Y1 : ", self.SELECTIONY1)
            # print("SELECTION Y2 : ", self.SELECTIONY2)

            selectionWidth = self.SELECTIONX2 - self.SELECTIONX1 + 1
            selectionHeight = self.SELECTIONY2 - self.SELECTIONY1  + 1
            for x in range(0, selectionWidth):
                    for y in range(0, selectionHeight):
                            # print "Removing tile at ", x + self.CURRENTSELECTIONX, ", ", y + self.CURRENTSELECTIONY
                            self.removeTileAtPos(self.CURRENTSELECTIONX + x,self.CURRENTSELECTIONY + y, False)
                            

            # print("pasting")

            selectionWidth = self.SELECTIONX2 - self.SELECTIONX1 + 1
            selectionHeight = self.SELECTIONY2 - self.SELECTIONY1  + 1

            # print "Width: ", selectionWidth
            # print "Height: ", selectionHeight

            for x in range(0, selectionWidth):
                for y in range(0, selectionHeight):

                    try:    
                        if(COPIED_SELECTION[x][y] == None):
                            continue
                        else:
                            tile = COPIED_SELECTION[x][y]

                    except IndexError:
                        print("Error: tried to access COPIED_SELECTION[", x, "][", y, "]")
                        print("Its size is ", len(COPIED_SELECTION), ", ", len(COPIED_SELECTION[0]))

                    # print "x: ",x
                    # print "y: ", y

                    

                    if tile == None:
                            continue

                    newX = self.CURRENTSELECTIONX + (selectionWidth - x) - 1
                    # print "NEWX: ", newX
                    newY = self.CURRENTSELECTIONY + y
                    # print "NEWY: ", newY

                    if newX > self.board.Rows or newY > self.board.Cols:
                            continue
                    p = TT.Polyomino(0, newX, newY, tile.glues, tile.color)
                    northGlue = self.newTileN.get()
                    eastGlue = self.newTileE.get()
                    southGlue = self.newTileS.get()
                    westGlue = self.newTileW.get()
                    

                    glues = [northGlue, eastGlue, southGlue, westGlue]
                    color = "#686868"
            
                
                    newConcTile = TT.Tile(None, 0, newX, newY, glues , color , True)

                    # COPIED_SELECTION[x][y].x = newX
                    # COPIED_SELECTION[x][y].y = newY

                    if COPIED_SELECTION[x][y].isConcrete:
                        # print "is concrete"
                        self.board.AddConc(newConcTile)
                    elif not COPIED_SELECTION[x][y].isConcrete:
                        self.board.Add(p)

            self.redrawPrev()
            self.board.remapArray()


    def fillInShiftSelection(self):
        for x in range(0, self.board.Cols):
            for y in range(0, self.board.Rows):
                if not self.ShiftSelectionMatrix[x][y]  == None:
                    self.addTileAtPos(x, y)
        self.clearShiftSelection()
        self.redrawPrev()
        self.board.remapArray()
                
    def fillIn(self):

        self.CURRENTSELECTIONX = self.SELECTIONX1
        self.CURRENTSELECTIONY = self.SELECTIONY1
        # print("CURRENT SELECTION X : ", self.CURRENTSELECTIONX)
        # print("CURRENT SELECTION Y : ", self.CURRENTSELECTIONY)
        # print("SELECTION X1 : ", self.SELECTIONX1)
        # print("SELECTION X2 : ", self.SELECTIONX2)
        # print("SELECTION Y1 : ", self.SELECTIONY1)
        # print("SELECTION Y2 : ", self.SELECTIONY2)

        selectionWidth = self.SELECTIONX2 - self.SELECTIONX1 + 1
        selectionHeight = self.SELECTIONY2 - self.SELECTIONY1  + 1
        for x in range(0, selectionWidth):
            for y in range(0, selectionHeight):
                # print "Removing tile at ", x + self.CURRENTSELECTIONX, ", ", y + self.CURRENTSELECTIONY
                self.removeTileAtPos(self.CURRENTSELECTIONX + x,self.CURRENTSELECTIONY + y, False)
                        

        # print("fill in")

        selectionWidth = self.SELECTIONX2 - self.SELECTIONX1 + 1
        selectionHeight = self.SELECTIONY2 - self.SELECTIONY1  + 1

        # print "Width: ", selectionWidth
        # print "Height: ", selectionHeight

        for x in range(0, selectionWidth):
            for y in range(0, selectionHeight):
                newX = self.CURRENTSELECTIONX + (selectionWidth - x) - 1
                # print "NEWX: ", newX
                newY = self.CURRENTSELECTIONY + y
                # print "NEWY: ", newY

                if newX > self.board.Rows or newY > self.board.Cols:
                        continue
                
                self.addTileAtPos(newX, newY)
                        

        self.redrawPrev()
        self.board.remapArray()
                
    # Paste all tiles in the stored selection in the new selected spot
    def pasteSelection(self):
        global CURRENTNEWTILECOLOR
        color = CURRENTNEWTILECOLOR
        

        global COPYMADE
        global COPIED_SELECTION
        global COPIED_SELECTION_COORDS
        self.SELECTIONX1 = COPIED_SELECTION_COORDS.x1 
        self.SELECTIONX2 = COPIED_SELECTION_COORDS.x2 
        self.SELECTIONY1 = COPIED_SELECTION_COORDS.y1 
        self.SELECTIONY2 = COPIED_SELECTION_COORDS.y2 

        if not COPYMADE:
            debug_print("Nothing to paste")

        else:

            for x in range(0, self.SELECTIONX2 - self.SELECTIONX1):
                for y in range(0, self.SELECTIONY2 - self.SELECTIONY1):
                    debug_print("Removing tile at ", x + self.CURRENTSELECTIONX, ", ", y + self.CURRENTSELECTIONY)
                    self.removeTileAtPos(self.CURRENTSELECTIONX + x,self.CURRENTSELECTIONY + y, False)
                    

            # print("pasting")

            selectionWidth = self.SELECTIONX2 - self.SELECTIONX1 + 1
            selectionHeight = self.SELECTIONY2 - self.SELECTIONY1  + 1

            # print "Width: ", selectionWidth
            # print "Height: ", selectionHeight

            for x in range(0, selectionWidth):
                for y in range(0, selectionHeight):

                    try:    
                        if(COPIED_SELECTION[x][y] == None):
                            continue
                        else:
                            tile = COPIED_SELECTION[x][y]

                    except IndexError:
                        print("Error: tried to access COPIED_SELECTION[", x, "][", y, "]")
                        print("Its size is ", len(COPIED_SELECTION), ", ", len(COPIED_SELECTION[0]))

                    # print "x: ",x
                    # print "y: ", y

                    

                    if tile == None:
                        continue

                    newX = self.CURRENTSELECTIONX + x
                    # print "NEWX: ", newX
                    newY = self.CURRENTSELECTIONY + y
                    # print "NEWY: ", newY

                    if newX > self.board.Rows or newY > self.board.Cols:
                        continue

                    p = TT.Polyomino(0, newX, newY, tile.glues, tile.color)
                    northGlue = self.newTileN.get()
                    eastGlue = self.newTileE.get()
                    southGlue = self.newTileS.get()
                    westGlue = self.newTileW.get()
                    

                    glues = [northGlue, eastGlue, southGlue, westGlue]
                    color = "#686868"
            
                
                    newConcTile = TT.Tile(None, 0, newX, newY, glues , color , True)


                    # COPIED_SELECTION[x][y].x = newX
                    # COPIED_SELECTION[x][y].y = newY

                    if COPIED_SELECTION[x][y].isConcrete:
                        # print "is concrete"
                        self.board.AddConc(newConcTile)
                    elif not COPIED_SELECTION[x][y].isConcrete:
                        self.board.Add(p)





        self.redrawPrev()
        self.board.remapArray()


    def DisplaySelection(self):
        global COPIED_SELECTION
        debug_print(COPIED_SELECTION)

    def drawSquareSelectionYellow(self):
        self.BoardCanvas.delete(self.squareSelection)
        self.squareSelection = self.BoardCanvas.create_rectangle(self.tile_size*self.CURRENTSELECTIONX, self.tile_size*self.CURRENTSELECTIONY, self.tile_size*self.CURRENTSELECTIONX + self.tile_size, self.tile_size*self.CURRENTSELECTIONY + self.tile_size, outline = "#FFFF00", stipple="gray50")
    
    def drawSquareSelectionRed(self):
        self.BoardCanvas.delete(self.squareSelection)
        self.squareSelection = self.BoardCanvas.create_rectangle(self.tile_size*self.CURRENTSELECTIONX, self.tile_size*self.CURRENTSELECTIONY, self.tile_size*self.CURRENTSELECTIONX + self.tile_size, self.tile_size*self.CURRENTSELECTIONY + self.tile_size, outline = "#FF0000", stipple="gray50")
    
    def drawSquareSelectionGreen(self):
        self.BoardCanvas.delete(self.squareSelection)
        self.squareSelection = self.BoardCanvas.create_rectangle(self.tile_size*self.CURRENTSELECTIONX, self.tile_size*self.CURRENTSELECTIONY, self.tile_size*self.CURRENTSELECTIONX + self.tile_size, self.tile_size*self.CURRENTSELECTIONY + self.tile_size, outline = "#00FF00", stipple="gray50")
        

    # ***********************************************************************************************

            # Utility Code

    # ***********************************************************************************************


    

    def getTileIndex(self, widget_name):
        names = widget_name.split('.')
        return int(names[len(names) - 1].strip())
    
    # Removes tile at (x,y), redraw is a flag whether or not to redraw after removal
    def removeTileAtPos(self, x, y, redraw):
        # print "trying to remove tile at ", x, ", ", y

        try:
            tile = self.board.coordToTile[x][y]
        except IndexError:
            return

        if tile == None:
            return

        if tile.isConcrete:
            self.board.ConcreteTiles.remove(tile)
            self.board.coordToTile[x][y] = None
        
        else:
            tile.parent.Tiles.remove(tile) #remove tile from the polyomino that its in
            if len(tile.parent.Tiles) == 0:
                self.board.Polyominoes.remove(tile.parent) #remove polyomino from the array
            
            self.board.coordToTile[x][y] = None

        # self.verifyTileLocations()
        if redraw:
            self.redrawPrev()

        

    def addTileAtPos(self, f_x: float, f_y: float):
        x = int(f_x)
        y = int(f_y)
        
        i = self.selectedTileIndex

        if self.board.coordToTile[x][y] != None:
            return


        # random color function: https://stackoverflow.com/questions/13998901/generating-a-random-hex-color-in-python
        r = lambda: random.randint(100,255)
        if self.randomizeColor:
            color = ('#%02X%02X%02X' % (r(),r(),r()))
        else:
            color = self.prevTileList[i].color


        if not self.prevTileList[i].isConcrete:
            newPoly = TT.Polyomino(0, x, y, self.prevTileList[i].glues, color)
            self.board.Add(newPoly)
            self.board.coordToTile[x][y]= newPoly.Tiles[0]
        else:
            newConcTile = TT.Tile(None, 0, x, y, [], self.prevTileList[i].color, "True")
            self.board.AddConc(newConcTile)
            self.board.coordToTile[x][y]= newConcTile



        # self.verifyTileLocations()
        self.redrawPrev()


    
    def verifyTileLocations(self):
        verified = True
        for p in self.board.Polyominoes:
            for tile in p.Tiles:
                if self.board.coordToTile[tile.x][tile.y] != tile:
                    debug_print("ERROR: Tile at ", tile.x, ", ", tile.y, " is not in array properly \n", end=' ')
                    verified = False

        for tile in self.board.ConcreteTiles:
            if self.board.coordToTile[tile.x][tile.y] != tile:
                debug_print("ERROR: Tile at ", tile.x, ", ", tile.y, " is not in array properly \n", end=' ')
                verified = False

        # if verified:
        #     print("Tile Locations Verified")
        # if not verified:
        #     print("Tile Locations Incorrect")





    def stepAllTiles(self, direction):
        debug_print("STEPPING", direction) 
        dx = 0
        dy = 0

        crosses_edge_north = False  
        crosses_edge_south = False 
        crosses_edge_west  = False 
        crosses_edge_east  = False 

        for y in range(self.board.Cols):
            if self.board.coordToTile[0][y] is not None: crosses_edge_west = True 
            if self.board.coordToTile[-1][y] is not None: crosses_edge_east = True 

        for x in range(self.board.Rows):
            if self.board.coordToTile[x][0] is not None: crosses_edge_north = True 
            if self.board.coordToTile[x][-1] is not None: crosses_edge_south = True 

        if direction == "N":
            if crosses_edge_north: return 
            dy = -1
        elif direction == "S":
            if crosses_edge_south: return 
            dy = 1
        elif direction == "E":
            if crosses_edge_east: return 
            dx = 1
        elif direction == "W":
            if crosses_edge_west: return 
            dx = -1

        for p in self.board.Polyominoes:
            for tile in p.Tiles:
                if tile.x + dx >= 0 and tile.x < self.board.Cols:
                        tile.x = tile.x + dx
                if tile.x + dx >= 0 and tile.x < self.board.Cols:   
                        tile.y = tile.y + dy


            
        for tile in self.board.ConcreteTiles:
            if tile.x + dx >= 0 and tile.x + dx < self.board.Cols:
                tile.x = tile.x + dx
            if tile.y + dy >= 0 and tile.y + dy < self.board.Rows:          
                tile.y = tile.y + dy

        self.redrawPrev()
        self.board.remapArray()



    def Board(self, w, h):

        self.board_w = w
        self.board_h = h


        self.board.Cols = self.board_w
        self.board.Rows = self.board_h
        self.board.resizeBoard(w,h)

        self.newWindow.geometry(str(self.board_w*self.tile_size + self.tilePrevCanvas.winfo_width() + 20)+'x'+str(self.board_h*self.tile_size+76))
        self.BoardCanvas.config(width=self.board_w*self.tile_size, height=self.board_h*self.tile_size)
        self.BoardCanvas.pack(side=LEFT)

        self.populateArray()
        self.redrawPrev()

    

    def resizeBoard(self, w, h):
        self.board_w = w
        self.board_h = h

        self.board.Cols = self.board_w 
        self.board.Rows = self.board_h
        self.board.resizeBoard(w,h)

        self.newWindow.geometry(str(self.board_w*self.tile_size + self.tilePrevCanvas.winfo_width() + 20)+'x'+str(self.board_h*self.tile_size+76))
        self.BoardCanvas.config(width=self.board_w*self.tile_size, height=self.board_h*self.tile_size, scrollregion=(0, 0, self.board_w*self.tile_size, self.board_w*self.tile_size))
        self.BoardCanvas.pack(side=TOP)
        self.populateArray()
        self.redrawPrev()
        self.ShiftSelectionMatrix = [[None for y in range(self.board.Rows)] for x in range(self.board.Cols)]


        
        
    def boardResizeDial(self):
        # print"boardResizeDial: ", self.board_w,", ", self.board_h
        wr = self.WindowResizeDialogue(self.newWindow, self, self.board_w, self.board_h)

    def redrawPrev(self):
        redrawCanvas(self.board, self.board.Cols, self.board.Rows, self.BoardCanvas, self.tile_size, b_drawGrid = True, b_drawLoc = self.tkSHOWLOC.get())


    def onApply(self):
        self.tumbleEdit.resizeBoard(int(self.bw.get()), int(self.bh.get()))
        self.pressed_apply = True
        self.w.destroy()

    def onAddState(self):
        self.remove_state = False
        self.add_state = True
        
    def onRemoveState(self):
        self.remove_state = True
        self.add_state = False
        self.selectedTileIndex = -1


    def onClearState(self):
        self.remove_state = False
        self.add_state = False
        self.tile_to_add = None





    # ***********************************************************************************************

            # File I/O Code

    # ***********************************************************************************************



    def newBoard(self):
        del self.board.Polyominoes[:]
        self.board.LookUp = {}

        self.board = TT.Board(self.board.Cols,  self.board.Rows)
        bh = self.board.Cols
        bw = self.board.Rows
        TT.GLUEFUNC = {'N':1, 'E':1, 'S':1, 'W':1,}
        self.redrawPrev()

    def exportTiles(self):
        # print("new cols : ", self.board.Cols, "new rows : ", self.board.Rows)

        self.tumbleGUI.setTilesFromEditor(self.board, self.glue_data, self.prevTileList, self.board.Cols, self.board.Rows)

    def saveTileConfig(self):
        filename = tkinter.filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("eXtensible Markup Language", ".xml")])
        if not filename: 
            return
        

        tile_config = ET.Element("TileConfiguration")
        board_size = ET.SubElement(tile_config, "BoardSize")
        glue_func = ET.SubElement(tile_config, "GlueFunction")
                
        board_size.set("width", str(self.board.Cols))       
        board_size.set("height", str(self.board.Rows))

                
        # Add all preview tiles to the .xml file if there are any
        p_tiles = ET.SubElement(tile_config, "PreviewTiles")
        if len(self.prevTileList) != 0:
            for td in self.prevTileList:
                # print(td.color)
                if td.glues == [] or len(td.glues) == 0:
                        td.glues = [0,0,0,0]

                # Save the tile data exactly as is
                prevTile = ET.SubElement(p_tiles, "PrevTile")


                c = ET.SubElement(prevTile, "Color")
                c.text = str(td.color).replace("#", "")


                ng = ET.SubElement(prevTile, "NorthGlue")
                

                sg = ET.SubElement(prevTile, "SouthGlue")


                eg = ET.SubElement(prevTile, "EastGlue")
                

                wg = ET.SubElement(prevTile, "WestGlue")
                

                if len(td.glues) > 0:
                    ng.text = str(td.glues[0])
                    sg.text = str(td.glues[2])
                    eg.text = str(td.glues[1])
                    wg.text = str(td.glues[3])

                co = ET.SubElement(prevTile, "Concrete")
                co.text = str(td.isConcrete)

                la = ET.SubElement(prevTile, "Label")
                la.text = str(td.id)



        tiles = ET.SubElement(tile_config, "TileData")
        # save all tiles on the board to the .xml file
        for p in self.board.Polyominoes:
            for tile in p.Tiles:
                # print(tile)
                if tile.glues == None or len(tile.glues) == 0:
                    tile.glues = [0,0,0,0]

                t = ET.SubElement(tiles, "Tile")

                loc = ET.SubElement(t, "Location")
                loc.set("x", str(tile.x))
                loc.set("y", str(tile.y))

                c = ET.SubElement(t, "Color")
                c.text = str(str(tile.color).replace("#", ""))

                ng = ET.SubElement(t, "NorthGlue")
                ng.text = str(tile.glues[0])

                sg = ET.SubElement(t, "SouthGlue")
                sg.text = str(tile.glues[2])

                eg = ET.SubElement(t, "EastGlue")
                eg.text = str(tile.glues[1])

                wg = ET.SubElement(t, "WestGlue")
                wg.text = str(tile.glues[3])

                co = ET.SubElement(t, "Concrete")
                co.text = str(tile.isConcrete)



                la = ET.SubElement(t, "Label")
                la.text = str(tile.id)

        for conc in self.board.ConcreteTiles:
        
            # print(conc)
            if conc.glues == None or len(conc.glues) == 0:
                conc.glues = [0,0,0,0]

            t = ET.SubElement(tiles, "Tile")

            loc = ET.SubElement(t, "Location")
            loc.set("x", str(conc.x))
            loc.set("y", str(conc.y))

            c = ET.SubElement(t, "Color")
            c.text = str(str(conc.color).replace("#", ""))

            ng = ET.SubElement(t, "NorthGlue")
            ng.text = str(conc.glues[0])

            sg = ET.SubElement(t, "SouthGlue")
            sg.text = str(conc.glues[2])

            eg = ET.SubElement(t, "EastGlue")
            eg.text = str(conc.glues[1])

            wg = ET.SubElement(t, "WestGlue")
            wg.text = str(conc.glues[3])

            co = ET.SubElement(t, "Concrete")
            co.text = str(conc.isConcrete)

            la = ET.SubElement(t, "Label")
            la.text = str(conc.id)

        # Just port the glue function data over to the new file
        # print "glue data in tumbleedit.py ", self.glue_data
        for gl in self.glue_data:
            gs = self.glue_data[gl]
            f = ET.SubElement(glue_func, "Function")
            l = ET.SubElement(f, "Labels")
            l.set('L1', gl)
            s = ET.SubElement(f, "Strength")
            s.text = str(gs)

            commands = ET.SubElement(tile_config, "Commands")
            for c in self.tumbleGUI.listOfCommands:
                    command = ET.SubElement(commands, "Command")
                    command.set("name", str(c[0]))
                    command.set("filename", str(c[1]))
                    debug_print("Name: ", c[0],", Filename: ", c[1])
                        
        # print tile_config
        mydata = ET.tostring(tile_config)

        if ".xml" not in filename:
            filename = filename + ".xml"

        file = open(filename, "wb")
        file.write(mydata)

        self.newWindow.master.title(f"{filename.split('/')[-1]}")
        self.newWindow.title(f"Editor - {self.parent.title()}")




    def closeGUI(self):
        self.newWindow.destroy()
        self.newWindow.destroy()

    def closeNewTileWindow(self):
        self.addTileWindow.destroy()
        self.addTileWindow = None 


    class WindowResizeDialogue:
        def onApply(self):
            self.tumbleEdit.resizeBoard(int(self.bw.get()), int(self.bh.get()))
            self.pressed_apply = True
            self.w.destroy()
        
        def __init__(self, parent, tumbleEdit, board_w, board_h):

            self.parent = parent

            self.tumbleEdit = tumbleEdit

            self.bw = board_w
            self.bh = board_h

            self.bw = StringVar()
            self.bw.set(str(board_w))

            self.bh = StringVar()
            self.bh.set(str(board_h))

            self.w = Toplevel(self.parent)
            self.w.resizable(True, True)
            self.pressed_apply = False

            Label(self.w, text="Width:").pack()
            self.bw_sbx=Spinbox(self.w, from_=10, to=1000,width=5, increment=5, textvariable = self.bw)
            # self.e1.insert(0, str(board_w))
            self.bw_sbx.pack()

            Label(self.w, text="Height:").pack()
            self.bh_sbx = Spinbox(self.w, from_=10, to=1000,width=5, increment=5, textvariable = self.bh)
            # self.e2.insert(0, str(board_h))
            self.bh_sbx.pack()


            Button(self.w, text="Apply:", command = lambda: self.onApply()).pack()

            self.w.focus_set()
            # Make sure events only go to our dialog
            self.w.grab_set()
            # Make sure dialog stays on top of its parent window (if needed)
            self.w.transient(self.parent)
            # Display the window and wait for it to close
            self.w.wait_window(self.w)




    # ***********************************************************************************************

            # LEGACY CODE

    # ***********************************************************************************************




        






