from random import randrange
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
        
    def getNeighbours(self,tileX,tileY):
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
    def getTileChar(self,number):
        return "." if number==0 else "#" if number==-1 else str(number)
    def openTile(self,x,y)->bool:
        """
    @return True if succesfull
    """
        assert len(self.tilesToOpen)==0
        self.tilesToOpen=[(x,y)]
        if self.isBomb[x][y]:
                return False
        while len(self.tilesToOpen)!=0:
            x,y = self.tilesToOpen.pop()
            self.board[x][y]=self.countBombs(x,y)
            if self.board[x][y]==0:
                for x,y in self.getNeighbours(x,y):
                    if self.board[x][y]==-1:#not visited yet
                        self.tilesToOpen.append((x,y))
            
        return True
    
    def countBombs(self,tileX,tileY):
        counter = 0
        for x,y in self.getNeighbours(tileX,tileY):
            if self.isBomb[x][y]:
                counter+=1
        return counter
        
