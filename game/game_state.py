from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Collection
from pathlib import Path
import random
import pygame
from . import objects
from . import user_input as module_user_input
from . import consts
from . import data_structures
from . import sound as module_sound
import math

GAME_SIZE = (consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
imp = pygame.image.load(Path(Path(__file__).parent, "images", "lx5gafg9.png"))


class GameStateType(ABC):
    canvas: objects.Canvas
    current_objects: Collection[objects.Object2D]
    user_input: module_user_input.UserInputType
    @abstractmethod
    def loop(self):
        pass
    
    @abstractmethod
    def add_object(self, obj: objects.Object2D):
        pass
    
    @abstractmethod
    def remove_object(self, obj: objects.Object2D):
        pass

class AndromedaClashGameState(GameStateType):
    """
    Der Spielzustand. 
    Hier sollte in Methoden das erstellen von Objekten und ähnliches passieren.
    Die Hauptschleife sollte sich auch hier befinden.
    """
    current_objects: data_structures.ObjectContainer
    clock: pygame.time.Clock # Wird für Bildrate verwendet.
    fps: int # Bildrate
    player: objects.SpaceShip
    user_input: module_user_input.UserInputType
    min_y_vel_stone = 0.5
    max_vel_stone = 1
    stone_spawn_probability: float
    score: int
    highscore: int
    score_object: objects.Text
    lives_object: objects.LiveDisplay
    @property
    def lives(self) -> int:
        return self.lives_object.lives
    
    def __init__(self, canvas: objects.Canvas, user_input: module_user_input.UserInputType) -> None:
        self.canvas = canvas
        self.current_objects = data_structures.ObjectContainer()
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.user_input = user_input
        self.stone_spawn_probability = consts.START_STONE_SPAWNING_PROBABILITY
        
        self.score = 0
        self.highscore = 0
        self.score_object = objects.Text(consts.POS_SCORE, "", consts.TEXT_SIZE_SCORE, consts.TEXT_COLOR_SCORE)
        self.update_score()
        self.add_object(self.score_object)
        
        self.lives_object = objects.LiveDisplay()
        self.add_object(self.lives_object)
        
        self.add_player()
    
    def add_object(self, obj: objects.Object2D):
        self.current_objects.add_object(obj)
        
    def add_player(self):
        self.player = objects.SpaceShip((consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT - consts.SPACESHIP_HEIGHT + 8), (0, 0))
        self.add_object(self.player)
    
    def remove_object(self, obj: objects.Object2D):
        self.current_objects.remove_object(obj)
    
    def remove_all_objects(self):
        self.current_objects.remove_all()
        
    def loop(self) -> None:
        running = True
        while running:
            self.canvas.fill((0, 0, 0)) # Hintergrund wird mit Schwarz gefüllt. (Farbenwerte werden als RGB-Tupel angegeben)
            self.user_input.process_tick()
            for event in pygame.event.get():
                self.user_input.process_event(event)
                if event.type == pygame.QUIT: # Falls Schliessen-Knopf gedruckt wird, wird das Programm beendet. 
                    running = False
            self.spawn_stone()
            for object2d in self.current_objects:
                if not hasattr(object2d, "game_state"):
                    object2d.game_state = self
                object2d.update()
            for object2d in self.current_objects:
                object2d.draw(self.canvas)
            if self.user_input.get_key_down_now(consts.key.r):
                self.remove_all_objects()
                self.add_player()
            pygame.display.update() # Änderungen werden umgesetzt.
            self.clock.tick(self.fps)

    def spawn_stone(self):
        if random.random() < self.stone_spawn_probability: # Wahrscheinlichkeit. dass ein Stein entsteht
            
            vel_y = AndromedaClashGameState.min_y_vel_stone + random.random() * (AndromedaClashGameState.max_vel_stone - AndromedaClashGameState.min_y_vel_stone)   #Stellt sicher, dass die vertikale Bewegung im Intervall von min_y_vel_stone bis max_vel_stone liegt.
            vel_x = math.sqrt(AndromedaClashGameState.max_vel_stone - vel_y**2) * random.randrange(-1, 2, 2)   #Stellt sicher, dass die absolute Geschwindigkeit der Maximalen entspricht. Die random Funktion am Ende macht, dass der Stein sich zufällig nach rechts oder links bewegt.
            vel = (vel_x, vel_y)
            size = random.choice(consts.STONE_SIZES)
            pos = (random.random()*GAME_SIZE[0], -consts.STONE_BASE_RADIUS * size)
            
            self.add_object(objects.Stone(pos, vel, size))
        self.stone_spawn_probability += consts.STONE_SPAWNING_PROPABILITY_INCREASE / (1 + self.stone_spawn_probability * consts.STONE_SPAWNING_PROPABILITY_INCREASE_DECREASE)
    
    def game_over(self):
        self.remove_all_objects()
        if self.score > self.highscore:
            self.highscore = self.score
        self.add_object(objects.Text((consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT / 2), f"GAME OVER\nSCORE: {self.score}\nHIGHSCORE: {self.highscore} ", 20, (255, 255, 255)))
        self.score = 0
    
    def update_score(self):
        self.score_object.set_text(f'SCORE {self.score}')