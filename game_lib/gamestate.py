from __future__ import annotations
from abc import ABC, abstractmethod
import pygame
from . import objects
from . import user_input as module_user_input
import win32api
import win32con
import win32gui

class GameStateType(ABC):
    canvas: objects.Canvas
    current_objects: list[objects.Object2D]
    user_input: module_user_input.UserInputType
    @abstractmethod
    def loop(self):
        pass

class AndromedaClashGameState(GameStateType):
    """
    Der Spielzustand. 
    Hier sollte in Methoden das erstellen von Objekten und ähnliches passieren.
    Die Hauptschleife sollte sich auch hier befinden.
    """
    clock: pygame.time.Clock # Wird für Bildrate verwendet.
    fps: int # Bildrate
    def __init__(self, canvas: objects.Canvas, user_input: module_user_input.UserInputType) -> None:
        self.canvas = canvas
        self.current_objects = []
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.user_input = user_input
    
    def loop(self) -> None:
        fuchsia = (255, 0, 128)
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST
        )
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 200, 200, 200, 200, 0) 
        running = True
        while running:
            win32gui.ShowWindow(hwnd, 5)
            win32gui.SetFocus(hwnd)
            self.canvas.fill(fuchsia)#(0, 0, 0)) # Hintergrund wird mit Schwarz gefüllt. (Farbenwerte werden als RGB-Tupel angegeben)
            self.user_input.process_tick()
            for event in pygame.event.get():
                self.user_input.process_event(event)
                if event.type == pygame.QUIT: # Falls Schliessen-Knopf gedruckt wird, wird das Programm beendet. 
                    running = False
            for object2d in self.current_objects:
                if not hasattr(object2d, "game_state"):
                    object2d.game_state = self
                object2d.update()
            for object2d in self.current_objects:
                object2d.draw(self.canvas)
            pygame.display.update() # Änderungen werden umgesetzt.
            self.clock.tick(self.fps)