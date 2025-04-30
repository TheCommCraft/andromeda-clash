from time import sleep
import pygame
from game_lib.objects import SpaceShip
from game_lib.gamestate import AndromedaClashGameState
from game_lib.user_input import UserInput

pygame.init()
canvas = pygame.display.set_mode((800, 800), pygame.NOFRAME) # Bildschirmgröße festlegen und dabei den Canvas erstellen.
user_input = UserInput()

state = AndromedaClashGameState(canvas, user_input)
ship = SpaceShip((50, 50), (4, 4))
state.current_objects.append(ship)
state.loop()