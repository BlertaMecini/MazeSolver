import pygame

# Start Pygame to manage graphics and user input
pygame.init()

# Set window and cell dimensions
CELL_SIZE = 16
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Maze Solver")


font = pygame.font.SysFont("Arial", 32, bold=True)

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
            return         


def main():
    # Main loop to run the game
    game = MazeGame()

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

if __name__ == "__main__":
    main()