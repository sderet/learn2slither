import numpy
import copy
import random

APPLE_CODES = ["G", "R"]


class Board:
    def __init__(
        self,
        board_size=10,
        green_apples_count=2,
        red_apples_count=1,
        snake_size=3,
        seed=False,
    ):
        self.lost = False
        self.area = numpy.full((board_size, board_size), "0", dtype=str)

        self.board_size = board_size

        self.rngstate = random.getstate()

        self.snake_size = snake_size
        self.snake_pos = []
        self.init_snake()

        self.green_apples_count = green_apples_count
        self.red_apples_count = red_apples_count
        self.green_apples_pos = numpy.full((green_apples_count, 2), 0)
        self.red_apples_pos = numpy.full((red_apples_count, 2), 0)
        self.init_apples()

        if seed:
            self.rngseed = seed
        else:
            self.rngseed = random.randrange(0, 100000)

        random.seed(self.rngseed)
        self.rngstate = random.getstate()

        self.update_area()

    def set_board(self, new_board):
        self.area = numpy.array(new_board["starting_state"])

        self.snake_pos = []

        green_apples_pos = []
        red_apples_pos = []

        self.red_apples_count = 0
        self.green_apples_count = 0

        for x, column in enumerate(self.area):
            for y, cell in enumerate(column):
                if cell == "G":
                    green_apples_pos.append([x, y])
                    self.green_apples_count += 1
                if cell == "R":
                    red_apples_pos.append([x, y])
                    self.red_apples_count += 1
                if cell == "H":
                    self.snake_pos.append([x, y])

        self.green_apples_pos = numpy.array(green_apples_pos)
        self.red_apples_pos = numpy.array(red_apples_pos)

        directions = [[-1, 0], [1, 0], [0, -1], [0, 1]]

        self.snake_size = 1
        finished = False
        while finished is False:
            finished = True
            for direction in directions:
                new_pos = [
                    self.snake_pos[-1][0] + direction[0],
                    self.snake_pos[-1][1] + direction[1],
                ]
                if (
                    not self.is_out_of_bounds(new_pos)
                    and new_pos not in self.snake_pos
                    and self.area[new_pos[0]][new_pos[1]] == "S"
                ):
                    self.snake_pos.append(new_pos)
                    self.snake_size += 1
                    finished = False
                    break

        self.rngseed = new_board["seed"]
        random.seed(self.rngseed)
        self.rngstate = random.getstate()

        print("set new board!")

    def reset_board(self):
        self.area = numpy.full(
            (self.board_size, self.board_size), "0", dtype=str
        )

        self.snake_pos = []
        self.init_snake()

        self.green_apples_pos = numpy.full((self.green_apples_count, 2), 0)
        self.red_apples_pos = numpy.full((self.red_apples_count, 2), 0)
        self.init_apples()
        pass

    def init_apples(self, all=True):
        random.setstate(self.rngstate)

        apple_types = [self.green_apples_pos, self.red_apples_pos]

        for apple_type_index, apple_type in enumerate(apple_types):
            for index, apple in enumerate(apple_type):
                if all or (apple == [-1, -1]).all():
                    x = self.random_int_within_width()
                    y = self.random_int_within_width()

                    while self.area[x][y] != "0":
                        x = self.random_int_within_width()
                        y = self.random_int_within_width()

                    apple_type[index] = [x, y]
                    self.area[x][y] = APPLE_CODES[apple_type_index]

        self.rngstate = random.getstate()

    def init_snake(self):
        random.setstate(self.rngstate)

        self.snake_pos = []

        # Head
        self.snake_pos.append(
            [self.random_int_within_width(), self.random_int_within_width()]
        )

        # Body
        for _ in range(1, self.snake_size):
            new_pos = -1

            while new_pos == -1:
                # Choose X or Y
                dimension = random.randint(0, 1)
                new_pos = (
                    self.snake_pos[-1][dimension]
                    + [-1, 1][random.randrange(2)]
                )

                # Check if new position is valid
                if new_pos >= self.board_size:
                    new_pos = -1

                tile_to_be = copy.deepcopy(self.snake_pos[-1])
                tile_to_be[dimension] = new_pos

                # Check if new position isn't already taken
                for snake_chunk in self.snake_pos:
                    if snake_chunk == tile_to_be:
                        new_pos = -1
                        break

            # Copy last pos, then modify it
            self.snake_pos.append(copy.deepcopy(self.snake_pos[-1]))
            self.snake_pos[-1][dimension] = new_pos

        self.rngstate = random.getstate()
        self.update_area_snake()

    def update_area_snake(self):
        for snake_chunk in self.snake_pos:
            if (
                snake_chunk[0] < self.board_size
                and snake_chunk[1] < self.board_size
            ):
                self.area[snake_chunk[0]][snake_chunk[1]] = "S"

        if (
            self.snake_pos[0][0] < self.board_size
            and self.snake_pos[0][1] < self.board_size
        ):
            self.area[self.snake_pos[0][0]][self.snake_pos[0][1]] = "H"

    def update_area_apples(self):
        apple_types = [self.green_apples_pos, self.red_apples_pos]

        for apple_type, apple_code in zip(apple_types, APPLE_CODES):
            for apple in apple_type:
                self.area[apple[0]][apple[1]] = apple_code

    def update_area(self):
        # Reset area
        self.area = numpy.full(
            (self.board_size, self.board_size), "0", dtype=str
        )

        self.update_area_snake()
        self.update_area_apples()

    def random_int_within_width(self):
        return random.randint(0, self.board_size - 1)

    def move_snake(self, direction):
        new_head_pos = [sum(x) for x in zip(self.snake_pos[0], direction)]

        if self.is_out_of_bounds(new_head_pos):
            # print("Out of bounds!")
            self.lost = True

        ate_green = False
        ate_red = False

        for index, green_apple in enumerate(self.green_apples_pos):
            if (
                new_head_pos[0] == green_apple[0]
                and new_head_pos[1] == green_apple[1]
            ):
                ate_green = True
                self.green_apples_pos[index] = [-1, -1]

        for index, red_apple in enumerate(self.red_apples_pos):
            if (
                new_head_pos[0] == red_apple[0]
                and new_head_pos[1] == red_apple[1]
            ):
                ate_red = True
                self.red_apples_pos[index] = [-1, -1]

        if ate_red and len(self.snake_pos) <= 1:
            # print("Got too small!")
            self.lost = True

        self.snake_pos.insert(0, new_head_pos)
        if not ate_green:
            self.snake_pos.pop()
        if ate_red and not self.lost:
            self.snake_pos.pop()

        if new_head_pos in self.snake_pos[1:]:
            # print("Hit tail!")
            self.lost = True

        if ate_green or ate_red:
            self.init_apples(all=False)

        self.update_area()

        if self.lost:
            return "L"
        elif ate_green:
            return "G"
        elif ate_red:
            return "R"
        else:
            return "0"

    def is_out_of_bounds(self, position):
        for value in position:
            if value < 0 or value >= self.board_size:
                return True
        return False

    def display_area_cli(self):
        displayed_board = self.area.T

        for _ in range(len(displayed_board) + 2):
            print("W", end="")
        print("")

        for column_index, column in enumerate(displayed_board):
            print("W", end="")
            for tile_index, tile in enumerate(displayed_board[column_index]):
                print(tile, end="")
            print("W")

        for _ in range(len(displayed_board) + 2):
            print("W", end="")
        print("")


if __name__ == "__main__":
    board = Board()
