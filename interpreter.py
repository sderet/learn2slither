import board
import agent
import numpy
import json
import random
import math

ACTIONS = ["U", "D", "L", "R"]
DIRECTIONS = [[0, -1], [0, 1], [-1, 0], [1, 0]]

VALUES = {'0': 0, 'G': 1, 'R': 2, 'S': 3, 'g': 4}

REWARDS = {'0': -5, 'G': 1000, 'R': -100, 'L': -1000, 'g': 200}

def partial_sum(x):
    total = 0
    for index in range(x):
        total += index
    return total

class Interpreter:
    def __init__(self, vision_length=1):
        self.vision_length = vision_length


    def calculate_vision(self, board: board.Board):
        head_pos = board.snake_pos[0]
        vision = []

        for index, direction in enumerate(DIRECTIONS):
            vision.append([])
            newest_pos = [sum(x) for x in zip(head_pos, direction)]
            while not board.is_out_of_bounds(newest_pos):
                vision[index].append(board.area[newest_pos[0]][newest_pos[1]])
                newest_pos = [sum(x) for x in zip(newest_pos, direction)]

        types = []

        for index, viewed_direction in enumerate(vision):
            current_distance = 0
            while (current_distance < len(viewed_direction) and current_distance < self.vision_length and viewed_direction[current_distance] == '0'):
                current_distance += 1

            if not current_distance < self.vision_length:
                value = VALUES['0']
                if 'G' in viewed_direction:
                    value = VALUES['g']
                current_distance -= 1
            elif not current_distance < len(viewed_direction):
                value = VALUES['S']
                current_distance -= 1
            else:
                value = VALUES[viewed_direction[current_distance]]
            
            types.append(value)
        
        return (types)

    def calculate_state(self, board: board.Board):
        if board.lost:
            return REWARDS['L'], 0, 0

        types = self.calculate_vision(board)

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

        return total_state_value, actions, REWARDS['L']


    def calculate_reward(self, direction, type_eaten, board: board.Board):
        reward = REWARDS[type_eaten]

        head_pos = board.snake_pos[0]
        position = [sum(x) for x in zip(head_pos, direction)]
        vision = []

        while not board.is_out_of_bounds(position):
            vision.append(board.area[position[0]][position[1]])
            position = [sum(x) for x in zip(position, direction)]

        if 'G' in vision and not board.lost:
            reward += REWARDS['g']

        return reward

    def save_qvalues(self):
        numpy.savetxt(self.save_to, self.states)

    def save_replay(self, replay):
        with open(self.replay_file, 'w') as fd:
            json.dump(replay, fd, indent=4)


if __name__ == "__main__":
    interpreter = Interpreter()