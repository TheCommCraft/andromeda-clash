from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Iterable, Collection, Iterator
import random
import pygame
from . import objects
from . import user_input as module_user_input
from . import consts
from . import data_structures
import math

GAME_SIZE = (consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
min_y_vel_stone = 0.5
max_vel_stone = 1
step_stone = 0.001

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
    def __init__(self, canvas: objects.Canvas, user_input: module_user_input.UserInputType) -> None:
        self.canvas = canvas
        self.current_objects = data_structures.ObjectContainer()
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.user_input = user_input
    
    def add_object(self, obj: objects.Object2D):
        self.current_objects.add_object(obj)
    
    def remove_object(self, obj: objects.Object2D):
        self.current_objects.remove_object(obj)
    
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
            pygame.display.update() # Änderungen werden umgesetzt.
            self.clock.tick(self.fps)

    def spawn_stone(self):
        if random() < 0.001: # Wahrscheinlichkeit. dass ein Stein entsteht
            pos = (random.random()*GAME_SIZE[0], 0)
            
            vel_y = random.randrange(min_y_vel_stone, max_vel_stone, step_stone)
            vel_x = math.sqrt(max_vel_stone - vel[1]**2)
            vel = (vel_x, vel_y)
            size = random.randrange(1, 5)
            
            self.current_objects.append() # Stone muss noch hier erstellt werden
            # ^ Hier sollte self.add_object verwendet werden.
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
        if random.random() < 0.01:
            pos = (random.random() * GAME_SIZE[0], 0)
            vel_y = random.random() * (max_vel_stone - min_y_vel_stone) + min_y_vel_stone
            vel_x = math.sqrt(max_vel_stone - vel_y**2)
            vel = (vel_x, vel_y)
            size = random.randrange(1, 5)
            self.add_object(objects.Stone(pos, vel, size))