import pygame
from game.game_state import AndromedaClashGameState, GAME_SIZE
from game.user_input import UserInput


pygame.init()
canvas = pygame.display.set_mode(GAME_SIZE) # Bildschirmgröße festlegen und dabei den Canvas erstellen.
user_input = UserInput()

state = AndromedaClashGameState(canvas, user_input)

if __name__ == "__main__":
    state.loop()
