import pygame 

pygame.init()

from .consts import SCREEN_HEIGHT, SCREEN_WIDTH

screen = pygame.display.set_mode((SCREEN_HEIGHT, SCREEN_WIDTH))

background_image = pygame.image.load("background.jpg").convert()

background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

running = True 

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        screen.blit(background_image, (0, 0))

        pygame.display.flip()


def draw(self):
    self.screen.blit(self.background_image, (0, 0))
