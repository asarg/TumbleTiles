import copy
from Tkinter import *
from scrollableFrame import VerticalScrolledFrame
import tkFileDialog, tkMessageBox, tkColorChooser
import xml.etree.ElementTree as ET
import tumbletiles as TT
import tumblegui as TG
from boardgui import redrawCanvas, drawGrid
import random
import time
import os,sys

#the x and y coordinate that the preview tiles will begin to be drawn on
PREVTILESTARTX = 20
PREVTILESTARTY = 21
TILESIZE = 35
PREVTILESIZE = 70

NEWTILEWINDOW_W = 150
NEWTILEWINDOW_H = 180

class TileEditorGUI:
	def __init__(self, parent, tumbleGUI, board, glue_data, previewTileList):

		#open two windows
		#`w1` will be the tile editor
		#`w2` will be a tile config previewer


		self.parent = parent
		self.board = board
		self.board_w = board.Cols
		self.board_h = board.Rows

		#instance of tumbleGUI that created it so methods from that class can be called
		self.tumbleGUI = tumbleGUI

		#self.rows = self.board.Rows
		#self.columns = self.board.Cols
		self.tile_size = TILESIZE
		self.width = self.board_w * self.tile_size
		self.height = self.board_h * self.tile_size



		self.prevTileList = previewTileList

		self.selectedTileIndex = -1

		#States for the tile editor
		self.remove_state = False
		self.add_state = False

		#Variable to hold on to the specifications of the tile to add
		self.tile_to_add = None

		self.glue_label_list = []

		self.glue_data = glue_data

		#A two-dimensional array
		self.coord2tile = [[None for x in range(self.board_w)] for y in range(self.board_h)]

		#outline of a preview tile when it is selected
		self.outline = None

		#boolean for whether or not to randomize the color of a placed tile
		self.randomizeColor = False

		#the variable associated with the entry in the create new tile window
		self.newTileN = StringVar()
		self.newTileE = StringVar()
		self.newTileS = StringVar()
		self.newTileW = StringVar()
		self.concreteChecked = IntVar()

		#populate the array
		self.populateArray()


		#//////////////////
		#	Window Config
		#/////////////////
		self.newWindow = Toplevel(self.parent)
		self.newWindow.wm_title("Editor")
		self.newWindow.resizable(False, False)
		self.newWindow.protocol("WM_DELETE_WINDOW", lambda: self.closeGUI())

		#Add Menu Bar
		self.menuBar = Menu(self.newWindow, relief=RAISED, borderwidth=1)

		optionsMenu = Menu(self.menuBar, tearoff=0)
		optionsMenu.add_command(label="Export", command = lambda: self.exportTiles())
		optionsMenu.add_command(label="Resize Board", command = lambda: self.boardResizeDial())
		optionsMenu.add_command(label="Save Configuration", command = lambda: self.saveTileConfig())
		
		#add the options menu to the menu bar
		self.menuBar.add_cascade(label="Option", menu=optionsMenu)
		self.newWindow.config(menu=self.menuBar)
		
		#Create two frames, one to hold the board and the buttons, and one to hold the tiles to be placed
		self.tileEditorFrame = Frame(self.newWindow, width = self.width, height = self.height, relief=SUNKEN,borderwidth=1)
		self.tileEditorFrame.pack(side=RIGHT, expand=True)

		self.BoardFrame = Frame(self.newWindow, borderwidth=1,relief=FLAT, width = 500, height = 500)
		self.BoardFrame.pack(side=LEFT)
		

		#The button thats toggles randomizing the color of a placed tile
		self.randomColorButton = Button(self.tileEditorFrame, text="Random Color", width=10, command= self.randomColorToggle)
		self.randomColorButton.pack(side=TOP)

		#Button that will allow user to add a new preview tile
		self.addNewPrevTileButton = Button(self.tileEditorFrame, text="New Tile", width=10, command= self.addNewPrevTile)
		self.addNewPrevTileButton.pack(side=TOP)
		
		#Canvas that tile and grid is drawn on
		self.BoardCanvas = Canvas(self.BoardFrame, width = self.width, height = self.height)
		self.BoardCanvas.pack(side=TOP)

		#Used to tell when a tile is trying to be placed, will send the event to onBoardClick to determine the location
		self.BoardCanvas.bind("<Button-1>", lambda event: self.onBoardClick(event)) # -- LEFT CLICK
		self.BoardCanvas.bind("<Button-3>", lambda event: self.onBoardClick(event)) # -- RIGHT CLICK

		self.tilePrevCanvas = Canvas(self.tileEditorFrame, width = self.tile_size * 3, height = self.height)
		self.tilePrevCanvas.pack(side=BOTTOM)


		#draw the board on the canvas
		self.popWinTiles()
		self.redrawPrev()

	# Called when you click to add a new tile. Will create a small window where you can insert the 4 glues, then add that tile to the
	# preview tile window
	def addNewPrevTile(self):
		self.addTileWindow = Toplevel(self.newWindow)



		self.addTileWindow.wm_title("Create Tile")
		self.addTileWindow.resizable(False, False)
		self.addTileWindow.protocol("WM_DELETE_WINDOW", lambda: self.closeNewTileWindow())

		#Frame that will hold the text boxes that the glues will be entered it
		self.tileFrame = Frame(self.addTileWindow, borderwidth=1, relief=FLAT, width = self.tile_size * 4, height = NEWTILEWINDOW_H - 40)
		self.tileFrame.pack(side=TOP)



		#Labels and entrys that user will enter the new glue configuration into
		self.glueN = Entry(self.tileFrame, textvariable= self.newTileN)
		self.glueE = Entry(self.tileFrame, textvariable= self.newTileE)
		self.glueS = Entry(self.tileFrame, textvariable= self.newTileS)
		self.glueW = Entry(self.tileFrame, textvariable= self.newTileW)
		self.concreteCheck = Checkbutton(self.tileFrame, text="Concrete", variable= self.concreteChecked)

		self.labelN = Label(self.tileFrame, text="N:")
		self.labelE = Label(self.tileFrame, text="E:")
		self.labelS = Label(self.tileFrame, text="S:")
		self.labelW = Label(self.tileFrame, text="W:")

		self.labelN.place(x = 40, y = 20)
		self.labelE.place(x = 40, y = 40)
		self.labelS.place(x = 40, y = 60)
		self.labelW.place(x = 40, y = 80)
		self.concreteCheck.place(x = 35, y = 100)

		self.glueN.place(x = 65, y = 20, width = 20)
		self.glueE.place(x = 65, y = 40, width = 20)
		self.glueS.place(x = 65, y = 60, width = 20)
		self.glueW.place(x = 65, y = 80, width = 20)

		#Frame that till hold the two buttons cancel / create
		self.buttonFrame = Frame(self.addTileWindow, borderwidth=1, background = "#000",relief=FLAT, width = self.tile_size * 3, height =  200)
		self.buttonFrame.pack(side=BOTTOM)

		self.createButton = Button(self.buttonFrame, text="Create Tile", width=8, command= self.createTile)
		self.cancelButton = Button(self.buttonFrame, text="Cancel", width=8, command= self.cancelTileCreation)
		self.createButton.pack(side=LEFT)
		self.cancelButton.pack(side=RIGHT)

		#Makes the new window open over the current editor window
		self.addTileWindow.geometry('%dx%d+%d+%d' % (NEWTILEWINDOW_W, NEWTILEWINDOW_H, 
			self.newWindow.winfo_x() + self.newWindow.winfo_width() / 2 - NEWTILEWINDOW_W /2, 
			self.newWindow.winfo_y() + self.newWindow.winfo_height() / 2 - NEWTILEWINDOW_H /2))


	def createTile(self):

		print "N ", self.newTileN.get(), "E ", self.newTileE.get(), "S ", self.newTileS.get(), "W ", self.newTileW.get(),
		r = lambda: random.randint(100,255)

		newPrevTile = {}
		print(newPrevTile)

		color = ('#%02X%02X%02X' % (r(),r(),r()))
		northGlue = self.newTileN.get()
		eastGlue = self.newTileE.get()
		southGlue = self.newTileS.get()
		westGlue = self.newTileW.get()
		label = "x"
		print "concreteChecked: ", self.concreteChecked.get()
		if self.concreteChecked.get() == 1:
			print("adding concrete")
			isConcrete = "True"
			color = "#686868"
		else:
			isConcrete = "False"

		glues = [northGlue, eastGlue, southGlue, westGlue]
		newTile = TT.Tile(None, 0, 0, 0, glues, color, isConcrete)

		self.prevTileList.append(newTile)
		self.popWinTiles()


	def cancelTileCreation(self):
		self.closeNewTileWindow()

	def selected(self, i):
		
		self.selectedTileIndex = i

		if self.outline is not None:
			self.tilePrevCanvas.delete(self.outline)

		self.outline = self.tilePrevCanvas.create_rectangle(PREVTILESTARTX, PREVTILESTARTY + 80 * i, 
			PREVTILESTARTX + PREVTILESIZE, PREVTILESTARTY + 80 * i + PREVTILESIZE, outline="#FF0000", width = 2)

		self.onAddState()

	# changes whether a tile placed will have a random color assigned to it
	# also changes the relief of the button to show whether or not it is currently selected
	def randomColorToggle(self):
		print(self.randomizeColor)
		if self.randomizeColor == True:
			print("raising")
			self.randomColorButton.config(relief=RAISED)
			self.randomizeColor = False
		else:
			print("sinking")
			self.randomColorButton.config(relief=SUNKEN)
			self.randomizeColor = True


	#fills the canvas with preview tiles
	def popWinTiles(self):

		self.tilePrevCanvas.delete("all")
		i = 0
		for prevTile in self.prevTileList:
			PREVTILESIZE = TILESIZE * 2
		 	x = PREVTILESTARTX
		 	y = PREVTILESTARTY + 80 * i
		 	size = PREVTILESIZE

		 	prevTileButton = self.tilePrevCanvas.create_rectangle(x, y, x + size, y + size, fill = prevTile.color)
		 	#tag_bing can bind an object in a canvas to an event, here the rectangle that bounds the
		 	#preview tile is bound to a mouse click, and it will call selected() with its index as the argument
		 	self.tilePrevCanvas.tag_bind(prevTileButton, "<Button-1>", lambda event, a=i: self.selected(a))
		 	#buttonArray.append(prevTileButton)

		 	
		 	if prevTile.isConcrete == False:
		 		print("printing glues")
			 	#Print Glues
			 	if prevTile.glues[0] != "None":
				 	#north
					self.tilePrevCanvas.create_text(x + size/2, y + size/5, text = prevTile.glues[0], fill="#000", font=('', size/5) )
				if prevTile.glues[1] != "None":
					#east
					self.tilePrevCanvas.create_text(x + size - size/5, y + size/2, text = prevTile.glues[1], fill="#000", font=('', size/5))
				if prevTile.glues[2] != "None":
					#south
					self.tilePrevCanvas.create_text(x + size/2, y + size - size/5, text = prevTile.glues[2], fill="#000", font=('', size/5) )
				if prevTile.glues[3] != "None":
					#west
					self.tilePrevCanvas.create_text(x + size/5, y + size/2, text = prevTile.glues[3], fill="#000", font=('',size/5) )
			
			i += 1

	def populateArray(self):
		self.coord2tile = [[None for x in range(self.board.Cols)] for y in range(self.board.Rows)]
		for p in self.board.Polyominoes:
			for tile in p.Tiles:
				self.coord2tile[tile.x][tile.y] = tile
		for conc in self.board.ConcreteTiles:
			self.coord2tile[conc.x][conc.y] = conc

	def populateBoard(self):
		#flush the board
		print("a")



	def onAddState(self):

		print("In Add State")
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

	def boardResizeDial(self):
		wr = self.WindowResizeDialogue(self.newWindow, self, self.board_w, self.board_h)

	def resizeBoard(self, w, h):
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

	def getTileIndex(self, widget_name):
		names = widget_name.split('.')
		return int(names[len(names) - 1].strip())

	def onBoardClick(self, event):
		#Determine the position on the board the player clicked
		#print "x: ", (event.x/self.tile_size)
		#print "y: ", (event.y/self.tile_size)

		if self.remove_state or event.num == 3:
			self.removeTileAtPos(event.x/self.tile_size, event.y/self.tile_size)
		elif self.add_state and event.num == 1:
			self.addTileAtPos(event.x/self.tile_size, event.y/self.tile_size)

	def removeTileAtPos(self, x, y):
		tile = self.coord2tile[x][y]

		if tile == None:
			return

		if tile.isConcrete:
			self.board.ConcreteTiles.remove(tile)
			self.coord2tile[x][y] = None
		
		else:
			tile.parent.Tiles.remove(tile) #remove tile from the polyomino that its in
			if len(tile.parent.Tiles) == 0:
				print "no more tiles in Poly!"
				self.board.Polyominoes.remove(tile.parent) #remove polyomino from the array
			
			self.coord2tile[x][y] = None

		self.board.coordToTile[x][y]= None

		print "Number of Polyominoes: ", len(self.board.Polyominoes)
		for p in self.board.Polyominoes:
			print "    Poly of length: ", len(p.Tiles)

		print "Number of ConcreteTiles: ", len(self.board.ConcreteTiles)

		self.verifyTileLocations()
		self.populateBoard()
		self.redrawPrev()

		

	def addTileAtPos(self, x, y):
		
		i = self.selectedTileIndex

		if self.coord2tile[x][y] != None:
			
			print "this is there there! ",
			print self.coord2tile[x][y]
			return
		else:
			print "There nothing there!"


		#random color function: https://stackoverflow.com/questions/13998901/generating-a-random-hex-color-in-python
		r = lambda: random.randint(100,255)
		if self.randomizeColor:
			color = ('#%02X%02X%02X' % (r(),r(),r()))
		else:
			color = self.prevTileList[i].color

		if not self.prevTileList[i].isConcrete:
			print "adding a poly"
			newPoly = TT.Polyomino(0, x, y, self.prevTileList[i].glues, color)
			self.board.Add(newPoly)
			self.coord2tile[x][y] = newPoly.Tiles[0]
			self.board.coordToTile[x][y]= newPoly.Tiles[0]
		else:
			print "adding a concrete tile"
			newConcTile = TT.Tile(None, 0, x, y, [], self.prevTileList[i].color, "True")
			self.board.AddConc(newConcTile)
			self.coord2tile[x][y] = newConcTile
			self.board.coordToTile[x][y]= newConcTile


		print "Number of Polyominoes: ", len(self.board.Polyominoes)
		for p in self.board.Polyominoes:
			print "    Poly of length: ", len(p.Tiles)

		print "Number of ConcreteTiles: ", len(self.board.ConcreteTiles)

		self.verifyTileLocations()
		self.redrawPrev()

	def verifyTileLocations(self):
		verified = True
		for p in self.board.Polyominoes:
			for tile in p.Tiles:
				if self.coord2tile[tile.x][tile.y] != tile:
					print "ERROR: Tile at ", tile.x, ", ", tile.y, " is not in array properly \n",
					verified = False

		for tile in self.board.ConcreteTiles:
			if self.coord2tile[tile.x][tile.y] != tile:
				print "ERROR: Tile at ", tile.x, ", ", tile.y, " is not in array properly \n",
				verified = False

		if verified:
			print("Tile Locations Verified")
		if not verified:
			print("TIle Locations Incorrect")



	def redrawPrev(self):
		redrawCanvas(self.board, self.board.Cols, self.board.Rows, self.BoardCanvas, self.tile_size, b_drawGrid = True, b_drawLoc = True)


	def exportTiles(self):
		self.tumbleGUI.setTilesFromEditor(self.board, self.glue_data, self.prevTileList, self.board.Cols, self.board.Rows)

	def saveTileConfig(self):
		filename = tkFileDialog.asksaveasfilename()
		tile_config = ET.Element("TileConfiguration")
		board_size = ET.SubElement(tile_config, "BoardSize")
		glue_func = ET.SubElement(tile_config, "GlueFunction")

		board_size.set("width", str(self.board.Cols))		
		board_size.set("height", str(self.board.Rows))

		#Add all preview tiles to the .xml file if there are any
		p_tiles = ET.SubElement(tile_config, "PreviewTiles")
		if len(self.prevTileList) != 0:
			for td in self.prevTileList:
				print(td.color)
				if td.glues == [] or len(td.glues) == 0:
					td.glues = [0,0,0,0]

				#Save the tile data exactly as is
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
		
			print(conc)
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

		#Just port the glue function data over to the new file
		print "glue data in tumbleedit.py ", self.glue_data
		for gl in self.glue_data:
			gs = self.glue_data[gl]
			f = ET.SubElement(glue_func, "Function")
			l = ET.SubElement(f, "Labels")
			l.set('L1', gl)
			s = ET.SubElement(f, "Strength")
			s.text = str(gs)

		#print tile_config
		mydata = ET.tostring(tile_config)
		file = open(filename+".xml", "w")
		file.write(mydata)


	def closeGUI(self):
		self.newWindow.destroy()
		self.newWindow.destroy()

	def closeNewTileWindow(self):
		self.addTileWindow.destroy()


	class WindowResizeDialogue:
		def __init__(self, parent, tumbleEdit, board_w, board_h):

			self.parent = parent

			self.tumbleEdit = tumbleEdit

			#self.bw = board_w
			#self.bh = board_h

			self.bw = StringVar()
			self.bw.set(str(board_w))

			self.bh = StringVar()
			self.bh.set(str(board_h))

			self.w = Toplevel(self.parent)
			self.w.resizable(False, False)
			self.pressed_apply = False

			Label(self.w, text="Width:").pack()
			self.bw_sbx=Spinbox(self.w, from_=10, to=100,width=5, increment=5, textvariable = self.bw)
			#self.e1.insert(0, str(board_w))
			self.bw_sbx.pack()

			Label(self.w, text="Height:").pack()
			self.bh_sbx = Spinbox(self.w, from_=10, to=100,width=5, increment=5, textvariable = self.bh)
			#self.e2.insert(0, str(board_h))
			self.bh_sbx.pack()

			Button(self.w, text="Apply:", command = lambda: self.onApply()).pack()

			self.w.focus_set()
			## Make sure events only go to our dialog
			self.w.grab_set()
			## Make sure dialog stays on top of its parent window (if needed)
			self.w.transient(self.parent)
			## Display the window and wait for it to close
			self.w.wait_window(self.w)

		def onApply(self):
			self.tumbleEdit.resizeBoard(int(self.bw.get()), int(self.bh.get()))
			self.pressed_apply = True
			self.w.destroy()


