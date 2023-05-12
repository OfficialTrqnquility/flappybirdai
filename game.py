import math
import random

import pygame


class Game:
    def __init__(self, nets=None, training=False):
        self.nets = nets
        self.training = training

        self.running = True

        self.display_width = 600
        self.display_height = 800

        self.FPS = 60

        self.scroll_speed = 3
        self.ground_x = 0

        self.pipe_gap = 75
        self.pipe_frequency = 90
        self.ticks_till_next_pipe = 0

        self.default_bird_x = 100
        self.default_bird_y = 300

        pygame.init()

        self.display = pygame.display.set_mode((self.display_width, self.display_height))

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(None, 25)
        self.background_image = pygame.image.load("assets/background.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (self.display_width, self.display_height))
        self.floor_image = pygame.image.load("assets/floor.png").convert_alpha()
        self.floor_image = pygame.transform.scale(self.floor_image, (self.display_width + 41, self.display_height / 6))
        self.pipe_image = pygame.image.load("assets/pipe.png").convert_alpha()
        self.pipe_image = pygame.transform.scale(self.pipe_image,
                                                 (self.pipe_image.get_width(), self.pipe_image.get_height() * 2))
        self.bird_image = pygame.image.load("assets/bird.png").convert_alpha()

        self.floor_width = self.floor_image.get_width()
        self.floor_images = math.ceil(self.floor_width / self.display_width)

        pygame.display.set_caption("Flappy Bird!!!")

    def draw_text(self, text, x, y, color=(255, 255, 255)):
        surface = self.font.render(text, True, color)
        self.display.blit(surface, [x, y])

    def run(self):

        self.score = 0

        self.pipe_group = pygame.sprite.Group()
        self.bird_group = pygame.sprite.Group()
        self.last_pipe = pygame.time.get_ticks() / self.pipe_frequency

        if self.nets:
            for net in self.nets:
                self.bird_group.add(Bird(self.default_bird_x, self.default_bird_y, self.bird_image, net[0], net[1]))
        else:
            self.bird_group.add(Bird(self.default_bird_x, self.default_bird_y, self.bird_image))


        while self.running:
            self.game_loop()

        results = list(map(lambda bird: (bird.genome_id, bird.fitness), self.bird_group))

        pygame.quit()

        return results

    def game_loop(self):
        jump = False

        all_dead = all(not bird.alive for bird in self.bird_group)
        if all_dead:
            self.running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    self.FPS = 60
                if event.key == pygame.K_F2:
                    self.FPS = 300
                if event.key == pygame.K_F3:
                    self.FPS = 500
                if event.key == pygame.K_F4:
                    self.FPS = 5000
                if event.key == pygame.K_q:

                    for bird in self.bird_group:
                        bird.alive = False

            if not self.training:
                if not self.nets:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            jump = True

        self.bird_group.update(jump, self.pipe_group)

        # Compute Pipes and Score
        self.ticks_till_next_pipe -= 1
        if self.ticks_till_next_pipe <= 0:
            self.ticks_till_next_pipe = self.pipe_frequency
            if pygame.time.get_ticks() > 3000 / self.FPS / 60:
                self.score += 1

            pipe_height = random.randint(-100, 100)
            top_pipe = Pipe(self.display_width, int(self.display_height / 2) + pipe_height, True, self.pipe_gap,
                            self.pipe_image)
            bottom_pipe = Pipe(self.display_width, int(self.display_height / 2) + pipe_height, False, self.pipe_gap,
                               self.pipe_image)
            self.pipe_group.add(top_pipe)
            self.pipe_group.add(bottom_pipe)

        self.pipe_group.update(self.scroll_speed)

        # Compute scroll
        self.ground_x -= self.scroll_speed
        if abs(self.ground_x) > self.floor_width:
            self.ground_x = 0

        # Clear Screen

        self.display.blit(self.background_image, (0, 0))

        # Draw Here

        # Draw Pipes
        self.pipe_group.draw(self.display)

        # Draw Birds
        self.bird_group.draw(self.display)

        # Draw Ground
        for i in range(0, self.floor_images):
            self.display.blit(self.floor_image, (i * self.floor_width + self.ground_x, self.display_height - 120))

        # Draw Text

        self.draw_text(str(self.score), 30, 30, "white")

        # Render Screen

        pygame.display.flip()

        self.clock.tick(self.FPS)


class Pipe(pygame.sprite.Sprite):

    def __init__(self, x, y, top, pipe_gap, image):
        super().__init__()

        self.image = image
        self.rect = image.get_rect()

        if top:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - pipe_gap]
        else:
            self.rect.topleft = [x, y + pipe_gap]

    def update(self, scroll_speed):
        self.rect.x -= scroll_speed

        if self.rect.x < -50:
            self.kill()


class Bird(pygame.sprite.Sprite):

    def __init__(self, x, y, image, genome_id=None, net=None):
        super().__init__()
        self.base_image = image
        self.image = image
        self.rect = image.get_rect()
        self.rect.topleft = [x, y]
        self.velocity = 0
        self.alive = True

        self.fitness = 0
        self.net = net
        self.genome_id = genome_id

    def update(self, jump, pipes):
        if self.net is not None:
            jump = self.shouldJump(pipes)

        if self.rect.x < -50:
            return

        if pygame.sprite.spritecollideany(self, pipes):
            self.alive = False

        if self.alive:
            self.fitness += 0.01

            if jump:
                self.velocity = -8
            else:
                self.velocity = min(self.velocity + 0.5, 10)
        else:
            self.velocity += 1
            self.rect.x -= 3

        if self.alive:
            if self.velocity < 0:
                self.image = pygame.transform.rotate(self.base_image.copy(), 30)
            else:
                self.image = pygame.transform.rotate(self.base_image.copy(), -30)
        else:
            self.image = pygame.transform.rotate(self.base_image.copy(), -90)

        if self.rect.y >= 655:
            self.alive = False
        else:
            if self.rect.y + self.velocity > 0:
                self.rect.y += self.velocity

    def shouldJump(self, pipes):
        if pipes:

            next_pipes = pipes.sprites()[:2]
            top_pipe = next_pipes[0]
            bottom_pipe = next_pipes[1]
            bird_y = self.rect.y
            bird_velocity = self.velocity
            top_pipe_y = top_pipe.rect.bottomleft[1] - self.rect.y
            bottom_pipe_y = bottom_pipe.rect.bottomleft[1] - self.rect.y

            inputs = [bird_y, bird_velocity, top_pipe_y, bottom_pipe_y]
            output = self.net.activate(inputs)
            return output[0] > 0.5
        else:
            return False
