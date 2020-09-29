# This script takes images from a file, 
# determines the best way to lay them out on a given page given their size and the dimensions,
# and then places them on this page for printing

#Modules
import os
from PIL import Image

#Variables:
#Names
imgPath = "" #String path to the folder containing the images
outputName = "" #String for what to name the output file
#Dimension calculations
numImages = 0 #The total number of images in the file
allFactors = [] #All factors of the number of images
coFactors = []  #Groups of factors of the number of images
bestCoFactors = [] #The best cofactors by which to gorup the images
incompRow = 0  #The number of images to place on an incomplete row
pageDims = [0, 0]   #The dimensions of the page to print the images to
pageResolution = 240    #Resolution of the page to print to convert from size to pixels
imgMargin = 20  #Space between images
subImages = []  #Holds the separate images imported from the folder
cellDims = [0, 0]   #Holds the max space each image can take on the page
imgPos = [] #Holds the coordinates for each image to appear on the page

#Functions
#Finds all factors of a number
def FindFactors(_keyNum):
    _facList = []   #Stores factors of the number
    #Loop through all numbers less than the key number to determine if they are factors
    for _fac in range(1, _keyNum + 1):
        if(_keyNum % _fac == 0):
            _facList.append(_fac)
    return _facList

#Groups all cofactors of a number together from a factor list
def GroupCoFactors(_facList):
    _coFacList = []
    for i in range(0, len(_facList)):
        _coFacList.append([])
        _coFacList[i].append(_facList[i])
        _coFacList[i].append(_facList[-(i + 1)])
    return _coFacList

#Find the 2 cofactors of the number of images that best match the ratio of the dimensions of the page
def FindBestCoFactors(_coFacList):
    _bestCoFacs = [_coFacList[0][0], _coFacList[0][1]]
    global pageDims
    _bestRatio = abs((_coFacList[0][0] / _coFacList[0][1]) - (pageDims[0] / pageDims[1]))
    _newRatio = 0
    for i in range(0, len(_coFacList)):
        _newRatio = abs((_coFacList[i][0] / _coFacList[i][1]) - (pageDims[0] / pageDims[1]))
        if(_newRatio < _bestRatio):
            _bestRatio = _newRatio
            _bestCoFacs = [_coFacList[i][0], _coFacList[i][1]]
    return _bestCoFacs

#Deal with numbers that have poor factors, e.g. prime numbers
def ReSortPhotos(_keyNum, _bestCoFacs):
    _excessPhotos = 0
    while(_bestCoFacs[0] < pageDims[0] / 3 and _bestCoFacs[1] > pageDims [1] / 3):
        _keyNum -= 1
        _excessPhotos += 1
        _bestCoFacs = FindBestCoFactors(GroupCoFactors(FindFactors(_keyNum)))
    global bestCoFactors 
    bestCoFactors = _bestCoFacs
    return _excessPhotos

#Actual script
#Get the dimensions of the page to print
pageDims[0] = float(input('Input the X dimension of the page: '))
pageDims[1] = float(input('Input the Y dimension of the page: '))
#Get the path to the image folder
imgPath = str(input('Enter the path to the folder containing the images: '))
#Get the output name of the file
outputName = str(input('Enter what you would like the file to be named. Do not include extension: '))

#Import images
for _img in os.listdir(imgPath):
    if(not _img.endswith(".jpg") and not _img.endswith(".JPG") and not _img.endswith(".jpeg") and not _img.endswith(".JPEG")):
        continue
    else:
        subImages.append(Image.open(imgPath + "\\" + _img))

numImages = len(subImages)

#Determine the best layout for the images
if(numImages < 2):
    bestCoFactors = [1, 1]
else:
    allFactors = FindFactors(numImages)
    coFactors = GroupCoFactors(allFactors)
    bestCoFactors = FindBestCoFactors(coFactors)
    if(bestCoFactors[0] < 3 and bestCoFactors[1] > 3):
        incompRow = ReSortPhotos(numImages, bestCoFactors)

#Determine the size of each cell
cellDims[0] = (pageDims[0] * pageResolution) / bestCoFactors[0]
if(incompRow == 0):
    cellDims[1] = (pageDims[1] * pageResolution) / bestCoFactors[1]
else:
    cellDims[1] = (pageDims[1] * pageResolution) / (bestCoFactors[1] + 1)

#Resize each image to fit it's cell
for i in range(0, len(subImages)):
    #Resize relative to the long axis to ensure it fits
    #Figure out if by decreaing X axis Y axis will overflow
    if(int(subImages[i].size[1] * ((int(cellDims[0] - (2 * imgMargin))) / subImages[i].size[0])) * bestCoFactors[1] < pageDims[1]):
        _newXDim = int(cellDims[0] - (2 * imgMargin))
        _newYDim = int(subImages[i].size[1] * (_newXDim / subImages[i].size[0]))
        subImages[i] = subImages[i].resize ((_newXDim, _newYDim))
    else:
        _newYDim = int(cellDims[1] - (4 * imgMargin))
        _newXDim = int(subImages[i].size[0] * (_newYDim / subImages[i].size[1]))
        subImages[i] = subImages[i].resize((_newXDim, _newYDim))

#Make a page and place all the images on it
outputImg = Image.new('RGB', (int(pageDims[0] * pageResolution), int(pageDims[1] * pageResolution)), color = (255, 255, 255))
#First make a list that contains the coordinates for each
for x in range(0, bestCoFactors[0]):
    for y in range(0, bestCoFactors[1]):
        imgPos.append((int((cellDims[0] * x) + imgMargin), int((cellDims[1] * y) + imgMargin)))

#Add the incomplete row if there is one
if(incompRow != 0):
    for i in range(0, incompRow):
        imgPos.append((int ((cellDims[0] * i) + imgMargin), int((cellDims[1] * bestCoFactors[1]) + imgMargin)))

#Actually paste the images onto the page
for i in range(0, len(subImages)):
    outputImg.paste(subImages[i], (imgPos[i]))

#Save the image
outputImg.save(imgPath + "\\" + outputName + ".jpg")

input('DONE! Press Enter to quit...')