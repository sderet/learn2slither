import tkinter as tk
from tkinter import filedialog
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
SPEED_LIMITS = [0, 1/120, 1/60, 1/30, 1/15, 1/5, 1]

def get_direction_vector(name):
    return DIRECTIONS[DIRECTIONS_NAMES.index(name)]

class GraphicalInterface:
    def __init__(self, model=learn2slither.Qlearner(), speedlimit = 2, stopped = False):
        self.model = model

        self.speedlimit = speedlimit

        self.stopped = False

        # Create the main window
        self.root = tk.Tk()

        self.root.title("Learn2Slither")

        self.board_frame = tk.Canvas(self.root, width=BOARD_HEIGHT, height=BOARD_HEIGHT, bg="ivory")
        self.board_frame.grid()

        if stopped:
            self.pausebutton = tk.Button(self.root, text = "Resume", command=self.start)
        else:
            self.pausebutton = tk.Button(self.root, text = "Pause", command=self.stop)
        self.pausebutton.grid(column=0, sticky="w")
        button = tk.Button(self.root, text = "Options", command=self.init_options_menu)
        button.grid(column=0, sticky="w")

        button = tk.Button(self.root, text = "Reset", command=lambda: self.update_board(board.Board()))
        button.grid(column=0, row=1, sticky="e")
        button = tk.Button(self.root, text = "Load replay", command=self.open_replay_file)
        button.grid(column=0, row=2, sticky="e")

        # Q values
        self.q_values_frame = tk.Frame(self.root)

        text = tk.StringVar(self.q_values_frame)
        text.set("Q values:")
        label = tk.Label(self.q_values_frame, textvariable=text)
        label.grid(column=0, row=0)

        self.q_values = []
        for index, qvalue in enumerate(DIRECTIONS):
            qvalue = tk.StringVar(self.q_values_frame, 0)
            label = tk.Label(self.q_values_frame, textvariable=qvalue)
            label.grid(column=1 + DIRECTIONS[index][0], row=2 + DIRECTIONS[index][1])
            self.q_values.append(qvalue)

        self.update_displayed_qvalues()

        self.q_values_frame.grid(row=0, column=1)

        # Movement buttons
        self.controls_frame = tk.Frame(self.root)

        for index, direction in enumerate(DIRECTIONS_NAMES):
            button = tk.Button(self.controls_frame, text = DIRECTIONS_FULL_NAMES[index], command=lambda dir=direction: self.move_snake(get_direction_vector(dir)))
            button.grid(column=1 + DIRECTIONS[index][0], row=2 + DIRECTIONS[index][1])

        if stopped:
            self.controls_frame.grid()
            self.bind_directions()

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

        self.current_speed_option = tk.StringVar(options_grid, FPS_OPTIONS[self.speedlimit])
        speeds = tk.OptionMenu(options_grid, self.current_speed_option, *FPS_OPTIONS, command=self.speed_option_changed)
        speeds.grid(column=1, row=0)

        # Close button
        button = tk.Button(self.menu_window, text = "Close", command=self.close_options_menu)
        button.grid(sticky="e")

    def bind_directions(self):
        self.bindings = []

        for index, direction in enumerate(DIRECTIONS_NAMES):
            bind = self.root.bind(f"<{DIRECTIONS_FULL_NAMES[index]}>", lambda e, dir=direction: self.move_snake(get_direction_vector(dir)))
            self.bindings.append(bind)

    def unbind_directions(self):
        for index, direction_full in enumerate(DIRECTIONS_NAMES):
            self.root.unbind(f"<{direction_full}>", self.bindings[index])

    # Might be leaking something?
    def update_displayed_qvalues(self):
        state, order, _ = self.model.interpreter.calculate_state(self.model.board)

        for index, qvalue in enumerate(self.q_values):
            if (state >= 0):
                qvalue.set(round(self.model.agent.states[state][order.index(DIRECTIONS_NAMES[index])], 2))

    def open_replay_file(self):
        replay_filename = filedialog.askopenfilename(
            title= "Open a replay file",
            initialdir="./",
            filetypes=(("Replay files", "*.rpl"), ("All files", "*.*"))
        )
        print(replay_filename)
        ## TODO: finish this function
        

    def close_options_menu(self):
        self.menu_window.destroy()

    def speed_option_changed(self, *args):
        self.speedlimit = FPS_OPTIONS.index(self.current_speed_option.get())

    def move_snake(self, direction):
        print(self.model.interpreter.calculate_vision(self.model.board))
        self.model.board.move_snake(direction)
        self.draw_board()
        self.update_displayed_qvalues()
        print(self.model.interpreter.calculate_vision(self.model.board))

    def update_board(self, board):
        self.model.board = board
        self.draw_board()

    def draw_board(self):
        tile_size = BOARD_HEIGHT / self.model.board.board_size

        canvas = self.board_frame
        canvas.delete("all")

        board_area = self.model.board.area.T

        # Connect the snake
        if (self.model.board.lost == False):
            for index, _ in enumerate(self.model.board.snake_pos):
                if (len(self.model.board.snake_pos) > index + 1):
                    canvas.create_rectangle(
                        tile_size * ((self.model.board.snake_pos[index][0] + self.model.board.snake_pos[index + 1][0]) / 2), tile_size * ((self.model.board.snake_pos[index][1] + self.model.board.snake_pos[index + 1][1]) / 2),
                        tile_size * (((self.model.board.snake_pos[index][0] + self.model.board.snake_pos[index + 1][0]) / 2) + 1), tile_size * (((self.model.board.snake_pos[index][1] + self.model.board.snake_pos[index + 1][1]) / 2) + 1),
                        outline='', fill="blue"
                    )

        # Draw the elements
        for column_index, column in enumerate(board_area):
            for index, tile in enumerate(column):
                if (self.model.board.lost == False):
                    canvas.create_oval(
                        tile_size * (index + 1), tile_size * (column_index + 1),
                        tile_size * index, tile_size * column_index,
                        outline='', fill=COLORS[TILES.index(tile)])

    def stop(self):
        self.stopped = True
        self.pausebutton.config(text = "Resume", command=self.start)
        self.controls_frame.grid()
        self.bind_directions()

    def start(self):
        if self.stopped:
            self.stopped = False
            self.pausebutton.config(text = "Pause", command=self.stop)
            self.controls_frame.grid_remove()
            self.unbind_directions()
            
            self.start_loop(resume=True)

    def start_loop(self, resume=False):
        prevtime = time.time()

        while self.stopped == False:
            max_time = SPEED_LIMITS[self.speedlimit]

            while self.model.board.lost == False:
                self.model.new_step()
                self.draw_board()
                self.update_displayed_qvalues()
                self.root.update_idletasks()
                self.root.update()

                if (self.speedlimit): # Limit FPS
                    to_sleep = max_time - (time.time() - prevtime)
                    if (to_sleep > 0):
                        time.sleep(to_sleep)
                    prevtime = time.time()
                if self.stopped == True:
                    break

            if self.stopped == False and not resume:
                new_board = board.Board()
                self.model.board = new_board
            resume = False
    
        # Start the GUI event loop
        self.root.mainloop()

if __name__ == "__main__":
    model = learn2slither.Qlearner(load_qval="values.qval")

    gui = GraphicalInterface(model)
    gui.draw_board()
    gui.start_loop()
