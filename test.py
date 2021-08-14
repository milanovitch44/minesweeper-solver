import main

# print(main.MineField(2,3,4).board)
mf = main.MineField(4,4,bombs=1)
print(mf.openTile(0,0))
print(mf.board)
print(mf.getBoard())