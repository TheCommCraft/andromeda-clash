import pygame
from game.objects import SpaceShip
from game.gamestate import AndromedaClashGameState
from game.user_input import UserInput

pygame.init()
canvas = pygame.display.set_mode((400, 400)) # Bildschirmgröße festlegen und dabei den Canvas erstellen.
user_input = UserInput()

state = AndromedaClashGameState(canvas, user_input)
ship = SpaceShip((200, 350), (0, 0))
state.current_objects.append(ship)
state.loop()