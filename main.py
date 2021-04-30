import pygame
import time

from pygame.locals import *


BACKGROUND_COLOR = (58, 178, 186)
SCREEN_SIZE = (800, 600)
SIZE = 20
BASE_COORD = 100


class Snake:
    def __init__(self, screen, length):
        self.brick = pygame.image.load("resources/brick.png")
        self.screen = screen
        self.length = length
        self.x_coords = [BASE_COORD] * length
        self.y_coords = [BASE_COORD] * length
        self.direction = 'down'

    def move_up(self):
        self.direction = 'up'

    def move_down(self):
        self.direction = 'down'

    def move_left(self):
        self.direction = 'left'

    def move_right(self):
        self.direction = 'right'

    def update_move(self):
        for i in range(self.length-1, 0, -1):
            self.x_coords[i] = self.x_coords[i-1]
            self.y_coords[i] = self.y_coords[i-1]

        if self.direction == 'up':
            self.y_coords[0] -= SIZE
        elif self.direction == 'down':
            self.y_coords[0] += SIZE
        elif self.direction == 'right':
            self.x_coords[0] += SIZE
        elif self.direction == 'left':
            self.x_coords[0] -= SIZE
        self.draw()

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        for i in range(self.length):
            self.screen.blit(self.brick, (self.x_coords[i], self.y_coords[i]))
        pygame.display.update()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.screen.fill(BACKGROUND_COLOR)
        self.snake = Snake(self.screen, 7)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_UP:
                        self.snake.move_up()
                    elif event.key == K_DOWN:
                        self.snake.move_down()
                    elif event.key == K_LEFT:
                        self.snake.move_left()
                    elif event.key == K_RIGHT:
                        self.snake.move_right()
                elif event.type == QUIT:
                    exit(0)
            self.snake.update_move()
            time.sleep(0.3)

if __name__ == "__main__":
    game = Game()
    game.run()
