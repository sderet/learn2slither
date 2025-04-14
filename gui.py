import tkinter as tk
from tkinter import filedialog
import board
import interpreter
import time

TILES = ["0", "H", "S", "G", "R"]
COLORS = ["white", "skyblue", "blue", "green", "red"]

DIRECTIONS_NAMES = ["U", "D", "L", "R"]
DIRECTIONS = [[0, -1], [0, 1], [-1, 0], [1, 0]]

BOARD_HEIGHT = 300

FPS_OPTIONS = ["Unlimited", "120", "60", "30", "15", "5", "1"]
SPEED_LIMITS = [0, 1/120, 1/60, 1/30, 1/15, 1/5, 1]

def get_direction_vector(name):
    return DIRECTIONS[DIRECTIONS_NAMES.index(name)]

class GraphicalInterface:
    def __init__(self, gui_board = board.Board(), interpreter = interpreter.Interpreter(), speedlimit = 0, stopped = False):
        self.board = gui_board
        self.interpreter = interpreter

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

        # Movement buttons
        self.controls_frame = tk.Frame(self.root)

        up = tk.Button(self.controls_frame, text = "Up", command=lambda: self.move_snake(get_direction_vector("U")))
        up.grid(column=1, row=0)
        left = tk.Button(self.controls_frame, text = "Left", command=lambda: self.move_snake(get_direction_vector("L")))
        left.grid(column=0, row=1)
        right = tk.Button(self.controls_frame, text = "Right", command=lambda: self.move_snake(get_direction_vector("R")))
        right.grid(column=2, row=1)
        down = tk.Button(self.controls_frame, text = "Down", command=lambda: self.move_snake(get_direction_vector("D")))
        down.grid(column=1, row=2)
        if stopped:
            self.controls_frame.grid()

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
        self.board.move_snake(direction)
        self.draw_board()

    def update_board(self, board):
        self.board = board
        self.draw_board()

    def draw_board(self):
        tile_size = BOARD_HEIGHT / self.board.board_size

        canvas = self.board_frame
        canvas.delete("all")

        board_area = self.board.area.T

        # Connect the snake
        if (self.board.lost == False):
            for index, _ in enumerate(self.board.snake_pos):
                if (len(self.board.snake_pos) > index + 1):
                    canvas.create_rectangle(
                        tile_size * ((self.board.snake_pos[index][0] + self.board.snake_pos[index + 1][0]) / 2), tile_size * ((self.board.snake_pos[index][1] + self.board.snake_pos[index + 1][1]) / 2),
                        tile_size * (((self.board.snake_pos[index][0] + self.board.snake_pos[index + 1][0]) / 2) + 1), tile_size * (((self.board.snake_pos[index][1] + self.board.snake_pos[index + 1][1]) / 2) + 1),
                        outline='', fill="blue"
                    )

        # Draw the elements
        for column_index, column in enumerate(board_area):
            for index, tile in enumerate(column):
                if (self.board.lost == False):
                    canvas.create_oval(
                        tile_size * (index + 1), tile_size * (column_index + 1),
                        tile_size * index, tile_size * column_index,
                        outline='', fill=COLORS[TILES.index(tile)])

    def stop(self):
        self.stopped = True
        self.pausebutton.config(text = "Resume", command=self.start)
        self.controls_frame.grid()

    def start(self):
        if self.stopped:
            self.stopped = False
            self.pausebutton.config(text = "Pause", command=self.stop)
            self.controls_frame.grid_remove()
            
            self.start_loop(resume=True)

    def start_loop(self, resume=False):
        prevtime = time.time()

        while self.stopped == False:
            max_time = SPEED_LIMITS[self.speedlimit]

            while self.board.lost == False:
                self.interpreter.new_step()
                self.draw_board()
                self.root.update_idletasks()
                self.root.update()

                # Limit FPSes
                if (self.speedlimit):
                    to_sleep = max_time - (time.time() - prevtime)
                    if (to_sleep > 0):
                        time.sleep(to_sleep)
                    prevtime = time.time()
                if self.stopped == True:
                    break
            #self.interpreter.save_qvalues()

            if not resume:
                new_board = board.Board()
                self.interpreter.board = new_board
                self.board = new_board
            resume = False
    
        # Start the GUI event loop
        self.root.mainloop()

if __name__ == "__main__":
    base_board = board.Board()
    base_interpreter = interpreter.Interpreter(base_board, load_model="values.qval", sessions=100)

    gui = GraphicalInterface(base_board, base_interpreter)
    gui.draw_board()
    gui.start_loop()
