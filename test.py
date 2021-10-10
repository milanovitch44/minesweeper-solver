import main
import unittest
import queue

# print(main.MineField(2,3,4).board)


class testEngine(unittest.TestCase):
    def test_engine(self):
        mf = main.MineField(50, 10, bombs=100)
        mf.openTile((2, 2))

        e = main.Engine(mf)
        while True:
            # print(mf.getBoard())
            fc = e.getNextTile(mf)
            # print(str(fc))

            realValue = mf.isBomb[fc.coordinates[0]][fc.coordinates[1]]
            assert realValue == fc.isBomb
            mf.board[fc.coordinates[0]][fc.coordinates[1]] = (
                -2 if fc.isBomb else mf.countBombs(fc.coordinates)
            )
            e = main.Engine(mf)  # hard reload

    def test_flood_fill(self):
        mf = main.MineField(50, 10, bombs=30)
        mf.openTile((0, 0))
        print(mf.getBoard())


testEngine().test_engine()
# print(mf.board)

# print(list(main.Engine().calculateEdgeTiles(mf)))
# e = main.Engine()
# print(r:=e.isValid(mf,[main.fieldChange(True,(1,0)),main.fieldChange(False,(0,0))]))
# print(", ".join([str(el) for el in r[(0,1)]]))
