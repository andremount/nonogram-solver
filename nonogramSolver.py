# import time tools and start stopwatch
import time
t0 = time.time()

# get math functions for working with arrays
import numpy

# show steps as analyzer works?
showWork = True

# save an animated gif of the analysis?
exportGif = True
if exportGif:

    # get filename for output gif
    filename = input("Enter a filename for the animated gif (do not include the extension): ")

    # get operating system functions like listing files in directory and making directories
    import os 

    # get the current directory (__file__ is this module)
    current_directory = os.path.dirname(os.path.abspath(__file__)) 

    # import image tools (Pillow)
    from PIL import Image, ImageDraw

    # set counter for filenames
    #imgCount = 0
    frames = []

    # function for generating frame image from grid
    def exportImg(grid):

        # set scale by specifying pixels per square
        scale = 30

        # calculate image dimensions from grid
        width = len(grid[0])
        height = len(grid)

        # create new canvas
        im = Image.new('RGB', (width * scale, height * scale), (186, 192, 198))
        draw = ImageDraw.Draw(im)

        # iterate through grid rows, then columns
        for xPos, row in enumerate(grid):
            for yPos, val in enumerate(row):

                # get upper-left and lower right corner coordinates for each box
                ulx = yPos * scale
                uly = xPos * scale
                lrx = (yPos * scale) + scale - 1
                lry = (xPos * scale) + scale - 1

                # add colored squares according to grid values
                if val == 1:
                    draw.rectangle((ulx, uly, lrx, lry), fill=(11, 29, 36))
                elif val == 0:
                    draw.rectangle((ulx, uly, lrx, lry), fill=(243, 244, 252))
                
        # save individual frames
        # outputPath = os.path.join(current_directory, 'output', 'output-' + f'{imgCount:03}' + '.gif')
        # im.save(outputPath, quality=100)

        # add current frame to list
        frames.append(im)


def solvePuzzle(allClues):

    # check validity by comparing sums of horizontal and vertical clues
    # (this does not guarantee a valid puzzle)
    hSum = sum([sum(i) for i in allClues["horizontalClues"]])
    vSum = sum([sum(i) for i in allClues["verticalClues"]])
    if hSum != vSum:
        print("These clues will not create a valid puzzle.")
        return

    # get grid dimensions based on the number of clues
    numRows = len(allClues["horizontalClues"])
    numCols = len(allClues["verticalClues"])

    # build the grid
    grid = []
    for _ in range(numRows): # (_ is for unused variable in loop)
        row = []
        for _ in range(numCols):
            row.append(None)
        grid.append(row)

    # convert the grid into a NumPy array    
    # https://numpy.org/doc/stable/reference/generated/numpy.array.html
    grid = numpy.array(grid)

    # set up a dictionary for the layout possibilities for each row/column
    layoutPossibilities = {
        "rows" : [],
        "cols" : []
    }

    # analyze rows
    print("Calculating layout possibilities for each row...")
    for rowPos in range(numRows):
        print(rowPos + 1,"/",numRows)

        # send cells and clues to getLayoutPossibilities()
        layoutsForThisRow = getLayoutPossibilities(cells = grid[rowPos], clues = allClues["horizontalClues"][rowPos])

        # add results to the list in the dictionary
        layoutPossibilities["rows"].append(layoutsForThisRow)

    # transpose the grid using NumPy to make analyzing columns easier
    transposedGrid = numpy.transpose(grid)

    # analyze columns    
    print("Calculating layout possibilities for each column...")
    for colPos in range(numCols):
        print(colPos + 1,"/",numCols)

        # send cells and clues to getLayoutPossibilities()
        layoutsForThisCol = getLayoutPossibilities(cells = transposedGrid[colPos], clues = allClues["verticalClues"][colPos])

        # add results to the list in the dictionary
        layoutPossibilities["cols"].append(layoutsForThisCol)

    # send the puzzle to the grid analyzer
    solution = analyzeGrid(allClues, grid, numRows, numCols, layoutPossibilities)

    # print the solution    
    printGrid(solution)


def getLayoutPossibilities(cells, clues):

    # length of the row/column being analyzed
    seriesLength = len(cells)

    # how many gaps (of length 0 to ? cells) there around the clues
    gapCount = len(clues) + 1

    # number of empty cells not counting to single empty cell that must appear between clues
    # (length of series, minus sum of clues, minus one less than the number of clues)
    emptyCellsNoSpacers = seriesLength - sum(clues) - (len(clues) - 1)

    # get all of the different arrangements of white space
    gaps = getPartitions(targetSum = emptyCellsNoSpacers, addendCount = gapCount)

    # given these clues and gaps, generate a list of row possibilities
    # frist declare an empty list
    seriesPossibilities = []
    
    # for each arrangement of empty in gaps
    for arr in gaps:

        # declare an empty list for the current arrangment
        thisSeries = []

        # alternate between adding 0-x instances of empty space and the clues in order
        for i, num in enumerate(arr):

            # add white cells...
            for _ in range(num):
                thisSeries.append(0)
            
            # add cells according to clues...
            if i < len(clues):

                # add filled cells...
                for _ in range(clues[i]):
                    thisSeries.append(1)
                
                # add spacer cells (except for after the last clue)
                if i < len(clues) - 1:
                    thisSeries.append(0)
        
        # add this arrangement of empty and filled cells to the list of possibilities
        seriesPossibilities.append(thisSeries)

    return seriesPossibilities


# recursive function that will generate a list of addends (of predetermined length) for a given target sum
def getPartitions(targetSum, addendCount, listPosition = 0):
    
    # this is for when the recursion gets to its maximum depth
    # the target sum (which is incrementally decreased below) will now be equal to the original target minus anything in the list
    if addendCount - 1 == listPosition:
        return [[targetSum]]

    # declare an empty list for the output
    output = []

    # loop a number of times according to the target sum (plus one to include that sum in the range)
    for i in range(targetSum + 1):

        # recurse with lowered target sum and increased list position to track recursion depth
        for item in getPartitions(targetSum - i, addendCount, listPosition = listPosition + 1):

            # add the result to the output
            output.append([i] + item)

    return output


def analyzeGrid(allClues, grid, numRows, numCols, seriesPossibilities):

    # show work at this step
    if showWork:
        printGrid(grid)
        print("\nNow solving rows...\n")

    # analyze rows
    for rowPos in range(numRows):
        
        # send cells and layout possibilities to filter function
        filterResults = filterLayouts(cells = grid[rowPos], layoutPossibilities = seriesPossibilities["rows"][rowPos])
        
        # update grid and layout possibilities
        grid[rowPos] = filterResults[0]
        seriesPossibilities["rows"][rowPos] = filterResults[1]

    # show work at this step
    if showWork:
        printGrid(grid)
        print("\nNow solving columns...\n")

    # transpose the grid using NumPy to make analyzing columns easier
    transposedGrid = numpy.transpose(grid)
    
    # (more complicted than rows because columns need to be built by iterating over rows)
    for colPos in range(numCols):

        # send cells and layout possibilities to filter function
        filterResults = filterLayouts(cells = transposedGrid[colPos], layoutPossibilities = seriesPossibilities["cols"][colPos])

        # update grid and layout possibilities
        transposedGrid[colPos] = filterResults[0]
        seriesPossibilities["cols"][colPos] = filterResults[1]
    
    # transpose the grid back to the original
    grid = numpy.transpose(transposedGrid)
    
    # scan the grid for unmarked cells and repeat the analysis if any are found
    # (NOTE: It is possible that simply counting instances of None will allow this function to run in an infinite loop. Further testing required.)
    noneCount = 0
    for row in grid:
        for cell in row:
            if cell == None:
                noneCount += 1
    if noneCount > 0:
        analyzeGrid(allClues, grid, numRows, numCols, seriesPossibilities)
    
    # send the completed grid back
    return grid


def filterLayouts(cells, layoutPossibilities):

    # eliminate arrangements that don't fit the current constraints
    # first set up a dictionary for the constraints...
    constraintPositions = {}
    for i, cell in enumerate(cells):
        if cell != None:
            constraintPositions[i] = cell

    # ...then filter the list of possible arrangments
    for pos, val in constraintPositions.items():
        layoutPossibilities = [layout for layout in layoutPossibilities if layout[pos] == val]

    # find what the remaining series have in common
    # first declare a dictionary for the commonalities
    commonalities = {}
    
    # then cycle through and compare all the possibilities
    for i in range(len(cells)):
        
        # iterate through all series possibilities and compare them, item by item, to the first possibility
        # if all series possibilities have the same item in the current position...
        result = all(layout[i] == layoutPossibilities[0][i] for layout in layoutPossibilities)
        
        # ...add it to the list of commonalities
        if result:
            commonalities[i] = layoutPossibilities[0][i]

    # copy the input cells for the output
    output = cells

    # for any commonalities, change the corresponding item in the output list
    for pos, val in commonalities.items():
        output[pos] = val

    return output, layoutPossibilities

# function for printing the grid at any point
def printGrid(grid):
    for line in grid:
        thisString = ""
        for char in line:
            if char == None:
                thisString += "__"
            elif char == 0:
                thisString += "\u2588\u2588"
            elif char == 1:
                thisString += "\u2591\u2591"
        print(thisString)

    if exportGif:
        exportImg(grid)



    



# SHAPE
testPuzzle0 = {"horizontalClues": [[4], [2], [2]], "verticalClues": [[3], [3], [1], [1]]}
# solvePuzzle(testPuzzle0)
# 0.39 seconds

# BIRD
testPuzzle1 = {"horizontalClues": [[2], [1, 2], [8], [5], [3], [1]], "verticalClues": [[1], [1, 2], [5], [5], [3], [2], [1], [1], [1]]}
# solvePuzzle(testPuzzle1)
# 0.47 seconds

# CROW
testPuzzle2 = {"horizontalClues": [[2], [2, 2], [7], [5], [6], [7], [7], [8], [9], [9], [7, 1], [6], [8, 4], [1, 1, 1, 3], [10, 4]], "verticalClues": [[1, 1], [3], [4, 1, 1], [7, 1, 1], [9, 3], [10, 1, 1], [13, 1], [1, 13], [2, 8, 1], [2, 6, 1], [1, 5], [1, 4], [1, 3], [2], [1]]}
# solvePuzzle(testPuzzle2)
# 0.79 seconds

# MAGNIFYING GLASS
testPuzzle3 = {"horizontalClues": [[5], [9], [2, 8], [1, 9], [1, 3, 6], [2, 2, 6], [2, 2, 2, 4], [2, 2, 3, 4], [1, 3, 2, 4], [1, 3, 4], [2, 8], [9], [6], [3], [1], [1], [3], [3], [3], [3], [3], [3], [3], [3], [1]], "verticalClues": [[3], [5], [2, 2], [2, 5, 2], [1, 7, 1], [5, 5], [4, 5, 8], [4, 2, 15], [5, 3, 4, 8], [8, 4], [5, 5], [11], [9], [5], [3]]}
# solvePuzzle(testPuzzle3)
# 0.65 seconds

# TIGER
testPuzzle4 = {"horizontalClues": [[5, 5], [1, 9, 1], [1, 2, 1, 1, 2, 1], [1, 1, 3, 3, 1, 1], [2, 1, 1, 1], [1, 1], [1, 3, 4, 1], [1, 1, 1, 1, 3, 1, 1], [2, 1, 1, 1, 1, 2], [1, 1, 1, 2, 1, 1, 1], [1, 3, 4, 1], [1, 4, 1, 1], [2, 1, 2, 1, 2], [1, 1, 1, 2], [3, 1, 2, 1, 3], [1, 1, 8, 1, 2], [1, 4, 4, 1], [2, 2, 2, 2], [1, 2, 2, 1, 1], [1, 4, 1]], "verticalClues": [[4, 5, 1], [1, 2, 1, 5, 1, 1], [1, 2, 1, 1, 1, 1, 2], [1, 1, 1, 1, 1, 1], [1, 1, 2], [1, 2, 3, 2], [1, 1, 1, 1, 1, 2], [4, 4, 1, 1], [1, 1, 2, 1, 1], [1, 1, 2, 2, 1], [1, 4, 2, 1], [1, 1, 2, 1, 1], [4, 5, 1, 1], [1, 1, 2, 1, 1, 2], [2, 2, 4, 2], [1, 1, 2], [1, 1, 1, 1, 1, 1], [1, 2, 1, 1, 1, 1, 2], [1, 2, 1, 5, 1, 1], [3, 5, 1, 2, 1]]}
#solvePuzzle(testPuzzle4)
# 2.81 seconds

# YELLOW SUBMARINE
testPuzzle5 = {"horizontalClues": [[20,1,15],[21,1,16],[21,1,14],[19,15],[20,15],[20,15],[40],[16,14],[3,14,2,13],[1,12,4,8],[1,10,4,1,1],[1,1,1,1,9,2],[3,1,1,1,2],[3,9,2,2,2,1],[6,1,2,2,2,2],[5,2,1,2,2,2,3],[5,1,2,2,2,5,3],[5,2,1,1,1,4],[16,5,1,1,5],[17,1,1,1,1,6]], "verticalClues": [[7,1,1,6],[7,1,1,6],[7,1,1,6],[8,3,6],[9,6],[9,1,2],[10,1,3],[10,1,3],[11,2],[13,2],[11,1,2],[11,1,2],[11,1,2],[13,2],[11,5],[13,1,2],[11,1,1],[11,1,2],[8,1,2],[3,3,1],[2,1,2,1,2],[1,3,1,2],[3,1,3,1,2],[1,2,1,2,1],[1,1,2,2,1],[2,4,2,1],[8,1,2,2],[9,1,2],[9,1,4],[9,1,2,1],[9,1,2,1],[9,1,1],[10,1,2,4],[10,1,2],[11,1],[10,2],[10,1,3],[10,1,5],[10,6],[11,7]]}
# solvePuzzle(testPuzzle5)
# 34.01 seconds

# FISH
testPuzzle6 = {"horizontalClues": [[3,3,2],[1,1,3,2,2],[1,2,1,3,2,2],[1,1,1,1,4,2,3,1],[1,3,1,4,1,3],[1,1,2,6,2,1],[3,1,3,6,3],[4,2,6,1,1],[3,2,2,1,8,2,1],[1,2,2,5,9,1,3],[1,3,6,13,3],[5,3,3,4,4,2,1],[3,2,2,3,2,3,9],[2,2,1,2,1,3,5,5],[2,3,4,3,3,6,1,2],[2,6,2,4,2,8,2,1],[7,5,2,10],[12,5,5,2,2],[3,8,5,7,2,1],[1,1,2,3,3,6,1,3],[1,2,1,5,12,1,1],[1,2,5,10,1],[1,2,3,1,10,3,2],[2,1,2,1,2,1,2,5,1,1],[1,1,1,1,6,4,3,1,2],[3,2,2,5,4,2,1],[1,1,1,2,5,2,1,2],[3,1,2,1,4,1,2,2],[2,1,1,3,1,1,1],[1,1,2,3,1,1]], "verticalClues": [[3,3,3],[3,1,2,2,1,3,1,1],[1,1,1,3,2,3,3,2],[1,2,1,5,1,1,2],[1,1,1,1,3,2,1,5],[1,3,1,3,3,3],[1,1,4,2,1],[3,6,2,2,1],[9,1,2,1,1],[3,5,2,1,1],[3,2,5,1,1],[3,4,2,2,2],[5,1,1,2,2,5],[3,1,3,2,3,2,5],[2,7,4,3,5],[3,4,7,1,2,6],[3,2,2,6,2,8],[3,1,5,3,5,3,1],[2,1,3,4,2,3],[1,2,2,5,2,2,4],[2,7,3,2,5],[2,1,6,3,3,3,2],[1,3,5,2,3,4,2],[3,5,1,1,5,2],[1,2,4,9,1,1],[3,15,2],[1,1,14,2],[3,12,3,2],[1,1,9,3,1,1],[3,1,3,3,1,1,1],[3,2,4],[9,3],[2,2,2,2,1,3],[2,3,2,1,3,2],[2,1,3,4,3]]}
# solvePuzzle(testPuzzle6)
# 55.40 seconds

# OWL
testPuzzle7 = {"horizontalClues": [[2,9,3],[1,7,9,3],[5,2,1,1,1,2,2],[1,1,4,1,1,4,1],[3,2,5,1,5,1],[1,5,2,4,2,1],[2,6,2,5,2,1],[7,1,6,7],[5,3,3,4,4,3],[1,3,6,3,2],[2,2,5,1,1,1,1],[2,2,5,1,1,2],[3,4,1,1,1,1,1],[3,1,4,2,1,1,2,1],[2,2,4,3,1,1,1,3,1],[10,2,1,1,1,1,2,1],[10,3,1,1,1,3,1],[10,2,1,1,1,1,2,1],[10,3,1,1,1,3,1],[10,5,1,1,5,1],[7,2,2,3,1,3,2,2],[5,4,1,7,1,1],[1,7,1,7,1,2],[3,9,1,4,2,2],[4,12,7],[6,7,6,3],[8,2,3],[2,1,1,1,2,1,1,1,3],[4,14,2],[11]], "verticalClues": [[2,3,13,3,2],[1,3,12,3,2],[3,2,7,3,2],[5,9,2,3],[5,9,1,1,1,1],[1,2,6,2,2,1],[1,1,2,12,3,1,1],[2,3,12,4,1,1],[4,2,12,6,1],[3,2,19,1],[3,4,3,7,1],[7,2,5],[3,2,3,6],[2,6,11,1,2,1],[1,6,7,3,2],[4,2,1,1,1,3,1,1],[1,2,2,1,1,1,4,2,2],[2,1,3,1,1,1,6,1],[1,1,2,2,1,1,1,3,4],[2,3,2,1,1,1,4,4],[1,1,2,2,1,1,1,5,1],[2,5,1,1,1,3,2,2],[1,2,2,1,1,1,4,1,1],[4,2,1,1,1,3,3,2],[1,6,7,3,1],[2,6,11,1,5],[3,2,3,2,1],[9,2,2],[3,3,2],[10,2]]}
# solvePuzzle(testPuzzle7)
# 8.71 seconds

# ZEBRA
testPuzzle8 = {"horizontalClues": [[2,5],[6,1,2],[2,1,1,1,2],[1,4,1,2],[1,1,1,5,1,2],[3,2,1,1,1],[1,1,1,2,2,1],[1,3,2,2,2,1],[1,1,1,2,2,1],[1,2,3,1],[2,1,3,2],[1,3,1,1,3,2],[1,1,1,1,2,3],[2,1,1,2,2],[1,1,1,1,2,1],[1,2,2,1,1],[1,2,1,1,1,2,2],[2,5,1,1],[3,1,1,1,2,2],[3,1,2,2],[1,4,1,2,1],[1,3,2,1],[5,2,2],[3,2],[6]], "verticalClues": [[3],[2,5],[2,2,11,2],[2,1,2,1,1,7],[2,3,4],[1,1,1,1,1,1,3],[1,1,2,2,1,1],[1,1,3,1,2,1],[6,2,4],[1,4,4,1],[1,1,2,2],[1,1,3,1],[8,4],[1,10,2],[1,5,2,1,1],[1,6,3,2,1],[6,3,2,1],[1,4,2,2],[1,4,4,3],[7,1,3,1,3,1]]}
# solvePuzzle(testPuzzle8)
#  seconds

# BIRD
testPuzzle8 = {"horizontalClues": [[7],[12],[9,2,3],[8,1,2,5],[9,2,10],[11,7],[19],[12,5,1],[10,1,4,1],[9,7,2],[21],[6,12],[5,13],[4,4,10],[5,5,1,2,3],[3,4,1,1,1,2],[6,4,1,2],[4,6,2,4],[3,5,10],[4,17],[4,18],[3,12,6],[2,14,4],[2,5,3,1,2,2,1],[7,3],[3,3,2],[3,2,2],[2,5,2],[5,3,2],[1,2,4],[5,6],[1,3,1,3],[1,2],[1,3],[2,4],[23],[18,12],[14,1,1,2,6],[4,4,1,1,1,4],[2,2,1,1]], "verticalClues": [[3,2],[3,2],[2,1,2],[2,1,2],[2,2,2],[2,2,2],[9,2],[7,2,1,2],[8,3,2,2],[9,2,1,2],[8,3,2,2],[7,1,2,2,2,1],[8,1,2,10],[7,2,1,5],[7,3,1,4],[8,4,2,4],[8,5,1,2],[9,2,6,2,2],[9,11,1,2],[22,2,2],[8,13,1,2],[8,5,8,2,2],[8,4,1,1,5,3,1],[8,5,5,1,1,1],[3,2,6,4,2,2,1],[3,1,2,7,3,2,4],[2,2,8,5,2,6],[3,17,1,2,4],[14,8,6],[1,6,4,6,1,2],[2,3,6,8,3],[8,11,4],[4,8,2],[3,2],[2,3],[2,2],[1,3],[1,3],[2],[3]]}
# solvePuzzle(testPuzzle8)
#  seconds


if exportGif:
    frames[0].save(os.path.join(current_directory, filename + '.gif'), format="GIF", append_images=frames, save_all=True, duration=300, loop=0)


t1 = time.time()
print(t1-t0)
