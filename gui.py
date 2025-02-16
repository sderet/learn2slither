import tkinter as tk
import board

TILES = ["0", "H", "S", "G", "R"]
COLORS = ["white", "skyblue", "blue", "green", "red"]

class GraphicalInterface:
    def __init__(self):
        # Create the main window
        self.root = tk.Tk()

        self.root.title("Learn2Slither")

        self.board_frame = tk.Frame(self.root)
        self.board_frame.grid()

        self.update_button = tk.Button(self.root, text = "Update board", command=lambda: self.draw_board(board.Board()))
        self.update_button.grid()

    def draw_board(self, board):
        for column_index, column in enumerate(board.area):
            for index, tile in enumerate(column):
                tile = tk.Canvas(self.board_frame, bg=COLORS[TILES.index(tile)], height=20, width=20)
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
    gui.draw_board(base_board)
    gui.start_loop()