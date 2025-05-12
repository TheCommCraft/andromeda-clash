from __future__ import annotations # Das sorgt dafür, dass Typannotationen besser funktionieren.
from abc import ABC, abstractmethod
from typing import Literal
from pygame import SurfaceType
import pygame
from . import gamestate as game_state # Das "." sorgt für einen relativen Import also einen aus dem derzeitigen Modul.
from . import user_input
from . import collider as module_collider
from . import consts
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
    game_state: game_state.GameStateType
    collider: module_collider.Collider
    
    @property
    def user_input(self):
        return self.game_state.user_input
    
    @abstractmethod # Das ist eine abstrakte Methode, also eine von den erwähnten, nicht implementierten Methoden.
    def draw(self, canvas: Canvas) -> None:
        pass
    
    @abstractmethod
    def update(self) -> None:
        pass

class SpaceShip(Object2D):
    pos: tuple[float, float]
    vel: tuple[float, float]
    collider: module_collider.BoxCollider
    shot_cooldown: int # Hiermit wird gezählt, wann wieder geschossen werden darf.
    SHOT_COOLDOWN = 12 # Hiermit wird festgelegt, wie viel Zeit es zwischen Schüssen geben muss.
    
    def __init__(self, pos: tuple[float, float], vel: tuple[float, float]):
        self.pos = pos
        self.vel = vel
        self.collider = module_collider.BoxCollider(consts.SPACESHIP_HITBOX_WIDTH, consts.SPACESHIP_HITBOX_HEIGHT, pos)
        self.shot_cooldown = 0
        
    def draw(self, canvas):
        pygame.draw.rect(
            canvas,
            (255, 0, 0), # Farbenwerte werden als RGB-Tupel angegeben
            (
                (self.pos[0] - consts.SPACESHIP_WIDTH / 2, self.pos[1] - consts.SPACESHIP_HEIGHT / 2), # Position
                (consts.SPACESHIP_WIDTH, consts.SPACESHIP_HEIGHT) # Größe
            )
        )
    
    def update(self):
        self.shot_cooldown -= 1
        self.pos = (
            (self.pos[0] + self.vel[0] + consts.SPACESHIP_WIDTH / 2) % (consts.SCREEN_WIDTH + consts.SPACESHIP_WIDTH) - consts.SPACESHIP_WIDTH / 2,
            self.pos[1] + self.vel[1]
        )
        self.vel = (
            consts.SPACESHIP_INERTIA_FACTOR * self.vel[0] + consts.SPACESHIP_ACCELERATION * (self.user_input.get_key_pressed(consts.key.d) - self.user_input.get_key_pressed(consts.key.a)),
            consts.SPACESHIP_INERTIA_FACTOR * self.vel[1]
        )
        if self.user_input.get_key_pressed(consts.key.SPACE) and self.shot_cooldown <= 0:
            self.shot_cooldown = self.SHOT_COOLDOWN
            projectile = Projectile(self.pos, (0, -consts.PROJECTILE_SPEED), 0)
            self.game_state.add_object(projectile)
            self.game_state.shoot_or_damage_sound.play()
        self.collider.position = self.pos
        for obj in self.game_state.current_objects:
            if not isinstance(obj, Stone):
                continue
            if obj.collider.collides(self.collider):
                self.game_state.game_over()

class Projectile(Object2D):
    pos: tuple[float, float]
    vel: tuple[float, float]
    direction: float
    collider: module_collider.BoxCollider
    def __init__(self, pos: tuple[float, float], vel: tuple[float, float], direction: float):
        self.pos = pos
        self.vel = vel
        self.direction = direction
        self.collider = module_collider.BoxCollider(consts.PROJECTILE_HITBOX_WIDTH, consts.PROJECTILE_HITBOX_HEIGHT, pos)
    
    def draw(self, canvas):
        pygame.draw.line(canvas, (255, 0, 0), self.pos, (self.pos[0], self.pos[1] + consts.PROJECTILE_HEIGHT), consts.PROJECTILE_WIDTH)
    
    def update(self):
        if self.pos[1] < -50:
            self.game_state.remove_object(self)
        self.pos = (
            self.pos[0] + self.vel[0],
            self.pos[1] + self.vel[1]
        )
        self.collider.position = self.pos

class Stone(Object2D):
    pos: tuple[float, float]
    vel: tuple[float, float]
    collider: module_collider.CircleCollider
    def __init__(self, pos: tuple[float, float], vel: tuple[float, float], size: Literal[1, 2, 3, 4]):
        self.pos = pos
        self.vel = vel
        self.size = consts.STONE_BASE_RADIUS * size
        self.collider = module_collider.CircleCollider(consts.STONE_BASE_HITBOX_RADIUS * size, pos)
    

    def update(self):
        if (self.pos[1] > consts.SCREEN_HEIGHT + self.size):
            self.game_state.remove_object(self)
        self.pos = (
            (self.pos[0] + self.vel[0] + self.size) % (consts.SCREEN_WIDTH + self.size * 2) - self.size,
            self.pos[1] + self.vel[1]
        )
        self.collider.position = self.pos
        self.collision()
        
    def collision(self):
        for g in self.game_state.current_objects:
            if not isinstance(g, Projectile):
                continue
            if self.collider.collides(g.collider):
                if self.size/consts.STONE_BASE_RADIUS >= consts.STONE_SIZES[1]:
                    self.split_stone()
                self.game_state.score_object.set_text(f'Score {self.game_state.score + 1}')    
                self.game_state.remove_object(self)
                self.game_state.remove_object(g)
                self.game_state.shoot_or_damage_sound.play()
    
    def split_stone(self):
        '''
        Wird ein Stein getroffen, teilt er sich in 2 kleinere auf. Beide fliegen gleich schnell nach unten und zur Seite. Jedoch einer nach rechts und einer nach links.
        '''
        self.game_state.add_object(Stone(self.pos, self.vel, (self.size // consts.STONE_BASE_RADIUS) - 1))
        self.game_state.add_object(Stone(self.pos, (-self.vel[0], self.vel[1]), (self.size // consts.STONE_BASE_RADIUS) - 1))


    def draw(self, canvas):
        pygame.draw.circle(canvas, (0, 255, 0), self.pos, self.size, 4)

    def set_pos(self, new_pos):
        self.pos = new_pos
    
    def set_vel(self, new_vel):
        self.vel = new_vel







class Text(Object2D): 
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GRAY = (200, 200, 200)
    img: SurfaceType
    pos: tuple[float, float]
    text: str
    text_color: tuple[int, int, int]
    text_size: int
    font: pygame.font.FontType
    
    def __init__(self, pos: tuple[float, float], text: str, text_size: int, text_color: tuple[int, int, int]):
        self.pos = pos
        self.set_all(text, text_size, text_color)
        
    def update(self):
        pass
        
    def draw(self, canvas):
        rect = self.img.get_rect()
        pos_x = self.pos[0] - rect.width / 2
        pos_y = self.pos[1] - rect.height / 2
        canvas.blit(self.img, (pos_x, pos_y))       # Zeichnen des Textes
        
    def set_all(self, text, text_size, text_color):               # Setter-Methoden
        self.text = text
        self.text_color = text_color
        self.set_text_size(text_size)
        
    def set_text(self, text):
        self.text = text
        self.img = self.font.render(self.text, True, self.text_color)       
        
    def set_text_size(self, text_size):
        self.text_size = text_size
        self.font = pygame.font.SysFont(None, self.text_size)       # Font aktualisieren/erstellen
        self.img = self.font.render(self.text, True, self.text_color)       # Text aktualisieren/erstellen
        
    def set_text_color(self, text_color):
        self.text_color = text_color
        self.img = self.font.render(self.text, True, self.text_color)    