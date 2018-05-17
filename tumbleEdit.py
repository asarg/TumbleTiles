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
PREVTILESTARTY = 1

PREVTILESIZE = 70

class TileEditorGUI:
	def __init__(self, parent, board_width, board_height, tile_size, tile_data, glue_data, preview_tile_data):

		#open two windows
		#`w1` will be the tile editor
		#`w2` will be a tile config previewer

		self.parent = parent
		self.board = None
		self.board_w = board_width
		self.board_h = board_height

		#self.rows = self.board.Rows
		#self.columns = self.board.Cols
		self.tile_size = tile_size
		self.width = board_width*tile_size
		self.height = board_height*tile_size
		self.tile_data = tile_data
		self.glue_data = glue_data
		self.preview_tile_data = preview_tile_data

		#States for the tile editor
		self.remove_state = False
		self.add_state = False

		#Variable to hold on to the specifications of the tile to add
		self.tile_to_add = None

		self.glue_label_list = []

		#A two-dimensional array
		self.coord2tile = {}

		#populate the array
		self.populateArray()

		#populate the board
		self.populateBoard()

		#/////////////////
		#	Window 1 config
		#////////////////
		
		

		#populate the window with tiles
		self.w1f = None


		#//////////////////
		#	Window Config
		#/////////////////
		self.newWindow = Toplevel(self.parent)
		self.newWindow.wm_title("Previewer")
		self.newWindow.resizable(False, False)
		self.newWindow.protocol("WM_DELETE_WINDOW", lambda: self.closeGUI())
		self.newWindow.bind("<Button-1>", lambda event: self.onPreviewClick(event))
		
		#Create two frames, one to hold the board and the buttons, and one to hold the tiles to be placed
		self.tileEditorFrame = Frame(self.newWindow, width = self.width, height = self.height, borderwidth=1)
		self.tileEditorFrame.pack(side=RIGHT)
		
		self.BoardFrame = Frame(self.newWindow, borderwidth=1, width = 500, height = 500)
		self.BoardFrame.pack(side=LEFT)
		
		self.BoardCanvas = Canvas(self.BoardFrame, width = self.width, height = self.height)
		self.BoardCanvas.pack(side=TOP)
		

		Button(self.BoardFrame, text = "Remove tile", command = self.onRemoveState).pack(side=BOTTOM)
		Button(self.BoardFrame, text = "Resize board", command = self.boardResizeDial).pack(side=BOTTOM)
		Button(self.BoardFrame, text = "Save tile config", command = self.saveTileConfig).pack(side=BOTTOM)

		#draw the board on the canvas
		self.popWinTiles()
		self.redrawPrev()
		#//////////////////
		# 	End Window 2 config
		#/////////////////

	def selected(i):
		data = self.preview_tile_data


	#fills the canvas with preview tiles
	def popWinTiles(self):

		data = self.preview_tile_data

		
		tilePrevCanvas = Canvas(self.tileEditorFrame, width = self.tile_size * 3, height = self.height)
		tilePrevCanvas.pack(side=TOP)
		
		buttonArray = []

		#loop through the list of tiles and draw a rectangle for each one
		for i in range(len(data)):
		 	tile = data[i]
		 	print(tile)

		 	x = PREVTILESTARTX
		 	y = PREVTILESTARTY + 80 * i
		 	size = PREVTILESIZE

		 	prevTileButton = tilePrevCanvas.create_rectangle(x, y, x + size, y + size, fill = tile["color"])
		 	tilePrevCanvas.tag_bind("prevTileButton", "<Button-1>", lambda event, a=i: self.selected(a))
		 	buttonArray.append(prevTileButton)

		 	print tile["northGlue"], tile["southGlue"], tile["eastGlue"]
		 	#Print Glues
		 	#north
			tilePrevCanvas.create_text(x + size/2, y + size/5, text = tile["northGlue"], fill="#000", font=('', size/5) )
			#east
			tilePrevCanvas.create_text(x + size - size/5, y + size/2, text = tile["eastGlue"], fill="#000", font=('', size/5))
			#south
			tilePrevCanvas.create_text(x + size/2, y + size - size/5, text = tile["southGlue"], fill="#000", font=('', size/5) )
			#west
			tilePrevCanvas.create_text(x + size/5, y + size/2, text = tile["westGlue"], fill="#000", font=('',size/5) )

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
					td["color"], False)

				self.board.Add(TT.Polyomino(tile, self.board.poly_id_c))

	def onAddState(self, event):
		tile_index = self.getTileIndex(str(event.widget))
		#print "Clicked on ",tile_index
		#print "Label: %s\n Location: (%i, %i)\n[NG: %s, EG: %s, SG: %s, WG: %s]\n, C: %s", self.tile_data[tile_index]["label"],self.tile_data[tile_index]["location"]["x"], self.tile_data[tile_index]["location"]["y"],self.tile_data[tile_index]["northGlue"], self.tile_data[tile_index]["eastGlue"], self.tile_data[tile_index]["southGlue"], self.tile_data[tile_index]["westGlue"],self.tile_data[tile_index]["color"]
		#print "Click on a position in the board to add a tile"
		self.remove_state = False
		self.add_state = True
		self.tile_to_add = self.tile_data[tile_index]

	def onRemoveState(self):
		#print "Click on a position in the board to remove a tile"
		self.remove_state = True
		self.add_state = False
		self.tile_to_add = None

	def onClearState(self):
		self.remove_state = False
		self.add_state = False
		self.tile_to_add = None

	def boardResizeDial(self):
		wr = self.WindowResizeDialogue(self.w2, self.board_w, self.board_h)
		
		if wr.pressed_apply:
			print "Resizing"

			self.board_w = int(wr.bw.get())
			self.board_h = int(wr.bh.get())

			print self.board_w
			print self.board_h

			#self.w2.config(width=self.board_w*self.tile_size, height=self.board_h*self.tile_size)
			self.w2.geometry(str(self.board_w*self.tile_size)+'x'+str(self.board_h*self.tile_size+76))
			self.w2c.config(width=self.board_w*self.tile_size, height=self.board_h*self.tile_size)

			self.populateBoard()
			self.redrawPrev()
		else:
			print "Closed regularly"

	def getTileIndex(self, widget_name):
		names = widget_name.split('.')
		return int(names[len(names) - 1].strip())

	def onPreviewClick(self, event):
		#Determine the position on the board the player clicked
		#print "x: ", (event.x/self.tile_size)
		#print "y: ", (event.y/self.tile_size)

		if self.remove_state:
			self.removeTileAtPos(event.x/self.tile_size, event.y/self.tile_size)
		elif self.add_state:
			self.addTileAtPos(event.x/self.tile_size, event.y/self.tile_size)

	def removeTileAtPos(self, x, y):
		tile = self.getTileAtPos(x, y)

		if tile != None:
			del self.coord2tile[x][y]
			self.populateBoard()
			self.redrawPrev()

		self.onClearState()

	def addTileAtPos(self, x, y):
		if x not in self.coord2tile.keys():
			self.coord2tile[x] = {}
		#create a copy of the tile
		ntile = {}
		ntile["label"] = self.tile_to_add["label"]
		ntile["location"] = {}
		ntile["location"]["x"] = x
		ntile["location"]["y"] = y
		ntile["northGlue"] = self.tile_to_add["northGlue"]
		ntile["eastGlue"] = self.tile_to_add["eastGlue"]
		ntile["southGlue"] = self.tile_to_add["southGlue"]
		ntile["westGlue"] = self.tile_to_add["westGlue"]
		ntile["color"] = self.tile_to_add["color"]
		ntile["concrete"] = self.tile_to_add["concrete"]

		self.coord2tile[x][y] = ntile

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

	def saveTileConfig(self):
		filename = tkFileDialog.asksaveasfilename()
		tile_config = ET.Element("TileConfiguration")
		glue_func = ET.SubElement(tile_config, "GlueFunction")

		#Save preview tiles
		#First check if there are any preview tiles
		#if not, this is a fresh edit of a versaTile file.
		#create a new preview tile block
		p_tiles = ET.SubElement(tile_config, "PreviewTiles")
		if self.preview_tile_data == None:
			for td in self.tile_data:
				#Save the tile data exactly as is
				tt = ET.SubElement(p_tiles, "TileType")
				t = ET.SubElement(tt, "Tile")
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
				la = ET.SubElement(t, "Label")
				la.text = td["label"]
		else:
			#do the same as above, but with the
			#preview tiles object
			for td in self.preview_tile_data:
				#Save the tile data exactly as is
				tt = ET.SubElement(p_tiles, "TileType")
				t = ET.SubElement(tt, "Tile")
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

		#For each tile type on the board, save it to the xml file
		for x in self.coord2tile:
			for y in self.coord2tile[x]:
				td = self.coord2tile[x][y]
				tt = ET.SubElement(tile_config, "TileType")
				t = ET.SubElement(tt, "Tile")
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
				la = ET.SubElement(t, "Label")
				la.text = td["label"]

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


