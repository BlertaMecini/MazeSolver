import pygame

# Start Pygame to manage graphics and user input
pygame.init()
# Define colors with RGB values for visual consistency
WHITE = (255, 255, 255)      # Background and open paths
BLACK = (0, 0, 0)            # Walls and text
GRAY = (150, 150, 150)       # Default button color
DARK_GRAY = (100, 100, 100)  # Button outlines and shadows
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

# Maze difficulty options with base sizes
DIFFICULTIES = {
    "Easy": (10, 10),
    "Medium": (20, 20),
    "Hard": (30, 30)
}

class MazeGame:
    def __init__(self):
        # Initialize game variables
        self.state = "menu"          # Current game mode: menu, playing, solving, solved
        self.difficulty = None       # Selected difficulty level

    def draw(self):
        if self.state == "menu":
                # draw the main menu of app   
            self.draw_menu()

    def draw_menu(self):
        # Render menu with gradient background and difficulty buttons
        # Gradient transitions from top to bottom color
        for y in range(WINDOW_HEIGHT):
            t = y / WINDOW_HEIGHT  # Fraction of height (0 to 1)
            r = int(MENU_TOP[0] * (1 - t) + MENU_BOTTOM[0] * t)  # Blend red
            g = int(MENU_TOP[1] * (1 - t) + MENU_BOTTOM[1] * t)  # Blend green
            b = int(MENU_TOP[2] * (1 - t) + MENU_BOTTOM[2] * t)  # Blend blue
            pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

        # Draw centered title
        title = title_font.render("Maze Solver", True, BLACK)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 80))

        # Position difficulty buttons vertically centered
        btn_w = 220
        btn_h = 60
        start_y = (WINDOW_HEIGHT - (len(DIFFICULTIES) * (btn_h + 20) - 20)) // 2
        for i, (level, _) in enumerate(DIFFICULTIES.items()):
            text = font.render(level, True, WHITE)
            rect = pygame.Rect(WINDOW_WIDTH//2 - btn_w//2, start_y + i * (btn_h + 20), btn_w, btn_h)
            mouse = pygame.mouse.get_pos()
            hover = rect.collidepoint(mouse)
            # Add shadow for depth
            pygame.draw.rect(screen, SHADOW, rect.move(5, 5), border_radius=15)
            # Change color on hover
            if hover:
                pygame.draw.rect(screen, LIGHT_GRAY, rect, border_radius=15)
            else:
                pygame.draw.rect(screen, GRAY, rect, border_radius=15)
            pygame.draw.rect(screen, DARK_GRAY, rect, 2, border_radius=15)  # Outline
            screen.blit(text, text.get_rect(center=rect.center))


def main():
    # Main loop to run the game
    game = MazeGame()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Exit if window closed
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                pos = pygame.mouse.get_pos()
                if game.state == "menu":
                    # Check clicks on difficulty buttons
                   return
                
        game.draw()
        pygame.display.flip()
        clock.tick(60) 

if __name__ == "__main__":
    main()