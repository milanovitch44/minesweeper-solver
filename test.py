import main

# print(main.MineField(2,3,4).board)
mf = main.MineField(120,37,bombs=200)
mf.openTile((3,3))
print(mf.getBoard())
e=main.Engine(mf)
print(e.getNextTile(mf))
# print(mf.board)

# print(list(main.Engine().calculateEdgeTiles(mf)))
# e = main.Engine()
# print(r:=e.isValid(mf,[main.fieldChange(True,(1,0)),main.fieldChange(False,(0,0))]))
# print(", ".join([str(el) for el in r[(0,1)]]))