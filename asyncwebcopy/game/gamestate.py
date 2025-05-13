from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Collection
from pathlib import Path
import asyncio
import random
import pygame
import pyautogui
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
    shoot_or_damage_sound: module_sound.Sound
    min_y_vel_stone = 0.5
    max_vel_stone = 1
    stone_spawn_probability: float
    p_pos: tuple[float, float]
    def __init__(self, canvas: objects.Canvas, user_input: module_user_input.UserInputType) -> None:
        self.canvas = canvas
        self.current_objects = data_structures.ObjectContainer()
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.user_input = user_input
        self.shoot_or_damage_sound = module_sound.Sound(Path(Path(__file__).parent, "sounds", "shoot.wav"))
        self.stone_spawn_probability = consts.START_STONE_SPAWNING_PROBABILITY
        self.score = 0
        self.score_object = objects.Text(consts.POS_SCORE, f'SCORE {self.score}', consts.TEXT_SIZE_SCORE, consts.TEXT_COLOR_SCORE)
        self.p_pos = (0.0, 0.0)

    def add_object(self, obj: objects.Object2D):
        self.current_objects.add_object(obj)
    
    def remove_object(self, obj: objects.Object2D):
        self.current_objects.remove_object(obj)
    
    async def loop(self) -> None:
        running = True
        last_pos = None
        real_pos = pyautogui.Window(hWnd=pygame.display.get_wm_info()["window"]).topleft
        while running:
            self.canvas.fill((0, 0, 0)) # Hintergrund wird mit Schwarz gefüllt. (Farbenwerte werden als RGB-Tupel angegeben)
            self.user_input.process_tick()
            for event in pygame.event.get():
                self.user_input.process_event(event)
                if event.type == pygame.QUIT: # Falls Schliessen-Knopf gedruckt wird, wird das Programm beendet. 
                    running = False
            self.spawn_stone()
            current_objects = list(self.current_objects)
            for object2d in current_objects:
                if not hasattr(object2d, "game_state"):
                    object2d.game_state = self
                object2d.update()
            for object2d in current_objects:
                object2d.draw(self.canvas)
            pygame.display.update() # Änderungen werden umgesetzt.
            r_pos = last_pos and (self.p_pos[0] - last_pos[0], self.p_pos[1] - last_pos[1]) or (0, 0)
            last_pos = self.p_pos
            real_pos = (real_pos[0] + r_pos[0], real_pos[1] + r_pos[1])
            pyautogui.Window(hWnd=pygame.display.get_wm_info()["window"]).moveTo(int(real_pos[0]), int(real_pos[1]))
            self.clock.tick(self.fps)
            await asyncio.sleep(0)

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
        for obj in self.current_objects:
            self.remove_object(obj)
        self.add_object(objects.Text((consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT / 2), "Game over", 20, (255, 255, 255)))
    
    def update_score(self):
        self.score += 1
        self.score_object.set_text = f'Score {self.score}'