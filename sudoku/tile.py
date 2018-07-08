from termcolor import colored


class Tile:

    def __init__(self, grid, x, y, value):
        self.grid = grid
        self.x = x
        self.y = y
        self.value = value
        self.editable = (value == 0)
        self.possibilities = set(range(1, 10))

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
        # print(str(self.x) + "," + str(self.y) + " has possibilities " + str(self.possibilities))

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
        affectors.extend(self.grid.get_squares()[self.x // 3 + (self.y // 3) * 3])
        return affectors

    def __str__(self):
        if self.value == 0:
            return " "
        if self.editable:
            return colored(self.value, "cyan")
        return colored(self.value, "red")

    def __repr__(self):
        return "%i:%i=%i" % (self.x, self.y, self.value)

