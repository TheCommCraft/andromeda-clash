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

O = TypeVar("O", bound="module_objects.Object2D")
V = TypeVar("V")
class ObjectContainerBase(Generic[O]):
    objects: set[ReferenceToObject[O]]
    def __init__(self, start_value: Iterable[O] = ()):
        self.objects = {ReferenceToObject(obj) for obj in start_value}
    
    def add_object(self, value: O) -> None:
        self.objects.add(ReferenceToObject(value))

    def remove_object(self, value: O) -> None:
        if value not in self:
            return
        self.objects.remove(ReferenceToObject(value))
    
    def remove_all(self) -> None:
        self.objects.clear()
    
    def __iter__(self) -> Iterator[O]:
        return iter(obj.obj for obj in self.objects.copy())
    
    def __contains__(self, value: object) -> bool:
        return ReferenceToObject(value) in self.objects
    
    def __len__(self) -> int:
        return len(self.objects)

class ObjectContainer(ObjectContainerBase["module_objects.Object2D"]):
    pass

class ObjectDictBase(Generic[O, V]):
    objects: dict[ReferenceToObject[O], V]
    def __init__(self, start_value: Iterable[tuple[O, V]] | None = None):
        self.objects = {ReferenceToObject(obj): val for obj, val in start_value} if start_value else {}

    def __getitem__(self, obj: O) -> V:
        return self.objects[ReferenceToObject(obj)]

    def __setitem__(self, obj: O, value: V) -> None:
        self.objects[ReferenceToObject(obj)] = value

    def pop(self, obj: O) -> V:
        return self.objects.pop(ReferenceToObject(obj))

    def popitem(self) -> tuple[O, V]:
        obj, value = self.objects.popitem()
        return (obj.obj, value)

    def clear(self) -> None:
        self.objects.clear()
    
    def __iter__(self) -> Iterator[O]:
        return iter(obj.obj for obj in self.objects.copy())
    
    def items(self) -> Iterator[tuple[O, V]]:
        return iter((obj.obj, val) for obj, val in self.objects.copy().items())
    
    def __contains__(self, obj: object) -> bool:
        return ReferenceToObject(obj) in self.objects
    
    def __len__(self) -> int:
        return len(self.objects)
    
    def __delitem__(self, obj: O):
        self.pop(obj)

class ObjectDict(Generic[V], ObjectDictBase["module_objects.Object2D", V]):
    pass