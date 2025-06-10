from game.collider import BoxCollider, RotatedRectangleCollider
import pygame
from math import radians

pygame.init()
canvas = pygame.display.set_mode((600, 600))
coll_a = RotatedRectangleCollider(100, 200, (300, 350), radians(10))
coll_b = RotatedRectangleCollider(100, 200, (0, 0), radians(30))


x: int = 16
y: int = 16
fine: int = 32
if __name__ == "__main__":
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        coll_b.position = (x, y)
        c1 = coll_b.collides(coll_a)
        c2 = BoxCollider(0, 0, (x, y)).collides(coll_a)
        coll_b.position = (300, 300)
        c3 = coll_b.collides(BoxCollider(0, 0, (x, y)))
        pygame.draw.rect(canvas, (20 + 220 * c1, 20 + 220 * c2, 20 + 220 * c3), (x - fine / 2, y - fine / 2, fine, fine))
        pygame.display.flip()
        x += fine
        if x >= 600:
            x = fine // 2
            y += fine
        if y >= 600:
            fine //= 2
            x = fine // 2
            y = fine // 2
