from random import randrange

class MineField:
    def __init__(self,width,height,bombs) -> None:
        self.board=[[-1]*height for _ in range(width)]
        self.isBomb = [[False]*height for _ in range(width)]

        while bombs!=0:
            x,y = randrange(0,width),randrange(0,height)
            if not self.isBomb[x][y]:
                bombs-=1
                self.isBomb[x][y]=True
        
