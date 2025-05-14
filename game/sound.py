from __future__ import annotations
import pygame
from functools import cache
from collections.abc import Callable, Hashable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

_load_sound = cache(pygame.mixer.Sound)
load_sound: Callable[["FileDescriptorOrPath"], pygame.mixer.Sound] = lambda x: _load_sound(x) if isinstance(x, Hashable) else _load_sound("")

Sound = pygame.mixer.Sound