import math as m
import queue
from random import random, randrange
import itertools


class MineField:
    def __init__(self, width: int, height: int, bombs: int) -> None:
        self.board = [[-1] * height for _ in range(width)]
        self.isBomb = [[False] * height for _ in range(width)]
        self.width, self.height = width, height
        self.tilesToOpen = []

        while bombs != 0:
            x, y = randrange(0, width), m.floor(((random() * height) ** 2) / height)
            if not self.isBomb[x][y] and (x > 3 or y > 3):
                bombs -= 1
                self.isBomb[x][y] = True

    def getCoordinate(self, coordinate):
        return self.board[coordinate[0]][coordinate[1]]

    def getNeighbours(self, coordinate):
        tileX, tileY = coordinate
        out = []
        for xOffset, yOffset in (
            (-1, -1),
            (1, -1),
            (-1, 1),
            (1, 1),
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
        ):
            x = xOffset + tileX
            y = yOffset + tileY
            if x >= 0 and y >= 0 and x < self.width and y < self.height:
                out.append((x, y))
        return out

    def getBoard(self) -> str:
        return " " + "\n ".join(
            [
                "".join([self.getTileChar(self.board[x][y]) for x in range(self.width)])
                for y in range(self.height)
            ]
        )

    getTileChar = (
        lambda self, number: "."
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

    countBombs = lambda self, coordinate: sum(
        map(
            lambda coordinate: 1 if self.isBomb[coordinate[0]][coordinate[1]] else 0,
            self.getNeighbours(coordinate),
        )
    )


class FieldChange:
    def __init__(self, isBomb, coordinate) -> None:
        self.isBomb = isBomb
        self.coordinate = coordinate

    def __str__(self) -> str:
        return f"fieldChange({self.getType()} on {self.coordinate})"

    getType = lambda self: "flagged bomb" if self.isBomb else "safe spot"
    opposite = lambda self: FieldChange(not (self.isBomb), self.coordinate)


class ParentFieldChange:
    def __init__(self, fieldChanges) -> None:
        self.fieldChanges = fieldChanges
        self.forbiddenChildren: set[list[FieldChange]] = set()
        self.finished = False


class PossSet:
    def __init__(self, values, counter_values, bomb_diff) -> None:
        self.values: set = values
        self.counter_values: set = counter_values
        self.bomb_diff = bomb_diff
        if self.values == set() == self.counter_values:
            print("!")

    def simplify(self):
        v, cv = self.values.copy(), self.counter_values.copy()
        for i in v:
            if i in cv:
                self.counter_values.remove(i)
                self.values.remove(i)
        # if len(self.values)==0:
        #     self.values = self.counter_values
        #     self.bomb_diff*=-1

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
        self.poss_sets: list[PossSet] = []
        self.calculateEdgeTiles(field)
        self.calculateSimpleSets(field)
        # print("\n".join(str(el) for el in self.poss_sets))
        self.changesToEvaluate: queue.Queue[list[FieldChange]] = queue.Queue()
        self.changesToEvaluate.put([])
        # self.addedToChangesToEvaluate:set[list[FieldChange]] = set()
        self.parentFieldChanges = {}

    def calculateEdgeTiles(self, field: MineField):
        self.unknownEdgeTiles = set()
        # self.knownEdgeTiles = {}
        for x, row in enumerate(field.board):
            for y, el in enumerate(row):
                if field.board[x][y] != -1:
                    for neighbour in field.getNeighbours((x, y)):
                        if field.getCoordinate(neighbour) == -1:
                            self.unknownEdgeTiles.add(neighbour)
                    # self.knownEdgeTiles[(x,y)] = FieldChange(False,(x,y))

    def calculateSimpleSets(self, field: MineField):
        for x, row in enumerate(field.board):
            for y, el in enumerate(row):
                bombs_left = field.getCoordinate((x, y))
                if -2 != bombs_left != -1:
                    unknowns = set()
                    for neighbour in field.getNeighbours((x, y)):
                        if field.getCoordinate(neighbour) == -1:
                            unknowns.add(neighbour)
                        elif field.getCoordinate(neighbour) == -2:
                            bombs_left -= 1
                    if len(unknowns):
                        # self.poss_sets.append(PossSet(unknowns, set(), bombs_left))
                        self.poss_sets.append(PossSet(set(), unknowns, -bombs_left))
                        # print(f"{(x,y)} gives {PossSet(unknowns, set(), bombs_left)}")

    def getNextTile(self):
        for pass_ in range(10):
            for el in self.poss_sets:
                res = el.is_solved()
                if res is not None:
                    return res
            print(f"Pass: {pass_}")
            for x, y in itertools.product(self.poss_sets.copy(), repeat=2):
                if (
                    any(
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
                        self.poss_sets.append(new_)
        input("10 loops but nothing found, continue: ")

    def isValid(self, field: MineField, changes: list[FieldChange]):
        neighbours = self.getNeighboursOfFieldChange(field, changes)
        for coordinate, changes in neighbours.items():
            # print(f"{coordinate=} {changes=}")
            upperLimit = 0
            lowerLimit = 0
            for neighbour in field.getNeighbours(coordinate):

                tileValue = field.getCoordinate(neighbour)
                if tileValue == -1:
                    upperLimit += 1
                elif tileValue == -2:
                    lowerLimit += 1
                    upperLimit += 1
            for change in changes:
                if change.isBomb:
                    lowerLimit += 1
                else:
                    upperLimit -= 1
            surroundingBombs = field.getCoordinate(coordinate)
            # print(f"{lowerLimit}<={surroundingBombs}<={upperLimit}")
            if not (lowerLimit <= surroundingBombs <= upperLimit):
                return False

        return True

    def getNeighboursOfFieldChange(
        self, field: MineField, changes: list[FieldChange]
    ) -> dict:
        neighbours = {}

        for change in changes:
            for neighbour in field.getNeighbours(change.coordinate):

                if field.getCoordinate(neighbour) >= 0:
                    if neighbour in neighbours:
                        neighbours[neighbour].append(change)
                    else:
                        neighbours[neighbour] = [change]
        return neighbours

    def getPossibleChanges(
        self, field: MineField, changes: list[FieldChange]
    ) -> set[list] | None:
        neighbours = set()
        if len(changes) == 0:
            return
        for change in changes:
            for localNeighbour in field.getNeighbours(change.coordinate):
                for farNeighbour in field.getNeighbours(localNeighbour):
                    if field.getCoordinate(farNeighbour) == -1:
                        neighbours.add(farNeighbour)

                        # if field.board[neighbour[0]][neighbour[1]]!=-1:
                        #     if neighbour in neighbours:
                        #         neighbours[neighbour].append(change)
                        #     else:
                        #         neighbours[neighbour]=[change]
        # changes = [fieldChange(False,coordinates) for coordinates in ]
        return neighbours

    def changeListIdentifier(self, changeList):
        return ", ".join([str(el) for el in changeList])

    # returns right answer or None if unknown
    # def helpParent(self, changeList: list[FieldChange], change) -> FieldChange:
    #     oppositeChange = change.opposite()
    #     if changeList == []:
    #         return oppositeChange
    #     parent = self.parentFieldChanges[self.changeListIdentifier(changeList)]
    #     if not parent.finished:
    #         if oppositeChange in parent.forbiddenChildren:
    #             parent.finished = True
    #             for index in range(len(changeList)):
    #                 parentOfParent = self.parentFieldChanges[
    #                     self.changeListIdentifier(
    #                         changeList[:index] + changeList[index + 1 :]
    #                     )
    #                 ]

    #                 res = self.helpParent(self, parentOfParent, changeList[index])
    #                 if res is not None:
    #                     return res
    #         else:
    #             parent.forbiddenChildren.add(change)
    #     return None

    # def getNextTile(self, field: MineField) -> FieldChange:
    #     while self.changesToEvaluate.not_empty:

    #         changeList = self.changesToEvaluate.get()
    #         if changeList == []:  # first run
    #             possibleChanges = self.unknownEdgeTiles
    #         else:
    #             possibleChanges = self.getPossibleChanges(field, changeList)
    #         for possibleChangeCoordinate in possibleChanges:
    #             for change in (
    #                 FieldChange(True, possibleChangeCoordinate),
    #                 FieldChange(False, possibleChangeCoordinate),
    #             ):
    #                 newChangeList = changeList + [change]
    #                 # print(self.deepStr(newChangeList),self.isValid(field,newChangeList))
    #                 if self.isValid(field, newChangeList):
    #                     self.changesToEvaluate.put(newChangeList)

    #                 else:
    #                     result = self.helpParent(changeList, change)

    #                     if result is not None:
    #                         return result
    #         # print(f"Setting {self.deepStr(changeList)} to ")
    #         self.parentFieldChanges[
    #             self.changeListIdentifier(changeList)
    #         ] = ParentFieldChange(changeList)
    #         print(f"Set {self.changeListIdentifier(changeList)} to ({changeList})")

    #     return None
