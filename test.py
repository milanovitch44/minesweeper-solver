import main
import unittest
# print(main.MineField(2,3,4).board)

class testEngine(unittest.TestCase):
    def test_engine(self):
        mf = main.MineField(50,10,bombs=20)
        mf.openTile((3,3))
        print(mf.getBoard())
        e=main.Engine(mf)
        print(e.getNextTile(mf))

# print(mf.board)

# print(list(main.Engine().calculateEdgeTiles(mf)))
# e = main.Engine()
# print(r:=e.isValid(mf,[main.fieldChange(True,(1,0)),main.fieldChange(False,(0,0))]))
# print(", ".join([str(el) for el in r[(0,1)]]))