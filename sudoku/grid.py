from __future__ import print_function
from termcolor import colored

from tile import Tile

import random

END_MULTI_SOL = -1
END_VALID_SOL = -3
END_NO_SOL = -2


# doesnt work because of a logical flaw: needs to know when one value exists
# within a certain third of the group

class Grid:

    def __init__(self, grid=None, generate=False):
        # type: (list, bool) -> None
        self.grid = []

        self.cols = []
        self.rows = []
        self.squares = []
        self.groups = []

        if generate:
            self.fill_grid(0)
            self.generate()
        elif grid:
            self.fill_from_grid(grid)
        else:
            self.fill_grid(0)

    def get_squares(self):
        # 0 | 1 | 2
        # ---------
        # 3 | 4 | 5
        # ---------
        # 6 | 7 | 8
        squares = []
        for sy in range(3):
            for sx in range(3):
                square = []
                for y in range(3):
                    for x in range(3):
                        square.append(self.grid[sx * 3 + x][sy * 3 + y])
                squares.append(square)
        return squares

    def get_cols(self):
        return self.grid

    def get_rows(self):
        rows = []
        for _ in range(9):
            rows.append([0] * 9)
        for x in range(9):
            for y in range(9):
                rows[y][x] = self.grid[x][y]
        return rows

    def fill_grid(self, value):
        for x in range(9):
            self.grid.append([])
            for y in range(9):
                self.grid[x].append(Tile(self, x, y, value))

        # save these groups
        self.cols = self.get_cols()
        self.rows = self.get_rows()
        self.squares = self.get_squares()
        self.groups = self.get_groups()

    def fill_from_grid(self, grid):
        for x in range(9):
            self.grid.append([])
            for y in range(9):
                self.grid[x].append(Tile(self, x, y, grid[x][y].value))

        # save these groups
        self.cols = self.get_cols()
        self.rows = self.get_rows()
        self.squares = self.get_squares()
        self.groups = self.get_groups()

    def generate(self):
        solveability = END_MULTI_SOL
        while True:
            if solveability == END_VALID_SOL:
                return
            elif solveability == END_MULTI_SOL:

                # randomly pick one and set to a random possibility
                empty_tiles = self.get_empty_tiles()

                to_change = random.choice(empty_tiles)
                to_change.value = random.choice(tuple(to_change.possibilities))
                to_change.editable = False

                print(self)

                self.update_possibilities()
                solveability = self.is_solvable()

            elif solveability == END_NO_SOL:
                print("Whoops")
                return

    def get_empty_tiles(self):
        empty_tiles = []
        for x in range(9):
            for y in range(9):
                if self.grid[x][y].value == 0:
                    empty_tiles.append(self.grid[x][y])
        return empty_tiles

    def is_solvable(self):
        new_grid = Grid(grid=self.grid)
        new_grid.full_solve()
        print(new_grid)

        if new_grid.is_solved():
            return END_VALID_SOL
        else:
            empty_tiles = new_grid.get_empty_tiles()
            for tile in empty_tiles:
                    if tile.value == 0 and len(tile.possibilities) == 0:
                        return END_NO_SOL
            return END_MULTI_SOL

    def is_valid(self):
        for group in self.get_groups():
            for i in range(1, 10):
                c = 0
                for tile in group:
                    if tile.value == i:
                        c += 1
                if c > 1:
                    return False
        return True

    def is_solved(self):
        if not self.is_valid():
            return False
        for x in range(9):
            for y in range(9):
                if self.grid[x][y].value == 0:
                    return False
        return True

    def update_possibilities(self):
        changed = False
        for x in range(9):
            for y in range(9):
                changed = changed or self.grid[x][y].update_possibilities()
        changed = changed or self.simplify_external_possibilities()
        changed = changed or self.simplify_internal_possibilities()
        return changed

    def get_groups(self):
        groups = self.get_squares()
        groups.extend(self.get_rows())
        groups.extend(self.get_cols())
        return groups

    def get_unsolved_groups(self):
        unsolved = []
        for group in self.groups:
            new_group = []
            for tile in group:
                if tile.value == 0:
                    new_group.append(tile)
            if len(new_group) != 0:
                unsolved.append(new_group)
        return unsolved

    def exclusive_subgroups(self):
        squares = self.get_squares()
        for i in range(9):
            rows = [[squares[i][0].value, squares[i][1].value, squares[i][2].value],
                    [squares[i][3].value, squares[i][4].value, squares[i][5].value],
                    [squares[i][6].value, squares[i][7].value, squares[i][8].value]]
        return rows

    def simplify_internal_possibilities(self):
        any_changed = False

        for group in self.get_unsolved_groups():
            # eliminate based on subgroup of 2
            for num1 in range(1, 9):
                for num2 in range(num1 + 1, 10):
                    tiles_with_nums = []
                    stop = False
                    for tile in group:
                        tile.update_possibilities()
                        if num1 in tile.possibilities and num2 in tile.possibilities:
                            tiles_with_nums.append(tile)
                        elif num1 in tile.possibilities or num2 in tile.possibilities:
                            stop = True
                            break
                    if stop:
                        continue

                    if len(tiles_with_nums) == 2:
                        for tile in tiles_with_nums:

                            # print(num1, num2, 'at', tile.x, tile.y)
                            if len(tile.possibilities) > 2:
                                any_changed = True
                                to_remove = []
                                for i in tile.possibilities:
                                    if i != num1 and i != num2:
                                        to_remove.append(i)
                                tile.eliminate_possibilities(to_remove)

            # eliminate based on subgroup of 3
            for num1 in range(1, 8):
                for num2 in range(num1 + 1, 9):
                    for num3 in range(num2 + 1, 10):
                        tiles_with_nums = []
                        stop = False
                        for tile in group:
                            tile.update_possibilities()
                            if num1 in tile.possibilities and num2 in tile.possibilities and num3 in tile.possibilities:
                                tiles_with_nums.append(tile)
                            elif num1 in tile.possibilities or num2 in tile.possibilities or num3 in tile.possibilities:
                                stop = True
                                break
                        if stop:
                            continue
                        if len(tiles_with_nums) == 3:
                            for tile in tiles_with_nums:
                                if len(tile.possibilities) > 3:
                                    any_changed = True
                                    to_remove = []
                                    for i in tile.possibilities:
                                        if i != num1 and i != num2 and i != num3:
                                            to_remove.append(i)
                                    tile.eliminate_possibilities(to_remove)
        return any_changed

    def simplify_external_possibilities(self):
        any_changed = False

        for group in self.get_unsolved_groups():

            # eliminate based on subgroup of 2
            for tile_index_1 in range(len(group) - 1):
                for tile_index_2 in range(tile_index_1 + 1, len(group) - 0):
                    tile1 = group[tile_index_1]
                    tile2 = group[tile_index_2]
                    if len(tile1.possibilities) != 2 or tile1.possibilities != tile2.possibilities:
                        continue
                    for tile in group:
                        if tile in [tile1, tile2]:
                            continue
                        any_changed = any_changed or tile.eliminate_possibilities(tile1.possibilities)

            # eliminate based on subgroup of 3
            for tile_index_1 in range(len(group) - 2):
                for tile_index_2 in range(tile_index_1 + 1, len(group) - 1):
                    for tile_index_3 in range(tile_index_2 + 1, len(group) - 0):
                        tile1 = group[tile_index_1]
                        tile2 = group[tile_index_2]
                        tile3 = group[tile_index_3]

                        possibilities = []
                        possibilities.extend(tile1.possibilities)
                        possibilities.extend(tile2.possibilities)
                        possibilities.extend(tile3.possibilities)

                        if len(set(possibilities)) != 3:
                            continue

                        for tile in group:
                            if tile in [tile1, tile2, tile3]:
                                continue
                            any_changed = any_changed or tile.eliminate_possibilities(possibilities)
        return any_changed

    def singe_value_solve(self):
        run_changed = True
        any_change = False
        while run_changed:
            run_changed = False
            for group in self.get_unsolved_groups():
                for tile in group:
                    if len(tile.possibilities) == 1:
                        tile.value = tile.possibilities[0]
                        run_changed = True
                        any_change = True
                        self.update_possibilities()
        return any_change

    def single_tile_solve(self):
        run_changed = True
        any_change = False
        while run_changed:
            run_changed = False
            for group in self.get_unsolved_groups():
                has_possibility = [[] for _ in range(10)]
                for tile in group:
                    for possibility in tile.possibilities:
                        has_possibility[possibility].append(tile)
                for i in range(1, 10):
                    if len(has_possibility[i]) == 1:
                        tile = has_possibility[i][0]
                        tile.value = i
                        any_change = True
                        run_changed = True
                        self.update_possibilities()
        return any_change

    def full_solve(self):
        changed = True
        while changed:
            changed = False
            if self.update_possibilities():
                changed = True
            if self.single_tile_solve():
                changed = True
            if self.singe_value_solve():
                changed = True

    def manual_solve(self):
        while not self.is_solved():
            self.update_possibilities()
            print(self)
            s = input("What to set?\n> x,y,v\n> ")
            x, y, v = s
            if v not in self.grid[x][y].possiblities:
                print(colored("Invalid", "yellow", "on_red"))
            else:
                self.grid[x][y].value = v

    def __str__(self):
        s = ""
        for y in range(9):
            if y % 3 == 0 and y != 0:
                s += "-" * 22 + "\n"
            for x in range(9):
                if x % 3 == 0 and x != 0:
                    s += "| "
                s += str(self.grid[x][y]) + " "
            s += "\n"
        s += "\n" + "#" * 22 + "\n"
        return s
