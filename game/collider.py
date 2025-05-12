from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Iterable
import math

class Collider(ABC):
    @abstractmethod
    def collides(self, other: Collider) -> bool:
        pass

number = float | int

class PositionedCollider(Collider):
    pos_x: number
    pos_y: number
    @property
    def position(self) -> tuple[number, number]:
        return (self.pos_x, self.pos_y)
    
    @position.setter
    def position(self, value: tuple[number, number]) -> None:
        self.pos_x = value[0]
        self.pos_y = value[1]

class BoxCollider(PositionedCollider):
    width: number
    height: number
    @property
    def size(self) -> tuple[number, number]:
        return (self.width, self.height)
    
    def __init__(self, width: number, height: number, position: tuple[number, number] = (0, 0)):
        self.width = width
        self.height = height
        self.position = position
    
    def collides(self, other):
        if isinstance(other, BoxCollider):
            return self.collide_box_collider(other)
        if isinstance(other, CircleCollider):
            return other.collide_box_collider(self)
        return False # Falls es ein anderer Typ ist
        
    def collide_box_collider(self, other: BoxCollider):
        if abs(self.pos_x - other.pos_x) > (self.width + other.width) / 2:
            return False
        if abs(self.pos_y - other.pos_y) > (self.height + other.height) / 2:
            return False
        return True

class CircleCollider(PositionedCollider):
    radius: number
    def __init__(self, radius: number, position: tuple[number, number] = (0, 0)):
        self.radius = radius
        self.position = position
    
    def collides(self, other):
        if isinstance(other, CircleCollider):
            return self.collide_circle_collider(other)
        if isinstance(other, BoxCollider):
            return self.collide_box_collider(other)
        return False
    
    def collide_circle_collider(self, other: CircleCollider):
        return math.sqrt((self.pos_x - other.pos_x) ** 2 + (self.pos_y - other.pos_y) ** 2) <= self.radius + other.radius
    
    def collide_box_collider(self, other: BoxCollider):
        dx, dy = other.pos_x - self.pos_x, other.pos_y - self.pos_y
        reduced_dx, reduced_dy = max(abs(dx) - other.width / 2, 0), max(abs(dy) - other.height / 2, 0)
        return math.sqrt(reduced_dx ** 2 + reduced_dy ** 2) <= self.radius



class PolyPositionedCollider(PositionedCollider):
    colliders: list[PositionedCollider]
    def __init__(self, colliders: Iterable[PositionedCollider], position: tuple[number, number] = (0, 0)):
        self.colliders = list(colliders)
        self.position = position
    
    def collides(self, other):
        for collider in self.colliders:
            collider.position = self.position
            if collider.collides(other):
                return True
        return False
