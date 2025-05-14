from __future__ import annotations
import pygame
from functools import cache
from collections.abc import Callable, Hashable
from os import PathLike
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

def _hashable_path(path: "FileDescriptorOrPath") -> Hashable:
    if isinstance(path, Hashable):
        return path
    if isinstance(path, PathLike):
        return str(path)
    return ""

_load_sound = cache(pygame.mixer.Sound)
load_sound: Callable[["FileDescriptorOrPath"], Sound] = lambda x: _load_sound(_hashable_path(x))

Sound = pygame.mixer.Sound