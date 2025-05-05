from __future__ import annotations
from abc import ABC, abstractmethod

class Collider(ABC):
    @abstractmethod
    def collides(self, other: Collider) -> bool:
        pass

number = float | int

class BoxCollider(Collider):
    width: number
    height: number
    pos_x: number
    pos_y: number
    @property
    def size(self) -> tuple[number, number]:
        return (self.width, self.height)
    
    @property
    def position(self) -> tuple[number, number]:
        return (self.pos_x, self.pos_y)
    
    @position.setter
    def position(self, value: tuple[number, number]) -> None:
        self.pos_x = value[0]
        self.pos_y = value[1]
    
    def __init__(self, width: number, height: number, position: tuple[number, number]):
        self.width = width
        self.height = height
        self.position = position
    
    def collides(self, other: Collider):
        if isinstance(other, BoxCollider):
            return self.collide_box_collider(other)
        return False # Falls es ein anderer Typ ist
        
    def collide_box_collider(self, other: BoxCollider):
        if abs(self.pos_x - other.pos_x) > (self.width + other.width) / 2:
            return False
        if abs(self.pos_y - other.pos_y) > (self.height + other.height) / 2:
            return False
        return True