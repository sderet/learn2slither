import tkinter as tk
import board
import interpreter
import time

TILES = ["0", "H", "S", "G", "R"]
COLORS = ["white", "skyblue", "blue", "green", "red"]

DIRECTIONS_NAMES = ["U", "D", "L", "R"]
DIRECTIONS = [[0, -1], [0, 1], [-1, 0], [1, 0]]

def get_direction_vector(name):
    return DIRECTIONS[DIRECTIONS_NAMES.index(name)]

class GraphicalInterface:
    def __init__(self, gui_board = board.Board(), interpreter = interpreter.Interpreter()):
        self.board = gui_board
        self.interpreter = interpreter

        self.stopped = False

        # Create the main window
        self.root = tk.Tk()

        self.root.title("Learn2Slither")

        self.board_frame = tk.Frame(self.root)
        self.board_frame.grid()

        self.update_button = tk.Button(self.root, text = "Update board", command=lambda: self.update_board(board.Board()))
        self.update_button.grid()
        self.update_button = tk.Button(self.root, text = "Stop training", command=self.stop)
        self.update_button.grid()
        self.update_button = tk.Button(self.root, text = "Start training", command=self.start)
        self.update_button.grid()

        self.controls_frame = tk.Frame(self.root)

        up = tk.Button(self.controls_frame, text = "Up", command=lambda: self.move_snake(get_direction_vector("U")))
        up.grid(column=1, row=0)
        left = tk.Button(self.controls_frame, text = "Left", command=lambda: self.move_snake(get_direction_vector("L")))
        left.grid(column=0, row=1)
        right = tk.Button(self.controls_frame, text = "Right", command=lambda: self.move_snake(get_direction_vector("R")))
        right.grid(column=2, row=1)
        down = tk.Button(self.controls_frame, text = "Down", command=lambda: self.move_snake(get_direction_vector("D")))
        down.grid(column=1, row=2)

        self.controls_frame.grid()

    def move_snake(self, direction):
        self.board.move_snake(direction)
        self.draw_board()

    def update_board(self, board):
        self.board = board
        self.draw_board()

    def draw_board(self):
        #self.drawn_board = [[]]
        for widget in self.board_frame.winfo_children():
            #print(widget)
            widget.destroy()

        for column_index, column in enumerate(self.board.area):
            for index, tile in enumerate(column):
                if (self.board.lost == False):
                    tile = tk.Canvas(self.board_frame, bg=COLORS[TILES.index(tile)], height=20, width=20)
                else:
                    tile = tk.Canvas(self.board_frame, bg="white", height=20, width=20)
                tile.grid(row=index, column=column_index)

    def stop(self):
        self.stopped = True

    def start(self):
        if self.stopped:
            self.stopped = False
            self.start_loop()

    def start_loop(self):
        while self.stopped == False:
            while self.board.lost == False:
                self.interpreter.new_step()
                self.draw_board()
                self.root.update_idletasks()
                self.root.update()
                #time.sleep(0.1)
                if self.stopped == True:
                    break
            #self.interpreter.save_qvalues()

            new_board = board.Board()
            self.interpreter.board = new_board
            self.board = new_board
    
        # Start the GUI event loop
        self.root.mainloop()

if __name__ == "__main__":
    base_board = board.Board()
    base_interpreter = interpreter.Interpreter(base_board, load_model="values.qval", sessions=100)

    gui = GraphicalInterface(base_board, base_interpreter)
    gui.draw_board()
    gui.start_loop()
