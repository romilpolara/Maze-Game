import tkinter as tk
import random
import time
from PIL import Image, ImageTk
from tkinter import font as tkFont

# Maze settings
ROWS, COLS = 23, 35
CELL_SIZE = 28
LEVEL_TIME = 60

def load_custom_font():
    return tkFont.Font(family="Roboto", size=24)

# Maze generation function (same as before)
def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]
    def carve_path(x, y):
        maze[y][x] = 0
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0
                carve_path(nx, ny)
    carve_path(1, 1)
    maze[1][1] = maze[height - 2][width - 2] = 0
    return maze

mazes = [generate_maze(COLS, ROWS) for _ in range(10)]

class MazeGame:
    def __init__(self, master):
        self.master = master
        self.master.title("3D Maze Game")

        self.Heading_color = "#990F02"
        self.bg_color = "#000000"
        self.wall_color = "#592D1D"
        self.player_color = "#4CAF50"
        self.goal_color = "#FFC107"
        self.text_color = "#FFDF00"
        self.level_color = "#FFFFFF"

        self.canvas = tk.Canvas(self.master, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE + 100, bg=self.bg_color)
        self.canvas.pack()

        self.state = "start"
        self.level = 0
        self.start_time = 0
        self.time_left = LEVEL_TIME
        self.player_pos = [1, 1]
        self.is_moving = False  # To track if player is moving
        # Load player frames for each direction
        self.right_frames = [
            ImageTk.PhotoImage(Image.open(f"image/Player/player_right_{i}.png").resize((CELL_SIZE - 4, CELL_SIZE - 4), Image.Resampling.LANCZOS))
            for i in range(0, 5)
        ]
        self.left_frames = [
            ImageTk.PhotoImage(Image.open(f"image/Player/player_left_{i}.png").resize((CELL_SIZE - 4, CELL_SIZE - 4), Image.Resampling.LANCZOS))
            for i in range(0, 5)
        ]
        self.up_frames = [
            ImageTk.PhotoImage(Image.open(f"image/Player/player_up_{i}.png").resize((CELL_SIZE - 4, CELL_SIZE - 4), Image.Resampling.LANCZOS))
            for i in range(0, 5)
        ]
        self.down_frames = [
            ImageTk.PhotoImage(Image.open(f"image/Player/player_buttom_{i}.png").resize((CELL_SIZE - 4, CELL_SIZE - 4), Image.Resampling.LANCZOS))
            for i in range(0, 5)
        ]

        self.current_frame = 0  # Initialize the current frame index
        self.current_frames = self.right_frames  # Default to right-facing animation
        self.animation_direction = "right"  # Default direction

        self.master.bind("<KeyPress>", self.on_key_press)
        self.master.bind("<KeyRelease>", self.on_key_release)  # New binding for key release


        self.draw_start_screen()

    def draw_start_screen(self):
        self.canvas.delete("all")

        # Load the GIF image
        self.gif_image = Image.open("image/start.gif")
        self.gif_frames = []
        for i in range(self.gif_image.n_frames):
            self.gif_image.seek(i)
            frame = self.gif_image.copy()
            frame = frame.resize((1050, 1050))
            photo = ImageTk.PhotoImage(frame)
            self.gif_frames.append(photo)

        self.gif_index = 0
        self.gif_image_id = self.canvas.create_image(
            COLS * CELL_SIZE // 2, ROWS * CELL_SIZE // 2,
            image=self.gif_frames[self.gif_index]
        )

        self.animation_count = 0
        self.max_animations = 1

        self.animate_gif()
        self.master.after(4000, self.draw_level_select_screen)

    def animate_gif(self):
        if self.animation_count < self.max_animations:
            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            self.canvas.itemconfig(self.gif_image_id, image=self.gif_frames[self.gif_index])

            if self.gif_index == 0:
                self.animation_count += 1

            self.master.after(70, self.animate_gif)
        else:
            self.draw_level_select_screen()

    def draw_level_select_screen(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            COLS * CELL_SIZE / 2, ROWS * CELL_SIZE / 4,
            text="Select Level", fill=self.Heading_color, font=("Arial", 36)
        )
        left_x = COLS * CELL_SIZE / 4
        right_x = 3 * COLS * CELL_SIZE / 4
        margin_top = 50
        starting_y = ROWS * CELL_SIZE / 3 + margin_top

        for i in range(5):
            self.canvas.create_text(
                left_x, starting_y + i * 55,
                text=f"Level {i + 1}", fill=self.text_color, font=("Arial", 24),
                tags=f"level_{i + 1}"
            )

        for i in range(5, 10):
            self.canvas.create_text(
                right_x, starting_y + (i - 5) * 55,
                text=f"Level {i + 1}", fill=self.text_color, font=("Arial", 24),
                tags=f"level_{i + 1}"
            )

        self.canvas.create_line(
            COLS * CELL_SIZE / 2, ROWS * CELL_SIZE / 3 - 10,
            COLS * CELL_SIZE / 2, ROWS * CELL_SIZE, fill="white", width=4
        )
        self.canvas.bind("<Button-1>", self.on_level_select)

    def draw_game_over_screen(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            COLS * CELL_SIZE / 2, ROWS * CELL_SIZE / 3,
            text="Game Over", fill="red", font=("Arial", 36, "bold")
        )
        self.canvas.create_text(
            COLS * CELL_SIZE / 2, ROWS * CELL_SIZE / 2,
            text="Press R to Restart", fill=self.Heading_color, font=("Arial", 24)
        )

    def draw_level_screen(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            COLS * CELL_SIZE / 2, ROWS * CELL_SIZE / 2,
            text=f"Level {self.level + 1}", fill=self.text_color, font=("Arial", 36)
        )
        self.master.after(2000, self.start_game)

    def start_game(self):
        self.state = "playing"
        self.player_pos = [1, 1]
        self.start_time = time.time()
        self.time_left = LEVEL_TIME
        self.draw_maze()
        self.draw_player()
        self.draw_goal()
        self.update_timer()

    def draw_maze(self):
        self.canvas.delete("all")
        maze = mazes[self.level]
        self.wall_image_horizontal = ImageTk.PhotoImage(Image.open("image/block_01.png").resize((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS))
        self.wall_image_vertical = ImageTk.PhotoImage(Image.open("image/block_05.png").resize((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS))

        # for y in range(ROWS):
        #     for x in range(COLS):
        #         if maze[y][x] == 1:
        #             if x > 0 and maze[y][x - 1] == 1 or x < COLS - 1 and maze[y][x + 1] == 1:
        #                 self.canvas.create_image(
        #                     x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2,
        #                     image=self.wall_image_horizontal
        #                 )
        #             elif y > 0 and maze[y - 1][x] == 1 or y < ROWS - 1 and maze[y + 1][x] == 1:
        #                 self.canvas.create_image(
        #                     x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2,
        #                     image=self.wall_image_vertical
        #                 )
        
        for y in range(ROWS):
            for x in range(COLS):
                if maze[y][x] == 1:
                    # Check for horizontal walls
                    if (x > 0 and maze[y][x - 1] == 1) or (x < COLS - 1 and maze[y][x + 1] == 1):
                        self.canvas.create_image(
                            x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2,
                            image=self.wall_image_horizontal
                        )
                    # Check for vertical walls
                    if (y > 0 and maze[y - 1][x] == 1) or (y < ROWS - 1 and maze[y + 1][x] == 1):
                        self.canvas.create_image(
                            x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2,
                            image=self.wall_image_vertical
                        )
                    # Check for bottom wall
                    if y < ROWS - 1 and maze[y + 1][x] == 1:
                        self.canvas.create_image(
                            x * CELL_SIZE + CELL_SIZE // 2, (y + 1) * CELL_SIZE - CELL_SIZE // 2,
                            image=self.wall_image_horizontal
                        )


    def draw_player(self):
        self.canvas.delete("player")
        self.canvas.create_image(
            self.player_pos[0] * CELL_SIZE + CELL_SIZE // 2,
            self.player_pos[1] * CELL_SIZE + CELL_SIZE // 2,
            image=self.current_frames[self.current_frame],
            tags="player"
        )

        if self.is_moving:  # Only update the frame if the player is moving
            self.current_frame = (self.current_frame + 1) % len(self.current_frames)
            self.master.after(100, self.draw_player)


    def draw_goal(self):
        goal_image = ImageTk.PhotoImage(Image.open("image/crate_31.png").resize((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS))
        self.canvas.create_image(
            (COLS - 2) * CELL_SIZE + CELL_SIZE // 2, (ROWS - 2) * CELL_SIZE + CELL_SIZE // 2,
            image=goal_image, tags="goal"
        )

    def update_timer(self):
        self.time_left = LEVEL_TIME - (time.time() - self.start_time)
        self.canvas.delete("timer")
        self.canvas.create_text(
            COLS * CELL_SIZE // 2, ROWS * CELL_SIZE + 50,
            text=f"Time Left: {int(self.time_left)}", fill=self.text_color, font=("Arial", 24), tags="timer"
        )
        if self.time_left <= 0:
            self.state = "game_over"
            self.draw_game_over_screen()
        elif self.state == "playing":
            self.master.after(1000, self.update_timer)

    def on_level_select(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        tags = self.canvas.gettags(item)
        if tags and tags[0].startswith("level_"):
            self.level = int(tags[0].split("_")[1]) - 1
            self.draw_level_screen()

    def on_key_press(self, event):
        if self.state != "playing":
            return

        x, y = self.player_pos
        maze = mazes[self.level]
        moved = False

        if event.keysym == "Right" and maze[y][x + 1] == 0:
            self.player_pos[0] += 1
            self.current_frames = self.right_frames
            moved = True
        elif event.keysym == "Left" and maze[y][x - 1] == 0:
            self.player_pos[0] -= 1
            self.current_frames = self.left_frames
            moved = True
        elif event.keysym == "Up" and maze[y - 1][x] == 0:
            self.player_pos[1] -= 1
            self.current_frames = self.up_frames
            moved = True
        elif event.keysym == "Down" and maze[y + 1][x] == 0:
            self.player_pos[1] += 1
            self.current_frames = self.down_frames
            moved = True

        if moved:
            self.is_moving = True  # Set moving flag
            self.current_frame = 0  # Reset to the first frame
            self.draw_player()  # Start animation
            
    def on_key_release(self, event):
        if event.keysym in ["Right", "Left", "Up", "Down"]:
            self.is_moving = False  # Stop the animation

if __name__ == "__main__":
    root = tk.Tk()
    game = MazeGame(root)
    root.mainloop()
    
