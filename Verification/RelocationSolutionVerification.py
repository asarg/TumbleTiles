from __future__ import absolute_import
from __future__ import print_function
import tumbletiles as TT
from sets import Set
from getFile import getFile, parseFile
import time
import random
from six.moves import range

#	"[bluex][bluey][redx][redy]"
# Structure for starting and end coordinates is "21003603"

# Since calculating the starting coordinates is costly, only run it if you want to check different positions
recalcStart = True

blueStartN = "2903" #NORTH
blueStartE = "5125" #EAST
blueStartS = "2650" #SOUTH
blueStartW = "0428" #WEST

blueOutN = "2903" 
blueOutE = "5125"
blueOutS = "2650"
blueOutW = "0428"

redPath1 = "4411" #The North East path the red is trapped in
redPath2 = "1243" #The South West path the red is trapped in

#Empty board must not have any tiles on it
emptyBoardFile = "RelocationEmpty.xml"

#Location where the starting coordinates will be saved
startFile = "Coordinates/startCoordinates.txt"

# 'valid' 'invalid' 'all' which positions the script will check for
checkFor = "invalid"

visitedPositions = Set()
startingPositions = Set()
stuckPositions = Set()
redEscapedPositions = Set()
solvedPositions1 = Set()
solvedPositions2 = Set()
solvedNodes = []
redEscapedNodes = []
board = None
nodeCount = 0
root = None
solution = ""
start =  ""
solutions = 0


stuckSetFile = "Coordinates/stuckCoordinates.txt"

startSetFile = "Coordinates/startCoordinates.txt"

redEscSetFile = "Coordinates/redEscCoordinates.txt"


class Tree(object):
	def __init__(self, coordinates):
		self.coordinates = coordinates
		self.directionFromParent = ""
		self.north = None
		self.south = None
		self.east = None
		self.west = None
		self.stuck = False
		self.redundant = False
		self.solved = False
		self.redEscaped = False
		self.parent = None

def moveRandomDirection():
    randToDirection = {'0':'N', '1':'E', '2':'S', '3':'W'}
    rand = random.randint(0,3)
    dir = randToDirection.get(str(rand))
    board.Tumble(dir)


def logStartingCoordinates():
	global blueStartN
	global blueStartE
	global blueStartS
	global blueStartW
	global emptyBoardFile
	global redPath1
	global redPath2
	global startFile
	global checkFor

	checkValid = False
	checkInvalid = False
	checkAll = False

	print("Calculating ", checkFor, "starting positions...")

	if checkFor == 'valid':
		checkValid = True
	if checkFor == 'invalid':
		checkInvalid = True
	if checkFor == 'all':
		checkAll = True

	redX1 = int(redPath1[:2])
	redY1 = int(redPath1[2:4])

	redX2 = int(redPath2[:2])
	redY2 = int(redPath2[2:4])

	redGlues = ["S","S","S","S"]

	positionSet = Set()
	redSet = Set()

	

	file = open(startFile, "w")

	redPoly = TT.Polyomino(0, redX1, redY1, redGlues, "#ff0000")
	board.Add(redPoly)

	tile = board.Polyominoes[0].Tiles[0]

	tile.x = redX1
	tile.y = redY1

	tileMoved = False
	for x in range(0,1000):
	    stringX = str(tile.x)
	    stringY = str(tile.y)
	    coordString = ""

	    if len(stringX) == 1:
	        coordString = "0"
	    coordString = coordString + stringX

	    if len(stringY) == 1:
	        coordString = coordString + "0"
	    coordString = coordString + stringY

	    if coordString not in redSet:
	        redSet.add(coordString)
	        # print(coordString)

	        if (not tileMoved and checkValid) or (tileMoved and checkInvalid) or checkAll:
	            file.write(blueStartN + coordString + "\n")
	            file.write(blueStartE + coordString + "\n")
	        if (tileMoved and checkValid) or (not tileMoved and checkInvalid) or checkAll:
	            file.write(blueStartS + coordString + "\n")
	            file.write(blueStartW + coordString + "\n")

	        positionSet.add(blueStartN + coordString)
	        positionSet.add(blueStartW + coordString)
	        positionSet.add(blueStartS + coordString)
	        positionSet.add(blueStartE + coordString)

	    moveRandomDirection()


	    if tileMoved == False and x > 500:
	        tile.x = redX2
	        tile.y = redY2
	        tileMoved = True

	board.Polyominoes.remove(redPoly)


# Takes a board and returns the coordinates of the red and blue tile in the correct format
def getCoordinateString():
	global board
	if len(board.Polyominoes[1].Tiles) == 4:
		bluePoly = board.Polyominoes[1]
	else:
		print("error")

	blueX = bluePoly.Tiles[0].x  
	blueY = bluePoly.Tiles[0].y

	if bluePoly.Tiles[1].x < blueX or bluePoly.Tiles[1].y < blueY:
		blueX = bluePoly.Tiles[1].x
		blueY = bluePoly.Tiles[1].y

	if bluePoly.Tiles[2].x < blueX or bluePoly.Tiles[2].y < blueY:
		blueX = bluePoly.Tiles[2].x
		blueY = bluePoly.Tiles[2].y

	if bluePoly.Tiles[3].x < blueX or bluePoly.Tiles[3].y < blueY:
		blueX = bluePoly.Tiles[3].x
		blueY = bluePoly.Tiles[3].y

	blueX = str(blueX)
	blueY = str(blueY)

	if len(board.Polyominoes[0].Tiles) == 1:
		redPoly = board.Polyominoes[0]
	else:
		print("error")

	redX = str(redPoly.Tiles[0].x)
	redY = str(redPoly.Tiles[0].y)

	if len(blueX) == 1:
		blueX = "0" + blueX
	if len(blueY) == 1:
		blueY = "0" + blueY
	if len(redX) == 1:
		redX = "0" + redX
	if len(redY) == 1:
		redY = "0" + redY
	coordString = blueX + blueY + redX + redY
	# print(coordString)

	return coordString



def printTileCoords():
	bluePoly = board.Polyominoes[1]

	print("Blue: ", bluePoly.Tiles[0].x, ", ", bluePoly.Tiles[0].y,"   ", bluePoly.Tiles[1].x, ", ", bluePoly.Tiles[1].y, "   ", bluePoly.Tiles[2].x, ", ", bluePoly.Tiles[2].y, "   ", bluePoly.Tiles[3].x, ", ", bluePoly.Tiles[3].y) 

	redPoly = board.Polyominoes[0]

	print("Red: ", redPoly.Tiles[0].x, ", ", redPoly.Tiles[0].y)

def revertBoardToStart(startingPosition):
	blueX = int(startingPosition[:2])
	blueY = int(startingPosition[2:4])

	redX = int(startingPosition[4:6])
	redY = int(startingPosition[6:8])

	# print "BlueX: ", blueX, "\nBlueY: ", blueY, "\nRedX: ", redX, "\nRedY: ", redY
	
	bluePoly = board.Polyominoes[1]
	bluePoly.Tiles[0].x = blueX
	bluePoly.Tiles[0].y = blueY

	bluePoly.Tiles[1].x = blueX + 1
	bluePoly.Tiles[1].y = blueY

	bluePoly.Tiles[2].x = blueX
	bluePoly.Tiles[2].y = blueY + 1

	bluePoly.Tiles[3].x = blueX + 1
	bluePoly.Tiles[3].y = blueY + 1

	redPoly = board.Polyominoes[0]

	redPoly.Tiles[0].x = redX
	redPoly.Tiles[0].y = redY

	board.ActivateGlues()
	board.remapArray()

	# print "Current Positions\n Blue:\n1: ", bluePoly.Tiles[0].x, ", ", bluePoly.Tiles[0].y, "\n2: ", bluePoly.Tiles[1].x, ", ", bluePoly.Tiles[1].y, "\n3: ", bluePoly.Tiles[2].x, ", ", bluePoly.Tiles[2].y, "\n4: ", bluePoly.Tiles[3].x, ", ", bluePoly.Tiles[3].y 
	# time.sleep(5)
	# board.ActivateGlues()

# Check to see if athe blue square is trying to leave out of the hallway, which is not allowed
def blueLeaving(startingPosition, newPosition, direction):
	# return False
	if newPosition[:4] == blueOutN and solution == blueStartS:
		return True
	if newPosition[:4] == blueOutE and solution == blueStartW:
		return True
	if newPosition[:4] == blueOutS and solution == blueStartN:
		return True
	if newPosition[:4] == blueOutW and solution == blueStartE:
		return True
	if startingPosition[:4] == blueStartN and direction == "N":
		# print("Blue trying to leave!")
		return True
	if startingPosition[:4] == blueStartE and direction == "E":
		# print("Blue trying to leave!")
		return True
	if startingPosition[:4] == blueStartS and direction == "S":
		# print("Blue trying to leave!")
		return True
	if startingPosition[:4] == blueStartW and direction == "W":
		# print("Blue trying to leave!")
		return True

	return False

def recurseTree(root, startingPosition, direction):
	global nodeCount
	# print(nodeCount)
	nodeCount = nodeCount + 1

	newNode = Tree(startingPosition)
	newNode.parent = root
	newNode.directionFromParent = direction


	# print "CURRENT POSITION: ", getCoordinateString()

	if startingPosition in visitedPositions:
		newNode.redundant = True
	else:
		visitedPositions.add(startingPosition)

	if startingPosition in stuckPositions:
		newNode.stuck = True

	if startingPosition[:4] == solution:
		# print "Solution: "
		# print(startingPosition[:4])
		# printTileCoords()
		newNode.solved = True
		solvedNodes.append(newNode)

	if startingPosition[4:8] in redEscapedPositions:
		newNode.redEscaped = True
		redEscapedNodes.append(newNode)

	
	if not newNode.solved and not newNode.redEscaped:

		board.Tumble("N")
		newConfig = getCoordinateString()
		if not "N" == newNode.directionFromParent and newConfig not in visitedPositions and newConfig != startingPosition and not blueLeaving(startingPosition, newConfig, "N"):
			newNode.north = recurseTree(newNode, newConfig,"N")

		revertBoardToStart(startingPosition)


		board.Tumble("S")
		newConfig = getCoordinateString()
		if not "S" == newNode.directionFromParent and newConfig not in visitedPositions and newConfig != startingPosition and not blueLeaving(startingPosition,newConfig,  "S"):
			newNode.north = recurseTree(newNode, newConfig,"S")

		revertBoardToStart(startingPosition)



		board.Tumble("E")
		newConfig = getCoordinateString()
		if not "E" == newNode.directionFromParent and newConfig not in visitedPositions and newConfig != startingPosition and not blueLeaving(startingPosition,newConfig,  "E"):
			newNode.north = recurseTree(newNode, newConfig,"E")

		revertBoardToStart(startingPosition)


		board.Tumble("W")
		newConfig = getCoordinateString()
		if not "W" == newNode.directionFromParent and newConfig not in visitedPositions and newConfig != startingPosition and not blueLeaving(startingPosition,newConfig,  "W"):
			newNode.north = recurseTree(newNode, newConfig,"W")

	return newNode

# Loads the positions for the stuck positions, solved positions, 
# and red escaped positions into their respective sets
# adds the blue tile to the board
def initialize():
	global stuckSetFile 
	global startSetFile 
	global redEscSetFile

	#Clear log file
	file = open("Log/log.txt", "w")
	file.write("")

	stuckFile = open(stuckSetFile, "r")
	startFile = open(startSetFile, "r")
	redEscFile = open(redEscSetFile, "r")

	for l in startFile.readlines():
		startingPositions.add(l[:8])

	# for l in stuckFile.readlines():
	# 	stuckPositions.add(l[:8])

	for l in redEscFile.readlines():
		redEscapedPositions.add(l[:4])

	print("Number of starting positions: ", len(startingPositions))

	blueGlues = ["N","N","N","N"]
	redGlues = ["S","S","S","S"]


	bluePoly = TT.Polyomino(1, 0, 0, blueGlues, "#0000ff")
	redPoly = TT.Polyomino(0, board.Rows - 1, board.Cols - 1, redGlues, "#ff0000")
	board.Add(redPoly)
	board.Add(bluePoly)

	# Add the rest of the tiles to the blue square
	bluePoly.Tiles.append(TT.Tile(bluePoly, 1, 1, 0, blueGlues, "#0000ff", False))
	bluePoly.Tiles.append(TT.Tile(bluePoly, 1, 0, 1, blueGlues, "#0000ff", False))
	bluePoly.Tiles.append(TT.Tile(bluePoly, 1, 1, 1, blueGlues, "#0000ff", False))

	# print "Added blue tile at", board.Polyominoes[1].Tiles[0]



def printSequence(node):
	if node.directionFromParent == "START":
		print("START", " - ", node.coordinates)
		return

	printSequence(node.parent)

	print(node.directionFromParent, " - ", node.coordinates)


def logSequence(node, file):
	if node.directionFromParent == "START":
		return

	logSequence(node.parent, file)

	file.write(node.directionFromParent)

def logData():
	file = open("Log/log.txt", "a")
	file.write("\n" + start + "\n")
	file.write("****************************\nSolutions:\n")
	for node in solvedNodes:
		file.write(start)
		logSequence(node, file)
		file.write("\n")
	# file.write("****************************\nRed Escape:\n")

	# for node in redEscapedNodes:
	# 	file.write(start)
	# 	logSequence(node, file)
	# 	file.write("\n")

		


def createTree(startingPosition):
	global nodeCount
	global solution
	global board
	global root
	global start
	global solvedNodes
	global visitedPositions
	global redEscapedNodes
	global blueStartN
	global blueStartE
	global blueStartS
	global blueStartW
	global solutions

	revertBoardToStart(startingPosition)

	# print "Reverting to ", startingPosition
	# printTileCoords()

	start = startingPosition
	# Set to hold all position that have been visited
	nodeCount = 0
	solvedNodes = []
	redEscapedNodes = []
	visitedPositions.clear()

	#set determines if the solution should be in the blue in the bottom and right or

	if startingPosition[:4] == blueStartN:
		solution = blueStartS
	elif startingPosition[:4] == blueStartS:
		solution = blueStartN
	elif startingPosition[:4] == blueStartE:
		solution = blueStartW
	elif startingPosition[:4] == blueStartW:
		solution = blueStartE

	root = Tree(startingPosition)
	

	recurseTree(root, startingPosition, "START")

	print("Tree Creation Complete for: ", startingPosition, "\nTotal Nodes: ", nodeCount, "\nSolution Nodes: ", len(solvedNodes))
	# print "\nRed Esc Nodes:", len(redEscapedNodes)

	logData()
	if len(solvedNodes) > 0:
		solutions = solutions + 1



def loadBoard():
	global board

	print("Loading empty board file from: ", emptyBoardFile, "...")

	boardData = parseFile(emptyBoardFile)
	board = boardData[0]






if __name__ =="__main__":
	loadBoard()

	if recalcStart:
		logStartingCoordinates()

	initialize()

	for start in startingPositions:
		createTree(start)
	# print "\n\n******************************\n--Tree Creation Complete\n"
	#createTree("51254024")

	print("Number of paths with a solution: ", solutions)
	# createTree("26504330")






	
	
	






