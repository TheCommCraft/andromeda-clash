from __future__ import annotations
from abc import ABC, abstractmethod
import pygame
from . import objects

class GameStateType(ABC):
    canvas: objects.Canvas
    current_objects: list[objects.Object2D]
    @abstractmethod
    def loop(self):
        pass

class AndromedaClashGameState(GameStateType):
    """
    Der Spielzustand. 
    Hier sollte in Methoden das erstellen von Objekten und ähnliches passieren.
    Die Hauptschleife sollte sich auch hier befinden.
    """
    def __init__(self, canvas: objects.Canvas) -> None:
        self.canvas = canvas
        self.current_objects = []
    
    def loop(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # Falls Schliessen-Knopf gedruckt wird, wird das Programm beendet. 
                    running = False
            for object2d in self.current_objects:
                object2d.update()
            for object2d in self.current_objects:
                object2d.draw(self.canvas)
            pygame.display.update() # Änderungen werden umgesetzt.