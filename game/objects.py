from __future__ import annotations # Das sorgt dafür, dass Typannotationen besser funktionieren.
from abc import ABC, abstractmethod
from typing import Literal, Self
import random
import time
import math
from pathlib import Path
from functools import lru_cache
from enum import Enum
from pygame import SurfaceType
import pygame
from . import game_state as module_game_state # Das "." sorgt für einen relativen Import also einen aus dem derzeitigen Modul.
from . import sound as module_sound
from . import collider as module_collider
from . import consts
from . import data_structures
from .images import load_image, Image
# Das ist ein Kommentar, er wird nicht als Code interpretiert.


class ProjectileOwner(Enum):
    PLAYER = 0
    ENEMY = 1

Canvas = SurfaceType

number = float | int #Wenn der Typ sowohl float, als auch int sein kann, wird number angegeben.

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
    game_state: module_game_state.GameStateType
    collider: module_collider.Collider
    
    @property
    def user_input(self):
        return self.game_state.user_input
    
    def get_draw_details(self) -> consts.DrawDetails:
        return consts.DrawDetails.NONE
    
    @abstractmethod # Das ist eine abstrakte Methode, also eine von den erwähnten, nicht implementierten Methoden.
    def draw(self, canvas: Canvas) -> None:
        pass
    
    @abstractmethod
    def update(self) -> None:
        pass

class SpaceShip(Object2D):
    '''
    Die Klasse SpaceShip definiert das Raumschiff, welches der Spieler steuert.
    Er kann es bewegen und schießen lassen.
    '''
    pos: tuple[number, number]
    vel: tuple[number, number]
    collider: module_collider.BoxCollider
    shot_cooldown_timer: int # Hiermit wird gezählt, wann wieder geschossen werden darf.
    shot_cooldown = consts.SPACESHIP_SHOT_COOLDOWN # Hiermit wird festgelegt, wie viel Zeit es zwischen Schüssen geben muss.#in consts übertragen
    shoot_sound: module_sound.Sound
    damage_sound: module_sound.Sound
    game_state: module_game_state.AndromedaClashGameState
    image: Image
    invincible: bool
    point_multiplier: int
    damage_multiplier: int
    piercing: bool
    multishot: bool
    
    @property
    def attack_damage(self) -> number:
        return consts.SPACESHIP_DAMAGE * self.damage_multiplier

    @property
    def lives(self) -> int:
        return self.game_state.lives
    
    @lives.setter
    def lives(self, value):
        self.game_state.lives = value
    
    def __init__(self, pos: tuple[number, number], vel: tuple[number, number]):
        self.pos = pos
        self.vel = vel
        self.collider = module_collider.BoxCollider(consts.SPACESHIP_HITBOX_WIDTH, consts.SPACESHIP_HITBOX_HEIGHT, pos)
        self.shot_cooldown_timer = 0
        self.shoot_sound = module_sound.load_sound(consts.SHOOT_SOUND_PATH)
        self.damage_sound = module_sound.load_sound(consts.HIT_SOUND_PATH)
        self.image = pygame.transform.scale(load_image(consts.SPACESHIP_IMAGE_PATH), (consts.SPACESHIP_WIDTH, consts.SPACESHIP_HEIGHT))
        self.invincible = False
        self.point_multiplier = 1
        self.damage_multiplier = 1
        self.piercing = False
        self.multishot = False

    def draw(self, canvas):
        if self.invincible:
            pygame.draw.circle(canvas, consts.SPACESHIP_SHIELD_COLOR, self.pos, consts.SPACESHIP_HEIGHT / 2)
        canvas.blit(self.image, (self.pos[0] - consts.SPACESHIP_WIDTH / 2, self.pos[1] - consts.SPACESHIP_HEIGHT / 2))
    
    def update(self):
        self.pos = (
            (self.pos[0] + self.vel[0] + consts.SPACESHIP_WIDTH / 2)
                % (consts.SCREEN_WIDTH + consts.SPACESHIP_WIDTH)
                - consts.SPACESHIP_WIDTH / 2,
            min(self.pos[1] + self.vel[1], consts.SCREEN_HEIGHT - consts.SPACESHIP_HEIGHT - 16)
        )
        self.vel = (
            consts.SPACESHIP_INERTIA_FACTOR * self.vel[0]
                + (
                    consts.SPACESHIP_ACCELERATION
                    * (self.user_input.get_key_pressed(consts.key.d) - self.user_input.get_key_pressed(consts.key.a))
                ),
            consts.SPACESHIP_INERTIA_FACTOR * self.vel[1]
                + (
                    consts.SPACESHIP_ACCELERATION
                    * (
                        self.user_input.get_key_pressed(consts.key.s)
                        * (self.pos[1] < consts.SCREEN_HEIGHT - consts.SPACESHIP_HEIGHT - 16)
                        - self.user_input.get_key_pressed(consts.key.w)
                    )
                )
        )
        self.handle_shooting()
        self.collider.position = self.pos
        if not self.invincible:
            for obj in self.game_state.current_objects:
                if not isinstance(obj, Stone) and not isinstance(obj, Projectile) and not isinstance(obj, CommonEnemy):
                    continue
                if isinstance(obj, PiercingProjectile) and obj.has_hit_enemy(self):
                    continue
                if obj.collider.collides(self.collider):
                    if isinstance(obj, Projectile) and obj.owner != ProjectileOwner.ENEMY:
                        continue
                    self.lives -= 1
                    self.damage_sound.play()
                    if isinstance(obj, PiercingProjectile):
                        obj.register_enemy(self)
                    else:
                        self.game_state.remove_object(obj)
                    if self.lives <= 0:
                        self.game_state.game_over()
    
    def handle_shooting(self):
        self.shot_cooldown_timer -= 1
        if self.user_input.get_key_pressed(consts.key.SPACE) and self.shot_cooldown_timer <= 0:
            self.handle_shot()
            self.shot_cooldown_timer = self.shot_cooldown
    
    def handle_shot(self):
        if not self.multishot:
            projectile = \
                (PiercingProjectile if self.piercing else Projectile)((self.pos[0], self.pos[1] - consts.SPACESHIP_HEIGHT / 2 - consts.PROJECTILE_HEIGHT / 2), (0, -consts.PROJECTILE_SPEED), 0, ProjectileOwner.PLAYER)
            self.game_state.add_object(projectile)
        else:
            # Die Projektile müssen noch schrägfliegend gemacht werden.
            projectile_1 = \
                (PiercingProjectile if self.piercing else Projectile)((self.pos[0], self.pos[1] - consts.SPACESHIP_HEIGHT / 2 - consts.PROJECTILE_HEIGHT / 2), (-math.sin(consts.PROJECILE_MULTISHOT_ANGLE) * consts.PROJECTILE_SPEED, -math.cos(consts.PROJECILE_MULTISHOT_ANGLE) * consts.PROJECTILE_SPEED), -consts.PROJECILE_MULTISHOT_ANGLE, ProjectileOwner.PLAYER)
            projectile_2 = \
                (PiercingProjectile if self.piercing else Projectile)((self.pos[0], self.pos[1] - consts.SPACESHIP_HEIGHT / 2 - consts.PROJECTILE_HEIGHT / 2), (math.sin(consts.PROJECILE_MULTISHOT_ANGLE) * consts.PROJECTILE_SPEED, -math.cos(consts.PROJECILE_MULTISHOT_ANGLE) * consts.PROJECTILE_SPEED), consts.PROJECILE_MULTISHOT_ANGLE, ProjectileOwner.PLAYER)
            self.game_state.add_object(projectile_1)
            self.game_state.add_object(projectile_2)
        self.shoot_sound.play()

class Projectile(Object2D):
    owner: ProjectileOwner
    pos: tuple[number, number]
    vel: tuple[number, number]
    color: tuple[int, int, int] = (255, 0, 0)
    direction: number
    collider: module_collider.BoxCollider
    game_state: module_game_state.AndromedaClashGameState
    width = consts.PROJECTILE_WIDTH
    height = consts.PROJECTILE_HEIGHT
    hitbox_width = consts.PROJECTILE_HITBOX_WIDTH
    hitbox_height = consts.PROJECTILE_HITBOX_HEIGHT
    def __init__(self, pos: tuple[number, number], vel: tuple[number, number], direction: number, owner: ProjectileOwner):
        self.pos = pos
        self.vel = vel
        self.direction = direction
        self.collider = self.get_collider()
        self.owner = owner
    
    def get_collider(self):
        return module_collider.BoxCollider(self.hitbox_width, self.hitbox_height, self.pos)
    
    def draw(self, canvas):
        offset = (math.sin(self.direction) * self.height, -math.cos(self.direction) * self.height)
        pygame.draw.line(
            canvas,
            self.color,
            (self.pos[0] - offset[0] / 2, self.pos[1] - offset[1] / 2),
            (self.pos[0] + offset[0] / 2, self.pos[1] + offset[1] / 2),
            self.width
        )
    
    def update(self):
        if self.pos[1] < -50:
            self.game_state.remove_object(self)
        self.pos = (
            self.pos[0] + self.vel[0],
            self.pos[1] + self.vel[1]
        )
        self.collider.position = self.pos

class PiercingProjectile(Projectile):
    _hit_enemies: data_structures.ObjectDict[float]
    color = (0, 255, 255)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hit_enemies = data_structures.ObjectDict()
    
    def register_enemy(self, enemy: Object2D):
        self._hit_enemies[enemy] = time.time() + consts.PIERCING_PROJECTILE_ENEMY_COOLDOWN
    
    def _clean(self):
        for obj, __time in self._hit_enemies.items():
            if __time < time.time():
                self._hit_enemies.pop(obj)
    
    def has_hit_enemy(self, enemy: Object2D):
        self._clean()
        return enemy in self._hit_enemies

class FireProjectile(PiercingProjectile):
    width = consts.FIRE_PROJECTILE_WIDTH
    height = consts.FIRE_PROJECTILE_HEIGHT
    hitbox_width = consts.FIRE_PROJECTILE_HITBOX_WIDTH
    hitbox_height = consts.FIRE_PROJECTILE_HITBOX_HEIGHT
    color = (255, 0, 0)

class PowerUp(Object2D):
    '''
    PowerUps verbessern die Eigenschaften des Raumschiffes oder machen die Rahmenbedingungen einfacher. Sie fallen senkrecht nach unten und müssen eingesammelt werden.
    '''
    pos: tuple[number, number]
    vel: tuple[number, number]
    size: number
    type: str
    collider: module_collider.CircleCollider
    color: tuple[int, int, int]
    end_time: float
    effect_time: float
    game_state: module_game_state.AndromedaClashGameState
    activated: bool = False
    arc_cooldown: ArcCooldown
    image: Image
    IMAGE_FILE: Path

    def __init__(self, pos: tuple[number, number], vel: tuple[number, number]):
        self.pos = pos
        self.vel = vel
        self.size = consts.POWERUP_HITBOX_RADIUS
        self.collider = module_collider.CircleCollider(consts.POWERUP_HITBOX_RADIUS, pos)
        self.image = pygame.transform.scale(load_image(self.IMAGE_FILE), (consts.POWERUP_HEIGHT, consts.POWERUP_WIDTH))

    @classmethod
    @abstractmethod
    def make_one(cls, pos: tuple[number, number], vel: tuple[number, number]) -> Self:
        pass
       
    def update(self):
        if (self.pos[1] > consts.SCREEN_HEIGHT + self.size):
            self.game_state.remove_object(self)
        self.pos[1] += self.vel[1]
        self.collider.position = self.pos
        self.collision()

    def collision(self):
        if self.collider.collides(self.game_state.player.collider):
            self.game_state.activate_powerup(self)
    
    def draw(self, canvas):
        canvas.blit(self.image, (self.pos[0] - consts.POWERUP_WIDTH / 2, self.pos[1] - consts.POWERUP_HEIGHT / 2))

    @abstractmethod
    def activate_power(self):
        pass

    @abstractmethod
    def deactivate_power(self):
        pass
    
    @abstractmethod
    def update_activated(self):
        pass
    
    @abstractmethod
    def __eq__(self, value) -> bool: # Soll zurückgeben ob ein anderes Powerup äquivalent ist
        pass
    
    @abstractmethod
    def __gt__(self, value) -> bool: # Soll zurückgeben ob dieses Powerup ein anderes Powerup enthält.
        pass

    def set_pos(self, new_pos):
        self.pos = new_pos
    
    def set_vel(self, new_vel):
        self.vel = new_vel
    
    def __del__(self):
        if not self.activated:
            return
        self.deactivate_power()
        self.activated = False

class DoubleSpeedPowerUp(PowerUp):
    '''
    Diese PowerUp verursacht, dass die Schussrate temporär verdoppelt wird.
    '''
    strength: int
    effect_time = 20
    color = (0, 255, 0)
    IMAGE_FILE = consts.POWERUP_DOUBLESPEED_IMAGE_PATH

    def __init__(self, pos: tuple[number, number], vel: tuple[number, number], strength: int = 1):
        super().__init__(pos, vel)
        self.strength = strength

    @classmethod
    def make_one(cls, pos, vel):
        return cls(pos, vel)

    def activate_power(self):
        self.game_state.player.shot_cooldown /= 2
    
    def deactivate_power(self):
        self.game_state.player.shot_cooldown *= 2
    
    def update_activated(self):
        pass

    def __eq__(self, value):
        if not isinstance(value, DoubleSpeedPowerUp):
            return False
        return self.strength == value.strength
    
    def __gt__(self, value):
        if not isinstance(value, DoubleSpeedPowerUp):
            return False
        return self.strength > value.strength

class InvincibilityPowerUp(PowerUp):
    '''
    Dieses PowerUp verursacht, dass der Spieler zeitweise nicht getroffen werden kann oder anderweitig Schaden erleidet.
    '''
    strength: int
    effect_time = 20
    color = (0, 0, 255)
    IMAGE_FILE = consts.POWERUP_INVINCIBILITY_IMAGE_PATH

    def __init__(self, pos: tuple[number, number], vel: tuple[number, number], strength: int = 1):
        super().__init__(pos, vel)
        self.strength = strength

    def activate_power(self):
        self.game_state.player.invincible = True

    def deactivate_power(self):
        self.game_state.player.invincible = False

    @classmethod
    def make_one(cls, pos, vel):
        return cls(pos, vel)
    
    def update_activated(self):
        pass

    def __eq__(self, value):
        if not isinstance(value, InvincibilityPowerUp):
            return False
        return self.strength == value.strength
    
    def __gt__(self, value):
        if not isinstance(value, InvincibilityPowerUp):
            return False
        return self.strength > value.strength

class DoublePointsPowerUp(PowerUp):
    '''
    Dieses PowerUp verursacht, dass der Spieler zeitweise die Doppelte Anzahl an Punkten pro Kill für den Score erhält.
    '''
    strength: int
    effect_time = 20
    color = (200, 55, 100)
    IMAGE_FILE = consts.POWERUP_DOUBLEPOINTS_IMAGE_PATH

    def __init__(self, pos: tuple[number, number], vel: tuple[number, number], strength: int = 1):
        super().__init__(pos, vel)
        self.strength = strength

    def activate_power(self):
        self.game_state.player.point_multiplier += 1

    def deactivate_power(self):
        self.game_state.player.point_multiplier -= 1

    @classmethod
    def make_one(cls, pos, vel):
        return cls(pos, vel)
    
    def update_activated(self):
        pass

    def __eq__(self, value):
        if not isinstance(value, DoublePointsPowerUp):
            return False
        return self.strength == value.strength
    
    def __gt__(self, value):
        if not isinstance(value, DoublePointsPowerUp):
            return False
        return self.strength > value.strength
    
class DoubleDamagePowerUp(PowerUp):
    '''
    Dieses PowerUp verursacht, dass der Spieler zeitweise Gegnern und Steinen doppelten Schaden zufügt.
    '''
    strength: int
    effect_time = 20
    color = (255, 0, 0)
    IMAGE_FILE = consts.POWERUP_DOUBLEDAMAGE_IMAGE_PATH

    def __init__(self, pos: tuple[number, number], vel: tuple[number, number], strength: int = 1):
        super().__init__(pos, vel)
        self.strength = strength

    def activate_power(self):
        self.game_state.player.damage_multiplier += 1

    def deactivate_power(self):
        self.game_state.player.damage_multiplier -= 1

    @classmethod
    def make_one(cls, pos, vel):
        return cls(pos, vel)
    
    def update_activated(self):
        pass

    def __eq__(self, value):
        if not isinstance(value, DoubleDamagePowerUp):
            return False
        return self.strength == value.strength
    
    def __gt__(self, value):
        if not isinstance(value, DoubleDamagePowerUp):
            return False
        return self.strength > value.strength

class StrikePowerUp(PowerUp):
    '''
    Dieses PowerUp verursacht, dass der Spieler, mit Durchschussprojektilen schießt, wodurch er mit einem Schuss mehrere Gegner / Steine, aber keinen Stein / Gegner mehrfach, treffen kann.
    
    '''
    strength: int
    effect_time = 20
    color = (0, 255, 255)
    IMAGE_FILE = consts.POWERUP_STRIKE_IMAGE_PATH

    def __init__(self, pos: tuple[number, number], vel: tuple[number, number], strength: int = 1):
        super().__init__(pos, vel)
        self.strength = strength

    def activate_power(self):
        if type(self.game_state.player) == SpaceShip:
            self.game_state.player.piercing = True

    def deactivate_power(self):
        if type(self.game_state.player) == SpaceShip:
            self.game_state.player.piercing = False

    @classmethod
    def make_one(cls, pos, vel):
        return cls(pos, vel)
    
    def update_activated(self):
        pass

    def __eq__(self, value):
        if not isinstance(value, StrikePowerUp):
            return False
        return self.strength == value.strength
    
    def __gt__(self, value):
        if not isinstance(value, StrikePowerUp):
            return False
        return self.strength > value.strength

class MultishotPowerUp(PowerUp):
    '''
    Dieses PowerUp verursacht, dass der Spieler zeitweise mit mehreren Projektilen in verschiedene Richtungen schießt.
    '''
    strength: int
    effect_time = 20
    color = (255, 0, 255)
    IMAGE_FILE = consts.POWERUP_MULTISHOT_IMAGE_PATH

    def __init__(self, pos: tuple[number, number], vel: tuple[number, number], strength: int = 1):
        super().__init__(pos, vel)
        self.strength = strength

    def activate_power(self):
        if type(self.game_state.player) == SpaceShip:
            self.game_state.player.multishot = True

    def deactivate_power(self):
        if type(self.game_state.player) == SpaceShip:
            self.game_state.player.multishot = False

    @classmethod
    def make_one(cls, pos, vel):
        return cls(pos, vel)
    
    def update_activated(self):
        pass

    def __eq__(self, value):
        if not isinstance(value, MultishotPowerUp):
            return False
        return self.strength == value.strength
    
    def __gt__(self, value):
        if not isinstance(value, MultishotPowerUp):
            return False
        return self.strength > value.strength
    
POWERUP_TYPES: list[type[PowerUp]] = [DoubleSpeedPowerUp, InvincibilityPowerUp, DoublePointsPowerUp, DoubleDamagePowerUp, StrikePowerUp, MultishotPowerUp] # Ansonsten funnktioniert es nicht. (wenn nicht in dieser Datei)

class Stone(Object2D):
    pos: tuple[number, number]
    vel: tuple[number, number]
    collider: module_collider.CircleCollider
    death_sound: module_sound.Sound
    lives: int
    health_bar: HealthBar
    game_state: module_game_state.AndromedaClashGameState
    image: Image
    turning_speed: float
    exist_time: int
    
    def __init__(self, pos: tuple[number, number], vel: tuple[number, number], size: Literal[1, 2, 3, 4], turning_speed: float = 0.002):
        self.pos = pos
        self.vel = vel
        self.size = consts.STONE_BASE_RADIUS * size
        self.collider = module_collider.CircleCollider(consts.STONE_BASE_HITBOX_RADIUS * size, pos)
        self.death_sound = module_sound.load_sound(consts.EXPLOSION_SOUND_PATH)
        self.lives = consts.STONE_LIVES
        self.color = consts.STONE_COLOR
        self.health_bar = HealthBar(self.pos, self.lives, self.lives, self)
        self.image = pygame.transform.scale(load_image(consts.STONE_IMAGE_PATH), (self.size * 2, self.size * 2))
        self.turning_speed = turning_speed
        self.exist_time = 0

    def update(self):
        self.exist_time += 1
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
            elif isinstance(g, PiercingProjectile) and g.has_hit_enemy(self):
                pass
            elif self.collider.collides(g.collider):
                if isinstance(g, PiercingProjectile):
                    g.register_enemy(self)
                else:
                    self.game_state.remove_object(g)
                self.lives -= self.game_state.player.attack_damage
                self.health_bar.lives = self.lives
                if self.lives > 0:
                    continue
                if self.size / consts.STONE_BASE_RADIUS >= consts.STONE_SIZES[1]:
                    self.split_stone()
                self.game_state.remove_object(self)
                self.death_sound.play()
                if g.owner != ProjectileOwner.ENEMY:
                    self.game_state.score += consts.SCORE_STONE * self.game_state.player.point_multiplier
                self.game_state.update_score()


    def split_stone(self):
        '''
        Wird ein Stein getroffen, teilt er sich in 2 kleinere auf. Beide fliegen gleich schnell nach unten und zur Seite. Jedoch einer nach rechts und einer nach links.        
        '''
        
        # Magic Numbers vermeiden, und Kommentare zu den Operationen
        weight_a = random.random() * 0.25 + 0.375
        vel_x = self.vel[0] * 2.5
        vel_y = self.vel[1] * 2.2
        self.game_state.add_object(
            Stone(self.pos, (vel_x * weight_a, vel_y * weight_a), (self.size // consts.STONE_BASE_RADIUS) - 1, self.turning_speed)
        )
        self.game_state.add_object(
            Stone(self.pos, (-vel_x * (1 - weight_a), vel_y * (1 - weight_a)), (self.size // consts.STONE_BASE_RADIUS) - 1, -self.turning_speed)
        )

    def draw(self, canvas):
        if self.health_bar.lives < self.health_bar.max_lives:
            self.health_bar.pos = (self.pos[0], self.pos[1] - self.size - consts.HEALTH_BAR_HEIGHT - 2)
            self.health_bar.draw(canvas)
        canvas.blit(pygame.transform.rotate(self.image, self.turning_speed * (self.exist_time + 1000)), (self.pos[0] - self.size, self.pos[1] - self.size))

    def set_pos(self, new_pos):
        self.pos = new_pos
    
    def set_vel(self, new_vel):
        self.vel = new_vel  
        
class CommonEnemy(Object2D):
    pos: tuple[number, number]
    vel: tuple[number, number]
    size: tuple[number, number] = (consts.ENEMY_WIDTH, consts.ENEMY_HEIGHT)
    hitbox_width = consts.ENEMY_HITBOX_WIDTH
    hitbox_height = consts.ENEMY_HITBOX_HEIGHT
    collider: module_collider.BoxCollider
    shot_cooldown_timer: int
    shot_sound: module_sound.Sound
    lives: int
    image: Image
    health_bar: HealthBar
    game_state: module_game_state.AndromedaClashGameState
    target_height: float
    shot_cooldown = consts.ENEMY_SHOT_COOLDOWN
    projectile_speed = consts.PROJECTILE_SPEED
    max_lives = consts.ENEMY_LIVES

    def __init__(self, pos: tuple[number, number], vel: tuple[number, number], target_height: float):
        self.pos = pos
        self.vel = vel
        self.collider = module_collider.BoxCollider(self.hitbox_width, self.hitbox_height, pos)
        self.color = consts.ENEMY_COLOR[0]
        self.shot_cooldown_timer = self.shot_cooldown
        self.shot_sound = module_sound.load_sound(consts.SHOOT_SOUND_PATH)
        self.damage_sound = module_sound.load_sound(consts.HIT_SOUND_PATH)
        self.lives = self.max_lives
        self.image = self.get_image()
        self.health_bar = self.get_health_bar()
        self.target_height = target_height
    
    def get_health_bar(self) -> HealthBar:
        return HealthBar(self.pos, self.lives, self.lives, self)
        
    def get_image(self) -> Image:
        return pygame.transform.flip(
            pygame.transform.scale(
                load_image(consts.ENEMY_IMAGE_PATH), self.size
            ),
            False, True
        )

    def update(self):
        if (self.pos[1] > consts.SCREEN_HEIGHT + self.size[1]):
            self.game_state.remove_object(self)
        self.pos = (
            (self.pos[0] + self.vel[0] + self.size[0]) % (consts.SCREEN_WIDTH + self.size[0] * 2) - self.size[0],
            self.pos[1] + self.vel[1]
        )
        self.vel = (
            self.vel[0],
            (self.target_height - self.pos[1]) * 0.01
        )
        self.collider.position = self.pos
        self.collision()
        self.handle_shooting()
    
    def handle_shooting(self):
        self.shot_cooldown_timer -= 1
        if self.shot_cooldown_timer <= 0:
            self.handle_shot()
            self.shot_cooldown_timer = self.shot_cooldown
    
    def handle_shot(self):
        projectile = Projectile((self.pos[0], self.pos[1] + consts.ENEMY_HEIGHT / 2 + consts.PROJECTILE_HEIGHT / 2), (0, self.projectile_speed), 0, ProjectileOwner.ENEMY)
        self.game_state.add_object(projectile)
        self.shot_sound.play()

    def collision(self):
        for g in self.game_state.current_objects:
            if not isinstance(g, Projectile) and not isinstance(g, Stone):
                continue
            if isinstance(g, Projectile) and g.owner != ProjectileOwner.PLAYER:
                continue
            if isinstance(g, PiercingProjectile) and g.has_hit_enemy(self):
                continue
            if not self.collider.collides(g.collider):
                continue
            
            if isinstance(g, PiercingProjectile):
                g.register_enemy(self)
            else:
                self.game_state.remove_object(g)
            self.lives -= self.game_state.player.attack_damage
            if self.lives > 0:
                self.health_bar.lives = self.lives
                self.damage_sound.play()
                continue

            self.damage_sound.play()
            self.game_state.remove_object(self)
            self.game_state.score += consts.SCORE_ENEMY * self.game_state.player.point_multiplier
            self.game_state.update_score()

    def draw(self, canvas):
        self.health_bar.pos = (self.pos[0], self.pos[1] - consts.ENEMY_HEIGHT / 2 - consts.HEALTH_BAR_HEIGHT - 2)
        self.health_bar.draw(canvas)
        canvas.blit(self.image, (self.pos[0] - consts.ENEMY_WIDTH / 2, self.pos[1] - consts.ENEMY_HEIGHT / 2))
        
    def set_pos(self, new_pos):
        self.pos = new_pos
    
    def set_vel(self, new_vel):
        self.vel = new_vel

class PiercingProjectileEnemy(CommonEnemy):
    def handle_shot(self):
        projectile = PiercingProjectile((self.pos[0], self.pos[1] + consts.ENEMY_HEIGHT / 2 + consts.PROJECTILE_HEIGHT / 2), (0, self.projectile_speed), 0, ProjectileOwner.ENEMY)
        self.game_state.add_object(projectile)
        self.shot_sound.play()
    
    def get_image(self) -> Image:
        return pygame.transform.flip(
            pygame.transform.scale(
                load_image(consts.PIERCING_ENEMY_IMAGE_PATH), (consts.ENEMY_WIDTH, consts.ENEMY_HEIGHT)
            ),
            False, True
        )

class FireEnemy(CommonEnemy):
    shot_cooldown = consts.FIRE_ENEMY_SHOT_COOLDOWN
    projectile_speed = consts.FIRE_PROJECTILE_SPEED
    def handle_shot(self):
        projectile = FireProjectile((self.pos[0], self.pos[1] + consts.ENEMY_HEIGHT / 2 + consts.FIRE_PROJECTILE_HEIGHT / 2), (0, self.projectile_speed), 0, ProjectileOwner.ENEMY)
        self.game_state.add_object(projectile)
        self.shot_sound.play()
    
    def get_image(self) -> Image:
        return pygame.transform.flip(
            pygame.transform.scale(
                load_image(consts.FIRE_ENEMY_IMAGE_PATH), self.size
            ),
            False, True
        )

class BossEnemy(CommonEnemy):
    shot_cooldown = consts.BOSS_ENEMY_SHOT_COOLDOWN
    max_lives = consts.BOSS_ENEMY_LIVES
    projectile_speed = consts.FIRE_PROJECTILE_SPEED
    hitbox_width = consts.BOSS_ENEMY_HITBOX_WIDTH
    hitbox_height = consts.BOSS_ENEMY_HITBOX_HEIGHT
    size = (consts.BOSS_ENEMY_WIDTH, consts.BOSS_ENEMY_HEIGHT)
    
    def __init__(self, pos, vel, target_height):
        super().__init__(pos, vel, target_height)
        self.vel = (
            1.0,
            self.vel[1]
        )
    
    def update(self):
        self.vel = (
            self.vel[0] + (consts.SCREEN_WIDTH / 2 - self.pos[0]) * 0.0002,
            self.vel[1]
        )
        return super().update()
    
    def get_health_bar(self) -> HealthBar:
        return BossBar(self.pos, self.lives, self.lives, self)
    
    def handle_shot(self):
        projectile_middle = FireProjectile((self.pos[0] + consts.BOSS_ENEMY_WIDTH / 2, self.pos[1] + consts.BOSS_ENEMY_HEIGHT / 2 + consts.FIRE_PROJECTILE_HEIGHT / 2), (0, self.projectile_speed), 0, ProjectileOwner.ENEMY)
        projectile_right = FireProjectile((self.pos[0] + consts.BOSS_ENEMY_WIDTH / 2, self.pos[1] + consts.BOSS_ENEMY_HEIGHT / 2 - consts.FIRE_PROJECTILE_HEIGHT / 2), (math.sin(consts.PROJECILE_MULTISHOT_ANGLE) * self.projectile_speed, math.cos(consts.PROJECILE_MULTISHOT_ANGLE) * self.projectile_speed), -consts.PROJECILE_MULTISHOT_ANGLE, ProjectileOwner.ENEMY)
        projectile_left = FireProjectile((self.pos[0] + consts.BOSS_ENEMY_WIDTH / 2, self.pos[1] + consts.BOSS_ENEMY_HEIGHT / 2 - consts.FIRE_PROJECTILE_HEIGHT / 2), (-math.sin(consts.PROJECILE_MULTISHOT_ANGLE) * self.projectile_speed, math.cos(consts.PROJECILE_MULTISHOT_ANGLE) * self.projectile_speed), consts.PROJECILE_MULTISHOT_ANGLE, ProjectileOwner.ENEMY)
        self.game_state.add_object(projectile_middle)
        self.game_state.add_object(projectile_right)
        self.game_state.add_object(projectile_left)
        self.shot_sound.play()

    def get_image(self) -> Image:
        return pygame.transform.flip(
            pygame.transform.scale(
                load_image(consts.BOSS_ENEMY_IMAGE_PATH), (consts.BOSS_BAR_WIDTH, consts.BOSS_ENEMY_HEIGHT)
            ),
            False, True
        )

ENEMY_TYPES: list[type[CommonEnemy]] = [CommonEnemy, PiercingProjectileEnemy, FireEnemy, BossEnemy, BossEnemy]
ENEMY_COSTS: dict[type[CommonEnemy], int] = {CommonEnemy: 1, PiercingProjectileEnemy: 3, FireEnemy: 8, BossEnemy: 16}
ENEMY_THRESHOLDS: dict[type[CommonEnemy], int] = {CommonEnemy: 1, PiercingProjectileEnemy: 8, FireEnemy: 14, BossEnemy: 22}

class LifeDisplay(Object2D):
    image: Image
    pos: tuple[number, number]
    lives: int
    image_width: number
    def __init__(self, lives: int = 3):
        self.image = load_image(consts.HEART_IMAGE_PATH)
        self.image_width = self.image.get_width()
        self.lives = lives
        self.pos = consts.POS_LIVES
    
    def update(self):
        pass
    
    def get_draw_details(self):
        return consts.DrawDetails.TOP_LAYER

    def draw(self, canvas):
        for i in range(self.lives):
            canvas.blit(self.image, (self.pos[0] + (self.image_width + consts.LIFE_ICON_DISTANCE) * i, self.pos[1]))

class Text(Object2D): 
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GRAY = (200, 200, 200)
    img: SurfaceType
    pos: tuple[number, number]
    text: str
    text_color: tuple[int, int, int]
    text_size: int
    font: pygame.font.FontType
    justify: float
    
    def __init__(self, pos: tuple[number, number], text: str, text_size: int, text_color: tuple[int, int, int], justify: float = 0.5):
        self.pos = pos
        self.set_all(text, text_size, text_color)
        self.justify = justify
        
    def update(self):
        pass
        
    def draw(self, canvas):
        rect = self.img.get_rect()
        pos_x = self.pos[0] - rect.width * self.justify
        pos_y = self.pos[1] - rect.height * self.justify
        canvas.blit(self.img, (pos_x, pos_y))       # Zeichnen des Textes
        
    def set_all(self, text: str, text_size: int, text_color: tuple[int, int, int]):               # Setter-Methoden
        self.text = text
        self.text_color = text_color
        self.set_text_size(text_size)
        
    def set_text(self, text: str):
        self.text = text
        self.img = self.font.render(self.text, True, self.text_color)       
        
    def set_text_size(self, text_size: int):
        self.text_size = text_size
        self.font = self.load_font(consts.FONT_NAME, text_size)       # Font aktualisieren/erstellen
        self.img = self.font.render(self.text, True, self.text_color)       # Text aktualisieren/erstellen
        
    def set_text_color(self, text_color: tuple[int, int, int]):
        self.text_color = text_color
        self.img = self.font.render(self.text, True, self.text_color)
    
    @staticmethod
    @lru_cache(256)
    def load_font(name: str | Path, size: int) -> pygame.font.FontType:
        return pygame.font.Font(name, size)

class GameOverText(Text):
    def get_draw_details(self):
        return consts.DrawDetails.TOP_LAYER

class Score(Text):
    def get_draw_details(self):
        return consts.DrawDetails.TOP_LAYER

class Credits(Text):
    def get_draw_details(self):
        return consts.DrawDetails.TOP_LAYER
    
class HealthBar(Object2D):
    max_lives: int
    lives: int
    pos: tuple[number, number]
    height: int = consts.HEALTH_BAR_HEIGHT
    width: int = consts.HEALTH_BAR_WIDTH
    parent: Object2D
    color: tuple[int, int, int] = consts.HEALTH_BAR_COLOR
    background_color: tuple[int, int, int] = consts.HEALTH_BAR_BACKGROUND_COLOR
    slice_color: tuple[int, int, int] = consts.HEALTH_BAR_SLICE_COLOR
    
    def __init__(self, pos: tuple[number, number], lives: int, max_lives: int, parent: Object2D):
        self.pos = pos
        self.lives = lives
        self.max_lives = max_lives
        self.parent = parent

    @property
    def parent_game_state(self) -> module_game_state.AndromedaClashGameState:
        assert isinstance(g_s := self.parent.game_state, module_game_state.AndromedaClashGameState)
        return g_s

    def update(self):
        pass

    def draw(self, canvas):
        pos_x = self.pos[0]
        pos_y = self.pos[1]
        pygame.draw.rect(canvas, self.background_color, (pos_x - self.width / 2, pos_y, self.width, self.height))
        pygame.draw.rect(canvas, self.color, (pos_x - self.width / 2, pos_y, self.width * (self.lives / self.max_lives), self.height))
        player_attack_damage = self.parent_game_state.player.attack_damage
        for i in range(0, math.ceil(self.lives / player_attack_damage)):
            health_step = self.lives - i * player_attack_damage
            pygame.draw.rect(canvas, self.slice_color, (pos_x - self.width / 2 - consts.HEALTH_BAR_SLICE_WIDTH / 2 + self.width * (health_step / self.max_lives), pos_y, consts.HEALTH_BAR_SLICE_WIDTH, self.height))

class BossBar(HealthBar):
    width = consts.BOSS_BAR_WIDTH
    color = consts.BOSS_BAR_COLOR
    slice_color = consts.BOSS_BAR_COLOR
    
    def draw(self, canvas):
        self.pos = (self.pos[0] + consts.BOSS_ENEMY_WIDTH / 2, self.pos[1])
        return super().draw(canvas)

class ArcCooldown(Object2D):
    max_time: float
    end_time: float
    pos: tuple[number, number]
    radius: int = consts.ARC_COOLDOWN_RADIUS
    parent: Object2D
    color: tuple[int, int, int] = consts.ARC_COOLDOWN_COLOR
    
    def __init__(self, pos: tuple[number, number], end_time: float, max_time: float, parent: Object2D):
        self.pos = pos
        self.end_time = end_time
        self.max_time = max_time
        self.parent = parent
    
    @property
    def parent_game_state(self) -> module_game_state.AndromedaClashGameState:
        assert isinstance(g_s := self.parent.game_state, module_game_state.AndromedaClashGameState)
        return g_s

    def update(self):
        pass
    
    def draw(self, canvas):
        pos_x = self.pos[0]
        pos_y = self.pos[1]
        fraction = (self.end_time - time.time()) / self.max_time
        pygame.draw.arc(canvas, self.color, (pos_x - self.radius, pos_y - self.radius, self.radius * 2, self.radius * 2), -math.pi / 2, (fraction - 0.25) * math.pi * 2)

class UsernameInputTracker(Object2D):
    username: str
    game_state: module_game_state.AndromedaClashGameState
    keys: dict[consts.key, str]= {
        consts.key.a: "A",
        consts.key.b: "B",
        consts.key.c: "C",
        consts.key.d: "D",
        consts.key.e: "E",
        consts.key.f: "F",
        consts.key.g: "G",
        consts.key.h: "H",
        consts.key.i: "I",
        consts.key.j: "J",
        consts.key.k: "K",
        consts.key.l: "L",
        consts.key.m: "M",
        consts.key.n: "N",
        consts.key.o: "O",
        consts.key.p: "P",
        consts.key.q: "Q",
        consts.key.r: "R",
        consts.key.s: "S",
        consts.key.t: "T",
        consts.key.u: "U",
        consts.key.v: "V",
        consts.key.w: "W",
        consts.key.x: "X",
        consts.key.y: "Y",
        consts.key.z: "Z",
        consts.key.zero: "0",
        consts.key.one: "1",
        consts.key.two: "2",
        consts.key.three: "3",
        consts.key.four: "4",
        consts.key.five: "5",
        consts.key.six: "6",
        consts.key.seven: "7",
        consts.key.eight: "8",
        consts.key.nine: "9",
        consts.key.SPACE: "_",
        consts.key.MINUS: "_",
        consts.key.PLUS: "_",
        consts.key.UNDERSCORE: "_"
    }
    def __init__(self):
        self.username = ""
    
    def draw(self, canvas):
        pass
    
    def update(self):
        for key, value in self.keys.items():
            if self.user_input.get_key_down_now(key):
                self.username += value
        if self.user_input.get_key_down_now(consts.key.BACKSPACE):
            self.username = self.username[:-1]
        self.username = self.username[:32]
        text = self.username + ("_" if self.game_state.current_tick % 20 < 10 else "")
        self.game_state.username_input.justify = 0.0
        self.game_state.username_input.set_text(text)
        self.game_state.username = self.username