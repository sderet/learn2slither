import board
import numpy
import json
import random
import math

ACTIONS = ["U", "D", "L", "R"]
DIRECTIONS = [[0, -1], [0, 1], [-1, 0], [1, 0]]

VALUES = {'0': 0, 'G': 1, 'R': 2, 'S': 3, 'g': 4}

REWARDS = {'0': -5, 'G': 1000, 'R': -100, 'L': -1000}

def partial_sum(x):
    total = 0
    for index in range(x):
        total += index
    return total

class Interpreter:
    def __init__(self, board=board.Board(), learning_rate=0.1, exploration_rate=0.05, decay=0.8, sessions=100, epoch=0, save_to="values.qval", load_model=False, vision_length=1, max_epoch=100000, replay_file="replay.rpl"):
        self.board = board
        self.exploration_rate = exploration_rate
        self.decay = decay
        self.learning_rate = learning_rate
        self.sessions = sessions
        self.epoch = epoch
        self.max_epoch = max_epoch
        self.vision_length = vision_length

        self.starting_state = board.area.tolist()
        self.inputs = []

        self.save_to = save_to
        self.replay_file = replay_file

        # Number of combinations. why bother with repeats?
        self.states = numpy.zeros([math.comb(vision_length * len(VALUES) + len(DIRECTIONS) - 1, len(DIRECTIONS)), len(ACTIONS)])

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

        types = []

        for index, viewed_direction in enumerate(vision):

            current_distance = 0
            while (current_distance < len(viewed_direction) and current_distance < self.vision_length and viewed_direction[current_distance] == '0'):
                current_distance += 1
            if not current_distance < len(viewed_direction):
                value = VALUES['S']
                current_distance -= 1
            elif  not current_distance < self.vision_length:
                value = VALUES['0']
                if 'G' in viewed_direction:
                    value = VALUES['g']
                current_distance -= 1
            else:
                value = VALUES[viewed_direction[current_distance]]
            
            types.append(value)

        actions = [x for (y,x) in sorted(zip(types, ACTIONS), key=lambda pair: pair[0])]

        sorted_values = sorted(types)
        total_state_value = 0
        inc = 0

        n = self.vision_length * len(VALUES)
        k = len(DIRECTIONS)

        for value in sorted_values:
            value -= inc
            k -= 1
            for j in range(value):
                total_state_value += math.comb(n-j+k-1, k)
            n -= value
            inc += value

        return total_state_value, actions, types

    def new_step(self):
        self.current_state, actions, types = self.calculate_state()

        if random.uniform(0, 1) < self.exploration_rate:
            action = random.randrange(0, len(actions))
            attempts = 0
            while (self.states[self.current_state][action] < REWARDS['L'] * self.learning_rate * self.decay and attempts < 100):
                action = random.randrange(0, len(actions))
                attempts += 1
        else:
            action = numpy.argmax(self.states[self.current_state])

        direction = DIRECTIONS[ACTIONS.index(actions[action])]
        self.inputs.append(direction)

        type_eaten = self.board.move_snake(direction)
        reward = REWARDS[type_eaten]

        if VALUES['g'] in types and not self.board.lost:
            reward += 300

        new_state, _, _ = self.calculate_state()

        current_score_for_action = self.states[self.current_state][action]
        max_score_after_action = numpy.max(self.states[new_state])

        self.states[self.current_state][action] = (self.learning_rate * current_score_for_action) + (self.learning_rate * (reward + (self.decay * max_score_after_action)))

        self.epoch += 1

    def save_qvalues(self):
        numpy.savetxt(self.save_to, self.states)

    def save_replay(self, replay):
        with open(self.replay_file, 'w') as fd:
            json.dump(replay, fd, indent=4)

    def loop(self):
        ep_count = 0

        longest_size = 0
        longest_life = 0
        best = {"starting_state": 0, "inputs": []}

        while ep_count < self.sessions:
            while self.board.lost == False and self.epoch < self.max_epoch:
                self.new_step()

            ep_count += 1

            if self.epoch > longest_life:
                print(f"Newest best lifetime: {self.epoch}")
                longest_life = self.epoch
            print(len(self.board.snake_pos))
            if len(self.board.snake_pos) > longest_size:
                print(f"Newest longest size: {len(self.board.snake_pos)}")
                longest_size = len(self.board.snake_pos)
                best['starting_state'] = self.starting_state
                best['inputs'] = self.inputs

            self.board = board.Board()
            self.starting_state = self.board.area.tolist()
            self.inputs = []

            self.epoch = 0
            print(f"Episode {ep_count}")
        
        print(f'Longest size: {longest_size}\nLongest session: {longest_life}')

        self.save_qvalues()
        self.save_replay(best)


if __name__ == "__main__":
    interpreter = Interpreter()
    interpreter.loop()