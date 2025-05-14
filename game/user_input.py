from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
import pygame

class MouseButton(Enum):
    RIGHT = 0
    LEFT = 2
    MIDDLE = 1
    UNKNOWN = -1
    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN

class UserInputType(ABC):
    """
    Used for user input.
    """
    @abstractmethod
    def get_key_pressed(self, key: KeyboardKey) -> bool:
        """
        Ob die Taste derzeit gerdückt wird.
        """
    
    @abstractmethod
    def get_key_changed(self, key: KeyboardKey) -> bool:
        """
        Ob sich der Tastenzustand in diesem Frame geändert hat. 
        """
    
    @abstractmethod
    def get_mouse_pos(self) -> tuple[int, int]:
        """
        Wo sich die Maus derzeit befindet.
        """
    
    @abstractmethod
    def get_mouse_movement(self) -> tuple[int, int]:
        """
        Wie sich die Maus derzeit bewegt.
        """
    
    @abstractmethod
    def get_mouse_down(self, button: MouseButton = MouseButton.RIGHT) -> bool:
        """
        Ob die Mouse derzeit gedrückt wird. Man kann auch nach spezifischen Maustasten fragen.
        """
    
    @abstractmethod
    def get_mouse_changed(self, button: MouseButton = MouseButton.RIGHT) -> bool:
        """
        Ob sich der Maustastenzustand im derzeitigen Frame geändert hat. Man kann auch nach spezifischen Maustasten fragen.
        """
    
    @abstractmethod
    def process_event(self, event: pygame.event.EventType) -> None:
        pass
    
    @abstractmethod
    def process_tick(self) -> None:
        pass
    
    def get_key_up_now(self, key: KeyboardKey) -> bool:
        return self.get_key_changed(key) and not self.get_key_pressed(key)
    
    def get_key_down_now(self, key: KeyboardKey) -> bool:
        return self.get_key_changed(key) and self.get_key_pressed(key)

class UserInput(UserInputType):
    changed: set[KeyboardKey | MouseButton]
    def __init__(self):
        self.changed = set()
        
    def get_key_pressed(self, key):
        return pygame.key.get_pressed()[key.value]
    
    def get_key_changed(self, key):
        return key in self.changed
    
    def get_mouse_down(self, button = MouseButton.RIGHT):
        return pygame.mouse.get_pressed()[button.value]
    
    def get_mouse_changed(self, button = MouseButton.RIGHT):
        return button in self.changed
    
    def get_mouse_pos(self):
        return pygame.mouse.get_pos()
    
    def get_mouse_movement(self):
        return pygame.mouse.get_rel()
    
    def process_event(self, event):
        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            self.changed.add(KeyboardKey(event.key))
        if event.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
            self.changed.add(MouseButton(event.button))
    
    def process_tick(self):
        self.changed.clear()

class KeyboardKey(Enum):
    BACKSPACE = pygame.K_BACKSPACE
    TAB = pygame.K_TAB
    CLEAR = pygame.K_CLEAR
    RETURN = pygame.K_RETURN
    PAUSE = pygame.K_PAUSE
    ESCAPE = pygame.K_ESCAPE
    SPACE = pygame.K_SPACE
    EXCLAIM = pygame.K_EXCLAIM
    QUOTEDBL = pygame.K_QUOTEDBL
    HASH = pygame.K_HASH
    DOLLAR = pygame.K_DOLLAR
    AMPERSAND = pygame.K_AMPERSAND
    QUOTE = pygame.K_QUOTE
    LEFTPAREN = pygame.K_LEFTPAREN
    RIGHTPAREN = pygame.K_RIGHTPAREN
    ASTERISK = pygame.K_ASTERISK
    PLUS = pygame.K_PLUS
    COMMA = pygame.K_COMMA
    MINUS = pygame.K_MINUS
    PERIOD = pygame.K_PERIOD
    SLASH = pygame.K_SLASH
    zero = pygame.K_0
    one = pygame.K_1
    two = pygame.K_2
    three = pygame.K_3
    four = pygame.K_4
    five = pygame.K_5
    six = pygame.K_6
    seven = pygame.K_7
    eight = pygame.K_8
    nine = pygame.K_9
    COLON = pygame.K_COLON
    SEMICOLON = pygame.K_SEMICOLON
    LESS = pygame.K_LESS
    EQUALS = pygame.K_EQUALS
    GREATER = pygame.K_GREATER
    QUESTION = pygame.K_QUESTION
    AT = pygame.K_AT
    LEFTBRACKET = pygame.K_LEFTBRACKET
    BACKSLASH = pygame.K_BACKSLASH
    RIGHTBRACKET = pygame.K_RIGHTBRACKET
    CARET = pygame.K_CARET
    UNDERSCORE = pygame.K_UNDERSCORE
    BACKQUOTE = pygame.K_BACKQUOTE
    a = pygame.K_a
    b = pygame.K_b
    c = pygame.K_c
    d = pygame.K_d
    e = pygame.K_e
    f = pygame.K_f
    g = pygame.K_g
    h = pygame.K_h
    i = pygame.K_i
    j = pygame.K_j
    k = pygame.K_k
    l = pygame.K_l
    m = pygame.K_m
    n = pygame.K_n
    o = pygame.K_o
    p = pygame.K_p
    q = pygame.K_q
    r = pygame.K_r
    s = pygame.K_s
    t = pygame.K_t
    u = pygame.K_u
    v = pygame.K_v
    w = pygame.K_w
    x = pygame.K_x
    y = pygame.K_y
    z = pygame.K_z
    DELETE = pygame.K_DELETE
    KP0 = pygame.K_KP0
    KP1 = pygame.K_KP1
    KP2 = pygame.K_KP2
    KP3 = pygame.K_KP3
    KP4 = pygame.K_KP4
    KP5 = pygame.K_KP5
    KP6 = pygame.K_KP6
    KP7 = pygame.K_KP7
    KP8 = pygame.K_KP8
    KP9 = pygame.K_KP9
    KP_PERIOD = pygame.K_KP_PERIOD
    KP_DIVIDE = pygame.K_KP_DIVIDE
    KP_MULTIPLY = pygame.K_KP_MULTIPLY
    KP_MINUS = pygame.K_KP_MINUS
    KP_PLUS = pygame.K_KP_PLUS
    KP_ENTER = pygame.K_KP_ENTER
    KP_EQUALS = pygame.K_KP_EQUALS
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN
    RIGHT = pygame.K_RIGHT
    LEFT = pygame.K_LEFT
    INSERT = pygame.K_INSERT
    HOME = pygame.K_HOME
    END = pygame.K_END
    PAGEUP = pygame.K_PAGEUP
    PAGEDOWN = pygame.K_PAGEDOWN
    F1 = pygame.K_F1
    F2 = pygame.K_F2
    F3 = pygame.K_F3
    F4 = pygame.K_F4
    F5 = pygame.K_F5
    F6 = pygame.K_F6
    F7 = pygame.K_F7
    F8 = pygame.K_F8
    F9 = pygame.K_F9
    F10 = pygame.K_F10
    F11 = pygame.K_F11
    F12 = pygame.K_F12
    F13 = pygame.K_F13
    F14 = pygame.K_F14
    F15 = pygame.K_F15
    NUMLOCK = pygame.K_NUMLOCK
    CAPSLOCK = pygame.K_CAPSLOCK
    SCROLLOCK = pygame.K_SCROLLOCK
    RSHIFT = pygame.K_RSHIFT
    LSHIFT = pygame.K_LSHIFT
    RCTRL = pygame.K_RCTRL
    LCTRL = pygame.K_LCTRL
    RALT = pygame.K_RALT
    LALT = pygame.K_LALT
    RMETA = pygame.K_RMETA
    LMETA = pygame.K_LMETA
    LSUPER = pygame.K_LSUPER
    RSUPER = pygame.K_RSUPER
    MODE = pygame.K_MODE
    HELP = pygame.K_HELP
    PRINT = pygame.K_PRINT
    SYSREQ = pygame.K_SYSREQ
    BREAK = pygame.K_BREAK
    MENU = pygame.K_MENU
    POWER = pygame.K_POWER
    EURO = pygame.K_EURO
    AC_BACK = pygame.K_AC_BACK
    UNKNOWN = -1
    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN