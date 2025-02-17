import tkinter as tk
import board

TILES = ["0", "H", "S", "G", "R"]
COLORS = ["white", "skyblue", "blue", "green", "red"]

class GraphicalInterface:
    def __init__(self, gui_board = board.Board()):
        self.board = gui_board

        # Create the main window
        self.root = tk.Tk()

        self.root.title("Learn2Slither")

        self.board_frame = tk.Frame(self.root)
        self.board_frame.grid()

        self.update_button = tk.Button(self.root, text = "Update board", command=lambda: self.update_board(board.Board()))
        self.update_button.grid()

        self.controls_frame = tk.Frame(self.root)

        up = tk.Button(self.controls_frame, text = "Up", command=lambda: self.move_snake([0, -1]))
        up.grid(column=1, row=0)
        left = tk.Button(self.controls_frame, text = "Left", command=lambda: self.move_snake([-1, 0]))
        left.grid(column=0, row=1)
        right = tk.Button(self.controls_frame, text = "Right", command=lambda: self.move_snake([1, 0]))
        right.grid(column=2, row=1)
        down = tk.Button(self.controls_frame, text = "Down", command=lambda: self.move_snake([0, 1]))
        down.grid(column=1, row=2)

        self.controls_frame.grid()

    def move_snake(self, direction):
        self.board.move_snake(direction)
        self.draw_board()

    def update_board(self, board):
        self.board = board
        self.draw_board()

    def draw_board(self):
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        for column_index, column in enumerate(self.board.area):
            for index, tile in enumerate(column):
                if (self.board.lost == False):
                    tile = tk.Canvas(self.board_frame, bg=COLORS[TILES.index(tile)], height=20, width=20)
                else:
                    tile = tk.Canvas(self.board_frame, bg="white", height=20, width=20)
                tile.grid(row=index, column=column_index)

    def add_label(self, label):
        # Create a label widget
        label = tk.Label(self.root, text=label)
        label.grid()

    def start_loop(self):
        # Start the GUI event loop
        self.root.mainloop()

if __name__ == "__main__":
    base_board = board.Board()

    gui = GraphicalInterface()
    gui.draw_board()
    gui.start_loop()