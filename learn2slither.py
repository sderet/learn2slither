import board
import interpreter
import agent
import numpy
import math
import json

ACTIONS = ["U", "D", "L", "R"]
DIRECTIONS = [[0, -1], [0, 1], [-1, 0], [1, 0]]
VALUES = {'0': 0, 'G': 1, 'R': 2, 'S': 3, 'g': 4}

class Qlearner():

    def __init__(self, board=board.Board(), interpreter=interpreter.Interpreter(), agent=agent.Agent(), max_sessions=100, max_epoch=10000, load_qval=False, save_qval=False, save_replay=False):
        self.board = board
        self.interpreter = interpreter
        self.agent = agent
        
        if (load_qval):
            states = numpy.loadtxt(load_qval)
        else: # Lowest possible number of states without repeats
            states = numpy.zeros([math.comb(self.interpreter.vision_length * len(VALUES) + len(DIRECTIONS) - 1, len(DIRECTIONS)), len(ACTIONS)])
        self.agent.states = states

        self.max_sessions = max_sessions
        self.max_epoch = max_epoch

        self.save_qval = save_qval
        self.save_replay = save_replay
        self.starting_state = self.board.area.tolist()
        self.inputs = []

    def new_step(self):
        state = self.interpreter.calculate_state(self.board)

        action, direction = self.agent.choose_direction(state)
        self.inputs.append(direction)

        type_eaten = self.board.move_snake(direction)

        new_state = self.interpreter.calculate_state(self.board)
        reward = self.interpreter.calculate_reward(direction, type_eaten, self.board)

        self.agent.update_states(state, new_state, action, reward)

    def loop(self):
        ep_count = 0
        epoch = 0

        longest_size = 0
        longest_life = 0
        best = {"starting_state": 0, "inputs": []}

        while ep_count < self.max_sessions:
            while self.board.lost == False and epoch < self.max_epoch:
                self.new_step()
                epoch += 1

            ep_count += 1

            if epoch > longest_life:
                print(f"Newest best lifetime: {epoch}")
                longest_life = epoch
            print(len(self.board.snake_pos))
            if len(self.board.snake_pos) > longest_size:
                print(f"Newest longest size: {len(self.board.snake_pos)}")
                longest_size = len(self.board.snake_pos)
                
                best['starting_state'] = self.starting_state
                best['inputs'] = self.inputs

            self.board = board.Board()
            self.starting_state = self.board.area.tolist()
            self.inputs = []

            epoch = 0
            print(f"Episode {ep_count}")
        
        print(f'Longest size: {longest_size}\nLongest session: {longest_life}')

        if self.save_qval:
            self.save_qvalues_file()
        if self.save_replay:
            self.save_replay_file(best)

    def save_qvalues_file(self):
        numpy.savetxt(self.save_qval, self.agent.states)

    def save_replay_file(self, replay):
        with open(self.save_replay, 'w') as fd:
            json.dump(replay, fd)


if __name__ == "__main__":
    qlearner = Qlearner(save_qval="values1.qval", save_replay="replay.rpl")
    qlearner.loop()