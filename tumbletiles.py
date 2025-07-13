#GUI for Tumble Tiles
#Tim Wylie
#2018

from __future__ import absolute_import
from __future__ import print_function
from time import sleep
import copy
import sys
import inspect
import random


DEBUGGING = False

TEMP = 1
GLUEFUNC = {'N':1, 'E':1, 'S':1, 'W':1,  'A': 1, 'B': 1, 'C': 1, 'D': 1, 'X': 1, 'Y': 1, 'Z': 1}

BOARDHEIGHT = 15
BOARDWIDTH = 15
FACTORYMODE = False
COLORCHANGE = False
SINGLESTEP = False




# http://code.activestate.com/recipes/145297-grabbing-the-current-line-number-easily/
def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

#tile class for individual tiles
class Tile:
    def __init__(self):
        global COLOR
        self.symbol = ' '
        self.id = 0 #id of the polyomino that it is in
        self.x = 0
        self.y = 0
        self.color = COLOR[0]
        self.glues = ['N','E','S','W']
        self.isConcrete = False

    def __init__(self,s,r,c,g):
        self.symbol = s
        self.id = s
        self.color = "fff"
        self.x = r
        self.y = c
        self.glues = g
        self.isConcrete = False
        
    def __init__(self, parent, s,r,c,g,color, isConcrete):
        self.parent = parent #polyomino that this tile is a part of
        self.id = s
        self.symbol = s
        self.color = color
        self.x = int(r)
        self.y = int(c)


        # Check for the case that isConcrete might be passed as a String if being read from an xml file
        if isConcrete == True or isConcrete == "True":
            self.isConcrete = True
        else:
            self.isConcrete = False

        #concrete tiles wll have a symbol/id of -1
        if(self.isConcrete):
            self.glues = []
        else:
            self.glues = g

        

        
#tiles must be part of a polyomino
class Polyomino:

    #creates an empty polyomino with no tiles
    def __init__(self, p_id):
        self.id = p_id
        self.Tiles = []
        self.NumTiles = 0
        self.HasMoved = False
    

    #Takes a tile and an id, sets the tile as the only tile in the polyomino
    def __init__(self, p_id, r,c,g,color):
        self.id = p_id
        newTile = Tile(self, p_id, r, c, g, color, False)
        self.Tiles = [newTile]
        self.NumTiles = 1
        self.HasMoved = False
    
    #Takes two polyominos, adds all the tiles from poly into the tile array in (self), adjusts the number of tiles
    def Join(self, poly):
        #sym = self.Tiles[0].symbol
        sym = self.id
        color = self.Tiles[0].color
        parent = self.Tiles[0].parent
        self.Tiles.extend(poly.Tiles)
        self.NumTiles = len(self.Tiles)
        for t in self.Tiles:
            t.symbol = sym
            if False:
                t.color = color
            t.parent = parent
            
    #Checks for possible connections between every pair of tiles in two polynomials (self) and poly
    #if glue connections are found the strength is added to gluestrength and if gluestrength is
    #larger than TEMP the polyominos can be joined
    def CanJoin(self, poly):
        global TEMP
        global GLUEFUNC
        
        if poly == None:
            return False

        #glues go n,e,s,w = 0,1,2,3
        try:
            gluestrength = 0
            N,E,S,W = 0,1,2,3

            for t in self.Tiles:
                for pt in poly.Tiles:
                    
                    #pt on left, t on right
                    if pt.glues[E] != None and t.x - pt.x == 1 and pt.glues[E] != " " and len(pt.glues[E]) > 0 and t.y == pt.y:
                        if t.glues[W] != None and t.glues[W] != " " and t.glues[W] == pt.glues[E]:
                            gluestrength += int(GLUEFUNC[pt.glues[E]])
                    #t on left, pt on right
                    if pt.glues[W] != None and pt.x - t.x == 1 and pt.glues[W] != " " and len(pt.glues[W]) > 0 and t.y == pt.y:
                        if  t.glues[E] != None and t.glues[E] != " " and t.glues[E] == pt.glues[W]:
                            gluestrength += int(GLUEFUNC[pt.glues[W]])
                    #t on top, pt on bottom
                    if pt.glues[N] != None and t.x  == pt.x and pt.glues[N] != " " and len(pt.glues[N]) > 0 and t.y - pt.y == -1:
                        if t.glues[S] != None and t.glues[S] != " " and t.glues[S] == pt.glues[N]:
                            gluestrength += int(GLUEFUNC[pt.glues[N]])
                    #pt on top, t on bottom
                    if pt.glues[S] != None and t.x  == pt.x and pt.glues[S] != " " and len(pt.glues[S]) > 0 and pt.y - t.y == -1:
                        if t.glues[N] != None and t.glues[N] != " " and t.glues[N] == pt.glues[S]:
                            gluestrength += int(GLUEFUNC[pt.glues[S]])
            if gluestrength >= TEMP:
                return True
            else:
                return False
        except Exception as e:
            ...
            # print("Glue Error")
            # print(sys.exc_info()[0])  
    
    #moves every tile in the polyomino by one in the indicated direction
    def Move(self, direction):
        dx = 0
        dy = 0
        if direction == "N":
            dy = -1
        elif direction == "E":
            dx = 1
        elif direction == "S":
            dy = 1
        elif direction == "W":
            dx = -1
        
        for i in range(len(self.Tiles)):
            self.Tiles[i].x = self.Tiles[i].x + dx
            self.Tiles[i].y = self.Tiles[i].y + dy
        
        self.HasMoved = True
    

    #this method is never called
    def Closest(self, direction, x, y):
        closest = True
        for t in self.Tiles:
            if direction == "N" and t.y < y:
                closest = False
            elif direction == "E" and t.x > x:
                closest = False
            elif direction == "S" and t.y > y:
                closest = False
            elif direction == "W" and t.x < x:
                closest = False

        return closest
        
class Board:
    #constructor for polyomino, assigns the size of Rows and Colums and creates an empty board
    def __init__(self,R,C):
        self.rectangles = []
        self.glueText = []
        self.stateTmpSaves = []
        self.polyTmpSaves = []
        
        self.maxStates = 10
        self.CurrentState = -1
        
        self.poly_id_c = 0  #the number of seperate polyominos?
        self.Rows = R
        self.Cols = C
        self.Board = [[' ' for x in range(self.Cols)] for y in range(self.Rows)] #[[' ']*self.Cols]*self.Rows
        #list of polyominoes
        self.Polyominoes = []
        self.ConcreteTiles = []
        self.ConcreteColor = "#686868"
        #get the index of a polyomino based on symbol
        #need dictionary based on symbol - maybe just the index in the list? d["x"] = 3 so self.Polyominoes[d["x"]]
        #the symbol's a bad idea in the case of duplicate tile types
        self.LookUp = {}

        #a 2 dimensional dict that will be used to find a tile from its position on the board, this should make LookUp redundant
        # and can also speed up ActivateGlues, since right now it runs in O(P * P * N) time since it compares every tile of every polyominoe
        # to every tile of every other polyomino
        self.coordToTile = [[None for x in range(self.Rows)] for y in range(self.Cols)]


    def SaveStates(self):
        if len(self.stateTmpSaves) == self.maxStates:
            if(self.CurrentState == self.maxStates - 1):     
                self.stateTmpSaves.pop(0)
                self.stateTmpSaves.append(copy.copy(self))
                self.CurrentState = self.maxStates - 1
            else:
                for x in range(self.CurrentState + 1, self.maxStates - 1):
                    self.stateTmpSaves.pop(x)
                
                self.stateTmpSaves.append(copy.copy(self))
                self.CurrentState = self.CurrentState + 1
        else:
            
            self.stateTmpSaves.append(copy.copy(self))
            self.CurrentState = self.CurrentState + 1

    def Undo(self):
        if self.CurrentState == -1:
            pass
        else:
            print("Current is, ",self.CurrentState,", tried to undo", self.stateTmpSaves[self.CurrentState])
            self.CurrentState = self.CurrentState - 1
            print("Current is, ",self.CurrentState, "after")

    def Redo(self):
        if self.coordToTile == self.maxStates - 1 or self.CurrentState == len(self.stateTmpSaves)-1:
            pass
        
        else:
            self.CurrentState = self.CurrentState + 1
            
            
        
    #Adds a polyomino the the list
    def Add(self, p):
        #add tile two the two dimensional array

        tile = p.Tiles[0]

        if self.coordToTile[tile.x][tile.y] == None:
            self.coordToTile[tile.x][tile.y] = tile

            self.Polyominoes.append(p)
            print(len(self.Polyominoes))

        elif DEBUGGING:
            print("tumbletiles.py - Board.Add(): Can not add tile. A tile already exists at this location - Line ", lineno(), "\n", end=' ')

    def AddConc(self,t):

        #print "trying to add conc at", t.x, ", ", t.y, "\n"

        try:
            if self.coordToTile[t.x][t.y] == None:
                    self.coordToTile[t.x][t.y] = t
                    self.ConcreteTiles.append(t)
            elif DEBUGGING:
                print("tumbletiles.py - Board.AddConc(): Can not add tile. A tile already exists at this location - Line ", lineno(), "\n", end=' ')

        except IndexError:
            print("Can't add concrete there")

       
    
    #Joins two polyominos, deletes the 2nd redundant polyomino, calls setGrid() to make the character grid
    #accurately represent the new polyominos.
    def CombinePolys(self, p1, p2):
        if p1 == p2:
            return
        # Join the two polyominoes
        p1.Join(p2)
        
       
        if p2 in self.Polyominoes:
            self.Polyominoes.remove(p2)
        

    def resizeBoard(self, w, h):
        self.Rows = h
        self.Cols = w
        self.remapArray()
     
    #This method will check to see if loop through every position in the board and if two polyominoes are 
    #touching it will check if they can be joined and if so, it will join them
    def ActivateGlues(self):

        changed = True
        while changed: #If two polyominoes join, the resulting polyominos may need to be joined as well, so loop until none join
            changed = False
            for p in self.Polyominoes: 
                for tile in p.Tiles: #for every tile in every polyomino
                    #check every direction

                    neighbors = []


                    if tile.x + 1 < self.Cols:
                        if self.coordToTile[tile.x + 1][tile.y] != None and self.coordToTile[tile.x + 1][tile.y].parent != tile.parent:
                            neighbors.append(self.coordToTile[tile.x + 1][tile.y])

                    if tile.x - 1 >= 0:
                        if self.coordToTile[tile.x - 1][tile.y] != None and self.coordToTile[tile.x - 1][tile.y].parent != tile.parent:
                            neighbors.append(self.coordToTile[tile.x - 1][tile.y])

                    if tile.y + 1 < self.Rows:
                        if self.coordToTile[tile.x][tile.y + 1] != None and self.coordToTile[tile.x][tile.y + 1].parent != tile.parent:
                            neighbors.append(self.coordToTile[tile.x][tile.y + 1])

                    if tile.y - 1 >= 0:
                        if self.coordToTile[tile.x][tile.y - 1] != None and self.coordToTile[tile.x][tile.y - 1].parent != tile.parent:
                            neighbors.append(self.coordToTile[tile.x][tile.y - 1])
                  
                    for nei in neighbors:

                        if nei != None and nei.parent != tile.parent and p.CanJoin(nei.parent):
                            self.CombinePolys(p, nei.parent)
                            self.remapArray()
                            changed = True

            #         if changed:
            #             break
            #     if changed:
            #         break
            # if changed:
            #     break


    # Repeatedly calls Step() in a direction until Step() returns false, then Activates the glues and sets the grid again
    def Tumble(self, direction):

        global SINGLESTEP
        
        if direction == "N" or direction == "S" or direction == "E" or direction == "W":
            StepTaken = self.Step(direction)
            while StepTaken == True:
                StepTaken = self.Step(direction)
        else:
            print("Someone doesn't know what they're doing (You can only use ['N', 'E', 'S', 'W'] for glues)")
        self.ActivateGlues()


        # If in factory mode tiles will be removed if they hit the borders of the board
        if FACTORYMODE:

            deletedFlag = True

            while deletedFlag:

                #Flag to keep loop running
                deletedFlag = False

                # step in the same direction to see if anymore tiles are now hitting the border
                # not necessary in single step
                if not SINGLESTEP:
                    self.Step(direction)

                for p in self.Polyominoes:
                    for tile in p.Tiles:
                        if tile.y >= self.Rows - 1 or tile.x <= 0 or tile.x >= self.Cols - 1 or tile.y <= 0:

                            print("X: ", tile.x, " Y: ", tile.y)
                            print(("X: ", len(self.coordToTile), " Y: ", len(self.coordToTile[0])))

                            # remove the tile pointer from the mapping
                            self.coordToTile[tile.x][tile.y] = None
                            deletedFlag = True

                            # remove the tile from the polyominoes list of tiles
                            p.Tiles.remove(tile)
                
                            # IF the polyomino is now size 0 its remove from the polyomino list
                            if len(p.Tiles) == 0:
                                self.Polyominoes.remove(p)

    # Functions the same as Tumble() but it activates glues after every step
    def TumbleGlue(self, direction):
        if direction == "N" or direction == "S" or direction == "E" or direction == "W":
            StepTaken = self.Step(direction)
            self.ActivateGlues()
            while StepTaken == True:
                StepTaken = self.Step(direction)
                self.ActivateGlues()
        else:
            print("Someone doesn't know what they're doing")
    
    # Steps all tiles in one direction
    def Step(self, direction):
        for p in self.Polyominoes:
            p.HasMoved = False
            

        StepTaken = False
        dx = 0
        dy = 0
        if direction == "N":
            wallindex = -1
            dy = -1
        elif direction == "S":
            wallindex = self.Rows
            dy = 1
        if direction == "W":
            wallindex = -1
            dx = -1
        elif direction == "E":
            wallindex = self.Cols
            dx = 1
        
        # First check for all polyominos touching a wall or a concrete tile
        anyMarked = True
        while anyMarked: # This is not efficient but may be necesary to to ensure that all polyonimos that should be marked
                         # do get marked. If any polyomino is marked then it runs again check if a polyomino is touching that
                            # polyomino that was not touching a hasMoved polyomino before
            anyMarked = False

            for p in self.Polyominoes:
                # If p has already been marked as moved, checking again is not necessary
                if p.HasMoved:
                    continue

                for tile in p.Tiles:
                    neighbor = None

                    # Check if any tile is moving into a wall
                    if direction == "N" or direction == "S":
                      #  print tile.y + dy, "Y vs ", wallindex, "\n",
                        if tile.y + dy == wallindex:
                            anyMarked = True
                            p.HasMoved = True
                            

                    if direction == "W" or direction == "E":
                       # print tile.x + dx, "X vs ", wallindex, "\n",
                        if tile.x + dx == wallindex:
                            anyMarked = True
                            p.HasMoved = True                                                                                                                                         
                            

                    # Check if it is touching a concrete tile or a polyomnino that has moved
                    try:
                        neighbor = self.coordToTile[tile.x + dx][tile.y + dy]
                    except IndexError:
                        if DEBUGGING:
                            print("tumbletiles.py - Board.Step() - Index Error - Line ", lineno(), "\n", end=' ')
                    
                    if neighbor != None:
                        if neighbor.isConcrete or neighbor.parent.HasMoved:
                            anyMarked = True
                            p.HasMoved = True


        # Move all tiles in every polyomino, if none end up moving, then step taken is still false
        for p in self.Polyominoes:
            if p.HasMoved:
                continue
            if p.HasMoved == False:
               # print p, " has not moved, it has a tile at ", p.Tiles[0].x, ", ", p.Tiles[0].y, "\n"
                p.HasMoved = True
                StepTaken = True
                for tile in p.Tiles:
                    try:
                        self.coordToTile[tile.x][tile.y] = None
                    except IndexError:
                        if DEBUGGING:
                            print("tumbletiles.py - Board.Step() - Index Error - Line ", lineno(), "\n", end=' ')

                    tile.x += dx
                    tile.y += dy
                    self.coordToTile[tile.x][tile.y] = tile


        for p in self.Polyominoes: 
            for tile in p.Tiles:
                self.coordToTile[tile.x][tile.y] = tile
        # self.remapArray()

        global FACTORYMODE
        global SINGLESTEP

         # If in factory mode tiles will be removed if they hit the bottom wall
        if FACTORYMODE and SINGLESTEP:

            deletedFlag = True

            while deletedFlag:

                deletedFlag = False
               
                for p in self.Polyominoes:
                    for tile in p.Tiles:
                        if tile.y >= self.Rows - 1 or tile.x <= 0 or tile.x >= self.Cols - 1 or tile.y <= 0:

                            print("X: ", tile.x, " Y: ", tile.y)
                            print(("X: ", len(self.coordToTile), " Y: ", len(self.coordToTile[0])))
                            self.coordToTile[tile.x][tile.y] = None
                            deletedFlag = True
                            p.Tiles.remove(tile)
                
                            
                            if len(p.Tiles) == 0:
                                self.Polyominoes.remove(p)

        return StepTaken

    # Removes all tiles from their current polyomino, then puts them each in their own
    # polyomino, and activates glues
    def relistPolyominoes(self):

        r = lambda: random.randint(100,255)
        
        tileList = []
        for p in self.Polyominoes:
            for tile in p.Tiles:
                tileList.append(tile)
            p.Tiles = []
        self.Polyominoes = []
        for tile in tileList:
           # color = ('#%02X%02X%02X' % (r(),r(),r()))
            color = tile.color
            poly = Polyomino(0, tile.x, tile.y, tile.glues, color)
            self.Polyominoes.append(poly)
        self.remapArray()
        self.ActivateGlues()

    # Assignes every tile to its new correct position in coordToTile
    def remapArray(self):
        self.coordToTile = [[None for x in range(self.Rows)] for y in range(self.Cols)]
        for p in self.Polyominoes: 
            for tile in p.Tiles:
                self.coordToTile[tile.x][tile.y] = tile
        for conc in self.ConcreteTiles:
            self.coordToTile[conc.x][conc.y] = conc

    # Debugging method
    def printAllTileLocations(self):
        for p in self.Polyominoes:
            for tile in p.Tiles:
                print("Tile id: ", tile.id, " at (", tile.x, ",", tile.y, ")\n")
        
    def verifyTileLocations(self):
        verified = True
        for p in self.Polyominoes:
            for tile in p.Tiles:
                if self.coordToTile[tile.x][tile.y] != tile:
                    print("ERROR: Tile at ", tile.x, ", ", tile.y, " is not in array properly \n", end=' ')
                    verified = False
        if verified:
            print("Tile Locations Verified")
        if not verified:
            print("TIle Locations Incorrect")

    

if __name__ =="__main__":
    bh = BOARDHEIGHT
    bw = BOARDWIDTH
    board = Board(bh,bw)
    #initial
    #CreateTiles(board)
    #for i in range(5):
        #bottom tiles
       # p = Polyomino(Tile(chr(ord('M')+i), 0, bh-i-2, ['N','E','S','W']))
       # board.Add(p)
        #left tiles
       # p = Polyomino(Tile(chr(ord('A')+i), i+1, bh-1, ['S','W','N','E']))
       # board.Add(p)

    #main program loop
    # response = 'A'
    # while response != 'Q':
    #     board.GridDraw()
    #     response = raw_input("\nDirection to tumble (N,E,S,W)?")
    #     response = response.capitalize()
    #     if response != 'Q' and response !='P':
    #         board.Tumble(response)
    #     elif response == 'P':
    #         #pat = ['N','E','S','W']
    #         #pat = ['N','E','W','S']
    #         pat = ['N','W','E','S']
    #         for i in range(10):
    #             for p in pat:
    #                 board.Tumble(p.capitalize())
    

