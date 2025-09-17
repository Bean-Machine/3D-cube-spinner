from tkinter import *
import math

# Canvas properties
canvasSize = 600
upperLeft = (0, 0)
upperRight = (canvasSize, 0)
lowerLeft = (0, canvasSize)
lowerRight = (canvasSize, canvasSize)
vPoint = [canvasSize/2, canvasSize/2]                   # the 2D vanishing point for the 3D perspective
lightSource = [4*canvasSize/6, 0, canvasSize/2]       # the position of the light source in 3D
# Cube properties:
cubeSize = canvasSize / 4
cubeCenter = [canvasSize/2, canvasSize/2, canvasSize/2]
cubeSpeed = 2
cubeRotateAccel = 0.0004
cubeRotateDecel = cubeRotateAccel / 2
cubeRotateSpeedMax = 0.04
cubeRotateSpeedX, cubeRotateSpeedY, cubeRotateSpeedZ = [0] * 3
# Fish eye effect properties:
fishEye = 1
fishEyeSpeed = 0.02
fishEyeMin, fishEyeMax = 1, 4
# Key inputs:
leftKey, rightKey, upKey, downKey, sKey, wKey, aKey, dKey, eKey, qKey, zKey, xKey = [False] * 12

pi = math.pi
floatErrorFactor = 1000000000000

def keyOn(event):
    global leftKey, rightKey, upKey, downKey, qKey, eKey, wKey, sKey, aKey, dKey, zKey, xKey
    k = event.keysym
    if k == "Left": leftKey = True
    if k == "Right": rightKey = True
    if k == "Up": upKey = True
    if k == "Down": downKey = True
    if k == "q": qKey = True
    if k == "e": eKey = True
    if k == "w": wKey = True
    if k == "s": sKey = True
    if k == "a": aKey = True
    if k == "d": dKey = True
    if k == "z": zKey = True
    if k == "x": xKey = True
def keyOff(event):
    global leftKey, rightKey, upKey, downKey, qKey, eKey, wKey, sKey, aKey, dKey, zKey, xKey
    k = event.keysym
    if k == "Left": leftKey = False
    if k == "Right": rightKey = False
    if k == "Up": upKey = False
    if k == "Down": downKey = False
    if k == "q": qKey = False
    if k == "e": eKey = False
    if k == "w": wKey = False
    if k == "s": sKey = False
    if k == "a": aKey = False
    if k == "d": dKey = False
    if k == "z": zKey = False
    if k == "x": xKey = False

def convert3DCoords(x, y, z):
    global fishEye
    lineX = x - vPoint[0]
    lineY = y - vPoint[1]
    z = (z / canvasSize) + 1
    zFactor = 1 / (z ** fishEye)
    x = vPoint[0] + (lineX * zFactor)
    y = vPoint[1] + (lineY * zFactor)
    return x, y

def matrixMultiply(mat1, mat2):
    m1rows = len(mat1)               # matrix 1 rows
    m2rows = len(mat2)               # matrix 2 rows
    m1cols = len(mat1[0])            # matrix 1 columns
    m2cols = len(mat2[0])            # matrix 2 columns
    if m1cols != m2rows:
        return None                  # return None if matrices cannot be multiplied
    output = []
    for i in range(m1rows):
        newRow = []
        for j in range(m2cols):
            newNumber = 0
            for k in range(m2rows):
                 newNumber += mat1[i][k] * mat2[k][j]
            newRow.append(newNumber)
        output.append(newRow)
    return output

def rotateX(point, pivotPoint, angle):
    for i in range(3):
        point[i] -= pivotPoint[i]           # move the point relative to the origin before rotating it
    point = [point]                         # give the point an extra list wrapper, turning it into a matrix
    cos = math.cos(angle)
    sin = math.sin(angle)
    xRotation = ((1, 0, 0),
                 (0, cos, sin),
                 (0, -sin, cos))
    point = matrixMultiply(point, xRotation)
    point = point[0]                        # strip away the list wrapper
    for i in range(3):
        point[i] += pivotPoint[i]           # move the point back relative to the point of rotation
    return point

def rotateY(point, pivotPoint, angle):
    for i in range(3):
        point[i] -= pivotPoint[i]           # move the point relative to the origin before rotating it
    point = [point]                         # give the point an extra list wrapper, turning it into a matrix
    cos = math.cos(angle)
    sin = math.sin(angle)
    yRotation = ((cos, 0, sin),
                 (0, 1, 0),
                 (-sin, 0, cos))
    point = matrixMultiply(point, yRotation)
    point = point[0]                        # strip away the list wrapper
    for i in range(3):
        point[i] += pivotPoint[i]           # move the point back relative to the point of rotation
    return point

def rotateZ(point, pivotPoint, angle):
    for i in range(3):
        point[i] -= pivotPoint[i]           # move the point relative to the origin before rotating it
    point = [point]                         # give the point an extra list wrapper, turning it into a matrix
    cos = math.cos(angle)
    sin = math.sin(angle)
    zRotation = ((cos, sin, 0),
                 (-sin, cos, 0),
                 (0, 0, 1))
    point = matrixMultiply(point, zRotation)
    point = point[0]                        # strip away the list wrapper
    for i in range(3):
        point[i] += pivotPoint[i]           # move the point back relative to the point of rotation
    return point

def crossProduct(v1, v2):
    return [v1[1]*v2[2] - v2[1]*v1[2],
            v1[2]*v2[0] - v2[2]*v1[0],
            v1[0]*v2[1] - v2[0]*v1[1]]

def angleBetweenVectors(v1, v2):
    x1, y1, z1 = v1[0], v1[1], v1[2]
    x2, y2, z2 = v2[0], v2[1], v2[2]
    temp = ((x1*x2 + y1*y2 + z1*z2) /
            (((x1*x1 + y1*y1 + z1*z1) ** 0.5) *
            ((x2*x2 + y2*y2 + z2*z2) ** 0.5)))
    temp = round(temp * floatErrorFactor) / floatErrorFactor
    angle = math.acos(temp)
    return angle

def calculateLightValue(face):
    # Calculate the centre point of the face
    noOfPoints = len(face)
    faceCenter = [0, 0, 0]
    for i in face:
        for j in range(3):
            faceCenter[j] += cubePoints[i][j]
    for i in range(3):
        faceCenter[i] /= noOfPoints
    p1, p2 = cubePoints[face[0]], cubePoints[face[1]]
    vector1 = [p1[0] - faceCenter[0], p1[1] - faceCenter[1], p1[2] - faceCenter[2]]
    vector2 = [p2[0] - faceCenter[0], p2[1] - faceCenter[1], p2[2] - faceCenter[2]]
    faceNormal = crossProduct(vector2, vector1)
    lightVector = [lightSource[0] - faceCenter[0], lightSource[1] - faceCenter[1], lightSource[2] - faceCenter[2]]
    return angleBetweenVectors(faceNormal, lightVector)

def getColour(angle, colour):
    scale = angle / pi
    if colour == "white":
        rgb = 255 - int(scale * 255)
        rgbHex = str(hex(rgb)[2:])
        if rgb < 16:
            rgbHex = "0" + rgbHex
        colourString = "#" + rgbHex + rgbHex + rgbHex
    elif colour == "blue":
        red = 127 - int(scale * 127)
        redHex = hex(red)[2:]
        if red < 16:
            redHex = "0" + redHex
        green = 255 - int(scale * 255)
        greenHex = hex(green)[2:]
        if green < 16:
            greenHex = "0" + greenHex
        colourString = "#" + redHex + greenHex + "ff"
    elif colour == "red":
        red = 255 - int(scale * 127)
        redHex = str(hex(red)[2:])
        if red < 16:
            redHex = "0" + redHex
        gb = 100 - int(scale * 100)
        gbHex = str(hex(gb)[2:])
        if gb < 16:
            gbHex = "0" + gbHex
        colourString = "#" + redHex + gbHex + gbHex
    elif colour == "yellow":
        rg = 255 - int(scale * 255)
        rgHex = str(hex(rg)[2:])
        if rg < 16:
            rgHex = "0" + rgHex
        colourString = "#" + rgHex + rgHex + "00"
    elif colour == "cyan":
        gb = 255 - int(scale * 255)
        gbHex = str(hex(gb)[2:])
        if gb < 16:
            gbHex = "0" + gbHex
        colourString = "#" + "00" + gbHex + gbHex
    elif colour == "magenta":
        rb = 255 - int(scale * 255)
        rbHex = str(hex(rb)[2:])
        if rb < 16:
            rbHex = "0" + rbHex
        colourString = "#" + rbHex + "00" + rbHex
    elif colour == "green":
        green = 255 - int(scale * 127)
        greenHex = str(hex(green)[2:])
        if green < 16:
            greenHex = "0" + greenHex
        rb = 100 - int(scale * 100)
        rbHex = str(hex(rb)[2:])
        if rb < 16:
            rbHex = "0" + rbHex
        colourString = "#" + rbHex + greenHex + rbHex
    return colourString

# Create window and background
window = Tk()
window.title("Cube Spinner")
window.bind("<KeyPress>", keyOn)
window.bind("<KeyRelease>", keyOff)
canvas = Canvas(window, width=canvasSize, height=canvasSize, bg="black")
canvas.pack()

# Initialise the lines of the cube and the 3D space
spaceLines = [0] * 8
for i in range(len(spaceLines)):
    spaceLines[i] = canvas.create_line(0,0,0,0, fill="grey")

# Define cube's initial points
x, y, z = cubeCenter[0], cubeCenter[1], cubeCenter[2]
cubePoints = []
cubePoints.append([x + cubeSize, y - cubeSize, z - cubeSize])       # top right, front
cubePoints.append([x - cubeSize, y - cubeSize, z - cubeSize])       # top left, front
cubePoints.append([x + cubeSize, y + cubeSize, z - cubeSize])       # bottom right, front
cubePoints.append([x - cubeSize, y + cubeSize, z - cubeSize])       # bottom left, front
cubePoints.append([x + cubeSize, y - cubeSize, z + cubeSize])       # top right, back
cubePoints.append([x - cubeSize, y - cubeSize, z + cubeSize])       # top left, back
cubePoints.append([x + cubeSize, y + cubeSize, z + cubeSize])       # bottom right, back
cubePoints.append([x - cubeSize, y + cubeSize, z + cubeSize])       # bottom left, back
# Create an array to store cubePoints' 2D equivalents
cubePoints2D = [[0, 0]] * 8
# Define cube's faces and which points they contain
cubeFaces = [0] * 6                             # List for storing the actual polygons drawn on the canvas
cubeFacePoints = []
cubeFacePoints.append([0, 2, 3, 1])             # Front face, clockwise from top right point
cubeFacePoints.append([4, 5, 7, 6])             # Back face, clockwise from top right point
cubeFacePoints.append([1, 3, 7, 5])             # Left face, clockwise from top left point
cubeFacePoints.append([0, 4, 6, 2])             # Right face, clockwise from top right point
cubeFacePoints.append([0, 1, 5, 4])             # Top face, clockwise from top right point
cubeFacePoints.append([2, 6, 7, 3])             # Bottom face, clockwise from bottom right point

# Define container space's points:
spacePoints = []
spacePoints.append([0, 0, 0])
spacePoints.append([canvasSize, 0, 0])
spacePoints.append([0, canvasSize, 0])
spacePoints.append([canvasSize, canvasSize, 0])
spacePoints.append([0, 0, canvasSize])
spacePoints.append([canvasSize, 0, canvasSize])
spacePoints.append([0, canvasSize, canvasSize])
spacePoints.append([canvasSize, canvasSize, canvasSize])
# Create an array to store spacePoints' 2D equivalents:
spacePoints2D = [[0, 0]] * 8
# Define container space's lines and which points they connect to:
spaceLineConnections = []
spaceLineConnections.append([0, 4])
spaceLineConnections.append([1, 5])
spaceLineConnections.append([2, 6])
spaceLineConnections.append([3, 7])
spaceLineConnections.append([4, 5])
spaceLineConnections.append([4, 6])
spaceLineConnections.append([5, 7])
spaceLineConnections.append([6, 7])


lightSource2D = convert3DCoords(lightSource[0], lightSource[1], lightSource[2])
canvas.create_oval(lightSource2D[0]-6, lightSource2D[1]-6, lightSource2D[0]+6, lightSource2D[1]+6, fill="yellow")


firstPass = True            # allows the Main loop to draw the container space for the first iteration of the loop

# Main loop
while True:
    # Key inputs
    if leftKey:
        cubeRotateSpeedY -= cubeRotateAccel
        cubeRotateSpeedY = max(cubeRotateSpeedY, -cubeRotateSpeedMax)
    if rightKey:
        cubeRotateSpeedY += cubeRotateAccel
        cubeRotateSpeedY = min(cubeRotateSpeedY, cubeRotateSpeedMax)
    elif not (leftKey or rightKey):
        if cubeRotateSpeedY < 0:
            cubeRotateSpeedY += cubeRotateDecel
        else:
            cubeRotateSpeedY -= cubeRotateDecel
        if abs(cubeRotateSpeedY) < 0.001:
            cubeRotateSpeedY = 0
    if upKey:
        cubeRotateSpeedX -= cubeRotateAccel
        cubeRotateSpeedX = max(cubeRotateSpeedX, -cubeRotateSpeedMax)
    if downKey:
        cubeRotateSpeedX += cubeRotateAccel
        cubeRotateSpeedX = min(cubeRotateSpeedX, cubeRotateSpeedMax)
    elif not (upKey or downKey):
        if cubeRotateSpeedX < 0:
            cubeRotateSpeedX += cubeRotateDecel
        else:
            cubeRotateSpeedX -= cubeRotateDecel
        if abs(cubeRotateSpeedX) < 0.001:
            cubeRotateSpeedX = 0
    if qKey:
        cubeRotateSpeedZ -= cubeRotateAccel
        cubeRotateSpeedZ = max(cubeRotateSpeedZ, -cubeRotateSpeedMax)
    if eKey:
        cubeRotateSpeedZ += cubeRotateAccel
        cubeRotateSpeedZ = min(cubeRotateSpeedZ, cubeRotateSpeedMax)
    elif not (qKey or eKey):
        if cubeRotateSpeedZ < 0:
            cubeRotateSpeedZ += cubeRotateDecel
        else:
            cubeRotateSpeedZ -= cubeRotateDecel
        if abs(cubeRotateSpeedZ) < 0.001:
            cubeRotateSpeedZ = 0
    # Move all cube points and cube's center in response to cube being moved
    if wKey:
        cubeCenter[1] -= cubeSpeed
        for point in cubePoints:
            point[1] -= cubeSpeed
    if sKey:
        cubeCenter[1] += cubeSpeed
        for point in cubePoints:
            point[1] += cubeSpeed
    if aKey:
        cubeCenter[0] -= cubeSpeed
        for point in cubePoints:
            point[0] -= cubeSpeed
    if dKey:
        cubeCenter[0] += cubeSpeed
        for point in cubePoints:
            point[0] += cubeSpeed
    # Adjust fisheye lens effect
    if zKey:
        fishEye -= fishEyeSpeed
        fishEye = max(fishEye, fishEyeMin)
    if xKey:
        fishEye += fishEyeSpeed
        fishEye = min(fishEye, fishEyeMax)

    # Process cube's points
    for i in range(len(cubePoints)):
        # Rotate cube in all three axes
        if cubeRotateSpeedX != 0:
            cubePoints[i] = rotateX(cubePoints[i], cubeCenter, cubeRotateSpeedX)
        if cubeRotateSpeedY != 0:
            cubePoints[i] = rotateY(cubePoints[i], cubeCenter, cubeRotateSpeedY)
        if cubeRotateSpeedZ != 0:
            cubePoints[i] = rotateZ(cubePoints[i], cubeCenter, cubeRotateSpeedZ)
        # Convert the cube's points to 2D
        cubePoints2D[i] = convert3DCoords(cubePoints[i][0], cubePoints[i][1], cubePoints[i][2])

    # Redraw faces, in reverse order of closeness to the camera:
    for face in cubeFaces:
        canvas.delete(face)             # delete existing cube faces
    zOrderList = []
    for i in range(len(cubeFacePoints)):
        # Calculate the mean distance (using pythagoras) value for each cube face:
        meanDist = 0
        for j in cubeFacePoints[i]:
            xDist, yDist, zDist = cubePoints[j][0] - vPoint[0], cubePoints[j][1] - vPoint[1], cubePoints[j][2] + (canvasSize / fishEye)
            meanDist += (xDist*xDist + yDist*yDist + zDist*zDist) ** 0.5
        meanDist /= len(cubeFacePoints[i])
        zOrderList.append([meanDist, i])        # add the face's mean distance value to the list, plus the face index
    zOrderList.sort(reverse=True)               # sort the list by the distance values for each face, from back to front
    for i in range(len(zOrderList)):            # strip the distance value from each face, leaving just the index
        zOrderList[i] = zOrderList[i][1]
    # Draw each cube face, from back to front, specified by the order of the zOrderList:
    for i in zOrderList:
        points = cubeFacePoints[i]
        points2D = []
        for j in range(len(points)):
            point = cubePoints[points[j]]
            point = convert3DCoords(point[0], point[1], point[2])
            points2D.append(point)
        lightAngle = calculateLightValue(points)
        colours = ("cyan", "magenta", "yellow", "yellow", "white", "white")
        colour = getColour(lightAngle, colours[i])
        cubeFaces[i] = canvas.create_polygon(points2D[0][0],points2D[0][1],points2D[1][0],points2D[1][1],
                              points2D[2][0],points2D[2][1],points2D[3][0],points2D[3][1],
                              fill=colour, outline="black")

    # Define the container frame points in 3D and covert them to 2D
    #   (code appears here, in case of changes to fish eye effect)
    if zKey or xKey or firstPass:
        # Convert the cube's points to 2D:
        for i in range(len(spacePoints)):
            spacePoints2D[i] = convert3DCoords(spacePoints[i][0], spacePoints[i][1], spacePoints[i][2])
        # Draw space's lines:
        for i in range(len(spaceLines)):
            p1, p2 = spaceLineConnections[i][0], spaceLineConnections[i][1]
            canvas.coords(spaceLines[i], spacePoints2D[p1][0], spacePoints2D[p1][1], spacePoints2D[p2][0], spacePoints2D[p2][1])

    firstPass = False
    window.update()

window.mainloop()