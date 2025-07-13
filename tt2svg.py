#!/usr/bin/env python2.7

from __future__ import absolute_import
import xml.etree.ElementTree as ET

def parseFile(filename):
    tree = ET.parse(filename)
    treeroot = tree.getroot()

    #default size of board, changes if new board size data is read from the file
    rows = 15
    columns = 15

    boardSizeExits = False
    previewTilesExist = False
    tileDataExists = False

    if tree.find("PreviewTiles") != None:
        previewTilesExist = True

    if tree.find("BoardSize") != None:
        boardSizeExists = True

    if tree.find("TileData") != None:
        tileDataExists = True

    data = {"size": [],"tileData": []}

    if boardSizeExists:
        rows = treeroot[0].attrib["height"]
        columns = treeroot[0].attrib["width"]

    geomerty = [rows, columns]
    #geomerty["rows"] = rows
    #geomerty["columns"] = columns
    data["size"].append(geomerty)

    if tileDataExists:
        tileDataTree = treeroot[3]
        for tile in tileDataTree:
            newTile = {}

            newTile["location"] = {'x': 0, 'y': 0}
            newTile["color"] = "#555555"

            if tile.find('Location') != None:
                newTile["location"]["x"] = int(tile.find('Location').attrib['x'])
                newTile["location"]["y"] = int(tile.find('Location').attrib['y'])
        
            if tile.find('Color') != None:
                if tile.find('Concrete').text == "True":
                    newTile["color"] = "#686868"
                else:
                    newTile["color"] = "#" + tile.find('Color').text

            data["tileData"].append(newTile)
    return data

#  usage
#  data2SVG(parseFile("in.xml"), "out.svg", True)
def data2SVG(data, filename, gridlines=False):
    #the width of one square 
    scale = 10

    f = open(filename, 'w')
    w = scale*int(data["size"][0][0])
    h = scale*int(data["size"][0][1])
    f.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.1" baseProfile="full" width="'+str(w+2)+'" height="'+str(h+2)+'">\n')
    
    #tile the svg with transparant sqares for gridlines
    if gridlines:
        for x in range(0,w+1,scale):
            line = '<path d="M'+str(x+1)+' 1 V '+str(h+1)+'" stroke="black" stroke-width="0.5"/>'
            f.write(line)
        for y in range(0,h+1,scale):
            line = '<path d="M1 '+str(y+1)+' H '+str(w+1)+'" stroke="black" stroke-width="0.5"/>'
            f.write(line)
    
    #place tiles of file where appropriate
    for tile in data["tileData"]:
        x = scale*int(tile["location"]["x"])
        y = scale*int(tile["location"]["y"])
        c = tile["color"]
        line = '<rect x="'+str(x+1)+'" y="'+str(y+1)+'" width="'+str(scale)+'" height="'+str(scale)+'" fill="'+str(c)+'" stroke="black" stroke-width="0.5" />\n'
        f.write(line)

    f.write("</svg>")
    f.close()





#data2SVG(parseFile("in.xml"), "out.svg", True)
