import main

class testEngine:
    def test_engine(self):
        mf = main.MineField(50, 20, bombs=int((50 * 20) / 6))
        print(mf.openTile((2, 2), False))
        print(".")

        for i in range(1000000000):
            e = main.Engine(mf)  # hard reset
            if i % 15 == 0:
                print()
                print(mf)

            fc = e.getNextTile()

            # print(str(fc))
            assert fc is not None, "impossible to further solve the board"
            assert mf.openTile(fc.coordinate, fc.isBomb), f"Tried {fc}"
            # time.sleep(0.1)
            # input()

    def test_flood_fill(self):
        mf = main.MineField(50, 10, bombs=30)
        # mf.openTile((0, 0))
        print(mf)


testEngine().test_engine()
print("done")
# print(mf.board)

# print(list(main.Engine().calculateEdgeTiles(mf)))
# e = main.Engine()
# print(r:=e.isValid(mf,[main.fieldChange(True,(1,0)),main.fieldChange(False,(0,0))]))
# print(", ".join([str(el) for el in r[(0,1)]]))
