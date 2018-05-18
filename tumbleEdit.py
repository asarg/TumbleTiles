import copy
from Tkinter import *
from scrollableFrame import VerticalScrolledFrame
import tkFileDialog, tkMessageBox, tkColorChooser
import xml.etree.ElementTree as ET
import tumbletiles as TT
from boardgui import redrawCanvas, drawGrid
import random
import time
import os,sys

#the x and y coordinate that the preview tiles will begin to be drawn on
PREVTILESTARTX = 20
PREVTILESTARTY = 21

PREVTILESIZE = 70

class TileEditorGUI:
	def __init__(self, parent, tumbleGUI, board_width, board_height, tile_size, tile_data, glue_data, preview_tile_data):

		#open two windows
		#`w1` will be the tile editor
		#`w2` will be a tile config previewer


		self.parent = parent
		self.board = None
		self.board_w = board_width
		self.board_h = board_height

		#instance of tumbleGUI that created it so methods from that class can be called
		self.tumbleGUI = tumbleGUI

		#self.rows = self.board.Rows
		#self.columns = self.board.Cols
		self.tile_size = tile_size
		self.width = board_width*tile_size
		self.height = board_height*tile_size
		self.tile_data = tile_data
		self.glue_data = glue_data
		self.preview_tile_data = preview_tile_data
		self.previewTileArray = None

		self.selectedTileIndex = -1

		#States for the tile editor
		self.remove_state = False
		self.add_state = False

		#Variable to hold on to the specifications of the tile to add
		self.tile_to_add = None

		self.glue_label_list = []

		#A two-dimensional array
		self.coord2tile = {}

		#outline of a preview tile when it is selected
		self.outline = None

		#boolean for whether or not to randomize the color of a placed tile
		self.randomizeColor = False


		#populate the array
		self.populateArray()

		#populate the boards
		self.populateBoard()

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


		#draw the board on the canvas
		self.popWinTiles()
		self.redrawPrev()
		


	def addNewPrevTile(self):
		print("A")

	def selected(self, i):
		print(self.preview_tile_data[i])
		data = self.preview_tile_data
		
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

		data = self.preview_tile_data

		
		self.tilePrevCanvas = Canvas(self.tileEditorFrame, width = self.tile_size * 3, height = self.height)
		self.tilePrevCanvas.pack(side=BOTTOM)
		
		buttonArray = []

		#loop through the list of tiles and draw a rectangle for each one
		if data == None:
			return

		for i in range(len(data)):
		 	tile = data[i]
		 	print(tile)

		 	x = PREVTILESTARTX
		 	y = PREVTILESTARTY + 80 * i
		 	size = PREVTILESIZE

		 	prevTileButton = self.tilePrevCanvas.create_rectangle(x, y, x + size, y + size, fill = tile["color"])

		 	#tag_bing can bind an object in a canvas to an event, here the rectangle that bounds the
		 	#preview tile is bound to a mouse click, and it will call selected() with its index as the argument
		 	self.tilePrevCanvas.tag_bind(prevTileButton, "<Button-1>", lambda event, a=i: self.selected(a))
		 	#buttonArray.append(prevTileButton)

		 	
		 	if not tile["concrete"] == "True":
			 	#Print Glues
			 	#north
				self.tilePrevCanvas.create_text(x + size/2, y + size/5, text = tile["northGlue"], fill="#000", font=('', size/5) )
				#east
				self.tilePrevCanvas.create_text(x + size - size/5, y + size/2, text = tile["eastGlue"], fill="#000", font=('', size/5))
				#south
				self.tilePrevCanvas.create_text(x + size/2, y + size - size/5, text = tile["southGlue"], fill="#000", font=('', size/5) )
				#west
				self.tilePrevCanvas.create_text(x + size/5, y + size/2, text = tile["westGlue"], fill="#000", font=('',size/5) )

	def populateArray(self):
		for td in self.tile_data:
			if td["location"]["x"] not in self.coord2tile.keys():
				self.coord2tile[td["location"]["x"]] = {}
			self.coord2tile[td["location"]["x"]][td["location"]["y"]] = td

	def populateBoard(self):
		#flush the board
		self.board = TT.Board(self.board_h, self.board_w)

		for x in self.coord2tile:
			for y in self.coord2tile[x]:
				td = self.coord2tile[x][y]

				
				tile = TT.Tile(td["label"],
					td["location"]["x"], 
					td["location"]["y"],
					[td["northGlue"], td["eastGlue"], td["southGlue"], td["westGlue"]],
					td["color"], td["concrete"])

				if tile.isConcrete == False:
					self.board.Add(TT.Polyomino(tile, self.board.poly_id_c))
				else:
					self.board.AddConc(tile)



	def onAddState(self):

		#print "Clicked on ",tile_index
		#print "Label: %s\n Location: (%i, %i)\n[NG: %s, EG: %s, SG: %s, WG: %s]\n, C: %s", self.tile_data[tile_index]["label"],self.tile_data[tile_index]["location"]["x"], self.tile_data[tile_index]["location"]["y"],self.tile_data[tile_index]["northGlue"], self.tile_data[tile_index]["eastGlue"], self.tile_data[tile_index]["southGlue"], self.tile_data[tile_index]["westGlue"],self.tile_data[tile_index]["color"]
		#print "Click on a position in the board to add a tile"
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
		wr = self.WindowResizeDialogue(self.newWindow, self.board_w, self.board_h)
		
		if wr.pressed_apply:
			print "Resizing"

			self.board_w = int(wr.bw.get())
			self.board_h = int(wr.bh.get())

			print self.board_w
			print self.board_h

			#self.w2.config(width=self.board_w*self.tile_size, height=self.board_h*self.tile_size)
			self.newWindow.geometry(str(self.board_w*self.tile_size)+'x'+str(self.board_h*self.tile_size+76))
			self.BoardCanvas.config(width=self.board_w*self.tile_size, height=self.board_h*self.tile_size)

			self.populateBoard()
			self.redrawPrev()
		else:
			print "Closed regularly"

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
		tile = self.getTileAtPos(x, y)
		
			

		if tile != None:
			self.tile_data.remove(tile)

			
			del self.coord2tile[x][y]
			self.populateBoard()
			self.redrawPrev()

		

	def addTileAtPos(self, x, y):
		
		if x not in self.coord2tile.keys():
			self.coord2tile[x] = {}

		#random color function: https://stackoverflow.com/questions/13998901/generating-a-random-hex-color-in-python
		r = lambda: random.randint(0,255)

		#Create new tile from preview tile data
		ntile = {}
		ntile["label"] = self.preview_tile_data[self.selectedTileIndex]["label"]
		ntile["location"] = {}
		ntile["location"]["x"] = x
		ntile["location"]["y"] = y
		ntile["northGlue"] = self.preview_tile_data[self.selectedTileIndex]["northGlue"]
		ntile["eastGlue"] = self.preview_tile_data[self.selectedTileIndex]["eastGlue"]
		ntile["southGlue"] = self.preview_tile_data[self.selectedTileIndex]["southGlue"]
		ntile["westGlue"] = self.preview_tile_data[self.selectedTileIndex]["westGlue"]

		#if random color is selected, will plae the tile down with a random color
		if not self.randomizeColor:
			ntile["color"] = self.preview_tile_data[self.selectedTileIndex]["color"]
		else:
			ntile["color"] = ('#%02X%02X%02X' % (r(),r(),r()))

		ntile["concrete"] = self.preview_tile_data[self.selectedTileIndex]["concrete"]

		
		
		
		#Add this tile into the Tile array
		self.coord2tile[x][y] = ntile
		self.tile_data.append(ntile)

		self.populateBoard()
		self.redrawPrev()
		#self.onClearState()



	def getTileAtPos(self, x, y):
		if x in self.coord2tile.keys():
			if y in self.coord2tile[x].keys():
				return self.coord2tile[x][y]

		return None

	def redrawPrev(self):
		redrawCanvas(self.board, self.board_w, self.board_h, self.BoardCanvas, self.tile_size, b_drawGrid = True, b_drawLoc = True)


	def exportTiles(self):
		self.tumbleGUI.setTilesFromEditor(self.tile_data, self.glue_data, self.preview_tile_data, self.board_w, self.board_h)

	def saveTileConfig(self):
		filename = tkFileDialog.asksaveasfilename()
		tile_config = ET.Element("TileConfiguration")
		board_size = ET.SubElement(tile_config, "BoardSize")
		glue_func = ET.SubElement(tile_config, "GlueFunction")

		#Add all preview tiles to the .xml file if there are any
		p_tiles = ET.SubElement(tile_config, "PreviewTiles")
		if self.preview_tile_data != None:
			for td in self.preview_tile_data:
				#Save the tile data exactly as is
				prevTile = ET.SubElement(p_tiles, "PrevTile")
	

				c = ET.SubElement(prevTile, "Color")
				c.text = str(td["color"]).replace("#", "")

				ng = ET.SubElement(prevTile, "NorthGlue")
				ng.text = td["northGlue"]

				sg = ET.SubElement(prevTile, "SouthGlue")
				sg.text = td["southGlue"]

				eg = ET.SubElement(prevTile, "EastGlue")
				eg.text = td["eastGlue"]

				wg = ET.SubElement(prevTile, "WestGlue")
				wg.text = td["westGlue"]

				co = ET.SubElement(prevTile, "Concrete")
				co.text = td["concrete"]

				la = ET.SubElement(prevTile, "Label")
				la.text = td["label"]

		tiles = ET.SubElement(tile_config, "TileData")
		# save all tiles on the board to the .xml file
		if self.tile_data != None:
			for td in self.tile_data:
				#Save the tile data exactly as is

				t = ET.SubElement(tiles, "Tile")

				loc = ET.SubElement(t, "Location")
				loc.set("x", str(td["location"]["x"]))
				loc.set("y", str(td["location"]["y"]))

				c = ET.SubElement(t, "Color")
				c.text = str(td["color"]).replace("#", "")

				ng = ET.SubElement(t, "NorthGlue")
				ng.text = td["northGlue"]

				sg = ET.SubElement(t, "SouthGlue")
				sg.text = td["southGlue"]

				eg = ET.SubElement(t, "EastGlue")
				eg.text = td["eastGlue"]

				wg = ET.SubElement(t, "WestGlue")
				wg.text = td["westGlue"]

				co = ET.SubElement(t, "Concrete")
				co.text = td["concrete"]

				la = ET.SubElement(t, "Label")
				la.text = td["label"]

		#Just port the glue function data over to the new file
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


	class WindowResizeDialogue:
		def __init__(self, parent, board_w, board_h):

			self.parent = parent

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
			self.pressed_apply = True
			self.w.destroy()


