import main
import unittest
import queue
import time

# print(main.MineField(2,3,4).board)


class testEngine(unittest.TestCase):
    def test_engine(self):
        mf = main.MineField(50, 10, bombs=100)
        print(mf.openTile((2, 2), False))
        print(".")

        while True:
            e = main.Engine(mf)  # hard reset
            print(mf.getBoard())
            fc = e.getNextTile(mf)
            print(str(fc))
            assert mf.openTile(fc.coordinate, fc.isBomb)
            # time.sleep(0.1)

    def test_flood_fill(self):
        mf = main.MineField(50, 10, bombs=30)
        mf.openTile((0, 0))
        print(mf.getBoard())


testEngine().test_engine()
print("done")
# print(mf.board)

# print(list(main.Engine().calculateEdgeTiles(mf)))
# e = main.Engine()
# print(r:=e.isValid(mf,[main.fieldChange(True,(1,0)),main.fieldChange(False,(0,0))]))
# print(", ".join([str(el) for el in r[(0,1)]]))
