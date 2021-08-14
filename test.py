import main

# print(main.MineField(2,3,4).board)
mf = main.MineField(40,10,bombs=50)
mf.openTile(0,0)
# print(mf.board)
print(mf.getBoard())