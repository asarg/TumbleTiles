#GUI for Tumble Tiles
#Tim Wylie
#2018


import copy
from Tkinter import *
import tkFileDialog, tkMessageBox, tkColorChooser
import xml.etree.ElementTree as ET
import random
import time
import tumbletiles as TT
import os,sys
#https://pypi.python.org/pypi/pyscreenshot

try:
    PYSCREEN = False
    #imp.find_module('pyscreenshot')
    import pyscreenshot as ImageGrab
    PYSCREEN = True
except ImportError:
    PYSCREEN = False

LOGFILE = None
LOGFILENAME = ""
TILESIZE = 35
VERSION = "1.4"

class MsgAbout:
    def __init__(self,  parent):
        global VERSION
        self.parent = parent
        self.t = Toplevel(self.parent)
        self.t.resizable(False, False)
        self.t.wm_title("About")
        #self.t.geometry('200x200') #WxH

        self.photo = PhotoImage(file="tumble.gif")
        
        #Return a new PhotoImage based on the same image as this widget but use only every Xth or Yth pixel.
        self.display = self.photo.subsample(3,3)
        self.label = Label(self.t, image=self.display, width=90, height=80)
        self.label.image = self.display # keep a reference!
        self.label.pack()
        
        self.l1 = Label(self.t, text="Tumble Tiles v"+VERSION, font=('',15)).pack()
        Label(self.t,text="Tim Wylie").pack()
        Label(self.t,text="For support contact schwellerr@gmail.com").pack()
        
        Button(self.t,text="OK", width=10, command=self.t.destroy).pack()
    
        self.t.focus_set()
        ## Make sure events only go to our dialog
        self.t.grab_set()
        ## Make sure dialog stays on top of its parent window (if needed)
        self.t.transient(self.parent)
        ## Display the window and wait for it to close
        self.t.wait_window(self.t)
        
        
        
class Settings:
    def __init__(self,  parent, logging):#, fun):
        global TILESIZE
        
        self.logging = logging
        #self.function = fun
        self.parent = parent
        self.t = Toplevel(self.parent)
        self.t.resizable(False, False)
        #self.wm_attributes("-disabled", True)
        self.t.wm_title("Board Options")
        #self.toplevel_dialog.transient(self)
        self.t.geometry('180x180') #WxH
        
        self.tkTILESIZE = StringVar()
        self.tkTILESIZE.set(str(TILESIZE))
        self.tkBOARDWIDTH = StringVar()
        self.tkBOARDWIDTH.set(str(TT.BOARDWIDTH))
        self.tkBOARDHEIGHT = StringVar()
        self.tkBOARDHEIGHT.set(str(TT.BOARDHEIGHT))
        self.tkTEMP = StringVar()
        self.tkTEMP.set(str(TT.TEMP))
        
        #tilesize
        self.l1 = Label(self.t, text="Tile Size").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.tilesize_sbx = Spinbox(self.t, from_=10, to=100, width=5, increment=5, textvariable=self.tkTILESIZE).grid(row=0, column=1, padx=5, pady=5)
        #board width
        self.l2 = Label(self.t, text="Board Width").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.boardwidth_sbx = Spinbox(self.t, from_=10, to=100, width=5,  textvariable=self.tkBOARDWIDTH).grid(row=1, column=1, padx=5, pady=5)
        #board height
        self.l3 = Label(self.t, text="Board Height").grid(row=2, column=0,  padx=5, pady=5, sticky=W)
        self.boardheight_sbx = Spinbox(self.t, from_=10, to=100, width=5, textvariable=self.tkBOARDHEIGHT).grid(row=2, column=1,  padx=5, pady=5)
        #temperature
        self.l4 = Label(self.t, text="Temperature").grid(row=3, column=0,  padx=5, pady=5, sticky=W)
        self.temperature_sbx = Spinbox(self.t, from_=1, to=10, width=5, textvariable=self.tkTEMP).grid(row=3, column=1,  padx=5, pady=5)
        #buttons
        Button(self.t,text="Cancel", command=self.t.destroy).grid(row=4, column=0, padx=5, pady=5)
        Button(self.t,text="Apply", command=self.Apply).grid(row=4, column=1, padx=5, pady=5)
    
        self.t.focus_set()
        ## Make sure events only go to our dialog
        self.t.grab_set()
        ## Make sure dialog stays on top of its parent window (if needed)
        self.t.transient(self.parent)
        ## Display the window and wait for it to close
        self.t.wait_window(self.t)

    def Apply(self):
        global TILESIZE
        
        TILESIZE = int(self.tkTILESIZE.get())
        if TT.BOARDWIDTH != int(self.tkBOARDWIDTH.get()):
            self.Log("\nChange BOARDWIDTH from "+str(TT.BOARDWIDTH)+" to "+self.tkBOARDWIDTH.get())
            TT.BOARDWIDTH = int(self.tkBOARDWIDTH.get())
        if TT.BOARDHEIGHT != int(self.tkBOARDHEIGHT.get()):
            self.Log("\nChange BOARDHEIGHT from "+str(TT.BOARDHEIGHT)+" to "+self.tkBOARDHEIGHT.get())
            TT.BOARDHEIGHT = int(self.tkBOARDHEIGHT.get())
        if TT.TEMP != int(self.tkTEMP.get()):
            self.Log("\nChange TEMP from "+str(TT.TEMP)+" to "+self.tkTEMP.get())
            TT.TEMP = int(self.tkTEMP.get())
        #self.function() #.RedrawCanvas()
        self.t.destroy()
        
        
    def Log(self, stlog):
        global LOGFILE
        global LOGFILENAME
        
        if self.logging == True:
            LOGFILE = open(LOGFILENAME,'a')
            LOGFILE.write(stlog)
            LOGFILE.close()




################################################################
class tumblegui:
    def __init__(self, root):
        global TILESIZE
        
        self.board = TT.Board(TT.BOARDHEIGHT, TT.BOARDWIDTH)
        self.root = root
        self.root.resizable(False, False)
        self.mainframe = Frame(self.root, bd=0, relief=FLAT)
        
        #main canvas to draw on
        self.w = Canvas(self.mainframe, width=TT.BOARDWIDTH*TILESIZE, height=TT.BOARDHEIGHT*TILESIZE)
        #mouse
        self.w.bind("<Button-1>", self.callback)
        #arrow keys
        self.root.bind("<Up>", self.key)
        self.root.bind("<Right>", self.key)
        self.root.bind("<Down>", self.key)
        self.root.bind("<Left>", self.key)
        self.w.pack() 
        
        #menu
        #menu - https://www.tutorialspoint.com/python/tk_menu.htm
        self.menubar = Menu(self.root, relief=FLAT)
        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Example", command=self.CreateInitial)
        filemenu.add_command(label="Load", command=self.getfile)
        
        self.tkLOG = BooleanVar()
        self.tkLOG.set(False)
        filemenu.add_checkbutton(label="Log Actions",onvalue=True, offvalue=False, variable=self.tkLOG,command=self.EnableLogging)
        
        if PYSCREEN == True:
            filemenu.add_command(label="Picture", command=self.picture)
        else:
            filemenu.add_command(label="Picture", command=self.picture, state=DISABLED)
            
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        
        aboutmenu = Menu(self.menubar, tearoff=0)
        aboutmenu.add_command(label="About", command=self.about)
        
        self.tkSTEPVAR = BooleanVar()
        self.tkSTEPVAR.set(False)
        self.tkGLUESTEP = BooleanVar()
        self.tkGLUESTEP.set(False)
        
        self.tkDRAWGRID = BooleanVar()
        self.tkDRAWGRID.set(False)
        self.tkSHOWLOC = BooleanVar()
        self.tkSHOWLOC.set(False)
        
        settingsmenu = Menu(self.menubar, tearoff=0)
        settingsmenu.add_checkbutton(label="Single Step", onvalue=True, offvalue=False, variable=self.tkSTEPVAR) #,command=stepmodel)
        settingsmenu.add_checkbutton(label="Glue on Step", onvalue=True, offvalue=False, variable=self.tkGLUESTEP) #,state=DISABLED)
        settingsmenu.add_separator()
        settingsmenu.add_command(label="Background Color", command=self.changecanvas)
        settingsmenu.add_checkbutton(label="Show Grid", onvalue=True, offvalue=False, variable=self.tkDRAWGRID, command=self.RedrawCanvas)
        settingsmenu.add_command(label="Grid Color", command=self.changegridcolor)
        settingsmenu.add_checkbutton(label="Show Locations", onvalue=True, offvalue=False, variable=self.tkSHOWLOC, command=self.RedrawCanvas)
        settingsmenu.add_separator()
        settingsmenu.add_command(label="Board Options", command=self.changetile)
        
        
        self.menubar.add_cascade(label="File", menu=filemenu)
        self.menubar.add_cascade(label="Settings", menu=settingsmenu)
        self.menubar.add_cascade(label="Help", menu=aboutmenu)
        self.root.config(menu=self.menubar)
        
        #toolbar
        #http://zetcode.com/gui/tkinter/menustoolbars/
        self.toolbar = Frame(self.mainframe, bd=0, relief=FLAT, height=10)
        lab1 = Label(self.toolbar, text="Width:", justify=RIGHT).pack(side=LEFT)
        self.tkWidthText = StringVar()
        self.tkWidthText.set(TT.BOARDWIDTH)
        bgcol = self.toolbar['bg']#._root().cget('bg')
        Label(self.toolbar, textvariable=self.tkWidthText, width=3, padx=0, justify=LEFT, relief=FLAT).pack(side=LEFT)
        
        Label(self.toolbar, text="          Height:", justify=RIGHT).pack(side=LEFT)
        self.tkHeightText = StringVar()
        self.tkHeightText.set(TT.BOARDHEIGHT)
        Label(self.toolbar, textvariable=self.tkHeightText, width=3, padx=0, justify=LEFT, relief=FLAT).pack(side=LEFT)
        
        Label(self.toolbar, text="          Temp:", justify=RIGHT).pack(side=LEFT)
        self.tkTempText = StringVar()
        self.tkTempText.set(TT.TEMP)
        Label(self.toolbar, textvariable=self.tkTempText, width=3, padx=0, justify=LEFT, relief=FLAT).pack(side=LEFT)
        
        self.toolbar.pack(side=TOP, fill=X)
        
        self.mainframe.pack()
        

        
        #other class variables
        self.gridcolor = "#000000"
        self.textcolor = "#000000"
        
        self.drawgrid()
        self.CreateInitial()
    
    def changetile(self):
        global TILESIZE
        
        Sbox = Settings(self.root, self.tkLOG.get())
        #expand grid
        self.board.ResizeGrid(TT.BOARDHEIGHT,  TT.BOARDWIDTH)
        #resize canvas
        self.w.config(width=TT.BOARDWIDTH*TILESIZE, height=TT.BOARDHEIGHT*TILESIZE)
        self.tkWidthText.set(TT.BOARDWIDTH)
        self.tkHeightText.set(TT.BOARDHEIGHT)
        self.tkTempText.set(TT.TEMP)
        #resize window #wxh
        toolbarframeheight = 24
        self.root.geometry(str(TT.BOARDWIDTH*TILESIZE)+'x'+str(TT.BOARDHEIGHT*TILESIZE+toolbarframeheight))
        #redraw
        self.RedrawCanvas()
    
    def key(self, event):
        if event.keysym == "Up":
            self.MoveDirection("N")
        elif event.keysym == "Right":
            self.MoveDirection("E")
        elif event.keysym == "Down":
            self.MoveDirection("S")
        elif event.keysym == "Left":
            self.MoveDirection("W")
        
    def callback(self, event):
        global TILESIZE
        
        try:
            #print "clicked at", event.x, event.y
            if event.y <= 2*TILESIZE and event.x > 2*TILESIZE and event.x < TT.BOARDWIDTH*TILESIZE-2*TILESIZE:
                self.MoveDirection("N")
            elif event.y >= TT.BOARDHEIGHT*TILESIZE-2*TILESIZE and event.x > 2*TILESIZE and event.x < TT.BOARDWIDTH*TILESIZE-2*TILESIZE:
                self.MoveDirection("S")
            elif event.x >= TT.BOARDWIDTH*TILESIZE-2*TILESIZE and event.y > 2*TILESIZE and event.y < TT.BOARDHEIGHT*TILESIZE-2*TILESIZE:
                self.MoveDirection("E")
            elif event.x <= 2*TILESIZE and event.y > 2*TILESIZE and event.y < TT.BOARDHEIGHT*TILESIZE-2*TILESIZE:
                self.MoveDirection("W")
                
        except:
            pass
                
    def MoveDirection(self, direction):
        try:            
            #board.GridDraw()
            #normal
            if direction != "" and self.tkSTEPVAR.get() == False and self.tkGLUESTEP.get()==False:
                self.board.Tumble(direction)
                self.RedrawCanvas()
                self.Log("T"+direction+", ")
            #normal with glues 
            elif direction != "" and self.tkSTEPVAR.get() == False and self.tkGLUESTEP.get() == True:
                self.board.TumbleGlue(direction)
                self.RedrawCanvas()
                self.Log("TG"+direction+", ")
            #single step
            elif direction != "" and self.tkSTEPVAR.get() == True:
                s = True
                s = self.board.Step(direction)
                if self.tkGLUESTEP.get()==True:
                    self.board.ActivateGlues()
                    self.Log("SG"+direction+", ")
                else:
                    self.Log("S"+direction+", ")
                if s == False and self.tkGLUESTEP.get()==False:
                    self.board.ActivateGlues()
                    self.Log("G, ")
                self.RedrawCanvas()
        except Exception as e:
            print e
            print sys.exc_info()[0]
            #pass
    
    def picture(self):
        #https://stackoverflow.com/questions/41940945/saving-canvas-from-tkinter-to-file
        try:
            filename = self.tkFileDialog.asksaveasfilename(initialdir = "./",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
            if filename != '':
                time.sleep(1)
                px = self.w.winfo_rootx() + self.w.winfo_x()
                py = self.w.winfo_rooty() + self.w.winfo_y()
                boardx = px + self.w.winfo_width() 
                boardy = py + self.w.winfo_height()
                grabcanvas = ImageGrab.grab(bbox=(px,py,boardx,boardy)).save(filename)
        except Exception as e:
            print "Could not print for some reason"
            #print e
    
    def getfile(self):
        fname = tkFileDialog.askopenfilename()
        #print "doing stuff with "+fname
        try:
            tree = ET.parse(fname)
            treeroot = tree.getroot()
            self.Log("\nLoad "+fname+"\n")
            gluefun = treeroot[0]
            
            #flush board
            del self.board.Polyominoes[:]
            self.board.LookUp = {}
            TT.GLUEFUNC = {}
            self.board = TT.Board(TT.BOARDHEIGHT,  TT.BOARDWIDTH)
        
            for fun in gluefun:
                TT.GLUEFUNC[fun.find('Labels').attrib['L1']] = int(fun.find('Strength').text)
            
            for tt in treeroot[1:]:
                
                ntlocx = 0
                ntlocy = 0
                if tt[0].find('Location') != None:
                    ntlocx = int(tt[0].find('Location').attrib['x'])
                    ntlocy = int(tt[0].find('Location').attrib['y'])
                ntcol = "#555555"
                if tt[0].find('Color') != None:
                    ntcol = "#" + tt[0].find('Color').text
                ntnort = " "
                if tt[0].find('NorthGlue') != None:
                    ntnort = tt[0].find('NorthGlue').text
                nteast = " "
                if tt[0].find('EastGlue') != None:
                    nteast = tt[0].find('EastGlue').text
                ntsouth = " "
                if tt[0].find('SouthGlue') != None:
                    ntsouth = tt[0].find('SouthGlue').text
                ntwest = " "
                if tt[0].find('WestGlue') != None:
                    ntwest = tt[0].find('WestGlue').text
                ntlab = "X"
                if tt[0].find('label') != None:
                    ntlab = tt[0].find('label').text
                
                
                ntile = TT.Tile(ntlab, ntlocx, ntlocy,[ntnort,nteast,ntsouth,ntwest],ntcol)
                self.board.Add(TT.Polyomino(ntile))
                self.board.SetGrid()
                self.RedrawCanvas()
                #board.GridDraw()
            #print TT.GLUEFUNC
        except:
            print "Problem with file: " + fname
            print sys.exc_info()[0]
            
    def RedrawCanvas(self):
        global TILESIZE
        
        self.w.delete(ALL)
        self.board.SetGrid()
        self.drawgrid()
        for row in range(self.board.Rows): #self.Board:
            for col in range(self.board.Cols):#row:
                if self.board.Board[row][col] != ' ':
                    pin = self.board.LookUp[self.board.Board[row][col]]
                    color = self.board.Polyominoes[pin].Tiles[0].color
                    self.w.create_rectangle(TILESIZE*col, TILESIZE*row, TILESIZE*col + TILESIZE, TILESIZE*row + TILESIZE, fill=color)
                    textcolor = self.textcolor
                    for t in self.board.Polyominoes[pin].Tiles:
                        if t.x == col and t.y == row:
                            #north
                            self.w.create_text(TILESIZE*col + TILESIZE/2, TILESIZE*row + TILESIZE/5, text = t.glues[0], fill=self.textcolor, font=('',TILESIZE/5) )
                            #east
                            self.w.create_text(TILESIZE*col + TILESIZE - TILESIZE/5, TILESIZE*row + TILESIZE/2, text = t.glues[1], fill=self.textcolor, font=('',TILESIZE/5))
                            #south
                            self.w.create_text(TILESIZE*col + TILESIZE/2, TILESIZE*row + TILESIZE - TILESIZE/5, text = t.glues[2], fill=self.textcolor, font=('',TILESIZE/5) )
                            #west
                            self.w.create_text(TILESIZE*col + TILESIZE/5, TILESIZE*row + TILESIZE/2, text = t.glues[3], fill=self.textcolor, font=('',TILESIZE/5) )
                
        
    def about(self):
        global VERSION
        MsgAbout(self.root)
        #tkMessageBox.showinfo("About", "    Tumble Tiles v"+VERSION+"\n         Tim Wylie\n\n  For support contact schwellerr@gmail.com")
       
             
    def changecanvas(self):
        try:
            result = tkColorChooser.askcolor(title="Background Color")
            if result[0] != None:
                self.w.config(background=result[1])
        except:
            pass

    def changegridcolor(self):
        try:
            result = tkColorChooser.askcolor(title="Grid Color")
            if result[0] != None:
                self.gridcolor = result[1]
                self.RedrawCanvas()
        except:
            pass


    def CreateInitial(self):
        
        self.Log("\nLoad initial\n")
        #flush board
        del self.board.Polyominoes[:]
        self.board.LookUp = {}
        
        self.board = TT.Board(TT.BOARDHEIGHT,  TT.BOARDWIDTH)
        bh = TT.BOARDHEIGHT
        bw = TT.BOARDWIDTH
        TT.GLUEFUNC = {'N':1, 'E':1, 'S':1, 'W':1,}
        #initial
        #CreateTiles(board)
        colorb = "#000"
        colorl = "#fff"
        NumTiles = 10
        for i in range(NumTiles):
            #bottom tiles
            #colorb = str(colorb[0]+chr(ord(colorb[1])+1)+colorb[2:])
            colorb = "#"+ str(hex(random.randint(0,16))[2:]) + str(hex(random.randint(0,16))[2:]) + str(hex(random.randint(0,16))[2:])
            if len(colorb) > 4:
                colorb = colorb[:4]
            p = TT.Polyomino(TT.Tile(chr(ord('A')+i), 0, bh-i-2, ['N','E','S','W'],colorb))
            self.board.Add(p)
            #left tiles
            #colorl = str(colorl[0]+chr(ord(colorl[1])-1)+colorl[2:])
            colorl = "#"+ str(hex(random.randint(0,16))[2:]) + str(hex(random.randint(0,16))[2:]) + str(hex(random.randint(0,16))[2:]) 
            if len(colorl) > 4:
                colorl = colorl[:4]
            p = TT.Polyomino(TT.Tile(chr(ord('a')+i), i+1, bh-1, ['S','W','N','E'],colorl))
            self.board.Add(p)
        
        self.board.SetGrid()
        self.RedrawCanvas()

    def EnableLogging(self):
        global LOGFILE
        global LOGFILENAME
        try:
            if self.tkLOG.get() == True:
                LOGFILENAME = self.tkFileDialog.asksaveasfilename(initialdir = "./", title = "Select file",filetypes = (("text files","*.txt"),("all files","*.*")))
                if LOGFILENAME != '':
                    LOGFILE = open(LOGFILENAME,'a')
                    LOGFILE.write("Tumble Tiles Log\n")
                    LOGFILE.close()
                else:
                    self.tkLOG.set(False)
            else:
                if not LOGFILE.closed:
                    LOGFILE.close()
        except Exception as e:
            print "Could not log"
            print e
        
    def Log(self, stlog):
        global LOGFILE
        global LOGFILENAME
        if self.tkLOG.get() == True:
            LOGFILE = open(LOGFILENAME,'a')
            LOGFILE.write(stlog)
            LOGFILE.close()
            
    def drawgrid(self):
        global TILESIZE
        
        if self.tkDRAWGRID.get() == True:
            for row in range(self.board.Rows):
                self.w.create_line(0, row*TILESIZE, TT.BOARDWIDTH*TILESIZE, row*TILESIZE, fill=self.gridcolor, width=.50)
            for col in range(self.board.Cols):
                self.w.create_line(col*TILESIZE, 0, col*TILESIZE, TT.BOARDHEIGHT*TILESIZE, fill=self.gridcolor, width=.50)
                    
        if self.tkSHOWLOC.get() == True:
            for row in range(TT.BOARDHEIGHT):
                for col in range(TT.BOARDWIDTH):
                    self.w.create_text(TILESIZE*(col+1) - TILESIZE/2, TILESIZE*(row+1) - TILESIZE/2, text = "("+str(row)+","+str(col)+")", fill=self.gridcolor,font=('',TILESIZE/5))
        
    
if __name__ =="__main__":
        
    random.seed()
    root = Tk()
    root.title("Tumble Tiles")
    #sets the icon
    #sp = os.path.realpath(__file__)
    sp = os.path.dirname(sys.argv[0])
    imgicon = PhotoImage(file=os.path.join(sp,'tumble.gif'))
    root.tk.call('wm', 'iconphoto', root._w, imgicon)  
    #root.iconbitmap(r'favicon.ico')
    #root.geometry('300x300')
    mainwin = tumblegui(root)
    
    mainloop()
    
