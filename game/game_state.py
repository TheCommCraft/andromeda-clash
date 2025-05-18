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
    stonemin_y_vel: float
    stone_max_vel: float
    stone_spawn_probability: float
    enemy_min_y_vel: float
    enemy_max_vel: float
    enemy_spawn_probability: float
    powerup_spawn_probability: float
    score: int
    highscore: int
    score_object: objects.Score
    lives_object: objects.LiveDisplay
    @property
    def lives(self) -> int:
        return self.lives_object.lives
    
    @lives.setter
    def lives(self, value):
        self.lives_object.lives = value
    
    def __init__(self, canvas: objects.Canvas, user_input: module_user_input.UserInputType) -> None:
        self.canvas = canvas
        self.current_objects = data_structures.ObjectContainer()
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.user_input = user_input
        self.stone_spawn_probability = consts.START_STONE_SPAWNING_PROBABILITY
        self.powerup_spawn_probability = consts.START_POWERUP_SPAWNING_PROBABILITY
        self.enemy_spawn_probability = consts.START_ENEMY_SPAWNING_PROBABILITY
        self.stone_min_y_vel = consts.STONE_STANDARD_MIN_Y_VEL
        self.stone_max_vel = consts.STONE_STANDARD_MAX_VEL
        self.enemy_min_y_vel = consts.ENEMY_STANDARD_MIN_Y_VEL
        self.enemy_max_vel = consts.ENEMY_STANDARD_MAX_VEL
        
        self.highscore = 0
        
        self.start_game()
    
    def start_game(self):
        self.remove_all_objects()
        self.score = 0
        self.score_object = objects.Score(consts.POS_SCORE, "", consts.TEXT_SIZE_SCORE, consts.TEXT_COLOR_SCORE)
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
            self.spawn_powerup()
            self.spawn_enemy()
            for object2d in self.current_objects:
                if not hasattr(object2d, "game_state"):
                    object2d.game_state = self
                object2d.update()
            top_layered = []
            for object2d in self.current_objects:
                draw_details = object2d.get_draw_details()
                if consts.DrawDetails.TOP_LAYER in draw_details:
                    top_layered.append(object2d)
                    continue
                object2d.draw(self.canvas)
            for object2d in top_layered:
                object2d.draw(self.canvas)
            if self.user_input.get_key_down_now(consts.key.r):
                self.start_game()
            pygame.display.update() # Änderungen werden umgesetzt.
            self.clock.tick(self.fps)

    def spawn_stone(self):
        if random.random() < self.stone_spawn_probability: # Wahrscheinlichkeit. dass ein Stein entsteht
            
            vel_y = self.stone_min_y_vel + random.random() * (self.stone_max_vel - self.stone_min_y_vel)   # Stellt sicher, dass die vertikale Bewegung im Intervall von min_y_vel_stone bis max_vel_stone liegt.
            vel_x = math.sqrt(self.stone_max_vel - vel_y**2) * random.randrange(-1, 2, 2)   # Stellt sicher, dass die absolute Geschwindigkeit der Maximalen entspricht. Die random Funktion am Ende macht, dass der Stein sich zufällig nach rechts oder links bewegt.
            vel = (vel_x, vel_y)
            size = random.choice(consts.STONE_SIZES)
            pos = (random.random()*GAME_SIZE[0], -consts.STONE_BASE_RADIUS * size)
            
            self.add_object(objects.Stone(pos, vel, size))
        self.stone_spawn_probability += consts.STONE_SPAWNING_PROPABILITY_INCREASE / (1 + self.stone_spawn_probability * consts.STONE_SPAWNING_PROPABILITY_INCREASE_DECREASE)
    
    def spawn_powerup(self):
        if random.random() < self.powerup_spawn_probability:
            pos = [random.random() * GAME_SIZE[0], -consts.POWERUP_HITBOX_RADIUS]
            vel = consts.POWERUP_SPEED
            type = random.randrange(0, len(consts.POWERUP_TYPES) + 1)
            self.add_object(objects.PowerUp(pos, vel, type))
        self.powerup_spawn_probability += consts.POWERUP_SPAWNING_PROPABILITY_INCREASE / (1 + self.powerup_spawn_probability * consts.POWERUP_SPAWNING_PROPABILITY_INCREASE_DECREASE)

    def spawn_enemy(self):
        if random.random() < self.enemy_spawn_probability: # Wahrscheinlichkeit. dass ein Stein entsteht
            vel_y = self.enemy_min_y_vel + random.random() * (self.enemy_max_vel - self.enemy_min_y_vel)   # Stellt sicher, dass die vertikale Bewegung im Intervall von min_y_vel_stone bis max_vel_stone liegt.
            vel_x = math.sqrt(self.enemy_max_vel - vel_y**2) * random.randrange(-1, 2, 2)   # Stellt sicher, dass die absolute Geschwindigkeit der Maximalen entspricht. Die random Funktion am Ende macht, dass der Stein sich zufällig nach rechts oder links bewegt.
            vel = (vel_x, vel_y)
            type = random.choice(consts.ENEMY_TYPES)
            pos = (random.random()*GAME_SIZE[0], -consts.ENEMY_HEIGHT)
            self.add_object(objects.Enemy(pos, vel, type))
        self.enemy_spawn_probability += consts.ENEMY_SPAWNING_PROPABILITY_INCREASE / (1 + self.enemy_spawn_probability * consts.ENEMY_SPAWNING_PROPABILITY_INCREASE_DECREASE)
    

    def game_over(self):
        self.remove_all_objects()
        if self.score > self.highscore:
            self.highscore = self.score
        self.add_object(objects.Text((consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT / 2 - consts.GAME_OVER_LINE_HEIGHT), "GAME OVER", 16, (255, 255, 255)))
        self.add_object(objects.Text((consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT / 2), f"SCORE: {self.score}", 16, (255, 255, 255)))
        self.add_object(objects.Text((consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT / 2 + consts.GAME_OVER_LINE_HEIGHT), f"HIGHSCORE: {self.highscore}", 16, (255, 255, 255)))
        self.add_object(objects.Text((consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT / 2 + consts.GAME_OVER_LINE_HEIGHT * 2.5), "PRESS R TO RESTART", 16, (200, 200, 200)))
        self.score = 0
    
    def update_score(self):
        self.score_object.set_text(f'SCORE {self.score}')