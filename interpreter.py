import board
import numpy
import random
import math

ACTIONS = ["U", "D", "L", "R"]
DIRECTIONS = [[0, -1], [0, 1], [-1, 0], [1, 0]]

VALUES = {'0': 0, 'G': 1, 'R': 2, 'S': 3, 'W': 4}

REWARDS = {'0': -10, 'G': 1000, 'R': -100, 'L': -1000}

class Interpreter:
    def __init__(self, board=board.Board(), learning_rate=0.3, exploration_rate=0.01, decay=0.8, sessions=100, epoch=0, save_to="values.qval", load_model=False, vision_length=1):
        self.board = board
        self.exploration_rate = exploration_rate
        self.decay = decay
        self.learning_rate = learning_rate
        self.sessions = sessions
        self.epoch = epoch
        self.save_to = save_to
        self.vision_length = vision_length

        # Number of tiles to look ahead times the number of different tile types to stop on, to the power of the number of directions we check
        self.states = numpy.zeros([pow(vision_length * len(VALUES), len(DIRECTIONS)), len(ACTIONS)])

        if (load_model):
            self.states = numpy.loadtxt(load_model)

    def calculate_state(self):
        total_state_value = 0

        head_pos = self.board.snake_pos[0]

        vision = []

        for index, direction in enumerate(DIRECTIONS):
            vision.append([])
            newest_pos = [sum(x) for x in zip(head_pos, direction)]
            while not self.board.is_out_of_bounds(newest_pos):
                vision[index].append(self.board.area[newest_pos[0]][newest_pos[1]])
                newest_pos = [sum(x) for x in zip(newest_pos, direction)]

        self.vision = vision

        total_state_value = 0

        for index, viewed_direction in enumerate(vision):

            current_distance = 0
            while (current_distance < len(viewed_direction) and current_distance < self.vision_length and viewed_direction[current_distance] == '0'):
                current_distance += 1
            if not current_distance < len(viewed_direction):
                value = VALUES['W']
                current_distance -= 1
            elif  not current_distance < self.vision_length:
                value = VALUES['0']
                current_distance -= 1
            else:
                value = VALUES[viewed_direction[current_distance]]
            
            total_state_value += (value + (current_distance * len(VALUES))) * pow(len(VALUES), index)

        return total_state_value

    def new_step(self):
        self.current_state = self.calculate_state()

        if random.uniform(0, 1) < self.exploration_rate:
            action = random.randrange(0, len(DIRECTIONS))
        else:
            action = numpy.argmax(self.states[self.current_state])

        type_eaten = self.board.move_snake(DIRECTIONS[action])
        reward = REWARDS[type_eaten]

        if 'G' in self.vision:
            reward += 100

        new_state = self.calculate_state()

        current_score_for_action = self.states[self.current_state][action]
        max_score_after_action = numpy.max(self.states[new_state])

        self.states[self.current_state][action] = (self.learning_rate * current_score_for_action) + (self.learning_rate * (reward + (self.decay * max_score_after_action)))

        self.epoch += 1

    def save_qvalues(self):
        numpy.savetxt(self.save_to, self.states)

    def loop(self):
        ep_count = 0

        longest_size = 0
        longest_life = 0

        while ep_count < self.sessions:
            while self.board.lost == False:
                self.new_step()

            ep_count += 1

            if self.epoch > longest_life:
                print(f"Newest best lifetime: {self.epoch}")
                longest_life = self.epoch
            if len(self.board.snake_pos) > longest_size:
                print(f"Newest longest size: {len(self.board.snake_pos)}")
                longest_size = len(self.board.snake_pos)

            new_board = board.Board()
            self.board = new_board
            self.epoch = 0
            print(f"Episode {ep_count}")
        
        print(f'Longest size: {longest_size}\nLongest session: {longest_life}')

        self.save_qvalues()


if __name__ == "__main__":
    interpreter = Interpreter()
    interpreter.loop()