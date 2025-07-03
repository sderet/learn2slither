import board
import interpreter
import agent
import numpy
import math
import json

import argparse

ACTIONS = ["U", "D", "L", "R"]
ACTIONS_NAMES = ["UP", "DOWN", "LEFT", "RIGHT"]
DIRECTIONS = [[0, -1], [0, 1], [-1, 0], [1, 0]]
VALUES = {"0": 0, "G": 1, "R": 2, "S": 3, "g": 4}


class Qlearner:

    def __init__(
        self,
        argboard=None,
        arginterpreter=None,
        argagent=None,
        max_sessions=100,
        max_epoch=10000,
        load_qval=False,
        save_qval=False,
        save_replay=False,
        no_learning=False,
        verbose=False,
    ):
        self.board = board.Board() if argboard is None else argboard
        self.interpreter = interpreter.Interpreter() if arginterpreter is None\
            else arginterpreter
        self.agent = agent.Agent() if argagent is None else argagent

        self.no_learning = no_learning
        self.verbose = verbose

        if load_qval:
            try:
                states = numpy.loadtxt(load_qval)
            except FileNotFoundError:
                print(f"Input file {load_qval} does not exist.")
                exit()
            if self.verbose:
                print(f"Loaded model from {load_qval}.")
        else:  # Lowest possible number of states without repeats
            states = numpy.zeros(
                [
                    math.comb(
                        self.interpreter.vision_length * len(VALUES)
                        + len(DIRECTIONS)
                        - 1,
                        len(DIRECTIONS),
                    ),
                    len(ACTIONS),
                ]
            )
        self.agent.states = states

        self.max_sessions = max_sessions
        self.max_epoch = max_epoch

        self.save_qval = save_qval
        self.save_replay = save_replay
        self.starting_state = self.board.area.tolist()
        self.inputs = []

    def new_step(self):
        state = self.interpreter.calculate_state(self.board, self.verbose)

        action, direction = self.agent.choose_direction(state)
        self.inputs.append(direction)

        if self.verbose:
            print(f"{ACTIONS_NAMES[DIRECTIONS.index(direction)]}\n")

        type_eaten = self.board.move_snake(direction)

        if not self.no_learning:
            new_state = self.interpreter.calculate_state(self.board)
            reward = self.interpreter.calculate_reward(
                direction, type_eaten, self.board
            )

            self.agent.update_states(state, new_state, action, reward)

    def loop(self):
        ep_count = 0
        epoch = 0

        longest_size = 0
        longest_life = 0
        best = {"score": 0, "lifetime": 0, "starting_state": 0, "inputs": []}

        while ep_count < self.max_sessions:
            while self.board.lost is False and epoch < self.max_epoch:
                self.new_step()
                epoch += 1

            ep_count += 1

            if epoch > longest_life:
                if self.verbose:
                    print(f"Newest best lifetime: {epoch}")
                longest_life = epoch
            if self.verbose:
                print("Length: ", len(self.board.snake_pos))
            if len(self.board.snake_pos) > longest_size:
                if self.verbose:
                    print(f"Newest longest size: {len(self.board.snake_pos)}")
                longest_size = len(self.board.snake_pos)

                best["score"] = longest_size
                best["lifetime"] = epoch
                best["starting_state"] = self.starting_state
                best["inputs"] = self.inputs
                best["seed"] = self.board.rngseed

            self.board = board.Board()
            self.starting_state = self.board.area.tolist()
            self.inputs = []

            epoch = 0
            if self.verbose:
                print(f"Episode {ep_count}")

        print(
            f"Training finished for {self.max_sessions} sessions.",
            f"Longest size: {longest_size}",
            f"Longest session: {longest_life}"
        )

        if self.save_qval:
            self.save_qvalues_file()
            if self.verbose:
                print(f"Q values file saved at {self.save_qval}.")
        if self.save_replay:
            self.save_replay_file(best)
            if self.verbose:
                print(f"Replay file saved at {self.save_replay}.")

        return best

    def save_qvalues_file(self):
        with open(self.save_qval, "w") as fd:
            numpy.savetxt(fd, self.agent.states)

    def save_replay_file(self, replay):
        with open(self.save_replay, "w") as fd:
            json.dump(replay, fd)


def play_wrapper(qlearner: Qlearner):
    replay_filename = qlearner.save_replay
    qlearner.save_replay = False
    qvalues_filename = qlearner.save_qval
    qlearner.save_qval = False

    replay = qlearner.loop()
    qlearner.save_replay = replay_filename
    qlearner.save_qval = qvalues_filename

    return qlearner, replay


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Learn2slither",
        description="Q Learning program for the game Snake",
    )
    parser.add_argument(
        "-g",
        "--gui",
        action="store_true",
        help="Use graphical user interface (GUI) mode",
    )
    parser.add_argument(
        "-s",
        "--sessions",
        type=int,
        default=100,
        help="The number of sessions to execute. Has no effect in GUI mode",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=False,
        help="The file to load Q values from",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=False,
        help="The file to save Q values to. Has no effect in GUI mode",
    )
    parser.add_argument(
        "-r",
        "--replay",
        type=str,
        default=False,
        help="The file to save the agent's best replay to. " +
        "Has no effect in GUI mode",
    )
    parser.add_argument(
        "-n",
        "--no-learning",
        action="store_true",
        help="Stops the Q values from updating as it happens",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=1,
        help="Train multiple snakes independently in different threads. " +
        "If used with --replay or --output, will only create a file for" +
        "the best performing snake. Has no effect in GUI mode",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase output verbosity",
    )

    args = parser.parse_args()

    if args.gui:
        import gui

        model = Qlearner(load_qval=args.input)

        user_interface = gui.GraphicalInterface(
            model, no_learning=args.no_learning, verbose=args.verbose
        )
        user_interface.draw_board()
        user_interface.start_loop()
    elif args.threads > 1:
        import multiprocessing.dummy as threading
        pool = threading.Pool(args.threads)

        learners = []
        for _ in range(args.threads):
            learner = Qlearner(
                max_sessions=args.sessions,
                load_qval=args.input,
                save_qval=args.output,
                save_replay=args.replay,
                verbose=args.verbose,
                no_learning=args.no_learning,
            )
            learners.append(learner)

        results, replays = map(list, zip(*pool.map(play_wrapper, learners)))
        if (args.output or args.replay):
            index_of_best = replays.index(
                max(
                    replays,
                    key=lambda replay: replay['score']
                )
            )
            if args.output:
                results[index_of_best].save_qvalues_file()
            if args.replay:
                results[index_of_best].save_replay_file(replays[index_of_best])
    else:
        qlearner = Qlearner(
            max_sessions=args.sessions,
            load_qval=args.input,
            save_qval=args.output,
            save_replay=args.replay,
            verbose=args.verbose,
            no_learning=args.no_learning,
        )
        qlearner.loop()
