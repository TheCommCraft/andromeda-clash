from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Collection
from pathlib import Path
from typing import TypeVar
import random
import time
import math
import pygame
from . import consts
from . import objects
from . import user_input as module_user_input
from . import data_structures
from . import sound as module_sound
from . import images as modules_images

GAME_SIZE = (consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
imp = pygame.image.load(Path(__file__).parent / "images" / "lx5gafg9.png")


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

E = TypeVar("E", bound=objects.CommonEnemy)

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
    powerup_spawn_probability: float
    score: int
    highscore: int
    score_object: objects.Score
    lives_object: objects.LifeDisplay
    background_image: modules_images.Image
    active_powerups: data_structures.ObjectContainerBase["objects.PowerUp"]
    currently_game_over: bool
    current_wave: list[objects.CommonEnemy]
    current_wave_cooldown: int
    current_wave_idx: int
    credits: int
    
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
        self.background_image = pygame.transform.scale(modules_images.load_image(consts.BACKGROUND_IMAGE_PATH), GAME_SIZE)
        
        self.highscore = 0
        self.credits = 0
        
        self.start_game()
    
    def start_game(self):
        if hasattr(self, "active_powerups"):
            for power_up in self.active_powerups:
                power_up.deactivate_power()
                power_up.activated = False
        self.stone_min_y_vel = consts.STONE_STANDARD_MIN_Y_VEL
        self.stone_max_vel = consts.STONE_STANDARD_MAX_VEL
        self.enemy_min_y_vel = consts.ENEMY_STANDARD_MIN_Y_VEL
        self.enemy_max_vel = consts.ENEMY_STANDARD_MAX_VEL
        self.stone_spawn_probability = consts.START_STONE_SPAWNING_PROBABILITY
        self.powerup_spawn_probability = consts.START_POWERUP_SPAWNING_PROBABILITY
        self.currently_game_over = False
        self.remove_all_objects()
        self.score = 0
        self.score_object = objects.Score(consts.POS_SCORE, "", consts.TEXT_SIZE_SCORE, consts.TEXT_COLOR_SCORE)
        self.update_score()
        self.add_object(self.score_object)
        self.active_powerups = data_structures.ObjectContainer()
        
        self.current_wave = []
        self.current_wave_cooldown = 0
        self.current_wave_idx = -1
        
        self.lives_object = objects.LifeDisplay()
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
    
    def activate_powerup(self, power_up: objects.PowerUp):
        '''
        Wird ein PowerUp eingesammelt, passieren mehrere Dinge:
            1.1 Falls der Spieler dieses PowerUp bereits ein PowerUp dieser Art hat, wird das PowerUp ersetzt, wodurch die wirkdauer verlängert wird.
            1.2 Falls der Spieler bereits ein PowerUp dieser Art hat, welches schwächer ist, wird dieses durch das Stärkere ersetzt.
            1.3 Falls er bereits ein PowerUp dieser Art hat, welches stärker ist, hat das Einsammeln keinen Effekt.
            2. Falls das powerUp neu ist, wird dessen Fähigkeit aktiviert.
            3. Es wird ein Timer erstellt, nach dessen Ablauf der Effekt des PowerUps beendet wird.
        '''
        self.remove_object(power_up)
        for other_power_up in self.active_powerups:
            if power_up == other_power_up:
                other_power_up.deactivate_power()
                other_power_up.activated = False
                self.active_powerups.remove_object(other_power_up)
                continue
            if other_power_up > power_up:
                return
            if power_up > other_power_up:
                other_power_up.deactivate_power()
                other_power_up.activated = False
                self.active_powerups.remove_object(other_power_up)
        power_up.activate_power()
        power_up.end_time = time.time() + power_up.effect_time
        power_up.activated = True
        power_up.arc_cooldown = objects.ArcCooldown(power_up.pos, power_up.end_time, power_up.effect_time, power_up)
        self.active_powerups.add_object(power_up)
        
    def loop(self) -> None:
        running = True
        while running:
            self.canvas.fill((0, 0, 0))
            self.canvas.blit(self.background_image, (0, 0)) # Hintergrund wird mit Bild gefüllt
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
            index = 0
            for power_up in self.active_powerups:
                if power_up.end_time <= time.time():
                    power_up.deactivate_power()
                    power_up.activated = False
                    self.active_powerups.remove_object(power_up)
                    continue
                power_up.pos = (consts.SCREEN_WIDTH - (consts.POWERUP_HITBOX_RADIUS + 8) * (2 * index + 1), consts.SCREEN_HEIGHT - (consts.POWERUP_HITBOX_RADIUS + 8))
                power_up.draw(self.canvas)
                power_up.arc_cooldown.pos = power_up.pos
                power_up.arc_cooldown.draw(self.canvas)
                index += 1
                power_up.update_activated()
            if self.user_input.get_key_down_now(consts.key.r) and self.currently_game_over:
                self.start_game()
            pygame.display.update() # Änderungen werden umgesetzt.
            self.clock.tick(self.fps)

    def spawn_stone(self):
        if random.random() < self.stone_spawn_probability: # Wahrscheinlichkeit. dass ein Stein entsteht
            
            size = random.choice(consts.STONE_SIZES)
            upwards = random.random() < 0.5
            on_the_left = random.random() < 0.5
            pos_y = self.player.pos[1] - consts.SPACESHIP_HITBOX_HEIGHT * 3
            if self.player.pos[1] < consts.SCREEN_HEIGHT / 2:
                pos_y = consts.SCREEN_HEIGHT / 2 + consts.SPACESHIP_HITBOX_HEIGHT
            pos = (-size * consts.STONE_BASE_RADIUS if on_the_left else consts.SCREEN_WIDTH + size * consts.STONE_BASE_RADIUS, pos_y)
            vel_y = (-1 if upwards else 1) * (self.stone_min_y_vel + random.random() * (self.stone_max_vel - self.stone_min_y_vel))   # Stellt sicher, dass die vertikale Bewegung im Intervall von min_y_vel_stone bis max_vel_stone liegt.
            vel_x = (1 if on_the_left else -1) * math.sqrt(self.stone_max_vel - vel_y**2)   # Stellt sicher, dass die absolute Geschwindigkeit der Maximalen entspricht. Die random Funktion am Ende macht, dass der Stein sich zufällig nach rechts oder links bewegt.
            vel = (vel_x, vel_y)
            
            self.add_object(objects.Stone(pos, vel, size))
        self.stone_spawn_probability += consts.STONE_SPAWNING_PROPABILITY_INCREASE / (1 + self.stone_spawn_probability * consts.STONE_SPAWNING_PROPABILITY_INCREASE_DECREASE)
    
    def spawn_powerup(self):
        if random.random() < self.powerup_spawn_probability:
            pos = [random.random() * GAME_SIZE[0], -consts.POWERUP_HITBOX_RADIUS]
            vel = (0, consts.POWERUP_SPEED)
            powerup_type = random.choice(objects.POWERUP_TYPES)
            self.add_object(powerup_type(pos, vel))
        self.powerup_spawn_probability += consts.POWERUP_SPAWNING_PROPABILITY_INCREASE / (1 + self.powerup_spawn_probability * consts.POWERUP_SPAWNING_PROPABILITY_INCREASE_DECREASE)

    def create_enemy(self, enemy_type: type[E]) -> E:
        vel_y = self.enemy_min_y_vel + random.random() * (self.enemy_max_vel - self.enemy_min_y_vel)   # Stellt sicher, dass die vertikale Bewegung im Intervall von min_y_vel_stone bis max_vel_stone liegt.
        vel_x = math.sqrt(self.enemy_max_vel - vel_y**2) * random.randrange(-1, 2, 2)   # Stellt sicher, dass die absolute Geschwindigkeit der Maximalen entspricht. Die random Funktion am Ende macht, dass der Stein sich zufällig nach rechts oder links bewegt.
        vel = (vel_x, vel_y)
        pos = (random.random() * GAME_SIZE[0], -consts.ENEMY_HEIGHT)
        target_height = consts.ENEMY_TARGET_HEIGHT_RANGE.start + consts.ENEMY_TARGET_HEIGHT_RANGE.stop - consts.ENEMY_TARGET_HEIGHT_RANGE.start * random.random()
        return enemy_type(pos, vel, target_height)

    def create_wave(self):
        self.current_wave_cooldown = 90
        self.current_wave_idx += 1
        self.current_wave = []
        wave_score = 2 + self.current_wave_idx * 2
        last_wave_score = 2 + (self.current_wave_idx - 1) * 2
        previous_type: type[objects.CommonEnemy] = objects.CommonEnemy
        for obj_type, score in objects.ENEMY_COSTS.items():
            if score > wave_score:
                strongest_type = previous_type
                break
            previous_type = obj_type
        else:
            strongest_type = obj_type
        if objects.ENEMY_COSTS[strongest_type] > last_wave_score:
            wave_score -= objects.ENEMY_COSTS[strongest_type]
            self.current_wave.append(self.create_enemy(strongest_type))
        while wave_score > 0:
            previous_type = objects.CommonEnemy
            for obj_type, score in objects.ENEMY_THRESHOLDS.items():
                if score > wave_score:
                    strongest_type = previous_type
                    break
                previous_type = obj_type
            else:
                strongest_type = obj_type
            wave_score -= objects.ENEMY_COSTS[strongest_type]
            self.current_wave.append(self.create_enemy(strongest_type))
    
    def has_enemies(self) -> bool:
        for i in self.current_objects:
            if isinstance(i, objects.CommonEnemy):
                return True
        return False

    def spawn_enemy(self):
        if not self.current_wave and not self.has_enemies():
            self.create_wave()
        self.current_wave_cooldown -= 1
        if self.current_wave_cooldown <= 0 and self.current_wave:
            self.add_object(self.current_wave.pop(0))
            self.current_wave_cooldown = consts.ENEMY_SPAWN_COOLDOWN

    def game_over(self):
        self.remove_all_objects()
        if self.score > self.highscore:
            self.highscore = self.score
        self.add_object(objects.Text((consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT / 2 - consts.GAME_OVER_LINE_HEIGHT), "GAME OVER", 16, (255, 255, 255)))
        self.add_object(objects.Text((consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT / 2), f"SCORE: {self.score}", 16, (255, 255, 255)))
        self.add_object(objects.Text((consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT / 2 + consts.GAME_OVER_LINE_HEIGHT), f"HIGHSCORE: {self.highscore}", 16, (255, 255, 255)))
        self.add_object(objects.Text((consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT / 2 + consts.GAME_OVER_LINE_HEIGHT * 2.5), "PRESS R TO RESTART", 16, (200, 200, 200)))
        self.credits += (self.score//100)
        self.score = 0
        self.currently_game_over = True
        for powerup in self.active_powerups:
            powerup.end_time = -1
    
    def update_score(self):
        self.score_object.set_text(f'SCORE {self.score}')
