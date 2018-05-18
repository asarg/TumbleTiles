from Tkinter import *

def redrawCanvas(board, boardwidth, boardheight, canvas, tilesize, textcolor = "#000000", gridcolor = "#000000", b_drawGrid = False, b_drawLoc = False):
	canvas.delete(ALL)
	board.SetGrid()
	drawGrid(board, boardwidth, boardheight, canvas, tilesize, gridcolor, b_drawGrid, b_drawLoc)

	# for row in range(board.Rows):
	# 	for col in range(board.Cols):
	# 		if board.Board[row][col] != ' ' and board.Board[row][col] != 'C':
	# 			pin = board.LookUp[board.Board[row][col]]
	# 			color = board.Polyominoes[pin].Tiles[0].color
	# 			canvas.create_rectangle(tilesize*col, tilesize*row, tilesize*col + tilesize, tilesize*row + tilesize, fill = color)

	# 			for t in board.Polyominoes[pin].Tiles:
	# 				if t.x == col and t.y == row:
	# 					#north
	# 					canvas.create_text(tilesize*col + tilesize/2, tilesize*row + tilesize/5, text = t.glues[0], fill=textcolor, font=('',tilesize/5) )
	# 					#east
	# 					canvas.create_text(tilesize*col + tilesize - tilesize/5, tilesize*row + tilesize/2, text = t.glues[1], fill=textcolor, font=('',tilesize/5))
	# 					#south
	# 					canvas.create_text(tilesize*col + tilesize/2, tilesize*row + tilesize - tilesize/5, text = t.glues[2], fill=textcolor, font=('',tilesize/5) )
	# 					#west
	# 					canvas.create_text(tilesize*col + tilesize/5, tilesize*row + tilesize/2, text = t.glues[3], fill=textcolor, font=('',tilesize/5) )
			
	# 		elif board.Board[row][col] == 'C':
	# 			canvas.create_rectangle(tilesize*col, tilesize*row, tilesize*col + tilesize, tilesize*row + tilesize, fill = board.ConcreteColor)
				# for i in range (1,11):
				# 	canvas.create_line(col*tilesize + i * tilesize / 10, tilesize*row, col*tilesize + i * tilesize / 10, tilesize*row + tilesize, fill="#000", width=.25)

	for p in board.Polyominoes:
		for tile in p.Tiles:
			color = p.Tiles[0].color
			canvas.create_rectangle(tilesize*tile.x, tilesize*tile.y, tilesize*tile.x + tilesize, tilesize*tile.y + tilesize, fill = color)

			# DRAW THE GLUES
			#north
			canvas.create_text(tilesize*tile.x + tilesize/2, tilesize*tile.y + tilesize/5, text = tile.glues[0], fill=textcolor, font=('',tilesize/5) )
			#east
			canvas.create_text(tilesize*tile.x + tilesize - tilesize/5, tilesize*tile.y + tilesize/2, text = tile.glues[1], fill=textcolor, font=('',tilesize/5))
			#south
			canvas.create_text(tilesize*tile.x + tilesize/2, tilesize*tile.y+ tilesize - tilesize/5, text = tile.glues[2], fill=textcolor, font=('',tilesize/5) )
			#west
			canvas.create_text(tilesize*tile.x + tilesize/5, tilesize*tile.y + tilesize/2, text = tile.glues[3], fill=textcolor, font=('',tilesize/5) )

	for c in board.ConcreteTiles:
		canvas.create_rectangle(tilesize*c.x, tilesize*c.y, tilesize*c.x + tilesize, tilesize*c.y + tilesize, fill = "#686868")


def drawGrid(board, boardwidth, boardheight, canvas, tilesize, gridcolor = "#000000", b_drawGrid = False, b_drawLoc = False):

    if b_drawGrid == True:
        for row in range(board.Rows):
            canvas.create_line(0, row*tilesize, boardwidth*tilesize, row*tilesize, fill=gridcolor, width=.50)
        for col in range(board.Cols):
            canvas.create_line(col*tilesize, 0, col*tilesize, boardheight*tilesize, fill=gridcolor, width=.50)
                
    if b_drawLoc == True:
        for row in range(boardheight):
            for col in range(boardwidth):
                canvas.create_text(tilesize*(col+1) - tilesize/2, tilesize*(row+1) - tilesize/2, text = "("+str(row)+","+str(col)+")", fill=gridcolor,font=('',tilesize/5))