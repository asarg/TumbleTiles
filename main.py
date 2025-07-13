# GUI for Tumble Tiles
# Tim Wylie
# 2018


from __future__ import absolute_import
from __future__ import print_function
import copy
import threading

from tkinter import *
from tkinter import messagebox
import tkinter.ttk 
import tkinter.filedialog
import tkinter.messagebox
import tkinter.colorchooser
import xml.etree.ElementTree as ET
import random
import time
import tumbletiles as TT
import tumbleEdit as TE

import tt2svg as TT2SVG

from getFile import getFile, parseFile, FileType
from boardgui import redrawCanvas, drawGrid, redrawTumbleTiles, deleteTumbleTiles, drawPILImage
import os
import sys


from PIL import Image, ImageDraw
# https://pypi.python.org/pypi/pyscreenshot

try:
    PYSCREEN = False
    # imp.find_module('pyscreenshot')
    import pyscreenshot as ImageGrab
    PYSCREEN = True
except ImportError:
    PYSCREEN = False
try:
    IMAGEIO = False
    import imageio as io
    IMAGEIO = True
except ImportError:
    IMAGEIO = False

try:
    PILLOW = False
    import imageio as io
    PILLOW = True
except ImportError:
    PILLOW = False

NEWTILEWINDOW_W = 400

NEWTILEWINDOW_H = 180

LOGFILE = None
LOGFILENAME = ""
#TODO: Change back to 25
TILESIZE = 12
VERSION = "2.0"
LASTLOADEDFILE = ""
LASTLOADEDSCRIPT = ""
SCRIPTSPEED = 1
RECORDING = False
SCRIPTSEQUENCE = ""



# https://stackoverflow.com/questions/19861689/check-if-modifier-key-is-pressed-in-tkinter
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


class ScriptExecutorThread(threading.Thread):
    def __init__(self, threadID, name, counter, tg, onstop=lambda: ...):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.tg = tg
        self.f = None
        self.onstop = onstop

    def setScript(self, f):
        self.f = f

    def run_once_(self):
        for c in self.f:
            if self.counter == 0:
                break

            time.sleep(self.counter / 1000)
            
            self.tg.MoveDirection(c)
            

    def run(self):
        if self.tg.tkLoopScript.get():
            while self.tg.tkLoopScript.get() and self.counter != 0:
                self.run_once_()
        else:
            self.run_once_()

        self.onstop()


class MsgAbout:
    def __init__(self, parent):
        global VERSION
        self.parent = parent
        self.t = Toplevel(self.parent)
        self.t.resizable(False, False)
        self.t.wm_title("About")
        # self.t.geometry('200x200') #WxH

        self.photo = PhotoImage(file="tumble.gif")

        # Return a new PhotoImage based on the same image as this widget but
        # use only every Xth or Yth pixel.
        self.display = self.photo.subsample(3, 3)
        self.label = Label(self.t, image=self.display, width=90, height=80)
        self.label.image = self.display  # keep a reference!
        self.label.pack()

        self.l1 = Label(
            self.t,
            text="Tumble Tiles v" +
            VERSION,
            font=(
                '',
                15)).pack()
        Label(self.t, text="Tim Wylie").pack()
        Label(self.t, text="For support contact schwellerr@gmail.com").pack()

        Button(self.t, text="OK", width=10, command=self.t.destroy).pack()

        self.t.focus_set()
        # Make sure events only go to our dialog
        self.t.grab_set()
        # Make sure dialog stays on top of its parent window (if needed)
        self.t.transient(self.parent)
        # Display the window and wait for it to close
        self.t.wait_window(self.t)


class ScriptSettings:
    def __init__(self, parent):
        global SCRIPTSPEED 

        self.parent = parent 
        self.top_level = Toplevel(self.parent)
        self.top_level.resizable(False, False)
        self.top_level.title("Script Settings")

        self.tkSCRIPTSPEED = StringVar()
        self.tkSCRIPTSPEED.set(str(SCRIPTSPEED))

        self.script_speed_label = Label(
            self.top_level,
            text="Time per Step (ms)").grid(
                row=0,
                column=0,
                sticky=W,
                padx=5,
                pady=5)
        self.script_speed_input = Spinbox(
            self.top_level,
            from_=1,
            to=1000,
            width=5,
            increment=0.1,
            textvariable=self.tkSCRIPTSPEED).grid(
                row=0,
                column=1,
                padx=5,
                pady=5)
        
        # buttons
        Button(
            self.top_level,
            text="Cancel",
            command=self.top_level.destroy).grid(
            row=1,
            column=0,
            padx=5,
            pady=5)
        Button(
            self.top_level,
            text="Apply",
            command=self.apply).grid(
            row=1,
            column=1,
            padx=5,
            pady=5)

        Label(
            self.top_level, 
            text="Note: Must reload script after changes.", 
            wraplength=145, 
            justify="left").grid(
                row=2, 
                column=0, 
                columnspan=2, 
                padx=5, 
                pady=5, 
                sticky=W)
        
        self.top_level.focus_set()
        self.top_level.grab_set()
        self.top_level.transient(self.parent)
        self.top_level.wait_window(self.top_level)
        
    def config_error(self):
        messagebox.showerror("Error", "Script speed must be a number between 1 and 1000")

    def apply(self):
        global SCRIPTSPEED
        
        try:
            SCRIPTSPEED = float(self.tkSCRIPTSPEED.get())
        except ValueError:
            self.config_error()
            return

        if SCRIPTSPEED < 1 or SCRIPTSPEED > 1000:
            self.config_error()
            return

        self.top_level.destroy()


class Settings:
    def __init__(self, parent, logging, tumblegui):  # , fun):
        global TILESIZE

        self.tumbleGUI = tumblegui
        self.logging = logging
        #self.function = fun
        self.parent = parent
        self.t = Toplevel(self.parent)
        self.t.resizable(False, False)
        #self.wm_attributes("-disabled", True)
        self.t.wm_title("Board Options")
        # self.toplevel_dialog.transient(self)
        # self.t.geometry('180x180')  # wxh
        self.parent.update_idletasks()
        parentX = self.parent.winfo_x()
        parentY = self.parent.winfo_y()
        parentW = self.parent.winfo_width()
        parentH = self.parent.winfo_height()
        x = parentX + (parentW // 2) - (180 // 2)
        y = parentY + (parentH // 2) - (180 // 2)
        self.t.geometry(f'180x180+{x}+{y}')

        self.tkTILESIZE = StringVar()
        self.tkTILESIZE.set(str(TILESIZE))
        self.tkBOARDWIDTH = StringVar()
        self.tkBOARDWIDTH.set(str(TT.BOARDWIDTH))
        self.tkBOARDHEIGHT = StringVar()
        self.tkBOARDHEIGHT.set(str(TT.BOARDHEIGHT))
        self.tkTEMP = StringVar()
        self.tkTEMP.set(str(TT.TEMP))

        # tilesize
        self.l1 = Label(
            self.t,
            text="Tile Size").grid(
            row=0,
            column=0,
            sticky=W,
            padx=5,
            pady=5)
        self.tilesize_sbx = Spinbox(
            self.t,
            from_=10,
            to=100,
            width=5,
            increment=5,
            textvariable=self.tkTILESIZE).grid(
            row=0,
            column=1,
            padx=5,
            pady=5)
        # board width
        self.l2 = Label(
            self.t,
            text="Board Width").grid(
            row=1,
            column=0,
            padx=5,
            pady=5,
            sticky=W)
        self.boardwidth_sbx = Spinbox(
            self.t,
            from_=10,
            to=500,
            width=5,
            textvariable=self.tkBOARDWIDTH).grid(
            row=1,
            column=1,
            padx=5,
            pady=5)
        # board height
        self.l3 = Label(
            self.t,
            text="Board Height").grid(
            row=2,
            column=0,
            padx=5,
            pady=5,
            sticky=W)
        self.boardheight_sbx = Spinbox(
            self.t,
            from_=10,
            to=500,
            width=5,
            textvariable=self.tkBOARDHEIGHT).grid(
            row=2,
            column=1,
            padx=5,
            pady=5)
        # temperature
        self.l4 = Label(
            self.t,
            text="Temperature").grid(
            row=3,
            column=0,
            padx=5,
            pady=5,
            sticky=W)
        self.temperature_sbx = Spinbox(
            self.t,
            from_=1,
            to=10,
            width=5,
            textvariable=self.tkTEMP).grid(
            row=3,
            column=1,
            padx=5,
            pady=5)
        # buttons
        Button(
            self.t,
            text="Cancel",
            command=self.t.destroy).grid(
            row=4,
            column=0,
            padx=5,
            pady=5)
        Button(
            self.t,
            text="Apply",
            command=self.Apply).grid(
            row=4,
            column=1,
            padx=5,
            pady=5)

        self.t.focus_set()
        # Make sure events only go to our dialog
        self.t.grab_set()
        # Make sure dialog stays on top of its parent window (if needed)
        self.t.transient(self.parent)
        # Display the window and wait for it to close
        self.t.wait_window(self.t)

    def Apply(self):
        global TILESIZE

        TILESIZE = int(self.tkTILESIZE.get())
        TE.TILESIZE = TILESIZE
        if TT.BOARDWIDTH != int(self.tkBOARDWIDTH.get()):
            self.Log("\nChange BOARDWIDTH from " +
                     str(TT.BOARDWIDTH) + " to " + self.tkBOARDWIDTH.get())
            TT.BOARDWIDTH = int(self.tkBOARDWIDTH.get())
        if TT.BOARDHEIGHT != int(self.tkBOARDHEIGHT.get()):
            self.Log("\nChange BOARDHEIGHT from " +
                     str(TT.BOARDHEIGHT) + " to " + self.tkBOARDHEIGHT.get())
            TT.BOARDHEIGHT = int(self.tkBOARDHEIGHT.get())
        if TT.TEMP != int(self.tkTEMP.get()):
            self.Log("\nChange TEMP from " + str(TT.TEMP) +
                     " to " + self.tkTEMP.get())
            TT.TEMP = int(self.tkTEMP.get())

        self.tumbleGUI.callCanvasRedraw()
        self.t.destroy()

    def Log(self, stlog):
        global LOGFILE
        global LOGFILENAME

        if self.logging:
            LOGFILE = open(LOGFILENAME, 'a')
            LOGFILE.write(stlog)
            LOGFILE.close()

class VideoExport:
    def __init__(self, parent, tumblegui):  # , fun):
        # TODO: Fix-dynamicize padding. It's atrocious. 
        global TILESIZE

        self.tumbleGUI = tumblegui
        #self.function = fun
        self.parent = parent

        self.parent = parent
        self.t = Toplevel(self.parent)
        self.t.resizable(False, False)
        #self.wm_attributes("-disabled", True)
        self.t.wm_title("Video Export")
        # self.toplevel_dialog.transient(self)
        self.t.geometry('360x280') 


        self.tileRes=StringVar()                # Variable for Tile Resolution
        self.fileName= StringVar()              # Variable for the script file name
        self.videoSpeed = StringVar()           # Variale for the frame rate
        self.lineWidth = StringVar()            # Variable for the width of tile border
        self.exportFileNameText = StringVar()   # Variabe for name of the output file
        self.exportText = StringVar()           # Variable for the text that logs the video output


        # Set default amounts

        self.tileRes.set("100")
        self.videoSpeed.set("3")
        self.lineWidth.set("10")


        # Initiate all Label objects

        self.tileResLabel = Label(self.t, text="Tile Resolution: ")
        self.fileNameLabel = Label(self.t, text="Script File Name: ")
        self.videoSpeedLabel = Label(self.t, text="Frames/Sec: ")
        self.lineWidthLabel = Label(self.t, text="Line Width: ")
        self.exportLabel = Label(self.t, text="", textvariable=self.exportText)
        self.exportFileNameLabel = Label(self.t, text="Output File Name:")
        
        # Initiate all text field objects

        self.tileResField = Entry(self.t, textvariable=self.tileRes, width=5)
        self.fileNameField = Entry(self.t, textvariable=self.fileName)
        self.videoSpeedField = Entry(self.t, textvariable=self.videoSpeed, width=5)
        self.lineWidthField = Entry(self.t, textvariable=self.lineWidth, width=5)
        # self.exportFileNameField = Entry(self.t, textvariable=self.exportFileNameText, width=5)
        
        

        # Horizontal starting points for the labels and the fields

        labelStartX=60
        fieldStartX=180

        # Place all the components using x and y coordinates

        self.tileResLabel.place(x=labelStartX, y=20)
        self.tileResField.place(x=fieldStartX, y=20)

        self.lineWidthLabel.place(x=labelStartX, y=40)
        self.lineWidthField.place(x=fieldStartX,y=40)

        self.fileNameLabel.place(x=labelStartX, y=80)
        self.fileNameField.place(x=fieldStartX,y=80, width=130)

        self.exportFileNameLabel.place(x=labelStartX, y=130)
        self.exportFileNameLabel.config(wraplength=360-labelStartX)
        # self.exportFileNameField.place(x=fieldStartX,y=130, width=130)

        self.videoSpeedLabel.place(x=labelStartX, y=60)
        self.videoSpeedField.place(x=fieldStartX, y=60)

        browseButton = Button(self.t, text="Browse", command=self.openFileWindow)
        browseButton.place(x=fieldStartX, y=100, height=20)


        self.exportLabel.place(x=labelStartX, y=175)
        # Create a progres bar to show status of video export

        self.progress_var = DoubleVar() 
        self.progress=tkinter.ttk.Progressbar(self.t,orient=HORIZONTAL,variable=self.progress_var,length=260,mode='determinate')
        self.progress.place(x=50, y=195)
        
        # Place export button    

        exportButton = Button(self.t, text="Export", command=self.export)
        exportButton.place(x=150, y=230)


        
    def openFileWindow(self):
        fileName = getFile(FileType.TXT)

        self.fileName.set(fileName)
        # self.fileNameField.delete(0,END)
        # self.fileNameField.insert(0, fileName)
        

    def export(self):   

        #Create a copy of the board to reset to once the recording is done
        boardCopy = copy.deepcopy(self.tumbleGUI.board)

        # Convert the tile resolution to an INT

        self.tileResInt = int(self.tileRes.get())

        self.createGif()

        # Delete the current board and restore the old board
        del(self.tumbleGUI.board)
        self.tumbleGUI.board = boardCopy
       


    # This function will load a script (sequence of directions to tumble) and
    # step through it, it will save a temp image in ./Gifs/ and compile these
    # into a gif
    def createGif(self):


        self.progress_var.set(0)        # Set progress bar to 0
        self.exportText.set("")         # Set the export text to blank

        filename = self.fileName.get()  # Get the filename from the text field
        file = open(filename, "r")


        # Calculate duration of each frame from the Framerate text field

        framesPerSec = 1000 / int(self.videoSpeed.get())

        lineWidthInt = int(self.lineWidth.get())

        images = [] 

        sequence = file.readlines()[0].rstrip('\n') # Read in the script file

        seqLen = len(sequence)  # total length used for progress bar


        # # If Videos folder does not exist, create it
        # if not os.path.exists("Videos"):
        #     os.makedirs("Videos")

        exportFile = tkinter.filedialog.asksaveasfilename(confirmoverwrite=True, defaultextension=".gif", filetypes=[("Graphics Interchange Format", ".gif")])
        self.exportFileNameLabel.config(text=f"Output File Name: {exportFile}")

        # if self.exportFileNameText.get() == "": # If no file name was given create one
        
        #     x = 0
        #     y = 0
        #     z = 0
        #     while os.path.exists("Videos/%s%s%s.gif" % (x, y, z)):
        #         z = z + 1
        #         if z == 10:
        #             z = 0
        #             y = y + 1
        #         if y == 10:
        #             y = 0
        #             x = x + 1

        #     exportFile = ("Videos/%s%s%s.gif" % (x, y, z))
        # else:
        #     exportFile = "Videos/" + self.exportFileNameText.get() + ".gif"

        for x in range(0, len(sequence)):   


            self.progress_var.set(float(x)/seqLen * 100)    # Update progress bar
            self.t.update()                                 # update toplevel window
           
            
            self.tumbleGUI.MoveDirection(sequence[x], redraw= False) # Move the board in the specified direction
            

            # Call function to get and image in memory of the current state of the board, passing it the tile resolution and the line width to use
            image = self.tumbleGUI.getImageOfBoard(self.tileResInt, lineWidthInt)

            # Append the returned image to the image array
            images.append(image)
        
        # Save the image

        images[0].save(exportFile, save_all=True, append_images=images[1:], duration=framesPerSec, loop=1)

        # Set the export Text
        self.exportText.set("Video saved at "+exportFile)

        # Update the progress bar and update the toplevel to redraw the progress bar

        self.progress_var.set(100)
        self.t.update()

        


################################################################
class tumblegui:
    def __init__(self, root):
        global TILESIZE
        self.thread1 = ScriptExecutorThread(1, "Thread-1", 0, self, self.reinitializeRunScript)
        self.stateTmpSaves = []
        self.polyTmpSaves = []

        self.maxStates = 255
        self.CurrentState = -1

        # 3 sets of data that the class will keep track of, these are used to sending tiles to the editor or updating the board
        # when tile data is received from the editor
        self.tile_data = None  # the data of the actual tiles on the board
        self.glueFunc = {}  # contains the glue function
        # contains the preview tiles so if the editor needs to be reopened the
        # preview tiles are reserved
        self.prevTileList = []

        self.board = TT.Board(TT.BOARDHEIGHT, TT.BOARDWIDTH)
        self.root = root
        self.root.resizable(True, True)
        self.mainframe = Frame(self.root, bd=0, relief=FLAT)

        FACTORYMODE = BooleanVar()
        FACTORYMODE.set(False)
        self.rightFrame = Frame(
            self.mainframe,
            width=200,
            height=500,
            relief=SUNKEN,
            borderwidth=1)
        self.BoardFrame = Frame(
            self.mainframe,
            borderwidth=1,
            relief=FLAT,
            width=TT.BOARDWIDTH *
            TILESIZE,
            height=TT.BOARDHEIGHT *
            TILESIZE)

        # main canvas to draw on
        self.w = Canvas(
            self.BoardFrame,
            width=TT.BOARDWIDTH *
            TILESIZE,
            height=TT.BOARDHEIGHT *
            TILESIZE,
            scrollregion=(
                0,
                0,
                TT.BOARDWIDTH *
                TILESIZE,
                TT.BOARDHEIGHT *
                TILESIZE))
        # mouse
        self.w.bind("<Button-1>", self.callback)
        # arrow keys
        self.root.bind("<Up>", self.keyPressed)
        self.root.bind("<Right>", self.keyPressed)
        self.root.bind("<Down>", self.keyPressed)
        self.root.bind("<Left>", self.keyPressed)
        self.root.bind("<space>", self.keyPressed)
        self.root.bind("<Key>", self.keyPressed)

        self.scrollbarV = Scrollbar(self.BoardFrame)
        self.scrollbarV.pack(side=RIGHT, fill=Y)
        self.w.config(yscrollcommand=self.scrollbarV.set)
        self.scrollbarV.config(command=self.w.yview)

        self.scrollbarH = Scrollbar(self.BoardFrame, orient=HORIZONTAL)
        self.scrollbarH.pack(side=BOTTOM, fill=X)
        self.w.config(xscrollcommand=self.scrollbarH.set)
        self.scrollbarH.config(command=self.w.xview)
        self.w.pack()
        self.rightFrame.pack(side=RIGHT, expand=True)
        self.BoardFrame.pack(side=LEFT, expand=True)

        # menu
        # menu - https://www.tutorialspoint.com/python/tk_menu.htm
        self.menubar = Menu(self.root, relief=RAISED)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New Board", command=self.newBoard)
        self.filemenu.add_command(
            label="Create SVG",
            command=lambda: self.createSvg())
        self.filemenu.add_command(label="Example", command=self.CreateInitial)
        #filemenu.add_command(label="Generate Tiles", command=self.openTileEditDial)
        self.filemenu.add_command(
            label="Load", command=lambda: self.loadFile())
        self.filemenu.add_command(
            label="Reload Last File",
            command=lambda: self.reloadFile())

        self.tkLOG = BooleanVar()
        self.tkLOG.set(False)
        self.filemenu.add_checkbutton(
            label="Log Actions",
            onvalue=True,
            offvalue=False,
            variable=self.tkLOG,
            command=self.EnableLogging)

        if PYSCREEN:
            self.filemenu.add_command(label="Picture", command=self.picture)
        else:
            self.filemenu.add_command(
                label="Picture",
                command=self.picture,
                state=DISABLED)

        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.root.quit)

        self.aboutmenu = Menu(self.menubar, tearoff=0)
        self.aboutmenu.add_command(label="About", command=self.about)

        self.tkSTEPVAR = BooleanVar()
        self.tkSTEPVAR.set(False)
        self.tkGLUESTEP = BooleanVar()
        self.tkGLUESTEP.set(False)

        self.tkDRAWGRID = BooleanVar()
        self.tkDRAWGRID.set(False)
        self.tkSHOWLOC = BooleanVar()
        self.tkSHOWLOC.set(False)
        self.tkFACTORYMODE = BooleanVar()
        self.tkFACTORYMODE.set(False)

        self.tkLoopScript = BooleanVar()
        self.tkLoopScript.set(False)

        # This text will change from "Record Script" to "Stop Recording"
        self.recordScriptText = "Record Script"
        self.runScriptText = "Run Script"

        self.settingsmenu = Menu(self.menubar, tearoff=0)
        self.settingsmenu.add_checkbutton(
            label="Single Step",
            onvalue=True,
            offvalue=False,
            variable=self.tkSTEPVAR,
            command=self.setSingleStep)  # ,command=stepmodel)
        self.settingsmenu.add_checkbutton(
            label="Glue on Step",
            onvalue=True,
            offvalue=False,
            variable=self.tkGLUESTEP)  # ,state=DISABLED)
        self.settingsmenu.add_separator()
        self.settingsmenu.add_command(
            label="Background Color",
            command=self.changecanvas)
        self.settingsmenu.add_checkbutton(
            label="Show Grid",
            onvalue=True,
            offvalue=False,
            variable=self.tkDRAWGRID,
            command=lambda: self.callCanvasRedraw())
        self.settingsmenu.add_command(
            label="Grid Color",
            command=self.changegridcolor)
        self.settingsmenu.add_checkbutton(
            label="Show Locations",
            onvalue=True,
            offvalue=False,
            variable=self.tkSHOWLOC,
            command=lambda: self.callCanvasRedraw())
        self.settingsmenu.add_separator()
        self.settingsmenu.add_command(
            label="Board Options",
            command=self.changetile)
        self.settingsmenu.add_checkbutton(
            label="Factory Mode",
            onvalue=True,
            offvalue=False,
            variable=self.tkFACTORYMODE,
            command=self.setFactoryMode)

        self.editormenu = Menu(self.menubar, tearoff=0)
        self.editormenu.add_command(
            label="Open Editor",
            command=self.editCurrentTiles)

        self.scriptmenu = Menu(self.menubar, tearoff=0)
        self.scriptmenu.add_command(
            label=self.recordScriptText,
            command=self.recordScript)
        self.scriptmenu.add_command(
            label=self.runScriptText,
            command=self.loadScript)
        self.scriptmenu.add_checkbutton(
            label="Loop",
            onvalue=True,
            offvalue=False,
            variable=self.tkLoopScript)
        if PILLOW:
            self.scriptmenu.add_command(
                label="Export Video..", command=self.openVideoExportWindow)
        else:
            self.scriptmenu.add_command(
                label="Export Video..",
                command=self.openVideoExportWindow,
                state=DISABLED)
        self.scriptmenu.add_separator()
        self.scriptmenu.add_command(label="Settings", command=self.scriptSettings)

        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Settings", menu=self.settingsmenu)
        self.menubar.add_cascade(label="Editor", menu=self.editormenu)
        self.menubar.add_cascade(label="Script", menu=self.scriptmenu)
        self.menubar.add_cascade(label="Help", menu=self.aboutmenu)
        self.root.config(menu=self.menubar)

        # toolbar
        # http://zetcode.com/gui/tkinter/menustoolbars/
        self.toolbar = Frame(self.rightFrame, bd=0, relief=FLAT, height=10)
        lab1 = Label(
            self.toolbar,
            text="Width:",
            justify=RIGHT).pack(
            side=LEFT)
        self.tkWidthText = StringVar()
        self.tkWidthText.set(TT.BOARDWIDTH)
        bgcol = self.toolbar['bg']  # ._root().cget('bg')
        Label(
            self.toolbar,
            textvariable=self.tkWidthText,
            width=3,
            padx=0,
            justify=LEFT,
            relief=FLAT).pack(
            side=LEFT)

        Label(
            self.toolbar,
            text="          Height:",
            justify=RIGHT).pack(
            side=LEFT)
        self.tkHeightText = StringVar()
        self.tkHeightText.set(TT.BOARDHEIGHT)
        Label(
            self.toolbar,
            textvariable=self.tkHeightText,
            width=3,
            padx=0,
            justify=LEFT,
            relief=FLAT).pack(
            side=LEFT)

        Label(
            self.toolbar,
            text="          Temp:",
            justify=RIGHT).pack(
            side=LEFT)
        self.tkTempText = StringVar()
        self.tkTempText.set(TT.TEMP)
        Label(
            self.toolbar,
            textvariable=self.tkTempText,
            width=3,
            padx=0,
            justify=LEFT,
            relief=FLAT).pack(
            side=LEFT)


#################################################
        self.addSequenceButton = Button(
            self.rightFrame,
            text="Add Sequence",
            width=10,
            command=self.addSequenceWin)

        self.newCommandName = StringVar()
        self.newCommandFile = StringVar()

        self.listOfCommands = []
        self.listOfCommandButtons = []
#################################################
        self.TilesFrame = Frame(
            self.rightFrame,
            width=200,
            height=200,
            relief=SUNKEN,
            borderwidth=1)
        self.tilePrevCanvas = Canvas(
            self.TilesFrame,
            width=200,
            height=300,
            scrollregion=(
                0,
                0,
                200,
                2000))

        self.scrollbarCanvasV = Scrollbar(self.TilesFrame)
        self.scrollbarCanvasV.pack(side=RIGHT, fill=Y)
        self.tilePrevCanvas.config(yscrollcommand=self.scrollbarCanvasV.set)
        self.scrollbarCanvasV.config(command=self.tilePrevCanvas.yview)

        self.scrollbarCanvasH = Scrollbar(self.TilesFrame, orient=HORIZONTAL)
        self.scrollbarCanvasH.pack(side=BOTTOM, fill=X)
        self.tilePrevCanvas.config(xscrollcommand=self.scrollbarCanvasH.set)
        self.scrollbarCanvasH.config(command=self.tilePrevCanvas.xview)

        self.tilePrevCanvas.pack()

#################################################

        self.toolbar.pack(side=TOP, fill=X)
        self.addSequenceButton.pack(side=TOP)
        self.TilesFrame.pack(side=TOP)
        self.mainframe.pack()

        toolbarframeheight = 24
        self.w.config(
            width=self.board.Cols *
            TILESIZE,
            height=self.board.Rows *
            TILESIZE)

        self.root.geometry(str(self.board.Cols * TILESIZE + 300) + 'x' +
                           str(self.board.Rows * TILESIZE + toolbarframeheight))

        # other class variables
        self.gridcolor = "#000000"
        self.textcolor = "#000000"

        self.callGridDraw()
        #self.CreateInitial()
        self.glue_data = []

    def TestThreadDisplay(self):
        print ("testing \n")

    def TestThread(self):
        self.thread1.start()

    # Sets the factory mode variable
    def setFactoryMode(self):
        TT.FACTORYMODE = self.tkFACTORYMODE.get()

    # sets the single step variable declared in the tumbletiles.py file
    def setSingleStep(self):
        TT.SINGLESTEP = self.tkSTEPVAR.get()

    def scriptSettings(self):
        ScriptSettings(self.root)
        ...

    def recordScript(self):
        global RECORDING
        global SCRIPTSEQUENCE

        if not RECORDING:
            RECORDING = True
            SCRIPTSEQUENCE = ""
            self.scriptmenu.entryconfigure(0, label='Stop Recording')
        elif RECORDING:
            self.scriptmenu.entryconfigure(0, label='Record Script')
            filename = tkinter.filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Plain Text", ".txt")])
            if not filename: return
            file = open(filename, 'w+')
            file.write(SCRIPTSEQUENCE)
            file.close()
            RECORDING = False

    def reinitializeRunScript(self):
        self.thread1.counter = 0
        self.thread1 = ScriptExecutorThread(1, "Thread-1", 0, self, self.reinitializeRunScript)
        self.scriptmenu.entryconfigure(1, label='Run Script')

    # Gets the path of the script from the gui file browser
    def loadScript(self):
        global LASTLOADEDSCRIPT
        if self.thread1.counter == 0:
            filename = getFile(FileType.TXT)
            if not filename: return
            LASTLOADEDSCRIPT = filename
            file = open(filename, "r")
            self.runScript(file)
        else:
            self.reinitializeRunScript()

    # Returns a PIL image object of the board by calling the function in boardgui.py
    def getImageOfBoard(self, tileResInt, lineWidthInt):

        return drawPILImage(
            self.board,
            self.board.Cols,
            self.board.Rows,
            self.w,
            TILESIZE,
            self.textcolor,
            self.gridcolor,
            self.tkDRAWGRID.get(),
            self.tkSHOWLOC.get(),
            tileRes=tileResInt,
            lineWidth=lineWidthInt)

    # Call the sequence runner
    def runScript(self, file):
        global SCRIPTSPEED

        self.scriptmenu.entryconfigure(1, label='Stop Script')
        script = file.readlines()[0].rstrip('\n')
        #self.thread1.counter = 0.0000001
        self.thread1.counter = SCRIPTSPEED
        self.thread1.setScript(script)
        self.thread1.start()
        # self.runSequence(script)

    # Steps through string in script and tumbles in that direction

    # TODO: Integrate into sequence widget
    def runSequence(self, sequence):
        global SCRIPTSPEED

        for x in range(0, len(sequence)):
            time.sleep(SCRIPTSPEED / 1000)
            
            self.MoveDirection(sequence[x])
            
            # print sequence[x], " - ",

            self.w.update_idletasks()

    def changetile(self):
        global TILESIZE

        Sbox = Settings(self.root, self.tkLOG.get(), self)
        self.resizeBoardAndCanvas()
        self.tkTempText.set(TT.TEMP)

    def resizeBoardAndCanvas(self):

        self.board.Cols = TT.BOARDWIDTH
        self.board.Rows = TT.BOARDHEIGHT
        self.board.remapArray()
        toolbarframeheight = 24
        self.root.geometry(str(self.board.Cols * TILESIZE + 300) + 'x' +
                           str(self.board.Rows * TILESIZE + toolbarframeheight))
        self.w.config(
            width=self.board.Cols *
            TILESIZE,
            height=self.board.Rows *
            TILESIZE,
            scrollregion=(
                0,
                0,
                TT.BOARDWIDTH *
                TILESIZE,
                TT.BOARDHEIGHT *
                TILESIZE))
        self.w.pack()
        self.tkWidthText.set(self.board.Cols)
        self.tkHeightText.set(self.board.Rows)
        # resize window #wxh

        # self.root.geometry(str(self.board.Cols*TILESIZE)+'x'+str(self.board.Rows*TILESIZE+toolbarframeheight))
        # redraw
        self.callCanvasRedraw()

    # Handles the arrow keys to call the tumbling and the shortcuts for file
    # options

    def keyPressed(self, event):
        global RECORDING
        global SCRIPTSEQUENCE

        
        if event.keysym == "Up":
            self.MoveDirection("N")
        elif event.keysym == "Right":
            self.MoveDirection("E")
        elif event.keysym == "Down":
            self.MoveDirection("S")
        elif event.keysym == "Left":
            self.MoveDirection("W")
        elif event.keysym == "space":
            def clear(): return os.system('cls')
            clear()
            for x in self.listOfCommands:
                print(x[0], " ", x[1])
        


        # if RECORDING:
        ##                print SCRIPTSEQUENCE
        ##            print "Current State: ",self.CurrentState
        ##            print "Length of states: ", len(self.stateTmpSaves)
        # for z in self.stateTmpSaves:
        # i=0
        # for x in z:
        ##                    print "polyomino",i, ", \n"
        ##                    i = i+1
        # for y in x.Tiles:
        ##                        print "     tile:",y.x,", ",y.y


        elif event.keysym == "z":
            self.Undo()
        elif event.keysym == "a":
            self.ApplyUndo()
        elif event.keysym == "x":
            self.Redo()
        elif event.keysym == "1":
            self.Zoom(-1)
        elif event.keysym == "2":
            self.Zoom(1)
        elif event.keysym == "r" and MODS.get(event.state, None) == 'Control':
            self.reloadFile()
        # print(event.keysym)

        

    def callback(self, event):
        global TILESIZE

        try:
            #print "clicked at", event.x, event.y
            if event.y <= 2 * TILESIZE and event.x > 2 * \
                    TILESIZE and event.x < TT.BOARDWIDTH * TILESIZE - 2 * TILESIZE:
                
                self.MoveDirection("N")
                
            elif event.y >= TT.BOARDHEIGHT * TILESIZE - 2 * TILESIZE and event.x > 2 * TILESIZE and event.x < TT.BOARDWIDTH * TILESIZE - 2 * TILESIZE:
                
                self.MoveDirection("S")
                
            elif event.x >= TT.BOARDWIDTH * TILESIZE - 2 * TILESIZE and event.y > 2 * TILESIZE and event.y < TT.BOARDHEIGHT * TILESIZE - 2 * TILESIZE:
                
                self.MoveDirection("E")
                
            elif event.x <= 2 * TILESIZE and event.y > 2 * TILESIZE and event.y < TT.BOARDHEIGHT * TILESIZE - 2 * TILESIZE:
                
                self.MoveDirection("W")
                 

        except BaseException:
            pass

    def performSequence(self, i):
        print("some Function: ", i)
        print("Command Name: ", self.listOfCommands[i][0])
        print("File Name: ", self.listOfCommands[i][1])
        #file = open(self.listOfCommands[i][1], "r")

        self.scriptmenu.entryconfigure(1, label='Stop Script')
        script = self.listOfCommands[i][1]
        self.thread1.counter = 0.0000001
        self.thread1.setScript(script)
        self.thread1.start()

    def popWinSequences(self):
        ##		global PREVTILESIZE
        ##		global PREVTILESTARTX
        frame_size = 0
        for prevTile in self.listOfCommandButtons:
            prevTile.destroy()
        for x in range(0, len(self.listOfCommandButtons)):
            self.listOfCommandButtons.pop()
        i = -1
        for prevTile in self.listOfCommands:
            i += 1
            # PREVTILESIZE = TILESIZE * 2
    ##			PREVTILESTARTX = (70 - PREVTILESIZE) / 2
    ##		 	x = (70 - PREVTILESIZE) / 2
    ##		 	y = PREVTILESTARTY + 80 * i
    ##		 	size = PREVTILESIZE

            #prevTileButton = self.tilePrevCanvas.create_rectangle(x, y, x + size, y + size, fill = prevTile.color)
            # tag_bing can bind an object in a canvas to an event, here the rectangle that bounds the
            # preview tile is bound to a mouse click, and it will call selected() with its index as the argument
            #self.tilePrevCanvas.tag_bind(prevTileButton, "<Button-1>", lambda event, a=i: self.someFunction(a))

            # buttonArray.append(prevTileButton)

            frame_size = 10
            self.listOfCommandButtons.append(
                Button(
                    self.tilePrevCanvas,
                    text=prevTile[0],
                    width=8,
                    command=lambda a=i: self.performSequence(a),
                    padx=10))

        for prevTile in self.listOfCommandButtons:
            prevTile.pack()

        ##frame_size = (PREVTILESIZE)*len(self.prevTileList) + 20
        self.TilesFrame.config(width=150, height=500)
        self.tilePrevCanvas.config(
            width=100, height=frame_size, scrollregion=(
                0, 0, 500, frame_size + 500))

        self.TilesFrame.pack(side=TOP)
        self.tilePrevCanvas.pack()

    def closeNewSequenceWindow(self):
        self.addSequenceWindow.destroy()

    def addSequence(self):
        if(self.newCommandFile.get() == "No File Selected"):
            print("No File Seleceted")
        elif(self.newCommandName.get().strip() == ""):
            print("No Name Entered")
        else:
            print("There was a file Selected: ", self.newCommandFile.get())
            print("Command Name Entered: ", self.newCommandName.get())

            filename = self.newCommandFile.get()
            file = open(filename, "r")
            script = file.readlines()[0].rstrip('\n')
            sequence = ""
            for x in range(0, len(script)):
                print(script[x], " - ", end=' ')
                sequence = sequence + script[x]
                # self.tg.w.update_idletasks()

            self.listOfCommands.append(
                (self.newCommandName.get().strip(), sequence))
            self.popWinSequences()

        self.closeNewSequenceWindow()

    def selectSequence(self):
        filename = getFile()
        self.newCommandFile.set(filename)

    def addSequenceWin(self):
        global CURRENTNEWTILECOLOR

        self.addSequenceWindow = Toplevel(self.root)
        self.addSequenceWindow.lift(aboveThis=self.root)
        self.addSequenceWindow.wm_title("Create Sequence")
        self.addSequenceWindow.resizable(False, False)
        self.addSequenceWindow.protocol(
            "WM_DELETE_WINDOW",
            lambda: self.closeNewSequenceWindow())

        self.prevFrame = Frame(
            self.addSequenceWindow,
            borderwidth=1,
            relief=FLAT,
            width=200,
            height=NEWTILEWINDOW_H - 40)
        self.filename = Label(self.prevFrame, textvariable=self.newCommandFile)
        self.newCommandFile.set("No File Selected")
        self.filename.pack()
        self.prevFrame.pack()

        self.nameFrame = Frame(self.prevFrame, borderwidth=1, relief=FLAT)
        self.nameLabel = Label(self.nameFrame, text="Command Name:")
        self.commandName = Entry(
            self.nameFrame,
            textvariable=self.newCommandName,
            width=20)

        self.nameLabel.pack(side=LEFT)
        self.commandName.pack(side=RIGHT)
        self.nameFrame.pack(side=TOP)

        # Frame that till hold the two buttons cancel / create
        self.buttonFrame = Frame(
            self.addSequenceWindow,
            borderwidth=1,
            background="#000",
            relief=FLAT,
            width=300,
            height=200)
        self.buttonFrame.pack(side=BOTTOM)

        self.createButton = Button(
            self.buttonFrame,
            text="Create Sequence",
            width=8,
            command=self.addSequence,
            padx=10)
        self.selectScriptButton = Button(
            self.buttonFrame,
            text="Select Script",
            width=8,
            command=self.selectSequence,
            padx=10)
        self.cancelButton = Button(
            self.buttonFrame,
            text="Cancel",
            width=5,
            command=self.closeNewSequenceWindow,
            padx=10)

        self.createButton.pack(side=LEFT)
        self.selectScriptButton.pack(side=LEFT)
        self.cancelButton.pack(side=RIGHT)

        # Makes the new window open over the current editor window
        

        self.addSequenceWindow.geometry(
            '%dx%d+%d+%d' %
            (NEWTILEWINDOW_W,
             NEWTILEWINDOW_H,
             self.root.winfo_x() +
             self.root.winfo_width() /
             2 -
             NEWTILEWINDOW_W /
             2,
             self.root.winfo_y() +
             self.root.winfo_height() /
             2 -
             NEWTILEWINDOW_H /
             2))

    def Zoom(self, x):
        global TILESIZE

        if TILESIZE > 5 and x < 0:
            TILESIZE = TILESIZE + x
            self.w.config(
                width=self.board.Cols *
                TILESIZE,
                height=self.board.Rows *
                TILESIZE,
                scrollregion=(
                    0,
                    0,
                    TT.BOARDWIDTH *
                    TILESIZE,
                    TT.BOARDHEIGHT *
                    TILESIZE))
            self.w.pack()
            self.callCanvasRedraw()
        elif TILESIZE < 35 and x > 0:
            TILESIZE = TILESIZE + x
            self.w.config(
                width=self.board.Cols *
                TILESIZE,
                height=self.board.Rows *
                TILESIZE,
                scrollregion=(
                    0,
                    0,
                    TT.BOARDWIDTH *
                    TILESIZE,
                    TT.BOARDHEIGHT *
                    TILESIZE))
            self.w.pack()
            self.callCanvasRedraw()

    def SaveStates(self):
        global RECORDING
        global SCRIPTSEQUENCE
        if len(self.stateTmpSaves) == self.maxStates:
            if(self.CurrentState == self.maxStates - 1):
                self.stateTmpSaves.pop(0)
                self.stateTmpSaves.append(
                    copy.deepcopy(self.board.Polyominoes))
                self.CurrentState = self.maxStates - 1
            else:
                print("Removing some states 1")
                self.ApplyUndo()

                self.stateTmpSaves.append(
                    copy.deepcopy(self.board.Polyominoes))
                self.CurrentState = self.CurrentState + 1
        else:
            if(self.CurrentState == len(self.stateTmpSaves) - 1):

                self.stateTmpSaves.append(
                    copy.deepcopy(self.board.Polyominoes))
                self.CurrentState = self.CurrentState + 1

            else:
                print("Removing some states 2")
                self.ApplyUndo()

                self.stateTmpSaves.append(
                    copy.deepcopy(self.board.Polyominoes))
                self.CurrentState = self.CurrentState + 1

    def ApplyUndo(self):
        global RECORDING
        global SCRIPTSEQUENCE
        print("Applying Undo")
        for x in range(0, len(self.stateTmpSaves) - self.CurrentState - 1):
            print("x :", x)
            self.stateTmpSaves.pop()
            if RECORDING:
                SCRIPTSEQUENCE = SCRIPTSEQUENCE[:-1]

    def Undo(self):

        if self.CurrentState == 0:
            pass
        else:

            self.CurrentState = self.CurrentState - 1
            print("Current is, ", self.CurrentState, "after")
            #deleteTumbleTiles(self.board, self.board.Cols, self.board.Rows, self.w, TILESIZE, self.textcolor, self.gridcolor, self.tkDRAWGRID.get(), self.tkSHOWLOC.get())
            self.board.Polyominoes = copy.deepcopy(
                self.stateTmpSaves[self.CurrentState])
            print("undo - ", self.CurrentState)
            self.callCanvasRedrawTumbleTiles()

    def Redo(self):

        if self.CurrentState == self.maxStates - \
                1 or self.CurrentState == len(self.stateTmpSaves) - 1:
            pass

        else:
            self.CurrentState = self.CurrentState + 1
            print("redo", self.CurrentState)
            self.board.Polyominoes = copy.deepcopy(
                self.stateTmpSaves[self.CurrentState])
            self.callCanvasRedrawTumbleTiles()

    # Tumbles the board in a direction, then redraws the Canvas
    def MoveDirection(self, direction, redraw=True):
        global RECORDING
        global SCRIPTSEQUENCE

    # try:

        # board.GridDraw()
        # normal
        if direction != "" and self.tkSTEPVAR.get(
        ) == False and self.tkGLUESTEP.get() == False:

            self.board.Tumble(direction)
            self.Log("T" + direction + ", ")

        # normal with glues
        elif direction != "" and self.tkSTEPVAR.get() == False and self.tkGLUESTEP.get() == True:

            self.board.TumbleGlue(direction)
            self.Log("TG" + direction + ", ")

        # single step
        elif direction != "" and self.tkSTEPVAR.get():

            s = True
            s = self.board.Step(direction)
            if self.tkGLUESTEP.get():
                self.board.ActivateGlues()
                self.Log("SG" + direction + ", ")
            else:
                self.Log("S" + direction + ", ")
            if s == False and self.tkGLUESTEP.get() == False:
                self.board.ActivateGlues()
                self.Log("G, ")
        self.SaveStates()
        if RECORDING:
            SCRIPTSEQUENCE = SCRIPTSEQUENCE + direction

        if redraw:    
            self.callCanvasRedrawTumbleTiles()

    # except Exception as e:
     #   print e
      #  print sys.exc_info()[0]
        # pass

    # Uses pyscreenshot to save an image of the canvas

    def picture(self):


        drawPILImage(
            self.board,
            self.board.Cols,
            self.board.Rows,
            self.w,
            TILESIZE,
            self.textcolor,
            self.gridcolor,
            self.tkDRAWGRID.get(),
            self.tkSHOWLOC.get())


    def openVideoExportWindow(self):
        videoExport = VideoExport(self.root, self)



    # Opens the GUI file browser
    def loadFile(self):
        global LASTLOADEDFILE
        filename = getFile(FileType.XML)
        LASTLOADEDFILE = filename
        self.loadTileSet(filename)
        # TODO: Replace hardcoded / with os file separator. Issue is at the getFile() level.

    # Will reload the last loaded file to enable quick testing
    def reloadFile(self):
        global LASTLOADEDFILE
        self.loadTileSet(LASTLOADEDFILE)

    # Gets the board data, preview tile data, and glue data from getFile.py, modifies all thses
    # accordingly, then redraws the canvas
    def loadTileSet(self, filename):

        if filename == "":
            return

        #self.Log("\nLoad "+filename+"\n")
        data = parseFile(filename)

        del self.board

        TT.GLUEFUNC = {}

        self.board = data[0]
        TT.BOARDHEIGHT = self.board.Rows
        TT.BOARDWIDTH = self.board.Cols

        self.resizeBoardAndCanvas()
        self.callCanvasRedraw()

        # Glue Function
        for label in data[1]:
            TT.GLUEFUNC[label] = int(data[1][label])
            self.glueFunc[label] = TT.GLUEFUNC[label]

        self.prevTileList = data[2]

        # Call the board editor
        self.board.relistPolyominoes()
        #self.openBoardEditDial(self.root, self.board, data[1], self.prevTileList)
        self.CurrentState = -1
        self.stateTmpSaves = []
        self.SaveStates()
        # self.board.SetGrid()

        self.listOfCommands = data[3]
        self.popWinSequences()
        self.callCanvasRedraw()

        self.root.title(LASTLOADEDFILE.split('/')[-1])

    def callCanvasRedraw(self):
        global TILESIZE
        redrawCanvas(
            self.board,
            self.board.Cols,
            self.board.Rows,
            self.w,
            TILESIZE,
            self.textcolor,
            self.gridcolor,
            self.tkDRAWGRID.get(),
            self.tkSHOWLOC.get())

    def callCanvasRedrawTumbleTiles(self):
        global TILESIZE
        redrawTumbleTiles(
            self.board,
            self.board.Cols,
            self.board.Rows,
            self.w,
            TILESIZE,
            self.textcolor,
            self.gridcolor,
            self.tkDRAWGRID.get(),
            self.tkSHOWLOC.get())

    def callGridDraw(self):
        global TILESIZE
        drawGrid(
            self.board,
            TT.BOARDWIDTH,
            TT.BOARDHEIGHT,
            self.w,
            TILESIZE,
            self.gridcolor,
            self.tkDRAWGRID.get(),
            self.tkSHOWLOC.get())

    def about(self):
        global VERSION
        MsgAbout(self.root)
        #tkMessageBox.showinfo("About", "    Tumble Tiles v"+VERSION+"\n         Tim Wylie\n\n  For support contact schwellerr@gmail.com")

    def changecanvas(self):
        try:
            result = tkinter.colorchooser.askcolor(title="Background Color")
            if result[0] is not None:
                self.w.config(background=result[1])
        except BaseException:
            pass

    def changegridcolor(self):
        try:
            result = tkinter.colorchooser.askcolor(title="Grid Color")
            if result[0] is not None:
                self.gridcolor = result[1]
                self.callCanvasRedraw()
        except BaseException:
            pass

    def openBoardEditDial(self, root, board, gluedata, prevTiles):
        TGBox = TE.TileEditorGUI(root, self, board, gluedata, prevTiles)

    # Opens the editor and loads the cuurent tiles from the simulator
    def editCurrentTiles(self):
        global TILESIZE
        self.glueFunc = TT.GLUEFUNC
        TE.TILESIZE = TILESIZE
        TGBox = TE.TileEditorGUI(
            self.root,
            self,
            self.board,
            self.glueFunc,
            self.prevTileList)

    # Turns the list of polyominoes and concrete tiles into a list of tiles including their position
    # this is used to get the tile list that will be paseed to the editor
    def getTileDataFromBoard(self):
        new_tile_data = []

        for p in self.board.Polyominoes:
            for t in p.Tiles:

                ntile = {}
                ntile["label"] = t.symbol
                ntile["location"] = {}
                ntile["location"]["x"] = t.x
                ntile["location"]["y"] = t.y
                ntile["northGlue"] = t.glues[0]
                ntile["eastGlue"] = t.glues[1]
                ntile["southGlue"] = t.glues[2]
                ntile["westGlue"] = t.glues[3]
                ntile["color"] = t.color
                ntile["concrete"] = "False"

                new_tile_data.append(ntile)

        for c in self.board.ConcreteTiles:

            ntile = {}
            ntile["label"] = c.symbol
            ntile["location"] = {}
            ntile["location"]["x"] = c.x
            ntile["location"]["y"] = c.y
            ntile["northGlue"] = 0
            ntile["eastGlue"] = 0
            ntile["southGlue"] = 0
            ntile["westGlue"] = 0
            ntile["color"] = c.color
            ntile["concrete"] = "True"

            new_tile_data.append(ntile)

        return new_tile_data

    # This method will be called wben you want to export the tiles from the
    # editor back to the simulation
    def setTilesFromEditor(self, board, glueFunc, prev_tiles, width, height):
        TT.BOARDHEIGHT = board.Rows
        TT.BOARDWIDTH = board.Cols
        self.board = board
        self.glueFunc = glueFunc
        TT.GLUEFUNC = self.glueFunc
        self.prevTileList = prev_tiles
        self.board.relistPolyominoes()
        self.resizeBoardAndCanvas()
        self.CurrentState = 0
        self.stateTmpSaves = []
        self.SaveStates()
        self.callCanvasRedraw()

    def parseFile2(self, filename):
        tree = ET.parse(filename)
        treeroot = tree.getroot()

        # default size of board, changes if new board size data is read from
        # the file
        rows = 15
        columns = 15

        boardSizeExits = False
        previewTilesExist = False
        tileDataExists = False

        if tree.find("PreviewTiles") is not None:
            previewTilesExist = True

        if tree.find("BoardSize") is not None:
            boardSizeExists = True

        if tree.find("TileData") is not None:
            tileDataExists = True

        #data = {"size": [],"tileData": []}
        data = {"size": [], "tileData": []}

        if boardSizeExists:
            rows = treeroot[0].attrib["height"]
            columns = treeroot[0].attrib["width"]

        geomerty = [rows, columns]
        #geomerty["rows"] = rows
        #geomerty["columns"] = columns
        data["size"].append(geomerty)
        # if isinstance(geomerty, dict):
        #    print "geomeryu"
        # if isinstance(data["size"], dict):
        #    print "data"

        if tileDataExists:
            tileDataTree = treeroot[3]
            for tile in tileDataTree:
                newTile = {}

                newTile["location"] = {'x': 0, 'y': 0}
                newTile["color"] = "#555555"

                if tile.find('Location') is not None:
                    newTile["location"]["x"] = int(
                        tile.find('Location').attrib['x'])
                    newTile["location"]["y"] = int(
                        tile.find('Location').attrib['y'])

                if tile.find('Color') is not None:
                    if tile.find('Concrete').text == "True":
                        newTile["color"] = "#686868"
                    else:
                        newTile["color"] = "#" + tile.find('Color').text

                data["tileData"].append(newTile)
        return data

    def data2SVG(self, data, filename, gridlines=False):
        # the width of one square
        scale = 10

        f = open(filename, 'w')
        w = scale * int(data["size"][0][0])
        h = scale * int(data["size"][0][1])
        f.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.1" baseProfile="full" width="' +
                str(w + 2) + '" height="' + str(h + 2) + '">\n')

        # tile the svg with transparant sqares for gridlines
        if gridlines:
            for x in range(w / scale):
                for y in range(h / scale):
                    c = "#ffffff"
                    line = '<rect x="' + str(x * scale + 1) + '" y="' + str(y * scale + 1) + '" width="' + str(scale) + '" height="' + str(
                        scale) + '" fill="' + str(c) + '" stroke="black" stroke-width="0.5" fill-opacity="0" />\n'
                    f.write(line)

        # place tiles of file where appropriate
        for tile in data["tileData"]:
            x = scale * int(tile["location"]["x"])
            y = scale * int(tile["location"]["y"])
            c = tile["color"]
            line = '<rect x="' + str(x + 1) + '" y="' + str(y + 1) + '" width="' + str(
                scale) + '" height="' + str(scale) + '" fill="' + str(c) + '" stroke="black" stroke-width="0.5" />\n'
            f.write(line)

        f.write("</svg>")
        f.close()

    def createSvg(self):
        filename = tkinter.filedialog.asksaveasfilename(confirmoverwrite=True, defaultextension=".svg", filetypes=[("Scalable Vector Graphics", ".svg")])
        if not filename: return
        if not '.' in filename:
            filename += ".svg"

        tile_config = ET.Element("TileConfiguration")
        board_size = ET.SubElement(tile_config, "BoardSize")
        glue_func = ET.SubElement(tile_config, "GlueFunction")

        board_size.set("width", str(self.board.Cols))
        board_size.set("height", str(self.board.Rows))

        # Add all preview tiles to the .xml file if there are any
        p_tiles = ET.SubElement(tile_config, "PreviewTiles")
        if len(self.prevTileList) != 0:
            for td in self.prevTileList:
                print((td.color))
                if td.glues == [] or len(td.glues) == 0:
                    td.glues = [0, 0, 0, 0]

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
                print(tile)
                if tile.glues is None or len(tile.glues) == 0:
                    tile.glues = [0, 0, 0, 0]

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

            print(conc)
            if conc.glues is None or len(conc.glues) == 0:
                conc.glues = [0, 0, 0, 0]

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

        #print tile_config
        mydata = ET.tostring(tile_config)
        file = open("tt2svg/tmp.xml", "wb")
        file.write(mydata)
        file.close()
        
        self.data2SVG(self.parseFile2("tt2svg/tmp.xml"), filename)

    def newBoard(self):
        del self.board.Polyominoes[:]
        self.board.LookUp = {}
        self.root.title("New Board")

        self.board = TT.Board(TT.BOARDHEIGHT, TT.BOARDWIDTH)
        bh = TT.BOARDHEIGHT
        bw = TT.BOARDWIDTH
        TT.GLUEFUNC = {
            'N': 1,
            'E': 1,
            'S': 1,
            'W': 1,
            'A': 1,
            'B': 1,
            'C': 1,
            'D': 1,
            'X': 1,
            'Y': 1,
            'Z': 1}
        self.CurrentState = -1
        self.stateTmpSaves = []
        self.SaveStates()
        self.callCanvasRedraw()

    # Creates the initial configuration that shows then you open the gui
    def CreateInitial(self):

        self.Log("\nLoad initial\n")
        # flush board
        del self.board.Polyominoes[:]
        self.board.LookUp = {}

        self.board = TT.Board(TT.BOARDHEIGHT, TT.BOARDWIDTH)
        bh = TT.BOARDHEIGHT
        bw = TT.BOARDWIDTH
        TT.GLUEFUNC = {
            'N': 1,
            'E': 1,
            'S': 1,
            'W': 1,
            'A': 1,
            'B': 1,
            'C': 1,
            'D': 1,
            'X': 1,
            'Y': 1,
            'Z': 1}
        # initial
        # CreateTiles(board)
        colorb = "#000"
        colorl = "#fff"
        colorg = "#686868"
        NumTiles = 10
        for i in range(NumTiles):
            # bottom tiles
            #colorb = str(colorb[0]+chr(ord(colorb[1])+1)+colorb[2:])
            colorb = "#" + str(hex(random.randint(0,
                                                  16))[2:]) + str(hex(random.randint(0,
                                                                                     16))[2:]) + str(hex(random.randint(0,
                                                                                                                        16))[2:])
            if len(colorb) > 4:
                colorb = colorb[:4]

            p = TT.Polyomino(self.board.poly_id_c,
                             bh - i - 2,
                             bh - 1,
                             ['N',
                              'E',
                              'S',
                              'W',
                              'A',
                              'B',
                              'C',
                              'D',
                              'X',
                              'Y',
                              'Z'],
                             colorb)
            self.board.Add(p)
            # left tiles
            #colorl = str(colorl[0]+chr(ord(colorl[1])-1)+colorl[2:])
            colorl = "#" + str(hex(random.randint(0,
                                                  16))[2:]) + str(hex(random.randint(0,
                                                                                     16))[2:]) + str(hex(random.randint(0,
                                                                                                                        16))[2:])
            if len(colorl) > 4:
                colorl = colorl[:4]

            char = chr(ord('a') + i)
            p = TT.Polyomino(self.board.poly_id_c,
                             0,
                             bh - i - 2,
                             ['S',
                              'W',
                              'N',
                              'E',
                              'A',
                              'B',
                              'C',
                              'D',
                              'X',
                              'Y',
                              'Z'],
                             colorb)

            self.board.Add(p)

            # test add a concrete tile

        self.board.AddConc(TT.Tile(None, -1, 5, 13, [], colorg, True))
        self.board.AddConc(TT.Tile(None, -1, 10, 1, [], colorg, True))
        self.board.AddConc(TT.Tile(None, -1, 8, 8, [], colorg, True))
        self.board.AddConc(TT.Tile(None, -1, 1, 10, [], colorg, True))
        self.board.AddConc(TT.Tile(None, -1, 13, 5, [], colorg, True))
        self.CurrentState = -1
        self.stateTmpSaves = []
        self.SaveStates()
        # self.board.SetGrid()
        self.callCanvasRedraw()

    def EnableLogging(self):
        global LOGFILE
        global LOGFILENAME
        try:
            if self.tkLOG.get():
                LOGFILENAME = self.tkFileDialog.asksaveasfilename(
                    initialdir="./",
                    title="Select file",
                    filetypes=(
                        ("text files",
                         "*.txt"),
                        ("all files",
                         "*.*")))
                if LOGFILENAME != '':
                    LOGFILE = open(LOGFILENAME, 'a')
                    LOGFILE.write("Tumble Tiles Log\n")
                    LOGFILE.close()
                else:
                    self.tkLOG.set(False)
            else:
                if not LOGFILE.closed:
                    LOGFILE.close()
        except Exception as e:
            print("Could not log")
            print(e)

    def Log(self, stlog):
        global LOGFILE
        global LOGFILENAME
        if self.tkLOG.get():
            LOGFILE = open(LOGFILENAME, 'a')
            LOGFILE.write(stlog)
            LOGFILE.close()

    def drawgrid(self):
        global TILESIZE

        if self.tkDRAWGRID.get():
            for row in range(self.board.Rows):
                self.w.create_line(
                    0,
                    row * TILESIZE,
                    TT.BOARDWIDTH * TILESIZE,
                    row * TILESIZE,
                    fill=self.gridcolor,
                    width=.50)
            for col in range(self.board.Cols):
                self.w.create_line(
                    col * TILESIZE,
                    0,
                    col * TILESIZE,
                    TT.BOARDHEIGHT * TILESIZE,
                    fill=self.gridcolor,
                    width=.50)

        if self.tkSHOWLOC.get():
            for row in range(TT.BOARDHEIGHT):
                for col in range(TT.BOARDWIDTH):
                    self.w.create_text(TILESIZE *
                                       (col +
                                        1) -
                                       TILESIZE /
                                       2, TILESIZE *
                                       (row +
                                        1) -
                                       TILESIZE /
                                       2, text="(" +
                                       str(row) +
                                       "," +
                                       str(col) +
                                       ")", fill=self.gridcolor, font=('', TILESIZE /
                                                                       5))


if __name__ == "__main__":

    random.seed()
    root = Tk()
    root.title("Tumble Tiles")
    # sets the icon
    #sp = os.path.realpath(__file__)
    sp = os.path.dirname(sys.argv[0])
    imgicon = PhotoImage(file=os.path.join(sp, 'tumble.gif'))
    root.tk.call('wm', 'iconphoto', root._w, imgicon)
    # root.iconbitmap(r'favicon.ico')
    # root.geometry('300x300')
    mainwin = tumblegui(root)

    # TODO: For threading and mutexes: https://stackoverflow.com/a/54374873
    mainloop()
