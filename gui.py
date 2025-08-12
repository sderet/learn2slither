import tkinter as tk
from tkinter import filedialog
import json
import numpy
import argparse
import board
import time
import learn2slither

TILES = ["0", "H", "S", "G", "R"]
COLORS = ["white", "skyblue", "blue", "green", "red"]

DIRECTIONS_FULL_NAMES = ["Up", "Down", "Left", "Right"]
DIRECTIONS_NAMES = ["U", "D", "L", "R"]
DIRECTIONS = [[0, -1], [0, 1], [-1, 0], [1, 0]]

BOARD_HEIGHT = 300

FPS_OPTIONS = ["Unlimited", "120", "60", "30", "15", "5", "1"]
SPEED_LIMITS = [0, 1 / 120, 1 / 60, 1 / 30, 1 / 15, 1 / 5, 1]


def get_direction_vector(name):
    return DIRECTIONS[DIRECTIONS_NAMES.index(name)]


class GraphicalInterface:
    def __init__(
        self,
        model=learn2slither.Qlearner(),
        speedlimit=2,
        stopped=True,
        no_learning=False,
        verbose=False,
    ):
        self.model = model

        self.speedlimit = speedlimit

        self.stopped = stopped
        self.model.no_learning = no_learning
        self.model.verbose = verbose

        # Create the main window
        self.root = tk.Tk()
        self.root.grid_columnconfigure(1, minsize=200, pad=10)

        self.root.title("Learn2Slither")

        self.board_frame = tk.Canvas(
            self.root, width=BOARD_HEIGHT, height=BOARD_HEIGHT, bg="ivory"
        )
        self.board_frame.grid(padx=(10, 10))

        if stopped:
            self.pausebutton = tk.Button(
                self.root, text="Resume", command=self.start
            )
        else:
            self.pausebutton = tk.Button(
                self.root, text="Pause", command=self.stop
            )
        self.pausebutton.grid(column=0, sticky="w", padx=(10, 0), pady=(10, 0))
        button = tk.Button(
            self.root, text="Options", command=self.init_options_menu
        )
        button.grid(column=0, sticky="w", padx=(10, 0))
        button = tk.Button(
            self.root, text="Save Q values", command=self.save_q_values
        )
        button.grid(column=0, stick="w", padx=(10, 0))

        if not self.model.no_learning:
            self.learning_button = tk.Button(
                self.root, text="Stop learning", command=self.stop_learning
            )
        else:
            self.learning_button = tk.Button(
                self.root, text="Resume learning", command=self.resume_learning
            )
        self.learning_button.grid(
            column=0, stick="w", padx=(10, 0), pady=(0, 10)
        )

        button = tk.Button(
            self.root,
            text="Reset board",
            command=lambda: self.update_board(board.Board()),
        )
        button.grid(column=0, row=1, sticky="e", padx=(0, 10), pady=(10, 0))
        button = tk.Button(
            self.root, text="Load replay", command=self.open_replay_file
        )
        button.grid(column=0, row=2, sticky="e", padx=(0, 10))

        button = tk.Button(
            self.root, text="Load Q values", command=self.load_q_values
        )
        button.grid(column=0, row=3, sticky="e", padx=(0, 10), pady=(0, 10))

        # Q values and other snake info
        self.snake_info_frame = tk.Frame(self.root)

        text = tk.StringVar(self.snake_info_frame)
        text.set("Snake size:")
        label = tk.Label(self.snake_info_frame, textvariable=text)
        label.grid(column=0, row=0, sticky="w")

        self.snake_size = tk.StringVar(self.snake_info_frame, 0)
        self.snake_size.set(self.model.board.snake_size)
        label = tk.Label(self.snake_info_frame, textvariable=self.snake_size)
        label.grid(column=1, row=0, sticky="w")

        text = tk.StringVar(self.snake_info_frame)
        text.set("Q values:")
        label = tk.Label(self.snake_info_frame, textvariable=text)
        label.grid(column=0, row=1, sticky="w")

        self.q_values = []
        for index, qvalue in enumerate(DIRECTIONS):
            qvalue = tk.StringVar(self.snake_info_frame, 0)
            label = tk.Label(self.snake_info_frame, textvariable=qvalue)
            label.grid(
                column=1 + DIRECTIONS[index][0], row=3 + DIRECTIONS[index][1]
            )
            self.q_values.append(qvalue)

        self.update_displayed_qvalues()

        self.snake_info_frame.grid(row=0, column=1, padx=(10, 20), sticky="w")

        # Movement buttons
        self.controls_frame = tk.Frame(self.root)

        for index, direction in enumerate(DIRECTIONS_NAMES):
            button = tk.Button(
                self.controls_frame,
                text=DIRECTIONS_FULL_NAMES[index],
                command=lambda dir=direction: self.move_snake(
                    get_direction_vector(dir)
                ),
            )
            button.grid(
                column=1 + DIRECTIONS[index][0], row=2 + DIRECTIONS[index][1]
            )

        button = tk.Button(
            self.controls_frame, text="Step", command=lambda: self.step()
        )
        button.grid(column=1, row=4, pady=(10, 0))

        if stopped:
            self.controls_frame.grid(pady=(0, 10))
            self.bind_directions()

        # Replay controls
        self.replay_frame = tk.Frame(self.root)

        self.inputs = []
        self.replay_mode = False
        button = tk.Button(
            self.replay_frame,
            text="Exit replay mode",
            command=self.exit_replay,
        )
        button.grid(sticky="w")

    def init_options_menu(self):
        self.stop()

        self.menu_window = tk.Toplevel(self.root)

        options_grid = tk.Frame(self.menu_window)
        options_grid.grid()

        # Speed
        text = tk.StringVar(options_grid)
        text.set("Maximum FPS")
        label = tk.Label(options_grid, textvariable=text)
        label.grid(column=0, row=0)

        self.current_speed_option = tk.StringVar(
            options_grid, FPS_OPTIONS[self.speedlimit]
        )
        speeds = tk.OptionMenu(
            options_grid,
            self.current_speed_option,
            *FPS_OPTIONS,
            command=self.speed_option_changed,
        )
        speeds.grid(column=1, row=0)

        # Learning rate
        text = tk.StringVar(options_grid)
        text.set("Learning rate")
        label = tk.Label(options_grid, textvariable=text)
        label.grid(column=0, row=1)

        scale = tk.Scale(
            options_grid,
            from_=0,
            to=0.5,
            orient="horizontal",
            resolution=0.05,
            command=self.learning_rate_changed,
        )
        scale.set(self.model.agent.learning_rate)
        scale.grid(column=1, row=1)

        # Exploration rate
        text = tk.StringVar(options_grid)
        text.set("Exploration rate")
        label = tk.Label(options_grid, textvariable=text)
        label.grid(column=0, row=2)

        scale = tk.Scale(
            options_grid,
            from_=0,
            to=1,
            orient="horizontal",
            resolution=0.05,
            command=self.exploration_rate_changed,
        )
        scale.set(self.model.agent.exploration_rate)
        scale.grid(column=1, row=2)

        # Decay rate
        text = tk.StringVar(options_grid)
        text.set("Reward decay rate")
        label = tk.Label(options_grid, textvariable=text)
        label.grid(column=0, row=3)

        scale = tk.Scale(
            options_grid,
            from_=0,
            to=1,
            orient="horizontal",
            resolution=0.05,
            command=self.decay_changed,
        )
        scale.set(self.model.agent.decay)
        scale.grid(column=1, row=3)

        # Close button
        button = tk.Button(
            self.menu_window, text="Close", command=self.close_options_menu
        )
        button.grid(sticky="e", padx=(10, 10), pady=(10, 10))

    def bind_directions(self):
        self.bindings = []

        for index, direction in enumerate(DIRECTIONS_NAMES):
            bind = self.root.bind(
                f"<{DIRECTIONS_FULL_NAMES[index]}>",
                lambda e, dir=direction: self.move_snake(
                    get_direction_vector(dir)
                ),
            )
            self.bindings.append(bind)

        bind = self.root.bind("<space>", lambda e: self.step())
        self.bindings.append(bind)

    def unbind_directions(self):
        for index, direction_full in enumerate(DIRECTIONS_NAMES):
            self.root.unbind(f"<{direction_full}>", self.bindings[index])

    def update_displayed_qvalues(self):
        self.snake_size.set(len(self.model.board.snake_pos))

        state, order, _ = self.model.interpreter.calculate_state(
            self.model.board
        )

        for index, qvalue in enumerate(self.q_values):
            if state >= 0:
                qvalue.set(
                    round(
                        self.model.agent.states[state][
                            order.index(DIRECTIONS_NAMES[index])
                        ],
                        2,
                    )
                )

    def save_q_values(self):
        q_values_file = filedialog.asksaveasfilename(
            title="File name",
            initialdir="./",
            filetypes=(("Replay files", "*.qval"), ("All files", "*.*")),
            defaultextension=".qval",
        )

        self.model.save_qval = q_values_file

        self.model.save_qvalues_file()

    def load_q_values(self):
        q_values_file = filedialog.askopenfilename(
            title="Open a Q values file",
            initialdir="./",
            filetypes=(("Replay files", "*.qval"), ("All files", "*.*")),
        )

        try:
            self.model.agent.states = numpy.loadtxt(q_values_file)
        except FileNotFoundError:
            return

    def open_replay_file(self):
        replay_filename = filedialog.askopenfilename(
            title="Open a replay file",
            initialdir="./",
            filetypes=(("Replay files", "*.rpl"), ("All files", "*.*")),
        )

        try:
            with open(replay_filename, "r") as fd:
                replay_data = json.load(fd)
        except FileNotFoundError:
            return

        self.model.board.set_board(replay_data)
        self.model.board.lost = False

        self.inputs = replay_data["inputs"]
        self.replay_mode = True

        self.draw_board()
        self.replay_frame.grid()

    def close_options_menu(self):
        self.menu_window.destroy()

    def speed_option_changed(self, *args):
        self.speedlimit = FPS_OPTIONS.index(self.current_speed_option.get())

    def learning_rate_changed(self, *args):
        self.model.agent.learning_rate = float(args[0])

    def exploration_rate_changed(self, *args):
        self.model.agent.exploration_rate = float(args[0])

    def decay_changed(self, *args):
        self.model.agent.decay = float(args[0])

    def exit_replay(self):
        self.replay_mode = False
        self.stop()
        self.replay_frame.grid_remove()

    def step(self):
        if not self.model.board.lost:
            if self.replay_mode and len(self.inputs) > 0:
                self.move_snake(self.inputs.pop(0))
            elif self.replay_mode:
                self.replay_mode = False
            else:
                self.model.new_step()
        else:
            new_board = board.Board()
            self.model.board = new_board

        self.draw_board()
        self.update_displayed_qvalues()
        self.root.update_idletasks()
        self.root.update()

    def move_snake(self, direction):
        self.model.board.move_snake(direction)
        self.draw_board()
        self.update_displayed_qvalues()

    def update_board(self, board):
        self.model.board = board
        self.draw_board()

    def draw_board(self):
        if self.model.board.lost:
            return

        tile_size = BOARD_HEIGHT / self.model.board.board_size

        canvas = self.board_frame
        canvas.delete("all")

        board_area = self.model.board.area.T

        # Connect the snake
        if self.model.board.lost is False:
            for index, _ in enumerate(self.model.board.snake_pos):
                if len(self.model.board.snake_pos) > index + 1:
                    canvas.create_rectangle(
                        tile_size
                        * (
                            (
                                self.model.board.snake_pos[index][0]
                                + self.model.board.snake_pos[index + 1][0]
                            )
                            / 2
                        ),
                        tile_size
                        * (
                            (
                                self.model.board.snake_pos[index][1]
                                + self.model.board.snake_pos[index + 1][1]
                            )
                            / 2
                        ),
                        tile_size
                        * (
                            (
                                (
                                    self.model.board.snake_pos[index][0]
                                    + self.model.board.snake_pos[index + 1][0]
                                )
                                / 2
                            )
                            + 1
                        ),
                        tile_size
                        * (
                            (
                                (
                                    self.model.board.snake_pos[index][1]
                                    + self.model.board.snake_pos[index + 1][1]
                                )
                                / 2
                            )
                            + 1
                        ),
                        outline="",
                        fill="blue",
                    )

        # Draw the elements
        for column_index, column in enumerate(board_area):
            for index, tile in enumerate(column):
                if self.model.board.lost is False:
                    canvas.create_oval(
                        tile_size * (index + 1),
                        tile_size * (column_index + 1),
                        tile_size * index,
                        tile_size * column_index,
                        outline="",
                        fill=COLORS[TILES.index(tile)],
                    )

    def stop_learning(self):
        self.model.no_learning = True
        self.learning_button.config(
            text="Resume learning", command=self.resume_learning
        )

    def resume_learning(self):
        self.model.no_learning = False
        self.learning_button.config(
            text="Stop learning", command=self.stop_learning
        )

    def stop(self):
        self.stopped = True
        self.pausebutton.config(text="Resume", command=self.start)
        self.controls_frame.grid()
        self.bind_directions()

    def start(self):
        if self.stopped:
            self.stopped = False
            self.pausebutton.config(text="Pause", command=self.stop)
            self.controls_frame.grid_remove()
            self.unbind_directions()

            self.start_loop(resume=True)

    def start_loop(self, resume=False):
        prevtime = time.time()

        while self.stopped is False:
            max_time = SPEED_LIMITS[self.speedlimit]

            while self.model.board.lost is False:
                if self.replay_mode and len(self.inputs) > 0:
                    self.move_snake(self.inputs.pop(0))
                elif self.replay_mode:
                    self.replay_mode = False
                else:
                    self.model.new_step()
                self.draw_board()
                self.update_displayed_qvalues()
                self.root.update_idletasks()
                self.root.update()

                if self.speedlimit:  # Limit FPS
                    to_sleep = max_time - (time.time() - prevtime)
                    if to_sleep > 0:
                        time.sleep(to_sleep)
                    prevtime = time.time()
                if self.stopped:
                    break

            if self.replay_mode:
                self.replay_mode = False
                self.stop()

            if self.stopped is False and not resume:
                new_board = board.Board()
                self.model.board = new_board
            resume = False

        # Start the GUI event loop
        self.root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Learn2slither GUI",
        description="GUI of Q Learning program for the game Snake",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=False,
        help="The file to load Q values from",
    )
    parser.add_argument(
        "-n",
        "--no-learning",
        action="store_true",
        help="Stops the Q values from updating as it happens",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase output verbosity",
    )

    args = parser.parse_args()
    model = learn2slither.Qlearner(load_qval=args.input)

    gui = GraphicalInterface(
        model, no_learning=args.no_learning, verbose=args.verbose
    )
    gui.draw_board()
    gui.start_loop()
