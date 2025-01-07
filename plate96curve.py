"""
    author:lizhaoyang
    data:20250102
"""
import math,os,string,csv
import matplotlib.pyplot as plt

class Plate:
    rowLabels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    mapPositions = {"position1D":0,"position2D":1,"wellID":2}
    def __init__(self,id,rows,columns):
        self.id = id
        self.rows = rows
        self.columns = columns
        self.size = self.rows * self.columns
        self.validate = {}
        self.data = {}
        for key in Plate.mapPositions:
            self.validate[key] = []
        for n in range(1,self.size + 1):
            self.data[n] = {}
            m = self.map(n,check=False)
            for key in Plate.mapPositions:
                self.validate[key].append(m[Plate.mapPositions[key]])

    def map(self,loc,check=True):
        if type(loc) == type(15):
            if check:
                if not loc in self.validate["position1D"]:
                    raise Exception("Invalid 1D Plate Position: %s" %str(loc))
            row = int(math.ceil(float(loc)/float(self.columns))) - 1
            col = loc - (row * self.columns) - 1

        elif type(loc) == type((3,2)):
            if check:
                if not loc in self.validate["position2D"]:
                    raise Exception("Invalid 2D Plate Position: %s" %str(loc))
            row = loc[0] - 1
            col = loc[1] - 1
        elif type(loc) == type("A07"):
            if check:
                if not loc in self.validate["wellID"]:
                    raise Exception("Invalid Well ID: %s" %str(loc))
            row = Plate.rowLabels.index(loc[0])
            col = int(loc[1:]) - 1
        else:
            raise Exception("Unrecognized Plate Location Type: %s" %str(loc))
        pos = self.columns * row + col + 1
        id = "%s%02d" % (Plate.rowLabels[row],col + 1)
        return (pos,(row + 1,col + 1),id)

    def set(self,loc,propertyName,value):
        m = self.map(loc)
        pos = m[Plate.mapPositions["position1D"]]
        self.data[pos][propertyName] = value

    def get(self,loc,propertyName):
        m = self.map(loc)
        pos = m[Plate.mapPositions["position1D"]]
        if propertyName in self.data[pos]:
            return self.data[pos][propertyName]
        else:
            return
    def reaCSV(self,filePath,propertyName):
        try:
            nWell = 1
            with open(filePath,mode="r") as csvFile:
                csvReader = csv.reader(csvFile)
                for row in csvReader:
                    for wellData in row:
                        self.set(nWell,propertyName,float(wellData))
                        nWell += 1
        except:
            print("CSV data could not be correctly read from: $S"%filePath)
            return
        return
    def getRow(self,loc):
        here = self.map(loc)
        row = []
        for n in range(0,self.size):
            there = self.map(n+1)
            if there[1][0] == here[1][0]:
                row.append(there)
        return row
    def getColumn(self,loc):
        here = self.map(loc)
        col = []
        for n in range(0,self.size):
            there = self.map(n+1)
            if there[1][1] == here[1][1]:
                col.append(there)
        return col
    def average(self,propertyName,loc=None):
        if loc == None:
            total = 0.0
            for pos in range(0,self.size):
                total += self.get(pos+1,propertyName)
            return total/self.size
        row = self.getRow(loc)
        col = self.getColumn(loc)
        rowTotal = 0.0
        colTotal = 0.0
        for pos in row:
            rowTotal += self.get(pos[1],propertyName)
        rowMean = rowTotal / self.columns
        for pos in row:
            colTotal += self.get(pos[1],propertyName)
        colMean = colTotal / self.rows
        return (rowMean,colMean)
    def definePhysicalMap(self,width,height,xBorder,yBorder,diameter,pitch,
                          stepsize):
        self.width = width
        self.height = height
        self.xBorder = xBorder
        self.yBorder = yBorder
        self.diameter = diameter
        self.pitch = pitch
        self.stepzize = stepsize
        self.xwells = []
        self.ywells = []
        xpos = self.xBorder + self.yBorder / 2.0
        for nx in range(0,self.columns):
            self.xwells.append(xpos)
            xpos += self.pitch
        ypos = -self.yBorder - self.diameter / 2.0
        for ny in range(0,self.rows):
            self.ywells.append(ypos)
            ypos -= self.pitch
        self.initializePlateHead()
        self.setPlotCurrentPosition()
    def initializePlatePosition(self):
        self.x = 0
        self.y = 0
    def setPlotCurrentPosition(self,status=False,color='yellow'):
        self.plotCurrentPosition = status
        self.currentPositionColor = color
    def mapWell(self,loc):
        m = self.map(loc)[Plate.mapPositions['position2D']]
        xpos = self.xwells[m[1] - 1]
        ypos = self.ywells[m[0] - 1]
        return (xpos,ypos)

    def moveTo(self,loc):
        pos = self.mapWell(loc)
        stepsPerUnit = 1.0 / self.stepzize
        newx = int(round(pos[0] * stepsPerUnit))
        newy = int(round(pos[1] * stepsPerUnit))
        xshift = newx - self.x
        yshift = newy - self.y
        self.x += xshift
        self.y += yshift
        return (xshift,yshift)
    def createColorMap(self,propertyName,loColor=(1.0,1.0,1.0),
                       hiColor=(1.0,0.0,0.0),propertyRange=(0.0,100.0)):
        self.colorMap = []
        pRange = propertyRange[1] - propertyRange[0]
        rRange = hiColor[0] - loColor[0]
        gRange = hiColor[1] - hiColor[1]
        bRange = hiColor[2] - hiColor[2]

        for n in range(0,self.size):
            p = self.get(n+1,propertyName)
            scaledP = (p - propertyRange[0]) / pRange
            r = loColor[0] + (scaledP * rRange)
            if r < 0.0 : r = 0.0
            if r > 1.0 : r = 1.0
            g = loColor[1] + (scaledP * gRange)
            if g < 0.0 : g = 0.0
            if g > 0.0 : g = 1.0
            b = loColor[2] + (scaledP * bRange)
            if b < 0.0 : b = 0.0
            if b > 0.0 : b = 1.0
            self.colorMap.append((r,g,b))
        return
    def plotPlate(self,figWidth=4.0,figHeight=3.0,dpi=200,rowlabelOffset=3.0,
                  columnLabelOffset=2.0,fontSize=None):
        if self.width == None:
            return
        wellColor = 'w'
        plt.figure(figsize=(figWidth,figHeight),dpi=dpi)
        plt.axes()
        plt.axis('off')
        if fontSize == None:
            fontSize = figHeight * 3
        #outline = plt.Rectangle((0,0),self.width,-self.height,fc="gray")
        #plt.gca().add_patch(outline)

        npos = -1
        leftText = self.xwells[0] - (self.diameter * rowlabelOffset)
        topText = self.ywells[0] + (self.diameter * columnLabelOffset)
        for yw in self.ywells:
            ymap = self.map(npos + 2)
            letter = ymap[2][0]

def main():
    p = Plate("Assay42",8,12)
    print(p.map((1,2)))


if __name__ == "__main__":
    main()