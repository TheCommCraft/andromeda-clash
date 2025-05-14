from __future__ import annotations
from pygame import image
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

_load_image = cache(image.load)
load_image: Callable[["FileDescriptorOrPath"], Image] = lambda x: _load_image(_hashable_path(x))

Image = pygame.Surface