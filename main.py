import pygame
import time
import random

from pygame.locals import *

from fireworks import Firework, update as update_fireworks


BACKGROUND_COLOR = (58, 178, 186)
SCREEN_SIZE = (800, 600)
SIZE = 20
BASE_COORD = 100


class Apple:
    def __init__(self, screen, snake_x_coords, snake_y_coords):
        self.snake_x_coords = snake_x_coords
        self.snake_y_coords = snake_y_coords
        self.x, self.y = self._get_xy()
        self.screen = screen
        self.image = pygame.image.load("resources/images/apple.png")

    def draw(self):
        self.screen.blit(self.image, (self.x, self.y))
        pygame.display.update()

    def _get_xy(self):
        while True:
            x = self._get_random_coord(0)
            y = self._get_random_coord(1)
            if x not in self.snake_x_coords and y not in self.snake_y_coords:
                return x, y

    @staticmethod
    def _get_random_coord(pos):
        return random.randint(0, (SCREEN_SIZE[pos] // SIZE - 1)) * SIZE


class Snake:
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    HEAD_INDEX = 0
    WIDTH_INDEX = 0
    HEIGHT_INDEX = 1

    def __init__(self, screen, length):
        self.brick = pygame.image.load("resources/images/brick.png")
        self.screen = screen
        self.length = length
        self.x_coords = [BASE_COORD] * length
        self.y_coords = [BASE_COORD] * length
        self.direction = self.DOWN
        self.prev_direction = self.DOWN

    def _switch_direction(self, direction):
        self.direction = direction
        self.prev_direction = direction

    def move_up(self):
        if self.prev_direction != self.DOWN or self.length < 2:
            self._switch_direction(self.UP)

    def move_down(self):
        if self.prev_direction != self.UP or self.length < 2:
            self._switch_direction(self.DOWN)

    def move_left(self):
        if self.prev_direction != self.RIGHT or self.length < 2:
            self._switch_direction(self.LEFT)

    def move_right(self):
        if self.prev_direction != self.LEFT or self.length < 2:
            self._switch_direction(self.RIGHT)

    def _check_border_collision(self):
        if self.x_coords[self.HEAD_INDEX] < 0:
            self.x_coords[self.HEAD_INDEX] = SCREEN_SIZE[self.WIDTH_INDEX]
        elif self.x_coords[self.HEAD_INDEX] > SCREEN_SIZE[self.WIDTH_INDEX]:
            self.x_coords[self.HEAD_INDEX] = 0
        elif self.y_coords[self.HEAD_INDEX] < 0:
            self.y_coords[self.HEAD_INDEX] = SCREEN_SIZE[self.HEIGHT_INDEX]
        elif self.y_coords[self.HEAD_INDEX] > SCREEN_SIZE[self.HEIGHT_INDEX]:
            self.y_coords[self.HEAD_INDEX] = 0

    def update_move(self):
        for i in range(self.length - 1, 0, -1):
            self.x_coords[i] = self.x_coords[i - 1]
            self.y_coords[i] = self.y_coords[i - 1]

        if self.direction == self.UP:
            self.y_coords[self.HEAD_INDEX] -= SIZE
        elif self.direction == self.DOWN:
            self.y_coords[self.HEAD_INDEX] += SIZE
        elif self.direction == self.RIGHT:
            self.x_coords[self.HEAD_INDEX] += SIZE
        elif self.direction == self.LEFT:
            self.x_coords[self.HEAD_INDEX] -= SIZE

        self._check_border_collision()
        self.draw()

    def increase_length(self):
        self.length += 1
        self.x_coords.append(-1)
        self.y_coords.append(-1)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        for i in range(self.length):
            self.screen.blit(self.brick, (self.x_coords[i], self.y_coords[i]))
        pygame.display.update()


class Button:
    def __init__(self, image_path, position):
        self.position = position
        self.image = pygame.image.load(image_path)
        self.image_rect = None

    def draw(self, screen):
        self.image_rect = self.image.get_rect(center=self.position)
        screen.blit(self.image, self.image_rect)

    def event_handler(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.image_rect.collidepoint(event.pos):
                    return True


class Game:
    INIT_SNAKE_LENGTH = 1
    SPEED = 0.3
    SPEED_DIFFERENCE = 0.005
    SNAKE_HEAD_INDEX = 0

    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.snake = None
        self.apple = None
        self.score = None
        self.paused = None
        self.play_button = None
        self.close_button = None
        self.best_score = None
        self.new_high_score = None
        self.init_game()

    def init_game(self):
        self.screen.fill(BACKGROUND_COLOR)
        self._play_background_music()
        self.snake = Snake(self.screen, self.INIT_SNAKE_LENGTH)
        self.apple = Apple(self.screen, self.snake.x_coords, self.snake.y_coords)
        self.score = self.INIT_SNAKE_LENGTH
        self.paused = False
        self.new_high_score = False
        self.play_button = None
        self.close_button = None
        with open("resources/best_score.txt", "r") as best_score_file:
            self.best_score = best_score_file.read()

    def display_score(self):
        font = pygame.font.SysFont('arial', 30)
        score_counter = font.render(f"Score: {self.score}", True, (255, 255, 255))
        best_score = font.render(f"Best Score: {self.best_score}", True, (255, 255, 255))
        self.screen.blit(score_counter, (SCREEN_SIZE[0]-200, 10))
        self.screen.blit(best_score, (SCREEN_SIZE[0]-200, 40))

    def play(self):
        self.snake.update_move()
        self.display_score()
        if self.is_collision(self.snake.x_coords[self.SNAKE_HEAD_INDEX], self.snake.y_coords[self.SNAKE_HEAD_INDEX], self.apple.x, self.apple.y):
            self._play_sound("ding.wav")
            self.snake.increase_length()
            self.score = self.snake.length
            self.SPEED -= self.SPEED_DIFFERENCE
            self.draw_new_apple()
        for i in range(2, self.snake.length):
            if self.is_collision(self.snake.x_coords[self.SNAKE_HEAD_INDEX], self.snake.y_coords[self.SNAKE_HEAD_INDEX], self.snake.x_coords[i], self.snake.y_coords[i]):
                self._play_sound("hit.wav")
                self.game_over()
        self.apple.draw()
        time.sleep(self.SPEED)

    @staticmethod
    def _play_sound(filename):
        sound = pygame.mixer.Sound(f"resources/sounds/{filename}")
        pygame.mixer.Sound.play(sound)

    @staticmethod
    def _play_background_music():
        playlist = ["cut-man.mp3", "elec-man.mp3", "fire-man.mp3", "ice-man.mp3", "password.mp3", "stage.mp3", "title.mp3"]
        filename = random.choice(playlist)
        pygame.mixer.music.load(f"resources/music/{filename}")
        pygame.mixer.music.play()

    def _update_best_score(self):
        if self.score > int(self.best_score):
            self.new_high_score = True
            with open("resources/best_score.txt", "w") as best_score_file:
                best_score_file.write(str(self.score))

    def _draw_game_over_buttons(self):
        self.play_button = Button("resources/images/play_button.png", (SCREEN_SIZE[0] / 2 - 100, SCREEN_SIZE[1] - 200))
        self.close_button = Button("resources/images/close_button.png", (SCREEN_SIZE[0] / 2 + 100, SCREEN_SIZE[1] - 200))
        self.play_button.draw(self.screen)
        self.close_button.draw(self.screen)

    def _draw_message(self, message, font_size, font_color, position, bold):
        font = pygame.font.SysFont("arial", font_size, bold)
        text = font.render(message, True, font_color)
        text_rect = text.get_rect(center=position)
        self.screen.blit(text, text_rect)

    def _draw_game_over_message(self):
        if self.score > int(self.best_score):
            high_score_message = f"New High Score: {self.score}"
        else:
            high_score_message = f"Your Score: {self.score}"
        game_over_message = "GAME OVER"

        self._draw_message(game_over_message, 60, (255, 255, 255), (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/3), True)
        self._draw_message(high_score_message, 40, (255, 255, 255), (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2.2), False)

    def game_over_with_new_high_score(self, fireworks):
        self.screen.fill(BACKGROUND_COLOR)
        if random.randint(0, 20) == 1:
            fireworks.append(Firework())
        self._draw_game_over_message()
        self._draw_game_over_buttons()
        self._draw_game_over_message()
        update_fireworks(self.screen, fireworks)

    def game_over(self):
        pygame.mixer.music.pause()
        self.screen.fill(BACKGROUND_COLOR)
        self.paused = True
        self._update_best_score()
        self._draw_game_over_buttons()
        self._draw_game_over_message()

    def draw_new_apple(self):
        self.apple = Apple(self.screen, self.snake.x_coords, self.snake.y_coords)

    @staticmethod
    def is_collision(x1, y1, x2, y2):
        return x1 == x2 and y1 == y2

    def restart_game(self):
        self.init_game()
        self.run()

    def run(self):
        fireworks = []
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
                if self.paused and self.close_button.event_handler(event):
                    exit(0)
                elif self.paused and self.play_button.event_handler(event):
                    self.restart_game()
                elif event.type == QUIT:
                    exit(0)
            if not self.paused:
                self.play()
            if self.new_high_score:
                self.game_over_with_new_high_score(fireworks)


if __name__ == "__main__":
    game = Game()
    game.run()
