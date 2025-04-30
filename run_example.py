import pygame
from game_lib.objects import SpaceShip
from game_lib.gamestate import AndromedaClashGameState

pygame.init()
canvas = pygame.display.set_mode((400, 400)) # Bildschirmgröße festlegen und dabei den Canvas erstellen.

state = AndromedaClashGameState(canvas)
ship = SpaceShip((50, 50), (0, 0), 1)
state.current_objects.append(ship)
state.loop()