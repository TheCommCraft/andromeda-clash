from __future__ import annotations # Das sorgt dafür, dass Typannotationen besser funktionieren.
from abc import ABC, abstractmethod
from pygame import SurfaceType
import pygame
from . import gamestate # Das "." sorgt für einen relativen Import also einen aus dem derzeitigen Modul.
from . import user_input
from . import sound as module_sound

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
    
    @property
    def user_input(self):
        return self.game_state.user_input
    
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
    sound: module_sound.Sound
    
    def __init__(self, pos: tuple[float, float], vel: tuple[float, float]):
        self.pos = pos
        self.vel = vel
        self.sound = module_sound.Sound("game/sounds/shoot.wav")
        
    def draw(self, canvas):
        pygame.draw.rect(
            canvas,
            (255, 0, 0), # Farbenwerte werden als RGB-Tupel angegeben
            (
                (self.pos[0] - SPACESHIP_SIZE / 2, self.pos[1] - SPACESHIP_SIZE / 2), # Position
                (SPACESHIP_SIZE, SPACESHIP_SIZE) # Größe
            )
        )
    
    def update(self):
        self.pos = (
            self.pos[0] + self.vel[0],
            self.pos[1] + self.vel[1]
        )
        self.vel = (
            0.9 * self.vel[0] + self.user_input.get_key_pressed(user_input.KeyboardKey.d) - self.user_input.get_key_pressed(user_input.KeyboardKey.a),
            0.9 * self.vel[1]
        )
        if self.user_input.get_key_changed(user_input.KeyboardKey.SPACE) and self.user_input.get_key_pressed(user_input.KeyboardKey.SPACE):
            projectile = Projectile(self.pos, (0, -6), 0)
            self.game_state.current_objects.append(projectile)
            self.sound.play()

class Projectile(Object2D):
    pos: tuple[float, float]
    vel: tuple[float, float]
    direction: float
    def __init__(self, pos: tuple[float, float], vel: tuple[float, float], direction: float):
        self.pos = pos
        self.vel = vel
        self.direction = direction
    
    def draw(self, canvas):
        pygame.draw.line(canvas, (255, 0, 0), self.pos, (self.pos[0], self.pos[1] + 20), 4)
    
    def update(self):
        if self.pos[1] < -50:
            self.game_state.current_objects.remove(self)
        self.pos = (
            self.pos[0] + self.vel[0],
            self.pos[1] + self.vel[1]
        )

"""
class Stone(Object2D):
    def __init__(self,pos: tuple[float, float], vel: tuple[float, float]):
        self.pos = pos
        self.vel = vel

    def 
"""