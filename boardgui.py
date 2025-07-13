from __future__ import absolute_import
from tkinter import *
from PIL import Image, ImageDraw

def redrawCanvas(board, boardwidth, boardheight, canvas, tilesize, textcolor = "#000000", gridcolor = "#000000", b_drawGrid = False, b_drawLoc = False):
    canvas.delete(ALL)
    drawGrid(board, boardwidth, boardheight, canvas, tilesize, gridcolor, b_drawGrid, b_drawLoc)

    for p in board.Polyominoes:
        for tile in p.Tiles:
            color = tile.color
            board.rectangles.append(canvas.create_rectangle(tilesize*tile.x, tilesize*tile.y, tilesize*tile.x + tilesize, tilesize*tile.y + tilesize, fill = color))
            # DRAW THE GLUES
            if tile.glues == [] or tile.glues == None:
                continue

            
            if tile.glues[0] != "None":
                #north
                board.glueText.append(canvas.create_text(tilesize*tile.x + tilesize//2, tilesize*tile.y + tilesize//5, text = tile.glues[0], fill=textcolor, font=('',tilesize//5)) )
            if tile.glues[1] != "None": 
                #east
                board.glueText.append(canvas.create_text(tilesize*tile.x + tilesize - tilesize//5, tilesize*tile.y + tilesize//2, text = tile.glues[1], fill=textcolor, font=('',tilesize//5)))
            if tile.glues[2] != "None": 
                #south
                board.glueText.append(canvas.create_text(tilesize*tile.x + tilesize//2, tilesize*tile.y+ tilesize - tilesize//5, text = tile.glues[2], fill=textcolor, font=('',tilesize//5) ))
            if tile.glues[3] != "None": 
                #west
                board.glueText.append(canvas.create_text(tilesize*tile.x + tilesize//5, tilesize*tile.y + tilesize//2, text = tile.glues[3], fill=textcolor, font=('',tilesize//5) ))

    for c in board.ConcreteTiles:
        canvas.create_rectangle(tilesize*c.x, tilesize*c.y, tilesize*c.x + tilesize, tilesize*c.y + tilesize, fill = "#686868")


def drawPILImage(board, boardwidth, boardheight, canvas, tilesize, textcolor = "#000000", gridcolor = "#000000", b_drawGrid = False, b_drawLoc = False, tileRes = 100, lineWidth=10):

    tileSize = tileRes
    
    im = Image.new("RGB", (boardwidth * tileSize, boardheight * tileSize), color="#FFFFFF")
    draw = ImageDraw.Draw(im)


    for p in board.Polyominoes:
        for tile in p.Tiles:
            color = tile.color

            PILDrawTile(draw, tile.x, tile.y, tileSize, color, lineWidth)

    color="#686868"

    for c in board.ConcreteTiles:
        PILDrawTile(draw, c.x, c.y, tileSize, color, lineWidth)



    # im.save("test.png", "PNG")
    return im


def PILDrawTile(imageDraw, x, y, tileSize, color, lineWidth):
    imageDraw.rectangle((x * tileSize - lineWidth / 2, y * tileSize - lineWidth / 2, x * tileSize + tileSize + lineWidth / 2, y * tileSize  + tileSize + lineWidth /2), fill =0, outline=0)
    imageDraw.rectangle((x * tileSize + lineWidth / 2, y * tileSize + lineWidth / 2, x * tileSize + tileSize - lineWidth / 2, y * tileSize + tileSize- lineWidth / 2 ), fill =color, outline=0)






def deleteTumbleTiles(board, boardwidth, boardheight, canvas, tilesize, textcolor = "#000000", gridcolor = "#000000", b_drawGrid = False, b_drawLoc = False):
        i = 0
        while i < len(board.rectangles):
                canvas.delete(board.rectangles[i])
                i=i+1
        i = 0
        while i < len(board.glueText):
                canvas.delete(board.glueText[i])
                i=i+1
                
def redrawTumbleTiles(board, boardwidth, boardheight, canvas, tilesize, textcolor = "#000000", gridcolor = "#000000", b_drawGrid = False, b_drawLoc = False):
        i = 0
        while i < len(board.rectangles):
                canvas.delete(board.rectangles[i])
                i=i+1
        i = 0
        while i < len(board.glueText):
                canvas.delete(board.glueText[i])
                i=i+1
                
        board.rectangles = []
        board.glueText = []
        for p in board.Polyominoes:
                
            for tile in p.Tiles:
                color = tile.color
                board.rectangles.append(canvas.create_rectangle(tilesize*tile.x, tilesize*tile.y, tilesize*tile.x + tilesize, tilesize*tile.y + tilesize, fill = color))

                # DRAW THE GLUES
                if tile.glues[0] != "None":
                    #north
                    board.glueText.append(canvas.create_text(tilesize*tile.x + tilesize//2, tilesize*tile.y + tilesize//5, text = tile.glues[0], fill=textcolor, font=('',tilesize//5)) )
                if tile.glues[1] != "None": 
                    #east
                    board.glueText.append(canvas.create_text(tilesize*tile.x + tilesize - tilesize//5, tilesize*tile.y + tilesize//2, text = tile.glues[1], fill=textcolor, font=('',tilesize//5)))
                if tile.glues[2] != "None": 
                    #south
                    board.glueText.append(canvas.create_text(tilesize*tile.x + tilesize//2, tilesize*tile.y+ tilesize - tilesize//5, text = tile.glues[2], fill=textcolor, font=('',tilesize//5) ))
                if tile.glues[3] != "None": 
                    #west
                    board.glueText.append(canvas.create_text(tilesize*tile.x + tilesize//5, tilesize*tile.y + tilesize//2, text = tile.glues[3], fill=textcolor, font=('',tilesize//5) ))
            
        # for c in board.ConcreteTiles:
        #     canvas.create_rectangle(tilesize*c.x, tilesize*c.y, tilesize*c.x + tilesize, tilesize*c.y + tilesize, fill = "#686868")
                

def drawGrid(board, boardwidth, boardheight, canvas, tilesize, gridcolor = "#000000", b_drawGrid = False, b_drawLoc = False):


    if b_drawGrid == True:
        for row in range(board.Rows):
            canvas.create_line(0, row*tilesize, boardwidth*tilesize, row*tilesize, fill=gridcolor, width=.50)
        for col in range(board.Cols):
            canvas.create_line(col*tilesize, 0, col*tilesize, boardheight*tilesize, fill=gridcolor, width=.50)
                
    if b_drawLoc == True:
        for row in range(boardheight):
            for col in range(boardwidth):
                canvas.create_text(tilesize*(col+1) - tilesize//2, tilesize*(row+1) - tilesize//2, text = "("+str(row)+","+str(col)+")", fill=gridcolor,font=('',tilesize//5))

