import random
import numpy

ACTIONS = ["U", "D", "L", "R"]
DIRECTIONS = [[0, -1], [0, 1], [-1, 0], [1, 0]]

VALUES = {"0": 0, "G": 1, "R": 2, "S": 3, "g": 4}


class Agent:

    def __init__(self, exploration_rate=0.05, learning_rate=0.1, decay=0.8):
        self.exploration_rate = exploration_rate
        self.learning_rate = learning_rate
        self.decay = decay

        self.states = []

    def choose_direction(self, state):
        state_serial_number, possible_directions, lowest_reward = state

        if random.uniform(0, 1) < self.exploration_rate:
            action = random.randrange(0, len(possible_directions))

            # If choosing an action that will instantly lose,
            # choose something else instead
            attempts = 0
            while (
                self.states[state_serial_number][action]
                < lowest_reward * self.learning_rate * self.decay
                and attempts < 100
            ):
                action = random.randrange(0, len(possible_directions))
                attempts += 1
        else:
            action = numpy.argmax(self.states[state_serial_number])

        direction = DIRECTIONS[ACTIONS.index(possible_directions[action])]
        return action, direction

    def update_states(self, previous_state, new_state, direction, reward):
        previous_state = previous_state[0]
        new_state = new_state[0]

        score_before_action = self.states[previous_state][direction]

        if new_state >= 0:
            max_score_after_action = numpy.max(self.states[new_state])
        else:
            max_score_after_action = new_state

        self.states[previous_state][direction] = (
            self.learning_rate * score_before_action
        ) + (
            self.learning_rate
            * (reward + (self.decay * max_score_after_action))
        )
