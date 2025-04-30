from __future__ import annotations # Das sorgt dafür, dass Typannotationen besser funktionieren.
from abc import ABC, abstractmethod
from pygame import SurfaceType
import pygame
from . import gamestate # Das "." sorgt für einen relativen Import also einen aus dem derzeitigen Modul.

# Das ist ein Kommentar, er wird nicht als Code interpretiert.

"""
Das ist ein mehrzeiliger Kommentar. Er wird teilweise dafür verwendet, Funktionen, Methoden und Klassen zu erklären.
"""

Canvas = SurfaceType
"""
Das ist der Typ von dem Bildschirm
"""


class Object2D(ABC):
    """
    Die Basisklasse für gemalte Objekte.
    """
    """
    Das (ABC) bedeutet, dass diese Klasse eine abstrakte Klasse ist. Eine abstrakte Klasse ist eine Klasse, 
    bei der bestimmte Methoden nicht implementiert sind. Eine solche Klasse kann nicht instanziiert werden. 
    Von ihr muss geerbt werden und in der geerbten Klasse müssen die nicht implementierten Methoden 
    implementiert werden, damit man sie instanziieren kann. Abstrakte Klassen werden verwendet, um quasi
    grundlegende Bausteine zu definieren, ohne zu beschreiben, wie genau diese im Inneren funktionieren.
    """
    game_state: gamestate.GameStateType
    
    @abstractmethod # Das ist eine abstrakte Methode, also eine von den erwähnten, nicht implementierten Methoden.
    def draw(self, canvas: Canvas) -> None:
        pass
    
    @abstractmethod
    def update(self) -> None:
        pass

SPACESHIP_SIZE = 20

class SpaceShip(Object2D):
    pos: tuple[float, float]
    vel: tuple[float, float]
     
    def __init__(self, pos: tuple[float, float], vel: tuple[float, float]):
        self.pos = pos
        self.vel = vel
        
    def draw(self, canvas):
        pygame.draw.rect(canvas, (255, 0, 0), ((self.pos[0] - SPACESHIP_SIZE / 2, self.pos[1] - SPACESHIP_SIZE / 2), (SPACESHIP_SIZE, SPACESHIP_SIZE)))
    
    def update(self):
        self.pos = [
            self.pos[0] + self.vel[0],
            self.pos[1] + self.vel[1]
        ]
    
"""
class Stone(Object2D):
    def __init__(self,pos: tuple[float, float], vel: tuple[float, float]):
        self.pos = pos
        self.vel = vel

    def 
"""