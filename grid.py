
from __future__ import print_function
from termcolor import colored

import random

END_MULTI_SOL = -1
END_NO_SOL = -2
#doesnt work because of a logical flaw: needs to know when one value exists
#within a certain third of the group

class Tile:


    def __init__(self, grid, x, y, value):
        self.grid = grid
        self.x = x
        self.y = y
        self.value = value
        self.editable = value == 0
        self.possibilities = [i for i in range(1,10)]

    def update_possibilities(self):
        if self.value != 0:
            self.possibilities = []
            return

        affectors = self.get_affectors()
        new_possibilties = []


        for i in self.possibilities:
            new_possibilties.append(i)
            for tile in affectors:
                if tile.value == i:
                    new_possibilties.remove(i)
                    break

        self.possibilities = new_possibilties

        #print(str(self.x) + "," + str(self.y) + " has possibilities " + str(self.possibilities))

    def eliminate_possibilities(self, possibilities):
        r = False
        for p in possibilities:
            if p in self.possibilities:
                r = True
                self.possibilities.remove(p)
        return r

    def get_affectors(self):
        affectors = []
        affectors.extend(self.grid.get_rows()[self.y])
        affectors.extend(self.grid.get_cols()[self.x])
        affectors.extend(self.grid.get_squares()[self.x//3 + (self.y//3)*3])
        return affectors

    def __str__(self):
        if self.value == 0:
            return " "
        if self.editable:
            return colored(self.value, "cyan")
        return colored(self.value, "red")

    def __repr__(self):
        return "%i:%i=%i" % (self.x, self.y, self.value)

class Grid:


    def __init__(self, fill=-1, grid=None, generate=False):
        self.grid = []
        if generate:
            self.generate()
        elif grid == None:
            for x in range(9):
                self.grid.append([])
                for y in range(9):
                    if fill == -1:
                        self.grid[x].append(Tile(self, x, y, int(input("Value of " + str(x+1) + ", " + str(y+1) + ": "))))
                    else:
                        self.grid[x].append(Tile(self, x, y, fill))
        else:
            for x in range(9):
                self.grid.append([])
                for y in range(9):
                    self.grid[x].append(Tile(self, x, y, grid[x][y]))

        self.__repr__ = self.__str__

    def __str__(self):
        s = ""
        for y in range(9):
            if y % 3 == 0 and y != 0:
                s += "-"*22 + "\n"
            for x in range(9):
                if x % 3 == 0 and x != 0:
                    s += "| "
                #if y % 3 == 0 and y != 0:
                #    s += "#"*11
                s += str(self.grid[x][y]) + " "
            s += "\n"
        s += "\n" + "#"*22 + "\n"
        return s

    def generate(self):

        for x in range(9):
            self.grid.append([])
            for y in range(9):
                self.grid[x].append(Tile(self, x, y, 0))

        solveability = END_MULTI_SOL

        while True:
            if solveability == True:
                return
            elif solveability == END_MULTI_SOL:

                self.update_possibilities()
                solveability = self.is_solvable()

            elif solveability == END_NO_SOL:
                print("Whoops")
                return



    def is_solvable(self):
        grid_v = []
        for x in range(9):
            grid_v.append([])
            for y in range(9):
                grid_v[x].append(self.grid[x][y].value)

        new_grid = Grid(grid=grid_v)
        new_grid.full_solve()

        if new_grid.is_solved():
            return True
        else:
            for x in range(9):
                for y in range(9):
                    if new_grid.grid[x][y].value == 0 and len(new_grid.grid[x][y].possibilities) == 0:
                        print(new_grid)
                        print(x,y)
                        return END_NO_SOL

            # randomly pick one and set to a random possibility
            empty_tiles = []
            for x in range(9):
                for y in range(9):
                    if new_grid.grid[x][y].value == 0:
                        empty_tiles.append(new_grid.grid[x][y])

            #self.update_possibilities()
            to_change = empty_tiles[random.randrange(len(empty_tiles))]
            print(to_change.x, to_change.y, to_change.possibilities)
            to_change.value = to_change.possibilities[random.randrange(len(to_change.possibilities))]
            to_change.editable = False
            self.grid[to_change.x][to_change.y].value = to_change.value
            self.update_possibilities()
            return END_MULTI_SOL


    def get_squares(self):
        squares = []
        for sy in range(3):
            for sx in range(3):
                square = []
                for y in range(3):
                    for x in range(3):
                        square.append(self.grid[sx*3 + x][sy*3 + y])
                squares.append(square)
        return squares

    def get_cols(self):
        return self.grid

    def get_rows(self):
        rows = []
        for _ in range(9):
            rows.append([0]*9)
        for x in range(9):
            for y in range(9):
                #print self.grid[x][y]
                rows[y][x] = self.grid[x][y]
                #print rows[y][x]
        #print rows
        return rows

    def is_valid(self):
        for group in self.get_groups():
            for i in range(1,10):
                c = 0
                for tile in group:
                    if tile.value == i:
                        c += 1
                if c > 1:
                    return False
        return True

    def set(self, x, y, v):
        self.grid[x][y].value = v

    def is_solved(self):
        if not self.is_valid():
            return False
        for x in range(9):
            for y in range(9):
                if self.grid[x][y].value == 0:
                    return False
        return True

    def get_groups(self):
        groups = self.get_squares()
        groups.extend(self.get_rows())
        groups.extend(self.get_cols())
        return groups

    def exclusive_subgroups(self):
        squares = self.get_squares()
        for i in range(9):
            rows = []
            rows.append([squares[i][0].value, squares[i][1].value, squares[i][2].value])
            rows.append([squares[i][3].value, squares[i][4].value, squares[i][5].value])
            rows.append([squares[i][6].value, squares[i][7].value, squares[i][8].value])
            
            print(rows)

    def simplify_internal_possibilities(self):
        any_changed = False

        for group_full in self.get_groups():

            group = []
            for t in group_full:
                if t.value == 0:
                    group.append(t)

            # eliminate based on subgroup of 2
            if True:
                for num1 in range(1, 9):
                    for num2 in range(num1+1, 10):
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

                                #print(num1, num2, 'at', tile.x, tile.y)
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
                for num3 in range(num2 +1, 10):
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

                            #print(num1, num2, 'at', tile.x, tile.y)
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

        for group_full in self.get_groups():
            group = []
            for t in group_full:
                if t.value == 0:
                    group.append(t)

            #eliminate based on subgroup of 2
            for tile_index_1 in range(len(group) - 1):
                for tile_index_2 in range(tile_index_1+1, len(group) - 0):
                    tile1 = group[tile_index_1]
                    tile2 = group[tile_index_2]
                    if len(tile1.possibilities) != 2 or tile1.possibilities != tile2.possibilities:
                        continue
                    for tile in group:
                        if tile is tile1 or tile is tile2:
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
        self.update_possibilities()
        while run_changed:
            run_changed = False
            for x in range(9):
                for y in range(9):
                    if self.grid[x][y].editable:
                        if len(self.grid[x][y].possibilities) == 1:
                            v = self.grid[x][y].possibilities[0]
                            self.grid[x][y].value = v
                            run_changed = True
                            any_change = True
                            #print(self)
                            self.update_possibilities()
                            #print ('Simple Solve Change: Set (%i,%i) to %i' % (x,y,v))
        return any_change

    def update_possibilities(self):
        for x in range(9):
            for y in range(9):
                self.grid[x][y].update_possibilities()

    def single_tile_solve(self):
        run_changed = True
        any_change = False
        self.update_possibilities()
        while run_changed:
            run_changed = False
            for group in self.get_groups():
                has_possibility = [[] for i in range(10)]
                for tile in group:
                    for possibility in tile.possibilities:
                        has_possibility[possibility].append(tile)
                for i in range(1, 10):
                    if len(has_possibility[i]) == 1:
                        tile = has_possibility[i][0]
                        tile.value = i
                        any_change = True
                        run_changed = True
                        #print(self)
                        self.update_possibilities()
                        #print ('Tile Solve Change: Set (%i,%i) to %i' % (tile.x,tile.y,i))
        return any_change

    def full_solve(self):
        changed = True
        while changed:
            changed = False
            if self.single_tile_solve():
                changed = True
            if self.singe_value_solve():
                changed = True
            if self.simplify_external_possibilities():
                changed = True
            if self.simplify_internal_possibilities():
                changed = True
        self.update_possibilities()
        print(self)

    def manual_solve(self):
        while not self.is_solved():
            print (self)
            s = input("What to set?\n> x,y,v\n> ")
            x,y,v = s
            original = self.grid[x][y].value
            self.grid[x][y].value = v
            if not self.is_valid():
                print (colored("Invalid", "yellow", "on_red"))
                self.grid[x][y].value = original


s = [[0,0,1,0,7,2,0,8,4],
     [6,4,9,8,0,0,2,5,7],
     [8,2,0,5,0,9,0,0,3],
     [0,0,0,2,8,0,1,0,0],
     [0,0,8,0,9,0,0,4,5],
     [0,0,0,1,0,7,0,0,2],
     [9,6,0,0,0,5,0,7,0],
     [3,0,4,0,0,0,5,6,0],
     [0,0,0,7,0,3,0,0,9],
]

hard1 = [
    [0,2,0,5,0,8,0,0,0],
    [9,0,0,0,0,0,8,0,0],
    [6,0,3,0,0,0,0,2,4],
    [0,3,2,6,0,0,0,0,0],
    [0,0,0,0,3,4,0,0,0],
    [7,0,0,0,1,9,3,0,0],
    [8,0,0,0,2,0,0,0,0],
    [0,0,0,0,0,0,9,0,1],
    [0,0,9,0,0,0,0,7,6],
]

expert = [
    [4,0,0,0,1,7,0,0,3],
    [0,1,0,0,3,0,0,0,4],
    [0,0,0,0,2,0,0,0,0],
    [5,0,0,0,0,0,9,0,0],
    [0,0,9,0,0,0,0,7,5],
    [0,0,0,4,0,0,0,0,0],
    [0,8,0,6,0,0,0,0,2],
    [9,0,0,0,0,0,3,0,0],
    [0,7,0,2,0,0,5,0,6],
]

expert2 = [
    [0,0,0,0,7,0,0,0,0],
    [0,1,0,5,0,0,8,0,0],
    [0,0,0,0,0,1,6,4,9],
    [0,0,8,1,0,0,0,0,0],
    [0,0,0,3,0,0,0,0,0],
    [0,9,0,2,0,4,0,5,3],
    [0,0,4,0,0,0,1,0,0],
    [0,7,3,0,0,0,9,0,0],
    [0,0,0,0,2,0,0,0,0],
]

def str_to_array(s):
    out = []
    ints = map(int, s)
    for i in range(0, 9):
        out.append(ints[i*9:i*9+9])
    return out


expert3 = str_to_array("000000000801000340006400800004210000000030002100600079000008000600000054900002007")
test    = str_to_array("0"*81)

generated = Grid(generate=True)
generated.exclusive_subgroups()
generated.manual_solve()
