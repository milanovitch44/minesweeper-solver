import queue
from random import random, randrange
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
            if not self.isBomb[x][y] and (x,y)!=(0,0):
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

class FieldChange:
    def __init__(self,isBomb,coordinates) -> None:
        self.isBomb=isBomb
        self.coordinates=coordinates
    def __str__(self) -> str:
        return f"fieldChange({self.getType()} on {self.coordinates})"
    getType = lambda self:"flagged bomb" if self.isBomb else "safe spot"
    opposite = lambda self:FieldChange(not(self.isBomb),self.coordinates)

class ParentFieldChange:
    def __init__(self,fieldChanges) -> None:
        self.fieldChanges = fieldChanges
        self.forbiddenChildren:set[fieldChanges] = set()
        self.finished=False

class Engine:
    def __init__(self,field:MineField) -> None:
        self.calculateEdgeTiles(field)
        self.changesToEvaluate:queue.Queue[list[FieldChange]] = queue.Queue()
        self.changesToEvaluate.put([])
        # self.addedToChangesToEvaluate:set[list[FieldChange]] = set()
        self.parentFieldChanges = {}


    def calculateEdgeTiles(self,field:MineField):
        self.unknownEdgeTiles = set()
        # self.knownEdgeTiles = {}
        for x,row in enumerate(field.board):
            for y,el in enumerate(row):
                if field.board[x][y]!=-1:
                    for neighbour in field.getNeighbours((x,y)):
                        if field.getCoordinate(neighbour)==-1:
                            self.unknownEdgeTiles.add(neighbour)
                    # self.knownEdgeTiles[(x,y)] = FieldChange(False,(x,y))
                       
    def isValid(self,field:MineField,changes:list[FieldChange]):
        neighbours = self.getNeighboursOfFieldChange(field,changes)
        for coordinate,changes in neighbours.items():
            # print(f"{coordinate=} {changes=}")
            upperLimit = 0
            lowerLimit = 0
            for neighbour in field.getNeighbours(coordinate):
                
                tileValue = field.getCoordinate(neighbour)
                if tileValue==-1:
                    upperLimit+=1
                elif tileValue==-2:
                    lowerLimit+=1
            for change in changes:
                if change.isBomb:
                    lowerLimit+=1
                else:
                    upperLimit-=1
            surroundingBombs = field.getCoordinate(coordinate)
            # print(f"{lowerLimit}<={surroundingBombs}<={upperLimit}")
            if not(lowerLimit<=surroundingBombs<=upperLimit):
                return False

        return True

    def getNeighboursOfFieldChange(self,field:MineField,changes:list[FieldChange])->dict[list[FieldChange]]:
        neighbours = {}

        for change in changes:
            for neighbour in field.getNeighbours(change.coordinates):
                if field.getCoordinate(neighbour)!=-1:
                    if neighbour in neighbours:
                        neighbours[neighbour].append(change)
                    else:
                        neighbours[neighbour]=[change]
        return neighbours
    def getPossibleChanges(self,field:MineField,changes:list[FieldChange])->set[list]:
        neighbours=set()
        if len(changes)==0:
            return 
        for change in changes:
            for localNeighbour in field.getNeighbours(change.coordinates):
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
    def deepStr(self,changeList):
        return "".join([str(el) for el in changeList])
    # returns right answer or None if unknown
    def helpParent(self,changeList:list[FieldChange],change)->FieldChange:
        oppositeChange = change.opposite()
        if changeList==[]:
            return oppositeChange
        
        parent = self.parentFieldChanges[self.deepStr(changeList)]
        if not parent.finished:
            if oppositeChange in parent.forbiddenChildren:
                parent.finished = True
                for index in range(len(changeList)):
                    parentOfParent = self.parentFieldChanges[self.deepStr(changeList[:index]+changeList[index+1:])]
                        
                    res =  self.helpParent(self,parentOfParent,changeList[index])
                    if res is not None:
                        return res
            else:
                parent.forbiddenChildren.add(change)
        return None
    def getNextTile(self,field:MineField)->FieldChange:
        while self.changesToEvaluate.not_empty:
            changeList = self.changesToEvaluate.get()
            if changeList==[]:# first run
                possibleChanges = self.unknownEdgeTiles
            else:
                possibleChanges = self.getPossibleChanges(field,changeList)
            for possibleChangeCoordinate in possibleChanges:
                for change in (FieldChange(True,possibleChangeCoordinate)
                              ,FieldChange(False,possibleChangeCoordinate)):
                    newChangeList = changeList+[change]
                    if self.isValid(field,newChangeList):
                        
                        self.changesToEvaluate.put(newChangeList)
                            
                    else:
                        result = self.helpParent(changeList,change)
                        
                        if result is not None:
                            return result
            self.parentFieldChanges[self.deepStr(changeList)]=ParentFieldChange(changeList)
            


        return None



    