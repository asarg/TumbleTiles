import copy
from Tkinter import *
import tkFileDialog, tkMessageBox, tkColorChooser
import xml.etree.ElementTree as ET
import random
import time
import os,sys

def getFile():
    return tkFileDialog.askopenfilename()

def parseFile(filename):


    #print "doing stuff with "+filename
    tree = ET.parse(filename)
    treeroot = tree.getroot()
    #self.Log("\nLoad "+filename+"\n")

    preview_tiles_exist = False
    if tree.find("PreviewTiles") != None:
        glue_index = False
        preview_tiles_exist = True

    gluefun = treeroot[0]

    tile_set_data = {"prevTiles": [], "glueFunc": {}, "tileData": []}

    
    #flush board
    #del tumble_board.Polyominoes[:]
    #tumble_board.LookUp = {}
    #tumble_t.GLUEFUNC = {}
    #tumble_board = tumble_t.Board(tumble_t.BOARDHEIGHT,  tumble_t.BOARDWIDTH)
    #print "get glue function"
    for fun in gluefun:
        tile_set_data["glueFunc"][fun.find('Labels').attrib['L1']] = (fun.find('Strength').text)
        #tumble_t.GLUEFUNC[fun.find('Labels').attrib['L1']] = int(fun.find('Strength').text)
    
    tile_index = 1
    if preview_tiles_exist:
        tile_index = 2
    for tt in treeroot[tile_index:]:
        new_tile_data = {}

        new_tile_data["location"] = {'x': 0, 'y': 0}
        new_tile_data["color"] = "#555555"
        new_tile_data["northGlue"] = " "
        new_tile_data["southGlue"] = " "
        new_tile_data["westGlue"] = " "
        new_tile_data["eastGlue"] = " "
        new_tile_data["label"] = "X"
        new_tile_data["concrete"] = " "


        if tt[0].find('Location') != None:
            new_tile_data["location"]["x"] = int(tt[0].find('Location').attrib['x'])
            new_tile_data["location"]["y"] = int(tt[0].find('Location').attrib['y'])

        if tt[0].find('Color') != None:
            if tt[0].find('Concrete').text == "True":
                new_tile_data["color"] = "#686868"
            else:
                new_tile_data["color"] = "#" + tt[0].find('Color').text

        if tt[0].find('NorthGlue') != None:
            new_tile_data["northGlue"] = tt[0].find('NorthGlue').text

        if tt[0].find('EastGlue') != None:
            new_tile_data["eastGlue"] = tt[0].find('EastGlue').text

        if tt[0].find('SouthGlue') != None:
            new_tile_data["southGlue"] = tt[0].find('SouthGlue').text

        if tt[0].find('WestGlue') != None:
            new_tile_data["westGlue"] = tt[0].find('WestGlue').text

        if tt[0].find('label') != None:
            new_tile_data["label"] = tt[0].find('label').text

        if tt[0].find('Concrete') != None:
            new_tile_data["concrete"] = tt[0].find('Concrete').text
        
        tile_set_data["tileData"].append(new_tile_data)

    if not preview_tiles_exist:
        return tile_set_data

    for tt in treeroot[1]:
        new_p_tile_data = {}

        new_p_tile_data["location"] = {'x': 0, 'y': 0}
        new_p_tile_data["color"] = "#555555"
        new_p_tile_data["northGlue"] = " "
        new_p_tile_data["southGlue"] = " "
        new_p_tile_data["westGlue"] = " "
        new_p_tile_data["eastGlue"] = " "
        new_p_tile_data["label"] = "X"


        if tt[0].find('Location') != None:
            new_p_tile_data["location"]["x"] = int(tt[0].find('Location').attrib['x'])
            new_p_tile_data["location"]["y"] = int(tt[0].find('Location').attrib['y'])

        if tt[0].find('Color') != None:
            new_p_tile_data["color"] = "#" + tt[0].find('Color').text

        if tt[0].find('NorthGlue') != None:
            new_p_tile_data["northGlue"] = tt[0].find('NorthGlue').text

        if tt[0].find('EastGlue') != None:
            new_p_tile_data["eastGlue"] = tt[0].find('EastGlue').text

        if tt[0].find('SouthGlue') != None:
            new_p_tile_data["southGlue"] = tt[0].find('SouthGlue').text

        if tt[0].find('WestGlue') != None:
            new_p_tile_data["westGlue"] = tt[0].find('WestGlue').text

        if tt[0].find('label') != None:
            new_p_tile_data["label"] = tt[0].find('label').text

        tile_set_data["prevTiles"].append(new_p_tile_data)
        
        #ntile = tumble_t.Tile(ntlab, ntlocx, ntlocy,[ntnort,nteast,ntsouth,ntwest],ntcol)
        #self.board.Add(tumble_t.Polyomino(ntile))
        #self.board.SetGrid()
        #self.RedrawCanvas()
        #board.GridDraw()
    #print TT.GLUEFUNC

    #print "returning tile set"
    return tile_set_data