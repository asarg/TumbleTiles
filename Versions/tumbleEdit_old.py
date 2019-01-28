,



class TileGeneratorGUI:

	def __init__(self, parent, canvas_width, canvas_height, rows, columns, tile_size):

		#open three windows. Call them `window_1`, `window_2`, and `window_3`
		#`window_1` will be the tile editor
		#`window_2` will be the previewer for the starting tile configuration
		#`window_3` will be the glue function editor

		self.parent = parent
		self.rows = rows
		self.columns = columns
		self.tile_size = tile_size
		self.width = canvas_width
		self.height = canvas_height

		self.glue_id = 0
		self.tile_id = 0

		self.glue_label_list = []

		self.window_1 = Toplevel(self.parent, width = canvas_width, height = canvas_height)
		self.window_2 = Toplevel(self.parent)
		self.window_3 = Toplevel(self.parent, width = canvas_width, height = canvas_height)

		self.window_1.resizable(True, True)
		self.window_2.resizable(False, False)
		self.window_3.resizable(True, True)

		self.window_1.protocol("WM_DELETE_WINDOW", self.closeGUI)
		self.window_2.protocol("WM_DELETE_WINDOW", self.closeGUI)
		self.window_3.protocol("WM_DELETE_WINDOW", self.closeGUI)

		self.window_1.wm_title("Tile Editor")
		self.window_2.wm_title("Preview")
		self.window_3.wm_title("Glue Editor")


		#self.window_1.update_idletasks()

		#self.tile_list = Frame(self.window_1)
		#self.tile_list.pack()

		
		#scrollbar.pack(side = RIGHT, fill=Y)
		#scrollbar.config(command = self.tile_canvas.yview)
		#self.tile_canvas.pack()

		##############################
		#
		#	ADD STUFF TO WINDOW 1
		#
		##############################
		self.d_tiles = {}

		self.w1f = VerticalScrolledFrame(self.window_1)
		self.w1f.pack(side = LEFT)


		self.add_tile_button = Button(self.w1f.interior, text = "Add Tile", command = self.newTile)
		self.add_tile_button.pack()

		##############################
		#
		#	ADD STUFF TO WINDOW 2
		#
		##############################
		self.preview_canvas = Canvas(self.window_2, width = canvas_width, height = canvas_height)
		self.preview_canvas.pack()

		self.drawGrid(self.preview_canvas)
		

		###############################
		#
		# ADD STUFF TO WINDOW 3
		#
		###############################

		self.d_glues = {}
		self.d_glues_names = []

		self.w3f = VerticalScrolledFrame(self.window_3)
		self.w3f.pack(side = LEFT)

		self.add_glue_button = Button(self.w3f.interior, text="Add Glue", command= self.newGlue)
		self.add_glue_button.pack(fill = X)

		self.apply_glue_button = Button(self.w3f.interior, text = "Apply Glues", command = self.applyGlues)
		self.apply_glue_button.pack(fill = X)


	def drawGrid(self, canvas):
		for row in range(self.rows):
			canvas.create_line(0, row*self.tile_size, self.width, row*self.tile_size, width = .50)
		for col in range(self.columns):
			canvas.create_line(col*self.tile_size, 0, col*self.tile_size, self.height, width = .50)

	def newGlue(self):
		new_glue = GlueGUI(self.d_glues, self.w3f.interior, self.glue_id, self.glueDestroy)

		self.glue_id +=1 

		self.d_glues[self.glue_id] = new_glue
		self.d_glues_names.append(new_glue)

		#self.w3f.SignalNewItem()

	def newTile(self):
		new_tile = TileGUI(self.d_tiles, self.w1f.interior, self.tile_id, self.tileDestroy, self.glue_label_list)

		self.tile_id += 1

		self.d_tiles[self.tile_id] = new_tile

		#self.w1f.SignalNewItem()


	def glueDestroy(self, glue_id):
		self.d_glues.pop(glue_id)

	def tileDestroy(self, tile_id):
		self.d_tiles.pop(tile_id)

	def closeGUI(self):
		self.window_1.destroy()
		self.window_2.destroy()
		self.window_3.destroy()

	def applyGlues(self):
		self.UpdateGlueMenu()


	def UpdateGlueMenu(self):
		# Build up a list of glue labels
		self.glue_label_list = []
		for glue in self.d_glues:
			label = self.d_glues[glue].label
			self.glue_label_list.append(label)


		for tile in self.d_tiles:
			self.d_tiles[tile].destroyUI()

		for tile in self.d_tiles:
			TileGUI(self.d_tiles, self.w1f.interior, self.d_tiles[tile].id, self.tileDestroy, self.glue_label_list, self.d_tiles[tile].label)

class TileGUI:

	def __init__(self, arr, parent, number, destroy_callback, glue_labels, label = None):

		self.destroy_callback = destroy_callback

		self.id = number
		self.list = arr
		
		if label == None:
			self.label = "tile_"+str(number)
		else:
			self.label = label

		self.my_frame = Frame(parent)
		self.my_frame.pack()

		Label(self.my_frame, text = "Label").pack(side = LEFT)
		self.my_label_entry = Entry(self.my_frame)
		self.my_label_entry.pack(side = LEFT)
		self.my_label_entry.insert(0, self.label)
		Frame(self.my_frame).pack()
		Label(self.my_frame, text = "Glues").pack(side = LEFT)

		variables = {"N" : StringVar(self.my_frame), "E" : StringVar(self.my_frame),
		 "S" : StringVar(self.my_frame), "W" : StringVar(self.my_frame)}
		
		Label(self.my_frame, text = "N").pack(side = LEFT)
		self.N = OptionMenu(self.my_frame, variables["N"], *glue_labels).pack(side = LEFT)

		Label(self.my_frame, text = "E").pack(side = LEFT)
		self.E = OptionMenu(self.my_frame, variables["E"], *glue_labels).pack(side = LEFT)

		Label(self.my_frame, text = "S").pack(side = LEFT)
		self.S = OptionMenu(self.my_frame, variables["S"], *glue_labels).pack(side = LEFT)

		Label(self.my_frame, text = "W").pack(side = LEFT)
		self.W = OptionMenu(self.my_frame, variables["W"], *glue_labels).pack(side = LEFT)

		Button(self.my_frame, text = "Delete Me", command = self.destroy).pack(side = LEFT)

	def destroy(self):
		self.my_frame.destroy()
		self.destroy_callback(self.id)

	def destroyUI(self):
		self.my_frame.destroy()

class GlueGUI:

	def __init__(self, arr, parent, number, destroy_callback):

		self.destroy_callback = destroy_callback

		self.id = number
		self.list = arr
		self.label = "glue_"+str(number)
		self.strength = 0

		self.my_frame = Frame(parent)
		self.my_frame.pack()

		Label(self.my_frame, text = "Label").pack(side = LEFT)
		self.my_label_entry = Entry(self.my_frame)
		self.my_label_entry.pack(side = LEFT)
		self.my_label_entry.insert(0, self.label)

		Label(self.my_frame, text = "Strength").pack(side = LEFT)
		self.my_strength = Entry(self.my_frame)
		self.my_strength.pack(side = LEFT)
		self.my_strength.insert(0, str(self.strength))

		Button(self.my_frame, text = "Delete Me", command = self.destroy).pack(side = LEFT)

	def destroy(self):
		self.my_frame.destroy()
		self.destroy_callback(self.id)

	def destroyUI(self):
		self.my_frame.destroy()