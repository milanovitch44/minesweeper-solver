import math
import random
import itertools

rel_table = (
    (-1, -1),
    (1, -1),
    (-1, 1),
    (1, 1),
    (1, 0),
    (0, 1),
    (-1, 0),
    (0, -1),
)


class MineField:
    def __init__(self, width: int, height: int, bombs: int) -> None:
        # random.seed(1)
        self.board = [[-1] * height for _ in range(width)]
        self.isBomb = [[False] * height for _ in range(width)]
        self.width, self.height = width, height
        self.tilesToOpen = []
        while bombs != 0:
            x, y = random.randrange(0, width), math.floor(
                ((random.random() * height) ** 2) / height
            )
            if not self.isBomb[x][y] and (x > 3 or y > 10):
                bombs -= 1
                self.isBomb[x][y] = True

    def getCoordinate(self, coordinate):
        return self.board[coordinate[0]][coordinate[1]]

    def getNeighbours(self, coordinate):
        global rel_table
        tileX, tileY = coordinate
        return (
            (xOffset + tileX, yOffset + tileY)
            for xOffset, yOffset in rel_table
            if (
                xOffset + tileX >= 0
                and yOffset + tileY >= 0
                and xOffset + tileX < self.width
                and yOffset + tileY < self.height
            )
        )

    def __str__(self) -> str:
        return " " + "\n ".join(
            [
                "".join([self.getTileChar(self.board[x][y]) for x in range(self.width)])
                for y in range(self.height)
            ]
        )

    def getTileChar(self, number):
        return (
            "."
            if number == 0
            else "~"
            if number == -1
            else "F"
            if number == -2
            else str(number)
        )

    def openTile(self, beginCoordinate: tuple, guessedBomb: bool) -> bool:
        """
        returns if guess was correct
        """
        beginX, beginY = beginCoordinate
        if self.isBomb[beginX][beginY] != guessedBomb:
            return False
        self.board[beginX][beginY] = (
            -2 if guessedBomb else self.countBombs(beginCoordinate)
        )
        return True

    def countBombs(self, coordinate):
        return sum(self.isBomb[el[0]][el[1]] for el in self.getNeighbours(coordinate))


class FieldChange:
    def __init__(self, isBomb, coordinate):
        self.isBomb = isBomb
        self.coordinate = coordinate

    def getType(self):
        return "flagged bomb" if self.isBomb else "safe spot"

    def opposite(self):
        return FieldChange(not self.isBomb, self.coordinate)

    def __str__(self):
        return f"fieldChange({self.getType()} on {self.coordinate})"


class PossSet:
    def __init__(self, values, counter_values, bomb_diff) -> None:
        self.values: set = values
        self.counter_values: set = counter_values
        self.bomb_diff = bomb_diff

    def simplify(self):
        for i in self.values.copy():
            if i in self.counter_values:
                self.counter_values.remove(i)
                self.values.remove(i)

    def is_solved(self):
        found_counter_bomb = None
        if (
            len(self.counter_values) == -self.bomb_diff
        ):  # all counter bombs is only option
            found_counter_bomb = True
        elif len(self.values) == self.bomb_diff:  # all bombs only option
            found_counter_bomb = False
        if found_counter_bomb is not None:
            if len(self.counter_values) != 0:
                return FieldChange(found_counter_bomb, list(self.counter_values)[0])
            if len(self.values) != 0:
                return FieldChange(not (found_counter_bomb), list(self.values)[0])
                # return PossSet(self.values,set(),)
        return

    def __str__(self) -> str:
        return f"{self.values}-{self.counter_values}={self.bomb_diff}"


class Engine:
    def __init__(self, field: MineField) -> None:
        self.field = field

    def calculateSimpleSets(self, level=-1):
        self.poss_sets = set()
        for x, row in enumerate(self.field.board):
            for y, el in enumerate(row):
                bombs_left = self.field.getCoordinate((x, y))
                if -2 != bombs_left != -1:
                    unknowns = set()
                    for neighbour in self.field.getNeighbours((x, y)):
                        if self.field.getCoordinate(neighbour) == -1:
                            unknowns.add(neighbour)
                        elif self.field.getCoordinate(neighbour) == -2:
                            bombs_left -= 1
                    if len(unknowns):
                        self.poss_sets.add(PossSet(set(), unknowns, -bombs_left))
                        level -= 1
                        if level == 0:
                            return

    def getNextTile(self):
        for pass_ in range(30):
            if pass_ % 3==0:
                self.calculateSimpleSets(30 * 300 ** (pass_ // 3))
            for el in self.poss_sets:
                res = el.is_solved()
                if res is not None:
                    return res
            if pass_ > 0:
                pass
            for x, y in itertools.product(self.poss_sets.copy(), repeat=2):
                if (
                    (
                        len(x.values) == 0
                        or len(y.values) == 0
                        or (
                            abs(next(iter(x.values))[0] - next(iter(y.values))[0]) < 8
                            and abs(next(iter(x.values))[1] - next(iter(y.values))[1])
                            < 8
                        )
                    )
                    and any(
                        (el in y.values or el in y.counter_values)
                        for el in itertools.chain(x.values, x.counter_values)
                    )
                    and x != y
                ):
                    new_ = None
                    if all((el not in y.values for el in x.values)) and all(
                        (el not in y.counter_values for el in x.counter_values)
                    ):
                        new_ = PossSet(
                            x.values | y.values,
                            x.counter_values | y.counter_values,
                            x.bomb_diff + y.bomb_diff,
                        )
                    elif all((el not in y.values for el in x.counter_values)) and all(
                        (el not in y.values for el in x.counter_values)
                    ):
                        new_ = PossSet(
                            x.values | y.counter_values,
                            x.counter_values | y.values,
                            x.bomb_diff - y.bomb_diff,
                        )
                    if new_ is not None:
                        new_.simplify()
                        self.poss_sets.add(new_)
        print(len(self.poss_sets))
        print(self.field)
        print()
        # input(f"30 loops but nothing found, continue: ")
