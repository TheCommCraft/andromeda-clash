from __future__ import annotations
from abc import ABC, abstractmethod
from itertools import combinations, product
from dataclasses import dataclass, field
from typing import Optional
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
        if isinstance(other, RotatedRectangleCollider):
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
        if isinstance(other, RotatedRectangleCollider):
            return other.collide_circle_collider(self)
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

class EmptyCollider(PositionedCollider):
    def __init__(self, position: tuple[number, number] = (0, 0)):
        self.position = position
        
    def collides(self, other):
        return False

def line_collision(
    a_g: number, b_g: number, e_g: number, f_g: number, # XY of first and second position of line a
    a_f: number, b_f: number, e_f: number, f_f: number  # XY of first and second position of line b
    ) -> bool:
    c_g = e_g - a_g
    d_g = f_g - b_g
    c_f = e_f - a_f
    d_f = f_f - b_f
    try:
        t_f = (a_f - a_g + (c_g / d_g) * (b_g - b_f)) / ((d_f * c_g) / d_g - c_f)
        t_g = (b_f + t_f * d_f - b_g) / d_g
    except ZeroDivisionError:
        return False
    if not (0 <= t_g <= 1):
        return False
    if not (0 <= t_f <= 1):
        return False
    return True


class RotatedRectangleCollider(BoxCollider):
    @dataclass
    class BoundingBoxCache:
        pos_x: Optional[number] = field(default=None)
        pos_y: Optional[number] = field(default=None)
        width: Optional[number] = field(default=None)
        height: Optional[number] = field(default=None)
        rotation: Optional[number] = field(default=None)
        bounding_box: Optional[BoxCollider] = field(default=None)
    rotation: number
    _bounding_box_cache: BoundingBoxCache
    
    def __init__(self, width: number, height: number, position: tuple[number, number] = (0, 0), rotation: number = 0):
        super().__init__(width, height, position)
        self.rotation = rotation
        self._bounding_box_cache = self.BoundingBoxCache()
    
    @staticmethod
    def _rotate_position(pos_x: number, pos_y: number, rotation: number) -> tuple[number, number]:
        return (
            pos_y * math.sin(rotation) + pos_x * math.cos(rotation),
            pos_y * math.cos(rotation) - pos_x * math.sin(rotation)
        )
    
    @property
    def _two_relative_corners(self) -> tuple[tuple[number, number], tuple[number, number]]:
        dx_a, dy_a = self._rotate_position(self.width, self.height, self.rotation)
        dx_b, dy_b = self._rotate_position(-self.width, self.height, self.rotation)
        return ((dx_a / 2, dy_a / 2), (dx_b / 2, dy_b / 2))
    
    @property
    def bounding_box(self) -> BoxCollider:
        if (
            not self._bounding_box_cache.bounding_box or
            self._bounding_box_cache.width != self.width or
            self._bounding_box_cache.height != self.height or
            self._bounding_box_cache.rotation != self.rotation
        ):
            ((dx_a, dy_a), (dx_b, dy_b)) = self._two_relative_corners
            if abs(dx_a) > abs(dx_b):
                dx = dx_a * 2
            else:
                dx = dx_b * 2
            if abs(dy_a) > abs(dy_b):
                dy = dy_a * 2
            else:
                dy = dy_b * 2
            self._bounding_box_cache.bounding_box = BoxCollider(abs(dx), abs(dy), self.position)
            self._bounding_box_cache.pos_x = self.pos_x
            self._bounding_box_cache.pos_y = self.pos_y
            self._bounding_box_cache.width = self.width
            self._bounding_box_cache.height = self.height
            self._bounding_box_cache.rotation = self.rotation
        if self._bounding_box_cache.pos_x != self.pos_x or self._bounding_box_cache.pos_y != self.pos_y:
            self._bounding_box_cache.pos_x = self.pos_x
            self._bounding_box_cache.pos_y = self.pos_y
            self._bounding_box_cache.bounding_box.position = self.position
        return self._bounding_box_cache.bounding_box
    
    def collides(self, other: Collider):
        if isinstance(other, CircleCollider):
            return self.collide_circle_collider(other)
        elif isinstance(other, BoxCollider):
            return self.collide_box_collider(other)
        elif isinstance(other, RotatedRectangleCollider):
            return self.collide_rotated_rectangle_collider(other)
        return False
    
    def collide_circle_collider(self, other: CircleCollider) -> bool:
        rotated_circle_position = self._rotate_position(other.pos_x - self.pos_x, other.pos_y - self.pos_y, -self.rotation)
        new_circle = CircleCollider(other.radius, (rotated_circle_position[0] + self.pos_x, rotated_circle_position[1] + self.pos_y))
        return new_circle.collide_box_collider(self)
    
    def collide_box_collider(self, other: BoxCollider) -> bool:
        if not self.bounding_box.collides(other):
            return False
        rotated_box_position = self._rotate_position(other.pos_x - self.pos_x, other.pos_y - self.pos_y, -self.rotation)
        new_box = BoxCollider(0, 0, (rotated_box_position[0] + self.pos_x, rotated_box_position[1] + self.pos_y))
        if new_box.collide_box_collider(self):
            return True
        ((dx_a, dy_a), (dx_b, dy_b)) = self._two_relative_corners
        points_a = [
            (self.pos_x + dx_a, self.pos_y + dy_a), (self.pos_x + dx_b, self.pos_y + dy_b),
            (self.pos_x - dx_a, self.pos_y - dy_a), (self.pos_x - dx_b, self.pos_y - dy_b)
        ]
        lines_a = list(combinations(points_a, 2))
        points_b = [
            (other.pos_x + other.width / 2, other.pos_y + other.height / 2), (other.pos_x + other.width / 2, other.pos_y - other.height / 2),
            (other.pos_x - other.width / 2, other.pos_y + other.height / 2), (other.pos_x - other.width / 2, other.pos_y - other.height / 2)
        ]
        lines_b = list(combinations(points_b, 2))
        for (((a_g, b_g), (e_g, f_g)), ((a_f, b_f), (e_f, f_f))) in product(lines_a, lines_b):
            if line_collision(a_g, b_g, e_g, f_g, a_f, b_f, e_f, f_f):
                return True
        return False
    
    def collide_rotated_rectangle_collider(self, other: RotatedRectangleCollider) -> bool:
        rotated_rect_position = self._rotate_position(other.pos_x - self.pos_x, other.pos_y - self.pos_y, -other.rotation)
        new_box = BoxCollider(other.width, other.height, (rotated_rect_position[0] + self.pos_x, rotated_rect_position[1] + self.pos_y))
        new_self = RotatedRectangleCollider(self.width, self.height, self.position, self.rotation - other.rotation)
        return new_self.collide_box_collider(new_box)
