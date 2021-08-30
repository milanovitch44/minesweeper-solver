from random import randrange
import heapq
import time
class MineField:
    def __init__(self,width,height,bombs) -> None:
        self.board=[[-1]*height for _ in range(width)]
        self.isBomb = [[False]*height for _ in range(width)]
        self.width,self.height = width,height
        self.tilesToOpen = []

        while bombs!=0:
            x,y = randrange(0,width),randrange(0,height)
            if not self.isBomb[x][y]:
                bombs-=1
                self.isBomb[x][y]=True
    def getCoordinate(self,coordinate:list):
        return self.board[coordinate[0]][coordinate[1]]
    def getNeighbours(self,coordinate:list):
        tileX,tileY=coordinate
        out=[]
        for xOffset,yOffset in (
            (-1,-1),(1,-1),(-1,1),(1,1),
            (1,0),(0,1),(-1,0),(0,-1)
                                ):
            x = xOffset+tileX
            y = yOffset+tileY
            if x>=0 and y>=0 and x<self.width and y<self.height:
                out.append((x,y))
        return out

    def getBoard(self)->str:
        return "\t\t"+"\n\t\t".join(["".join(
                [self.getTileChar(self.board[x][y]) for x in range(self.width)]
            ) for y in range(self.height)])

    getTileChar = lambda self,number:"." if number==0 else "#" if number==-1 else str(number)
    def openTile(self,beginCoordinate)->bool:
        """
    @return True if succesfull
    """
        beginX,beginY = beginCoordinate
        assert len(self.tilesToOpen)==0
        self.tilesToOpen=[beginCoordinate]
        if self.isBomb[beginX][beginY]:
            return False
        while len(self.tilesToOpen)!=0:
            
            coordinate = self.tilesToOpen.pop()
            x,y = coordinate
            if self.board[x][y]!=self.countBombs(coordinate):
                print(self.getBoard(),end="\n\n\n\n\n\n",flush=True)
                # time.sleep(0.00001)
            self.board[x][y]=self.countBombs(coordinate)
            
            if self.board[x][y]==0:
                for nextX,nextY in self.getNeighbours(coordinate):
                    if self.board[nextX][nextY]==-1:#not visited yet
                        self.tilesToOpen.append((nextX,nextY))
            
        return True
    
    def countBombs(self,coordinate:list):
        tileX,tileY = coordinate
        counter = 0
        for x,y in self.getNeighbours((tileX,tileY)):
            if self.isBomb[x][y]:
                counter+=1
        return counter

class fieldChange:
    def __init__(self,isBomb,coordinates) -> None:
        self.isBomb=isBomb
        self.coordinates=coordinates
    def __str__(self) -> str:
        return f"fieldChange({self.getType()} on {self.coordinates})"
    getType = lambda self:"flagged bomb" if self.isBomb else "safe spot"

class Engine:
    def __init__(self,field:MineField) -> None:
        self.calculateEdgeTiles(field)
        self.changesToEvaluate:heapq.__heap = [[]]


    def calculateEdgeTiles(self,field:MineField):
        self.unknownEdgeTiles = set()
        self.knownEdgeTiles = {}
        for x,row in enumerate(field.board):
            for y,el in enumerate(row):
                if field.board[x][y]!=-1:
                    for neighbour in field.getNeighbours((x,y)):
                        if field.getCoordinate(neighbour)==-1:
                            self.unknownEdgeTiles.add(neighbour)
                    self.knownEdgeTiles[(x,y)] = fieldChange(False,(x,y))
                       
    def isValid(self,field:MineField,changes:list[fieldChange]):
        neighbours = self.getNeighboursOfFieldChange(field,changes)
        for changes,coordinate in neighbours.items():
            upperLimit = 8
            lowerLimit = 0
            for neighbour in field.getNeighbours(coordinate):
                if neighbour in self.knownEdgeTiles:
                    if self.knownEdgeTiles[neighbour].isBomb:
                        lowerLimit+=1
                    else:
                        upperLimit-=1
            for change in changes:
                if change.isBomb:
                    lowerLimit+=1
                else:
                    upperLimit-=1
            surroundingBombs = field.getCoordinate(coordinate)
            if lowerLimit>surroundingBombs or upperLimit<surroundingBombs:
                return False
        return True

    def getNeighboursOfFieldChange(self,field:MineField,changes:list[fieldChange])->dict[list[fieldChange]]:
        neighbours = {}
        for change in changes:
            for neighbour in field.getNeighbours(change.coordinates):
                if field.getCoordinate(neighbour)!=-1:
                    if neighbour in neighbours:
                        neighbours[neighbour].append(change)
                    else:
                        neighbours[neighbour]=[change]
        return neighbours
    def getPossibleChanges(self,field:MineField,changes:list[fieldChange])->set[list]:
        neighbours=set()
        for change in changes:
            for localNeighbour in field.getNeighbours(change.coordinates):
                if field.getCoordinate(localNeighbour)!=-1:
                    for farNeighbour in field.getNeighbours(localNeighbour):
                        if field.getCoordinate(farNeighbour)==-1:
                            neighbours.add(farNeighbour)

                        # if field.board[neighbour[0]][neighbour[1]]!=-1:
                        #     if neighbour in neighbours:
                        #         neighbours[neighbour].append(change)
                        #     else:
                        #         neighbours[neighbour]=[change]
        # changes = [fieldChange(False,coordinates) for coordinates in ]
        return neighbours
    def getNextTile(self,field:MineField)->fieldChange:
        while len(self.changesToEvaluate)!=0:
            changeList = heapq.heappop(self.changesToEvaluate)
            neighbours = self.getPossibleChanges(field,changeList)
            print(neighbours)
        

        return None



    