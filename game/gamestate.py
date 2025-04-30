from __future__ import annotations
from abc import ABC, abstractmethod
import pygame
from . import objects
from . import user_input as module_user_input

class GameStateType(ABC):
    canvas: objects.Canvas
    current_objects: list[objects.Object2D]
    user_input: module_user_input.UserInputType
    @abstractmethod
    def loop(self):
        pass

class AndromedaClashGameState(GameStateType):
    """
    Der Spielzustand. 
    Hier sollte in Methoden das erstellen von Objekten und ähnliches passieren.
    Die Hauptschleife sollte sich auch hier befinden.
    """
    clock: pygame.time.Clock # Wird für Bildrate verwendet.
    fps: int # Bildrate
    def __init__(self, canvas: objects.Canvas, user_input: module_user_input.UserInputType) -> None:
        self.canvas = canvas
        self.current_objects = []
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.user_input = user_input
    
    def loop(self) -> None:
        running = True
        while running:
            self.canvas.fill((0, 0, 0)) # Hintergrund wird mit Schwarz gefüllt. (Farbenwerte werden als RGB-Tupel angegeben)
            self.user_input.process_tick()
            for event in pygame.event.get():
                self.user_input.process_event(event)
                if event.type == pygame.QUIT: # Falls Schliessen-Knopf gedruckt wird, wird das Programm beendet. 
                    running = False
            for object2d in self.current_objects:
                if not hasattr(object2d, "game_state"):
                    object2d.game_state = self
                object2d.update()
            for object2d in self.current_objects:
                object2d.draw(self.canvas)
            pygame.display.update() # Änderungen werden umgesetzt.
            self.clock.tick(self.fps)