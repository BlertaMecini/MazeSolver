import random
import pygame
import heapq
import time
import math

# Start Pygame to manage graphics and user input
pygame.init()

# Define colors with RGB values for visual consistency
WHITE = (255, 255, 255)      # Background and open paths
BLACK = (0, 0, 0)            # Walls and text
RED = (255, 80, 80)          # End position marker
GREEN = (80, 255, 80)        # Start position marker
BLUE = (100, 100, 255)       # Cells visited during solving
GRAY = (150, 150, 150)       # Default button color
DARK_GRAY = (100, 100, 100)  # Button outlines and shadows
YELLOW = (255, 255, 100)     # Path when maze is solved
LIGHT_GRAY = (200, 200, 200) # Button color on hover
SHADOW = (50, 50, 50, 100)   # Shadow effect with transparency
MENU_TOP = (180, 220, 255)   # Top color for menu gradient
MENU_BOTTOM = (80, 120, 180) # Bottom color for menu gradient

# Set window and cell dimensions
CELL_SIZE = 16               # Size of each maze cell in pixels
WINDOW_WIDTH = 1000          # Window width in pixels
WINDOW_HEIGHT = 800          # Window height in pixels
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # Create display window
pygame.display.set_caption("Maze Solver")  # Set window title

# Fonts for different UI elements
font = pygame.font.SysFont("Arial", 32, bold=True)      # For buttons and metrics
title_font = pygame.font.SysFont("Arial", 48, bold=True)  # For titles
alert_font = pygame.font.SysFont("Arial", 60, bold=True)  # For alert messages
close_font = pygame.font.SysFont("Arial", 28, bold=True)  # For alert dismiss "X"

# Maze difficulty options with base sizes (rows, cols)
DIFFICULTIES = {
    "Easy": (10, 10),
    "Medium": (20, 20),
    "Hard": (30, 30)
}

class Button:
    # A reusable button class for UI interaction
    def __init__(self, x, y, width, height, text, action, font=font):
        self.rect = pygame.Rect(x, y, width, height)  # Button's bounding box
        self.text = font.render(text, True, WHITE)    # Rendered text for button
        self.action = action                          # Function to call on click

    def draw(self, screen):
        # Draw button with shadow, hover effect, and outline
        mouse = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse)
        pygame.draw.rect(screen, SHADOW, self.rect.move(5, 5), border_radius=15)
        if hover:
            pygame.draw.rect(screen, LIGHT_GRAY, self.rect, border_radius=15)
        else:
            pygame.draw.rect(screen, GRAY, self.rect, border_radius=15)
        pygame.draw.rect(screen, DARK_GRAY, self.rect, 2, border_radius=15)
        screen.blit(self.text, self.text.get_rect(center=self.rect.center))

    def handle_click(self, pos):
        # Trigger action if button is clicked
        if self.rect.collidepoint(pos):
            self.action()

class MazeGame:
    # Main game class managing state, maze, and UI
    def __init__(self):
        self.state = "menu"          # Current state: menu, playing, solving, solved
        self.difficulty = None       # Selected difficulty level
        self.maze = None             # 2D grid: 1 = wall, 0 = path
        self.start = None            # Start position (row, col)
        self.end = None              # End position (row, col)
        self.path = []               # List of coordinates for solved path
        self.visited = set()         # Set of visited cells during solving
        self.iterations = 0          # Count of A* steps
        self.time = 0                # Time taken to solve maze
        self.alert_message = None    # Message for alert (e.g., "Maze Solved!")
        self.alert_color = BLACK     # Color of alert text
        self.alert_start_time = None # Timestamp for alert animation
        # Menu buttons for difficulty selection
        btn_w = 220
        btn_h = 60
        start_y = (WINDOW_HEIGHT - (len(DIFFICULTIES) * (btn_h + 20) - 20)) // 2
        self.menu_buttons = []
        for i, (level, (rows, cols)) in enumerate(DIFFICULTIES.items()):
            x = WINDOW_WIDTH // 2 - btn_w // 2
            y = start_y + i * (btn_h + 20)
            action = lambda lvl=level, r=rows, c=cols: self.set_difficulty(lvl, r, c)
            self.menu_buttons.append(Button(x, y, btn_w, btn_h, level, action))
        self.play_buttons = []       # Buttons for "playing" state
        self.solved_buttons = []     # Buttons for "solved" state

    def set_difficulty(self, level, rows, cols):
        # Set difficulty, generate maze, and switch to playing state
        self.difficulty = level
        self.generate_maze(rows, cols)
        self.state = "playing"
        btn_w = 140
        btn_h = 50
        self.play_buttons = [
            Button(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 80, btn_w, btn_h, "Start", self.start_solving),
            Button(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 140, btn_w, btn_h, "Back", self.back_to_menu)
        ]
        self.solved_buttons = []

    def start_solving(self):
        # Start A* solving process and animate it
        self.state = "solving"
        self.path = []
        self.visited = set()
        self.iterations = 0
        start_time = time.time()
        solver = self.a_star()
        for _ in solver:
            self.iterations += 1
            self.draw()
            pygame.display.flip()
            pygame.time.wait(10)  # Small delay to make solving visible
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
        self.time = time.time() - start_time
        self.state = "solved"
        self.alert_message = "Maze Solved!"
        self.alert_color = GREEN
        self.alert_start_time = time.time()
        btn_w = 140
        btn_h = 50
        self.solved_buttons = [
            Button(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 80, btn_w, btn_h, "Restart", self.restart),
            Button(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 140, btn_w, btn_h, "Back", self.back_to_menu)
        ]

    def back_to_menu(self):
        # Reset game to menu state
        self.state = "menu"
        self.maze = None
        self.difficulty = None
        self.play_buttons = []
        self.solved_buttons = []
        self.alert_message = None
        self.alert_start_time = None

    def restart(self):
        # Regenerate maze and return to playing state
        self.generate_maze(len(self.maze), len(self.maze[0]))
        self.state = "playing"
        self.path = []
        self.visited = set()
        self.iterations = 0
        self.time = 0
        self.alert_message = None
        self.alert_start_time = None
        btn_w = 140
        btn_h = 50
        self.play_buttons = [
            Button(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 80, btn_w, btn_h, "Start", self.start_solving),
            Button(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 140, btn_w, btn_h, "Back", self.back_to_menu)
        ]
        self.solved_buttons = []

    def heuristic(self, a, b):
        # Manhattan distance heuristic for A*: estimates cost between two points
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self):
        # A* algorithm: finds shortest path from start to end using a heuristic
        # Uses a priority queue to explore cells with lowest f_score (g + h)
        queue = [(0, self.start)]  # Queue of (f_score, position) tuples
        g_score = {self.start: 0}  # Cost from start to each cell
        f_score = {self.start: self.heuristic(self.start, self.end)}  # Estimated total cost
        came_from = {}  # Tracks parent of each cell for path reconstruction

        while queue:  # Loop until queue is empty or goal is found
            current = heapq.heappop(queue)[1]  # Get cell with lowest f_score
            if current == self.end:  # If end is reached, build and return path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(self.start)
                self.path = path[::-1]  # Reverse path to go from start to end
                return

            self.visited.add(current)  # Mark cell as explored
            yield  # Yield to allow step-by-step visualization

            # Check all four adjacent cells (right, down, left, up)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                # Validate neighbor: in bounds, not a wall, not visited
                if (0 <= neighbor[0] < len(self.maze) and 
                    0 <= neighbor[1] < len(self.maze[0]) and 
                    self.maze[neighbor[0]][neighbor[1]] == 0 and 
                    neighbor not in self.visited):
                    tentative_g = g_score[current] + 1  # Cost to move is 1
                    # If this is a new or cheaper path, update scores
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current  # Record parent
                        g_score[neighbor] = tentative_g  # Update cost so far
                        f_score[neighbor] = tentative_g + self.heuristic(neighbor, self.end)  # Update total cost
                        heapq.heappush(queue, (f_score[neighbor], neighbor))  # Add to queue

    def draw(self):
        # Render the current game state
        if self.state == "menu":
            self.draw_menu()
        else:
            screen.fill(WHITE)
            self.draw_maze()
            self.draw_alert()

    def draw_menu(self):
        # Draw menu with gradient background and difficulty buttons
        for y in range(WINDOW_HEIGHT):
            t = y / WINDOW_HEIGHT
            r = int(MENU_TOP[0] * (1 - t) + MENU_BOTTOM[0] * t)
            g = int(MENU_TOP[1] * (1 - t) + MENU_BOTTOM[1] * t)
            b = int(MENU_TOP[2] * (1 - t) + MENU_BOTTOM[2] * t)
            pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

        title = title_font.render("Maze Solver", True, BLACK)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))

        for button in self.menu_buttons:
            button.draw(screen)

    def draw_maze(self):
        # Draw maze grid, title, metrics, and buttons based on state
        maze_w = len(self.maze[0]) * CELL_SIZE
        maze_h = len(self.maze) * CELL_SIZE
        off_x = (WINDOW_WIDTH - maze_w) // 2  # Center maze horizontally
        off_y = (WINDOW_HEIGHT - maze_h - 150) // 2 + 100  # Center with space for title

        if self.difficulty:
            title = title_font.render(f"{self.difficulty} Maze", True, BLACK)
            screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 30))
            if self.state == "solved":
                title_h = title.get_height()
                time_text = font.render(f"Time: {self.time:.2f}s", True, BLACK)
                iter_text = font.render(f"Iterations: {self.iterations}", True, BLACK)
                screen.blit(time_text, (WINDOW_WIDTH // 2 - time_text.get_width() // 2, 40 + title_h))
                screen.blit(iter_text, (WINDOW_WIDTH // 2 - iter_text.get_width() // 2, 80 + title_h))

        # Render each cell with appropriate color
        for i in range(len(self.maze)):
            for j in range(len(self.maze[0])):
                if self.maze[i][j] == 1:
                    color = BLACK  # Wall
                elif (i, j) == self.start:
                    color = GREEN  # Start point
                elif (i, j) == self.end:
                    color = RED    # End point
                elif (i, j) in self.path:
                    color = YELLOW  # Solved path
                elif (i, j) in self.visited:
                    color = BLUE    # Visited during solving
                else:
                    color = WHITE   # Open path
                pygame.draw.rect(screen, color, (off_x + j * CELL_SIZE, off_y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, GRAY, (off_x + j * CELL_SIZE, off_y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        # Draw state-specific buttons
        if self.state == "playing":
            for button in self.play_buttons:
                button.draw(screen)
        elif self.state == "solved":
            for button in self.solved_buttons:
                button.draw(screen)

    def draw_alert(self):
        # Draw alert message with pulsing effect and dismiss button
        if self.alert_message:
            alert_text = alert_font.render(self.alert_message, True, self.alert_color)
            alert_rect = alert_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

            # Calculate scale for pulsing effect (oscillates for 3 seconds)
            if self.alert_start_time:
                elapsed = time.time() - self.alert_start_time
                if elapsed < 3:
                    scale = 1 + 0.1 * math.sin(elapsed * 6)  # Oscillate between 0.9 and 1.1
                else:
                    scale = 1
            else:
                scale = 1

            # Create a surface for the alert with padding
            padding = 60
            alert_surface = pygame.Surface((alert_rect.width + padding, alert_rect.height + padding), pygame.SRCALPHA)
            alert_surface.fill((0, 0, 0, 0))  # Transparent background
            pygame.draw.rect(alert_surface, SHADOW, (10, 10, alert_rect.width + padding - 10, alert_rect.height + padding - 10), border_radius=20)
            pygame.draw.rect(alert_surface, WHITE, (0, 0, alert_rect.width + padding, alert_rect.height + padding), border_radius=20)
            pygame.draw.rect(alert_surface, DARK_GRAY, (0, 0, alert_rect.width + padding, alert_rect.height + padding), 3, border_radius=20)
            alert_surface.blit(alert_text, (padding // 2, padding // 2))

            # Scale and blit the alert surface
            scaled_surface = pygame.transform.smoothscale(alert_surface, 
                                                          (int(alert_surface.get_width() * scale), 
                                                           int(alert_surface.get_height() * scale)))
            scaled_rect = scaled_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(scaled_surface, scaled_rect)

            # Draw the "X" button
            close_text = close_font.render("X", True, BLACK)
            close_rect = pygame.Rect(scaled_rect.right + 15 * scale, scaled_rect.top - 15 * scale, 40 * scale, 40 * scale)
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = close_rect.collidepoint(mouse_pos)
            pygame.draw.circle(screen, SHADOW, close_rect.center, int(25 * scale))
            color = LIGHT_GRAY if is_hovered else GRAY
            pygame.draw.circle(screen, color, close_rect.center, int(20 * scale))
            pygame.draw.circle(screen, DARK_GRAY, close_rect.center, int(20 * scale), 2)
            close_text_scaled = pygame.transform.smoothscale(close_text, 
                                                             (int(close_text.get_width() * scale), 
                                                              int(close_text.get_height() * scale)))
            close_text_rect = close_text_scaled.get_rect(center=close_rect.center)
            screen.blit(close_text_scaled, close_text_rect)

            # Dismiss alert if "X" is clicked
            if pygame.mouse.get_pressed()[0] and close_rect.collidepoint(mouse_pos):
                self.alert_message = None
                self.alert_start_time = None

    def generate_maze(self, rows, cols):
        # Generate a random maze using recursive backtracking (DFS algorithm)
        if rows % 2 == 0: rows += 1  # Ensure odd rows for proper wall/path structure
        if cols % 2 == 0: cols += 1  # Ensure odd cols for proper wall/path structure
        maze = [[1 for _ in range(cols)] for _ in range(rows)]  # Initialize grid with walls (1)
        visited = set()  # Track cells visited during DFS

        def carve(x, y):
            # Recursive DFS to carve paths through the maze
            maze[x][y] = 0  # Mark current cell as a path
            visited.add((x, y))  # Add to visited set
            dirs = [(0, 2), (2, 0), (0, -2), (-2, 0)]  # Directions: right, down, left, up (step by 2)
            random.shuffle(dirs)  # Randomize directions for maze variety
            for dx, dy in dirs:
                new_x = x + dx
                new_y = y + dy
                # Check if new position is valid and unvisited
                if (0 <= new_x < rows and 0 <= new_y < cols and 
                    (new_x, new_y) not in visited):
                    maze[x + dx//2][y + dy//2] = 0  # Carve wall between current and new cell
                    carve(new_x, new_y)  # Recursively carve from new position

        maze[1][1] = 0  # Start carving from an inner cell
        carve(1, 1)  # Begin DFS maze generation
        
        maze[0][0] = 0  # Ensure start position is open
        maze[rows-1][cols-1] = 0  # Ensure end position is open
        # Ensure start is connected if surrounded by walls
        if maze[0][1] == 1 and maze[1][0] == 1:
            maze[0][1] = 0  # Open a path to the right
        end_x = rows-1
        end_y = cols-1
        # Ensure end is connected if not reached by DFS
        if (end_x, end_y) not in visited:
            if end_x > 1 and maze[end_x-1][end_y] == 0:
                maze[end_x-2][end_y] = 0  # Connect from above
            elif end_y > 1 and maze[end_x][end_y-1] == 0:
                maze[end_x][end_y-2] = 0  # Connect from left
            else:
                maze[rows-2][cols-1] = 0  # Fallback: open vertical path
                maze[rows-3][cols-1] = 0

        # Add extra paths to increase maze complexity
        walls = []
        for i in range(rows):
            for j in range(cols):
                if maze[i][j] == 1:
                    walls.append((i, j))  # Collect all wall positions
        random.shuffle(walls)  # Shuffle for random extra paths
        extra = int((rows * cols) * 0.1)  # Target 10% of cells for extra paths
        for i in range(min(extra, len(walls))):
            x, y = walls[i]
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]  # Check four neighbors
            open_count = 0
            for nx, ny in neighbors:
                if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 0:
                    open_count += 1  # Count adjacent open paths
            if open_count >= 2:
                maze[x][y] = 0  # Remove wall if it connects multiple paths

        self.maze = maze
        self.start = (0, 0)
        self.end = (rows-1, cols-1)
        self.path = []
        self.visited = set()

def main():
    # Main loop: initialize game and handle events
    game = MazeGame()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if game.state == "menu":
                    for button in game.menu_buttons:
                        button.handle_click(pos)
                elif game.state == "playing":
                    for button in game.play_buttons:
                        button.handle_click(pos)
                elif game.state == "solved":
                    for button in game.solved_buttons:
                        button.handle_click(pos)

        game.draw()
        pygame.display.flip()
        clock.tick(60)  # Cap frame rate at 60 FPS

if __name__ == "__main__":
    main()