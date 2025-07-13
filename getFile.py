from __future__ import absolute_import
from __future__ import print_function
import copy
from tkinter import *
import tkinter.filedialog, tkinter.messagebox, tkinter.colorchooser
import xml.etree.ElementTree as ET
import random
import time
import os,sys
import tumbletiles as TT
from enum import Enum 


class FileType(Enum):
    ANY = ("All Files", '*')
    TXT = ("Plain Text", ".txt")
    XML = ("eXtensible Markup Language", '.xml')
    GIF = ("Graphics Interchange Format", '.gif')


def getFile(type: FileType=FileType.ANY):
    filetypes = [FileType.ANY.value, FileType.TXT.value, FileType.XML.value, FileType.GIF.value]
    defaultextension = FileType.ANY.value[1]
    if type != FileType.ANY:
        filetypes = [type.value]
        defaultextension = type.value[1]

    print(filetypes)
    print(defaultextension)
    return tkinter.filedialog.askopenfilename(filetypes=filetypes, defaultextension=defaultextension)    


#parse file will get the data from a file and now return both a board object and a preview tile object
def parseFile(filename):


    tree = ET.parse(filename)
    treeroot = tree.getroot()
    #self.Log("\nLoad "+filename+"\n")

    #default size of board, changes if new board size data is read from the file
    rows = 15
    columns = 15

    boardSizeExits = False
    glueFuncExists = False
    previewTilesExist = False
    tileDataExists = False
    CommandsExists = False
   #check if the xml attributes are found
    if tree.find("GlueFunction") != None:
        glueFuncExists = True

    if tree.find("PreviewTiles") != None:
        previewTilesExist = True

    if tree.find("BoardSize") != None:
        boardSizeExists = True

    if tree.find("TileData") != None:
        tileDataExists = True

    if tree.find("Commands") != None:
        CommandsExists = True


    #data set that will be passed back to tumblegui
    tile_set_data = {"glueFunc": {}, "prevTiles": [], "tileData": []}

    if boardSizeExists:
        rows = treeroot[0].attrib["height"]
        columns = treeroot[0].attrib["width"]

    #add glue function to the data set
    if glueFuncExists:
        glueFuncTree = treeroot[1]
        for fun in glueFuncTree:
            tile_set_data["glueFunc"][fun.find('Labels').attrib['L1']] = (fun.find('Strength').text)
    
    #add preview tiles to the data set
    if previewTilesExist:
        prevTilesTree = treeroot[2];
        for prev in prevTilesTree:

            newPrevTile = {}

            newPrevTile["color"] = "#555555"
            newPrevTile["northGlue"] = " "
            newPrevTile["southGlue"] = " "
            newPrevTile["westGlue"] = " "
            newPrevTile["eastGlue"] = " "
            newPrevTile["label"] = "X"
            newPrevTile["concrete"] = " "

    

            if prev.find('Color') != None:
                if prev.find('Concrete').text == "True":
                    newPrevTile["color"] = "#686868"
                else:
                    newPrevTile["color"] = "#" + prev.find('Color').text

            if prev.find('NorthGlue') != None:
                newPrevTile["northGlue"] = prev.find('NorthGlue').text

            if prev.find('EastGlue') != None:
                newPrevTile["eastGlue"] = prev.find('EastGlue').text

            if prev.find('SouthGlue') != None:
                newPrevTile["southGlue"] = prev.find('SouthGlue').text

            if prev.find('WestGlue') != None:
                newPrevTile["westGlue"] = prev.find('WestGlue').text

            if prev.find('label') != None:
                newPrevTile["label"] = prev.find('label').text

            if prev.find('Concrete') != None:
                newPrevTile["concrete"] = prev.find('Concrete').text

            tile_set_data["prevTiles"].append(newPrevTile)


    #add tile data to the data set, these are the tiles that will actually be loaded onto the plane
    if tileDataExists:
        tileDataTree = treeroot[3]
        for tile in tileDataTree:

            newTile = {}

            newTile["location"] = {'x': 0, 'y': 0}
            newTile["color"] = "#555555"
            newTile["northGlue"] = " "
            newTile["southGlue"] = " "
            newTile["westGlue"] = " "
            newTile["eastGlue"] = " "
            newTile["label"] = "X"
            newTile["concrete"] = " "

            if tile.find('Location') != None:
                newTile["location"]["x"] = int(tile.find('Location').attrib['x'])
                newTile["location"]["y"] = int(tile.find('Location').attrib['y'])

        
            if tile.find('Color') != None:
                if tile.find('Concrete').text == "True":
                    newTile["color"] = "#686868"
                else:
                    newTile["color"] = "#" + tile.find('Color').text

            if tile.find('NorthGlue') != None:
                newTile["northGlue"] = tile.find('NorthGlue').text

            if tile.find('EastGlue') != None:
                newTile["eastGlue"] = tile.find('EastGlue').text

            if tile.find('SouthGlue') != None:
                newTile["southGlue"] = tile.find('SouthGlue').text

            if tile.find('WestGlue') != None:
                newTile["westGlue"] = tile.find('WestGlue').text

            if tile.find('label') != None:
                newTile["label"] = tile.find('label').text

            if tile.find('Concrete') != None:
                newTile["concrete"] = tile.find('Concrete').text
        

            tile_set_data["tileData"].append(newTile)

    board = TT.Board(int(rows), int(columns))
    glueFunc = tile_set_data["glueFunc"]
    prevTiles = tile_set_data["prevTiles"]
    prevTileList = []

    for tile in tile_set_data["tileData"]:
        if tile["concrete"] != "True":
            glues = [tile["northGlue"],tile["eastGlue"],tile["southGlue"],tile["westGlue"]]
            board.Add(TT.Polyomino(0, tile["location"]["x"], tile["location"]["y"], glues, tile["color"]))
        else:
            glues = []
            board.AddConc(TT.Tile(None, 0, tile["location"]["x"], tile["location"]["y"], glues, tile["color"], "True"))

    for prevTile in prevTiles:
        prevGlues = [prevTile["northGlue"],prevTile["eastGlue"],prevTile["southGlue"],prevTile["westGlue"]]
        prevTileList.append(TT.Tile( None, 0, 0, 0, prevGlues, prevTile["color"], prevTile["concrete"]))

    commands = []
    if CommandsExists:
        listOfCommands = treeroot[4]
        print(listOfCommands)
        for c in listOfCommands:
            print(c)
            print("NAME: ",c.attrib["name"],"  FILENAME: ",c.attrib["filename"])
            commands.append((c.attrib["name"], c.attrib["filename"]))

    data = [board, glueFunc, prevTileList, commands]


    return data
