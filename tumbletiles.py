#GUI for Tumble Tiles
#Tim Wylie
#2018


import copy
import sys

TEMP = 1
GLUEFUNC = {'N':1, 'E':1, 'S':1, 'W':1,}
BOARDHEIGHT = 15
BOARDWIDTH = 15

#tile class for individual tiles
class Tile:
    def __init__(self):
        self.symbol = ' '
        self.x = 0
        self.y = 0
        self.color = COLOR[0]
        self.glues = ['N','E','S','W']

    def __init__(self,s,r,c,g):
        self.symbol = s
        self.color = "fff"
        self.x = r
        self.y = c
        self.glues = g
        
    def __init__(self,s,r,c,g,color):
        self.symbol = s
        self.color = color
        self.x = r
        self.y = c
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
    def __init__(self, t, p_id):
        self.id = p_id
        self.Tiles = [t]
        self.NumTiles = 1
        self.HasMoved = False
    
    #Takes two polyominos, adds all the tiles from poly into the tile array in (self), adjusts the number of tiles
    def Join(self, poly):
        #sym = self.Tiles[0].symbol
        sym = self.id
        color = self.Tiles[0].color
        self.Tiles.extend(poly.Tiles)
        self.NumTiles = len(self.Tiles)
        for t in self.Tiles:
            t.symbol = sym
            t.color = color
            
    #Checks for possible connections between every pair of tiles in two polynomials (self) and poly
    #if glue connections are found the strength is added to gluestrength and if gluestrength is
    #larger than TEMP the polyominos can be joined
    def CanJoin(self, poly):
        global TEMP
        global GLUEFUNC
        
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
                    #print t.glues,t.x,t.y,pt.glues,pt.x,pt.y,gluestrength
            if gluestrength >= TEMP:
                return True
            else:
                return False
        except Exception as e:
            #print "CANJOIN"
            print sys.exc_info()[0]        
    
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
        self.poly_id_c = 0  #the number of seperate polyominos?
        self.Rows = R
        self.Cols = C
        self.Board = [[' ' for x in range(self.Cols)] for y in range(self.Rows)] #[[' ']*self.Cols]*self.Rows
        #list of polyominoes
        self.Polyominoes = []
        #get the index of a polyomino based on symbol
        #need dictionary based on symbol - maybe just the index in the list? d["x"] = 3 so self.Polyominoes[d["x"]]
        #the symbol's a bad idea in the case of duplicate tile types
        self.LookUp = {}
    
    #Adds a polyomino the the list
    def Add(self, p):
        self.Polyominoes.append(p)
        #self.LookUp[p.Tiles[0].symbol] = len(self.Polyominoes) - 1
        self.LookUp[self.poly_id_c] = len(self.Polyominoes) - 1
        self.poly_id_c += 1
        #print self.Polyominoes[0].Tiles[0].x
    
    #Prints out every character at their respective position on the grid   
    def GridDraw(self):
        self.SetGrid()
        for row in range(self.Rows): #self.Board:
            for col in range(self.Cols):#row:
                print self.Board[row][col],
            print "\n",

    #Sets all position of the grid to ' '
    def ClearGrid(self):
        for row in range(self.Rows):
            for col in range(self.Cols):
                self.Board[row][col] = ' '
    
    #Sets the values of each position in the grid to their respective polyomino ID             
    def SetGrid(self):
        #reset board to blanks
        self.ClearGrid()

        #add in symbols
        for p in self.Polyominoes:
            p.HasMoved = False
            for t in p.Tiles:
                #self.Board[t.y][t.x] = t.symbol
                self.Board[t.y][t.x] = p.id

    def ResizeGrid(self, nheight, nwidth):
        self.Rows = nheight
        self.Cols = nwidth
        self.Board = [[' ' for x in range(self.Cols)] for y in range(self.Rows)] 
        self.SetGrid()
    
    #Joins two polyominos, deletes the 2nd redundant polyomino, calls setGrid() to make the character grid
    #accurately represent the new polyominos.
    def CombinePolys(self, pin1, pin2):
        #remove 2nd poly from list
        #p1 = self.Polyominoes[pin1]
        #p2 = self.Polyominoes[pin2]
        #p2sym = self.Polyominoes[pin2].Tiles[0].symbol
        p2sym = self.Polyominoes[pin2].id
        self.Polyominoes[pin1].Join(self.Polyominoes[pin2])
        
        #self.Polyominoes.remove(p2)
        # or self.Polyominoes.pop(pin2)
        del self.Polyominoes[pin2]
        
        #update symbols on grid
        self.SetGrid()
        #delete lookup record for other symbol
        del self.LookUp[p2sym]
        
        #since a polyomino was removed, the indices in the lookup may be bad, reconfigure
        for p in range(len(self.Polyominoes)):
            #self.LookUp[self.Polyominoes[p].Tiles[0].symbol] = p
            self.LookUp[self.Polyominoes[p].id] = p
     
    #This method will check to see if loop through every position in the board and if two polyominoes are 
    #touching it will check if they can be joined and if so, it will join them
    def ActivateGlues(self):
        try:
            Changed = True
            while Changed == True:
                Changed = False
                #search west / east neighbors
                for row in range(self.Rows):
                    for we in range(self.Cols-1):
                        #if something here
                        we1sym = self.Board[row][we] #we1sym = the char at Board[row][we]
                        if we1sym != ' ':
                            #if different poly than east neighbor
                            we2sym = self.Board[row][we+1]
                            if we2sym != ' ' and we1sym != we2sym:
                                we1in = self.LookUp[we1sym] #we1in = id of 1st polyomino
                                we2in = self.LookUp[we2sym] #we2in = id of 2nd polyomino
                                #if they can bond
                                if self.Polyominoes[we1in].CanJoin(self.Polyominoes[we2in]):
                                    #combine
                                    self.CombinePolys(we1in,we2in)
                                    Changed = True
                #search north /south neighbors
                for col in range(self.Cols):
                    for ns in range(self.Rows-1):
                        #if something here
                        ns1sym = self.Board[ns][col]
                        if ns1sym != ' ':
                            #if different poly than east neighbor
                            ns2sym = self.Board[ns+1][col]
                            if ns2sym != ' ' and ns1sym != ns2sym:
                                ns1in = self.LookUp[ns1sym] #ns1in = id of 1st polyomino
                                ns2in = self.LookUp[ns2sym] #ns2in = id of 2nd polyomino
                                #if they can bond
                                if self.Polyominoes[ns1in].CanJoin(self.Polyominoes[ns2in]):
                                    #combine
                                    self.CombinePolys(ns1in,ns2in)
                                    Changed = True
        except Exception as e:
            print sys.exc_info()[0]                     
    
    #Repeatedly calls Step() in a direction until Step() returns false, then Activates the glues and sets the grid again
    def Tumble(self, direction):
        if direction == "N" or direction == "S" or direction == "E" or direction == "W":
            StepTaken = self.Step(direction)
            while StepTaken == True:
                StepTaken = self.Step(direction)
        else:
            print "Someone doesn't know what they're doing"
            
        self.ActivateGlues()
        self.SetGrid()

    #Functions the same as Tumble() but it activates glues after every step
    def TumbleGlue(self, direction):
        if direction == "N" or direction == "S" or direction == "E" or direction == "W":
            StepTaken = self.Step(direction)
            self.ActivateGlues()
            while StepTaken == True:
                StepTaken = self.Step(direction)
                self.ActivateGlues()
        else:
            print "Someone doesn't know what they're doing"
          
        self.SetGrid()
        
 
        
    
    #
    def Step(self, direction):
        for p in self.Polyominoes:
            p.HasMoved = False
            
        StepTaken = False
        dx = 0
        dy = 0
        if direction == "N":
            wallindex = 0
            dy = -1
        elif direction == "S":
            wallindex = self.Rows - 1
            dy = 1
        if direction == "W":
            wallindex = 0
            dx = -1
        elif direction == "E":
            wallindex = self.Cols - 1
            dx = 1
        
        #move everything up while nothing touches the wall
        if (direction == "N" or direction == "S") and self.Board[wallindex].count(' ') == self.Cols:
            for i in range(len(self.Polyominoes)):
                self.Polyominoes[i].Move(direction)
            StepTaken = True
        elif (direction == "E" or direction == "W") and zip(*self.Board)[wallindex].count(' ') == self.Rows:
            for i in range(len(self.Polyominoes)):
                self.Polyominoes[i].Move(direction)
            StepTaken = True
        else:
            #something is touching the wall,
            #mark these as moved
            if (direction == "N" or direction == "S"):
                for sym in self.Board[wallindex]:
                    if sym != ' ':
                        self.Polyominoes[self.LookUp[sym]].HasMoved = True
            else:
                for sym in zip(*self.Board)[wallindex]:
                    if sym != ' ':
                        self.Polyominoes[self.LookUp[sym]].HasMoved = True
                
                    
            allmoved = False
            #now stepwise tumble all things not touching wall that can move
            while allmoved == False:
                nonemarked = True
                for pin in range(len(self.Polyominoes)):
                    if self.Polyominoes[pin].HasMoved == False:
                        for t in self.Polyominoes[pin].Tiles:
                            #checks if any polyominoes are touching a wall, if so it marks them as moved
                            if t.y + dy < 0 or t.y + dy == self.Rows or t.x + dx < 0 or t.x + dx == self.Cols:
                                self.Polyominoes[pin].HasMoved = True
                                nonemarked = False
                            else:
                                #checks if it is touching a polyominoe that will not move, if so mark hasMoved as true
                                symmove = self.Board[t.y + dy][t.x + dx]
                                if symmove != ' ' and symmove != t.symbol:
                                    nei = self.LookUp[symmove]
                                    if self.Polyominoes[nei].HasMoved == True:
                                        self.Polyominoes[pin].HasMoved = True
                                        nonemarked = False
                
                if nonemarked == True:
                    for pin in range(len(self.Polyominoes)):
                        if self.Polyominoes[pin].HasMoved == False:
                            self.Polyominoes[pin].Move(direction)
                            StepTaken = True
        
                #check if everything has moved
                allmoved = True
                for p in self.Polyominoes:
                    if p.HasMoved == False:
                        allmoved = False
           
        self.SetGrid()
        return StepTaken
        
    


if __name__ =="__main__":
    bh = BOARDHEIGHT
    bw = BOARDWIDTH
    board = Board(bh,bw)
    #initial
    #CreateTiles(board)
    for i in range(5):
        #bottom tiles
        p = Polyomino(Tile(chr(ord('M')+i), 0, bh-i-2, ['N','E','S','W']))
        board.Add(p)
        #left tiles
        p = Polyomino(Tile(chr(ord('A')+i), i+1, bh-1, ['S','W','N','E']))
        board.Add(p)
    
    board.SetGrid()

    #main program loop
    response = 'A'
    while response != 'Q':
        board.GridDraw()
        response = raw_input("\nDirection to tumble (N,E,S,W)?")
        response = response.capitalize()
        if response != 'Q' and response !='P':
            board.Tumble(response)
        elif response == 'P':
            #pat = ['N','E','S','W']
            #pat = ['N','E','W','S']
            pat = ['N','W','E','S']
            for i in range(10):
                for p in pat:
                    board.Tumble(p.capitalize())
    

