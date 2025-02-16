import numpy
import copy
import random

APPLE_CODES = ['G', 'R']

class Board():
    def __init__(self,
                 board_size=10,
                 green_apples_count=2, 
                 red_apples_count=1,
                 snake_size=3):
        self.area = numpy.full((board_size, board_size), '0', dtype=str)

        self.board_size = board_size

        self.snake_size = snake_size
        self.snake_pos = []
        self.init_snake()

        self.green_apples_count = green_apples_count
        self.red_apples_count = red_apples_count
        self.green_apples_pos = numpy.full((green_apples_count, 2), 0)
        self.red_apples_pos = numpy.full((red_apples_count, 2), 0)
        self.init_apples()

        self.update_area()

    ### TODO
    # There has to be a better way to do this lol
    def init_apples(self):
        apple_types = [self.green_apples_pos, self.red_apples_pos]

        for apple_type_index, apple_type in enumerate(apple_types):
            for index, _ in enumerate(apple_type):
                x = self.random_int_within_width()
                y = self.random_int_within_width()
                
                while (self.area[x][y] != '0'):
                    x = self.random_int_within_width()
                    y = self.random_int_within_width()

                apple_type[index] = [x, y]
                self.area[x][y] = APPLE_CODES[apple_type_index]

    def init_snake(self):
        self.snake_pos = []

        # Head
        self.snake_pos.append([self.random_int_within_width(), self.random_int_within_width()])

        # Body
        for _ in range(1, self.snake_size):
            new_pos = -1

            while (new_pos == -1):
                # Choose X or Y
                dimension = random.randint(0, 1)
                new_pos = self.snake_pos[-1][dimension] + [-1,1][random.randrange(2)]

                # Check if new position is valid
                if (new_pos >= self.board_size):
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

        self.update_area_snake()

    def update_area_snake(self):
        for snake_chunk in self.snake_pos:
            self.area[snake_chunk[0]][snake_chunk[1]] = 'S'

        self.area[self.snake_pos[-1][0]][self.snake_pos[-1][1]] = 'H'

    def update_area_apples(self):
        apple_types = [self.green_apples_pos, self.red_apples_pos]

        for apple_type, apple_code in zip(apple_types, APPLE_CODES):
            for apple in apple_type:
                self.area[apple[0]][apple[1]] = apple_code

    def update_area(self):
        # Reset area
        self.area = numpy.full((self.board_size, self.board_size), '0', dtype=str)

        self.update_area_snake()
        self.update_area_apples()

    def random_int_within_width(self):
        return random.randint(0, self.board_size - 1)

    def display_area_cli(self):
        displayed_board = self.area.T

        for _ in range(len(displayed_board) + 2):
            print('W', end='')
        print('')

        for column_index, column in enumerate(displayed_board):
            print('W', end='')
            for tile_index, tile in enumerate(displayed_board[column_index]):
                print(tile, end='')
            print('W')
        
        for _ in range(len(displayed_board) + 2):
            print('W', end='')
        print('')


if __name__ == "__main__":
    board = Board()