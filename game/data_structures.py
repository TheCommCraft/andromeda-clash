from __future__ import annotations
from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar
from . import objects as module_objects

T = TypeVar("T")
class ReferenceToObject(Generic[T]):
    obj: T
    def __init__(self, obj: T):
        self.obj = obj
    
    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return id(self.obj) == id(other.obj)
    
    def __hash__(self) -> int:
        return hash(id(self.obj))

class ObjectContainer:
    objects: set[ReferenceToObject[module_objects.Object2D]]
    def __init__(self, start_value: Iterable[module_objects.Object2D] = ()):
        self.objects = {ReferenceToObject(obj) for obj in start_value}
    
    def add_object(self, value: module_objects.Object2D):
        self.objects.add(ReferenceToObject(value))

    def remove_object(self, value: module_objects.Object2D):
        self.objects.remove(ReferenceToObject(value))
    
    def __iter__(self) -> Iterator[module_objects.Object2D]:
        return iter(obj.obj for obj in self.objects.copy())
    
    def __contains__(self, value: object) -> bool:
        return ReferenceToObject(value) in self.objects
    
    def __len__(self) -> int:
        return len(self.objects)