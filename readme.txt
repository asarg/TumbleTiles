################################################################################
# Tumble Tiles
# Version 1.5
# Manual Version 0.10
# Author: Tim Wylie
# Description: Implements the tumble tile model as designed by Robert Schweller and Tim Wylie.
################################################################################
# Tumble Tiles Manual

Table of Contents
Sections
1 - Application
2 - Models Overview
3 - File I/O
4 - Feature Map
5 - Build Notes
6 - Change Log


#############################
Section 1 - Application

## 1.1 Requirements
  Required:
    -Python 2.7.+
    -Tkinter (installs with python usually)
  Optional:
    -pyscreenshot (install using pip)
    -imageio (install using pip)


## 1.2 Usage
  Running:
    >python tumblegui.py


## 1.3 Menu Overview
Main Menu
 + File
    - Example 
    - Load
    - Log Actions
    - Picture
    - Exit
 + Settings
    - Single Step
    - Glue on Step
    - Background Color
    - Show Grid
    - Grid Color
    - Show Locations
    - Board Options
 + Editor
    - Open Editor
 + Script
    - Record Script
    - Run Script
    - Export GIF
 + Help
    - About 
    
## 1.4 Menu Functions
1.4.1 File Menu
1.4.1.1 Example
  This menu option loads a simple example system to play with. The tiles are hard-coded so they can not be changed. The colors of the tiles are randomly generated.
  
  This option can be selected at any time and will flush the system and load the example system, so be careful.
  
1.4.1.2 Load
  The item will prompt the user for a file and then attempt to open it. The application will only load XML files in the VersaTile XML tile set format. Note that Tumble Tiles has a discrete component which VersaTile does not. More details on this can be found in the VersaTile documentation and in Section 3.3.
  
1.4.1.2 Log Actions
  This is a binary switch menu item that turns logging on and off. When turned on, the application will prompt the user for a file name to log the information to. It will overwrite a file if it already exists. For details see Section 3.1.

1.4.1.3 Picture
  This will prompt the user for a .jpg file name and will take a screenshot of the current tile configuration and save it. Every time it is selected the user will be prompted for another file name. For more information, see Section 3.2.

1.4.1.4 Exit
  This closes the application.

1.4.2 Settings Menu
1.4.2.1 Single Step
  This binary switch turns on the ability to move one step at a time. Thus, the direction can be switched or changed after any given step giving the user/model more flexibility. Also good for illustrative purposes.
  
1.4.2.2 Glue on Step
  This as also a binary option which glues tiles together if matching glues ever pass by each other, and not after all tiles have moved.
  
1.4.2.3 Background Color
  Prompts the user with a color dialog and the user can choose the background color behind the tiles.
  
1.4.2.4 Show Grid 
  This is a binary option to draw the discrete grid lines that the tiles are contained in.

1.4.2.5 Grid Color
  Prompts the user with a color dialog and the user can choose the color of the grid lines.

1.4.2.6 Show Locations
  This labels each square in the grid with the row/column label for additional clarity in setting up a system. The color is the same as the grid.
  
1.4.2.7 Board Options
  This brings up the "Board Options" dialog box, which lets the user modify the size of the board (rows and columns in grid), and the ability to change the size of each cell/tile displayed.   

1.4.3 Editor
1.4.3.1 Open Editor
  This loads the current board that is shown on the simulator into the editor
1.4.4 Script
1.4.4.1 Record Script
  Clicking this once will start logging the tumbles that the board makes, clicking again will save this file
1.4.4.2 Run Script
  This will let you open a file that contains a sequence of directions e.g "NWSNESNWENSNNESWNENS", it will then play them back in the simulator
1.4.4.3 Export GIF
  This will run a script and record an image after each tumble, it will then combine these images into a gif and save it in ./Gifs/
1.4.5 Help Menu
1.4.5.1 About
  Standard about menu showing the current version, author, and the all-important contact email for any issues whatsoever. Even if you just want to chat, or are having a hard day, contact this email and get help.
  
## 1.3 Controls
  The controls are fairly simple. A left-click on the side of the window will tumble the tiles in that direction. The corners and the center are disabled due to ambiguity.
  
  The arrow keys are also bound to the application so they can be used to tumble in that direction.

## 1.4 Console Application
  Tumble tiles can be run without the gui if desired. Running >python tumbletiles.py does this. The label/symbol for a tile must be unique and a single character for every tile in order for it to line up correctly.
#############################
Section 2 - Models Overview

## 2.1 Basic Model
## 2.2 Step Model
## 2.3 Glue Model
## 2.4 Glue Step Model

#############################
Section 3 - File I/O
## 3.1 Logging
  Turning this on only logs the tumbles, board changes, and loading of files/models. The log also is slightly different if there are options that change the model. 
  
  Loading Key:
  - Change BOARDWIDTH from x to y
  - Change BOARDHEIGHT from x to y
  - Change TEMP from x to y
  - Load filename - 'filename' XML model is loaded
  
  Tumble Key:
  - TN - Tumble North
  - TE - Tumble East
  - TS - Tumble South
  - TW - Tumble West
  - SN - Step North
  - SE - Step East
  - SS - Step South
  - SW - Step West
  - TGN - Tumble North (Glue Model)
  - TGE - Tumble East (Glue Model)
  - TGS - Tumble South (Glue Model)
  - TGW - Tumble West (Glue Model)
  - SGN - Step North (Glue Model)
  - SGE - Step East (Glue Model)
  - SGS - Step South (Glue Model)
  - SGW - Step West (Glue Model)
  - G - Glues applied
  
  
## 3.2 Pictures
  If pyscreenshot is installed, the current canvas can be saved as a jpg. Clicking the menu item prompts the user for the .jpg file name to use for the image. Thus, as many pictures as desired can be saved. It does not save the entire application- only the canvas.
  
  If pyscreenshot is not installed, the menu item will be disabled.

## 3.3 Loading Files

3.3.1 Modifications needed from the VersaTile XML file
  Discrete issues: 
    A. The board size will stay at the default and must be changed to the desired size in Settings/Board Options (Section 1.2.2.5). If your locations are larger than the default 10x10, the board should be resized before loading the system.
    B. VersaTile does not give the location necessary on the board. Although it does have a Location, it is used for something different in VersaTile and thus it needs to be manually changed.
    C. Tile types are only written once in the VersaTile file. Thus, if you need multiple copies of a type at a different location, the XML file will need to be manually changed.

3.3.2 XML format
  An example simple system XML file is shown below. Glue functions are bidirectional, and generally assumed to be the same label. All glue functions should be layed out separate from the tile definitions, which just reference the labels of glue functions.
  
  For tiles, as metioned in the previous section, for two identical tile types at different locations, two separate tiles must be declared in the XML.

EXAMPLE:
    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <TileConfiguration>
        <GlueFunction>
            <Function>
                <Labels L1="x2x3" L2="x2x3"/>
                <Strength>2</Strength>
            </Function>
        </GlueFunction>
        <TileType Label="New" Color="1A3399">
            <Tile>
                <Location x="0" y="1"/>
                <Color>1A3399</Color>
                <NorthGlue>bs</NorthGlue>
                <EastGlue>e</EastGlue>
                <SouthGlue>t</SouthGlue>
                <WestGlue>t1t2</WestGlue>
                <label>bs</label>
            </Tile>
        </TileType>
    </TileConfiguration>
    
#############################
Section 4 - Feature Map
  -More Flexible logging
  -Better distribution system
  -File loading should be moved out of the GUI and into the base model.
    --The console version only supports single character labels, which causes issues when loading names from VersaTile files. Need a way to expand symbol, or reduce name without causing conflict -> a polyomino must have a unique symbol for the lookup dictionary.
  -Either move example to external size file or make it optional on startup.
  -Have option on load to specify board options. (a New menu item)
  -Fill out model descriptions in manual (or better document)
  -Add ability to bring up Manual in GUI.
  -default options should be saved in a config file
  -icon in about
  -Locations font size
    
#############################
Section 5 - BUILD NOTES

  In order to build a Windows exe (as opposed to just running from the console) requires installing pyinstaller and building. The only reason to do this is if you really hate using python and like doing a lot of unnecessary work.

  Windows build exe
    #https://pyinstaller.readthedocs.io/en/stable/installation.html
        Install python https://www.python.org
        Install pypiwin - https://pypi.python.org/pypi/pypiwin32/219
        install pip-win - https://site  s.google.com/site/pydatalog/python/pip-for-windows
        install pyinstaller
        install pyscreenshot

    To build on windows 
        cd C:\Python27\Scripts\pyinstaller.exe O:\Hackr\Tumble\tumblegui.py --onedir


#############################
Section 6 - Changelog

## 6.1 Version 1.0
    - Initial version distributed to others
    
## 6.2 Version 1.1
    - Ability to change system temperature added
    - Ability to change the grid color
    - Logging details added to manual
    - Refactored globals importing tumbletiles (better encapsulation)
    - Added logging to board options
    - Added textcolor as part of the variables, but it's not in the gui yet.
    
## 6.3 Version 1.2
    - Show locations added to menu for easier system design
    - Locations use grid color
    - Status bar added to bottom to display current board options
    - Manual updated with changes in GUI
    - added requirements/usage to beginning of manual, but still needs a lot of work.
    - Menu changed from Draw Grid to Show Grid
    - Added arrow keybindings
    
## 6.4 Version 1.3
    - Fixed bug that occurred when tumbling polyominoes that were nested in other tiles.
    - font size on tiles scale with tilesize 
    - custom icon
    - Fixed XML loading bug giving NameError caused by a refactoring of library calls
    - Added custom about box for more flexibility
    
## 6.5 Version 1.4
    - Fixed a small bug in the can join glue function. It was camparing the wrong glue and so loaded files might be missing it and get a key error.
    - Updated the xml loading code 
    - Fixed a bug with N/S glues being compared wrong in CanJoin 
