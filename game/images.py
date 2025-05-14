from pygame import image
import pygame
from functools import cache
from collections.abc import Callable, Hashable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

_load_image = cache(image.load)
load_image: Callable[["FileDescriptorOrPath"], pygame.Surface] = lambda x: _load_image(x) if isinstance(x, Hashable) else _load_image("")
