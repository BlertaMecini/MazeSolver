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
CELL_SIZE = 16
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Maze Solver")

# Fonts for different UI elements
font = pygame.font.SysFont("Arial", 32, bold=True)
title_font = pygame.font.SysFont("Arial", 48, bold=True)
alert_font = pygame.font.SysFont("Arial", 60, bold=True)
close_font = pygame.font.SysFont("Arial", 28, bold=True)

# Maze difficulty options with base sizes
DIFFICULTIES = {
    "Easy": (10, 10),
    "Medium": (20, 20),
    "Hard": (30, 30)
}

class Button:
    def __init__(self, x, y, width, height, text, action, font=font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = font.render(text, True, WHITE)
        self.action = action

    def draw(self, screen):
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
        if self.rect.collidepoint(pos):
            self.action()

class MazeGame:
    def __init__(self):
        self.state = "menu"
        self.difficulty = None
        self.maze = None
        self.start = None
        self.end = None
        self.path = []
        self.visited = set()
        self.iterations = 0
        self.time = 0
        self.alert_message = None
        self.alert_color = BLACK
        self.alert_start_time = None
        # Menu buttons
        btn_w = 220
        btn_h = 60
        start_y = (WINDOW_HEIGHT - (len(DIFFICULTIES) * (btn_h + 20) - 20)) // 2
        self.menu_buttons = []
        for i, (level, (rows, cols)) in enumerate(DIFFICULTIES.items()):
            x = WINDOW_WIDTH // 2 - btn_w // 2
            y = start_y + i * (btn_h + 20)
            action = lambda lvl=level, r=rows, c=cols: self.set_difficulty(lvl, r, c)
            self.menu_buttons.append(Button(x, y, btn_w, btn_h, level, action))
        # Playing and solved state buttons
        self.play_buttons = []
        self.solved_buttons = []

    def set_difficulty(self, level, rows, cols):
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
            pygame.time.wait(10)
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
        self.state = "menu"
        self.maze = None
        self.difficulty = None
        self.play_buttons = []
        self.solved_buttons = []
        self.alert_message = None
        self.alert_start_time = None

    def restart(self):
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
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self):
        queue = [(0, self.start)]
        g_score = {self.start: 0}
        f_score = {self.start: self.heuristic(self.start, self.end)}
        came_from = {}

        while queue:
            current = heapq.heappop(queue)[1]
            if current == self.end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(self.start)
                self.path = path[::-1]
                return

            self.visited.add(current)
            yield

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if (0 <= neighbor[0] < len(self.maze) and 
                    0 <= neighbor[1] < len(self.maze[0]) and 
                    self.maze[neighbor[0]][neighbor[1]] == 0 and 
                    neighbor not in self.visited):
                    tentative_g = g_score[current] + 1
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + self.heuristic(neighbor, self.end)
                        heapq.heappush(queue, (f_score[neighbor], neighbor))

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        else:
            screen.fill(WHITE)
            self.draw_maze()
            self.draw_alert()

    def draw_menu(self):
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
        maze_w = len(self.maze[0]) * CELL_SIZE
        maze_h = len(self.maze) * CELL_SIZE
        off_x = (WINDOW_WIDTH - maze_w) // 2
        off_y = (WINDOW_HEIGHT - maze_h - 150) // 2 + 100

        if self.difficulty:
            title = title_font.render(f"{self.difficulty} Maze", True, BLACK)
            screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 30))
            if self.state == "solved":
                title_h = title.get_height()
                time_text = font.render(f"Time: {self.time:.2f}s", True, BLACK)
                iter_text = font.render(f"Iterations: {self.iterations}", True, BLACK)
                screen.blit(time_text, (WINDOW_WIDTH // 2 - time_text.get_width() // 2, 40 + title_h))
                screen.blit(iter_text, (WINDOW_WIDTH // 2 - iter_text.get_width() // 2, 80 + title_h))

        for i in range(len(self.maze)):
            for j in range(len(self.maze[0])):
                if self.maze[i][j] == 1:
                    color = BLACK
                elif (i, j) == self.start:
                    color = GREEN
                elif (i, j) == self.end:
                    color = RED
                elif (i, j) in self.path:
                    color = YELLOW
                elif (i, j) in self.visited:
                    color = BLUE
                else:
                    color = WHITE
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
        if rows % 2 == 0: rows += 1
        if cols % 2 == 0: cols += 1
        maze = [[1 for _ in range(cols)] for _ in range(rows)]
        visited = set()

        def carve(x, y):
            maze[x][y] = 0
            visited.add((x, y))
            dirs = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                new_x = x + dx
                new_y = y + dy
                if (0 <= new_x < rows and 0 <= new_y < cols and 
                    (new_x, new_y) not in visited):
                    maze[x + dx//2][y + dy//2] = 0
                    carve(new_x, new_y)

        maze[1][1] = 0
        carve(1, 1)
        
        maze[0][0] = 0
        maze[rows-1][cols-1] = 0
        if maze[0][1] == 1 and maze[1][0] == 1:
            maze[0][1] = 0
        end_x = rows-1
        end_y = cols-1
        if (end_x, end_y) not in visited:
            if end_x > 1 and maze[end_x-1][end_y] == 0:
                maze[end_x-2][end_y] = 0
            elif end_y > 1 and maze[end_x][end_y-1] == 0:
                maze[end_x][end_y-2] = 0
            else:
                maze[rows-2][cols-1] = 0
                maze[rows-3][cols-1] = 0

        walls = []
        for i in range(rows):
            for j in range(cols):
                if maze[i][j] == 1:
                    walls.append((i, j))
        random.shuffle(walls)
        extra = int((rows * cols) * 0.1)
        for i in range(min(extra, len(walls))):
            x, y = walls[i]
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            open_count = 0
            for nx, ny in neighbors:
                if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 0:
                    open_count += 1
            if open_count >= 2:
                maze[x][y] = 0

        self.maze = maze
        self.start = (0, 0)
        self.end = (rows-1, cols-1)
        self.path = []
        self.visited = set()

def main():
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
        clock.tick(60)

if __name__ == "__main__":
    main()